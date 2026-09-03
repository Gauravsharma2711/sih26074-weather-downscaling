# SIH26074 — BRAIN.md

## Purpose
Permanent project context for Antigravity. Read this file before major changes. Do not change the central problem, architecture, scope, or design system without team approval.

## Central Problem
SIH26074: Downscaling weather forecast from Block level to Panchayat level for agro-meteorological advisory services.

Organization: Ministry of Earth Sciences (MoES)
Department: India Meteorological Department
Theme: Agriculture, FoodTech & Rural Development

## Central Pipeline
Official Block-level forecast
→ local Panchayat information
→ ML downscaling
→ Panchayat-level forecast
→ agricultural advisory
→ human officer approval
→ farmer

### Golden Rule
A feature is useful only if it:
1. Improves local forecast accuracy.
2. Makes the forecast more useful as agricultural advice.
3. Makes advice easier for farmers to receive and use.

Otherwise, do not prioritize it.

## V1 Scope
- Pilot one district, 1–3 blocks, roughly 20–100 Panchayats.
- First ML target: next-day Panchayat rainfall.
- Baseline: original Block forecast treated as Panchayat forecast.
- Metrics: MAE and RMSE.
- Validate against held-out real observations.
- Advisory starts as transparent rules.
- Officer must approve/edit/reject before final farmer delivery.

## Data Sources
- Weather forecast: IMD / BharatFS / official IMD forecast products.
- Ground truth: IMD AWS / ARG.
- Panchayat identity/boundaries: Ministry of Panchayati Raj / LGD / e-GramSwaraj ecosystem.
- Elevation/terrain: Bhuvan / ISRO-NRSC.
- Soil: Soil Health Card / relevant ICAR soil datasets.
- Advisory context: IMD Agromet / GKMS material.

Never invent official data. Never present synthetic data as official.

## Technology Stack
- Coding: Antigravity
- Backend: Python + FastAPI
- Database: PostgreSQL
- ML: Python + Random Forest first; XGBoost later if useful
- Farmer app: Flutter
- Officer dashboard: React
- Cloud: Prefer one simple deployment path. GCP Cloud Run + managed PostgreSQL is the preferred V1 path. AWS may be used if required, but avoid duplicate infrastructure.

## Repository
```text
sih26074-weather-downscaling/
├── backend/
├── data_pipeline/
├── ml/
├── advisory/
├── farmer_app/
├── officer_dashboard/
├── database/
├── tests/
├── docs/
├── brain.md
├── README.md
├── .env.example
├── .gitignore
└── docker-compose.yml
```

## ML Rules
Inputs may include Block forecast, historical weather/rainfall, Panchayat coordinates, elevation/terrain, and reliable soil features.
Target: next-day Panchayat rainfall.
Always compare:
- Baseline = Block forecast
- Model = downscaled Panchayat forecast
against real held-out observations.
Do not claim improvement without measured evidence. Avoid future-data leakage.

## Advisory Rules
The ML model predicts weather. The advisory engine converts weather into action.
Start with transparent rainfall-driven rules such as:
- high rain → do not spray
- heavy rain → delay fertilizer/field operation
- low rain + dry conditions → irrigation may be required

Every advisory should include action, reason, relevant forecast values, confidence, and status.

## Human Approval
Flow:
ML prediction → advisory → officer dashboard → Approve/Edit/Reject → farmer.
Only approved advice appears as final farmer advice.

## Design System — Mandatory
The supplied Universal Farmer Product Design System is the shared visual language for Flutter and React. Both should feel like two surfaces of one agricultural operating environment. The system is calm, optimistic, nature-led, contemporary, practical, and readable.

### Design principles
- Nature-led, not rustic.
- Green means action and growth.
- Softness reduces cognitive load.
- Data is glanceable.
- Images carry agricultural context.
- Mobile and desktop use the same visual vocabulary with different density.

### Color tokens
```text
primary.700  #056B43
primary.600  #087A4B
primary.500  #0A8A57
primary.100  #DDF3E8
primary.050  #EFFAF4
canvas       #F3F4F2
surface      #FFFFFF
surface.subtle #F8F9F7
ink.900      #1E2823
ink.700      #425149
ink.500      #77847C
ink.300      #C9D1CC
warning.600  #C78318
warning.100  #FFF1CF
danger.600   #C94B43
danger.100   #FDE8E6
info.600     #3D78A6
sun.500      #F6C744
```

Green is for primary actions, active states, positive status, progress, and brand identity. Status meaning must never depend on color alone.

### Typography
Use Inter where available.
```text
Display metric  32 / 700
Page title      24 / 700
Section title   18 / 700
Card title      16 / 650
Body            14 / 400
Label           12 / 600
Caption         11 / 400
Button          14 / 650
```

### Spacing and shape
Use a 4 px base grid:
4, 8, 12, 16, 20, 24, 32, 40 px.

Radii:
```text
small       10 px
medium      14 px
large       20 px
extra-large 28 px
pill        999 px
```

Use white rounded cards, generous whitespace, subtle elevation, and low-contrast borders.

### Iconography and imagery
Use friendly rounded line icons with roughly 1.75–2 px stroke. Use crop, field, weather, produce, and farm-activity imagery only. Avoid unrelated stock imagery.

### Flutter
Use a single ThemeData source of truth. Core concepts:
```text
FarmerScaffold
AppCard
MetricTile
WeatherHeroCard
FarmListTile
PrimaryPillButton
SectionHeader
StatusChip
PrimaryNavigation
```
Mobile: single-column flow, bottom navigation, 16–20 px page padding, 44–48 px minimum touch targets.

### React
Use a responsive shell. Desktop can use a sidebar/navigation rail, 24–32 px gutters, KPI cards, forecast panels, advisory review panels, and rounded tables. Maximum content width around 1440 px.

Core concepts:
```text
AppShell
AppCard
MetricCard
WeatherHeroCard
FarmListItem
PrimaryButton
SectionHeader
StatusChip
PrimaryNav
```

### Responsive rule
Change layout, not brand. Mobile uses bottom navigation and one-column cards. Desktop uses sidebar and responsive grids. Keep colors, typography, radii, icons, labels, and hierarchy consistent.

## Antigravity Rules
1. Read brain.md before major implementation.
2. For large tasks, plan first.
3. Make small, testable changes.
4. Run tests after changes.
5. Explain changes in beginner-friendly language.
6. Never invent APIs or government data.
7. Never hard-code secrets.
8. Create/use .env and .env.example correctly.
9. Do not change scope without asking.
10. Preserve the design system.
11. Preserve the SIH26074 central problem.
12. Do not build unnecessary features before the core pipeline works.
13. Avoid destructive commands unless explicitly approved.

## Security
Never commit .env, API keys, database passwords, cloud credentials, or private tokens. Use environment variables or a cloud secret manager.

## Seven-Day Context
Day 1: setup, Git, Antigravity, PostgreSQL, cloud foundation, design system, brain.md, frontend/backend skeleton.
Day 2: official data ingestion and clean dataset.
Day 3: baseline + first Random Forest model.
Day 4: model improvement + confidence + API/dashboard.
Day 5: advisory engine + human approval.
Day 6: full integration + farmer app.
Day 7: testing, evidence, demo hardening, rehearsal.

## Day 1 Definition of Done
- Git repository exists.
- Antigravity project exists.
- brain.md is committed.
- Design tokens are implemented or documented for both apps.
- Flutter shell runs.
- React shell runs.
- FastAPI starts and /health works.
- PostgreSQL connects.
- .env.example exists and .env is ignored.
- ML structure exists.
- Pilot region is selected.
- Official data sources are documented and access is tested.
- No fake accuracy numbers exist.

## Final Principle
This is not a generic farmer weather app.

The central innovation is:
Block-level weather → Panchayat-level downscaling → actionable agro-advisory.

The app is the delivery layer. The model and validation are the technical proof. Human approval makes the advisory operationally responsible.
