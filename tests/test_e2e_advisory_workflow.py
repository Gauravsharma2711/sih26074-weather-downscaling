"""
End-to-End Advisory Workflow Integration Test (Day 5 - Step 13).

Validates the full lifecycle for a real Nashik Panchayat (panchayat_id = 1001):
1. Retrieve or generate forecast for panchayat_id = 1001.
2. Generate an advisory -> verify status is DRAFT.
3. Verify DRAFT advisory is NOT exposed through farmer endpoint.
4. Retrieve draft advisory through extension officer endpoint.
5. Extension officer approves advisory -> verify status becomes APPROVED.
6. Retrieve advisory through farmer endpoint -> verify APPROVED advisory is returned.
7. Verify multilingual rendering (en, mr, hi) on farmer endpoint.
8. Test Rejection Workflow separately:
   - Generate second draft advisory.
   - Extension officer rejects advisory -> verify status becomes REJECTED.
   - Verify REJECTED advisory is never served to farmers.
   - Verify immutability constraints.
"""

from datetime import date, datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.downscaled_forecast import DownscaledForecast
from backend.app.models.advisory import Advisory
from src.advisory.advisory_engine import RULE_VERSION


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """SQLAlchemy database session fixture with cleanup."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_complete_advisory_approval_and_rejection_workflow(client, db_session: Session):
    """
    Execute full Step 13 End-to-End workflow for Panchayat 1001.
    """
    panchayat_id = 1001
    f_date_approve = date(2026, 9, 8)
    f_date_reject = date(2026, 9, 9)

    # Clean existing test records for panchayat 1001 on these dates
    db_session.query(Advisory).filter(
        Advisory.panchayat_id == panchayat_id,
        Advisory.forecast_date.in_([f_date_approve, f_date_reject]),
    ).delete(synchronize_session=False)

    db_session.query(DownscaledForecast).filter(
        DownscaledForecast.panchayat_id == panchayat_id,
        DownscaledForecast.forecast_date.in_([f_date_approve, f_date_reject]),
    ).delete(synchronize_session=False)
    db_session.commit()

    created_advisory_ids = []
    created_forecast_ids = []

    try:
        # ---------------------------------------------------------------------
        # STEP 1: Insert Forecast for Panchayat 1001
        # ---------------------------------------------------------------------
        forecast_approve = DownscaledForecast(
            panchayat_id=panchayat_id,
            forecast_date=f_date_approve,
            forecast_issue_date=date(2026, 9, 7),
            downscaled_rainfall_mm=28.5,
            model_name="XGBoost Regressor",
            model_version="v1.0.0",
        )
        db_session.add(forecast_approve)
        db_session.commit()
        db_session.refresh(forecast_approve)
        created_forecast_ids.append(forecast_approve.id)

        # ---------------------------------------------------------------------
        # STEP 2 & 3: Generate Advisory & Verify Status is DRAFT
        # ---------------------------------------------------------------------
        gen_res = client.post("/api/v1/advisory/generate", json={"forecast_id": forecast_approve.id})
        assert gen_res.status_code == 200
        draft_data = gen_res.json()
        advisory_id = draft_data["id"]
        created_advisory_ids.append(advisory_id)

        assert draft_data["status"] == "DRAFT"
        assert draft_data["panchayat_id"] == panchayat_id
        assert draft_data["forecast_id"] == forecast_approve.id
        assert draft_data["rule_version"] == RULE_VERSION
        assert draft_data["rainfall_category"] == "Moderate rainfall"
        assert draft_data["severity"] == "MODERATE"
        assert draft_data["officer_id"] is None
        assert draft_data["approved_at"] is None

        # ---------------------------------------------------------------------
        # STEP 4: Verify DRAFT Advisory is NOT exposed to Farmers
        # ---------------------------------------------------------------------
        farmer_pre_approve = client.get(f"/api/v1/farmer/panchayat/{panchayat_id}?forecast_date={f_date_approve}")
        assert farmer_pre_approve.status_code == 200
        farmer_pre_data = farmer_pre_approve.json()
        assert farmer_pre_data["advisory_status"] == "NO_APPROVED_ADVISORY"
        assert farmer_pre_data["advisory_title"] is None
        assert farmer_pre_data["advisory_points"] == []

        # ---------------------------------------------------------------------
        # STEP 5: Retrieve DRAFT Advisory through Officer Endpoint
        # ---------------------------------------------------------------------
        officer_get = client.get(f"/api/v1/officer/advisories/{advisory_id}")
        assert officer_get.status_code == 200
        officer_data = officer_get.json()
        assert officer_data["id"] == advisory_id
        assert officer_data["status"] == "DRAFT"
        assert "Moderate Rainfall Advisory" in officer_data["advisory_title"]

        # ---------------------------------------------------------------------
        # STEP 6: Officer Approves the Advisory
        # ---------------------------------------------------------------------
        approve_res = client.post(
            f"/api/v1/officer/advisories/{advisory_id}/approve",
            json={
                "officer_id": "OFFICER_NASHIK_BAGLAN_01",
                "officer_comment": "Verified against local micro-topography. Approved for panchayat distribution.",
            },
        )
        assert approve_res.status_code == 200
        approved_data = approve_res.json()
        assert approved_data["status"] == "APPROVED"
        assert approved_data["officer_id"] == "OFFICER_NASHIK_BAGLAN_01"
        assert "Approved for panchayat distribution" in approved_data["officer_comment"]
        assert approved_data["approved_at"] is not None

        # ---------------------------------------------------------------------
        # STEP 7 & 8: Retrieve through Farmer Endpoint & Verify APPROVED Advisory
        # ---------------------------------------------------------------------
        farmer_post_approve = client.get(f"/api/v1/farmer/panchayat/{panchayat_id}?forecast_date={f_date_approve}")
        assert farmer_post_approve.status_code == 200
        farmer_post_data = farmer_post_approve.json()
        assert farmer_post_data["advisory_status"] == "APPROVED"
        assert "Moderate Rainfall Advisory" in farmer_post_data["advisory_title"]
        assert len(farmer_post_data["advisory_points"]) >= 3
        assert farmer_post_data["rainfall_mm"] == 28.5
        assert farmer_post_data["rainfall_category"] == "Moderate rainfall"
        assert farmer_post_data["severity"] == "MODERATE"
        assert farmer_post_data["model_name"] == "XGBoost Regressor"
        assert farmer_post_data["model_version"] == "v1.0.0"

        # Verify Multilingual delivery
        farmer_mr = client.get(f"/api/v1/farmer/panchayat/{panchayat_id}?forecast_date={f_date_approve}&lang=mr")
        assert farmer_mr.status_code == 200
        assert farmer_mr.json()["language"] == "mr"
        assert "मध्यम पाऊस सल्ला" in farmer_mr.json()["advisory_title"]

        farmer_hi = client.get(f"/api/v1/farmer/panchayat/{panchayat_id}?forecast_date={f_date_approve}&lang=hi")
        assert farmer_hi.status_code == 200
        assert farmer_hi.json()["language"] == "hi"
        assert "मध्यम वर्षा सलाह" in farmer_hi.json()["advisory_title"]

        # ---------------------------------------------------------------------
        # STEP 9: TEST REJECTION WORKFLOW SEPARATELY
        # ---------------------------------------------------------------------
        # A. Insert second forecast for rejection test
        forecast_reject = DownscaledForecast(
            panchayat_id=panchayat_id,
            forecast_date=f_date_reject,
            forecast_issue_date=date(2026, 9, 7),
            downscaled_rainfall_mm=95.0,
            model_name="XGBoost Regressor",
            model_version="v1.0.0",
        )
        db_session.add(forecast_reject)
        db_session.commit()
        db_session.refresh(forecast_reject)
        created_forecast_ids.append(forecast_reject.id)

        # B. Generate second draft advisory
        gen_res_2 = client.post("/api/v1/advisory/generate", json={"forecast_id": forecast_reject.id})
        assert gen_res_2.status_code == 200
        draft_2 = gen_res_2.json()
        advisory_id_2 = draft_2["id"]
        created_advisory_ids.append(advisory_id_2)
        assert draft_2["status"] == "DRAFT"

        # C. Officer Rejects the Advisory
        reject_res = client.post(
            f"/api/v1/officer/advisories/{advisory_id_2}/reject",
            json={
                "officer_id": "OFFICER_NASHIK_BAGLAN_01",
                "officer_comment": "Manual raingauge calibration differs; rejecting draft.",
            },
        )
        assert reject_res.status_code == 200
        rejected_data = reject_res.json()
        assert rejected_data["status"] == "REJECTED"
        assert rejected_data["officer_id"] == "OFFICER_NASHIK_BAGLAN_01"
        assert "rejecting draft" in rejected_data["officer_comment"]

        # D. Verify REJECTED Advisory is NEVER exposed to Farmers
        farmer_reject_check = client.get(f"/api/v1/farmer/panchayat/{panchayat_id}?forecast_date={f_date_reject}")
        assert farmer_reject_check.status_code == 200
        farmer_reject_data = farmer_reject_check.json()
        assert farmer_reject_data["advisory_status"] == "NO_APPROVED_ADVISORY"
        assert farmer_reject_data["advisory_title"] is None
        assert farmer_reject_data["advisory_points"] == []

        # E. Verify Immutability: Cannot approve an already REJECTED advisory
        invalid_approve = client.post(
            f"/api/v1/officer/advisories/{advisory_id_2}/approve",
            json={"officer_id": "OFFICER_01"},
        )
        assert invalid_approve.status_code == 400
        assert "because it has been REJECTED" in invalid_approve.json()["detail"]

    finally:
        # Cleanup test entities
        if created_advisory_ids:
            db_session.query(Advisory).filter(Advisory.id.in_(created_advisory_ids)).delete(synchronize_session=False)
        if created_forecast_ids:
            db_session.query(DownscaledForecast).filter(DownscaledForecast.id.in_(created_forecast_ids)).delete(synchronize_session=False)
        db_session.commit()
