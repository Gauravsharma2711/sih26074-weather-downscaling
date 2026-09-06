"""
Panchayat API Endpoints.
Provides access to Nashik Gram Panchayats with geo-spatial attributes for weather downscaling.
"""

import math
import logging
from typing import Optional
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, Depends, Query, Path as FastAPIPath, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, cast, String

from backend.app.core.database import get_db
from backend.app.core.logging import log_db_operation
from backend.app.models.panchayat_weather import PanchayatWeatherData
from backend.app.schemas.panchayat import (
    PanchayatItem,
    PanchayatPagination,
    PanchayatDetailResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

PROCESSED_DATA_PATH = Path("data/processed/nashik_weather_clean.csv")


@router.get(
    "/panchayats",
    response_model=PanchayatPagination,
    summary="List Nashik District Panchayats",
    description=(
        "Retrieves a paginated list of Gram Panchayats in Nashik District with geographical "
        "coordinates (latitude, longitude, elevation) required for micro-level weather downscaling. "
        "Supports optional filtering by administrative block and case-insensitive search."
    ),
    response_description="Paginated list of Nashik Panchayats",
    tags=["Panchayats"],
)
def get_panchayats(
    block_name: Optional[str] = Query(
        None,
        min_length=1,
        max_length=100,
        description="Optional filter by administrative block/tehsil (e.g., 'Baglan', 'Dindori', 'Surgana', 'Igatpuri'). Case-insensitive.",
        examples=["Baglan"],
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        max_length=100,
        description="Optional search query matching panchayat name, block name, or LGD code (case-insensitive).",
        examples=["Ajmer"],
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number (1-indexed). Must be greater than or equal to 1.",
        examples=[1],
    ),
    page_size: int = Query(
        50,
        ge=1,
        le=500,
        description="Number of records to return per page (1 to 500). Default is 50.",
        examples=[50],
    ),
    db: Session = Depends(get_db),
) -> PanchayatPagination:
    """
    Fetch paginated Gram Panchayats from Supabase PostgreSQL database.
    Applies optional block filter and search query, returning safe public fields.
    """
    logger.info(
        f"[REQUEST] request_type=GET /api/v1/panchayats block_name={block_name} "
        f"search={search} page={page} page_size={page_size}"
    )
    try:
        # Build base query for distinct Panchayat metadata
        query = db.query(
            PanchayatWeatherData.panchayat_id,
            PanchayatWeatherData.lgd_code,
            PanchayatWeatherData.panchayat_name,
            PanchayatWeatherData.block_name,
            PanchayatWeatherData.district_name,
            PanchayatWeatherData.panchayat_latitude.label("latitude"),
            PanchayatWeatherData.panchayat_longitude.label("longitude"),
            PanchayatWeatherData.elevation_m,
        ).group_by(
            PanchayatWeatherData.panchayat_id,
            PanchayatWeatherData.lgd_code,
            PanchayatWeatherData.panchayat_name,
            PanchayatWeatherData.block_name,
            PanchayatWeatherData.district_name,
            PanchayatWeatherData.panchayat_latitude,
            PanchayatWeatherData.panchayat_longitude,
            PanchayatWeatherData.elevation_m,
        )

        # Apply block_name filter
        if block_name and block_name.strip():
            clean_block = block_name.strip().lower()
            query = query.filter(
                func.lower(PanchayatWeatherData.block_name) == clean_block
            )

        # Apply search filter across panchayat_name, block_name, and lgd_code
        if search and search.strip():
            search_pattern = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(PanchayatWeatherData.panchayat_name).ilike(search_pattern),
                    func.lower(PanchayatWeatherData.block_name).ilike(search_pattern),
                    cast(PanchayatWeatherData.lgd_code, String).ilike(search_pattern),
                    cast(PanchayatWeatherData.panchayat_id, String).ilike(search_pattern),
                )
            )

        # Order consistently by panchayat_id
        query = query.order_by(PanchayatWeatherData.panchayat_id.asc())

        # Count total distinct results
        total = query.count()

        # Apply pagination offset and limit
        offset = (page - 1) * page_size
        results = query.offset(offset).limit(page_size).all()

        items = [
            PanchayatItem(
                panchayat_id=int(row.panchayat_id),
                lgd_code=int(row.lgd_code),
                panchayat_name=str(row.panchayat_name),
                block_name=str(row.block_name),
                district_name=str(row.district_name),
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                elevation_m=float(row.elevation_m),
            )
            for row in results
        ]

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PanchayatPagination(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            items=items,
        )

    except Exception as db_exc:
        logger.warning(
            f"Database query failed ({db_exc}). Attempting fallback to local processed registry."
        )
        if PROCESSED_DATA_PATH.exists():
            try:
                df = pd.read_csv(PROCESSED_DATA_PATH)
                cols = [
                    "panchayat_id",
                    "lgd_code",
                    "panchayat_name",
                    "block_name",
                    "district_name",
                    "panchayat_latitude",
                    "panchayat_longitude",
                    "elevation_m",
                ]
                df_unique = df[cols].drop_duplicates().rename(
                    columns={
                        "panchayat_latitude": "latitude",
                        "panchayat_longitude": "longitude",
                    }
                )

                if block_name and block_name.strip():
                    df_unique = df_unique[
                        df_unique["block_name"].str.lower() == block_name.strip().lower()
                    ]

                if search and search.strip():
                    st = search.strip().lower()
                    match_mask = (
                        df_unique["panchayat_name"].str.lower().str.contains(st, na=False)
                        | df_unique["block_name"].str.lower().str.contains(st, na=False)
                        | df_unique["lgd_code"].astype(str).str.contains(st, na=False)
                        | df_unique["panchayat_id"].astype(str).str.contains(st, na=False)
                    )
                    df_unique = df_unique[match_mask]

                df_unique = df_unique.sort_values(by="panchayat_id")
                total = len(df_unique)
                total_pages = math.ceil(total / page_size) if total > 0 else 0

                offset = (page - 1) * page_size
                paged_df = df_unique.iloc[offset : offset + page_size]

                items = [
                    PanchayatItem(
                        panchayat_id=int(r["panchayat_id"]),
                        lgd_code=int(r["lgd_code"]),
                        panchayat_name=str(r["panchayat_name"]),
                        block_name=str(r["block_name"]),
                        district_name=str(r["district_name"]),
                        latitude=float(r["latitude"]),
                        longitude=float(r["longitude"]),
                        elevation_m=float(r["elevation_m"]),
                    )
                    for _, r in paged_df.iterrows()
                ]

                return PanchayatPagination(
                    total=total,
                    page=page,
                    page_size=page_size,
                    total_pages=total_pages,
                    items=items,
                )
            except Exception as file_exc:
                logger.error(f"Fallback registry failed: {file_exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve panchayats from database or fallback store.",
        )


@router.get(
    "/panchayats/{panchayat_id}",
    response_model=PanchayatDetailResponse,
    summary="Get Panchayat Details by ID",
    description=(
        "Retrieves detailed geographic and administrative metadata for a specific Gram Panchayat "
        "by its unique system ID (panchayat_id). Returns HTTP 404 if the Panchayat does not exist."
    ),
    response_description="Detailed metadata for the requested Gram Panchayat",
    responses={
        200: {"description": "Panchayat found and metadata returned successfully."},
        404: {"description": "Panchayat with the specified ID was not found."},
    },
    tags=["Panchayats"],
)
def get_panchayat_by_id(
    panchayat_id: int = FastAPIPath(
        ...,
        ge=1,
        description="Unique identifier of the Gram Panchayat (e.g., 1001, 2099)",
        examples=[1001],
    ),
    db: Session = Depends(get_db),
) -> PanchayatDetailResponse:
    """
    Fetch a single Gram Panchayat by ID from Supabase PostgreSQL database.
    Returns HTTP 404 if the Panchayat is not found.
    """
    logger.info(
        f"[REQUEST] request_type=GET /api/v1/panchayats/{{panchayat_id}} panchayat_id={panchayat_id}"
    )
    try:
        row = (
            db.query(
                PanchayatWeatherData.panchayat_id,
                PanchayatWeatherData.lgd_code,
                PanchayatWeatherData.panchayat_name,
                PanchayatWeatherData.block_name,
                PanchayatWeatherData.district_name,
                PanchayatWeatherData.panchayat_latitude.label("latitude"),
                PanchayatWeatherData.panchayat_longitude.label("longitude"),
                PanchayatWeatherData.elevation_m,
            )
            .filter(PanchayatWeatherData.panchayat_id == panchayat_id)
            .first()
        )

        if row is not None:
            log_db_operation(
                logger=logger,
                operation="SELECT",
                table="panchayat_weather_data",
                status="SUCCESS",
                panchayat_id=panchayat_id,
                details=f"panchayat_name=\"{row.panchayat_name}\" block_name=\"{row.block_name}\"",
            )
            return PanchayatDetailResponse(
                panchayat_id=int(row.panchayat_id),
                lgd_code=int(row.lgd_code),
                panchayat_name=str(row.panchayat_name),
                block_name=str(row.block_name),
                district_name=str(row.district_name),
                latitude=float(row.latitude),
                longitude=float(row.longitude),
                elevation_m=float(row.elevation_m),
            )

        # If not found in DB, log warning and return 404
        log_db_operation(
            logger=logger,
            operation="SELECT",
            table="panchayat_weather_data",
            status="NOT_FOUND",
            panchayat_id=panchayat_id,
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panchayat with ID {panchayat_id} not found.",
        )

    except HTTPException:
        # Re-raise explicit HTTP 404
        raise
    except Exception as db_exc:
        logger.warning(
            f"Database query failed for panchayat_id={panchayat_id} ({db_exc}). Attempting fallback."
        )
        if PROCESSED_DATA_PATH.exists():
            try:
                df = pd.read_csv(PROCESSED_DATA_PATH)
                match = df[df["panchayat_id"] == panchayat_id]
                if not match.empty:
                    r = match.iloc[0]
                    return PanchayatDetailResponse(
                        panchayat_id=int(r["panchayat_id"]),
                        lgd_code=int(r["lgd_code"]),
                        panchayat_name=str(r["panchayat_name"]),
                        block_name=str(r["block_name"]),
                        district_name=str(r["district_name"]),
                        latitude=float(r["panchayat_latitude"]),
                        longitude=float(r["panchayat_longitude"]),
                        elevation_m=float(r["elevation_m"]),
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Panchayat with ID {panchayat_id} not found.",
                    )
            except HTTPException:
                raise
            except Exception as file_exc:
                logger.error(f"Fallback registry failed for panchayat_id={panchayat_id}: {file_exc}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve panchayat details from database or fallback store.",
        )
