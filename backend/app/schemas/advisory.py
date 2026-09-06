"""
Pydantic Schemas for Agricultural Advisory Generation and Retrieval Endpoints.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AdvisoryGenerateRequest(BaseModel):
    """
    Request payload for generating a deterministic agricultural advisory from a stored forecast.
    """
    model_config = ConfigDict(from_attributes=True)

    forecast_id: int = Field(
        ...,
        ge=1,
        description="Unique identifier of the target stored forecast in downscaled_forecasts",
        examples=[1],
    )


class AdvisoryResponse(BaseModel):
    """
    Agricultural advisory response representing a generated or stored advisory record.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique identifier of the advisory record in Supabase",
        examples=[1],
    )
    panchayat_id: int = Field(
        ...,
        description="Unique system identifier of the target Gram Panchayat",
        examples=[1001],
    )
    forecast_id: Optional[int] = Field(
        None,
        description="Referenced downscaled forecast record identifier",
        examples=[1],
    )
    forecast_date: date = Field(
        ...,
        description="Target validity date for the advisory (YYYY-MM-DD)",
        examples=["2026-09-08"],
    )
    rainfall_mm: Optional[float] = Field(
        None,
        description="Downscaled predicted rainfall amount in mm",
        examples=[18.5],
    )
    rainfall_category: Optional[str] = Field(
        None,
        description="Standardized rainfall intensity category",
        examples=["Moderate rainfall"],
    )
    severity: Optional[str] = Field(
        None,
        description="Urgency/severity level (LOW, MODERATE, HIGH, CRITICAL)",
        examples=["MODERATE"],
    )
    advisory_title: Optional[str] = Field(
        None,
        description="Advisory summary headline",
        examples=["Moderate Rainfall Advisory for Ajmer Saundane - Drainage Preparedness & Irrigation Suspension"],
    )
    advisory_text: Optional[str] = Field(
        None,
        description="Bulleted actionable generic agricultural guidance",
        examples=["• Suspend all irrigation operations as anticipated rainfall will meet crop water requirements."],
    )
    rule_version: Optional[str] = Field(
        None,
        description="Version tag of the applied deterministic rule",
        examples=["v1.0.0"],
    )
    status: str = Field(
        ...,
        description="Workflow review status: DRAFT, APPROVED, PUBLISHED, or REJECTED",
        examples=["DRAFT"],
    )
    officer_id: Optional[str] = Field(
        None,
        description="Identifier of extension officer who reviewed/approved the advisory",
        examples=[None],
    )
    officer_comment: Optional[str] = Field(
        None,
        description="Officer remarks or local adjustments",
        examples=[None],
    )
    approved_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the advisory was approved",
        examples=[None],
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the advisory draft was generated",
    )
    language: str = Field(
        default="en",
        description="Canonical language code ('en')",
        examples=["en"],
    )
    available_languages: list[str] = Field(
        default_factory=lambda: ["en", "mr", "hi"],
        description="List of supported multilingual language codes",
        examples=[["en", "mr", "hi"]],
    )
    language_status: Optional[str] = Field(
        None,
        description="Translation review/readiness status (e.g. 'VERIFIED_PRIMARY')",
        examples=["VERIFIED_PRIMARY"],
    )


class PanchayatAdvisoryRetrievalResponse(BaseModel):
    """
    Farmer-facing agricultural advisory response for a Gram Panchayat.
    Exclusively serves APPROVED advisories with complete administrative spatial names.
    """
    model_config = ConfigDict(from_attributes=True)

    advisory_id: int = Field(
        ...,
        description="Unique identifier of the approved advisory record",
        examples=[1],
    )
    panchayat_id: int = Field(
        ...,
        description="Unique Gram Panchayat identifier",
        examples=[1001],
    )
    panchayat_name: str = Field(
        ...,
        description="Name of the Gram Panchayat",
        examples=["Ajmer Saundane"],
    )
    block_name: str = Field(
        ...,
        description="Administrative Tehsil / Block name",
        examples=["Baglan"],
    )
    forecast_date: date = Field(
        ...,
        description="Target validity date for the advisory (YYYY-MM-DD)",
        examples=["2026-09-08"],
    )
    rainfall_mm: Optional[float] = Field(
        None,
        description="Downscaled predicted rainfall amount in mm",
        examples=[18.5],
    )
    rainfall_category: Optional[str] = Field(
        None,
        description="Standardized rainfall intensity category",
        examples=["Moderate rainfall"],
    )
    severity: Optional[str] = Field(
        None,
        description="Urgency/severity level (LOW, MODERATE, HIGH, CRITICAL)",
        examples=["MODERATE"],
    )
    advisory_title: Optional[str] = Field(
        None,
        description="Advisory summary headline",
        examples=["Moderate Rainfall Advisory for Ajmer Saundane - Drainage Preparedness & Irrigation Suspension"],
    )
    advisory_text: Optional[str] = Field(
        None,
        description="Bulleted actionable generic agricultural guidance",
        examples=["• Suspend all irrigation operations as anticipated rainfall will meet crop water requirements."],
    )
    rule_version: Optional[str] = Field(
        None,
        description="Version tag of the applied deterministic rule",
        examples=["v1.0.0"],
    )
    status: str = Field(
        ...,
        description="Workflow review status (always 'APPROVED' for farmer retrieval)",
        examples=["APPROVED"],
    )
    approved_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the extension officer approved the advisory",
    )
    language: str = Field(
        default="en",
        description="Language code of the advisory response ('en', 'mr', 'hi')",
        examples=["en"],
    )
    available_languages: list[str] = Field(
        default_factory=lambda: ["en", "mr", "hi"],
        description="List of supported multilingual language codes",
        examples=[["en", "mr", "hi"]],
    )
    language_status: Optional[str] = Field(
        None,
        description="Translation review/readiness status (e.g. 'VERIFIED_PRIMARY', 'STRUCTURED_REVIEWED')",
        examples=["VERIFIED_PRIMARY"],
    )


class OfficerApproveRequest(BaseModel):
    """
    Request payload for extension officer approval of a draft agricultural advisory.
    """
    model_config = ConfigDict(from_attributes=True)

    officer_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier of the reviewing extension officer",
        examples=["OFFICER_BAGLAN_01"],
    )
    officer_comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional officer validation remarks, field notes, or guidance additions",
        examples=["Verified against ground conditions. Advisory approved for distribution."],
    )


class OfficerRejectRequest(BaseModel):
    """
    Request payload for extension officer rejection of a draft agricultural advisory.
    """
    model_config = ConfigDict(from_attributes=True)

    officer_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identifier of the reviewing extension officer",
        examples=["OFFICER_BAGLAN_01"],
    )
    officer_comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Reason or remarks for advisory rejection",
        examples=["Rainfall forecast adjusted based on local micro-climate observations; draft discarded."],
    )

