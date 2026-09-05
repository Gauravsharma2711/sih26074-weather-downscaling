import os
import sys
import logging
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml.preprocessing import TARGET_COLUMN, FEATURE_COLUMNS, load_dataset
from ml.predict import DEFAULT_OUTPUT_PREDICTIONS_PATH, load_trained_model, DEFAULT_MODEL_PATH

logger = logging.getLogger(__name__)

DEFAULT_VALIDATION_DIR = "ml/validation"
DEFAULT_METRICS_PATH = os.path.join(DEFAULT_VALIDATION_DIR, "model_metrics.csv")
DEFAULT_COMPARISON_PATH = os.path.join(DEFAULT_VALIDATION_DIR, "model_comparison.csv")
DEFAULT_FEATURE_IMPORTANCE_CSV = os.path.join(DEFAULT_VALIDATION_DIR, "feature_importance.csv")
DEFAULT_FEATURE_IMPORTANCE_PNG = os.path.join(DEFAULT_VALIDATION_DIR, "feature_importance.png")
DEFAULT_BLOCK_PERFORMANCE_CSV = os.path.join(DEFAULT_VALIDATION_DIR, "block_performance.csv")




def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Calculate regression evaluation metrics: MAE, RMSE, Pearson r, R2 score.
    """
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    
    # Pearson Correlation Coefficient
    if np.std(y_true) > 0 and np.std(y_pred) > 0:
        pearson_r = float(np.corrcoef(y_true, y_pred)[0, 1])
    else:
        pearson_r = 0.0
        
    return {
        "mae_mm": round(mae, 4),
        "rmse_mm": round(rmse, 4),
        "r2_score": round(r2, 4),
        "pearson_r": round(pearson_r, 4),
    }


def compute_segment_metrics(
    group_df: pd.DataFrame,
    dimension: str,
    segment_value: Any
) -> Dict[str, Any]:
    """
    Compute comparative metrics between baseline forecast and ML model for a data slice.
    """
    y_true = group_df["actual_rainfall_mm"].values
    y_base = group_df["block_forecast_rainfall_mm"].values
    y_pred = group_df["predicted_rainfall_mm"].values
    n = len(group_df)
    
    b_mae = float(np.mean(np.abs(y_base - y_true)))
    b_rmse = float(np.sqrt(np.mean((y_base - y_true) ** 2)))
    
    m_mae = float(np.mean(np.abs(y_pred - y_true)))
    m_rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))
    
    mae_imp = round(((b_mae - m_mae) / b_mae) * 100.0, 2) if b_mae > 0 else 0.0
    rmse_imp = round(((b_rmse - m_rmse) / b_rmse) * 100.0, 2) if b_rmse > 0 else 0.0
    
    return {
        "dimension": dimension,
        "segment": str(segment_value),
        "sample_count": n,
        "baseline_mae": round(b_mae, 4),
        "baseline_rmse": round(b_rmse, 4),
        "model_mae": round(m_mae, 4),
        "model_rmse": round(m_rmse, 4),
        "mae_improvement_pct": mae_imp,
        "rmse_improvement_pct": rmse_imp
    }


def evaluate_random_forest(
    predictions_path: str = DEFAULT_OUTPUT_PREDICTIONS_PATH,
    output_metrics_path: str = DEFAULT_METRICS_PATH,
    output_comparison_path: str = DEFAULT_COMPARISON_PATH
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Evaluate Random Forest predictions against baseline forecast across:
    1. overall
    2. lead_days
    3. block
    4. month
    
    Creates:
    - ml/validation/model_metrics.csv
    - ml/validation/model_comparison.csv
    """
    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions file not found at {predictions_path}. Run ml/predict.py first.")
        
    df = pd.read_csv(predictions_path)
    
    # Ensure month is present
    if "month" not in df.columns:
        df["month"] = pd.to_datetime(df["date"]).dt.month
        
    comparison_records: List[Dict[str, Any]] = []
    metrics_records: List[Dict[str, Any]] = []
    
    # 1. Overall
    comp_overall = compute_segment_metrics(df, "overall", "all")
    comparison_records.append(comp_overall)
    
    base_m = compute_regression_metrics(df["actual_rainfall_mm"].values, df["block_forecast_rainfall_mm"].values)
    rf_m = compute_regression_metrics(df["actual_rainfall_mm"].values, df["predicted_rainfall_mm"].values)
    
    metrics_records.append({
        "model_name": "IMD Block Baseline",
        "dimension": "overall",
        "segment": "all",
        "sample_count": len(df),
        **base_m
    })
    metrics_records.append({
        "model_name": "Random Forest Regressor",
        "dimension": "overall",
        "segment": "all",
        "sample_count": len(df),
        **rf_m
    })
    
    # 2. Breakdown by lead_days
    for ld in sorted(df["lead_days"].unique()):
        sub_df = df[df["lead_days"] == ld]
        comparison_records.append(compute_segment_metrics(sub_df, "lead_days", ld))
        
        m_base = compute_regression_metrics(sub_df["actual_rainfall_mm"].values, sub_df["block_forecast_rainfall_mm"].values)
        m_rf = compute_regression_metrics(sub_df["actual_rainfall_mm"].values, sub_df["predicted_rainfall_mm"].values)
        metrics_records.append({"model_name": "IMD Block Baseline", "dimension": "lead_days", "segment": str(ld), "sample_count": len(sub_df), **m_base})
        metrics_records.append({"model_name": "Random Forest Regressor", "dimension": "lead_days", "segment": str(ld), "sample_count": len(sub_df), **m_rf})

    # 3. Breakdown by block
    for blk in sorted(df["block_name"].unique()):
        sub_df = df[df["block_name"] == blk]
        comparison_records.append(compute_segment_metrics(sub_df, "block", blk))
        
        m_base = compute_regression_metrics(sub_df["actual_rainfall_mm"].values, sub_df["block_forecast_rainfall_mm"].values)
        m_rf = compute_regression_metrics(sub_df["actual_rainfall_mm"].values, sub_df["predicted_rainfall_mm"].values)
        metrics_records.append({"model_name": "IMD Block Baseline", "dimension": "block", "segment": str(blk), "sample_count": len(sub_df), **m_base})
        metrics_records.append({"model_name": "Random Forest Regressor", "dimension": "block", "segment": str(blk), "sample_count": len(sub_df), **m_rf})

    # 4. Breakdown by month
    for m in sorted(df["month"].unique()):
        sub_df = df[df["month"] == m]
        comparison_records.append(compute_segment_metrics(sub_df, "month", m))
        
        m_base = compute_regression_metrics(sub_df["actual_rainfall_mm"].values, sub_df["block_forecast_rainfall_mm"].values)
        m_rf = compute_regression_metrics(sub_df["actual_rainfall_mm"].values, sub_df["predicted_rainfall_mm"].values)
        metrics_records.append({"model_name": "IMD Block Baseline", "dimension": "month", "segment": str(m), "sample_count": len(sub_df), **m_base})
        metrics_records.append({"model_name": "Random Forest Regressor", "dimension": "month", "segment": str(m), "sample_count": len(sub_df), **m_rf})

    # Convert to DataFrames
    df_metrics = pd.DataFrame(metrics_records)
    df_comparison = pd.DataFrame(comparison_records)
    
    # Save CSVs
    os.makedirs(os.path.dirname(output_metrics_path), exist_ok=True)
    os.makedirs(os.path.dirname(output_comparison_path), exist_ok=True)
    
    df_metrics.to_csv(output_metrics_path, index=False, encoding="utf-8")
    df_comparison.to_csv(output_comparison_path, index=False, encoding="utf-8")
    
    summary_results = {
        "baseline_mae": comp_overall["baseline_mae"],
        "model_mae": comp_overall["model_mae"],
        "baseline_rmse": comp_overall["baseline_rmse"],
        "model_rmse": comp_overall["model_rmse"],
        "mae_improvement_pct": comp_overall["mae_improvement_pct"],
        "rmse_improvement_pct": comp_overall["rmse_improvement_pct"],
        "test_samples": len(df)
    }
    
    return df_metrics, df_comparison, summary_results


DEFAULT_DIAGNOSTICS_PATH = os.path.join(DEFAULT_VALIDATION_DIR, "prediction_diagnostics.csv")


def check_predictions_sanity(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform sanity check on model predictions:
    - negative predictions (< 0)
    - extremely large predictions (> 200 mm)
    - NaN predictions
    - infinite predictions
    - missing predictions
    - verify predicted_rainfall_mm == max(raw_predicted_rainfall_mm, 0)
    """
    raw_col = "raw_predicted_rainfall_mm" if "raw_predicted_rainfall_mm" in df.columns else "predicted_rainfall_mm"
    raw_preds = df[raw_col].values
    clipped_preds = df["predicted_rainfall_mm"].values
    
    neg_count = int(np.sum(raw_preds < 0))
    zero_count = int(np.sum(raw_preds == 0))
    large_count = int(np.sum(raw_preds > 200.0))
    nan_count = int(np.sum(np.isnan(raw_preds)))
    inf_count = int(np.sum(np.isinf(raw_preds)))
    missing_count = int(df["predicted_rainfall_mm"].isnull().sum())
    
    # Check clipping contract
    expected_clipped = np.clip(raw_preds, a_min=0.0, a_max=None)
    clipping_valid = bool(np.allclose(clipped_preds, expected_clipped, atol=1e-4))
    
    return {
        "total_records": len(df),
        "raw_min_mm": round(float(np.min(raw_preds)), 4),
        "raw_max_mm": round(float(np.max(raw_preds)), 4),
        "raw_mean_mm": round(float(np.mean(raw_preds)), 4),
        "negative_predictions_before_clipping": neg_count,
        "zero_predictions": zero_count,
        "extremely_large_predictions_gt_200mm": large_count,
        "nan_predictions": nan_count,
        "infinite_predictions": inf_count,
        "missing_predictions": missing_count,
        "clipping_contract_valid": clipping_valid
    }


def generate_prediction_diagnostics(

    predictions_path: str = DEFAULT_OUTPUT_PREDICTIONS_PATH,
    output_diagnostics_path: str = DEFAULT_DIAGNOSTICS_PATH,
    random_state: int = 42
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Generate diagnostic slices of model predictions:
    1. 20 random test predictions
    2. 10 best predictions
    3. 10 worst predictions
    4. Largest over-predictions (predicted > actual)
    5. Largest under-predictions (predicted < actual)
    
    Saves combined diagnostic report to ml/validation/prediction_diagnostics.csv.
    """
    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions file not found at {predictions_path}. Run ml/predict.py first.")
        
    df = pd.read_csv(predictions_path)
    
    cols = [
        "panchayat_name",
        "block_name",
        "date",
        "block_forecast_rainfall_mm",
        "predicted_rainfall_mm",
        "actual_rainfall_mm",
        "absolute_error"
    ]
    
    # 1. 20 random test predictions
    random_20 = df.sample(n=min(20, len(df)), random_state=random_state)[cols].copy()
    random_20.insert(0, "diagnostic_type", "random_sample")
    
    # 2. 10 best predictions (lowest absolute error)
    best_10 = df.sort_values(by="absolute_error", ascending=True).head(10)[cols].copy()
    best_10.insert(0, "diagnostic_type", "best_predictions")
    
    # 3. 10 worst predictions (highest absolute error)
    worst_10 = df.sort_values(by="absolute_error", ascending=False).head(10)[cols].copy()
    worst_10.insert(0, "diagnostic_type", "worst_predictions")
    
    # 4. Largest over-predictions (predicted > actual, sorted by prediction_error descending)
    if "prediction_error" not in df.columns:
        df["prediction_error"] = df["predicted_rainfall_mm"] - df["actual_rainfall_mm"]
    over_preds = df[df["prediction_error"] > 0].sort_values(by="prediction_error", ascending=False).head(10)[cols].copy()
    over_preds.insert(0, "diagnostic_type", "largest_over_predictions")
    
    # 5. Largest under-predictions (predicted < actual, sorted by prediction_error ascending)
    under_preds = df[df["prediction_error"] < 0].sort_values(by="prediction_error", ascending=True).head(10)[cols].copy()
    under_preds.insert(0, "diagnostic_type", "largest_under_predictions")
    
    combined_diag = pd.concat([random_20, best_10, worst_10, over_preds, under_preds], ignore_index=True)
    
    os.makedirs(os.path.dirname(output_diagnostics_path), exist_ok=True)
    combined_diag.to_csv(output_diagnostics_path, index=False, encoding="utf-8")
    logger.info(f"Saved prediction diagnostics to {output_diagnostics_path} ({len(combined_diag)} records)")
    
    slices = {
        "random_20": random_20,
        "best_10": best_10,
        "worst_10": worst_10,
        "largest_over": over_preds,
        "largest_under": under_preds
    }
    
    return combined_diag, slices


def export_feature_importance(
    model_path: str = DEFAULT_MODEL_PATH,
    output_csv_path: str = DEFAULT_FEATURE_IMPORTANCE_CSV,
    output_png_path: str = DEFAULT_FEATURE_IMPORTANCE_PNG,
    features: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Extract feature importances from trained Random Forest regressor,
    save ranked CSV (feature, importance, rank) and horizontal bar plot visualization.
    """
    if features is None:
        features = FEATURE_COLUMNS
        
    model, _ = load_trained_model(model_path)
    
    if not hasattr(model, "feature_importances_"):
        raise AttributeError(f"Model at {model_path} does not expose feature_importances_.")
        
    importances = model.feature_importances_
    
    df_imp = pd.DataFrame({
        "feature": features,
        "importance": np.round(importances, 6)
    }).sort_values(by="importance", ascending=False).reset_index(drop=True)
    
    df_imp["rank"] = range(1, len(df_imp) + 1)
    
    # Save CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_imp.to_csv(output_csv_path, index=False, encoding="utf-8")
    logger.info(f"Saved feature importance CSV to: {output_csv_path}")
    
    # Generate visualization
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6), dpi=300)
        # Plot in ascending order so top features appear at top of horizontal chart
        df_plot = df_imp.sort_values(by="importance", ascending=True)
        bars = plt.barh(df_plot["feature"], df_plot["importance"] * 100, color="#1f77b4", edgecolor="#0d47a1")
        
        plt.title("Random Forest Downscaling — Feature Importance Distribution", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Importance Share (%)", fontsize=12, fontweight="medium")
        plt.ylabel("Predictor Feature", fontsize=12, fontweight="medium")
        plt.xlim(0, max(df_plot["importance"] * 100) * 1.15)
        plt.grid(axis="x", linestyle="--", alpha=0.6)
        
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height() / 2, f"{width:.2f}%", ha="left", va="center", fontsize=10, fontweight="bold")
            
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
        plt.savefig(output_png_path, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved feature importance visualization to: {output_png_path}")
    except Exception as e:
        logger.warning(f"Could not generate feature importance plot: {e}")
        
    return df_imp


def compare_all_models(
    rf_predictions_path: str = DEFAULT_OUTPUT_PREDICTIONS_PATH,
    xgb_predictions_path: str = "ml/validation/xgboost_predictions.csv",
    output_comparison_path: str = DEFAULT_COMPARISON_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Compare:
    1. Original Block Forecast
    2. Random Forest
    3. XGBoost
    
    Using exactly the same test observations (278 records).
    Creates ml/validation/model_comparison.csv with columns:
    model, mae, rmse, mae_improvement_percent, rmse_improvement_percent
    """
    df_rf = pd.read_csv(rf_predictions_path)
    df_xgb = pd.read_csv(xgb_predictions_path)
    
    y_true = df_rf["actual_rainfall_mm"].values
    y_base = df_rf["block_forecast_rainfall_mm"].values
    y_rf = df_rf["predicted_rainfall_mm"].values
    y_xgb = df_xgb["predicted_rainfall_mm"].values
    
    b_mae = float(np.mean(np.abs(y_base - y_true)))
    b_rmse = float(np.sqrt(np.mean((y_base - y_true) ** 2)))
    
    rf_mae = float(np.mean(np.abs(y_rf - y_true)))
    rf_rmse = float(np.sqrt(np.mean((y_rf - y_true) ** 2)))
    
    xgb_mae = float(np.mean(np.abs(y_xgb - y_true)))
    xgb_rmse = float(np.sqrt(np.mean((y_xgb - y_true) ** 2)))
    
    rf_mae_imp = round(((b_mae - rf_mae) / b_mae) * 100.0, 2)
    rf_rmse_imp = round(((b_rmse - rf_rmse) / b_rmse) * 100.0, 2)
    
    xgb_mae_imp = round(((b_mae - xgb_mae) / b_mae) * 100.0, 2)
    xgb_rmse_imp = round(((b_rmse - xgb_rmse) / b_rmse) * 100.0, 2)
    
    records = [
        {
            "model": "Original Block Forecast",
            "mae": round(b_mae, 4),
            "rmse": round(b_rmse, 4),
            "mae_improvement_percent": 0.0,
            "rmse_improvement_percent": 0.0,
        },
        {
            "model": "Random Forest",
            "mae": round(rf_mae, 4),
            "rmse": round(rf_rmse, 4),
            "mae_improvement_percent": rf_mae_imp,
            "rmse_improvement_percent": rf_rmse_imp,
        },
        {
            "model": "XGBoost",
            "mae": round(xgb_mae, 4),
            "rmse": round(xgb_rmse, 4),
            "mae_improvement_percent": xgb_mae_imp,
            "rmse_improvement_percent": xgb_rmse_imp,
        }
    ]
    
    df_comp = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(output_comparison_path), exist_ok=True)
    df_comp.to_csv(output_comparison_path, index=False, encoding="utf-8")
    logger.info(f"Saved 3-model comparison to: {output_comparison_path}")
    
    # Recommendation logic
    ml_beats_baseline = (rf_mae < b_mae or xgb_mae < b_mae)
    
    if not ml_beats_baseline:
        verdict = "ML does not currently beat the baseline."
        recommended_model = "Original Block Forecast (IMD Baseline)"
    else:
        if xgb_mae <= rf_mae:
            recommended_model = "XGBoost"
        else:
            recommended_model = "Random Forest"
        verdict = f"Recommended V1 Model: {recommended_model}"
        
    summary = {
        "baseline_mae": round(b_mae, 4),
        "baseline_rmse": round(b_rmse, 4),
        "rf_mae": round(rf_mae, 4),
        "rf_rmse": round(rf_rmse, 4),
        "xgb_mae": round(xgb_mae, 4),
        "xgb_rmse": round(xgb_rmse, 4),
        "rf_mae_improvement_percent": rf_mae_imp,
        "rf_rmse_improvement_percent": rf_rmse_imp,
        "xgb_mae_improvement_percent": xgb_mae_imp,
        "xgb_rmse_improvement_percent": xgb_rmse_imp,
        "recommended_model": recommended_model,
        "verdict": verdict,
        "ml_beats_baseline": ml_beats_baseline
    }
    
    return df_comp, summary


def evaluate_block_spatial_performance(
    predictions_path: str = DEFAULT_OUTPUT_PREDICTIONS_PATH,
    output_path: str = DEFAULT_BLOCK_PERFORMANCE_CSV
) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """
    Evaluate downscaling performance per Nashik block.
    
    Creates ml/validation/block_performance.csv with columns:
    - block_name
    - test_observations
    - baseline_mae
    - model_mae
    - baseline_rmse
    - model_rmse
    - mae_improvement_percentage
    - rmse_improvement_percentage
    
    Sorted by mae_improvement_percentage descending.
    
    Categorizes blocks into:
    - improved (mae_improvement_percentage > 5.0%)
    - approximately_equal (-5.0% <= mae_improvement_percentage <= 5.0%)
    - worse (mae_improvement_percentage < -5.0%)
    """
    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions file not found at {predictions_path}.")
        
    df = pd.read_csv(predictions_path)
    
    records = []
    for blk in df["block_name"].unique():
        sub = df[df["block_name"] == blk]
        yt = sub["actual_rainfall_mm"].values
        yb = sub["block_forecast_rainfall_mm"].values
        yp = sub["predicted_rainfall_mm"].values
        n = len(sub)
        
        b_mae = float(np.mean(np.abs(yb - yt)))
        b_rmse = float(np.sqrt(np.mean((yb - yt) ** 2)))
        
        m_mae = float(np.mean(np.abs(yp - yt)))
        m_rmse = float(np.sqrt(np.mean((yp - yt) ** 2)))
        
        mae_imp = round(((b_mae - m_mae) / b_mae) * 100.0, 2) if b_mae > 0 else 0.0
        rmse_imp = round(((b_rmse - m_rmse) / b_rmse) * 100.0, 2) if b_rmse > 0 else 0.0
        
        records.append({
            "block_name": blk,
            "test_observations": n,
            "baseline_mae": round(b_mae, 4),
            "model_mae": round(m_mae, 4),
            "baseline_rmse": round(b_rmse, 4),
            "model_rmse": round(m_rmse, 4),
            "mae_improvement_percentage": mae_imp,
            "rmse_improvement_percentage": rmse_imp
        })
        
    df_res = pd.DataFrame(records).sort_values(by="mae_improvement_percentage", ascending=False).reset_index(drop=True)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_res.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Saved block spatial performance to: {output_path}")
    
    improved_blocks = df_res[df_res["mae_improvement_percentage"] > 5.0]["block_name"].tolist()
    equal_blocks = df_res[(df_res["mae_improvement_percentage"] >= -5.0) & (df_res["mae_improvement_percentage"] <= 5.0)]["block_name"].tolist()
    worse_blocks = df_res[df_res["mae_improvement_percentage"] < -5.0]["block_name"].tolist()
    
    categories = {
        "improved": improved_blocks,
        "approximately_equal": equal_blocks,
        "worse": worse_blocks
    }
    
    return df_res, categories


DEFAULT_LEAD_DAY_PERFORMANCE_CSV = os.path.join(DEFAULT_VALIDATION_DIR, "lead_day_performance.csv")


def evaluate_lead_day_performance(
    predictions_path: str = DEFAULT_OUTPUT_PREDICTIONS_PATH,
    output_path: str = DEFAULT_LEAD_DAY_PERFORMANCE_CSV
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Evaluate downscaled rainfall prediction performance broken down by lead_days.
    
    For each lead day:
    - observation_count
    - baseline_mae
    - model_mae
    - baseline_rmse
    - model_rmse
    - mae_improvement_percentage
    - rmse_improvement_percentage
    
    Saves to: ml/validation/lead_day_performance.csv
    Identifies forecast horizons that benefit from downscaling.
    """
    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions file not found at: {predictions_path}")
        
    df = pd.read_csv(predictions_path)
    required_cols = {"lead_days", "actual_rainfall_mm", "block_forecast_rainfall_mm", "predicted_rainfall_mm"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in predictions: {missing}")
        
    records = []
    for lead in sorted(df["lead_days"].unique()):
        sub = df[df["lead_days"] == lead]
        yt = sub["actual_rainfall_mm"].values
        yb = sub["block_forecast_rainfall_mm"].values
        yp = sub["predicted_rainfall_mm"].values
        n = len(sub)
        
        b_mae = float(np.mean(np.abs(yb - yt)))
        b_rmse = float(np.sqrt(np.mean((yb - yt) ** 2)))
        
        m_mae = float(np.mean(np.abs(yp - yt)))
        m_rmse = float(np.sqrt(np.mean((yp - yt) ** 2)))
        
        mae_imp = round(((b_mae - m_mae) / b_mae) * 100.0, 2) if b_mae > 0 else 0.0
        rmse_imp = round(((b_rmse - m_rmse) / b_rmse) * 100.0, 2) if b_rmse > 0 else 0.0
        
        records.append({
            "lead_days": int(lead),
            "observation_count": n,
            "baseline_mae": round(b_mae, 4),
            "model_mae": round(m_mae, 4),
            "baseline_rmse": round(b_rmse, 4),
            "model_rmse": round(m_rmse, 4),
            "mae_improvement_percentage": mae_imp,
            "rmse_improvement_percentage": rmse_imp
        })
        
    df_res = pd.DataFrame(records).sort_values(by="lead_days").reset_index(drop=True)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_res.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Saved lead day performance to: {output_path}")
    
    benefiting_leads = df_res[df_res["mae_improvement_percentage"] > 0.0]["lead_days"].tolist()
    non_benefiting_leads = df_res[df_res["mae_improvement_percentage"] <= 0.0]["lead_days"].tolist()
    
    summary = {
        "benefiting_lead_days": benefiting_leads,
        "non_benefiting_lead_days": non_benefiting_leads,
        "lead_days_evaluated": df_res["lead_days"].tolist()
    }
    
    return df_res, summary


DEFAULT_RAINFALL_DISTRIBUTION_CSV = os.path.join(DEFAULT_VALIDATION_DIR, "rainfall_distribution_report.csv")


def analyze_rainfall_distribution(
    predictions_path: str = DEFAULT_OUTPUT_PREDICTIONS_PATH,
    output_path: str = DEFAULT_RAINFALL_DISTRIBUTION_CSV
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Analyze and compare the rainfall distribution of:
    1. Actual Ground Rainfall (actual_rainfall_mm)
    2. IMD Block Forecast (block_forecast_rainfall_mm)
    3. Model Prediction (predicted_rainfall_mm)
    
    Computes:
    - Percentage of zero rainfall observations
    - Percentage of non-zero observations
    - Minimum, Maximum, Median, Mean, Std Dev, 25th percentile, 75th percentile, IQR
    
    Saves to: ml/validation/rainfall_distribution_report.csv
    """
    if not os.path.exists(predictions_path):
        raise FileNotFoundError(f"Predictions file not found at: {predictions_path}")
        
    df = pd.read_csv(predictions_path)
    series_map = {
        "Actual Ground Rainfall": "actual_rainfall_mm",
        "IMD Block Forecast": "block_forecast_rainfall_mm",
        "Selected Model Prediction": "predicted_rainfall_mm"
    }
    
    records = []
    summary = {}
    
    for label, col in series_map.items():
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in predictions dataframe.")
            
        vals = df[col].values
        n = len(vals)
        zero_count = int(np.sum(vals == 0.0))
        zero_pct = round((zero_count / n) * 100.0, 2) if n > 0 else 0.0
        nonzero_count = int(np.sum(vals > 0.0))
        nonzero_pct = round((nonzero_count / n) * 100.0, 2) if n > 0 else 0.0
        
        min_v = float(np.min(vals))
        max_v = float(np.max(vals))
        med_v = float(np.median(vals))
        mean_v = float(np.mean(vals))
        std_v = float(np.std(vals))
        p25_v = float(np.percentile(vals, 25))
        p75_v = float(np.percentile(vals, 75))
        iqr_v = p75_v - p25_v
        
        row_dict = {
            "series": label,
            "column_name": col,
            "total_observations": n,
            "zero_observations_count": zero_count,
            "zero_percentage": zero_pct,
            "nonzero_observations_count": nonzero_count,
            "nonzero_percentage": nonzero_pct,
            "minimum_mm": round(min_v, 4),
            "maximum_mm": round(max_v, 4),
            "median_mm": round(med_v, 4),
            "mean_mm": round(mean_v, 4),
            "std_mm": round(std_v, 4),
            "p25_mm": round(p25_v, 4),
            "p75_mm": round(p75_v, 4),
            "iqr_mm": round(iqr_v, 4)
        }
        records.append(row_dict)
        summary[label] = row_dict
        
    df_report = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_report.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Saved rainfall distribution report to: {output_path}")
    
    return df_report, summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=" * 70)
    print("SIH26074 -- MODEL EVALUATION & BENCHMARK COMPARISON (DAY 3 - STEP 14)")
    print("=" * 70)
    
    metrics_df, _, rf_summary = evaluate_random_forest()
    comp_df, comp_summary = compare_all_models()
    block_df, block_cats = evaluate_block_spatial_performance()
    lead_df, lead_summary = evaluate_lead_day_performance()
    dist_df, dist_summary = analyze_rainfall_distribution()
    diag_df, slices = generate_prediction_diagnostics()
    imp_df = export_feature_importance()
    
    print("\n" + "=" * 70)
    print("3-MODEL COMPARISON TABLE (ON IDENTICAL 278 TEST OBSERVATIONS)")
    print("=" * 70)
    print(comp_df.to_string(index=False))
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("SPATIAL PERFORMANCE BY NASHIK BLOCK (SORTED BY MAE IMPROVEMENT)")
    print("=" * 70)
    print(block_df.to_string(index=False))
    print("-" * 70)
    print("BLOCK CATEGORIZATION:")
    print(f"  - Blocks where model IMPROVES (>+5%):       {block_cats['improved']}")
    print(f"  - Blocks approximately EQUAL (within +/-5%): {block_cats['approximately_equal']}")
    print(f"  - Blocks where model performs WORSE (<-5%): {block_cats['worse']}")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("FORECAST LEAD DAY PERFORMANCE")
    print("=" * 70)
    print(lead_df.to_string(index=False))
    print("-" * 70)
    print(f"Benefiting Lead Days (MAE Improvement > 0%): {lead_summary['benefiting_lead_days']}")
    print(f"Non-Benefiting Lead Days (MAE Improvement <= 0%): {lead_summary['non_benefiting_lead_days']}")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("RAINFALL DISTRIBUTION ANALYSIS & COMPARISON")
    print("=" * 70)
    print(dist_df[["series", "zero_percentage", "nonzero_percentage", "minimum_mm", "maximum_mm", "median_mm", "mean_mm"]].to_string(index=False))
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("RECOMMENDED V1 MODEL & EVALUATION VERDICT")
    print("=" * 70)
    print(f"Verdict: {comp_summary['verdict']}")
    print(f"Recommended Model: {comp_summary['recommended_model']}")
    print("=" * 70)
    
    print(f"\nCreated: {DEFAULT_METRICS_PATH}")
    print(f"Created: {DEFAULT_COMPARISON_PATH}")
    print(f"Created: {DEFAULT_BLOCK_PERFORMANCE_CSV}")
    print(f"Created: {DEFAULT_LEAD_DAY_PERFORMANCE_CSV}")
    print(f"Created: {DEFAULT_RAINFALL_DISTRIBUTION_CSV}")
    print(f"Created: {DEFAULT_DIAGNOSTICS_PATH}")
    print(f"Created: {DEFAULT_FEATURE_IMPORTANCE_CSV}")
    print(f"Created: {DEFAULT_FEATURE_IMPORTANCE_PNG}")
    print("=" * 70)




