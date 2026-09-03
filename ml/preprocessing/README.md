# ML Preprocessing Layer

## Purpose
The `ml/preprocessing/` module ensures that ingested data conforms to physical constraints (e.g. rainfall >= 0) and standard types before being fed into feature engineering.

## Responsibilities
- Convert date strings to datetime objects.
- Cast latitude, longitude, elevation, distance, and rainfall to floating-point numbers.
- Filter invalid records and remove temporal anomalies.
