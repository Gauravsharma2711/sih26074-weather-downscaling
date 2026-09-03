import logging
from typing import Tuple, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Core feature list specified for SIH26074
FEATURE_COLUMNS: List[str] = [
    "block_forecast_rainfall_mm",
    "panchayat_latitude",
    "panchayat_longitude",
    "elevation_m",
    "station_distance_km",
    "lead_days",
    "month",
    "day_of_year",
]

TARGET_COLUMN: str = "actual_rainfall_mm"


def extract_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Extract the specified predictors (X) and target variable (y) from cleaned weather data:
    - block_forecast_rainfall_mm: Official forecast at the block level
    - panchayat_latitude, panchayat_longitude: Spatial coordinates
    - elevation_m: Elevation above sea level
    - station_distance_km: Distance to nearest validation weather station
    - lead_days: Difference in days between forecast date and issue date
    - month: Calendar month (1-12)
    - day_of_year: Day of the year (1-366)
    
    Target:
    - actual_rainfall_mm: Ground truth rainfall observation
    
    Args:
        df: Cleaned pandas DataFrame.
        
    Returns:
        Tuple of (X: pd.DataFrame, y: pd.Series)
    """
    data = df.copy()

    # Temporal Feature Engineering
    if "date" in data.columns and pd.api.types.is_datetime64_any_dtype(data["date"]):
        data["month"] = data["date"].dt.month
        data["day_of_year"] = data["date"].dt.dayofyear
    else:
        data["month"] = 1
        data["day_of_year"] = 1

    # Forecast Lead Time (lead_days)
    if (
        "date" in data.columns 
        and "forecast_issue_date" in data.columns
        and pd.api.types.is_datetime64_any_dtype(data["date"])
        and pd.api.types.is_datetime64_any_dtype(data["forecast_issue_date"])
    ):
        data["lead_days"] = (data["date"] - data["forecast_issue_date"]).dt.days
        data["lead_days"] = data["lead_days"].fillna(1).clip(lower=0)
    else:
        data["lead_days"] = 1

    # Fill default safe values if optional spatial columns are missing
    for col in FEATURE_COLUMNS:
        if col not in data.columns:
            data[col] = 0.0

    X = data[FEATURE_COLUMNS].copy()
    
    if TARGET_COLUMN in data.columns:
        y = data[TARGET_COLUMN].copy()
    else:
        y = pd.Series(index=data.index, dtype=float)

    logger.info(f"Extracted {len(FEATURE_COLUMNS)} features for {len(X)} records.")
    return X, y
