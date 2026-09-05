import os
import logging
from typing import Tuple
import pandas as pd

logger = logging.getLogger(__name__)


def validate_administrative_data(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    val_output_path: str = "data/validation/administrative_validation.csv",
    summary_output_path: str = "data/validation/nashik_block_summary.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform comprehensive administrative validation on the Nashik dataset:
    1. Validates that all records belong to 'Nashik' district.
    2. Verifies consistency of Panchayat IDs and LGD codes.
    3. Checks that no Panchayat belongs to multiple blocks or districts.
    4. Identifies duplicate LGD codes and duplicate Panchayat IDs.
    5. Flags missing administrative fields.
    6. Generates:
       - data/validation/administrative_validation.csv
       - data/validation/nashik_block_summary.csv
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # 1. Identify LGD codes that appear in multiple rows
    lgd_counts = df["lgd_code"].value_counts()
    duplicate_lgds = set(lgd_counts[lgd_counts > 1].index)

    # 2. Identify Panchayat IDs that appear in multiple rows
    pid_counts = df["panchayat_id"].value_counts()
    duplicate_pids = set(pid_counts[pid_counts > 1].index)

    # 3. Check for Panchayats mapped to multiple blocks or districts
    pid_to_blocks = df.groupby("panchayat_id")["block_name"].nunique()
    multi_block_pids = set(pid_to_blocks[pid_to_blocks > 1].index)

    pid_to_districts = df.groupby("panchayat_id")["district_name"].nunique()
    multi_district_pids = set(pid_to_districts[pid_to_districts > 1].index)

    validation_records = []

    for _, row in df.iterrows():
        pid = row["panchayat_id"]
        lgd = row["lgd_code"]
        pname = str(row["panchayat_name"])
        bname = str(row["block_name"])
        dname = str(row["district_name"])

        reasons = []
        status = "VALID"

        # Check 1: Missing administrative fields
        if pd.isna(pid) or pd.isna(lgd) or not pname or not bname or not dname:
            reasons.append("Missing administrative field")
            status = "INVALID"

        # Check 2: District must be Nashik
        if dname != "Nashik":
            reasons.append(f"Invalid district '{dname}' (expected 'Nashik')")
            status = "INVALID"

        # Check 3: Multi-district or Multi-block mapping
        if pid in multi_district_pids:
            reasons.append("Panchayat ID maps to multiple districts")
            status = "INVALID"

        if pid in multi_block_pids:
            reasons.append("Panchayat ID maps to multiple blocks")
            status = "INVALID"

        # Check 4: Duplicate Panchayat IDs
        if pid in duplicate_pids:
            reasons.append(f"Duplicate Panchayat ID ({pid}) in dataset")
            if status != "INVALID":
                status = "WARNING"

        # Check 5: Duplicate LGD codes
        if lgd in duplicate_lgds:
            count = lgd_counts[lgd]
            reasons.append(f"LGD code ({lgd}) appears in {count} records")
            if status != "INVALID":
                status = "WARNING"

        if not reasons:
            reasons.append("Passed all administrative integrity checks")

        validation_records.append({
            "panchayat_id": pid,
            "lgd_code": lgd,
            "panchayat_name": pname,
            "block_name": bname,
            "district_name": dname,
            "validation_status": status,
            "validation_reason": "; ".join(reasons)
        })

    val_df = pd.DataFrame(validation_records)
    os.makedirs(os.path.dirname(val_output_path), exist_ok=True)
    val_df.to_csv(val_output_path, index=False, encoding="utf-8")
    logger.info(f"Administrative validation report saved to {val_output_path} ({len(val_df)} rows).")

    # Generate Nashik Block Summary
    block_summary = (
        df.groupby("block_name")
        .agg(
            unique_panchayat_count=("panchayat_id", "nunique"),
            record_count=("panchayat_id", "count")
        )
        .reset_index()
        .sort_values(by="block_name")
    )

    os.makedirs(os.path.dirname(summary_output_path), exist_ok=True)
    block_summary.to_csv(summary_output_path, index=False, encoding="utf-8")
    logger.info(f"Nashik block summary saved to {summary_output_path} ({len(block_summary)} blocks).")

    return val_df, block_summary
