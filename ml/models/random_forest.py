import os
import joblib
import numpy as np
import pandas as pd
from typing import Optional


class RandomForestDownscaler:
    """
    Random Forest Regression model for downscaling Block rainfall forecasts
    to Panchayat-level hyper-local forecasts using spatial, terrain, and temporal features.
    """
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 12,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42
    ):
        self.model_name = "random_forest_downscaler"
        self.version = "1.0.0"
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "min_samples_leaf": min_samples_leaf,
            "random_state": random_state,
        }
        self.model = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Fit the Random Forest Regressor on features X and target y.
        (Invoked only during deliberate training phase).
        """
        from sklearn.ensemble import RandomForestRegressor
        self.model = RandomForestRegressor(**self.params)
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict downscaled rainfall in millimeters (clamped >= 0).
        """
        if self.model is None:
            raise RuntimeError("Model has not been fitted or loaded yet.")
        preds = self.model.predict(X)
        return np.clip(preds, a_min=0.0, a_max=None)

    def save(self, filepath: str):
        """Serialize model to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)

    def load(self, filepath: str):
        """Load serialized model from disk."""
        self.model = joblib.load(filepath)
        return self
