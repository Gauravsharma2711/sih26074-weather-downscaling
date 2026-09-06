"""
API v1 Extension Officer Advisory Endpoints.

Provides endpoints for agricultural extension officers to review, inspect, approve,
and reject deterministic agricultural advisories before they are served to farmers.
"""

import logging
from datetime import date, datetime, timezone
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.advisory import Advisory
from backend.app.schemas.advisory import (
    AdvisoryResponse,
    OfficerApproveRequest,
    OfficerRejectRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/officer/advisories",
    response_model=List[AdvisoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Advisories for Extension Officer Review",
    description="""
    Retrieve a paginated list of agricultural advisories with optional filtering by review status,
    Panchayat ID, and forecast date.

    Review Statuses:
    - `DRAFT`: Newly generated advisories awaiting officer inspection.
    - `APPROVED`: Validated advisories available to farmer-facing endpoints.
    - `REJECTED`: Discarded or invalid drafts.
    """,
    responses={
        200: {
            "description": "List of advisory records matching filter criteria.",
            "model": List[AdvisoryResponse],
        },
        422: {
            "description": "Validation error for filter parameters.",
        },
    },
)
def list_officer_advisories(
    review_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by workflow status (DRAFT, APPROVED, REJECTED)",
        examples=["DRAFT"],
    ),
    panchayat_id: Optional[int] = Query(
        None,
        ge=1,
        description="Filter by specific Gram Panchayat ID",
        examples=[1001],
    ),
    forecast_date: Optional[date] = Query(
        None,
        description="Filter by forecast validity date (YYYY-MM-DD)",
        examples=["2026-09-08"],
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Number of records to return per page (max 100)",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of records to skip for pagination",
    ),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP GET handler to list agricultural advisories with filtering and pagination.
    """
    query = db.query(Advisory)

    if review_status:
        query = query.filter(Advisory.status == review_status.upper())

    if panchayat_id:
        query = query.filter(Advisory.panchayat_id == panchayat_id)

    if forecast_date:
        query = query.filter(Advisory.forecast_date == forecast_date)

    advisories = (
        query
        .order_by(
            Advisory.forecast_date.desc(),
            Advisory.created_at.desc(),
            Advisory.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    logger.info(
        f"[OFFICER_LIST_ADVISORIES] count={len(advisories)} status={review_status} "
        f"panchayat_id={panchayat_id} forecast_date={forecast_date}"
    )
    return advisories


@router.get(
    "/officer/advisories/{advisory_id}",
    response_model=AdvisoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Advisory Detail for Officer Review",
    description="""
    Retrieve full inspection details of an agricultural advisory by its unique ID.
    """,
    responses={
        200: {
            "description": "Advisory details successfully retrieved.",
            "model": AdvisoryResponse,
        },
        404: {
            "description": "Advisory not found.",
            "content": {"application/json": {"example": {"detail": "Advisory with ID '1' not found."}}},
        },
        422: {
            "description": "Validation error for advisory_id path parameter.",
        },
    },
)
def get_officer_advisory(
    advisory_id: int = Path(
        ...,
        ge=1,
        description="Unique identifier of the target advisory",
        examples=[1],
    ),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP GET handler to retrieve detailed advisory record by ID.
    """
    advisory = db.query(Advisory).filter(Advisory.id == advisory_id).first()
    if not advisory:
        logger.warning(f"[OFFICER_ADVISORY_NOT_FOUND] advisory_id={advisory_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advisory with ID '{advisory_id}' not found.",
        )

    return advisory


@router.post(
    "/officer/advisories/{advisory_id}/approve",
    response_model=AdvisoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Draft Advisory for Farmer Distribution",
    description="""
    Approve a `DRAFT` agricultural advisory, transitioning its workflow status to `APPROVED`.

    Review & Safety Rules:
    - Only `DRAFT` advisories can be approved (`DRAFT → APPROVED`).
    - Approved advisories cannot be silently changed. If already approved, returns HTTP 409 Conflict.
    - If an advisory was previously `REJECTED`, returns HTTP 400 Bad Request (requires explicit new revision).
    - Records the reviewing extension officer's identifier, validation comments, and approval timestamp.
    """,
    responses={
        200: {
            "description": "Advisory successfully approved and released for farmer retrieval.",
            "model": AdvisoryResponse,
        },
        400: {
            "description": "Invalid state transition (e.g. attempting to approve a rejected advisory).",
            "content": {"application/json": {"example": {"detail": "Cannot approve advisory with ID '1' because it has been REJECTED."}}},
        },
        404: {
            "description": "Advisory not found.",
            "content": {"application/json": {"example": {"detail": "Advisory with ID '1' not found."}}},
        },
        409: {
            "description": "Conflict: Advisory is already approved.",
            "content": {"application/json": {"example": {"detail": "Advisory with ID '1' is already APPROVED. Approved advisories cannot be modified silently."}}},
        },
    },
)
def approve_advisory(
    payload: OfficerApproveRequest,
    advisory_id: int = Path(
        ...,
        ge=1,
        description="Unique identifier of the draft advisory to approve",
        examples=[1],
    ),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP POST handler to approve a draft advisory.
    """
    advisory = db.query(Advisory).filter(Advisory.id == advisory_id).first()
    if not advisory:
        logger.warning(f"[OFFICER_APPROVE_NOT_FOUND] advisory_id={advisory_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advisory with ID '{advisory_id}' not found.",
        )

    # Validate state transition
    if advisory.status == "APPROVED":
        logger.warning(
            f"[OFFICER_APPROVE_CONFLICT_ALREADY_APPROVED] advisory_id={advisory_id} "
            f"existing_officer_id={advisory.officer_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Advisory with ID '{advisory_id}' is already APPROVED. Approved advisories cannot be modified silently.",
        )

    if advisory.status == "REJECTED":
        logger.warning(f"[OFFICER_APPROVE_REJECTED_BLOCKED] advisory_id={advisory_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve advisory with ID '{advisory_id}' because it has been REJECTED. Create a new revision instead.",
        )

    if advisory.status != "DRAFT":
        logger.warning(f"[OFFICER_APPROVE_INVALID_STATUS] advisory_id={advisory_id} status={advisory.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve advisory with ID '{advisory_id}' with status '{advisory.status}'. Only DRAFT advisories can be approved.",
        )

    # Perform approval transition
    advisory.status = "APPROVED"
    advisory.officer_id = payload.officer_id.strip()
    advisory.officer_comment = payload.officer_comment.strip() if payload.officer_comment else None
    advisory.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(advisory)

    logger.info(
        f"[OFFICER_ADVISORY_APPROVED] advisory_id={advisory_id} officer_id=\"{advisory.officer_id}\" "
        f"panchayat_id={advisory.panchayat_id} approved_at={advisory.approved_at}"
    )
    return advisory


@router.post(
    "/officer/advisories/{advisory_id}/reject",
    response_model=AdvisoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject Draft Advisory",
    description="""
    Reject a `DRAFT` agricultural advisory, transitioning its workflow status to `REJECTED`.

    Review & Safety Rules:
    - Only `DRAFT` advisories can be rejected (`DRAFT → REJECTED`).
    - Approved advisories cannot be silently changed or rejected directly. If already approved, returns HTTP 409 Conflict.
    - If an advisory is already `REJECTED`, returns HTTP 409 Conflict.
    - Records the reviewing extension officer's identifier and rejection remarks.
    """,
    responses={
        200: {
            "description": "Advisory successfully rejected.",
            "model": AdvisoryResponse,
        },
        400: {
            "description": "Invalid state transition.",
            "content": {"application/json": {"example": {"detail": "Cannot reject advisory in current status."}}},
        },
        404: {
            "description": "Advisory not found.",
            "content": {"application/json": {"example": {"detail": "Advisory with ID '1' not found."}}},
        },
        409: {
            "description": "Conflict: Advisory is already approved or already rejected.",
            "content": {"application/json": {"example": {"detail": "Advisory with ID '1' is already APPROVED. Approved advisories cannot be modified silently."}}},
        },
    },
)
def reject_advisory(
    payload: OfficerRejectRequest,
    advisory_id: int = Path(
        ...,
        ge=1,
        description="Unique identifier of the draft advisory to reject",
        examples=[1],
    ),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP POST handler to reject a draft advisory.
    """
    advisory = db.query(Advisory).filter(Advisory.id == advisory_id).first()
    if not advisory:
        logger.warning(f"[OFFICER_REJECT_NOT_FOUND] advisory_id={advisory_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advisory with ID '{advisory_id}' not found.",
        )

    # Validate state transition
    if advisory.status == "APPROVED":
        logger.warning(
            f"[OFFICER_REJECT_CONFLICT_APPROVED] advisory_id={advisory_id} "
            f"existing_officer_id={advisory.officer_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Advisory with ID '{advisory_id}' is already APPROVED. Approved advisories cannot be silently changed. An explicit revision process is required.",
        )

    if advisory.status == "REJECTED":
        logger.warning(f"[OFFICER_REJECT_ALREADY_REJECTED] advisory_id={advisory_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Advisory with ID '{advisory_id}' is already REJECTED.",
        )

    if advisory.status != "DRAFT":
        logger.warning(f"[OFFICER_REJECT_INVALID_STATUS] advisory_id={advisory_id} status={advisory.status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject advisory with ID '{advisory_id}' with status '{advisory.status}'. Only DRAFT advisories can be rejected.",
        )

    # Perform rejection transition
    advisory.status = "REJECTED"
    advisory.officer_id = payload.officer_id.strip()
    advisory.officer_comment = payload.officer_comment.strip() if payload.officer_comment else None

    db.commit()
    db.refresh(advisory)

    logger.info(
        f"[OFFICER_ADVISORY_REJECTED] advisory_id={advisory_id} officer_id=\"{advisory.officer_id}\" "
        f"panchayat_id={advisory.panchayat_id}"
    )
    return advisory
