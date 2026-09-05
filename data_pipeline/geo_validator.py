import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

# Bounding box definitions
# Nashik District bounding box: 19.0°N - 21.0°N, 73.0°E - 75.2°E
NASHIK_LAT_MIN, NASHIK_LAT_MAX = 19.0, 21.0
NASHIK_LON_MIN, NASHIK_LON_MAX = 73.0, 75.2

# Maharashtra State bounding box: 15.6°N - 22.1°N, 72.6°E - 80.9°E
MAHARASHTRA_LAT_MIN, MAHARASHTRA_LAT_MAX = 15.6, 22.1
MAHARASHTRA_LON_MIN, MAHARASHTRA_LON_MAX = 72.6, 80.9


def validate_geographic_coordinates(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/geographic_validation.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate geographic coordinates for all Panchayats in the dataset:
    - Missing latitude / longitude
    - Global bounds (-90 to +90 lat, -180 to +180 lon)
    - Zero coordinates (0, 0)
    - Out-of-bounds relative to Nashik / Maharashtra pilot region
    - Duplicate coordinates (shared centroids across multiple entries)
    
    Generates data/validation/geographic_validation.csv.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # Find duplicate coordinate pairs
    coord_counts = df.groupby(["panchayat_latitude", "panchayat_longitude"]).size()
    dup_coords = set(coord_counts[coord_counts > 1].index)

    validation_records = []
    total_records = len(df)
    valid_count = 0
    invalid_count = 0
    missing_count = 0
    duplicate_count = 0

    for _, row in df.iterrows():
        pid = row["panchayat_id"]
        lgd = row["lgd_code"]
        pname = str(row["panchayat_name"])
        bname = str(row["block_name"])
        dname = str(row["district_name"])
        lat = row.get("panchayat_latitude")
        lon = row.get("panchayat_longitude")

        reasons = []
        status = "VALID"

        # Check 1: Missing coordinates
        if pd.isna(lat) or pd.isna(lon):
            reasons.append("Missing latitude or longitude")
            status = "INVALID"
            missing_count += 1
        else:
            lat = float(lat)
            lon = float(lon)

            # Check 2: Zero coordinates
            if lat == 0.0 or lon == 0.0:
                reasons.append("Zero coordinate value (0.0, 0.0)")
                status = "INVALID"

            # Check 3: Global physical limits
            if not (-90.0 <= lat <= 90.0):
                reasons.append(f"Latitude ({lat}) outside global range [-90, +90]")
                status = "INVALID"
            if not (-180.0 <= lon <= 180.0):
                reasons.append(f"Longitude ({lon}) outside global range [-180, +180]")
                status = "INVALID"

            # Check 4: Maharashtra & Nashik bounding boxes
            if not (MAHARASHTRA_LAT_MIN <= lat <= MAHARASHTRA_LAT_MAX and MAHARASHTRA_LON_MIN <= lon <= MAHARASHTRA_LON_MAX):
                reasons.append(f"Coordinates ({lat}, {lon}) outside Maharashtra region")
                status = "INVALID"
            elif not (NASHIK_LAT_MIN <= lat <= NASHIK_LAT_MAX and NASHIK_LON_MIN <= lon <= NASHIK_LON_MAX):
                reasons.append(f"Coordinates ({lat}, {lon}) outside Nashik pilot bounding box")
                if status != "INVALID":
                    status = "WARNING"

            # Check 5: Duplicate coordinates
            if (lat, lon) in dup_coords:
                count = coord_counts[(lat, lon)]
                reasons.append(f"Duplicate coordinates shared across {count} records")
                duplicate_count += 1
                if status == "VALID":
                    status = "WARNING"

        if status == "VALID":
            reasons.append("Passed all geographic and bounding box checks")
            valid_count += 1
        elif status == "INVALID":
            invalid_count += 1
        elif status == "WARNING":
            valid_count += 1

        validation_records.append({
            "panchayat_id": pid,
            "lgd_code": lgd,
            "panchayat_name": pname,
            "block_name": bname,
            "district_name": dname,
            "panchayat_latitude": lat,
            "panchayat_longitude": lon,
            "validation_status": status,
            "validation_reason": "; ".join(reasons)
        })

    val_df = pd.DataFrame(validation_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Geographic validation report saved to {output_path} ({len(val_df)} rows).")

    stats = {
        "total_records": total_records,
        "valid_records": valid_count,
        "invalid_records": invalid_count,
        "missing_coordinates": missing_count,
        "duplicate_coordinates": df.duplicated(subset=["panchayat_latitude", "panchayat_longitude"]).sum()
    }
    return val_df, stats
