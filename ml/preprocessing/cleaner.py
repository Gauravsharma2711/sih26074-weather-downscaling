import logging
import pandas as pd

logger = logging.getLogger(__name__)


def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate raw weather data for machine learning:
    1. Parse date columns (date, forecast_issue_date) to datetime.
    2. Ensure numeric types for rainfall, elevation, distance, and coordinates.
    3. Drop records with missing critical predictors or target values.
    
    Args:
        df: Raw pandas DataFrame from database.
        
    Returns:
        Cleaned pandas DataFrame ready for feature engineering.
    """
    if df.empty:
        logger.warning("Empty dataframe received for cleaning.")
        return df

    cleaned = df.copy()

    # 1. Parse date columns
    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"])
    if "forecast_issue_date" in cleaned.columns:
        cleaned["forecast_issue_date"] = pd.to_datetime(cleaned["forecast_issue_date"])

    # 2. Ensure numeric columns are properly converted
    numeric_cols = [
        "block_forecast_rainfall_mm",
        "actual_rainfall_mm",
        "panchayat_latitude",
        "panchayat_longitude",
        "elevation_m",
        "station_distance_km",
        "station_latitude",
        "station_longitude",
    ]
    for col in numeric_cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    # 3. Non-negative rainfall constraint
    if "block_forecast_rainfall_mm" in cleaned.columns:
        cleaned["block_forecast_rainfall_mm"] = cleaned["block_forecast_rainfall_mm"].clip(lower=0.0)
    if "actual_rainfall_mm" in cleaned.columns:
        cleaned["actual_rainfall_mm"] = cleaned["actual_rainfall_mm"].clip(lower=0.0)

    logger.info(f"Cleaned dataset contains {len(cleaned)} rows.")
    return cleaned
