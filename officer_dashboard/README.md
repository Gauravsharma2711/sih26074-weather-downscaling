# Officer Dashboard (React)

## Overview
The `officer_dashboard` is a web portal built with **React**, designed for Block and District Agricultural Officers and Subject Matter Specialists (SMS) to review, edit, approve, or reject machine-generated advisories.

## Key Features
1. **Panchayat Overview Map & Grid**: Visual inspection of downscaled rainfall across all Panchayats in the Block.
2. **Advisory Review Queue**: Filter advisories by status (`pending_review`, `approved`, `modified`, `rejected`).
3. **Approval Workspace**:
   - Inspect ML forecast metrics and feature anomalies.
   - 1-click **Approve**, inline **Edit**, or **Reject** with remarks.
4. **Historical Audit Log**: Complete trace of which officer approved/edited each advisory.

## Design System Compliance
The dashboard shares the **Universal Farmer Product Design System** with the mobile app:
- Max content width: ~1440px.
- Sidebar / navigation rail with 24–32px gutters.
- Rounded white cards with subtle elevations and low-contrast borders.
- Components: `AppShell`, `MetricCard`, `WeatherHeroCard`, `FarmListItem`, `PrimaryButton`, `StatusChip`.
