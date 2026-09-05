# Machine Learning Downscaling Architecture (SIH26074)

## 1. Problem Statement
In SIH26074, weather forecasts from the India Meteorological Department (IMD) are issued at the **Block level** (coarse 25–50 km grid). Agricultural operations (e.g. crop spraying, sowing, irrigation) require micro-level weather advisory services at the **Panchayat level** (3–8 km grid).

---

## 2. ML Directory Structure

```text
ml/
├── train.py            # Model training pipeline (Random Forest Regressor)
├── predict.py          # Downscaling inference and post-processing
├── evaluate.py         # Ground-truth evaluation against IMD baseline
├── preprocessing.py    # Feature extraction, metadata isolation, data preparation
├── models/             # Serialized trained model artifacts (.joblib)
├── validation/         # Validation reports, error metrics, benchmark comparisons
└── README.md           # Architecture documentation
```

---

## 3. Predictors & Target Specification

### Target Variable (1):
* **`actual_rainfall_mm`**: 24-hour ground-truth rainfall observation measured by AWS/ARG stations (mm).

### Input Features (8 Continuous / Discrete Predictors):
1. **`block_forecast_rainfall_mm`**: Official IMD forecast at the Block level (mm).
2. **`panchayat_latitude`**: Center latitude of the target Panchayat (degrees North).
3. **`panchayat_longitude`**: Center longitude of the target Panchayat (degrees East).
4. **`elevation_m`**: Elevation above sea level derived from Digital Elevation Model (m).
5. **`station_distance_km`**: Geospatial Haversine distance to nearest AWS/ARG station (km).
6. **`lead_days`**: Forecast lead time in days ($0, 1, \dots, 5$).
7. **`month`**: Month of the forecast ($1–12$) to capture seasonal monsoon variation.
8. **`day_of_year`**: Julian day of the year ($1–366$).

### Non-Feature Metadata Fields (Strictly Excluded from Numerical ML Features):
* `panchayat_id`
* `lgd_code`
* `panchayat_name`
* `block_name`
* `district_name`
* `station_id`
* `date`
* `forecast_issue_date`

---

## 4. Model Architecture & Evaluation Criteria

* **Baseline Benchmark**: `BlockPersistenceBaseline` (IMD Block forecast treated as Panchayat prediction: MAE = `4.3651 mm`, RMSE = `5.5919 mm`).
* **Initial Model**: `RandomForestRegressor` (Ensemble tree regression with geospatial, orographic, and temporal conditioning).
* **Validation Strategy**: Strict 80/20 chronological train/test split on Nashik dataset (`1,110` train rows / `278` test rows, zero temporal lookahead leakage).
* **Metrics**: Mean Absolute Error (**MAE**), Root Mean Squared Error (**RMSE**), Pearson Correlation (**$r$**), Coefficient of Determination (**$R^2$**).
