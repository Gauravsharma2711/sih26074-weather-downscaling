# ML Features Layer

## Predictors (X)
The downscaling model uses the following physical, geographical, and temporal features:
1. `block_forecast_rainfall_mm`: Official IMD Block forecast value.
2. `panchayat_latitude`: Latitude coordinate of the Panchayat center.
3. `panchayat_longitude`: Longitude coordinate of the Panchayat center.
4. `elevation_m`: Elevation above sea level (ISRO-NRSC DEM).
5. `station_distance_km`: Proximity to validation AWS/ARG station.
6. `lead_days`: Forecast lead horizon (`date` minus `forecast_issue_date`).
7. `month`: Month (1–12) capturing seasonal monsoon patterns.
8. `day_of_year`: Day of year (1–366) capturing annual cycle.

## Target (y)
- `actual_rainfall_mm`: 24-hour recorded ground truth rainfall.
