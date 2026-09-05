import os
import logging
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Canonical metadata fields (NOT ML features)
METADATA_COLUMNS: List[str] = [
    "panchayat_id",
    "lgd_code",
    "panchayat_name",
    "block_name",
    "district_name",
    "station_id",
    "date",
    "forecast_issue_date",
]

# Canonical ML predictor features (X)
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

# Target variable (y)
TARGET_COLUMN: str = "actual_rainfall_mm"


def build_rainfall_features(
    clean_df: pd.DataFrame,
    output_path: str = "data/features/nashik_rainfall_features.csv",
    summary_output_path: str = "data/validation/feature_summary.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Build the ML feature dataset for rainfall downscaling:
    1. Extracts calendar features: month = month(date), day_of_year = day_of_year(date).
    2. Calculates lead_days = date - forecast_issue_date.
    3. Retains essential metadata fields (not for model training).
    4. Produces data/features/nashik_rainfall_features.csv and data/validation/feature_summary.csv.
    """
    df = clean_df.copy()

    # 1. Parse dates and create calendar features
    date_series = pd.to_datetime(df["date"], errors="coerce")
    df["month"] = date_series.dt.month
    df["day_of_year"] = date_series.dt.dayofyear

    # 2. Compute forecast lead days (lead_days = date - forecast_issue_date)
    if "forecast_issue_date" in df.columns:
        issue_series = pd.to_datetime(df["forecast_issue_date"], errors="coerce")
        df["lead_days"] = (date_series - issue_series).dt.days.fillna(0).astype(int).clip(lower=0)
    elif "lead_days" not in df.columns:
        df["lead_days"] = 0

    # 3. Organize exact columns: Metadata -> Features -> Target
    all_target_columns = METADATA_COLUMNS + FEATURE_COLUMNS + [TARGET_COLUMN]
    available_cols = [c for c in all_target_columns if c in df.columns]
    feature_df = df[available_cols].copy()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    feature_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Rainfall feature dataset saved to {output_path} ({len(feature_df)} rows, {len(feature_df.columns)} columns).")

    # -------------------------------------------------------------
    # Build Feature Summary & Validation Report
    # -------------------------------------------------------------
    total_rows = len(feature_df)
    
    # Training eligible: Target is NOT null and all 8 features are NOT null
    features_present = feature_df[FEATURE_COLUMNS].notnull().all(axis=1)
    target_present = feature_df[TARGET_COLUMN].notnull()
    training_eligible = int((features_present & target_present).sum())
    prediction_only = int((features_present & ~target_present).sum())

    summary_records = []
    
    # Analyze all columns
    for col in available_cols:
        role = "METADATA" if col in METADATA_COLUMNS else ("TARGET" if col == TARGET_COLUMN else "ML_FEATURE")
        missing_cnt = int(feature_df[col].isnull().sum())
        missing_pct = round((missing_cnt / total_rows) * 100.0, 2)
        
        # Calculate statistics for numeric fields
        if pd.api.types.is_numeric_dtype(feature_df[col]):
            valid_s = feature_df[col].dropna()
            min_val = round(float(valid_s.min()), 4) if not valid_s.empty else None
            max_val = round(float(valid_s.max()), 4) if not valid_s.empty else None
            mean_val = round(float(valid_s.mean()), 4) if not valid_s.empty else None
            med_val = round(float(valid_s.median()), 4) if not valid_s.empty else None
        else:
            min_val = None
            max_val = None
            mean_val = None
            med_val = None

        summary_records.append({
            "column_name": col,
            "column_role": role,
            "data_type": str(feature_df[col].dtype),
            "total_rows": total_rows,
            "training_eligible_rows": training_eligible,
            "prediction_only_rows": prediction_only,
            "missing_count": missing_cnt,
            "missing_pct": missing_pct,
            "min_val": min_val,
            "max_val": max_val,
            "mean_val": mean_val,
            "median_val": med_val,
        })

    summary_df = pd.DataFrame(summary_records)
    os.makedirs(os.path.dirname(summary_output_path), exist_ok=True)
    summary_df.to_csv(summary_output_path, index=False, encoding="utf-8")
    logger.info(f"Feature summary report saved to {summary_output_path} ({len(summary_df)} columns evaluated).")

    stats = {
        "total_rows": total_rows,
        "training_eligible_rows": training_eligible,
        "prediction_only_rows": prediction_only,
        "feature_count": len(FEATURE_COLUMNS),
        "metadata_count": len(METADATA_COLUMNS),
    }

    return feature_df, summary_df, stats
