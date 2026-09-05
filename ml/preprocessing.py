import os
import logging
from typing import Tuple, List, Optional, Dict, Any, Union
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

# Strictly defined ML Feature columns (8 numerical predictors)
FEATURE_COLUMNS: List[str] = [
    "block_forecast_rainfall_mm",
    "panchayat_latitude",
    "panchayat_longitude",
    "elevation_m",
    "station_distance_km",
    "lead_days",
    "month",
    "day_of_year",
]

# Target column (1 continuous variable in mm)
TARGET_COLUMN: str = "actual_rainfall_mm"

# Metadata columns (strictly excluded from numerical ML features)
METADATA_COLUMNS: List[str] = [
    "panchayat_id",
    "lgd_code",
    "panchayat_name",
    "block_name",
    "district_name",
    "station_id",
    "date",
    "forecast_issue_date",
]


class WeatherDataPreprocessor:
    """
    Reproducible preprocessing pipeline for Panchayat-level weather downscaling.
    
    Rules enforced:
    1. Imputes missing numerical feature values using median imputation.
    2. Imputation statistics (medians) are strictly learned from TRAINING data only.
    3. Test data is transformed using the fitted training statistics (zero leakage).
    4. Target variable 'actual_rainfall_mm' is NEVER imputed.
    5. Rows with missing target values are dropped for supervised training/evaluation.
    6. Non-feature metadata fields are isolated and never fed to ML models.
    """

    def __init__(self, feature_columns: Optional[List[str]] = None):
        self.feature_columns = feature_columns or list(FEATURE_COLUMNS)
        self.imputer = SimpleImputer(strategy="median")
        self.is_fitted: bool = False
        self.medians_: Dict[str, float] = {}

    def fit(self, X_train: pd.DataFrame) -> "WeatherDataPreprocessor":
        """
        Fit the preprocessor on training feature matrix by computing feature medians.
        """
        missing_cols = [c for c in self.feature_columns if c not in X_train.columns]
        if missing_cols:
            raise ValueError(f"Missing feature columns in training data: {missing_cols}")

        X_num = X_train[self.feature_columns].copy()
        self.imputer.fit(X_num)
        self.medians_ = dict(zip(self.feature_columns, self.imputer.statistics_.tolist()))
        self.is_fitted = True
        logger.info(f"Fitted WeatherDataPreprocessor on {len(X_train)} training records.")
        logger.info(f"Learned feature medians: {self.medians_}")
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform feature matrix using learned training medians.
        """
        if not self.is_fitted:
            raise RuntimeError("WeatherDataPreprocessor must be fitted on training data before transforming.")

        missing_cols = [c for c in self.feature_columns if c not in X.columns]
        if missing_cols:
            raise ValueError(f"Missing feature columns in input data: {missing_cols}")

        X_num = X[self.feature_columns].copy()
        imputed_array = self.imputer.transform(X_num)
        
        # Preserve DataFrame structure, column names, and index
        imputed_df = pd.DataFrame(
            imputed_array,
            columns=self.feature_columns,
            index=X.index
        )
        return imputed_df

    def fit_transform(self, X_train: pd.DataFrame) -> pd.DataFrame:
        """
        Fit on training data and return transformed training feature matrix.
        """
        return self.fit(X_train).transform(X_train)


def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Load dataset from CSV file and ensure it exists.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8")
    return df


def prepare_training_features(
    df: pd.DataFrame,
    features: Optional[List[str]] = None,
    target: str = TARGET_COLUMN
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Extract feature matrix X, target vector y, and metadata DataFrame from a training dataset.
    Rows with missing target values are strictly excluded (never imputed).
    """
    feature_cols = features or FEATURE_COLUMNS

    missing_feats = [col for col in feature_cols if col not in df.columns]
    if missing_feats:
        raise ValueError(f"Missing required feature columns in dataset: {missing_feats}")

    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataset.")

    # Drop rows where target is missing (actual_rainfall_mm cannot be imputed)
    clean_df = df.dropna(subset=[target]).copy()

    meta_cols = [col for col in METADATA_COLUMNS if col in clean_df.columns]

    X = clean_df[feature_cols].copy()
    y = clean_df[target].copy()
    metadata = clean_df[meta_cols].copy()

    return X, y, metadata


def prepare_inference_features(
    df: pd.DataFrame,
    features: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract feature matrix X and metadata DataFrame for inference/prediction.
    """
    feature_cols = features or FEATURE_COLUMNS

    missing_feats = [col for col in feature_cols if col not in df.columns]
    if missing_feats:
        raise ValueError(f"Missing required feature columns for inference: {missing_feats}")

    meta_cols = [col for col in METADATA_COLUMNS if col in df.columns]

    X = df[feature_cols].copy()
    metadata = df[meta_cols].copy()

    return X, metadata


def get_train_test_data(
    train_path: str = "data/features/nashik_train.csv",
    test_path: str = "data/features/nashik_test.csv",
    features: Optional[List[str]] = None,
    target: str = TARGET_COLUMN
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Load train and test datasets, filter valid target rows, and apply reproducible median imputation.
    
    Imputation medians are learned STRICTLY from train data and applied to both train and test.
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    logger.info(f"Loading train dataset from: {train_path}")
    df_train = load_dataset(train_path)

    logger.info(f"Loading test dataset from: {test_path}")
    df_test = load_dataset(test_path)

    return preprocess_train_test_data(
        df_train=df_train,
        df_test=df_test,
        features=features,
        target=target
    )


def preprocess_train_test_data(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    features: Optional[List[str]] = None,
    target: str = TARGET_COLUMN
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Execute reproducible preprocessing on train and test DataFrames.
    
    1. Extracts raw X and y from train and test sets, dropping records where target is null.
    2. Fits WeatherDataPreprocessor (median imputer) ONLY on X_train.
    3. Imputes missing features in X_train using learned training medians.
    4. Imputes missing features in X_test using the SAME learned training medians.
    5. Returns (X_train, X_test, y_train, y_test).
    """
    feature_cols = features or FEATURE_COLUMNS

    # Extract raw matrices (drop rows where actual rainfall is missing)
    X_train_raw, y_train, _ = prepare_training_features(df_train, features=feature_cols, target=target)
    X_test_raw, y_test, _ = prepare_training_features(df_test, features=feature_cols, target=target)

    # Fit preprocessor on training data only
    preprocessor = WeatherDataPreprocessor(feature_columns=feature_cols)
    preprocessor.fit(X_train_raw)

    # Transform both sets with training-learned statistics
    X_train = preprocessor.transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    logger.info(
        f"Preprocessing complete: X_train={X_train.shape}, y_train={y_train.shape}, "
        f"X_test={X_test.shape}, y_test={y_test.shape}"
    )

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    X_tr, X_te, y_tr, y_te = get_train_test_data()
    print("\n--- Day 3 Preprocessing Verification ---")
    print(f"X_train shape: {X_tr.shape}")
    print(f"X_test shape:  {X_te.shape}")
    print(f"y_train shape: {y_tr.shape}")
    print(f"y_test shape:  {y_te.shape}")
    print(f"Features: {list(X_tr.columns)}")
    print(f"X_train missing values: {X_tr.isnull().sum().sum()}")
    print(f"X_test missing values:  {X_te.isnull().sum().sum()}")
