import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

from src.utils.geospatial import haversine_distance

logger = logging.getLogger(__name__)

# Tolerance in kilometers for validating distance discrepancies
TOLERANCE_KM = 1.0


def validate_station_distances(
    raw_input_path: str = "data/raw/nashik_panchayat_weather_raw.csv",
    output_path: str = "data/validation/distance_validation.csv",
    tolerance_km: float = TOLERANCE_KM
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate existing station distances against exact Haversine computed distances.
    
    Calculates:
    - calculated_station_distance_km from (panchayat_lat, lon) -> (station_lat, lon)
    - distance_difference_km = abs(station_distance_km - calculated_station_distance_km)
    - validation_status (VALID if diff <= tolerance, WARNING otherwise)

    Outputs:
    data/validation/distance_validation.csv
    """
    if not os.path.exists(raw_input_path):
        raise FileNotFoundError(f"Raw dataset not found at: {raw_input_path}")

    # Read raw dataset safely
    try:
        df = pd.read_csv(raw_input_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(raw_input_path, encoding="latin1")

    # Resolve coordinate field names
    p_lat_col = "panchayat_latitude" if "panchayat_latitude" in df.columns else "latitude"
    p_lon_col = "panchayat_longitude" if "panchayat_longitude" in df.columns else "longitude"
    st_lat_col = "station_latitude"
    st_lon_col = "station_longitude"
    raw_dist_col = "station_distance_km"

    p_lat = pd.to_numeric(df[p_lat_col], errors="coerce")
    p_lon = pd.to_numeric(df[p_lon_col], errors="coerce")
    st_lat = pd.to_numeric(df[st_lat_col], errors="coerce")
    st_lon = pd.to_numeric(df[st_lon_col], errors="coerce")
    existing_dist = pd.to_numeric(df[raw_dist_col], errors="coerce")

    # Compute Haversine distance
    calculated_dist = haversine_distance(p_lat, p_lon, st_lat, st_lon)
    diff = (existing_dist - calculated_dist).abs()

    # Determine validation status
    status = np.where(
        existing_dist.isnull() | calculated_dist.isnull(),
        "INVALID",
        np.where(diff <= tolerance_km, "VALID", "WARNING")
    )

    clean_station_ids = df["station_id"].astype(str).str.replace("\xa0", " ", regex=False).str.strip()

    val_df = pd.DataFrame({
        "panchayat_id": df["panchayat_id"],
        "station_id": clean_station_ids,
        "station_distance_km": existing_dist.round(2),
        "calculated_station_distance_km": calculated_dist.round(2),
        "distance_difference_km": diff.round(4),
        "validation_status": status
    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Distance validation report saved to {output_path} ({len(val_df)} records).")

    valid_count = int((val_df["validation_status"] == "VALID").sum())
    warning_count = int((val_df["validation_status"] == "WARNING").sum())
    invalid_count = int((val_df["validation_status"] == "INVALID").sum())

    stats = {
        "total_records": len(df),
        "valid_records": valid_count,
        "warning_records": warning_count,
        "invalid_records": invalid_count,
        "tolerance_km": tolerance_km,
        "min_difference_km": round(float(diff.min()), 4),
        "max_difference_km": round(float(diff.max()), 4),
        "mean_difference_km": round(float(diff.mean()), 4),
        "min_calculated_dist_km": round(float(calculated_dist.min()), 2),
        "max_calculated_dist_km": round(float(calculated_dist.max()), 2),
        "mean_calculated_dist_km": round(float(calculated_dist.mean()), 2),
    }
    return val_df, stats
