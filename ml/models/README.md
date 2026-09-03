# ML Models Layer

## Models Available
1. **`BlockPersistenceBaseline` (`baseline.py`)**:
   - Baseline benchmark that simply passes through the Block forecast without modification.
2. **`RandomForestDownscaler` (`random_forest.py`)**:
   - Random Forest Regressor trained on terrain, spatial coordinates, forecast lead time, and calendar features.
