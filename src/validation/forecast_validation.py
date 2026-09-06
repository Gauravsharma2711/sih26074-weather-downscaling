"""
Forecast Output Validation Module.
Validates machine learning model outputs to enforce physical plausibility,
numerical validity, and non-negativity before persisting or serving predictions.
"""

import math
import logging
from typing import Any, Dict, NamedTuple, Union
from decimal import Decimal
import numpy as np

logger = logging.getLogger(__name__)


class ForecastValidationError(Exception):
    """Base exception for forecast output validation errors."""
    pass


class InvalidForecastOutputError(ForecastValidationError):
    """Raised when forecast output is NaN, infinite, non-numeric, or corrupt."""
    pass


class ValidatedForecastResult(NamedTuple):
    """
    Structured validation container holding both sanitized physical rainfall
    and raw diagnostic ML prediction values.
    """
    downscaled_rainfall_mm: float
    raw_predicted_rainfall_mm: float
    is_clamped: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "downscaled_rainfall_mm": self.downscaled_rainfall_mm,
            "raw_predicted_rainfall_mm": self.raw_predicted_rainfall_mm,
            "is_clamped": self.is_clamped,
        }


def is_valid_forecast(raw_prediction: Any) -> bool:
    """
    Check if a raw forecast prediction value is numerically valid (finite and numeric).
    Returns True if valid numeric (can be positive, zero, or negative), False otherwise.
    """
    if raw_prediction is None:
        return False
    if isinstance(raw_prediction, bool):  # bool is a subclass of int in Python
        return False
    try:
        val = float(raw_prediction)
        return not (math.isnan(val) or math.isinf(val))
    except (ValueError, TypeError):
        return False


def validate_forecast_output(
    raw_prediction: Any,
    max_rainfall_limit_mm: float = 1000.0,
) -> ValidatedForecastResult:
    """
    Validate and sanitize raw machine learning rainfall forecast output.

    Validation Rules:
    1. Must be numeric (convertible to float, rejecting None, bools, strings, collections).
    2. Cannot be NaN (raises InvalidForecastOutputError).
    3. Cannot be Infinite (+inf or -inf) (raises InvalidForecastOutputError).
    4. Cannot exceed extreme meteorological physical threshold (default: 1000 mm/day).
    5. Non-negativity constraint: If raw model prediction is negative (< 0.0),
       sets final downscaled_rainfall_mm to 0.0 while preserving raw_predicted_rainfall_mm
       for diagnostic inspection.

    Args:
        raw_prediction: The raw numerical prediction output from the ML regressor.
        max_rainfall_limit_mm: Upper physical bound (default 1000.0 mm).

    Returns:
        ValidatedForecastResult containing downscaled_rainfall_mm, raw_predicted_rainfall_mm, and is_clamped.

    Raises:
        InvalidForecastOutputError: If output is non-numeric, NaN, infinite, or physically absurd.
    """
    if raw_prediction is None:
        raise InvalidForecastOutputError("Forecast output is None (null).")

    if isinstance(raw_prediction, bool):
        raise InvalidForecastOutputError("Forecast output cannot be a boolean value.")

    # Convert to standard Python float
    try:
        if isinstance(raw_prediction, (np.generic, Decimal)):
            val = float(raw_prediction)
        elif isinstance(raw_prediction, (int, float)):
            val = float(raw_prediction)
        else:
            val = float(raw_prediction)
    except (ValueError, TypeError) as e:
        raise InvalidForecastOutputError(
            f"Forecast output must be numeric. Received '{raw_prediction}' of type {type(raw_prediction).__name__}."
        ) from e

    # Check for NaN
    if math.isnan(val) or np.isnan(val):
        raise InvalidForecastOutputError("Forecast output is NaN (Not a Number).")

    # Check for Infinity (+inf or -inf)
    if math.isinf(val) or np.isinf(val):
        raise InvalidForecastOutputError(f"Forecast output is infinite ({val}).")

    # Check extreme upper boundary
    if val > max_rainfall_limit_mm:
        raise InvalidForecastOutputError(
            f"Forecast output {val:.2f} mm exceeds physical meteorological upper limit ({max_rainfall_limit_mm} mm)."
        )

    # Apply physical non-negativity constraint
    raw_float = round(val, 4)
    if raw_float < 0.0:
        logger.info(
            f"Raw prediction ({raw_float} mm) is negative. Clamping downscaled rainfall to 0.0 mm."
        )
        return ValidatedForecastResult(
            downscaled_rainfall_mm=0.0,
            raw_predicted_rainfall_mm=raw_float,
            is_clamped=True,
        )

    return ValidatedForecastResult(
        downscaled_rainfall_mm=raw_float,
        raw_predicted_rainfall_mm=raw_float,
        is_clamped=False,
    )


def validate_and_sanitize_rainfall(raw_prediction: Any) -> float:
    """
    Convenience wrapper that validates raw prediction and returns the sanitized float.
    """
    result = validate_forecast_output(raw_prediction)
    return result.downscaled_rainfall_mm
