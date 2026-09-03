import numpy as np
import pandas as pd


class BlockPersistenceBaseline:
    """
    Official Baseline Model:
    Directly treats the Block-level forecast as the Panchayat forecast.
    All ML models are evaluated against this baseline to measure true improvement.
    """
    def __init__(self):
        self.model_name = "block_persistence_baseline"
        self.version = "1.0.0"

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Baseline requires no training."""
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Passes through the block_forecast_rainfall_mm column.
        """
        if "block_forecast_rainfall_mm" in X.columns:
            return X["block_forecast_rainfall_mm"].to_numpy()
        raise ValueError("Feature 'block_forecast_rainfall_mm' required for baseline prediction.")
