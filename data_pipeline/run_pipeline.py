import os
import sys
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_pipeline.cleaner import clean_raw_weather_data
from data_pipeline.baseline_builder import build_baseline_dataset
from data_pipeline.feature_builder import build_rainfall_features
from data_pipeline.validator import validate_administrative_data
from data_pipeline.geo_validator import validate_geographic_coordinates
from data_pipeline.elevation_validator import validate_elevation_data
from data_pipeline.date_validator import validate_forecast_dates
from data_pipeline.forecast_validator import validate_block_forecasts
from data_pipeline.station_validator import validate_station_ground_truth
from data_pipeline.distance_validator import validate_station_distances
from data_pipeline.proximity_auditor import audit_station_proximity
from data_pipeline.duplicate_validator import validate_duplicates
from data_pipeline.data_splitter import split_features_chronologically
from data_pipeline.supabase_loader import load_clean_data_to_supabase, verify_supabase_data


def run_nashik_data_pipeline(
    raw_input_path: str = "data/raw/nashik_panchayat_weather_raw.csv",
    load_supabase: bool = True
):
    """
    Execute full Day 2 Nashik Data Pipeline:
    1. Clean raw weather dataset -> data/processed/nashik_weather_clean.csv
    2. Build baseline benchmark dataset -> data/processed/nashik_baseline_dataset.csv
    3. Build ML features dataset -> data/features/nashik_rainfall_features.csv
    4. Chronological Train/Test Split (80/20) -> data/features/nashik_train.csv & data/features/nashik_test.csv
    5. Administrative Validation -> data/validation/administrative_validation.csv & nashik_block_summary.csv
    6. Geographic Validation -> data/validation/geographic_validation.csv
    7. Elevation Validation -> data/validation/elevation_validation.csv
    8. Forecast Date Validation -> data/validation/date_validation.csv
    9. Block Forecast Validation -> data/validation/forecast_validation.csv
    10. Station Ground-Truth Validation -> data/validation/station_validation.csv
    11. Station Distance Validation -> data/validation/distance_validation.csv
    12. Station Proximity Audit -> data/validation/station_proximity.csv
    13. Duplicate Validation -> data/validation/duplicate_validation.csv & duplicate_removal_log.csv
    14. Supabase Data Load & Verification -> panchayat_weather_data table & data/validation/supabase_verification.csv
    """
    print("=" * 70)
    print("SIH26074 -- NASHIK DATA PIPELINE & VALIDATION (DAY 2)")
    print("=" * 70)

    # Step 1: Cleaning
    print("\n[1/13] Cleaning raw dataset...")
    clean_df = clean_raw_weather_data(
        input_path=raw_input_path,
        output_path="data/processed/nashik_weather_clean.csv"
    )
    print(f"  [OK] Produced data/processed/nashik_weather_clean.csv ({len(clean_df)} rows, {len(clean_df.columns)} columns)")

    # Step 2: Baseline Dataset & Evaluation Metrics
    print("\n[2/13] Building baseline dataset & evaluating original block forecast...")
    baseline_df, metrics_df, baseline_stats = build_baseline_dataset(
        clean_df=clean_df,
        output_path="data/processed/nashik_baseline_dataset.csv",
        metrics_output_path="data/validation/baseline_metrics.csv"
    )
    print(f"  [OK] Produced data/processed/nashik_baseline_dataset.csv ({len(baseline_df)} rows, {len(baseline_df.columns)} columns)")
    print(f"  [OK] Produced data/validation/baseline_metrics.csv ({len(metrics_df)} evaluation rows)")
    print(f"  --> Baseline Overall MAE:  {baseline_stats['overall_mae']:.4f} mm")
    print(f"  --> Baseline Overall RMSE: {baseline_stats['overall_rmse']:.4f} mm")

    # Step 3: Feature Engineering Dataset
    print("\n[3/13] Building rainfall features dataset...")
    feature_df, feat_summary_df, feat_stats = build_rainfall_features(
        clean_df=clean_df,
        output_path="data/features/nashik_rainfall_features.csv",
        summary_output_path="data/validation/feature_summary.csv"
    )
    print(f"  [OK] Produced data/features/nashik_rainfall_features.csv ({len(feature_df)} rows, {len(feature_df.columns)} columns)")
    print(f"  [OK] Produced data/validation/feature_summary.csv ({len(feat_summary_df)} columns evaluated)")
    print(f"  --> Training-Eligible Rows: {feat_stats['training_eligible_rows']:,}")
    print(f"  --> Prediction-Only Rows:   {feat_stats['prediction_only_rows']:,}")

    # Step 4: Chronological Train / Test Split (80/20)
    print("\n[4/13] Splitting features chronologically (80/20 train/test)...")
    train_df, test_df, split_summary_df, split_stats = split_features_chronologically(
        input_path="data/features/nashik_rainfall_features.csv",
        train_output_path="data/features/nashik_train.csv",
        test_output_path="data/features/nashik_test.csv",
        summary_output_path="data/validation/split_summary.csv"
    )
    print(f"  [OK] Produced data/features/nashik_train.csv ({len(train_df)} rows, {split_stats['train_pct']}%)")
    print(f"  [OK] Produced data/features/nashik_test.csv ({len(test_df)} rows, {split_stats['test_pct']}%)")
    print(f"  [OK] Produced data/validation/split_summary.csv")
    print(f"  --> Temporal Leakage Free: {split_stats['temporal_leakage_free']}")

    # Step 5: Administrative Validation
    print("\n[5/13] Performing administrative validation...")
    val_df, block_summary = validate_administrative_data(
        input_path="data/processed/nashik_weather_clean.csv",
        val_output_path="data/validation/administrative_validation.csv",
        summary_output_path="data/validation/nashik_block_summary.csv"
    )
    print(f"  [OK] Produced data/validation/administrative_validation.csv ({len(val_df)} rows)")
    print(f"  [OK] Produced data/validation/nashik_block_summary.csv ({len(block_summary)} blocks)")

    # Step 6: Geographic Coordinate Validation
    print("\n[6/13] Performing geographic coordinate validation...")
    geo_df, geo_stats = validate_geographic_coordinates(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/geographic_validation.csv"
    )
    print(f"  [OK] Produced data/validation/geographic_validation.csv ({len(geo_df)} rows)")

    # Step 7: Elevation Validation
    print("\n[7/13] Performing elevation validation...")
    elev_df, elev_stats = validate_elevation_data(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/elevation_validation.csv"
    )
    print(f"  [OK] Produced data/validation/elevation_validation.csv ({len(elev_df)} rows)")

    # Step 8: Forecast Date Validation
    print("\n[8/13] Performing forecast date validation...")
    date_df, freq_df = validate_forecast_dates(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/date_validation.csv"
    )
    print(f"  [OK] Produced data/validation/date_validation.csv ({len(date_df)} rows)")

    # Step 9: IMD Block Forecast Validation
    print("\n[9/13] Performing IMD block forecast validation...")
    fc_df, fc_stats = validate_block_forecasts(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/forecast_validation.csv"
    )
    print(f"  [OK] Produced data/validation/forecast_validation.csv ({len(fc_df)} groups)")

    # Step 10: Station Ground-Truth Validation
    print("\n[10/13] Performing station ground-truth validation...")
    st_df, st_stats = validate_station_ground_truth(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/station_validation.csv"
    )
    print(f"  [OK] Produced data/validation/station_validation.csv ({len(st_df)} station location entries)")

    # Step 11: Station Distance Validation
    print("\n[11/13] Performing station distance validation...")
    dist_df, dist_stats = validate_station_distances(
        raw_input_path=raw_input_path,
        output_path="data/validation/distance_validation.csv"
    )
    print(f"  [OK] Produced data/validation/distance_validation.csv ({len(dist_df)} records)")

    # Step 12: Station Proximity Audit
    print("\n[12/13] Performing station proximity audit...")
    prox_df, block_prox_df, prox_stats = audit_station_proximity(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/station_proximity.csv"
    )
    print(f"  [OK] Produced data/validation/station_proximity.csv ({len(prox_df)} records)")

    # Step 13: Duplicate Validation & Audit
    print("\n[13/14] Performing duplicate validation...")
    dup_df, rem_df, dup_stats = validate_duplicates(
        input_path="data/processed/nashik_weather_clean.csv",
        output_path="data/validation/duplicate_validation.csv",
        log_output_path="data/validation/duplicate_removal_log.csv"
    )
    print(f"  [OK] Produced data/validation/duplicate_validation.csv ({len(dup_df)} records)")
    print(f"  [OK] Produced data/validation/duplicate_removal_log.csv ({len(rem_df)} rows removed)")

    # Step 14: Supabase Database Load & Verification
    db_results = None
    if load_supabase:
        print("\n[14/14] Uploading clean dataset to Supabase & running verification...")
        uploaded_count, db_results = load_clean_data_to_supabase(
            csv_path="data/processed/nashik_weather_clean.csv",
            batch_size=250,
            summary_output_path="data/validation/supabase_verification.csv"
        )
        print(f"  [OK] Successfully synchronized {uploaded_count:,} records to Supabase 'panchayat_weather_data'.")
        print(f"  [OK] Produced data/validation/supabase_verification.csv")

    # Output Validation Summaries
    print("\n" + "=" * 70)
    print("BASELINE BLOCK FORECAST PERFORMANCE BENCHMARK (DAY 2 - STEP 13)")
    print("=" * 70)
    print(f"Total Evaluated Records:     {baseline_stats['total_records']:,}")
    print(f"Overall Baseline MAE:        {baseline_stats['overall_mae']:.4f} mm")
    print(f"Overall Baseline RMSE:       {baseline_stats['overall_rmse']:.4f} mm")
    print(f"Mean Forecast Rainfall:      {baseline_stats['mean_forecast_mm']:.2f} mm")
    print(f"Mean Actual Rainfall:        {baseline_stats['mean_actual_mm']:.2f} mm")
    print("-" * 70)
    print(f"{'Dimension':<12} {'Group':<22} {'Count':>6} {'Mean Fc':>8} {'Mean Act':>9} {'MAE (mm)':>9} {'RMSE (mm)':>10}")
    print("-" * 70)
    for _, r in metrics_df.iterrows():
        print(f"{r['group_type']:<12} {r['group_name']:<22} {int(r['record_count']):>6} {r['mean_forecast_mm']:>8.2f} {r['mean_actual_mm']:>9.2f} {r['mae_mm']:>9.4f} {r['rmse_mm']:>10.4f}")
    print("=" * 70)

    # Output Feature Engineering Summary
    print("\n" + "=" * 70)
    print("ML FEATURE DATASET SUMMARY (DAY 2 - STEP 14)")
    print("=" * 70)
    print(f"Total Rows:                  {feat_stats['total_rows']:,}")
    print(f"Training-Eligible Rows:      {feat_stats['training_eligible_rows']:,} ({feat_stats['training_eligible_rows']/feat_stats['total_rows']*100:.1f}%)")
    print(f"Prediction-Only Rows:        {feat_stats['prediction_only_rows']:,} ({feat_stats['prediction_only_rows']/feat_stats['total_rows']*100:.1f}%)")
    print(f"ML Features Count:           {feat_stats['feature_count']} (X)")
    print(f"Metadata Fields:             {feat_stats['metadata_count']} (Non-features)")
    print("-" * 70)
    print(f"{'Feature/Column':<28} {'Role':<11} {'Type':<8} {'Nulls':>5} {'Min':>8} {'Median':>8} {'Mean':>8} {'Max':>8}")
    print("-" * 70)
    for _, r in feat_summary_df.iterrows():
        min_s = f"{r['min_val']:.2f}" if pd.notnull(r['min_val']) else "-"
        med_s = f"{r['median_val']:.2f}" if pd.notnull(r['median_val']) else "-"
        mean_s = f"{r['mean_val']:.2f}" if pd.notnull(r['mean_val']) else "-"
        max_s = f"{r['max_val']:.2f}" if pd.notnull(r['max_val']) else "-"
        print(f"{r['column_name']:<28} {r['column_role']:<11} {r['data_type']:<8} {int(r['missing_count']):>5} {min_s:>8} {med_s:>8} {mean_s:>8} {max_s:>8}")
    print("=" * 70)

    # Output Chronological Split Summary
    print("\n" + "=" * 70)
    print("CHRONOLOGICAL TRAIN / TEST SPLIT SUMMARY (DAY 2 - STEP 15)")
    print("=" * 70)
    print(f"Total Dataset Records:       {split_stats['total_rows']:,}")
    print(f"Train Records (Earliest 80%):{split_stats['train_rows']:,} ({split_stats['train_pct']}%)")
    print(f"Test Records (Latest 20%):   {split_stats['test_rows']:,} ({split_stats['test_pct']}%)")
    print(f"Train Date Range:            {split_stats['train_start_date']} to {split_stats['train_end_date']}")
    print(f"Test Date Range:             {split_stats['test_start_date']} to {split_stats['test_end_date']}")
    print(f"Unique Train Panchayats:     {split_stats['unique_train_panchayats']}")
    print(f"Unique Test Panchayats:      {split_stats['unique_test_panchayats']}")
    print(f"Unique Train Blocks:         {split_stats['unique_train_blocks']}")
    print(f"Unique Test Blocks:          {split_stats['unique_test_blocks']}")
    print(f"Temporal Lookahead Leakage:  {'NONE (Zero Leakage Verified)' if split_stats['temporal_leakage_free'] else 'DETECTED!'}")
    print("=" * 70)

    # Output Supabase Verification Summary
    if db_results:
        print("\n" + "=" * 70)
        print("SUPABASE DATA LOAD VERIFICATION REPORT (DAY 2 - STEP 16)")
        print("=" * 70)
        print(f"1. Database Row Count:             {db_results['row_count']:,}")
        print(f"2. Unique Panchayat Count:         {db_results['unique_panchayat_count']:,}")
        print(f"3. Unique Block Count:             {db_results['unique_block_count']}")
        print(f"4. Unique Station Count:           {db_results['unique_station_count']}")
        print(f"5. Minimum Date:                   {db_results['min_date']}")
        print(f"6. Maximum Date:                   {db_results['max_date']}")
        print(f"7. Missing Actual Rainfall Count:  {db_results['missing_actual_rainfall_count']}")
        print(f"8. Missing Elevation Count:        {db_results['missing_elevation_count']}")
        print(f"9. Missing Forecast Count:         {db_results['missing_forecast_count']}")
        print("=" * 70)


if __name__ == "__main__":
    run_nashik_data_pipeline()







