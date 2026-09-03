# Data Pipeline Module

## Overview
The `data_pipeline` module is responsible for ingesting, validating, and preprocessing multi-source geospatial and meteorological data required for the downscaling engine.

## Responsibilities
1. **Weather Forecast Ingestion**: Fetch official Block-level forecasts from IMD / BharatFS.
2. **Ground Truth Observations**: Ingest actual rainfall and temperature data from IMD AWS (Automatic Weather Stations) and ARG (Automatic Rain Gauges) for validation.
3. **Panchayat Administrative Boundaries**: Process Local Government Directory (LGD) codes and administrative GIS polygons (Ministry of Panchayati Raj / e-GramSwaraj).
4. **Topography & Elevation**: Ingest digital elevation models (DEM), slope, and aspect data from ISRO-NRSC Bhuvan.
5. **Soil Features**: Ingest soil texture, moisture capacity, and type from ICAR / Soil Health Card datasets.

## Pipeline Architecture
```text
[Official IMD Block Forecast] ──┐
[IMD AWS/ARG Observations]   ──┼─► [Data Ingestion & Cleaning] ─► [Feature Engineering] ─► [Processed Dataset]
[ISRO Bhuvan DEM / Terrain]  ──┤
[ICAR Soil & LGD Metadata]   ──┘
```

## Rules (from brain.md)
- Never invent official data or present synthetic data as official.
- Ensure strict timestamp synchronization across historical datasets to avoid future data leakage.
