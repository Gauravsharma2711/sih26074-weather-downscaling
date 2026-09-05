import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

# Expected elevation bounds for Nashik District (Deccan plateau & Sahyadri Western Ghats)
# Typical terrain ranges from ~350m (plains) to ~1400m (Ghats peaks)
NASHIK_ELEVATION_MIN = 300
NASHIK_ELEVATION_MAX = 1500


def validate_elevation_data(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/elevation_validation.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Audit and validate elevation (elevation_m) for the Nashik pilot dataset:
    - Missing elevation
    - Zero elevation (potential placeholder)
    - Negative elevation
    - Physical boundary checks (inland Deccan / Sahyadri terrain)
    
    Generates data/validation/elevation_validation.csv.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    total_records = len(df)
    missing_count = 0
    zero_count = 0
    negative_count = 0
    valid_count = 0
    invalid_count = 0

    validation_records = []

    for _, row in df.iterrows():
        pid = row["panchayat_id"]
        pname = str(row["panchayat_name"])
        bname = str(row["block_name"])
        lat = row.get("panchayat_latitude")
        lon = row.get("panchayat_longitude")
        elev = row.get("elevation_m")

        reasons = []
        status = "VALID"

        # Check 1: Missing elevation
        if pd.isna(elev):
            reasons.append("Missing elevation value")
            status = "INVALID"
            missing_count += 1
        else:
            elev = float(elev)

            # Check 2: Zero elevation
            if elev == 0.0:
                reasons.append("Zero elevation value (sea-level placeholder)")
                status = "INVALID"
                zero_count += 1

            # Check 3: Negative elevation
            elif elev < 0.0:
                reasons.append(f"Negative elevation ({elev} m)")
                status = "INVALID"
                negative_count += 1

            # Check 4: Out of regional bounds
            elif elev < NASHIK_ELEVATION_MIN or elev > NASHIK_ELEVATION_MAX:
                reasons.append(f"Suspicious elevation ({elev} m) outside expected range [{NASHIK_ELEVATION_MIN}, {NASHIK_ELEVATION_MAX}] m")
                status = "WARNING"

        if status == "VALID":
            reasons.append("Passed physical elevation terrain checks")
            valid_count += 1
        elif status == "INVALID":
            invalid_count += 1
        elif status == "WARNING":
            valid_count += 1

        validation_records.append({
            "panchayat_id": pid,
            "panchayat_name": pname,
            "block_name": bname,
            "panchayat_latitude": lat,
            "panchayat_longitude": lon,
            "elevation_m": elev,
            "validation_status": status,
            "validation_reason": "; ".join(reasons)
        })

    val_df = pd.DataFrame(validation_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Elevation validation report saved to {output_path} ({len(val_df)} rows).")

    non_null_elev = df["elevation_m"].dropna()
    stats = {
        "total_records": total_records,
        "missing_elevation": missing_count,
        "zero_elevation": zero_count,
        "negative_elevation": negative_count,
        "minimum": float(non_null_elev.min()) if not non_null_elev.empty else None,
        "maximum": float(non_null_elev.max()) if not non_null_elev.empty else None,
        "mean": round(float(non_null_elev.mean()), 2) if not non_null_elev.empty else None,
        "median": float(non_null_elev.median()) if not non_null_elev.empty else None,
        "unique_elevation_values": int(non_null_elev.nunique()),
        "valid_records": valid_count,
        "invalid_records": invalid_count,
    }
    return val_df, stats
