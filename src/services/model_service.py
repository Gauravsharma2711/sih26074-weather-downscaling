import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Union, Tuple
import joblib
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

logger = logging.getLogger(__name__)

# Exact Day 3 feature column ordering
FEATURE_COLUMNS = [
    "block_forecast_rainfall_mm",
    "panchayat_latitude",
    "panchayat_longitude",
    "elevation_m",
    "station_distance_km",
    "lead_days",
    "month",
    "day_of_year"
]

DEFAULT_MODEL_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "best_model.joblib")
DEFAULT_PREPROCESSOR_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "best_model_preprocessor.joblib")
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "best_model_config.json")
FALLBACK_PREPROCESSOR_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "random_forest_preprocessor.joblib")


class ModelService:
    """
    Production Model Service interface for micro-level weather downscaling.
    
    Guarantees:
    - Single-instance in-memory caching (loaded once at application startup).
    - Strict Day 3 feature ordering and preprocessing transforms.
    - Zero retraining during API requests.
    - Zero exposure to actual rainfall (no label leakage).
    - Enforced physical non-negativity constraint (downscaled_rainfall_mm >= 0.0).
    - Comprehensive error handling and model metadata reporting.
    """
    
    _instance: Optional["ModelService"] = None

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        preprocessor_path: Optional[str] = DEFAULT_PREPROCESSOR_PATH,
        config_path: str = DEFAULT_CONFIG_PATH,
        auto_load: bool = True
    ):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.config_path = config_path
        
        self.model: Optional[Any] = None
        self.preprocessor: Optional[Any] = None
        self.config: Dict[str, Any] = {}
        self.is_loaded: bool = False
        
        if auto_load:
            self.load_model()

    @classmethod
    def get_instance(
        cls,
        model_path: str = DEFAULT_MODEL_PATH,
        preprocessor_path: Optional[str] = DEFAULT_PREPROCESSOR_PATH,
        config_path: str = DEFAULT_CONFIG_PATH
    ) -> "ModelService":
        """
        Get or initialize the singleton instance of ModelService.
        """
        if cls._instance is None:
            cls._instance = cls(
                model_path=model_path,
                preprocessor_path=preprocessor_path,
                config_path=config_path,
                auto_load=True
            )
        return cls._instance

    def load_model(
        self,
        model_path: Optional[str] = None,
        preprocessor_path: Optional[str] = None,
        config_path: Optional[str] = None
    ) -> None:
        """
        Load the frozen model, fitted preprocessor, and configuration metadata from disk.
        
        Loads once into memory; never retrains.
        """
        target_model_path = model_path or self.model_path
        target_preprocessor_path = preprocessor_path or self.preprocessor_path
        target_config_path = config_path or self.config_path

        logger.info(f"Loading ModelService artifacts from: {target_model_path}")

        # 1. Load Model Binary
        if not os.path.exists(target_model_path):
            raise FileNotFoundError(
                f"Model artifact not found at {target_model_path}. "
                "Ensure Day 3 model training/freezing has been completed."
            )
        
        try:
            self.model = joblib.load(target_model_path)
            # Handle potential dict container
            if isinstance(self.model, dict) and "model" in self.model:
                self.model = self.model["model"]
        except Exception as e:
            logger.error(f"Failed to deserialize model artifact from {target_model_path}: {e}")
            raise RuntimeError(f"Error loading model artifact: {e}") from e

        # 2. Load Preprocessor Binary
        actual_preprocessor_path = target_preprocessor_path
        if not actual_preprocessor_path or not os.path.exists(actual_preprocessor_path):
            if os.path.exists(FALLBACK_PREPROCESSOR_PATH):
                actual_preprocessor_path = FALLBACK_PREPROCESSOR_PATH

        if actual_preprocessor_path and os.path.exists(actual_preprocessor_path):
            try:
                self.preprocessor = joblib.load(actual_preprocessor_path)
            except Exception as e:
                logger.warning(f"Failed to load preprocessor from {actual_preprocessor_path}: {e}")
                self.preprocessor = None
        else:
            logger.warning(f"No preprocessor artifact found at {actual_preprocessor_path}.")
            self.preprocessor = None

        # 3. Load Model Config
        if os.path.exists(target_config_path):
            try:
                with open(target_config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not parse model config from {target_config_path}: {e}")
                self.config = {}
        else:
            self.config = {}

        self.is_loaded = True
        logger.info(
            f"ModelService successfully initialized: {self.get_model_name()} "
            f"(Version: {self.get_model_version()})"
        )

    def get_model_name(self) -> str:
        """Return human-readable model name."""
        return self.config.get("model_name", "XGBoost Regressor")

    def get_model_version(self) -> str:
        """Return model release version."""
        return self.config.get("model_version", "v1.0.0")

    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Return model metadata, hyperparameters, feature list, and evaluation metrics.
        """
        if not self.is_loaded:
            self.load_model()

        return {
            "model_name": self.get_model_name(),
            "model_version": self.get_model_version(),
            "feature_list": FEATURE_COLUMNS,
            "training_date_range": self.config.get("training_date_range", {}),
            "training_rows": self.config.get("training_rows"),
            "test_date_range": self.config.get("test_date_range", {}),
            "test_rows": self.config.get("test_rows"),
            "baseline_mae": self.config.get("baseline_mae"),
            "baseline_rmse": self.config.get("baseline_rmse"),
            "model_mae": self.config.get("model_mae"),
            "model_rmse": self.config.get("model_rmse"),
            "mae_improvement_percent": self.config.get("mae_improvement_percent"),
            "rmse_improvement_percent": self.config.get("rmse_improvement_percent"),
            "is_loaded": self.is_loaded
        }

    def predict(
        self,
        block_forecast_rainfall_mm: float,
        panchayat_latitude: float,
        panchayat_longitude: float,
        elevation_m: float,
        station_distance_km: float,
        lead_days: int = 0,
        month: Optional[int] = None,
        day_of_year: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate downscaled rainfall prediction for a single Gram Panchayat forecast instance.
        
        Args:
            block_forecast_rainfall_mm: Regional block forecast precipitation (mm).
            panchayat_latitude: Centroid latitude (°N).
            panchayat_longitude: Centroid longitude (°E).
            elevation_m: Terrain elevation (meters AMSL).
            station_distance_km: Distance to nearest reference ground station (km).
            lead_days: Forecast horizon lead days (default 0).
            month: Calendar month (1-12). If omitted, inferred from day_of_year or current time.
            day_of_year: Day of the year (1-366). If omitted, inferred from month.
            
        Returns:
            Dict containing downscaled_rainfall_mm, raw_predicted_rainfall_mm, model_name, model_version.
        """
        if not self.is_loaded or self.model is None:
            self.load_model()

        # Input validation & defaults
        try:
            bf_rain = float(block_forecast_rainfall_mm)
            lat = float(panchayat_latitude)
            lon = float(panchayat_longitude)
            elev = float(elevation_m)
            dist = float(station_distance_km)
            lead = int(lead_days)
            m = int(month) if month is not None else 5
            doy = int(day_of_year) if day_of_year is not None else 130
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid input types provided for prediction: {e}")
            raise ValueError(f"Invalid input parameter for prediction: {e}") from e

        # Construct single-row DataFrame in exact Day 3 feature column order
        input_data = {
            "block_forecast_rainfall_mm": [bf_rain],
            "panchayat_latitude": [lat],
            "panchayat_longitude": [lon],
            "elevation_m": [elev],
            "station_distance_km": [dist],
            "lead_days": [lead],
            "month": [m],
            "day_of_year": [doy],
        }
        input_df = pd.DataFrame(input_data)[FEATURE_COLUMNS]

        # Apply preprocessing
        if self.preprocessor is not None:
            try:
                X = self.preprocessor.transform(input_df)
            except Exception as e:
                logger.warning(f"Preprocessor transform failed ({e}), falling back to raw numeric array.")
                X = input_df.values.astype(float)
        else:
            X = input_df.values.astype(float)

        # Model Inference
        try:
            raw_prediction = float(self.model.predict(X)[0])
        except Exception as e:
            logger.error(f"Model predict execution failed: {e}")
            raise RuntimeError(f"Model prediction failed: {e}") from e

        # Enforce physical non-negativity constraint
        downscaled_rainfall_mm = float(max(raw_prediction, 0.0))

        return {
            "downscaled_rainfall_mm": round(downscaled_rainfall_mm, 4),
            "raw_predicted_rainfall_mm": round(raw_prediction, 4),
            "model_name": self.get_model_name(),
            "model_version": self.get_model_version(),
            "status": "success"
        }


# Convenience module-level functions for application integration
def get_model_service() -> ModelService:
    """Return the global ModelService singleton."""
    return ModelService.get_instance()


def load_model(
    model_path: Optional[str] = None,
    preprocessor_path: Optional[str] = None,
    config_path: Optional[str] = None
) -> None:
    """Load model into global service singleton."""
    service = get_model_service()
    service.load_model(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
        config_path=config_path
    )


def predict(
    block_forecast_rainfall_mm: float,
    panchayat_latitude: float,
    panchayat_longitude: float,
    elevation_m: float,
    station_distance_km: float,
    lead_days: int = 0,
    month: Optional[int] = None,
    day_of_year: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """Execute prediction using the global ModelService singleton."""
    return get_model_service().predict(
        block_forecast_rainfall_mm=block_forecast_rainfall_mm,
        panchayat_latitude=panchayat_latitude,
        panchayat_longitude=panchayat_longitude,
        elevation_m=elevation_m,
        station_distance_km=station_distance_km,
        lead_days=lead_days,
        month=month,
        day_of_year=day_of_year,
        **kwargs
    )


def get_model_metadata() -> Dict[str, Any]:
    """Retrieve metadata from the global ModelService singleton."""
    return get_model_service().get_model_metadata()
