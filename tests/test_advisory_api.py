"""
Tests for Agricultural Advisory API:
- POST /api/v1/advisory/generate
- GET /api/v1/advisory/panchayat/{panchayat_id}

Verifies validation, forecast lookup, draft advisory creation, approved advisory protection,
farmer retrieval endpoint (APPROVED only), 404 when draft/rejected, and Swagger/OpenAPI documentation.
"""

from datetime import date, datetime, timezone
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.downscaled_forecast import DownscaledForecast
from backend.app.models.advisory import Advisory


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def seeded_forecast():
    """Create a test forecast record for API tests and delete after."""
    db = SessionLocal()
    forecast = DownscaledForecast(
        panchayat_id=1001,
        forecast_date=date(2026, 9, 10),
        forecast_issue_date=date(2026, 9, 9),
        block_forecast_rainfall_mm=30.0,
        downscaled_rainfall_mm=22.5,
        actual_rainfall_mm=None,
        model_name="XGBoost Regressor",
        model_version="v1.0.0",
        confidence=None,
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    forecast_id = forecast.id
    db.close()

    yield forecast_id

    # Cleanup
    db = SessionLocal()
    try:
        db.query(Advisory).filter(Advisory.forecast_id == forecast_id).delete()
        db.query(DownscaledForecast).filter(DownscaledForecast.id == forecast_id).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


# =====================================================================
# 1. Success Flow: POST /api/v1/advisory/generate
# =====================================================================
def test_generate_advisory_api_success(client, seeded_forecast):
    """
    Test generating an advisory for a valid stored forecast.
    """
    payload = {"forecast_id": seeded_forecast}
    response = client.post("/api/v1/advisory/generate", json=payload)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["forecast_id"] == seeded_forecast
    assert data["panchayat_id"] == 1001
    assert data["forecast_date"] == "2026-09-10"
    assert data["rainfall_mm"] == 22.5
    assert data["rainfall_category"] == "Moderate rainfall"
    assert data["severity"] == "MODERATE"
    assert data["status"] == "DRAFT"
    assert data["rule_version"] == "RAIN_RULES_V1"
    assert "Ajmer Saundane" in data["advisory_title"] or "Panchayat" in data["advisory_title"]
    assert "•" in data["advisory_text"]
    assert data["officer_id"] is None
    assert data["approved_at"] is None


# =====================================================================
# 2. 404 Flow: Forecast Not Found
# =====================================================================
def test_generate_advisory_forecast_not_found(client):
    """
    Test that requesting an advisory for non-existent forecast returns HTTP 404.
    """
    payload = {"forecast_id": 99999999}
    response = client.post("/api/v1/advisory/generate", json=payload)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# =====================================================================
# 3. 422 Flow: Invalid Request Payload
# =====================================================================
def test_generate_advisory_invalid_forecast_id(client):
    """
    Test that invalid forecast_id (<= 0 or string) returns HTTP 422.
    """
    # Negative ID
    response = client.post("/api/v1/advisory/generate", json={"forecast_id": -5})
    assert response.status_code == 422

    # String ID
    response = client.post("/api/v1/advisory/generate", json={"forecast_id": "abc"})
    assert response.status_code == 422


# =====================================================================
# 4. Protection: Do Not Regenerate Existing Approved Advisory Automatically
# =====================================================================
def test_generate_advisory_does_not_regenerate_approved(client, seeded_forecast):
    """
    Test that when an approved advisory exists for a forecast,
    POST /api/v1/advisory/generate returns the existing approved advisory.
    """
    db = SessionLocal()
    try:
        # 1. Update the existing advisory to APPROVED
        advisory = db.query(Advisory).filter(Advisory.forecast_id == seeded_forecast).first()
        assert advisory is not None
        advisory_id = advisory.id
        advisory.status = "APPROVED"
        advisory.officer_id = "OFFICER_101"
        advisory.officer_comment = "Verified field drainage conditions manually."
        advisory.approved_at = datetime.now(timezone.utc)
        db.commit()

        # Count total advisories before
        count_before = db.query(Advisory).filter(Advisory.forecast_id == seeded_forecast).count()

        # 2. Call POST /api/v1/advisory/generate again
        response = client.post("/api/v1/advisory/generate", json={"forecast_id": seeded_forecast})
        assert response.status_code == 200
        data = response.json()

        # 3. Verify it returns the approved advisory
        assert data["id"] == advisory_id
        assert data["status"] == "APPROVED"
        assert data["officer_id"] == "OFFICER_101"
        assert data["officer_comment"] == "Verified field drainage conditions manually."

        # Verify no duplicate was created
        count_after = db.query(Advisory).filter(Advisory.forecast_id == seeded_forecast).count()
        assert count_after == count_before
    finally:
        db.close()


# =====================================================================
# 5. GET /api/v1/advisory/panchayat/{panchayat_id} - Approved Retrieval
# =====================================================================
def test_get_approved_panchayat_advisory_latest(client, seeded_forecast):
    """
    Test retrieving the latest approved advisory for a Panchayat.
    """
    response = client.get("/api/v1/advisory/panchayat/1001")
    assert response.status_code == 200, response.text
    data = response.json()

    assert "advisory_id" in data
    assert data["panchayat_id"] == 1001
    assert data["panchayat_name"] == "Ajmer Saundane"
    assert data["block_name"] == "Baglan"
    assert data["forecast_date"] == "2026-09-10"
    assert data["rainfall_mm"] == 22.5
    assert data["rainfall_category"] == "Moderate rainfall"
    assert data["severity"] == "MODERATE"
    assert "Ajmer Saundane" in data["advisory_title"] or "Panchayat" in data["advisory_title"]
    assert "•" in data["advisory_text"]
    assert data["rule_version"] == "RAIN_RULES_V1"
    assert data["status"] == "APPROVED"
    assert data["approved_at"] is not None


def test_get_approved_panchayat_advisory_by_date(client, seeded_forecast):
    """
    Test retrieving an approved advisory for a specific forecast date.
    """
    response = client.get("/api/v1/advisory/panchayat/1001?forecast_date=2026-09-10")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["panchayat_id"] == 1001
    assert data["forecast_date"] == "2026-09-10"
    assert data["status"] == "APPROVED"


# =====================================================================
# 6. DRAFT and REJECTED Advisory Exclusion (404 for Farmer Endpoint)
# =====================================================================
def test_get_advisory_does_not_return_draft_or_rejected(client):
    """
    Verify that DRAFT and REJECTED advisories are never returned by the farmer-facing endpoint.
    """
    db = SessionLocal()
    test_pid = 99911
    try:
        # Create a DRAFT advisory
        draft_adv = Advisory(
            panchayat_id=test_pid,
            forecast_date=date(2026, 9, 12),
            rainfall_mm=10.0,
            rainfall_category="Light rainfall",
            severity="LOW",
            advisory_title="Draft Title",
            advisory_text="Draft Text",
            rule_version="RAIN_RULES_V1",
            status="DRAFT",
        )
        # Create a REJECTED advisory
        rejected_adv = Advisory(
            panchayat_id=test_pid,
            forecast_date=date(2026, 9, 13),
            rainfall_mm=10.0,
            rainfall_category="Light rainfall",
            severity="LOW",
            advisory_title="Rejected Title",
            advisory_text="Rejected Text",
            rule_version="RAIN_RULES_V1",
            status="REJECTED",
        )
        db.add_all([draft_adv, rejected_adv])
        db.commit()

        # Query farmer endpoint -> MUST return 404
        response_latest = client.get(f"/api/v1/advisory/panchayat/{test_pid}")
        assert response_latest.status_code == 404
        assert "no approved advisory found" in response_latest.json()["detail"].lower()

        response_draft_date = client.get(f"/api/v1/advisory/panchayat/{test_pid}?forecast_date=2026-09-12")
        assert response_draft_date.status_code == 404

        response_rejected_date = client.get(f"/api/v1/advisory/panchayat/{test_pid}?forecast_date=2026-09-13")
        assert response_rejected_date.status_code == 404

    finally:
        db.query(Advisory).filter(Advisory.panchayat_id == test_pid).delete()
        db.commit()
        db.close()


def test_get_advisory_invalid_panchayat_id(client):
    """
    Test that invalid panchayat_id (<= 0 or string) returns HTTP 422.
    """
    res_neg = client.get("/api/v1/advisory/panchayat/-10")
    assert res_neg.status_code == 422

    res_str = client.get("/api/v1/advisory/panchayat/invalid")
    assert res_str.status_code == 422


# =====================================================================
# 7. OpenAPI & Swagger Documentation
# =====================================================================
def test_advisory_openapi_documentation(client):
    """
    Verify /api/v1/advisory/generate and /api/v1/advisory/panchayat/{panchayat_id}
    are fully documented in Swagger/OpenAPI.
    """
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    spec = response.json()

    # POST endpoint
    assert "/api/v1/advisory/generate" in spec["paths"]
    post_spec = spec["paths"]["/api/v1/advisory/generate"]["post"]
    assert "Generate Agricultural Advisory" in post_spec["summary"]
    assert "200" in post_spec["responses"]
    assert "404" in post_spec["responses"]
    assert "422" in post_spec["responses"]

    # GET endpoint
    assert "/api/v1/advisory/panchayat/{panchayat_id}" in spec["paths"]
    get_spec = spec["paths"]["/api/v1/advisory/panchayat/{panchayat_id}"]["get"]
    assert "Retrieve Approved Agricultural Advisory" in get_spec["summary"]
    assert "200" in get_spec["responses"]
    assert "404" in get_spec["responses"]
    assert "422" in get_spec["responses"]
