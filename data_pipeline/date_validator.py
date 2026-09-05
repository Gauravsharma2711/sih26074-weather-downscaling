import os
import logging
from typing import Tuple, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

# Lead days classification mapping according to SIH26074 guidelines
LEAD_CLASSIFICATION = {
    0: "same-day forecast",
    1: "next-day forecast",
    2: "two-day forecast",
    3: "three-day forecast",
    4: "four-day forecast",
    5: "five-day forecast",
}


def validate_forecast_dates(
    input_path: str = "data/processed/nashik_weather_clean.csv",
    output_path: str = "data/validation/date_validation.csv"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate and audit forecast dates and compute lead horizon (lead_days):
    - Parses date and forecast_issue_date
    - Computes lead_days = date - forecast_issue_date
    - Flags missing or invalid dates
    - Flags temporal inconsistencies (date < issue_date or lead_days < 0)
    - Flags out-of-range forecasts (lead_days > 5)
    
    Generates data/validation/date_validation.csv.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8")

    validation_records = []

    for _, row in df.iterrows():
        pid = row["panchayat_id"]
        raw_date = row.get("date")
        raw_issue_date = row.get("forecast_issue_date")

        reasons = []
        status = "VALID"
        lead_days = None

        # Check 1: Missing date fields
        if pd.isna(raw_date) or pd.isna(raw_issue_date):
            reasons.append("Missing date or forecast_issue_date")
            status = "INVALID"
        else:
            try:
                date_val = pd.to_datetime(raw_date)
                issue_date_val = pd.to_datetime(raw_issue_date)

                diff = (date_val - issue_date_val).days
                lead_days = int(diff)

                # Check 2: Forecast date before issue date
                if lead_days < 0:
                    reasons.append(f"Forecast date ({raw_date}) is before issue date ({raw_issue_date}) [lead_days={lead_days}]")
                    status = "INVALID"

                # Check 3: Lead days > 5
                elif lead_days > 5:
                    reasons.append(f"Lead horizon ({lead_days} days) exceeds maximum 5-day forecast limit")
                    status = "WARNING"

                # Check 4: Valid forecast horizons (0-5 days)
                else:
                    classification = LEAD_CLASSIFICATION.get(lead_days, f"{lead_days}-day forecast")
                    reasons.append(f"Valid {classification} (lead_days={lead_days})")

            except Exception as e:
                reasons.append(f"Invalid date format: {e}")
                status = "INVALID"

        validation_records.append({
            "panchayat_id": pid,
            "date": raw_date,
            "forecast_issue_date": raw_issue_date,
            "lead_days": lead_days,
            "validation_status": status,
            "validation_reason": "; ".join(reasons)
        })

    val_df = pd.DataFrame(validation_records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    val_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Forecast date validation report saved to {output_path} ({len(val_df)} rows).")

    # Generate Frequency Table
    freq_series = val_df["lead_days"].value_counts(dropna=False).sort_index()
    freq_data = []
    total = len(val_df)

    for lead_val, count in freq_series.items():
        if pd.isna(lead_val):
            label = "Missing / Invalid"
        else:
            label = LEAD_CLASSIFICATION.get(int(lead_val), f"{int(lead_val)}-day forecast")
        freq_data.append({
            "lead_days": lead_val,
            "classification": label,
            "count": count,
            "percentage": f"{(count / total) * 100:.2f}%"
        })

    freq_df = pd.DataFrame(freq_data)
    return val_df, freq_df
