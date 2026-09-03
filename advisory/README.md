# Agro-Meteorological Advisory Engine

## Overview
The `advisory` module converts hyper-local Panchayat-level weather forecasts into clear, actionable agricultural advisories for farmers.

## Operational Workflow
```text
[Panchayat Weather Forecast]
           ↓
[Agromet Rules Engine]
           ↓
[Draft Advisory Generated (Status: Pending)]
           ↓
[Agricultural Officer Review (Approve / Edit / Reject)]
           ↓
[Approved Advisory Published to Farmers]
```

## Core Advisory Rules (V1)
Transparent, rule-based logic derived from IMD Agromet / GKMS guidelines:
- **High Rain Risk (> 20mm)**: "Do not spray pesticides or foliar nutrients; high risk of runoff and wash-off."
- **Heavy Rain (> 50mm)**: "Delay fertilizer application, seed sowing, and field preparation; ensure field drainage channels are clear."
- **Low/No Rain + Soil Dryness**: "Irrigation recommended within 24–48 hours for moisture-sensitive standing crops."
- **High Wind / Squall**: "Provide staking/propping support for tall standing crops (e.g., banana, sugarcane, maize)."

## Required Advisory Payload Structure
Every advisory record contains:
- `panchayat_id` / `panchayat_name`
- `action` (e.g., "Postpone pesticide spraying")
- `reason` (e.g., "Predicted rainfall of 32mm will wash away chemicals")
- `forecast_values` (rainfall, temperature, humidity, wind)
- `confidence` (high / medium / low)
- `status` (`pending_review`, `approved`, `modified`, `rejected`)
- `reviewed_by` & `reviewed_at`
