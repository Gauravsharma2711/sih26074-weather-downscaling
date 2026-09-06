"""
Unit and Integration Tests for Advisory Service (src.services.advisory_service).

Verifies end-to-end connection between DownscaledForecast records, deterministic
rules, and Supabase database persistence.
"""

from datetime import date
import pytest
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.downscaled_forecast import DownscaledForecast
from backend.app.models.advisory import Advisory
from src.services.advisory_service import (
    generate_advisory,
    InvalidForecastInputError,
    AdvisoryServiceError,
)
from src.advisory.rainfall_classifier import RainfallCategory
from src.advisory.advisory_engine import AdvisorySeverity, RULE_VERSION


@pytest.fixture(scope="module")
def db_session():
    """Yield a database session for advisory testing and cleanup after."""
    db = SessionLocal()
    created_advisory_ids = []
    created_forecast_ids = []
    
    yield db, created_advisory_ids, created_forecast_ids
    
    # Cleanup created records
    try:
        if created_advisory_ids:
            db.query(Advisory).filter(Advisory.id.in_(created_advisory_ids)).delete(synchronize_session=False)
        if created_forecast_ids:
            db.query(DownscaledForecast).filter(DownscaledForecast.id.in_(created_forecast_ids)).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


def test_generate_advisory_from_stored_forecast(db_session):
    """
    Test Step 5 end-to-end pipeline:
    1. Seed a DownscaledForecast record in DB.
    2. Pass stored forecast to generate_advisory.
    3. Verify downscaled_rainfall_mm reading, classification, severity, rule_version, and DRAFT status.
    4. Verify database persistence in Supabase and forecast immutability.
    """
    db, created_advisory_ids, created_forecast_ids = db_session

    # 1. Create and store a mock DownscaledForecast
    forecast = DownscaledForecast(
        panchayat_id=1001,
        forecast_date=date(2026, 9, 8),
        forecast_issue_date=date(2026, 9, 7),
        block_forecast_rainfall_mm=25.0,
        downscaled_rainfall_mm=18.5,
        actual_rainfall_mm=None,
        model_name="XGBoost Regressor",
        model_version="v1.0.0",
        confidence=None,
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    created_forecast_ids.append(forecast.id)

    original_forecast_id = forecast.id
    original_rainfall = float(forecast.downscaled_rainfall_mm)

    # 2. Call generate_advisory
    advisory = generate_advisory(forecast, db=db)
    created_advisory_ids.append(advisory.id)

    # 3. Verify returned advisory attributes
    assert advisory.id is not None
    assert advisory.panchayat_id == 1001
    assert advisory.forecast_id == original_forecast_id
    assert advisory.forecast_date == date(2026, 9, 8)
    assert float(advisory.rainfall_mm) == original_rainfall
    assert advisory.rainfall_category == RainfallCategory.MODERATE
    assert advisory.severity == AdvisorySeverity.MODERATE
    assert advisory.rule_version == RULE_VERSION
    assert advisory.status == "DRAFT"
    assert advisory.officer_id is None
    assert advisory.officer_comment is None
    assert advisory.approved_at is None
    assert "Ajmer Saundane" in advisory.advisory_title or "Panchayat" in advisory.advisory_title
    assert "•" in advisory.advisory_text

    # 4. Verify database record lookup
    stored_advisory = db.query(Advisory).filter(Advisory.id == advisory.id).first()
    assert stored_advisory is not None
    assert stored_advisory.forecast_id == original_forecast_id
    assert stored_advisory.status == "DRAFT"

    # 5. Verify original forecast was NEVER modified
    db.refresh(forecast)
    assert forecast.id == original_forecast_id
    assert float(forecast.downscaled_rainfall_mm) == original_rainfall


def test_generate_advisory_from_dict_input(db_session):
    """
    Test generating advisory when forecast is provided as a dictionary payload.
    """
    db, created_advisory_ids, _ = db_session

    dict_forecast = {
        "id": 99991,
        "panchayat_id": 1265,
        "panchayat_name": "Ahiwantwadi",
        "block_name": "Dindori",
        "forecast_date": "2026-09-09",
        "forecast_issue_date": "2026-09-08",
        "downscaled_rainfall_mm": 72.4,
    }

    advisory = generate_advisory(dict_forecast, db=db)
    created_advisory_ids.append(advisory.id)

    assert advisory.panchayat_id == 1265
    assert advisory.forecast_id == 99991
    assert advisory.rainfall_category == RainfallCategory.HEAVY
    assert advisory.severity == AdvisorySeverity.HIGH
    assert advisory.status == "DRAFT"
    assert "Ahiwantwadi" in advisory.advisory_title
    assert "Drainage" in advisory.advisory_title or "Heavy Rainfall" in advisory.advisory_title


def test_generate_advisory_invalid_forecast_rejection(db_session):
    """
    Test that invalid or missing forecast inputs are rejected with descriptive errors.
    """
    db, _, _ = db_session

    # None forecast
    with pytest.raises(InvalidForecastInputError, match="null"):
        generate_advisory(None, db=db)

    # Missing panchayat_id
    with pytest.raises(InvalidForecastInputError, match="panchayat_id"):
        generate_advisory({"forecast_date": "2026-09-08", "downscaled_rainfall_mm": 5.0}, db=db)

    # Missing downscaled_rainfall_mm
    with pytest.raises(InvalidForecastInputError, match="downscaled_rainfall_mm"):
        generate_advisory({"panchayat_id": 1001, "forecast_date": "2026-09-08"}, db=db)
