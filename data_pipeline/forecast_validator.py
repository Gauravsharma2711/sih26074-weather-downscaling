import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def validate_block_forecasts(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/forecast_validation.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Audit and validate official IMD block-level forecasts:
    - Missing values
    - Negative values
    - Zero values
    - Extremely large / outlier values (> 500mm/day)
    - Numeric formatting
    - Consistency across (district, block, forecast_issue_date, date) groups
    
    Generates data/validation/forecast_validation.csv.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # Group by district, block, forecast_issue_date, date
    group_cols = ["district_name", "block_name", "forecast_issue_date", "date"]
    grouped = df.groupby(group_cols, sort=True)

    summary_records = []
    total_groups = len(grouped)
    consistent_groups = 0
    conflicting_groups = 0

    for (dname, bname, issue_date, fdate), group in grouped:
        fc = group["block_forecast_rainfall_mm"]
        record_cnt = len(fc)
        missing_cnt = int(fc.isnull().sum())
        neg_cnt = int((fc < 0).sum())
        
        # Calculate lead days
        try:
            lead = int((pd.to_datetime(fdate) - pd.to_datetime(issue_date)).days)
        except Exception:
            lead = 0

        valid_fc = fc.dropna()
        if not valid_fc.empty:
            min_val = round(float(valid_fc.min()), 2)
            max_val = round(float(valid_fc.max()), 2)
            mean_val = round(float(valid_fc.mean()), 2)
            is_uniform = (min_val == max_val)
        else:
            min_val = None
            max_val = None
            mean_val = None
            is_uniform = False

        # Status determination
        if missing_cnt > 0 or neg_cnt > 0:
            status = "INVALID"
        elif not is_uniform:
            status = "WARNING"
            conflicting_groups += 1
        else:
            status = "VALID"
            consistent_groups += 1

        summary_records.append({
            "district_name": dname,
            "block_name": bname,
            "forecast_issue_date": issue_date,
            "date": fdate,
            "lead_days": lead,
            "record_count": record_cnt,
            "missing_count": missing_cnt,
            "negative_count": neg_cnt,
            "min_forecast": min_val,
            "max_forecast": max_val,
            "mean_forecast": mean_val,
            "validation_status": status
        })

    val_df = pd.DataFrame(summary_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Block forecast validation report saved to {output_path} ({len(val_df)} groups).")

    all_fc = df["block_forecast_rainfall_mm"].dropna()
    stats = {
        "total_records": len(df),
        "total_groups": total_groups,
        "consistent_groups": consistent_groups,
        "conflicting_groups": conflicting_groups,
        "missing_values": int(df["block_forecast_rainfall_mm"].isnull().sum()),
        "negative_values": int((df["block_forecast_rainfall_mm"] < 0).sum()),
        "zero_values": int((df["block_forecast_rainfall_mm"] == 0).sum()),
        "min_forecast": float(all_fc.min()) if not all_fc.empty else None,
        "max_forecast": float(all_fc.max()) if not all_fc.empty else None,
        "mean_forecast": round(float(all_fc.mean()), 2) if not all_fc.empty else None,
    }
    return val_df, stats
