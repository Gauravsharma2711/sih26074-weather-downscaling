import logging
from typing import Dict, Any, Union
import pandas as pd
import numpy as np

from ml.preprocessing.cleaner import clean_weather_data
from ml.features.engineer import extract_features
from ml.models.baseline import BlockPersistenceBaseline

logger = logging.getLogger(__name__)


class DownscalingPipeline:
    """
    End-to-end inference pipeline:
    Takes raw Panchayat weather and Block forecast data -> cleans it ->
    extracts terrain & temporal features -> executes model prediction.
    """
    def __init__(self, model=None):
        self.model = model if model is not None else BlockPersistenceBaseline()

    def run(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute prediction pipeline on input dataframe.
        
        Args:
            raw_data: Raw input dataframe with block forecast and panchayat metadata.
            
        Returns:
            pd.DataFrame with 'downscaled_rainfall_mm' predictions.
        """
        if raw_data.empty:
            logger.warning("Empty dataframe supplied to prediction pipeline.")
            return raw_data

        cleaned = clean_weather_data(raw_data)
        X, _ = extract_features(cleaned)
        predictions = self.model.predict(X)

        result = cleaned.copy()
        result["downscaled_rainfall_mm"] = np.round(predictions, 2)
        result["model_used"] = getattr(self.model, "model_name", "custom_model")
        return result
