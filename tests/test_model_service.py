import os
import pytest
from src.services.model_service import (
    ModelService,
    get_model_service,
    load_model,
    predict,
    get_model_metadata,
    FEATURE_COLUMNS
)


def test_model_service_singleton():
    service1 = get_model_service()
    service2 = get_model_service()
    assert service1 is service2
    assert service1.is_loaded is True
    assert service1.model is not None


def test_model_service_metadata():
    metadata = get_model_metadata()
    assert isinstance(metadata, dict)
    assert metadata["model_name"] == "XGBoost Regressor"
    assert metadata["model_version"] == "v1.0.0"
    assert metadata["feature_list"] == FEATURE_COLUMNS
    assert len(metadata["feature_list"]) == 8
    assert metadata["is_loaded"] is True


def test_model_service_predict_valid():
    result = predict(
        block_forecast_rainfall_mm=15.0,
        panchayat_latitude=20.5016,
        panchayat_longitude=73.5393,
        elevation_m=645.0,
        station_distance_km=8.16,
        lead_days=0,
        month=5,
        day_of_year=129
    )
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "downscaled_rainfall_mm" in result
    assert "raw_predicted_rainfall_mm" in result
    assert isinstance(result["downscaled_rainfall_mm"], (int, float))
    assert result["downscaled_rainfall_mm"] >= 0.0
    assert result["model_name"] == "XGBoost Regressor"
    assert result["model_version"] == "v1.0.0"


def test_model_service_predict_non_negative():
    # Test zero rain input
    result = predict(
        block_forecast_rainfall_mm=0.0,
        panchayat_latitude=20.0,
        panchayat_longitude=73.5,
        elevation_m=400.0,
        station_distance_km=10.0,
        lead_days=0,
        month=1,
        day_of_year=10
    )
    
    assert result["downscaled_rainfall_mm"] >= 0.0


def test_model_service_invalid_inputs():
    service = get_model_service()
    with pytest.raises(ValueError):
        service.predict(
            block_forecast_rainfall_mm="invalid_number",
            panchayat_latitude=20.0,
            panchayat_longitude=73.0,
            elevation_m=500.0,
            station_distance_km=5.0
        )
