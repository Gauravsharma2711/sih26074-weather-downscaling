"""
Unit Tests for Agricultural Advisory Engine (src.advisory.advisory_engine).

Verifies deterministic rule-based advisory generation, rule traceability,
advisory content safety constraints, and output structure.
"""

from datetime import datetime
import pytest

from src.advisory.rainfall_classifier import RainfallCategory, InvalidRainfallError
from src.advisory.advisory_engine import (
    AdvisoryEngine,
    AdvisoryOutput,
    AdvisorySeverity,
    AdvisoryRule,
    ADVISORY_RULES_REGISTRY,
    generate_agricultural_advisory,
    RULE_VERSION,
)


# =============================================================================
# 1. Rule Traceability & Categorization Tests
# =============================================================================
@pytest.mark.parametrize(
    "rainfall_mm, expected_category, expected_rule_id, expected_severity",
    [
        (0.0, RainfallCategory.NO_RAIN, "RAIN_NO_SIGNIFICANT_V1", AdvisorySeverity.LOW),
        (1.5, RainfallCategory.VERY_LIGHT, "RAIN_VERY_LIGHT_V1", AdvisorySeverity.LOW),
        (10.0, RainfallCategory.LIGHT, "RAIN_LIGHT_V1", AdvisorySeverity.LOW),
        (35.0, RainfallCategory.MODERATE, "RAIN_MODERATE_V1", AdvisorySeverity.MODERATE),
        (85.0, RainfallCategory.HEAVY, "RAIN_HEAVY_V1", AdvisorySeverity.HIGH),
        (150.0, RainfallCategory.VERY_HEAVY, "RAIN_VERY_HEAVY_V1", AdvisorySeverity.CRITICAL),
        (250.0, RainfallCategory.EXTREMELY_HEAVY, "RAIN_EXTREMELY_HEAVY_V1", AdvisorySeverity.CRITICAL),
    ],
)
def test_advisory_rule_traceability(rainfall_mm, expected_category, expected_rule_id, expected_severity):
    """
    Test that every rainfall intensity maps deterministically to the expected rule_id,
    severity level, and category.
    """
    advisory = generate_agricultural_advisory(
        rainfall_mm=rainfall_mm,
        panchayat_name="Ajmer Saundane",
        block_name="Baglan",
        forecast_date="2026-09-07",
        lead_days=1,
    )

    assert advisory.rule_id == expected_rule_id
    assert advisory.rainfall_category == expected_category
    assert advisory.severity == expected_severity
    assert advisory.rule_version == "RAIN_RULES_V1"
    assert "Ajmer Saundane" in advisory.advisory_title
    assert len(advisory.advisory_points) >= 3


# =============================================================================
# 2. Output Schema & Required Fields Tests
# =============================================================================
def test_advisory_output_structure_and_serialization():
    """
    Verify all required output fields exist and serialization to dict works cleanly.
    """
    advisory = generate_agricultural_advisory(
        rainfall_mm=12.5,
        panchayat_name="Adgon",
        block_name="Chandwad",
        forecast_date="2026-09-08",
        lead_days=2,
    )

    assert isinstance(advisory.advisory_title, str)
    assert advisory.rainfall_category == RainfallCategory.LIGHT
    assert isinstance(advisory.advisory_points, list)
    assert len(advisory.advisory_points) > 0
    assert advisory.severity in [AdvisorySeverity.LOW, AdvisorySeverity.MODERATE, AdvisorySeverity.HIGH, AdvisorySeverity.CRITICAL]
    assert advisory.rule_version == "RAIN_RULES_V1"
    assert advisory.rule_id == "RAIN_LIGHT_V1"

    assert advisory.panchayat_name == "Adgon"
    assert advisory.block_name == "Chandwad"
    assert advisory.forecast_date == "2026-09-08"
    assert advisory.lead_days == 2
    assert advisory.rainfall_mm == 12.5

    # Check valid ISO datetime for generated_at
    parsed_dt = datetime.fromisoformat(advisory.generated_at)
    assert parsed_dt is not None

    # Check dictionary conversion
    d = advisory.to_dict()
    assert isinstance(d, dict)
    for field_name in [
        "advisory_title", "rainfall_category", "advisory_points",
        "severity", "generated_at", "rule_version", "rule_id",
        "rainfall_mm", "panchayat_name", "block_name", "forecast_date", "lead_days",
    ]:
        assert field_name in d


# =============================================================================
# 3. Safety & Policy Compliance Constraints
# =============================================================================
def test_advisory_safety_constraints():
    """
    Ensure no rule output contains pesticide dosage, fertilizer dosage,
    disease diagnosis, or unsupported yield predictions.
    """
    prohibited_terms = [
        "ml/l", "g/l", "kg/ha", "apply 200g", "dosage", "dose of",
        "diagnosed", "fungicide spray 2%", "yield increase by",
        "cure disease", "guaranteed yield", "medical",
    ]

    for category, rule in ADVISORY_RULES_REGISTRY.items():
        title = rule.title_template.lower()
        points = [p.lower() for p in rule.advisory_points_templates]

        for term in prohibited_terms:
            assert term not in title, f"Prohibited term '{term}' found in rule title for {category}"
            for point in points:
                assert term not in point, f"Prohibited term '{term}' found in rule point for {category}"


# =============================================================================
# 4. Input Validation & Error Handling
# =============================================================================
def test_advisory_invalid_rainfall_inputs():
    """
    Verify that invalid, NaN, infinite, or None rainfall inputs are rejected.
    """
    with pytest.raises(InvalidRainfallError):
        generate_agricultural_advisory(
            rainfall_mm=None,
            panchayat_name="Test",
            block_name="Test",
            forecast_date="2026-09-07",
        )

    with pytest.raises(InvalidRainfallError):
        generate_agricultural_advisory(
            rainfall_mm=float("nan"),
            panchayat_name="Test",
            block_name="Test",
            forecast_date="2026-09-07",
        )

    with pytest.raises(InvalidRainfallError):
        generate_agricultural_advisory(
            rainfall_mm=float("inf"),
            panchayat_name="Test",
            block_name="Test",
            forecast_date="2026-09-07",
        )


# =============================================================================
# 5. Ease of Updating & Custom Rules Extensibility
# =============================================================================
def test_custom_rules_registry_extensibility():
    """
    Verify that custom or updated rules can easily be supplied to AdvisoryEngine.
    """
    custom_rule = AdvisoryRule(
        rule_id="RAIN_HEAVY_V2_CUSTOM",
        rule_version="v2.0.0",
        rainfall_category=RainfallCategory.HEAVY,
        severity=AdvisorySeverity.HIGH,
        title_template="Custom Heavy Rain Protocol for {panchayat_name}",
        advisory_points_templates=[
            "Custom Rule Point 1: Rainfall {rainfall_mm:.1f} mm.",
            "Custom Rule Point 2: Clear all drain outlets in {block_name}.",
        ],
        description="Updated heavy rain protocol.",
    )

    custom_registry = {
        **ADVISORY_RULES_REGISTRY,
        RainfallCategory.HEAVY: custom_rule,
    }

    custom_engine = AdvisoryEngine(rules_registry=custom_registry)
    output = custom_engine.generate_advisory(
        rainfall_mm=75.0,
        panchayat_name="Deola",
        block_name="Deola",
        forecast_date="2026-09-07",
    )

    assert output.rule_id == "RAIN_HEAVY_V2_CUSTOM"
    assert output.rule_version == "v2.0.0"
    assert "Custom Heavy Rain Protocol for Deola" in output.advisory_title
    assert "Deola" in output.advisory_points[1]


# =============================================================================
# 6. Rule Versioning Invariant Tests
# =============================================================================
def test_advisory_cannot_be_generated_without_rule_version():
    """
    Verify that generating an advisory without a valid rule version is strictly prohibited.
    """
    invalid_rule = AdvisoryRule(
        rule_id="RAIN_TEST_NO_VERSION",
        rule_version="",  # Missing / empty rule version
        rainfall_category=RainfallCategory.LIGHT,
        severity=AdvisorySeverity.LOW,
        title_template="Test title",
        advisory_points_templates=["Point 1"],
        description="Test description",
    )

    engine = AdvisoryEngine(rules_registry={RainfallCategory.LIGHT: invalid_rule})
    with pytest.raises(ValueError, match="missing a valid rule_version"):
        engine.generate_advisory(
            rainfall_mm=10.0,
            panchayat_name="Test",
            block_name="Test",
            forecast_date="2026-09-08",
        )

