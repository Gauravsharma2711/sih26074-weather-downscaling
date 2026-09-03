# SIH26074 — Weather Downscaling & Agro-Meteorological Advisory

> **Smart India Hackathon 2024 (SIH26074)**  
> **Problem Statement**: Downscaling of weather forecast from Block level to Panchayat level for agro-meteorological advisory services.  
> **Ministry**: Ministry of Earth Sciences (MoES)  
> **Department**: India Meteorological Department (IMD)  
> **Theme**: Agriculture, FoodTech & Rural Development  

---

## 🌾 1. Project Purpose & Central Problem

Official weather forecasts in India are published at the **Block level** (coarse 25–50 km grid). However, rainfall and micro-climates vary drastically across individual villages. 

**SIH26074** bridges this critical gap by downscaling Block-level weather forecasts to the **Panchayat level** (hyper-local 3–8 km resolution), converting predictions into actionable agro-meteorological advisories, submitting them for **Human Officer Approval**, and delivering verified guidance directly to farmers.

### 🔄 The End-to-End Pipeline
```text
Official Block Forecast (IMD)
          ↓
Local Panchayat Context (Elevation, Soil, Admin Boundaries)
          ↓
Machine Learning Downscaling Engine
          ↓
Hyper-local Panchayat Forecast
          ↓
Actionable Agro-Meteorological Advisory
          ↓
Human Officer Review (Approve / Edit / Reject)
          ↓
Farmer Application (Flutter Mobile App)
```

---

## 🎯 2. Current Prototype Scope (Day 1)

* **Pilot Region Focus**: Pilot district with representative blocks and Panchayats.
* **Target ML Variable**: Next-day 24-hour Panchayat rainfall accumulation (`actual_rainfall_mm`).
* **Baseline Benchmark**: Direct Block forecast persistence (`BlockPersistenceBaseline`).
* **Evaluation Standard**: Strictly benchmarked against held-out ground truth observations from IMD Automatic Weather Stations (AWS) and Automatic Rain Gauges (ARG) using MAE and RMSE.
* **Advisory Integrity**: Human-in-the-loop verification — no unapproved automated advice is delivered to farmers.
* **Data Integrity**: Never invent official data; never present synthetic data as official.

---

## 🛠️ 3. Technology Stack

* **Backend API**: Python 3.10+, FastAPI, SQLAlchemy ORM, Uvicorn
* **Database**: PostgreSQL (hosted on Supabase)
* **Machine Learning**: Python, Scikit-Learn (Random Forest Regressor), Pandas, NumPy
* **Mobile Delivery**: Flutter (cross-platform Android & iOS)
* **Officer Portal**: React Web Dashboard
* **Design System**: Universal Farmer Product Design System (nature-led palette, Inter typography, 4px grid)

---

## 📁 4. Current Project Structure

```text
sih26074-weather-downscaling/
├── backend/                  # FastAPI Python backend application
│   ├── app/
│   │   ├── api/v1/          # Version 1 API routers & endpoints
│   │   │   ├── endpoints/
│   │   │   │   └── health.py # /health & /health/db routes
│   │   │   └── router.py
│   │   ├── core/            # App configuration & SQLAlchemy database engine
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/          # Database models (PanchayatWeatherData, DownscaledForecast)
│   │   │   ├── panchayat_weather.py
│   │   │   └── downscaled_forecast.py
│   │   └── main.py          # Application entry point & CORS configuration
│   └── requirements.txt     # Python backend dependencies
├── data_pipeline/           # Data ingestion specs (IMD, LGD, DEM, Soil)
│   └── README.md
├── ml/                      # Machine learning architecture
│   ├── data/                # Data loader using SQLAlchemy sessions
│   ├── preprocessing/       # Data cleaning and physical validation
│   ├── features/            # Feature extraction (terrain, lead days, calendar)
│   ├── models/              # Baseline and Random Forest Regressor wrappers
│   ├── evaluation/          # Validation metrics (MAE, RMSE) & benchmark comparison
│   ├── predictions/         # End-to-end inference pipeline
│   └── README.md
├── advisory/                # Agro-meteorological advisory rule engine specs
│   └── README.md
├── farmer_app/              # Flutter mobile app specs & design guidelines
│   └── README.md
├── officer_dashboard/       # React officer approval dashboard specs
│   └── README.md
├── database/                # PostgreSQL schema definitions & documentation
│   └── README.md
├── tests/                   # Pytest automated test suite
│   ├── test_health.py       # API and database connectivity tests
│   └── test_ml.py           # Feature engineering & ML pipeline unit tests
├── docs/                    # Architecture diagrams and specifications
│   └── architecture.md
├── brain.md                 # Single source of truth for project rules & scope
├── README.md                # This project guide
├── .env.example             # Safe environment variable template
└── .gitignore               # Version control exclusion rules
```

---

## 🗄️ 5. Supabase Database Setup

The prototype connects to a managed **PostgreSQL database on Supabase**.

### Core Tables:
1. **`panchayat_weather_data`**: Stores historical/current Panchayat weather observations, official Block forecasts, GIS coordinates, elevation, station proximity, and ground truth readings.
2. **`downscaled_forecasts`**: Stores ML downscaled predictions, model versions, confidence scores, and comparison values.

### Safety Guarantee:
* Credentials and connection URLs are loaded dynamically from `.env` via `pydantic-settings`.
* Secrets are **never hardcoded** in source files.

---

## ⚙️ 6. Environment Variables Required

Create a `.env` file in the root directory by copying the example:

```bash
# Windows PowerShell:
Copy-Item .env.example .env

# Linux / macOS:
cp .env.example .env
```

### Configuration Keys:
```env
# Application Settings
PROJECT_NAME="SIH26074 Weather Downscaling"
ENVIRONMENT="development"
DEBUG=True
API_V1_STR="/api/v1"

# Server Host & Port
SERVER_HOST="0.0.0.0"
SERVER_PORT=8000

# PostgreSQL / Supabase Connection URL
DATABASE_URL="postgresql://<username>:<password>@<host>:<port>/<dbname>"

# CORS Allowed Origins
CORS_ORIGINS="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
```

---

## 🚀 7. How to Run the Backend

### Step 1: Set Up Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Run the FastAPI Server
```bash
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Verify Live Endpoints
* **API Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status": "ok"}`
* **Database Health Check**: [http://127.0.0.1:8000/health/db](http://127.0.0.1:8000/health/db) → Live connection & table diagnostics
* **Interactive API Documentation**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)

---

## 🧪 8. Running Automated Tests

Run the complete test suite with `pytest`:
```bash
python -m pytest tests/
```

All tests verify health routes, database connectivity, and ML pipeline components.
