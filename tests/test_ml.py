import pandas as pd
import numpy as np
from ml.features.engineer import extract_features, FEATURE_COLUMNS, TARGET_COLUMN
from ml.preprocessing.cleaner import clean_weather_data
from ml.models.baseline import BlockPersistenceBaseline
from ml.models.random_forest import RandomForestDownscaler
from ml.evaluation.metrics import evaluate_predictions, compare_model_against_baseline
from ml.predictions.pipeline import DownscalingPipeline


def test_clean_weather_data():
    sample_df = pd.DataFrame([{
        "panchayat_id": 1,
        "date": "2026-09-04",
        "forecast_issue_date": "2026-09-03",
        "block_forecast_rainfall_mm": "12.5",
        "actual_rainfall_mm": "14.2",
        "panchayat_latitude": "23.5",
        "panchayat_longitude": "85.3",
        "elevation_m": "650",
        "station_distance_km": "5.2"
    }])
    cleaned = clean_weather_data(sample_df)
    assert cleaned["block_forecast_rainfall_mm"].iloc[0] == 12.5
    assert cleaned["actual_rainfall_mm"].iloc[0] == 14.2


def test_extract_features():
    sample_df = pd.DataFrame([{
        "panchayat_id": 1,
        "date": pd.to_datetime("2026-09-04"),
        "forecast_issue_date": pd.to_datetime("2026-09-03"),
        "block_forecast_rainfall_mm": 12.5,
        "actual_rainfall_mm": 14.2,
        "panchayat_latitude": 23.5,
        "panchayat_longitude": 85.3,
        "elevation_m": 650.0,
        "station_distance_km": 5.2
    }])
    X, y = extract_features(sample_df)
    for col in FEATURE_COLUMNS:
        assert col in X.columns
    assert y.iloc[0] == 14.2
    assert X["month"].iloc[0] == 9
    assert X["lead_days"].iloc[0] == 1


def test_baseline_model():
    baseline = BlockPersistenceBaseline()
    sample_X = pd.DataFrame({
        "block_forecast_rainfall_mm": [10.0, 25.0, 0.0]
    })
    preds = baseline.predict(sample_X)
    np.testing.assert_array_equal(preds, [10.0, 25.0, 0.0])


def test_evaluation_metrics():
    y_true = np.array([10.0, 20.0, 30.0])
    y_baseline = np.array([12.0, 25.0, 28.0])
    y_model = np.array([11.0, 21.0, 29.0])
    
    report = compare_model_against_baseline(y_true, y_baseline, y_model)
    assert "baseline" in report
    assert "downscaled_model" in report
    assert report["is_improvement"] is True


def test_downscaling_pipeline():
    pipeline = DownscalingPipeline()
    sample_df = pd.DataFrame([{
        "panchayat_id": 1,
        "date": pd.to_datetime("2026-09-04"),
        "forecast_issue_date": pd.to_datetime("2026-09-03"),
        "block_forecast_rainfall_mm": 15.0,
        "actual_rainfall_mm": 18.0,
        "panchayat_latitude": 23.5,
        "panchayat_longitude": 85.3,
        "elevation_m": 650.0,
        "station_distance_km": 5.2
    }])
    output = pipeline.run(sample_df)
    assert "downscaled_rainfall_mm" in output.columns
    assert output["downscaled_rainfall_mm"].iloc[0] == 15.0
