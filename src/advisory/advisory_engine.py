"""
Deterministic Rule-Based Agricultural Advisory Engine.

===============================================================================
RULE ENGINE NOTICE:
This module generates conservative, generic agricultural advisories strictly
derived from deterministic meteorological rules. NO LLM is used.
Every generated advisory is explicitly traceable to a versioned rule_id.

Safety & Compliance Constraints:
- NO pesticide dosage recommendations
- NO fertilizer dosage recommendations
- NO disease diagnoses
- NO medical advice
- NO highly specific crop treatment protocols
- NO unsupported yield predictions
===============================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import logging

from src.advisory.rainfall_classifier import (
    classify_rainfall,
    RainfallCategory,
    InvalidRainfallError,
)
from src.advisory.localization import (
    get_localized_rule_content,
    DEFAULT_LANGUAGE,
    ALL_SUPPORTED_LANGUAGES,
    LANGUAGE_METADATA,
    SupportedLanguage,
)

logger = logging.getLogger(__name__)

RULE_VERSION = "RAIN_RULES_V1"



# =============================================================================
# ADVISORY SEVERITY LEVELS
# =============================================================================
class AdvisorySeverity:
    """Standard advisory severity classification."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# =============================================================================
# RULE DEFINITION DATA STRUCTURE
# =============================================================================
@dataclass(frozen=True)
class AdvisoryRule:
    """
    Encapsulates a deterministic agricultural advisory rule.
    Easily configurable, extensible, and version-tracked.
    """
    rule_id: str
    rule_version: str
    rainfall_category: str
    severity: str
    title_template: str
    advisory_points_templates: List[str]
    description: str


# =============================================================================
# RULE REGISTRY (EASILY EXTENSIBLE & UPDATABLE)
# =============================================================================
ADVISORY_RULES_REGISTRY: Dict[str, AdvisoryRule] = {
    RainfallCategory.NO_RAIN: AdvisoryRule(
        rule_id="RAIN_NO_SIGNIFICANT_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.NO_RAIN,
        severity=AdvisorySeverity.LOW,
        title_template="Dry Weather Advisory for {panchayat_name} - Routine Farm Management",
        advisory_points_templates=[
            "No significant rainfall expected ({rainfall_mm:.1f} mm). Continue routine irrigation scheduling based on soil moisture and crop water needs.",
            "Favorable window for scheduled intercultural operations, hand weeding, and standard field maintenance.",
            "Inspect irrigation channels, drip lines, and pumps for leaks to optimize water conservation.",
            "Regularly assess soil moisture depth in shallow-rooted and newly transplanted crops.",
        ],
        description="Rule for zero or negligible rainfall conditions.",
    ),
    RainfallCategory.VERY_LIGHT: AdvisoryRule(
        rule_id="RAIN_VERY_LIGHT_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.VERY_LIGHT,
        severity=AdvisorySeverity.LOW,
        title_template="Very Light Rainfall Advisory for {panchayat_name} - Standard Farm Operations",
        advisory_points_templates=[
            "Very light rainfall expected ({rainfall_mm:.1f} mm). Normal field activities and crop management may continue as planned.",
            "Check root-zone soil moisture before initiating supplemental irrigation cycles.",
            "Favorable conditions for routine nursery management, intercultural hoeing, and field scouting.",
            "Ensure harvested produce in open threshing yards is kept under protective tarpaulins if drizzle occurs.",
        ],
        description="Rule for very light rainfall (0 < rainfall <= 2.5 mm).",
    ),
    RainfallCategory.LIGHT: AdvisoryRule(
        rule_id="RAIN_LIGHT_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.LIGHT,
        severity=AdvisorySeverity.LOW,
        title_template="Light Rainfall Advisory for {panchayat_name} - Soil Moisture & Spraying Precautions",
        advisory_points_templates=[
            "Light rainfall forecast ({rainfall_mm:.1f} mm). Postpone light surface irrigation until post-rain soil moisture is evaluated.",
            "Ensure field surface aeration and avoid excessive water stagnation around tender seedlings.",
            "Avoid routine foliar operations or dusting during active rainfall periods to prevent wash-off.",
            "Store harvested produce, crop residues, and farm inputs under secure, dry coverings.",
        ],
        description="Rule for light rainfall (2.5 < rainfall <= 15.5 mm).",
    ),
    RainfallCategory.MODERATE: AdvisoryRule(
        rule_id="RAIN_MODERATE_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.MODERATE,
        severity=AdvisorySeverity.MODERATE,
        title_template="Moderate Rainfall Advisory for {panchayat_name} - Drainage Preparedness & Irrigation Suspension",
        advisory_points_templates=[
            "Moderate rainfall forecast ({rainfall_mm:.1f} mm). Temporarily suspend all irrigation operations as rainfall will satisfy crop water demand.",
            "Inspect and clean field drainage channels to ensure free flow and prevent water stagnation in crop root zones.",
            "Postpone chemical spraying, broadcasting of fertilizers, and intercultural operations until the rainfall subsides.",
            "Move harvested grains and agricultural inputs into sheltered, elevated, moisture-free storage.",
        ],
        description="Rule for moderate rainfall (15.5 < rainfall <= 64.4 mm).",
    ),
    RainfallCategory.HEAVY: AdvisoryRule(
        rule_id="RAIN_HEAVY_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.HEAVY,
        severity=AdvisorySeverity.HIGH,
        title_template="Heavy Rainfall Warning for {panchayat_name} - Excess Water Drainage & Crop Protection",
        advisory_points_templates=[
            "Heavy rainfall forecast ({rainfall_mm:.1f} mm). Strictly suspend all irrigation and open field operations.",
            "Immediately open, clear, and deepen drainage furrows to discharge excess runoff and avoid severe root-zone waterlogging.",
            "Provide physical support or staking for standing vegetable crops, young orchards, and tall crops vulnerable to wind and heavy rain.",
            "Keep farm livestock sheltered indoors with clean drinking water and dry bedding away from low-lying areas.",
            "Do not allow standing water accumulation around tree basins and vegetable beds.",
        ],
        description="Rule for heavy rainfall (64.4 < rainfall <= 115.5 mm).",
    ),
    RainfallCategory.VERY_HEAVY: AdvisoryRule(
        rule_id="RAIN_VERY_HEAVY_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.VERY_HEAVY,
        severity=AdvisorySeverity.CRITICAL,
        title_template="Very Heavy Rainfall Alert for {panchayat_name} - Emergency Drainage & Infrastructure Protection",
        advisory_points_templates=[
            "Very heavy rainfall forecast ({rainfall_mm:.1f} mm). Immediate precautionary action required across farm plots.",
            "Open all main drainage outlets and field ditches to prevent inundation and topsoil erosion.",
            "Completely halt all agricultural machinery operations, chemical applications, and manual field labor.",
            "Safeguard nursery sheds, polyhouses, farm machinery, and electric motor pumps by relocating them to higher ground.",
            "Ensure livestock are secured in well-sheltered, flood-safe structures with adequate dry fodder reserves.",
            "Avoid crossing or working in submerged fields until excess water has safely receded.",
        ],
        description="Rule for very heavy rainfall (115.5 < rainfall <= 204.4 mm).",
    ),
    RainfallCategory.EXTREMELY_HEAVY: AdvisoryRule(
        rule_id="RAIN_EXTREMELY_HEAVY_V1",
        rule_version=RULE_VERSION,
        rainfall_category=RainfallCategory.EXTREMELY_HEAVY,
        severity=AdvisorySeverity.CRITICAL,
        title_template="Extremely Heavy Rainfall Red Alert for {panchayat_name} - Flood & Safety Precautions",
        advisory_points_templates=[
            "Extremely heavy rainfall forecast ({rainfall_mm:.1f} mm). Prioritize life, livestock, and farm infrastructure safety.",
            "Keep all farm waterways, drainage canals, and field bund outlets completely unobstructed to mitigate flash waterlogging and soil loss.",
            "Secure livestock, machinery, power lines, and valuable farm assets in elevated, flood-proof shelters.",
            "Strictly suspend all agricultural, harvesting, and transport activities across low-lying fields and riparian zones.",
            "Monitor farm bunds, perimeter embankments, and village water bodies for integrity against breaching.",
        ],
        description="Rule for extremely heavy rainfall (> 204.4 mm).",
    ),
}


# =============================================================================
# OUTPUT CONTAINER DATA CLASS
# =============================================================================
@dataclass
class AdvisoryOutput:
    """
    Structured container representing the canonical rule-generated agricultural advisory.
    Supports multilingual localization representations without separate engines.
    """
    advisory_title: str
    rainfall_category: str
    advisory_points: List[str]
    severity: str
    generated_at: str
    rule_version: str
    rule_id: str
    rainfall_mm: float
    panchayat_name: str
    block_name: str
    forecast_date: str
    lead_days: int
    language: str = DEFAULT_LANGUAGE
    available_languages: List[str] = field(default_factory=lambda: ALL_SUPPORTED_LANGUAGES.copy())

    def to_dict(self) -> Dict[str, Any]:
        """Convert advisory object into a standardized dictionary."""
        return {
            "advisory_title": self.advisory_title,
            "rainfall_category": self.rainfall_category,
            "advisory_points": self.advisory_points,
            "severity": self.severity,
            "generated_at": self.generated_at,
            "rule_version": self.rule_version,
            "rule_id": self.rule_id,
            "rainfall_mm": self.rainfall_mm,
            "panchayat_name": self.panchayat_name,
            "block_name": self.block_name,
            "forecast_date": self.forecast_date,
            "lead_days": self.lead_days,
            "language": self.language,
            "available_languages": self.available_languages,
        }


# =============================================================================
# DETERMINISTIC ADVISORY ENGINE
# =============================================================================
class AdvisoryEngine:
    """
    Deterministic rule-based agricultural advisory engine.
    Applies traceable, conservative agronomic rules based on downscaled rainfall.
    Produces canonical English advisories with deterministic multilingual rendering.
    """

    def __init__(self, rules_registry: Optional[Dict[str, AdvisoryRule]] = None):
        self.rules_registry = rules_registry or ADVISORY_RULES_REGISTRY
        self.rule_version = RULE_VERSION

    def generate_advisory(
        self,
        rainfall_mm: Any,
        panchayat_name: str,
        block_name: str,
        forecast_date: Union[str, Any],
        lead_days: int = 0,
        rainfall_category: Optional[str] = None,
        language: str = DEFAULT_LANGUAGE,
    ) -> AdvisoryOutput:
        """
        Generate a deterministic, rule-based agricultural advisory.

        Args:
            rainfall_mm: Downscaled rainfall prediction in mm.
            panchayat_name: Target Panchayat name.
            block_name: Target Block/Taluka name.
            forecast_date: Target date of forecast (YYYY-MM-DD or date object).
            lead_days: Forecast lead days (default 0).
            rainfall_category: Optional pre-classified category; if None, classified automatically.
            language: Target output language code ('en', 'mr', 'hi').

        Returns:
            AdvisoryOutput: Complete advisory record with rule traceability and language metadata.

        Raises:
            InvalidRainfallError: If rainfall value is invalid/NaN/infinite/non-numeric.
            KeyError: If classified category is missing from rule registry.
        """
        # 1. Classify rainfall category if not provided
        category = rainfall_category
        if category is None or category not in self.rules_registry:
            category = classify_rainfall(rainfall_mm, convert_negative_to_zero=True)

        # Standardize numeric rainfall
        clean_rainfall_mm = max(0.0, float(rainfall_mm)) if isinstance(rainfall_mm, (int, float)) else 0.0

        # Standardize string fields
        p_name = str(panchayat_name).strip() or "Panchayat"
        b_name = str(block_name).strip() or "Block"
        f_date = str(forecast_date).strip()
        l_days = max(0, int(lead_days))
        clean_lang = str(language).lower().strip() if language else DEFAULT_LANGUAGE

        # 2. Lookup Rule in Registry
        if category not in self.rules_registry:
            raise KeyError(f"No advisory rule defined for category: '{category}'")

        rule = self.rules_registry[category]

        # 3. Validate rule has required rule_version and rule_id (No advisory generated without version)
        if not rule.rule_version or not str(rule.rule_version).strip():
            raise ValueError(
                f"Advisory rule '{rule.rule_id}' is missing a valid rule_version. "
                f"Advisories cannot be generated without a rule version."
            )
        if not rule.rule_id or not str(rule.rule_id).strip():
            raise ValueError(f"Advisory rule for category '{category}' is missing a valid rule_id.")

        # 4. Context for template formatting
        context = {
            "panchayat_name": p_name,
            "block_name": b_name,
            "forecast_date": f_date,
            "lead_days": l_days,
            "rainfall_mm": clean_rainfall_mm,
        }

        # 5. Format Title and Points deterministically via Multilingual Catalog
        try:
            localized_content = get_localized_rule_content(rule.rule_id, language=clean_lang)
            title = localized_content.title_template.format(**context)
            points = [p.format(**context) for p in localized_content.advisory_points_templates]
            active_lang = clean_lang if clean_lang in ALL_SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        except Exception as loc_err:
            logger.warning(f"Localization lookup failed for rule '{rule.rule_id}', fallback to rule templates: {loc_err}")
            title = rule.title_template.format(**context)
            points = [p.format(**context) for p in rule.advisory_points_templates]
            active_lang = DEFAULT_LANGUAGE

        # 6. Construct Timestamp
        now_utc = datetime.now(timezone.utc).isoformat()

        # 7. Return Structured Advisory Output with Language Metadata
        return AdvisoryOutput(
            advisory_title=title,
            rainfall_category=category,
            advisory_points=points,
            severity=rule.severity,
            generated_at=now_utc,
            rule_version=rule.rule_version,
            rule_id=rule.rule_id,
            rainfall_mm=clean_rainfall_mm,
            panchayat_name=p_name,
            block_name=b_name,
            forecast_date=f_date,
            lead_days=l_days,
            language=active_lang,
            available_languages=ALL_SUPPORTED_LANGUAGES.copy(),
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================
_DEFAULT_ENGINE = AdvisoryEngine()


def generate_agricultural_advisory(
    rainfall_mm: Any,
    panchayat_name: str,
    block_name: str,
    forecast_date: Union[str, Any],
    lead_days: int = 0,
    rainfall_category: Optional[str] = None,
    language: str = DEFAULT_LANGUAGE,
) -> AdvisoryOutput:
    """
    Convenience function to generate a rule-based advisory using the default engine.
    """
    return _DEFAULT_ENGINE.generate_advisory(
        rainfall_mm=rainfall_mm,
        panchayat_name=panchayat_name,
        block_name=block_name,
        forecast_date=forecast_date,
        lead_days=lead_days,
        rainfall_category=rainfall_category,
        language=language,
    )

