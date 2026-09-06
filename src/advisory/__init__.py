"""
Agricultural Advisory and Weather Classification Package.
Contains deterministic rule-based modules for rainfall classification and advisory generation.
"""

from src.advisory.rainfall_classifier import (
    classify_rainfall,
    RainfallCategory,
    InvalidRainfallError,
    PROTOTYPE_RAINFALL_THRESHOLDS,
)
from src.advisory.advisory_engine import (
    AdvisoryEngine,
    AdvisoryRule,
    AdvisoryOutput,
    AdvisorySeverity,
    ADVISORY_RULES_REGISTRY,
    generate_agricultural_advisory,
    RULE_VERSION,
)

__all__ = [
    "classify_rainfall",
    "RainfallCategory",
    "InvalidRainfallError",
    "PROTOTYPE_RAINFALL_THRESHOLDS",
    "AdvisoryEngine",
    "AdvisoryRule",
    "AdvisoryOutput",
    "AdvisorySeverity",
    "ADVISORY_RULES_REGISTRY",
    "generate_agricultural_advisory",
    "RULE_VERSION",
]
