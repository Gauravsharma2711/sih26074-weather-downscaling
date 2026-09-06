import pytest
import pandas as pd
from datetime import date
from src.services.forecast_service import (
    generate_panchayat_forecast,
    PanchayatNotFoundError,
    BlockForecastNotFoundError,
    MissingFeatureError,
    ModelUnavailableError
)


def test_generate_panchayat_forecast_valid():
    # Test using real Panchayat ID 2099 (Palsan in Surgana Block)
    forecast = generate_panchayat_forecast(
        panchayat_id=2099,
        forecast_date="2026-05-09",
        forecast_issue_date="2026-05-09"
    )
    
    assert isinstance(forecast, dict)
    assert forecast["status"] == "success"
    assert forecast["panchayat_id"] == 2099
    assert forecast["panchayat_name"] == "Palsan"
    assert forecast["block_name"] == "Surgana"
    assert forecast["forecast_date"] == "2026-05-09"
    assert forecast["lead_days"] == 0
    assert forecast["month"] == 5
    assert forecast["day_of_year"] == 129
    assert isinstance(forecast["downscaled_rainfall_mm"], (int, float))
    assert forecast["downscaled_rainfall_mm"] >= 0.0
    assert "model_name" in forecast
    assert "model_version" in forecast
    # Verify zero ground truth exposure
    assert "actual_rainfall_mm" not in forecast


def test_generate_panchayat_forecast_custom_block_forecast():
    forecast = generate_panchayat_forecast(
        panchayat_id=2099,
        forecast_date="2026-05-10",
        forecast_issue_date="2026-05-08",
        block_forecast_rainfall_mm=25.0
    )
    
    assert forecast["lead_days"] == 2
    assert forecast["month"] == 5
    assert forecast["day_of_year"] == 130
    assert forecast["block_forecast_rainfall_mm"] == 25.0
    assert forecast["downscaled_rainfall_mm"] >= 0.0


def test_generate_panchayat_forecast_not_found():
    with pytest.raises(PanchayatNotFoundError):
        generate_panchayat_forecast(
            panchayat_id=999999,
            forecast_date="2026-05-09",
            forecast_issue_date="2026-05-09"
        )


def test_generate_panchayat_forecast_missing_block_forecast(tmp_path):
    # Create temporary dataset missing block forecast
    temp_csv = tmp_path / "temp_panchayats.csv"
    df = pd.DataFrame([{
        "panchayat_id": 101,
        "panchayat_name": "TestPanchayat",
        "block_name": "TestBlock",
        "district_name": "Nashik",
        "panchayat_latitude": 20.1,
        "panchayat_longitude": 73.8,
        "elevation_m": 550.0,
        "station_distance_km": 4.0,
        "date": "2026-05-09"
    }])
    df.to_csv(temp_csv, index=False)
    
    with pytest.raises(BlockForecastNotFoundError):
        generate_panchayat_forecast(
            panchayat_id=101,
            forecast_date="2026-05-09",
            forecast_issue_date="2026-05-09",
            dataset_path=str(temp_csv)
        )


def test_generate_panchayat_forecast_missing_elevation(tmp_path):
    temp_csv = tmp_path / "temp_panchayats_no_elev.csv"
    df = pd.DataFrame([{
        "panchayat_id": 102,
        "panchayat_name": "NoElevPanchayat",
        "block_name": "TestBlock",
        "panchayat_latitude": 20.1,
        "panchayat_longitude": 73.8,
        "block_forecast_rainfall_mm": 10.0,
        "date": "2026-05-09"
    }])
    df.to_csv(temp_csv, index=False)
    
    with pytest.raises(MissingFeatureError):
        generate_panchayat_forecast(
            panchayat_id=102,
            forecast_date="2026-05-09",
            forecast_issue_date="2026-05-09",
            dataset_path=str(temp_csv)
        )
