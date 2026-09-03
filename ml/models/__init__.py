"""Downscaling machine learning models."""
from ml.models.baseline import BlockPersistenceBaseline
from ml.models.random_forest import RandomForestDownscaler

__all__ = ["BlockPersistenceBaseline", "RandomForestDownscaler"]
