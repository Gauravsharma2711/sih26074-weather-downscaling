from backend.app.models.panchayat_weather import PanchayatWeatherData
from backend.app.models.downscaled_forecast import DownscaledForecast
from backend.app.core.database import SessionLocal


def test_root_health_endpoint(client):
    """
    Test that GET /health returns 200 and {'status': 'ok'}.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_v1_health_endpoint(client):
    """
    Test that GET /api/v1/health returns 200 and {'status': 'ok'}.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_endpoint(client):
    """
    Test that GET /health/db verifies live connection to Supabase PostgreSQL.
    """
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert data["database"]["connected"] is True
    assert "panchayat_weather_data" in data["database"]["tables"]
    assert "downscaled_forecasts" in data["database"]["tables"]


def test_api_v1_database_health_endpoint(client):
    """
    Test that GET /api/v1/health/db verifies live connection to the database.
    """
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"]["connected"] is True


def test_panchayat_weather_model_query():
    """
    Test querying the panchayat_weather_data table using the SQLAlchemy model.
    """
    db = SessionLocal()
    try:
        record = db.query(PanchayatWeatherData).first()
        if record is not None:
            assert hasattr(record, "panchayat_id")
            assert hasattr(record, "lgd_code")
            assert hasattr(record, "block_name")
            assert hasattr(record, "actual_rainfall_mm")
    finally:
        db.close()


def test_downscaled_forecasts_model_query():
    """
    Test querying the downscaled_forecasts table using the SQLAlchemy model.
    """
    db = SessionLocal()
    try:
        # Check query execution against the table
        count = db.query(DownscaledForecast).count()
        assert isinstance(count, int)
    finally:
        db.close()
