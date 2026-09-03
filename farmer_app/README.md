# Farmer Application (Flutter)

## Overview
The `farmer_app` is a cross-platform mobile application built with **Flutter**, designed specifically for farmers to view downscaled Panchayat weather forecasts and verified agro-meteorological advisories.

## Design System Compliance
The app strictly follows the **Universal Farmer Product Design System** specified in `brain.md`:
- **Theme & Colors**: Nature-led palette (`primary.700` `#056B43`, `primary.500` `#0A8A57`, `primary.050` `#EFFAF4`, `canvas` `#F3F4F2`, `surface` `#FFFFFF`, `sun` `#F6C744`, `ink.900` `#1E2823`).
- **Typography**: Inter / readable high-contrast scaling.
- **Components**:
  - `FarmerScaffold`
  - `AppCard`
  - `MetricTile`
  - `WeatherHeroCard`
  - `FarmListTile`
  - `PrimaryPillButton`
  - `SectionHeader`
  - `StatusChip`
- **Ergonomics**: Single-column layout, bottom navigation, 16–20px page padding, 44–48px minimum touch targets.

## Delivery Guarantee
Only advisories that have been approved or edited by an agricultural officer (`status: approved`) are displayed to the farmer.
