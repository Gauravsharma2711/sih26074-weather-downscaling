"""
Integration tests for Officer Review API endpoints (Day 5 - Step 8).

Validates:
1. GET /api/v1/officer/advisories (filtering, pagination)
2. GET /api/v1/officer/advisories/{advisory_id}
3. POST /api/v1/officer/advisories/{advisory_id}/approve (DRAFT -> APPROVED, immutability, timestamps, officer logging)
4. POST /api/v1/officer/advisories/{advisory_id}/reject (DRAFT -> REJECTED, immutability, farmer isolation)
5. State transition guards, immutability constraints, and input validation.
"""

from datetime import date, datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.advisory import Advisory


client = TestClient(app)


@pytest.fixture
def clean_advisories():
    """
    Fixture to cleanup test advisories after tests.
    """
    created_ids = []

    def _track(adv_id: int):
        created_ids.append(adv_id)

    yield _track

    if created_ids:
        db = next(get_db())
        try:
            db.query(Advisory).filter(Advisory.id.in_(created_ids)).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()



def test_officer_list_advisories(clean_advisories):
    """
    Test listing advisories with review_status, panchayat_id, and forecast_date filters.
    """
    db = next(get_db())
    test_date = date(2026, 9, 20)
    panchayat_id = 99801

    try:
        # Create a DRAFT, an APPROVED, and a REJECTED advisory
        adv_draft = Advisory(
            panchayat_id=panchayat_id,
            forecast_id=1,
            forecast_date=test_date,
            rainfall_mm=25.0,
            rainfall_category="Moderate rainfall",
            severity="MODERATE",
            advisory_title="Draft Test Advisory",
            advisory_text="• Draft guidance text",
            rule_version="RAIN_RULES_V1",
            status="DRAFT",
        )
        adv_approved = Advisory(
            panchayat_id=panchayat_id,
            forecast_id=1,
            forecast_date=test_date,
            rainfall_mm=10.0,
            rainfall_category="Light rainfall",
            severity="LOW",
            advisory_title="Approved Test Advisory",
            advisory_text="• Approved guidance text",
            rule_version="RAIN_RULES_V1",
            status="APPROVED",
            officer_id="OFFICER_TEST",
            approved_at=datetime.now(timezone.utc),
        )
        adv_rejected = Advisory(
            panchayat_id=panchayat_id,
            forecast_id=1,
            forecast_date=test_date,
            rainfall_mm=150.0,
            rainfall_category="Very heavy rainfall",
            severity="CRITICAL",
            advisory_title="Rejected Test Advisory",
            advisory_text="• Rejected guidance text",
            rule_version="RAIN_RULES_V1",
            status="REJECTED",
            officer_id="OFFICER_TEST",
            officer_comment="Outdated sensor data",
        )
        db.add_all([adv_draft, adv_approved, adv_rejected])
        db.commit()
        db.refresh(adv_draft)
        db.refresh(adv_approved)
        db.refresh(adv_rejected)

        clean_advisories(adv_draft.id)
        clean_advisories(adv_approved.id)
        clean_advisories(adv_rejected.id)

        # 1. Filter by status=DRAFT and panchayat_id
        res = client.get(f"/api/v1/officer/advisories?status=DRAFT&panchayat_id={panchayat_id}")
        assert res.status_code == 200
        data = res.json()
        assert any(a["id"] == adv_draft.id for a in data)
        assert not any(a["id"] == adv_approved.id for a in data)
        assert not any(a["id"] == adv_rejected.id for a in data)

        # 2. Filter by status=APPROVED
        res = client.get(f"/api/v1/officer/advisories?status=APPROVED&panchayat_id={panchayat_id}")
        assert res.status_code == 200
        data = res.json()
        assert any(a["id"] == adv_approved.id for a in data)
        assert not any(a["id"] == adv_draft.id for a in data)

        # 3. Filter by forecast_date
        res = client.get(f"/api/v1/officer/advisories?forecast_date={test_date.isoformat()}&panchayat_id={panchayat_id}")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 3

    finally:
        db.close()


def test_officer_get_advisory_by_id(clean_advisories):
    """
    Test retrieving an advisory by ID and handling 404 for non-existent IDs.
    """
    db = next(get_db())
    try:
        adv = Advisory(
            panchayat_id=99802,
            forecast_id=1,
            forecast_date=date(2026, 9, 21),
            rainfall_mm=0.0,
            rainfall_category="No significant rainfall",
            severity="LOW",
            advisory_title="Single Item Retrieval Test",
            advisory_text="• Advisory details",
            rule_version="RAIN_RULES_V1",
            status="DRAFT",
        )
        db.add(adv)
        db.commit()
        db.refresh(adv)
        clean_advisories(adv.id)

        # Success
        res = client.get(f"/api/v1/officer/advisories/{adv.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == adv.id
        assert data["advisory_title"] == "Single Item Retrieval Test"
        assert data["status"] == "DRAFT"

        # Not Found
        res_404 = client.get("/api/v1/officer/advisories/99999999")
        assert res_404.status_code == 404
        assert "not found" in res_404.json()["detail"].lower()

    finally:
        db.close()


def test_officer_approve_advisory_flow(clean_advisories):
    """
    Test officer approving a DRAFT advisory:
    - State transition: DRAFT -> APPROVED
    - Stores officer_id, officer_comment, and approved_at
    - Immediately becomes available to farmer retrieval endpoint
    - Cannot be re-approved or silently changed (returns 409 Conflict)
    """
    db = next(get_db())
    panchayat_id = 99803
    test_date = date(2026, 9, 22)

    try:
        adv = Advisory(
            panchayat_id=panchayat_id,
            forecast_id=1,
            forecast_date=test_date,
            rainfall_mm=45.0,
            rainfall_category="Moderate rainfall",
            severity="MODERATE",
            advisory_title="Approval Flow Test",
            advisory_text="• Ensure field drainage channels are clear.",
            rule_version="RAIN_RULES_V1",
            status="DRAFT",
        )
        db.add(adv)
        db.commit()
        db.refresh(adv)
        clean_advisories(adv.id)

        # Verify before approval: farmer endpoint returns 404
        res_farmer_before = client.get(f"/api/v1/advisory/panchayat/{panchayat_id}?forecast_date={test_date.isoformat()}")
        assert res_farmer_before.status_code == 404

        # Perform officer approval
        approval_payload = {
            "officer_id": "OFFICER_NASHIK_42",
            "officer_comment": "Field ground moisture checked. Advisory approved for dispatch.",
        }
        res_approve = client.post(f"/api/v1/officer/advisories/{adv.id}/approve", json=approval_payload)
        assert res_approve.status_code == 200
        approved_data = res_approve.json()
        assert approved_data["id"] == adv.id
        assert approved_data["status"] == "APPROVED"
        assert approved_data["officer_id"] == "OFFICER_NASHIK_42"
        assert approved_data["officer_comment"] == "Field ground moisture checked. Advisory approved for dispatch."
        assert approved_data["approved_at"] is not None

        # Verify after approval: farmer endpoint returns 200 with approved data
        res_farmer_after = client.get(f"/api/v1/advisory/panchayat/{panchayat_id}?forecast_date={test_date.isoformat()}")
        assert res_farmer_after.status_code == 200
        farmer_data = res_farmer_after.json()
        assert farmer_data["advisory_id"] == adv.id
        assert farmer_data["status"] == "APPROVED"

        # Attempt to re-approve (Approved advisories cannot be silently changed -> 409 Conflict)
        res_reapprove = client.post(
            f"/api/v1/officer/advisories/{adv.id}/approve",
            json={"officer_id": "OFFICER_OTHER", "officer_comment": "Attempting silent update"},
        )
        assert res_reapprove.status_code == 409
        assert "already approved" in res_reapprove.json()["detail"].lower()

    finally:
        db.close()


def test_officer_reject_advisory_flow(clean_advisories):
    """
    Test officer rejecting a DRAFT advisory:
    - State transition: DRAFT -> REJECTED
    - Stores officer_id and officer_comment
    - Never exposed to farmer retrieval endpoint
    - Re-rejection returns 409 Conflict
    - Attempt to approve a REJECTED advisory returns 400 Bad Request
    """
    db = next(get_db())
    panchayat_id = 99804
    test_date = date(2026, 9, 23)

    try:
        adv = Advisory(
            panchayat_id=panchayat_id,
            forecast_id=1,
            forecast_date=test_date,
            rainfall_mm=220.0,
            rainfall_category="Extremely heavy rainfall",
            severity="CRITICAL",
            advisory_title="Rejection Flow Test",
            advisory_text="• Heavy rain guidance",
            rule_version="RAIN_RULES_V1",
            status="DRAFT",
        )
        db.add(adv)
        db.commit()
        db.refresh(adv)
        clean_advisories(adv.id)

        # Reject the draft advisory
        reject_payload = {
            "officer_id": "OFFICER_BAGLAN_07",
            "officer_comment": "Local rain gauge radar indicates no cyclonic formation; draft rejected.",
        }
        res_reject = client.post(f"/api/v1/officer/advisories/{adv.id}/reject", json=reject_payload)
        assert res_reject.status_code == 200
        rejected_data = res_reject.json()
        assert rejected_data["id"] == adv.id
        assert rejected_data["status"] == "REJECTED"
        assert rejected_data["officer_id"] == "OFFICER_BAGLAN_07"
        assert "radar indicates" in rejected_data["officer_comment"]

        # Ensure farmer endpoint returns 404 (does NOT return REJECTED)
        res_farmer = client.get(f"/api/v1/advisory/panchayat/{panchayat_id}?forecast_date={test_date.isoformat()}")
        assert res_farmer.status_code == 404

        # Attempt to reject again (already REJECTED -> 409 Conflict)
        res_rereject = client.post(f"/api/v1/officer/advisories/{adv.id}/reject", json=reject_payload)
        assert res_rereject.status_code == 409
        assert "already rejected" in res_rereject.json()["detail"].lower()

        # Attempt to approve a rejected advisory -> 400 Bad Request
        res_approve_rejected = client.post(
            f"/api/v1/officer/advisories/{adv.id}/approve",
            json={"officer_id": "OFFICER_NEW", "officer_comment": "Attempting approval of rejected"},
        )
        assert res_approve_rejected.status_code == 400
        assert "rejected" in res_approve_rejected.json()["detail"].lower()

    finally:
        db.close()


def test_officer_cannot_reject_approved_advisory(clean_advisories):
    """
    Approved advisories cannot be silently changed or rejected directly.
    """
    db = next(get_db())
    try:
        adv = Advisory(
            panchayat_id=99805,
            forecast_id=1,
            forecast_date=date(2026, 9, 24),
            rainfall_mm=5.0,
            rainfall_category="Light rainfall",
            severity="LOW",
            advisory_title="Immutability Test",
            advisory_text="• Light rainfall advisory",
            rule_version="RAIN_RULES_V1",
            status="APPROVED",
            officer_id="OFFICER_ORIGINAL",
            approved_at=datetime.now(timezone.utc),
        )
        db.add(adv)
        db.commit()
        db.refresh(adv)
        clean_advisories(adv.id)

        # Attempting to reject an approved advisory should return 409 Conflict
        res = client.post(
            f"/api/v1/officer/advisories/{adv.id}/reject",
            json={"officer_id": "OFFICER_OTHER", "officer_comment": "Direct rejection of approved"},
        )
        assert res.status_code == 409
        assert "already approved" in res.json()["detail"].lower()

    finally:
        db.close()


def test_officer_request_validation():
    """
    Test validation errors on empty officer_id or invalid advisory_id.
    """
    # Empty officer_id on approve
    res_empty_officer = client.post("/api/v1/officer/advisories/1/approve", json={"officer_id": ""})
    assert res_empty_officer.status_code == 422

    # Missing officer_id on reject
    res_missing_officer = client.post("/api/v1/officer/advisories/1/reject", json={})
    assert res_missing_officer.status_code == 422

    # Invalid advisory ID (<= 0)
    res_invalid_id = client.post("/api/v1/officer/advisories/0/approve", json={"officer_id": "OFFICER_1"})
    assert res_invalid_id.status_code == 422
