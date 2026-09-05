import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

BASELINE_COLUMNS = [
    "panchayat_id",
    "panchayat_name",
    "block_name",
    "date",
    "forecast_issue_date",
    "lead_days",
    "block_forecast_rainfall_mm",
    "actual_rainfall_mm",
]


def calculate_mae_rmse(y_pred: pd.Series, y_true: pd.Series) -> Tuple[float, float]:
    """Calculate Mean Absolute Error and Root Mean Squared Error."""
    err = y_pred - y_true
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    return round(mae, 4), round(rmse, 4)


def build_baseline_dataset(
    clean_df: pd.DataFrame,
    output_path: str = "data/processed/nashik_baseline_dataset.csv",
    metrics_output_path: str = "data/validation/baseline_metrics.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Build the official baseline benchmark dataset:
    - In SIH26074, the baseline benchmark uses the official IMD Block-level forecast
      directly as the predicted rainfall for each Panchayat (lead_days persistence).
    - Uses only records where both forecast and actual rainfall exist.
    - Calculates baseline MAE and RMSE overall and grouped by lead_days, block, and month.
    - Creates data/processed/nashik_baseline_dataset.csv and data/validation/baseline_metrics.csv.
    """
    df = clean_df.copy()

    # Filter: use only records where both forecast and actual rainfall exist
    valid_mask = df["block_forecast_rainfall_mm"].notnull() & df["actual_rainfall_mm"].notnull()
    df = df[valid_mask].copy()

    # Calculate lead_days
    if "date" in df.columns and "forecast_issue_date" in df.columns:
        date_series = pd.to_datetime(df["date"], errors="coerce")
        issue_series = pd.to_datetime(df["forecast_issue_date"], errors="coerce")
        df["lead_days"] = (date_series - issue_series).dt.days.fillna(0).astype(int).clip(lower=0)
    elif "lead_days" not in df.columns:
        df["lead_days"] = 0

    # Extract month for temporal metrics evaluation
    df["month_name"] = pd.to_datetime(df["date"]).dt.strftime("%B")

    # Select exact standardized 8 baseline fields
    available_cols = [c for c in BASELINE_COLUMNS if c in df.columns]
    baseline_df = df[available_cols].copy()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    baseline_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Baseline dataset saved to {output_path} ({len(baseline_df)} rows).")

    # -------------------------------------------------------------
    # Calculate Baseline Error Metrics
    # -------------------------------------------------------------
    y_pred = df["block_forecast_rainfall_mm"]
    y_true = df["actual_rainfall_mm"]

    overall_mae, overall_rmse = calculate_mae_rmse(y_pred, y_true)

    metrics_records = []

    # 1. Overall Metrics
    metrics_records.append({
        "group_type": "OVERALL",
        "group_name": "Nashik District (Overall)",
        "record_count": len(df),
        "mean_forecast_mm": round(float(y_pred.mean()), 2),
        "mean_actual_mm": round(float(y_true.mean()), 2),
        "mae_mm": overall_mae,
        "rmse_mm": overall_rmse
    })

    # 2. Group by lead_days
    for lead, group in df.groupby("lead_days", sort=True):
        m_mae, m_rmse = calculate_mae_rmse(group["block_forecast_rainfall_mm"], group["actual_rainfall_mm"])
        metrics_records.append({
            "group_type": "LEAD_DAYS",
            "group_name": f"Lead {lead} Day(s)",
            "record_count": len(group),
            "mean_forecast_mm": round(float(group["block_forecast_rainfall_mm"].mean()), 2),
            "mean_actual_mm": round(float(group["actual_rainfall_mm"].mean()), 2),
            "mae_mm": m_mae,
            "rmse_mm": m_rmse
        })

    # 3. Group by block_name
    for bname, group in df.groupby("block_name", sort=True):
        m_mae, m_rmse = calculate_mae_rmse(group["block_forecast_rainfall_mm"], group["actual_rainfall_mm"])
        metrics_records.append({
            "group_type": "BLOCK",
            "group_name": bname,
            "record_count": len(group),
            "mean_forecast_mm": round(float(group["block_forecast_rainfall_mm"].mean()), 2),
            "mean_actual_mm": round(float(group["actual_rainfall_mm"].mean()), 2),
            "mae_mm": m_mae,
            "rmse_mm": m_rmse
        })

    # 4. Group by month
    for mname, group in df.groupby("month_name", sort=False):
        m_mae, m_rmse = calculate_mae_rmse(group["block_forecast_rainfall_mm"], group["actual_rainfall_mm"])
        metrics_records.append({
            "group_type": "MONTH",
            "group_name": mname,
            "record_count": len(group),
            "mean_forecast_mm": round(float(group["block_forecast_rainfall_mm"].mean()), 2),
            "mean_actual_mm": round(float(group["actual_rainfall_mm"].mean()), 2),
            "mae_mm": m_mae,
            "rmse_mm": m_rmse
        })

    metrics_df = pd.DataFrame(metrics_records)
    os.makedirs(os.path.dirname(metrics_output_path), exist_ok=True)
    metrics_df.to_csv(metrics_output_path, index=False, encoding="utf-8")
    logger.info(f"Baseline metrics report saved to {metrics_output_path} ({len(metrics_df)} rows).")

    stats = {
        "total_records": len(df),
        "overall_mae": overall_mae,
        "overall_rmse": overall_rmse,
        "mean_forecast_mm": round(float(y_pred.mean()), 2),
        "mean_actual_mm": round(float(y_true.mean()), 2),
    }

    return baseline_df, metrics_df, stats
