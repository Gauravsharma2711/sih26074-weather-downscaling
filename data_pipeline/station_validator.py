import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Nashik & Northern Maharashtra bounding box for AWS/ARG stations
LAT_MIN, LAT_MAX = 19.0, 21.5
LON_MIN, LON_MAX = 73.0, 75.5


def validate_station_ground_truth(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/station_validation.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Audit and validate ground-truth weather station observations:
    - Missing station IDs
    - Missing / invalid station coordinates
    - Missing rainfall observations
    - -999.9 sentinel values (converted to missing in processed)
    - Negative rainfall values
    - Inconsistent coordinates for the same station
    - Conflicting station/date observations

    Generates data/validation/station_validation.csv.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # Group by station_id, station_latitude, station_longitude
    group_cols = ["station_id", "station_latitude", "station_longitude"]
    grouped = df.groupby(group_cols, sort=True)

    summary_records = []
    total_groups = len(grouped)

    for (st_id, st_lat, st_lon), group in grouped:
        rec_cnt = len(group)
        
        # Missing rainfall: either NaN, null, or sentinel string
        missing_rain = int(group["actual_rainfall_mm"].isnull().sum())
        
        # Negative rainfall count
        rain_numeric = pd.to_numeric(group["actual_rainfall_mm"], errors="coerce")
        neg_rain = int((rain_numeric < 0).sum())

        # Coordinate validity check
        invalid_coord = 0
        if pd.isna(st_lat) or pd.isna(st_lon):
            invalid_coord = rec_cnt
        elif not (LAT_MIN <= st_lat <= LAT_MAX and LON_MIN <= st_lon <= LON_MAX):
            invalid_coord = rec_cnt

        # Missing station ID check
        missing_id = pd.isna(st_id) or str(st_id).strip() == ""

        # Status determination
        if invalid_coord > 0 or missing_id:
            status = "INVALID"
        elif missing_rain > 0 or neg_rain > 0:
            status = "WARNING"
        else:
            status = "VALID"

        summary_records.append({
            "station_id": st_id,
            "station_latitude": st_lat,
            "station_longitude": st_lon,
            "record_count": rec_cnt,
            "missing_rainfall_count": missing_rain,
            "invalid_coordinate_count": invalid_coord,
            "negative_rainfall_count": neg_rain,
            "validation_status": status
        })

    val_df = pd.DataFrame(summary_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Station ground-truth validation report saved to {output_path} ({len(val_df)} station entries).")

    # Aggregate station & rainfall statistics
    unique_stations = df["station_id"].nunique()
    coord_variations = df.groupby("station_id")[["station_latitude", "station_longitude"]].nunique()
    multi_coord_stations = int((coord_variations.max(axis=1) > 1).sum())

    conflicts = df.groupby(["station_id", "date"])["actual_rainfall_mm"].nunique()
    conflicting_station_dates = int((conflicts > 1).sum())

    valid_actuals = pd.to_numeric(df["actual_rainfall_mm"], errors="coerce").dropna()

    stats = {
        "total_records": len(df),
        "unique_stations": unique_stations,
        "station_location_entries": total_groups,
        "multi_coord_stations": multi_coord_stations,
        "conflicting_station_dates": conflicting_station_dates,
        "missing_station_ids": int(df["station_id"].isnull().sum()),
        "missing_station_coords": int(df["station_latitude"].isnull().sum() + df["station_longitude"].isnull().sum()),
        "missing_rainfall_records": int(df["actual_rainfall_mm"].isnull().sum()),
        "negative_rainfall_records": int((valid_actuals < 0).sum()),
        "zero_rainfall_records": int((valid_actuals == 0).sum()),
        "min_actual_rainfall": float(valid_actuals.min()) if not valid_actuals.empty else None,
        "max_actual_rainfall": float(valid_actuals.max()) if not valid_actuals.empty else None,
        "mean_actual_rainfall": round(float(valid_actuals.mean()), 2) if not valid_actuals.empty else None,
    }
    return val_df, stats
