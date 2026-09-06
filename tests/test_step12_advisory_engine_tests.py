"""
Comprehensive Boundary, Invariance, and Determinism Tests for Rainfall Classifier and Advisory Engine.
(Day 5 - Step 12)

Explicitly tests all required boundary thresholds:
- 0 mm -> 'No significant rainfall' / LOW / RAIN_NO_SIGNIFICANT_V1 / RAIN_RULES_V1
- 2.5 mm -> 'Very light rainfall' / LOW / RAIN_VERY_LIGHT_V1 / RAIN_RULES_V1
- 2.6 mm -> 'Light rainfall' / LOW / RAIN_LIGHT_V1 / RAIN_RULES_V1
- 15.5 mm -> 'Light rainfall' / LOW / RAIN_LIGHT_V1 / RAIN_RULES_V1
- 15.6 mm -> 'Moderate rainfall' / MODERATE / RAIN_MODERATE_V1 / RAIN_RULES_V1
- 64.4 mm -> 'Moderate rainfall' / MODERATE / RAIN_MODERATE_V1 / RAIN_RULES_V1
- 64.5 mm -> 'Heavy rainfall' / HIGH / RAIN_HEAVY_V1 / RAIN_RULES_V1
- 115.5 mm -> 'Heavy rainfall' / HIGH / RAIN_HEAVY_V1 / RAIN_RULES_V1
- 115.6 mm -> 'Very heavy rainfall' / CRITICAL / RAIN_VERY_HEAVY_V1 / RAIN_RULES_V1
- 204.4 mm -> 'Very heavy rainfall' / CRITICAL / RAIN_VERY_HEAVY_V1 / RAIN_RULES_V1
- 204.5 mm -> 'Extremely heavy rainfall' / CRITICAL / RAIN_EXTREMELY_HEAVY_V1 / RAIN_RULES_V1

Edge cases:
- null (None)
- NaN (float('nan'), math.nan, np.nan)
- infinity (+inf, -inf)
- negative rainfall (-5.0, -0.01)

Invariants verified:
- Correct rainfall category
- Correct severity level
- Correct rule ID
- Correct rule version (RAIN_RULES_V1)
- 100% Deterministic output (same input produces identical advisory representation)
- Same forecast produces identical draft advisory
"""

import math
from datetime import date
import numpy as np
import pytest
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.downscaled_forecast import DownscaledForecast
from backend.app.models.advisory import Advisory
from src.advisory.rainfall_classifier import (
    classify_rainfall,
    RainfallCategory,
    InvalidRainfallError,
)
from src.advisory.advisory_engine import (
    AdvisoryEngine,
    generate_agricultural_advisory,
    AdvisorySeverity,
    RULE_VERSION,
    AdvisoryOutput,
)
from src.services.advisory_service import generate_advisory


# =============================================================================
# 1. EXACT BOUNDARY THRESHOLD TESTS (CLASSIFIER + ENGINE)
# =============================================================================
BOUNDARY_TEST_CASES = [
    (0.0, RainfallCategory.NO_RAIN, "RAIN_NO_SIGNIFICANT_V1", AdvisorySeverity.LOW),
    (2.5, RainfallCategory.VERY_LIGHT, "RAIN_VERY_LIGHT_V1", AdvisorySeverity.LOW),
    (2.6, RainfallCategory.LIGHT, "RAIN_LIGHT_V1", AdvisorySeverity.LOW),
    (15.5, RainfallCategory.LIGHT, "RAIN_LIGHT_V1", AdvisorySeverity.LOW),
    (15.6, RainfallCategory.MODERATE, "RAIN_MODERATE_V1", AdvisorySeverity.MODERATE),
    (64.4, RainfallCategory.MODERATE, "RAIN_MODERATE_V1", AdvisorySeverity.MODERATE),
    (64.5, RainfallCategory.HEAVY, "RAIN_HEAVY_V1", AdvisorySeverity.HIGH),
    (115.5, RainfallCategory.HEAVY, "RAIN_HEAVY_V1", AdvisorySeverity.HIGH),
    (115.6, RainfallCategory.VERY_HEAVY, "RAIN_VERY_HEAVY_V1", AdvisorySeverity.CRITICAL),
    (204.4, RainfallCategory.VERY_HEAVY, "RAIN_VERY_HEAVY_V1", AdvisorySeverity.CRITICAL),
    (204.5, RainfallCategory.EXTREMELY_HEAVY, "RAIN_EXTREMELY_HEAVY_V1", AdvisorySeverity.CRITICAL),
]


@pytest.mark.parametrize("rainfall_mm, expected_category, expected_rule_id, expected_severity", BOUNDARY_TEST_CASES)
def test_rainfall_classifier_explicit_boundaries(rainfall_mm, expected_category, expected_rule_id, expected_severity):
    """Verify that classify_rainfall correctly maps each boundary value."""
    category = classify_rainfall(rainfall_mm)
    assert category == expected_category, (
        f"Rainfall {rainfall_mm} mm expected '{expected_category}' but got '{category}'"
    )


@pytest.mark.parametrize("rainfall_mm, expected_category, expected_rule_id, expected_severity", BOUNDARY_TEST_CASES)
def test_advisory_engine_explicit_boundaries(rainfall_mm, expected_category, expected_rule_id, expected_severity):
    """
    Verify that AdvisoryEngine maps each boundary value to the exact:
    - category
    - severity
    - rule_id
    - rule_version
    """
    advisory: AdvisoryOutput = generate_agricultural_advisory(
        rainfall_mm=rainfall_mm,
        panchayat_name="Saundane",
        block_name="Baglan",
        forecast_date="2026-09-08",
        lead_days=1,
    )

    assert advisory.rainfall_category == expected_category
    assert advisory.severity == expected_severity
    assert advisory.rule_id == expected_rule_id
    assert advisory.rule_version == RULE_VERSION
    assert advisory.rule_version == "RAIN_RULES_V1"
    assert advisory.rainfall_mm == float(rainfall_mm)
    assert "Saundane" in advisory.advisory_title
    assert len(advisory.advisory_points) >= 3


# =============================================================================
# 2. EDGE CASES: NULL, NAN, INFINITY, NEGATIVE RAINFALL
# =============================================================================
def test_null_rainfall_handling():
    """Verify null (None) rainfall raises InvalidRainfallError."""
    with pytest.raises(InvalidRainfallError, match="null"):
        classify_rainfall(None)

    with pytest.raises(InvalidRainfallError):
        generate_agricultural_advisory(
            rainfall_mm=None,
            panchayat_name="Saundane",
            block_name="Baglan",
            forecast_date="2026-09-08",
        )


def test_nan_rainfall_handling():
    """Verify NaN rainfall raises InvalidRainfallError."""
    nan_values = [float("nan"), math.nan, np.nan]
    for val in nan_values:
        with pytest.raises(InvalidRainfallError, match="NaN"):
            classify_rainfall(val)

        with pytest.raises(InvalidRainfallError):
            generate_agricultural_advisory(
                rainfall_mm=val,
                panchayat_name="Saundane",
                block_name="Baglan",
                forecast_date="2026-09-08",
            )


def test_infinity_rainfall_handling():
    """Verify infinite rainfall raises InvalidRainfallError."""
    inf_values = [float("inf"), float("-inf"), math.inf, -math.inf, np.inf, -np.inf]
    for val in inf_values:
        with pytest.raises(InvalidRainfallError, match="infinite"):
            classify_rainfall(val)

        with pytest.raises(InvalidRainfallError):
            generate_agricultural_advisory(
                rainfall_mm=val,
                panchayat_name="Saundane",
                block_name="Baglan",
                forecast_date="2026-09-08",
            )


def test_negative_rainfall_handling():
    """
    Verify negative rainfall handling:
    1. Default/convert_negative_to_zero=True converts negative to 0.0 ('No significant rainfall', LOW, RAIN_NO_SIGNIFICANT_V1).
    2. Strict mode (convert_negative_to_zero=False) raises InvalidRainfallError.
    """
    negative_values = [-0.01, -2.5, -15.5, -64.4, -100.0]

    for val in negative_values:
        # Default behavior: converted to 0.0 -> No significant rainfall
        category = classify_rainfall(val, convert_negative_to_zero=True)
        assert category == RainfallCategory.NO_RAIN

        # Strict rejection
        with pytest.raises(InvalidRainfallError, match="Negative rainfall"):
            classify_rainfall(val, convert_negative_to_zero=False)

        # Engine conversion to zero and generation of Dry Weather Advisory
        advisory = generate_agricultural_advisory(
            rainfall_mm=val,
            panchayat_name="Saundane",
            block_name="Baglan",
            forecast_date="2026-09-08",
        )
        assert advisory.rainfall_category == RainfallCategory.NO_RAIN
        assert advisory.severity == AdvisorySeverity.LOW
        assert advisory.rule_id == "RAIN_NO_SIGNIFICANT_V1"
        assert advisory.rainfall_mm == 0.0


# =============================================================================
# 3. DETERMINISM & INVARIANCE TESTS
# =============================================================================
def test_advisory_engine_strict_determinism():
    """
    Verify that generating an advisory repeatedly with identical parameters produces
    strictly identical titles, points, categories, rule IDs, severities, and versions.
    """
    engine = AdvisoryEngine()
    test_inputs = [
        (0.0, "Panchayat-A", "Block-A", "2026-09-08", 0),
        (2.5, "Panchayat-B", "Block-B", "2026-09-09", 1),
        (2.6, "Panchayat-C", "Block-C", "2026-09-10", 2),
        (15.5, "Panchayat-D", "Block-D", "2026-09-11", 3),
        (15.6, "Panchayat-E", "Block-E", "2026-09-12", 4),
        (64.4, "Panchayat-F", "Block-F", "2026-09-13", 5),
        (64.5, "Panchayat-G", "Block-G", "2026-09-14", 6),
        (115.5, "Panchayat-H", "Block-H", "2026-09-15", 7),
        (115.6, "Panchayat-I", "Block-I", "2026-09-16", 8),
        (204.4, "Panchayat-J", "Block-J", "2026-09-17", 9),
        (204.5, "Panchayat-K", "Block-K", "2026-09-18", 10),
    ]

    for rainfall_mm, p_name, b_name, f_date, lead in test_inputs:
        base_output = engine.generate_advisory(
            rainfall_mm=rainfall_mm,
            panchayat_name=p_name,
            block_name=b_name,
            forecast_date=f_date,
            lead_days=lead,
        )

        for _ in range(50):
            repeated_output = engine.generate_advisory(
                rainfall_mm=rainfall_mm,
                panchayat_name=p_name,
                block_name=b_name,
                forecast_date=f_date,
                lead_days=lead,
            )

            assert repeated_output.advisory_title == base_output.advisory_title
            assert repeated_output.advisory_points == base_output.advisory_points
            assert repeated_output.rainfall_category == base_output.rainfall_category
            assert repeated_output.severity == base_output.severity
            assert repeated_output.rule_id == base_output.rule_id
            assert repeated_output.rule_version == base_output.rule_version
            assert repeated_output.rainfall_mm == base_output.rainfall_mm


def test_same_forecast_produces_identical_draft_advisory():
    """
    Verify that passing the same forecast dictionary to generate_advisory produces
    identical draft advisories across repeated executions.
    """
    db: Session = SessionLocal()
    panchayat_id = 9601
    f_date = date(2026, 9, 8)

    # Clean up prior records if any
    db.query(Advisory).filter(Advisory.panchayat_id == panchayat_id).delete(synchronize_session=False)
    db.commit()

    created_advisory_ids = []

    try:
        forecast_payload = {
            "forecast_id": 8801,
            "panchayat_id": panchayat_id,
            "forecast_date": f_date,
            "downscaled_rainfall_mm": 64.5,
            "panchayat_name": "Panchayat-9601",
            "block_name": "Baglan",
        }

        # Generate advisory first time
        adv_1 = generate_advisory(forecast=forecast_payload, db=db)
        created_advisory_ids.append(adv_1.id)

        # Generate advisory second time from identical forecast
        adv_2 = generate_advisory(forecast=forecast_payload, db=db)
        created_advisory_ids.append(adv_2.id)

        assert adv_1.advisory_title == adv_2.advisory_title
        assert adv_1.advisory_text == adv_2.advisory_text
        assert adv_1.rainfall_category == adv_2.rainfall_category
        assert adv_1.rainfall_category == "Heavy rainfall"
        assert adv_1.severity == adv_2.severity
        assert adv_1.severity == "HIGH"
        assert adv_1.rule_version == adv_2.rule_version
        assert adv_1.rule_version == "RAIN_RULES_V1"
        assert adv_1.status == "DRAFT"
        assert adv_2.status == "DRAFT"
        assert float(adv_1.rainfall_mm) == float(adv_2.rainfall_mm) == 64.5

    finally:
        if created_advisory_ids:
            db.query(Advisory).filter(Advisory.id.in_(created_advisory_ids)).delete(synchronize_session=False)
            db.commit()
        db.close()
