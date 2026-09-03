# ML Evaluation Layer

## Core Metrics
- **MAE (Mean Absolute Error)**: Average magnitude of rainfall forecast errors in mm.
- **RMSE (Root Mean Squared Error)**: Penalizes larger rainfall forecast deviations.

## Golden Rule (from brain.md)
Every downscaled model must be directly benchmarked against `BlockPersistenceBaseline` on held-out test data. We never claim model improvement without recorded evidence.
