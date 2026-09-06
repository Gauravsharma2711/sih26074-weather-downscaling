import os
import sys
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.services.model_service import get_model_service, ModelService
from src.validation.forecast_validation import (
    validate_forecast_output,
    InvalidForecastOutputError,
)

logger = logging.getLogger(__name__)

DEFAULT_CLEAN_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "clean", "nashik_weather_clean.csv")
DEFAULT_FEATURES_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "features", "nashik_test.csv")


# =====================================================================
# CUSTOM SERVICE EXCEPTIONS
# =====================================================================

class ForecastServiceError(Exception):
    """Base exception for Forecast Service errors."""
    pass


class PanchayatNotFoundError(ForecastServiceError):
    """Raised when the requested Panchayat ID cannot be found."""
    pass


class BlockForecastNotFoundError(ForecastServiceError):
    """Raised when no numerical block rainfall forecast is available."""
    pass


class MissingFeatureError(ForecastServiceError):
    """Raised when essential spatial, geographic, or terrain features are missing."""
    pass


class ModelUnavailableError(ForecastServiceError):
    """Raised when the downscaling ML model or service cannot be reached."""
    pass


# =====================================================================
# DATE & TEMPORAL UTILITIES
# =====================================================================

def parse_date(date_val: Union[str, date, datetime]) -> date:
    """Parse string, datetime, or date into a datetime.date object."""
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, date):
        return date_val
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
        except ValueError:
            return datetime.fromisoformat(date_val.strip()).date()
    raise ValueError(f"Unable to parse date from value: {date_val}")


# =====================================================================
# REPOSITORY / DATA ACCESS HELPERS
# =====================================================================

def get_panchayat_record_from_db(
    panchayat_id: int,
    forecast_date: date,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Query database for Panchayat spatial attributes and block forecast.
    """
    try:
        query = text("""
            SELECT 
                panchayat_id, lgd_code, panchayat_name, block_name, district_name,
                panchayat_latitude, panchayat_longitude, elevation_m,
                date, forecast_issue_date, block_forecast_rainfall_mm,
                station_id, station_distance_km
            FROM panchayat_weather_data
            WHERE panchayat_id = :pid
            ORDER BY CASE WHEN date = :fdate THEN 0 ELSE 1 END, date DESC
            LIMIT 1;
        """)
        result = db.execute(query, {"pid": panchayat_id, "fdate": forecast_date}).mappings().first()
        if result:
            return dict(result)
        return None
    except Exception as e:
        logger.warning(f"Database query failed for panchayat_id={panchayat_id}: {e}")
        return None


def get_panchayat_record_from_dataset(
    panchayat_id: int,
    forecast_date: Optional[date] = None,
    dataset_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Query local CSV dataset registry for Panchayat attributes and block forecasts.
    """
    paths_to_try = [
        dataset_path,
        DEFAULT_FEATURES_DATASET_PATH,
        DEFAULT_CLEAN_DATASET_PATH,
        os.path.join(PROJECT_ROOT, "data", "features", "nashik_train.csv")
    ]
    
    for path in paths_to_try:
        if path and os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if "panchayat_id" in df.columns:
                    match = df[df["panchayat_id"] == int(panchayat_id)]
                    if len(match) > 0:
                        if forecast_date and "date" in match.columns:
                            date_str = str(forecast_date)
                            exact_date_match = match[match["date"] == date_str]
                            if len(exact_date_match) > 0:
                                return exact_date_match.iloc[0].to_dict()
                        return match.iloc[0].to_dict()
            except Exception as e:
                logger.warning(f"Error reading dataset at {path}: {e}")
    return None


# =====================================================================
# MAIN FORECAST GENERATION SERVICE
# =====================================================================

def generate_panchayat_forecast(
    panchayat_id: int,
    forecast_date: Union[str, date, datetime],
    forecast_issue_date: Union[str, date, datetime],
    block_forecast_rainfall_mm: Optional[float] = None,
    db: Optional[Session] = None,
    model_service: Optional[ModelService] = None,
    dataset_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate downscaled rainfall forecast for a specific Gram Panchayat.
    
    Workflow:
    1. Parse and validate forecast target date and issue date.
    2. Retrieve Panchayat spatial attributes (latitude, longitude, elevation, block name, station distance).
    3. Retrieve or accept block numerical weather forecast.
    4. Compute lead_days, month, and day_of_year.
    5. Build exact feature vector expected by the ML model.
    6. Execute downscaling inference using ModelService.
    7. Return downscaled prediction with complete metadata.
    
    Never uses actual ground rainfall when generating future forecasts.
    """
    # 1. Date processing
    f_date = parse_date(forecast_date)
    issue_date = parse_date(forecast_issue_date)
    
    lead_days = (f_date - issue_date).days
    if lead_days < 0:
        logger.warning(f"Forecast date ({f_date}) is earlier than issue date ({issue_date}). Lead days set to 0.")
        lead_days = 0
        
    month = f_date.month
    day_of_year = f_date.timetuple().tm_yday

    # 2. Retrieve Panchayat record (DB first, fallback to registry dataset)
    panchayat_record = None
    if db is not None:
        panchayat_record = get_panchayat_record_from_db(panchayat_id, f_date, db)
        
    if panchayat_record is None:
        panchayat_record = get_panchayat_record_from_dataset(panchayat_id, f_date, dataset_path)
        
    if panchayat_record is None:
        raise PanchayatNotFoundError(
            f"Panchayat with ID '{panchayat_id}' could not be found in the database or registry."
        )

    # 3. Extract attributes & validate features
    panchayat_name = panchayat_record.get("panchayat_name") or f"Panchayat-{panchayat_id}"
    block_name = panchayat_record.get("block_name") or "Unknown"
    district_name = panchayat_record.get("district_name") or "Nashik"
    
    lat = panchayat_record.get("panchayat_latitude")
    lon = panchayat_record.get("panchayat_longitude")
    elevation = panchayat_record.get("elevation_m")
    station_dist = panchayat_record.get("station_distance_km")

    if lat is None or pd.isna(lat) or lon is None or pd.isna(lon):
        raise MissingFeatureError(
            f"Geographic coordinates missing for Panchayat {panchayat_id} ({panchayat_name})."
        )
        
    if elevation is None or pd.isna(elevation):
        raise MissingFeatureError(
            f"Elevation data missing for Panchayat {panchayat_id} ({panchayat_name})."
        )
        
    # Distance to AWS fallback default if not recorded
    if station_dist is None or pd.isna(station_dist):
        station_dist = 5.0

    # 4. Resolve Block Rainfall Forecast
    bf_rainfall = block_forecast_rainfall_mm
    if bf_rainfall is None and panchayat_record:
        bf_rainfall = panchayat_record.get("block_forecast_rainfall_mm")

    if bf_rainfall is None or pd.isna(bf_rainfall):
        raise BlockForecastNotFoundError(
            f"No numerical block rainfall forecast found for Panchayat {panchayat_id} on {f_date}."
        )

    try:
        bf_rainfall = float(bf_rainfall)
        lat = float(lat)
        lon = float(lon)
        elevation = float(elevation)
        station_dist = float(station_dist)
    except (ValueError, TypeError) as e:
        raise MissingFeatureError(f"Feature type conversion failed: {e}") from e

    # 5. Model Inference via ModelService
    svc = model_service or get_model_service()
    if svc is None:
        raise ModelUnavailableError("ModelService is not initialized or unavailable.")

    try:
        pred_result = svc.predict(
            block_forecast_rainfall_mm=bf_rainfall,
            panchayat_latitude=lat,
            panchayat_longitude=lon,
            elevation_m=elevation,
            station_distance_km=station_dist,
            lead_days=lead_days,
            month=month,
            day_of_year=day_of_year
        )
    except Exception as e:
        logger.error(f"Downscaling model inference failed: {e}")
        raise ModelUnavailableError(f"Downscaling prediction failed: {e}") from e

    # 6. Validate and sanitize model output
    raw_pred = pred_result.get("raw_predicted_rainfall_mm", pred_result.get("downscaled_rainfall_mm"))
    validated_output = validate_forecast_output(raw_pred)

    # 7. Format Return Output (zero actual_rainfall exposure)
    return {
        "panchayat_id": int(panchayat_id),
        "panchayat_name": panchayat_name,
        "block_name": block_name,
        "district_name": district_name,
        "forecast_date": str(f_date),
        "forecast_issue_date": str(issue_date),
        "lead_days": int(lead_days),
        "month": int(month),
        "day_of_year": int(day_of_year),
        "panchayat_latitude": round(lat, 4),
        "panchayat_longitude": round(lon, 4),
        "elevation_m": round(elevation, 1),
        "station_distance_km": round(station_dist, 2),
        "block_forecast_rainfall_mm": round(bf_rainfall, 2),
        "downscaled_rainfall_mm": validated_output.downscaled_rainfall_mm,
        "raw_predicted_rainfall_mm": validated_output.raw_predicted_rainfall_mm,
        "model_name": pred_result.get("model_name", "XGBoost Regressor"),
        "model_version": pred_result.get("model_version", "v1.0.0"),
        # TODO (Day 5+): Implement statistical confidence/uncertainty calibration based on historical model residuals.
        # Null by default in Day 4 to avoid arbitrary unsupported percentage estimates.
        "confidence": None,
        "status": "success"
    }
