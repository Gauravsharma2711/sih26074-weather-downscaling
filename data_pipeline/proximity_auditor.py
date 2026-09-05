import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Distance classification thresholds in kilometers
PROXIMITY_OPTIMAL_KM = 25.0
PROXIMITY_FAR_KM = 50.0


def audit_station_proximity(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/station_proximity.csv",
    optimal_threshold_km: float = PROXIMITY_OPTIMAL_KM,
    far_threshold_km: float = PROXIMITY_FAR_KM
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Perform proximity audit on Panchayat-to-Station distances:
    - Analyzes min, max, mean, median, 25th, and 75th percentiles grouped by block.
    - Flags Panchayats with moderate (25-50km) and unusually large (>50km) station distances.
    - Preserves all records without deleting distant stations.

    Outputs:
    data/validation/station_proximity.csv
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    # Group by block and calculate distance distribution metrics
    block_stats_records = []
    grouped = df.groupby("block_name", sort=True)

    for bname, group in grouped:
        dist = group["station_distance_km"].dropna()
        block_stats_records.append({
            "block_name": bname,
            "record_count": len(group),
            "min_distance_km": round(float(dist.min()), 2),
            "p25_distance_km": round(float(dist.quantile(0.25)), 2),
            "median_distance_km": round(float(dist.median()), 2),
            "mean_distance_km": round(float(dist.mean()), 2),
            "p75_distance_km": round(float(dist.quantile(0.75)), 2),
            "max_distance_km": round(float(dist.max()), 2),
        })

    block_summary_df = pd.DataFrame(block_stats_records)

    # Classify each Panchayat record
    proximity_status = []
    proximity_reasons = []

    for _, row in df.iterrows():
        d = row["station_distance_km"]
        if pd.isna(d):
            proximity_status.append("INVALID")
            proximity_reasons.append("Missing station distance coordinates")
        elif d <= optimal_threshold_km:
            proximity_status.append("NORMAL")
            proximity_reasons.append(f"Optimal proximity (distance {d:.2f} km <= {optimal_threshold_km:.1f} km)")
        elif d <= far_threshold_km:
            proximity_status.append("MODERATE")
            proximity_reasons.append(f"Moderate distance ({d:.2f} km); spatial terrain gradient requires ML downscaling")
        else:
            proximity_status.append("REVIEW_REQUIRED")
            proximity_reasons.append(f"High distance ({d:.2f} km > {far_threshold_km:.1f} km); sparse station network flagged for review")

    proximity_df = pd.DataFrame({
        "panchayat_id": df["panchayat_id"],
        "panchayat_name": df["panchayat_name"],
        "block_name": df["block_name"],
        "station_id": df["station_id"],
        "calculated_station_distance_km": df["station_distance_km"].round(2),
        "proximity_status": proximity_status,
        "proximity_reason": proximity_reasons
    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    proximity_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Station proximity audit saved to {output_path} ({len(proximity_df)} records).")

    all_dists = df["station_distance_km"].dropna()
    stats = {
        "total_records": len(df),
        "normal_count": int((proximity_df["proximity_status"] == "NORMAL").sum()),
        "moderate_count": int((proximity_df["proximity_status"] == "MODERATE").sum()),
        "review_required_count": int((proximity_df["proximity_status"] == "REVIEW_REQUIRED").sum()),
        "min_distance_km": round(float(all_dists.min()), 2),
        "p25_distance_km": round(float(all_dists.quantile(0.25)), 2),
        "median_distance_km": round(float(all_dists.median()), 2),
        "mean_distance_km": round(float(all_dists.mean()), 2),
        "p75_distance_km": round(float(all_dists.quantile(0.75)), 2),
        "max_distance_km": round(float(all_dists.max()), 2),
    }

    return proximity_df, block_summary_df, stats
