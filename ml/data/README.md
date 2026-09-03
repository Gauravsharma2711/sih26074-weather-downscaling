# ML Data Layer

## Purpose
The `ml/data/` module handles reading official dataset records from PostgreSQL (Supabase) via SQLAlchemy into structured pandas DataFrames without hardcoding queries or credentials.

## Files
- `loader.py`: Connects via `SessionLocal` to fetch `panchayat_weather_data` records.
