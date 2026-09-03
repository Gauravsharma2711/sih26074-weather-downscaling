from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def evaluate_predictions(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series]
) -> Dict[str, float]:
    """
    Calculate core validation metrics required by SIH26074:
    - MAE (Mean Absolute Error) in mm
    - RMSE (Root Mean Squared Error) in mm
    
    Args:
        y_true: Ground truth rainfall observations.
        y_pred: Model predictions.
        
    Returns:
        Dict with 'mae' and 'rmse' values.
    """
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
    }


def compare_model_against_baseline(
    y_true: Union[np.ndarray, pd.Series],
    y_baseline: Union[np.ndarray, pd.Series],
    y_model: Union[np.ndarray, pd.Series],
) -> Dict[str, Any]:
    """
    Strictly compare downscaled ML model metrics against the Block forecast baseline
    on held-out real observations.
    
    Args:
        y_true: Actual recorded rainfall.
        y_baseline: Block forecast values.
        y_model: Downscaled model predictions.
        
    Returns:
        Comparison report containing baseline and model metrics, alongside relative % improvements.
    """
    baseline_metrics = evaluate_predictions(y_true, y_baseline)
    model_metrics = evaluate_predictions(y_true, y_model)

    mae_improvement_pct = 0.0
    if baseline_metrics["mae"] > 0:
        mae_improvement_pct = round(
            ((baseline_metrics["mae"] - model_metrics["mae"]) / baseline_metrics["mae"]) * 100, 2
        )

    rmse_improvement_pct = 0.0
    if baseline_metrics["rmse"] > 0:
        rmse_improvement_pct = round(
            ((baseline_metrics["rmse"] - model_metrics["rmse"]) / baseline_metrics["rmse"]) * 100, 2
        )

    return {
        "baseline": baseline_metrics,
        "downscaled_model": model_metrics,
        "mae_improvement_pct": mae_improvement_pct,
        "rmse_improvement_pct": rmse_improvement_pct,
        "is_improvement": model_metrics["mae"] < baseline_metrics["mae"],
    }
