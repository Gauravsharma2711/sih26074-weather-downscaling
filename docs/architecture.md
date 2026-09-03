# SIH26074 System Architecture

## 1. Problem Statement
**SIH26074**: Downscaling of weather forecasts from Block level to Panchayat level for agro-meteorological advisory services.
- **Organization**: Ministry of Earth Sciences (MoES)
- **Department**: India Meteorological Department (IMD)
- **Theme**: Agriculture, FoodTech & Rural Development

---

## 2. End-to-End System Pipeline
```text
┌────────────────────────────────────────────────────────┐
│               Official IMD Block Forecast               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│     Local Panchayat Geospatial Features Ingestion       │
│  (LGD Admin Boundaries + ISRO Bhuvan DEM + ICAR Soil)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           Machine Learning Downscaling Engine          │
│        (Baseline vs. Random Forest Regression)         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│         Hyper-local Panchayat Rainfall Forecast        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           Agro-Meteorological Advisory Engine          │
│            (IMD Agromet / GKMS Rule Matrix)            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Human Officer Review Dashboard             │
│            (React Web Portal — Approve/Edit)           │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Farmer Delivery                      │
│            (Flutter Mobile App / Alerts)               │
└────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL
- **Machine Learning**: Scikit-Learn (Random Forest), Pandas, NumPy
- **Farmer App**: Flutter (iOS & Android)
- **Officer Dashboard**: React (Vite / Next.js)
- **Design System**: Universal Farmer Product Design System (shared token palette and typography)
