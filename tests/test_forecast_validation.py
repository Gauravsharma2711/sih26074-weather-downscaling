"""
Unit tests for Forecast Output Validation module (src/validation/forecast_validation.py).
Tests:
- normal positive predictions
- zero predictions
- negative predictions (clamped to 0, raw preserved)
- NaN rejection
- infinity rejection (+inf and -inf)
- non-numeric / corrupt inputs rejection
- physical extreme threshold validation
"""

import math
import pytest
import numpy as np
from src.validation.forecast_validation import (
    validate_forecast_output,
    validate_and_sanitize_rainfall,
    is_valid_forecast,
    InvalidForecastOutputError,
    ValidatedForecastResult,
)


def test_normal_prediction():
    """
    Test validation of normal positive rainfall predictions.
    """
    val = 14.7825
    result = validate_forecast_output(val)

    assert isinstance(result, ValidatedForecastResult)
    assert result.downscaled_rainfall_mm == 14.7825
    assert result.raw_predicted_rainfall_mm == 14.7825
    assert result.is_clamped is False
    assert is_valid_forecast(val) is True
    assert validate_and_sanitize_rainfall(val) == 14.7825


def test_zero_prediction():
    """
    Test validation of exact zero rainfall prediction.
    """
    val = 0.0
    result = validate_forecast_output(val)

    assert result.downscaled_rainfall_mm == 0.0
    assert result.raw_predicted_rainfall_mm == 0.0
    assert result.is_clamped is False
    assert is_valid_forecast(val) is True
    assert validate_and_sanitize_rainfall(val) == 0.0


def test_negative_prediction():
    """
    Test that negative raw predictions are clamped to 0.0 while preserving raw value for diagnostics.
    """
    raw_val = -3.4567
    result = validate_forecast_output(raw_val)

    assert result.downscaled_rainfall_mm == 0.0
    assert result.raw_predicted_rainfall_mm == -3.4567
    assert result.is_clamped is True
    assert is_valid_forecast(raw_val) is True
    assert validate_and_sanitize_rainfall(raw_val) == 0.0


def test_nan_prediction():
    """
    Test that NaN values are strictly rejected.
    """
    with pytest.raises(InvalidForecastOutputError) as exc_info:
        validate_forecast_output(float("nan"))
    assert "nan" in str(exc_info.value).lower()

    with pytest.raises(InvalidForecastOutputError):
        validate_forecast_output(np.nan)

    assert is_valid_forecast(float("nan")) is False
    assert is_valid_forecast(np.nan) is False


def test_infinity_prediction():
    """
    Test that positive and negative infinity values are strictly rejected.
    """
    # Positive infinity
    with pytest.raises(InvalidForecastOutputError) as exc_pos:
        validate_forecast_output(float("inf"))
    assert "infinite" in str(exc_pos.value).lower()

    # Negative infinity
    with pytest.raises(InvalidForecastOutputError) as exc_neg:
        validate_forecast_output(float("-inf"))
    assert "infinite" in str(exc_neg.value).lower()

    assert is_valid_forecast(float("inf")) is False
    assert is_valid_forecast(float("-inf")) is False


def test_non_numeric_and_null_rejection():
    """
    Test that non-numeric types (None, strings, bools, dicts) are rejected.
    """
    with pytest.raises(InvalidForecastOutputError):
        validate_forecast_output(None)

    with pytest.raises(InvalidForecastOutputError):
        validate_forecast_output("invalid_text")

    with pytest.raises(InvalidForecastOutputError):
        validate_forecast_output(True)

    with pytest.raises(InvalidForecastOutputError):
        validate_forecast_output([10.5])

    assert is_valid_forecast(None) is False
    assert is_valid_forecast("abc") is False
    assert is_valid_forecast(True) is False


def test_extreme_upper_limit_rejection():
    """
    Test that physically impossible rainfall amounts (e.g. > 1000 mm/day) are rejected.
    """
    with pytest.raises(InvalidForecastOutputError) as exc_info:
        validate_forecast_output(25000.0)
    assert "exceeds physical" in str(exc_info.value).lower()
