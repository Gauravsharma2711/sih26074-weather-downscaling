import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

TRAIN_RATIO = 0.80


def split_features_chronologically(
    input_path: str = "data/features/nashik_rainfall_features.csv",
    train_output_path: str = "data/features/nashik_train.csv",
    test_output_path: str = "data/features/nashik_test.csv",
    summary_output_path: str = "data/validation/split_summary.csv",
    train_ratio: float = TRAIN_RATIO
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Perform strict chronological train/test split (80/20):
    1. Sorts all records strictly by date (and panchayat_id for deterministic ordering).
    2. Takes earliest 80% as TRAIN, latest 20% as TEST without shuffling.
    3. Verifies zero temporal lookahead leakage.
    4. Outputs:
       - data/features/nashik_train.csv
       - data/features/nashik_test.csv
       - data/validation/split_summary.csv
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Feature dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # 1. Sort records strictly chronologically
    df_sorted = df.sort_values(by=["date", "panchayat_id"]).reset_index(drop=True)

    # 2. Compute split index
    total_rows = len(df_sorted)
    split_idx = int(total_rows * train_ratio)

    train_df = df_sorted.iloc[:split_idx].copy().reset_index(drop=True)
    test_df = df_sorted.iloc[split_idx:].copy().reset_index(drop=True)

    # 3. Temporal leakage audit
    train_start = str(train_df["date"].min()) if len(train_df) > 0 else ""
    train_end = str(train_df["date"].max()) if len(train_df) > 0 else ""
    test_start = str(test_df["date"].min()) if len(test_df) > 0 else ""
    test_end = str(test_df["date"].max()) if len(test_df) > 0 else ""

    if len(train_df) > 0 and len(test_df) > 0:
        is_leakage_free = bool(train_end <= test_start)
    else:
        is_leakage_free = True

    if not is_leakage_free:
        logger.warning(f"Temporal anomaly detected: train_end ({train_end}) > test_start ({test_start})")

    # Save train & test sets
    os.makedirs(os.path.dirname(train_output_path), exist_ok=True)
    train_df.to_csv(train_output_path, index=False, encoding="utf-8")
    test_df.to_csv(test_output_path, index=False, encoding="utf-8")
    logger.info(f"Train dataset saved to {train_output_path} ({len(train_df)} rows).")
    logger.info(f"Test dataset saved to {test_output_path} ({len(test_df)} rows).")

    # 4. Generate Split Summary Report
    summary_record = {
        "train_start_date": train_start,
        "train_end_date": train_end,
        "train_rows": len(train_df),
        "test_start_date": test_start,
        "test_end_date": test_end,
        "test_rows": len(test_df),
        "unique_train_panchayats": train_df["panchayat_id"].nunique(),
        "unique_test_panchayats": test_df["panchayat_id"].nunique(),
        "unique_train_blocks": train_df["block_name"].nunique(),
        "unique_test_blocks": test_df["block_name"].nunique(),
    }

    summary_df = pd.DataFrame([summary_record])
    os.makedirs(os.path.dirname(summary_output_path), exist_ok=True)
    summary_df.to_csv(summary_output_path, index=False, encoding="utf-8")
    logger.info(f"Split summary saved to {summary_output_path}.")

    stats = {
        **summary_record,
        "total_rows": total_rows,
        "train_pct": round(len(train_df) / total_rows * 100.0, 2),
        "test_pct": round(len(test_df) / total_rows * 100.0, 2),
        "temporal_leakage_free": is_leakage_free,
    }

    return train_df, test_df, summary_df, stats
