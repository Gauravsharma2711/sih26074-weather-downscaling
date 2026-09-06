"""
Pydantic Schemas for Farmer-Facing Forecast & Advisory Endpoints.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class FarmerForecastResponse(BaseModel):
    """
    Farmer-friendly synthesized weather forecast and agricultural advisory response.
    Delivers hyper-local downscaled weather insights and verified agronomic actions
    without exposing internal technical, database, or officer metadata.
    """
    model_config = ConfigDict(from_attributes=True)

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
    district_name: str = Field(
        ...,
        description="Administrative District name",
        examples=["Nashik"],
    )
    forecast_date: date = Field(
        ...,
        description="Validity date for the predicted rainfall forecast (YYYY-MM-DD)",
        examples=["2026-09-08"],
    )
    rainfall_mm: float = Field(
        ...,
        description="Predicted downscaled rainfall amount in millimeters",
        examples=[18.5],
    )
    rainfall_category: str = Field(
        ...,
        description="Standardized rainfall intensity classification",
        examples=["Moderate rainfall"],
    )
    severity: str = Field(
        ...,
        description="Agricultural action urgency level (LOW, MODERATE, HIGH, CRITICAL)",
        examples=["MODERATE"],
    )
    advisory_title: Optional[str] = Field(
        None,
        description="Summary advisory headline for farmers (populated only when approved)",
        examples=["Moderate Rainfall Advisory for Ajmer Saundane - Drainage Preparedness & Irrigation Suspension"],
    )
    advisory_points: List[str] = Field(
        default_factory=list,
        description="List of actionable, conservative field guidance points (populated only when approved)",
        examples=[[
            "Temporarily suspend all irrigation operations as rainfall will satisfy crop water demand.",
            "Inspect and clean field drainage channels to ensure free flow and prevent water stagnation.",
        ]],
    )
    advisory_status: str = Field(
        ...,
        description="Status of agronomic advisory ('APPROVED', 'NO_APPROVED_ADVISORY', or 'PENDING_OFFICER_REVIEW')",
        examples=["APPROVED"],
    )
    model_name: str = Field(
        ...,
        description="Name of the high-resolution meteorological downscaling model",
        examples=["XGBoost Regressor"],
    )
    model_version: str = Field(
        ...,
        description="Operational release version of the meteorological downscaling model",
        examples=["v1.0.0"],
    )
    language: str = Field(
        default="en",
        description="Language code of the advisory response ('en', 'mr', 'hi')",
        examples=["en"],
    )
    available_languages: List[str] = Field(
        default_factory=lambda: ["en", "mr", "hi"],
        description="List of supported multilingual language codes",
        examples=[["en", "mr", "hi"]],
    )
    language_status: Optional[str] = Field(
        None,
        description="Translation review/readiness status (e.g. 'VERIFIED_PRIMARY', 'STRUCTURED_REVIEWED')",
        examples=["VERIFIED_PRIMARY"],
    )
