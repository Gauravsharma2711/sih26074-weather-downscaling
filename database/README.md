# Database Schema & Migrations

## Overview
This directory contains the database design, schema definitions, and migration scripts for the PostgreSQL database.

## Core Entities
1. **Administrative Entities**:
   - `districts`: District details and LGD code.
   - `blocks`: Block details and parent district.
   - `panchayats`: Panchayat boundary geometries, coordinates, elevation, soil type, and LGD codes.
2. **Weather Data Entities**:
   - `block_forecasts`: Raw weather forecasts from IMD.
   - `panchayat_forecasts`: Downscaled hyper-local forecasts produced by the ML pipeline.
   - `ground_truth_observations`: Real historical AWS / ARG readings for model training and validation.
3. **Advisory Entities**:
   - `advisories`: Generated advisories, action text, reason, confidence, status, and officer audit metadata.
4. **Users & Officers**:
   - `officers`: Authentication and role metadata for agricultural officers.

## Connection
Configuration is managed via the `DATABASE_URL` environment variable:
```bash
postgresql://<user>:<password>@<host>:<port>/<dbname>
```
