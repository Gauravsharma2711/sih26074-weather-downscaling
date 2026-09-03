# Machine Learning Downscaling Architecture (SIH26074)

## 1. Problem Statement
In SIH26074, official weather forecasts from IMD are provided at the **Block level** (coarse 25–50 km grid). Agricultural operations (e.g. pesticide spraying, sowing, irrigation) require hyper-local weather information at the **Panchayat level** (3–8 km grid).

---

## 2. ML Directory Structure

```text
ml/
├── data/               # Ingestion from database into pandas DataFrames
│   ├── loader.py
│   └── README.md
├── preprocessing/      # Data cleaning, timestamp parsing, physical boundary checks
│   ├── cleaner.py
│   └── README.md
├── features/           # Spatial, elevation, and temporal feature extraction
│   ├── engineer.py
│   └── README.md
├── models/             # Baseline and Random Forest regression models
│   ├── baseline.py
│   ├── random_forest.py
│   └── README.md
├── evaluation/         # Validation against AWS/ARG observations (MAE & RMSE)
│   ├── metrics.py
│   └── README.md
├── predictions/        # End-to-end inference pipeline
│   ├── pipeline.py
│   └── README.md
└── README.md           # This document
```

---

## 3. Predictors & Target

### Input Features (Predictors):
- `block_forecast_rainfall_mm`: Official IMD forecast at the Block level.
- `panchayat_latitude`: Center latitude of the Panchayat.
- `panchayat_longitude`: Center longitude of the Panchayat.
- `elevation_m`: Elevation above sea level (ISRO-NRSC DEM).
- `station_distance_km`: Distance to nearest validation weather station.
- `lead_days`: Days between forecast generation and target date.
- `month`: Month of the year (1–12) to capture seasonal monsoon variation.
- `day_of_year`: Day of the year (1–366).

### Target:
- `actual_rainfall_mm`: Ground truth 24-hour rainfall measured by AWS/ARG.

---

## 4. Evaluation Strategy (from `brain.md`)

- **Baseline Benchmark**: `BlockPersistenceBaseline` (directly using the Block forecast as the Panchayat prediction).
- **Initial Model**: `RandomForestDownscaler` (Random Forest Regressor).
- **Metrics**: 
  - Mean Absolute Error (**MAE**)
  - Root Mean Squared Error (**RMSE**)
- **Validation Rule**: Models are strictly evaluated on held-out real observations. No claim of improvement is made without measured, recorded evidence.
