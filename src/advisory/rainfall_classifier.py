"""
Deterministic Rainfall Classifier Module.

===============================================================================
PROTOTYPE THRESHOLDS NOTICE:
The rainfall categorization thresholds defined in this module are PROTOTYPE
thresholds aligned with standard meteorological standards (IMD guidelines).
These thresholds are deterministic and rule-based (NO LLM is used).
===============================================================================

Threshold Specifications:
- 0.0 mm                        -> "No significant rainfall"
- > 0.0 mm   and <= 2.5 mm      -> "Very light rainfall"
- > 2.5 mm   and <= 15.5 mm     -> "Light rainfall"
- > 15.5 mm  and <= 64.4 mm     -> "Moderate rainfall"
- > 64.4 mm  and <= 115.5 mm    -> "Heavy rainfall"
- > 115.5 mm and <= 204.4 mm    -> "Very heavy rainfall"
- > 204.4 mm                    -> "Extremely heavy rainfall"

Input handling:
- Exact zero (0 or 0.0) -> "No significant rainfall"
- Positive rainfall -> mapped to appropriate category
- Negative rainfall -> converted to 0.0 by default or rejected if convert_negative_to_zero=False
- Null (None) -> raises InvalidRainfallError
- NaN -> raises InvalidRainfallError
- Infinity (+inf, -inf) -> raises InvalidRainfallError
- Non-numeric types (strings, bools, objects) -> raises InvalidRainfallError
"""

import math
import logging
from typing import Any, Union
from decimal import Decimal
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# PROTOTYPE RAINFALL CATEGORIES & THRESHOLD CONSTANTS
# =============================================================================
class RainfallCategory:
    """Standard prototype rainfall category string constants."""
    NO_RAIN = "No significant rainfall"
    VERY_LIGHT = "Very light rainfall"
    LIGHT = "Light rainfall"
    MODERATE = "Moderate rainfall"
    HEAVY = "Heavy rainfall"
    VERY_HEAVY = "Very heavy rainfall"
    EXTREMELY_HEAVY = "Extremely heavy rainfall"


# Prototype Threshold Definitions: (upper_bound_inclusive, category_name)
PROTOTYPE_RAINFALL_THRESHOLDS = [
    (0.0, RainfallCategory.NO_RAIN),
    (2.5, RainfallCategory.VERY_LIGHT),
    (15.5, RainfallCategory.LIGHT),
    (64.4, RainfallCategory.MODERATE),
    (115.5, RainfallCategory.HEAVY),
    (204.4, RainfallCategory.VERY_HEAVY),
    (float("inf"), RainfallCategory.EXTREMELY_HEAVY),
]


class InvalidRainfallError(ValueError):
    """Exception raised when an invalid, null, NaN, or non-finite rainfall value is supplied."""
    pass


def classify_rainfall(
    rainfall_mm: Any,
    convert_negative_to_zero: bool = True,
) -> str:
    """
    Deterministic rainfall classifier based on prototype meteorological thresholds.

    PROTOTYPE THRESHOLDS:
    - 0 mm                  : "No significant rainfall"
    - > 0.0 and <= 2.5 mm   : "Very light rainfall"
    - > 2.5 and <= 15.5 mm  : "Light rainfall"
    - > 15.5 and <= 64.4 mm : "Moderate rainfall"
    - > 64.4 and <= 115.5 mm: "Heavy rainfall"
    - > 115.5 and <= 204.4 mm: "Very heavy rainfall"
    - > 204.4 mm            : "Extremely heavy rainfall"

    Args:
        rainfall_mm: Rainfall value in millimetres (int, float, Decimal, or numpy numeric).
        convert_negative_to_zero: If True, negative rainfall (< 0.0) is converted to 0.0 mm
                                  ("No significant rainfall"). If False, negative rainfall
                                  raises InvalidRainfallError.

    Returns:
        rainfall_category (str): Human-readable prototype category string.

    Raises:
        InvalidRainfallError: If rainfall_mm is None, NaN, Infinite, boolean,
                              non-numeric, or negative (when convert_negative_to_zero=False).
    """
    # 1. Null / None check
    if rainfall_mm is None:
        raise InvalidRainfallError("Rainfall input is null (None). Cannot classify rainfall.")

    # 2. Boolean check (in Python, bool is a subclass of int: isinstance(True, int) is True)
    if isinstance(rainfall_mm, bool):
        raise InvalidRainfallError("Rainfall input cannot be a boolean value.")

    # 3. Numeric conversion check
    try:
        if isinstance(rainfall_mm, (np.generic, Decimal)):
            val = float(rainfall_mm)
        elif isinstance(rainfall_mm, (int, float)):
            val = float(rainfall_mm)
        else:
            # Reject strings and other arbitrary objects
            raise InvalidRainfallError(
                f"Rainfall input must be a numeric type. Received type '{type(rainfall_mm).__name__}' with value '{rainfall_mm}'."
            )
    except (ValueError, TypeError) as e:
        if isinstance(e, InvalidRainfallError):
            raise
        raise InvalidRainfallError(
            f"Failed to convert rainfall value '{rainfall_mm}' to float."
        ) from e

    # 4. NaN check
    if math.isnan(val) or np.isnan(val):
        raise InvalidRainfallError("Rainfall input is NaN (Not a Number).")

    # 5. Infinity check
    if math.isinf(val) or np.isinf(val):
        raise InvalidRainfallError(f"Rainfall input cannot be infinite ({val}).")

    # 6. Negative rainfall handling
    if val < 0.0:
        if convert_negative_to_zero:
            logger.debug(f"Negative rainfall value {val} mm converted to 0.0 mm before classification.")
            val = 0.0
        else:
            raise InvalidRainfallError(f"Negative rainfall value {val} mm is not permitted.")

    # 7. Deterministic Prototype Threshold Categorization
    if val == 0.0:
        return RainfallCategory.NO_RAIN
    elif val <= 2.5:
        return RainfallCategory.VERY_LIGHT
    elif val <= 15.5:
        return RainfallCategory.LIGHT
    elif val <= 64.4:
        return RainfallCategory.MODERATE
    elif val <= 115.5:
        return RainfallCategory.HEAVY
    elif val <= 204.4:
        return RainfallCategory.VERY_HEAVY
    else:
        return RainfallCategory.EXTREMELY_HEAVY
