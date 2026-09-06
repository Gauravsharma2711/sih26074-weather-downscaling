"""
Unit Tests for Rainfall Classifier (src.advisory.rainfall_classifier).

Tests all prototype classification boundaries, edge cases, and invalid inputs:
1. Zero rainfall (0, 0.0) -> "No significant rainfall"
2. Very light rainfall (>0 and <=2.5) boundaries: 0.001, 1.2, 2.5
3. Light rainfall (>2.5 and <=15.5) boundaries: 2.5001, 8.0, 15.5
4. Moderate rainfall (>15.5 and <=64.4) boundaries: 15.5001, 30.0, 64.4
5. Heavy rainfall (>64.4 and <=115.5) boundaries: 64.4001, 90.0, 115.5
6. Very heavy rainfall (>115.5 and <=204.4) boundaries: 115.5001, 150.0, 204.4
7. Extremely heavy rainfall (>204.4) boundaries: 204.4001, 300.0, 1000.0
8. Negative rainfall: conversion to 0.0 (default) and rejection (convert_negative_to_zero=False)
9. Null (None) input rejection
10. NaN input rejection (float('nan'), np.nan)
11. Infinity input rejection (+inf, -inf)
12. Boolean and non-numeric input rejection (True, False, string, dict)
13. Input types: int, float, Decimal, numpy float32/float64
"""

import math
from decimal import Decimal
import numpy as np
import pytest

from src.advisory.rainfall_classifier import (
    classify_rainfall,
    RainfallCategory,
    InvalidRainfallError,
    PROTOTYPE_RAINFALL_THRESHOLDS,
)


# =============================================================================
# 1. Zero Rainfall Tests
# =============================================================================
def test_zero_rainfall_classification():
    """Test that exactly 0.0 mm yields 'No significant rainfall'."""
    assert classify_rainfall(0) == RainfallCategory.NO_RAIN
    assert classify_rainfall(0.0) == RainfallCategory.NO_RAIN
    assert classify_rainfall(Decimal("0.0")) == RainfallCategory.NO_RAIN
    assert classify_rainfall(np.float64(0.0)) == RainfallCategory.NO_RAIN


# =============================================================================
# 2. Very Light Rainfall Tests (>0.0 and <= 2.5 mm)
# =============================================================================
def test_very_light_rainfall_boundaries():
    """Test boundary and intermediate values for 'Very light rainfall'."""
    assert classify_rainfall(0.0001) == RainfallCategory.VERY_LIGHT
    assert classify_rainfall(0.1) == RainfallCategory.VERY_LIGHT
    assert classify_rainfall(1.0) == RainfallCategory.VERY_LIGHT
    assert classify_rainfall(2.5) == RainfallCategory.VERY_LIGHT
    assert classify_rainfall(np.float32(2.5)) == RainfallCategory.VERY_LIGHT


# =============================================================================
# 3. Light Rainfall Tests (>2.5 and <= 15.5 mm)
# =============================================================================
def test_light_rainfall_boundaries():
    """Test boundary and intermediate values for 'Light rainfall'."""
    assert classify_rainfall(2.5001) == RainfallCategory.LIGHT
    assert classify_rainfall(2.6) == RainfallCategory.LIGHT
    assert classify_rainfall(7.5) == RainfallCategory.LIGHT
    assert classify_rainfall(15.5) == RainfallCategory.LIGHT


# =============================================================================
# 4. Moderate Rainfall Tests (>15.5 and <= 64.4 mm)
# =============================================================================
def test_moderate_rainfall_boundaries():
    """Test boundary and intermediate values for 'Moderate rainfall'."""
    assert classify_rainfall(15.5001) == RainfallCategory.MODERATE
    assert classify_rainfall(15.6) == RainfallCategory.MODERATE
    assert classify_rainfall(35.0) == RainfallCategory.MODERATE
    assert classify_rainfall(64.4) == RainfallCategory.MODERATE


# =============================================================================
# 5. Heavy Rainfall Tests (>64.4 and <= 115.5 mm)
# =============================================================================
def test_heavy_rainfall_boundaries():
    """Test boundary and intermediate values for 'Heavy rainfall'."""
    assert classify_rainfall(64.4001) == RainfallCategory.HEAVY
    assert classify_rainfall(64.5) == RainfallCategory.HEAVY
    assert classify_rainfall(85.0) == RainfallCategory.HEAVY
    assert classify_rainfall(115.5) == RainfallCategory.HEAVY


# =============================================================================
# 6. Very Heavy Rainfall Tests (>115.5 and <= 204.4 mm)
# =============================================================================
def test_very_heavy_rainfall_boundaries():
    """Test boundary and intermediate values for 'Very heavy rainfall'."""
    assert classify_rainfall(115.5001) == RainfallCategory.VERY_HEAVY
    assert classify_rainfall(115.6) == RainfallCategory.VERY_HEAVY
    assert classify_rainfall(160.0) == RainfallCategory.VERY_HEAVY
    assert classify_rainfall(204.4) == RainfallCategory.VERY_HEAVY


# =============================================================================
# 7. Extremely Heavy Rainfall Tests (>204.4 mm)
# =============================================================================
def test_extremely_heavy_rainfall_boundaries():
    """Test boundary and intermediate values for 'Extremely heavy rainfall'."""
    assert classify_rainfall(204.4001) == RainfallCategory.EXTREMELY_HEAVY
    assert classify_rainfall(204.5) == RainfallCategory.EXTREMELY_HEAVY
    assert classify_rainfall(350.0) == RainfallCategory.EXTREMELY_HEAVY
    assert classify_rainfall(1200.0) == RainfallCategory.EXTREMELY_HEAVY


# =============================================================================
# 8. Negative Rainfall Handling
# =============================================================================
def test_negative_rainfall_conversion_to_zero():
    """Test that negative rainfall is converted to 0.0 ('No significant rainfall') by default."""
    assert classify_rainfall(-0.01) == RainfallCategory.NO_RAIN
    assert classify_rainfall(-5.0) == RainfallCategory.NO_RAIN
    assert classify_rainfall(-100.0, convert_negative_to_zero=True) == RainfallCategory.NO_RAIN


def test_negative_rainfall_rejection():
    """Test that negative rainfall raises InvalidRainfallError when convert_negative_to_zero=False."""
    with pytest.raises(InvalidRainfallError, match="Negative rainfall"):
        classify_rainfall(-0.1, convert_negative_to_zero=False)

    with pytest.raises(InvalidRainfallError, match="Negative rainfall"):
        classify_rainfall(-15.0, convert_negative_to_zero=False)


# =============================================================================
# 9. Null (None) Rejection
# =============================================================================
def test_null_rainfall_rejection():
    """Test that None input raises InvalidRainfallError."""
    with pytest.raises(InvalidRainfallError, match="null"):
        classify_rainfall(None)


# =============================================================================
# 10. NaN Rejection
# =============================================================================
def test_nan_rainfall_rejection():
    """Test that NaN values raise InvalidRainfallError."""
    with pytest.raises(InvalidRainfallError, match="NaN"):
        classify_rainfall(float("nan"))

    with pytest.raises(InvalidRainfallError, match="NaN"):
        classify_rainfall(np.nan)


# =============================================================================
# 11. Infinity Rejection
# =============================================================================
def test_infinity_rainfall_rejection():
    """Test that infinite values raise InvalidRainfallError."""
    with pytest.raises(InvalidRainfallError, match="infinite"):
        classify_rainfall(float("inf"))

    with pytest.raises(InvalidRainfallError, match="infinite"):
        classify_rainfall(float("-inf"))

    with pytest.raises(InvalidRainfallError, match="infinite"):
        classify_rainfall(np.inf)


# =============================================================================
# 12. Non-numeric and Boolean Rejection
# =============================================================================
def test_boolean_and_non_numeric_rejection():
    """Test that booleans, strings, and non-numeric types are rejected."""
    with pytest.raises(InvalidRainfallError, match="boolean"):
        classify_rainfall(True)

    with pytest.raises(InvalidRainfallError, match="boolean"):
        classify_rainfall(False)

    with pytest.raises(InvalidRainfallError, match="numeric"):
        classify_rainfall("15.5")

    with pytest.raises(InvalidRainfallError, match="numeric"):
        classify_rainfall({"rainfall": 10.0})


# =============================================================================
# 13. Numeric Types Compatibility
# =============================================================================
def test_numeric_types_compatibility():
    """Test compatibility with various Python and NumPy numeric types."""
    assert classify_rainfall(10) == RainfallCategory.LIGHT
    assert classify_rainfall(10.0) == RainfallCategory.LIGHT
    assert classify_rainfall(Decimal("10.0")) == RainfallCategory.LIGHT
    assert classify_rainfall(np.int64(50)) == RainfallCategory.MODERATE
    assert classify_rainfall(np.float32(75.5)) == RainfallCategory.HEAVY
    assert classify_rainfall(np.float64(150.0)) == RainfallCategory.VERY_HEAVY
