# ML Models Directory: Frozen V1 Downscaling Model

This directory contains trained model artifacts, fitted preprocessing pipelines, and configuration specifications for the micro-level weather downscaling system in Nashik District (Maharashtra).

---

## 1. Model Overview

* **Frozen Best V1 Model**: `ml/models/best_model.joblib` (XGBoost Regressor)
* **Fitted Preprocessor**: `ml/models/best_model_preprocessor.joblib` (`WeatherDataPreprocessor`)
* **Configuration Specification**: `ml/models/best_model_config.json`
* **Version**: `v1.0.0`

### What the Model Predicts
The model predicts **daily micro-level rainfall (`predicted_rainfall_mm`)** at individual Gram Panchayat village centroids by downscaling regional numerical block weather forecasts issued by IMD.

---

## 2. Model Input & Target Specifications

### Input Features (`feature_list`):
1. `block_forecast_rainfall_mm` — IMD regional numerical weather forecast for the encompassing block (mm).
2. `panchayat_latitude` — Gram Panchayat centroid latitude (WGS84 decimal degrees).
3. `panchayat_longitude` — Gram Panchayat centroid longitude (WGS84 decimal degrees).
4. `elevation_m` — Terrain elevation above mean sea level extracted from SRTM digital elevation model (meters).
5. `station_distance_km` — Euclidean distance to the nearest operational Automatic Weather Station (km).
6. `lead_days` — Forecast issue lead time in days (`0` = day-of forecast).
7. `month` — Calendar month of the forecast valid date (`1` to `12`).
8. `day_of_year` — Day of year for seasonal solar/monsoon cyclicity (`1` to `366`).

### Target Variable:
* `actual_rainfall_mm` — Daily ground-truth rainfall observation recorded at the nearest ground station / rain gauge.

---

## 3. Training & Evaluation Periods

* **Training Period**: `2026-01-09` to `2026-05-09` (`1,110` historical records)
* **Held-Out Evaluation Period**: `2026-05-09` to `2026-09-04` (`278` held-out test records)
* **Temporal Partitioning**: Strict chronological time-series split with zero future lookahead leakage.

---

## 4. Benchmark Performance & Selection Rationale

### Held-Out Test Set Performance (`278` records):

| Model Candidate | Test MAE (mm) | Test RMSE (mm) | MAE vs Baseline (%) | RMSE vs Baseline (%) | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **IMD Block Forecast (Baseline)** | **`5.4165`** | **`6.6747`** | — | — | Benchmark Baseline |
| **XGBoost Regressor** | **`5.5599`** | `8.7720` | **`-2.65%`** | `-31.42%` | **Selected Best ML Model (V1)** |
| **Random Forest Regressor** | `5.9482` | `8.7379` | `-9.82%` | `-30.91%` | Alternate ML Candidate |

### Selection Rationale:
1. **Lowest ML Test MAE**: XGBoost achieved lower Mean Absolute Error (`5.5599 mm`) compared to Random Forest (`5.9482 mm`).
2. **Local Orographic Downscaling Skill**: In complex terrain and high-elevation Western Ghats blocks (Dindori, Surgana, Baglan), the model demonstrated substantial accuracy gains over the raw regional block forecast ($> +40\text{ to } +54\%$ MAE improvement).
3. **Reproducibility & Stability**: Deterministic preprocessing imputation and fixed random seeds (`random_state = 42`) ensure consistent predictions across server restarts.

---

## 5. Diagnostic Notice & Production Readiness Disclaimer

> [!WARNING]
> **NOT PRODUCTION READY (Baseline V1 Candidate)**
>
> On the aggregate district-wide test set, **the raw IMD Block Forecast maintains lower MAE (`5.4165 mm` vs `5.5599 mm`) and RMSE (`6.6747 mm` vs `8.7720 mm`)** than the V1 ML model.
>
> Although the ML model improves local accuracy in high-elevation blocks, unmodeled precipitation extremes and local convective variance in eastern plateau blocks (e.g. Chandwad, Yeola) degrade overall aggregate performance.
> 
> **Do not deploy this V1 model as an autonomous operational advisory service** without further enhancements such as:
> - Dynamic atmospheric predictors (relative humidity, wind speed/direction, convective available potential energy).
> - Block-stratified local error bias corrections.
> - Probabilistic quantile regression for extreme rainfall threshold management.
