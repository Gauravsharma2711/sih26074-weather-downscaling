import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def validate_duplicates(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/duplicate_validation.csv",
    log_output_path: str = "data/validation/duplicate_removal_log.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Perform comprehensive duplicate validation:
    1. Exact duplicate rows across all standardized columns.
    2. Duplicate combinations of (panchayat_id, date, forecast_issue_date).
    3. Duplicate combinations of (panchayat_id, date).
    4. Conflicting duplicate records where weather or station telemetry differs.
    
    Generates:
    - data/validation/duplicate_validation.csv
    - data/validation/duplicate_removal_log.csv
    
    Removes ONLY exact duplicate rows (if present) from processed dataset.
    Does NOT remove conflicting records automatically.
    Never modifies raw data.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # 1. Exact duplicates
    exact_dup_mask = df.duplicated(keep=False)
    exact_dup_count = int(df.duplicated().sum())

    # 2. Duplicate (panchayat_id, date, forecast_issue_date)
    p_d_f_mask = df.duplicated(subset=["panchayat_id", "date", "forecast_issue_date"], keep=False)
    p_d_f_count = int(df.duplicated(subset=["panchayat_id", "date", "forecast_issue_date"]).sum())

    # 3. Duplicate (panchayat_id, date)
    p_d_mask = df.duplicated(subset=["panchayat_id", "date"], keep=False)
    p_d_count = int(df.duplicated(subset=["panchayat_id", "date"]).sum())

    # 4. Conflicting duplicate identification
    # Group by (panchayat_id, date) to see if forecast, actual, or station varies
    conflicting_indices = set()
    if p_d_mask.any():
        for (pid, dt), group in df[p_d_mask].groupby(["panchayat_id", "date"]):
            has_fc_conflict = group["block_forecast_rainfall_mm"].nunique(dropna=False) > 1
            has_act_conflict = group["actual_rainfall_mm"].nunique(dropna=False) > 1
            has_st_conflict = group["station_id"].nunique(dropna=False) > 1
            if has_fc_conflict or has_act_conflict or has_st_conflict:
                conflicting_indices.update(group.index)

    conflicting_dup_count = len(conflicting_indices)

    # Build validation status and reasons for every record
    validation_status = []
    validation_reasons = []

    for idx, row in df.iterrows():
        is_exact = exact_dup_mask.loc[idx]
        is_conflicting = idx in conflicting_indices
        is_pd_dup = p_d_mask.loc[idx]

        if is_exact:
            validation_status.append("EXACT_DUPLICATE")
            validation_reasons.append("Identical row exists across all fields (eligible for removal)")
        elif is_conflicting:
            validation_status.append("CONFLICTING_DUPLICATE")
            validation_reasons.append("Duplicate Panchayat/Date record with conflicting weather observations (flagged for review)")
        elif is_pd_dup:
            validation_status.append("CONSISTENT_DUPLICATE")
            validation_reasons.append("Duplicate Panchayat/Date with matching values (multiple issue dates)")
        else:
            validation_status.append("VALID")
            validation_reasons.append("Unique Panchayat/Date record")

    val_df = pd.DataFrame({
        "panchayat_id": df["panchayat_id"],
        "panchayat_name": df["panchayat_name"],
        "block_name": df["block_name"],
        "date": df["date"],
        "forecast_issue_date": df["forecast_issue_date"],
        "is_exact_duplicate": exact_dup_mask,
        "is_panchayat_date_duplicate": p_d_mask,
        "is_conflicting_duplicate": [idx in conflicting_indices for idx in df.index],
        "validation_status": validation_status,
        "validation_reason": validation_reasons
    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Duplicate validation report saved to {output_path} ({len(val_df)} records).")

    # Save duplicate removal log
    if exact_dup_count > 0:
        removal_log_df = df[df.duplicated(keep="first")].copy()
        removal_log_df["action"] = "REMOVED_EXACT_DUPLICATE"
    else:
        removal_log_df = pd.DataFrame(columns=list(df.columns) + ["action"])

    os.makedirs(os.path.dirname(log_output_path), exist_ok=True)
    removal_log_df.to_csv(log_output_path, index=False, encoding="utf-8")
    logger.info(f"Duplicate removal log saved to {log_output_path} ({len(removal_log_df)} removed rows).")

    stats = {
        "total_records": len(df),
        "exact_duplicate_count": exact_dup_count,
        "panchayat_issue_date_dup_count": p_d_f_count,
        "panchayat_date_dup_count": p_d_count,
        "conflicting_duplicate_count": conflicting_dup_count,
        "unique_records": len(df) - exact_dup_count,
        "removed_count": len(removal_log_df)
    }

    return val_df, removal_log_df, stats
