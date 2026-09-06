"""
Unit and Integration tests for POST /api/v1/forecast/generate endpoint.
Tests forecast generation, date validation, error handling (404, 422, 503, 500),
database persistence, zero ground-truth leakage, and OpenAPI schema compliance.
"""

from unittest.mock import patch
import pytest
from src.services.forecast_service import (
    PanchayatNotFoundError,
    BlockForecastNotFoundError,
    MissingFeatureError,
    ModelUnavailableError,
)


def test_generate_forecast_success(client):
    """
    Test POST /api/v1/forecast/generate for a valid Panchayat and date.
    """
    payload = {
        "panchayat_id": 1001,
        "forecast_date": "2026-09-04",
        "forecast_issue_date": "2026-09-04",
    }
    response = client.post("/api/v1/forecast/generate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()

    # Check exact expected schema fields
    assert data["panchayat_id"] == 1001
    assert data["panchayat_name"] == "Ajmer Saundane"
    assert data["block_name"] == "Baglan"
    assert data["district_name"] == "Nashik"
    assert data["forecast_date"] == "2026-09-04"
    assert data["forecast_issue_date"] == "2026-09-04"
    assert data["lead_days"] == 0
    assert isinstance(data["block_forecast_rainfall_mm"], (int, float))
    assert isinstance(data["downscaled_rainfall_mm"], (int, float))
    assert data["downscaled_rainfall_mm"] >= 0.0
    assert data["model_name"] == "XGBoost Regressor"
    assert data["model_version"] == "v1.0.0"
    assert data["confidence"] is None

    # Verify zero ground-truth leakage or internal fields
    forbidden_keys = {
        "actual_rainfall_mm",
        "station_id",
        "station_latitude",
        "station_longitude",
        "station_distance_km",
        "password",
        "database_url",
    }
    for key in forbidden_keys:
        assert key not in data


def test_generate_forecast_invalid_dates(client):
    """
    Test that forecast_date earlier than forecast_issue_date triggers 422 Unprocessable Entity.
    """
    payload = {
        "panchayat_id": 1001,
        "forecast_date": "2026-05-01",
        "forecast_issue_date": "2026-09-04",
    }
    response = client.post("/api/v1/forecast/generate", json=payload)
    assert response.status_code == 422


def test_generate_forecast_invalid_panchayat_id(client):
    """
    Test that invalid panchayat_id (< 1) triggers 422 Unprocessable Entity.
    """
    payload = {
        "panchayat_id": 0,
        "forecast_date": "2026-09-04",
        "forecast_issue_date": "2026-09-04",
    }
    response = client.post("/api/v1/forecast/generate", json=payload)
    assert response.status_code == 422


def test_generate_forecast_panchayat_not_found(client):
    """
    Test that non-existent panchayat_id returns HTTP 404.
    """
    with patch(
        "backend.app.api.v1.endpoints.forecast.generate_panchayat_forecast",
        side_effect=PanchayatNotFoundError("Panchayat 999999 not found."),
    ):
        payload = {
            "panchayat_id": 999999,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        }
        response = client.post("/api/v1/forecast/generate", json=payload)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_generate_forecast_block_forecast_not_found(client):
    """
    Test that missing block forecast returns HTTP 404.
    """
    with patch(
        "backend.app.api.v1.endpoints.forecast.generate_panchayat_forecast",
        side_effect=BlockForecastNotFoundError("No block forecast found."),
    ):
        payload = {
            "panchayat_id": 1001,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        }
        response = client.post("/api/v1/forecast/generate", json=payload)
        assert response.status_code == 404
        assert "no block forecast found" in response.json()["detail"].lower()


def test_generate_forecast_missing_feature_422(client):
    """
    Test that missing required Panchayat feature returns HTTP 422.
    """
    with patch(
        "backend.app.api.v1.endpoints.forecast.generate_panchayat_forecast",
        side_effect=MissingFeatureError("Elevation data missing."),
    ):
        payload = {
            "panchayat_id": 1001,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        }
        response = client.post("/api/v1/forecast/generate", json=payload)
        assert response.status_code == 422
        assert "elevation data missing" in response.json()["detail"].lower()


def test_generate_forecast_model_unavailable_503(client):
    """
    Test that ModelUnavailableError returns HTTP 503 Service Unavailable.
    """
    with patch(
        "backend.app.api.v1.endpoints.forecast.generate_panchayat_forecast",
        side_effect=ModelUnavailableError("Model service offline."),
    ):
        payload = {
            "panchayat_id": 1001,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        }
        response = client.post("/api/v1/forecast/generate", json=payload)
        assert response.status_code == 503
        assert "model service offline" in response.json()["detail"].lower()


def test_generate_forecast_unexpected_error_500(client):
    """
    Test that unexpected server error returns HTTP 500.
    """
    with patch(
        "backend.app.api.v1.endpoints.forecast.generate_panchayat_forecast",
        side_effect=RuntimeError("Unexpected tensor corruption."),
    ):
        payload = {
            "panchayat_id": 1001,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        }
        response = client.post("/api/v1/forecast/generate", json=payload)
        assert response.status_code == 500
        assert "internal model error" in response.json()["detail"].lower()


def test_forecast_generate_openapi_documentation(client):
    """
    Verify OpenAPI documentation includes POST /api/v1/forecast/generate and GET /api/v1/forecast/panchayat/{panchayat_id}.
    """
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    spec = response.json()

    assert "/api/v1/forecast/generate" in spec["paths"]
    post_spec = spec["paths"]["/api/v1/forecast/generate"]["post"]
    assert post_spec["summary"] == "Generate Micro-Level Weather Forecast"
    assert "200" in post_spec["responses"]
    assert "404" in post_spec["responses"]
    assert "422" in post_spec["responses"]
    assert "503" in post_spec["responses"]
    assert "500" in post_spec["responses"]

    # Check retrieval endpoint OpenAPI documentation
    assert "/api/v1/forecast/panchayat/{panchayat_id}" in spec["paths"]
    get_spec = spec["paths"]["/api/v1/forecast/panchayat/{panchayat_id}"]["get"]
    assert get_spec["summary"] == "Retrieve Stored Downscaled Forecast"
    param_names = [p["name"] for p in get_spec.get("parameters", [])]
    assert "panchayat_id" in param_names
    assert "forecast_date" in param_names
    assert "200" in get_spec["responses"]
    assert "404" in get_spec["responses"]


def test_get_panchayat_forecast_latest(client):
    """
    Test GET /api/v1/forecast/panchayat/{panchayat_id} retrieves latest stored forecast.
    """
    # 1. Seed a forecast via POST with valid date
    client.post(
        "/api/v1/forecast/generate",
        json={
            "panchayat_id": 1001,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        },
    )

    # 2. Retrieve latest
    response = client.get("/api/v1/forecast/panchayat/1001")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["panchayat_id"] == 1001
    assert data["panchayat_name"] == "Ajmer Saundane"
    assert data["block_name"] == "Baglan"
    assert data["district_name"] == "Nashik"
    assert isinstance(data["forecast_date"], str)
    assert isinstance(data["forecast_issue_date"], str)
    assert isinstance(data["lead_days"], int)
    assert isinstance(data["block_forecast_rainfall_mm"], (int, float))
    assert isinstance(data["downscaled_rainfall_mm"], (int, float))
    assert data["model_name"] == "XGBoost Regressor"
    assert data["model_version"] == "v1.0.0"
    assert data["confidence"] is None


def test_get_panchayat_forecast_by_date(client):
    """
    Test GET /api/v1/forecast/panchayat/{panchayat_id} with optional forecast_date.
    """
    # 1. Seed a forecast
    client.post(
        "/api/v1/forecast/generate",
        json={
            "panchayat_id": 1001,
            "forecast_date": "2026-09-04",
            "forecast_issue_date": "2026-09-04",
        },
    )

    # 2. Query with matching date
    response = client.get("/api/v1/forecast/panchayat/1001?forecast_date=2026-09-04")
    assert response.status_code == 200
    data = response.json()
    assert data["forecast_date"] == "2026-09-04"


def test_get_panchayat_forecast_not_found(client):
    """
    Test GET /api/v1/forecast/panchayat/{panchayat_id} returns 404 when no forecast exists.
    """
    # Non-existent Panchayat
    response = client.get("/api/v1/forecast/panchayat/999999")
    assert response.status_code == 404
    detail_lower = response.json()["detail"].lower()
    assert "found" in detail_lower and ("no" in detail_lower or "not" in detail_lower)

    # Non-existent date for valid Panchayat
    response_date = client.get("/api/v1/forecast/panchayat/1001?forecast_date=2199-12-31")
    assert response_date.status_code == 404
    detail_date_lower = response_date.json()["detail"].lower()
    assert "found" in detail_date_lower and ("no" in detail_date_lower or "not" in detail_date_lower)


def test_get_panchayat_forecast_invalid_id(client):
    """
    Test GET /api/v1/forecast/panchayat/{panchayat_id} returns 422 for invalid ID.
    """
    response = client.get("/api/v1/forecast/panchayat/0")
    assert response.status_code == 422


def test_e2e_panchayat_full_cycle(client):
    """
    Day 4 Step 11: End-to-end Panchayat workflow test for Panchayat 1001.
    Tests: Lookup -> Generate Forecast -> Output Validation -> Persist -> Retrieve -> Match Verification.
    """
    from datetime import date as dt_date
    from backend.app.core.database import SessionLocal
    from backend.app.models.downscaled_forecast import DownscaledForecast

    panchayat_id = 1001
    target_date = "2026-09-04"
    issue_date = "2026-09-04"

    # 1. Panchayat Lookup
    p_resp = client.get(f"/api/v1/panchayats/{panchayat_id}")
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert p_data["panchayat_id"] == panchayat_id
    assert p_data["panchayat_name"] == "Ajmer Saundane"
    assert p_data["block_name"] == "Baglan"

    # 2. Generate Forecast
    gen_resp = client.post(
        "/api/v1/forecast/generate",
        json={
            "panchayat_id": panchayat_id,
            "forecast_date": target_date,
            "forecast_issue_date": issue_date,
        },
    )
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["panchayat_id"] == panchayat_id
    assert gen_data["downscaled_rainfall_mm"] >= 0.0
    assert "actual_rainfall_mm" not in gen_data

    # 3. Retrieve Forecast
    get_resp = client.get(f"/api/v1/forecast/panchayat/{panchayat_id}?forecast_date={target_date}")
    assert get_resp.status_code == 200
    retrieved_data = get_resp.json()

    # 4. Compare with Database Record
    db = SessionLocal()
    try:
        db_rec = (
            db.query(DownscaledForecast)
            .filter(
                DownscaledForecast.panchayat_id == panchayat_id,
                DownscaledForecast.forecast_date == dt_date.fromisoformat(target_date),
            )
            .order_by(DownscaledForecast.id.desc())
            .first()
        )
        assert db_rec is not None
        assert db_rec.panchayat_id == retrieved_data["panchayat_id"]
        assert str(db_rec.forecast_date) == retrieved_data["forecast_date"]
        assert float(db_rec.downscaled_rainfall_mm) == float(retrieved_data["downscaled_rainfall_mm"])
        assert float(db_rec.block_forecast_rainfall_mm) == float(retrieved_data["block_forecast_rainfall_mm"])
        assert db_rec.model_name == retrieved_data["model_name"]
        assert db_rec.model_version == retrieved_data["model_version"]
    finally:
        db.close()


def test_multi_panchayat_10_blocks_suite(client):
    """
    Day 4 Step 12: Automated test verifying forecast generation, validation,
    and storage across 10 real Panchayats from distinct blocks.
    """
    import pandas as pd
    from pathlib import Path
    from backend.app.core.database import SessionLocal
    from backend.app.models.downscaled_forecast import DownscaledForecast
    from datetime import date as dt_date

    clean_path = Path("data/processed/nashik_weather_clean.csv")
    df = pd.read_csv(clean_path)
    distinct_panchayats = (
        df[["panchayat_id", "panchayat_name", "block_name", "date", "forecast_issue_date"]]
        .drop_duplicates(subset=["block_name"])
        .head(10)
        .to_dict(orient="records")
    )

    assert len(distinct_panchayats) == 10

    db = SessionLocal()
    try:
        for p in distinct_panchayats:
            pid = int(p["panchayat_id"])
            fdate = str(p["date"])
            tissue = str(p["forecast_issue_date"]) if str(p["forecast_issue_date"]) <= fdate else fdate

            # 1. Generate
            gen_res = client.post(
                "/api/v1/forecast/generate",
                json={
                    "panchayat_id": pid,
                    "forecast_date": fdate,
                    "forecast_issue_date": tissue,
                },
            )
            assert gen_res.status_code == 200, f"Failed for {pid} on {fdate}: {gen_res.text}"
            data = gen_res.json()
            assert data["downscaled_rainfall_mm"] >= 0.0

            # 2. Retrieve
            get_res = client.get(f"/api/v1/forecast/panchayat/{pid}?forecast_date={fdate}")
            assert get_res.status_code == 200
            ret = get_res.json()
            assert ret["downscaled_rainfall_mm"] == data["downscaled_rainfall_mm"]
    finally:
        db.close()
