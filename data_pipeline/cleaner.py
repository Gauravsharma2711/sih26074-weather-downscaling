import os
import logging
from typing import List
import pandas as pd

from src.utils.geospatial import haversine_distance

logger = logging.getLogger(__name__)

# Exact 16-field standardized schema for SIH26074
STANDARDIZED_COLUMNS: List[str] = [
    "panchayat_id",
    "lgd_code",
    "panchayat_name",
    "block_name",
    "district_name",
    "panchayat_latitude",
    "panchayat_longitude",
    "elevation_m",
    "date",
    "forecast_issue_date",
    "block_forecast_rainfall_mm",
    "station_id",
    "station_latitude",
    "station_longitude",
    "station_distance_km",
    "actual_rainfall_mm",
]


def clean_raw_weather_data(
    input_path: str = "data/raw/nashik_panchayat_weather_raw.csv",
    output_path: str = "data/processed/nashik_weather_clean.csv"
) -> pd.DataFrame:
    """
    Clean and standardize the raw Nashik Panchayat weather dataset:
    1. Reads raw data safely with encoding fallback.
    2. Drops empty unnamed trailing columns.
    3. Renames 'latitude' -> 'panchayat_latitude' and 'longitude' -> 'panchayat_longitude'.
    4. Cleans whitespace & non-breaking spaces (\xa0) from textual fields.
    5. Formats dates into standard ISO YYYY-MM-DD.
    6. Converts numeric fields and enforces physical constraints (rainfall >= 0).
    7. Selects and orders exactly the 16 standardized schema fields.
    8. Saves cleaned dataset to output_path without modifying the raw dataset.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw dataset not found at: {input_path}")

    # Read with latin1 fallback for non-breaking characters
    try:
        df = pd.read_csv(input_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(input_path, encoding="latin1")

    # 1. Drop unnamed trailing columns
    unnamed_cols = [c for c in df.columns if c.startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    # 2. Rename coordinate fields if present
    rename_mapping = {}
    if "latitude" in df.columns and "panchayat_latitude" not in df.columns:
        rename_mapping["latitude"] = "panchayat_latitude"
    if "longitude" in df.columns and "panchayat_longitude" not in df.columns:
        rename_mapping["longitude"] = "panchayat_longitude"
    if rename_mapping:
        df = df.rename(columns=rename_mapping)

    # 3. Clean text columns (strip spaces, replace non-breaking spaces \xa0)
    text_columns = ["panchayat_name", "block_name", "district_name", "station_id"]
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("\xa0", " ", regex=False).str.strip()

    # 4. Enforce Nashik pilot district boundary (Rule 1: Keep only Nashik records)
    if "district_name" in df.columns:
        df = df[df["district_name"].str.strip().str.lower() == "nashik"].copy()

    # 5. Standardize and parse dates (supporting day-first formats like 01-09-2026)
    for date_col in ["date", "forecast_issue_date"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True).dt.strftime("%Y-%m-%d")

    # 5. Standardize numeric columns
    numeric_cols = [
        "panchayat_latitude", "panchayat_longitude",
        "elevation_m", "station_latitude", "station_longitude",
        "station_distance_km", "block_forecast_rainfall_mm", "actual_rainfall_mm"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 6. Calculate trusted station distance (km) using Haversine formula
    if all(col in df.columns for col in ["panchayat_latitude", "panchayat_longitude", "station_latitude", "station_longitude"]):
        df["station_distance_km"] = haversine_distance(
            df["panchayat_latitude"], df["panchayat_longitude"],
            df["station_latitude"], df["station_longitude"]
        ).round(2)

    # 7. Convert -999.9 sentinel and invalid rainfall to missing/null (NaN)
    # Never treat -999.9 as rainfall and do not replace missing rainfall with zero
    if "actual_rainfall_mm" in df.columns:
        df["actual_rainfall_mm"] = df["actual_rainfall_mm"].replace(-999.9, pd.NA)
        # Convert any negative values to NA as well
        df.loc[df["actual_rainfall_mm"] < 0, "actual_rainfall_mm"] = pd.NA
    if "block_forecast_rainfall_mm" in df.columns:
        df["block_forecast_rainfall_mm"] = df["block_forecast_rainfall_mm"].replace(-999.9, pd.NA)
        df.loc[df["block_forecast_rainfall_mm"] < 0, "block_forecast_rainfall_mm"] = pd.NA

    # 8. Select and enforce exact standardized 16-column order
    available_cols = [c for c in STANDARDIZED_COLUMNS if c in df.columns]
    clean_df = df[available_cols].copy()

    # 9. Remove only exact duplicate rows from the processed dataset
    clean_df = clean_df.drop_duplicates().reset_index(drop=True)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clean_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Cleaned dataset saved to {output_path} ({len(clean_df)} rows, {len(clean_df.columns)} columns).")
    return clean_df
