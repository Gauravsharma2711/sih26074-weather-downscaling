import os
import logging
from typing import Dict, Any, Tuple
import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.app.core.database import engine
from backend.app.models.panchayat_weather import PanchayatWeatherData

logger = logging.getLogger(__name__)


def load_clean_data_to_supabase(
    csv_path: str = "data/processed/nashik_weather_clean.csv",
    batch_size: int = 250,
    summary_output_path: str = "data/validation/supabase_verification.csv"
) -> Tuple[int, Dict[str, Any]]:
    """
    Load validated processed Nashik weather dataset into Supabase PostgreSQL table: panchayat_weather_data.
    
    Rules enforced:
    1. Only loads clean processed dataset (data/processed/nashik_weather_clean.csv).
    2. Preserves NULL values (None instead of NaN).
    3. Preserves date formatting correctly (YYYY-MM-DD).
    4. Preserves rainfall units as mm.
    5. Never inserts -999.9 sentinels.
    6. Uses PostgreSQL ON CONFLICT (panchayat_id) DO UPDATE to avoid duplicates and safely upsert.
    7. Runs comprehensive database verification queries.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Processed dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8")
    total_records = len(df)
    logger.info(f"Preparing to upload {total_records} records from {csv_path} to Supabase...")

    # Convert DataFrame records to dicts with proper Python types and None for NaNs
    records_to_insert = []
    for _, row in df.iterrows():
        record = {
            "panchayat_id": int(row["panchayat_id"]),
            "lgd_code": int(row["lgd_code"]),
            "panchayat_name": str(row["panchayat_name"]) if pd.notnull(row["panchayat_name"]) else None,
            "block_name": str(row["block_name"]) if pd.notnull(row["block_name"]) else None,
            "district_name": str(row["district_name"]) if pd.notnull(row["district_name"]) else None,
            "panchayat_latitude": float(row["panchayat_latitude"]) if pd.notnull(row["panchayat_latitude"]) else None,
            "panchayat_longitude": float(row["panchayat_longitude"]) if pd.notnull(row["panchayat_longitude"]) else None,
            "elevation_m": float(row["elevation_m"]) if pd.notnull(row["elevation_m"]) else None,
            "date": str(row["date"]) if pd.notnull(row["date"]) else None,
            "forecast_issue_date": str(row["forecast_issue_date"]) if pd.notnull(row["forecast_issue_date"]) else None,
            "block_forecast_rainfall_mm": float(row["block_forecast_rainfall_mm"]) if pd.notnull(row["block_forecast_rainfall_mm"]) else None,
            "station_id": str(row["station_id"]) if pd.notnull(row["station_id"]) else None,
            "station_latitude": float(row["station_latitude"]) if pd.notnull(row["station_latitude"]) else None,
            "station_longitude": float(row["station_longitude"]) if pd.notnull(row["station_longitude"]) else None,
            "station_distance_km": float(row["station_distance_km"]) if pd.notnull(row["station_distance_km"]) else None,
            "actual_rainfall_mm": float(row["actual_rainfall_mm"]) if pd.notnull(row["actual_rainfall_mm"]) and float(row["actual_rainfall_mm"]) != -999.9 else None,
        }
        records_to_insert.append(record)

    # Batch Upsert using SQLAlchemy PostgreSQL dialect
    inserted_count = 0
    with engine.begin() as conn:
        for i in range(0, len(records_to_insert), batch_size):
            chunk = records_to_insert[i : i + batch_size]
            stmt = pg_insert(PanchayatWeatherData).values(chunk)
            
            # Upsert update dict: update all non-PK columns on conflict
            update_dict = {
                c.name: stmt.excluded[c.name]
                for c in PanchayatWeatherData.__table__.columns
                if c.name != "panchayat_id"
            }
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["panchayat_id"],
                set_=update_dict
            )
            conn.execute(upsert_stmt)
            inserted_count += len(chunk)
            logger.info(f"Uploaded batch {i // batch_size + 1} ({inserted_count}/{total_records} records)...")

    # Run Database Verification
    verification_results = verify_supabase_data(summary_output_path=summary_output_path)
    return inserted_count, verification_results


def verify_supabase_data(
    summary_output_path: str = "data/validation/supabase_verification.csv"
) -> Dict[str, Any]:
    """
    Execute verification queries directly on Supabase PostgreSQL database table.
    """
    with engine.connect() as conn:
        query_sql = text("""
            SELECT
                count(*) AS row_count,
                count(DISTINCT panchayat_id) AS unique_panchayat_count,
                count(DISTINCT block_name) AS unique_block_count,
                count(DISTINCT station_id) AS unique_station_count,
                min(date) AS min_date,
                max(date) AS max_date,
                count(*) FILTER (WHERE actual_rainfall_mm IS NULL) AS missing_actual_rainfall_count,
                count(*) FILTER (WHERE elevation_m IS NULL) AS missing_elevation_count,
                count(*) FILTER (WHERE block_forecast_rainfall_mm IS NULL) AS missing_forecast_count
            FROM panchayat_weather_data;
        """)
        row = conn.execute(query_sql).mappings().one()

        results = {
            "row_count": int(row["row_count"]),
            "unique_panchayat_count": int(row["unique_panchayat_count"]),
            "unique_block_count": int(row["unique_block_count"]),
            "unique_station_count": int(row["unique_station_count"]),
            "min_date": str(row["min_date"]),
            "max_date": str(row["max_date"]),
            "missing_actual_rainfall_count": int(row["missing_actual_rainfall_count"]),
            "missing_elevation_count": int(row["missing_elevation_count"]),
            "missing_forecast_count": int(row["missing_forecast_count"]),
        }

    # Save verification metrics to CSV
    os.makedirs(os.path.dirname(summary_output_path), exist_ok=True)
    summary_df = pd.DataFrame([results])
    summary_df.to_csv(summary_output_path, index=False, encoding="utf-8")
    logger.info(f"Supabase verification results saved to {summary_output_path}.")

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cnt, res = load_clean_data_to_supabase()
    print("Verification Results:", res)
