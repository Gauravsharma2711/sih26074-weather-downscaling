import os
import pandas as pd
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
from data_pipeline.supabase_loader import verify_supabase_data
from data_pipeline.final_audit import run_day2_final_readiness_audit
from src.utils.geospatial import haversine_distance


def test_data_pipeline_execution(tmp_path):
    # Create sample raw dataset
    raw_csv = tmp_path / "sample_raw.csv"
    sample_data = pd.DataFrame([{
        "panchayat_id": 1001,
        "lgd_code": 182597,
        "panchayat_name": "Test Panchayat\xa0",
        "block_name": "Baglan",
        "district_name": "Nashik",
        "latitude": 20.65,
        "longitude": 74.05,
        "elevation_m": 580.0,
        "date": "01-09-2026",
        "forecast_issue_date": "31-08-2026",
        "block_forecast_rainfall_mm": 12.5,
        "station_id": "Satana\xa0AWS",
        "station_latitude": 20.59,
        "station_longitude": 74.20,
        "station_distance_km": 16.92,
        "actual_rainfall_mm": 14.0,
        "Unnamed: 16": None
    }])
    sample_data.to_csv(raw_csv, index=False, encoding="latin1")

    # Test cleaner
    clean_csv = tmp_path / "sample_clean.csv"
    clean_df = clean_raw_weather_data(str(raw_csv), str(clean_csv))
    assert len(clean_df) == 1
    assert "Unnamed: 16" not in clean_df.columns
    assert clean_df["station_id"].iloc[0] == "Satana AWS"
    assert clean_df["date"].iloc[0] == "2026-09-01"
    assert "panchayat_latitude" in clean_df.columns
    assert "panchayat_longitude" in clean_df.columns
    assert clean_df["station_distance_km"].iloc[0] > 0

    # Test baseline builder
    baseline_csv = tmp_path / "sample_baseline.csv"
    metrics_csv = tmp_path / "sample_metrics.csv"
    baseline_df, metrics_df, baseline_stats = build_baseline_dataset(clean_df, str(baseline_csv), str(metrics_csv))
    assert len(baseline_df) == 1
    assert "lead_days" in baseline_df.columns
    assert "block_forecast_rainfall_mm" in baseline_df.columns
    assert "actual_rainfall_mm" in baseline_df.columns
    assert baseline_stats["overall_mae"] == 1.5
    assert baseline_stats["overall_rmse"] == 1.5
    assert len(metrics_df) > 0

    # Test feature builder
    features_csv = tmp_path / "sample_features.csv"
    feat_summary_csv = tmp_path / "sample_feat_summary.csv"
    features_df, feat_summary_df, feat_stats = build_rainfall_features(clean_df, str(features_csv), str(feat_summary_csv))
    assert len(features_df) == 1
    assert "lead_days" in features_df.columns
    assert "month" in features_df.columns
    assert "day_of_year" in features_df.columns
    assert features_df["lead_days"].iloc[0] == 1
    assert features_df["month"].iloc[0] == 9
    assert feat_stats["training_eligible_rows"] == 1
    assert len(feat_summary_df) > 0

    # Test administrative validator
    val_csv = tmp_path / "sample_val.csv"
    summary_csv = tmp_path / "sample_summary.csv"
    val_df, summary_df = validate_administrative_data(str(clean_csv), str(val_csv), str(summary_csv))
    assert len(val_df) == 1
    assert val_df["validation_status"].iloc[0] == "VALID"
    assert len(summary_df) == 1
    assert summary_df["unique_panchayat_count"].iloc[0] == 1

    # Test geographic coordinate validator
    geo_csv = tmp_path / "sample_geo.csv"
    geo_df, stats = validate_geographic_coordinates(str(clean_csv), str(geo_csv))
    assert len(geo_df) == 1
    assert stats["valid_records"] == 1
    assert stats["missing_coordinates"] == 0
    assert stats["invalid_records"] == 0

    # Test elevation validator
    elev_csv = tmp_path / "sample_elev.csv"
    elev_df, elev_stats = validate_elevation_data(str(clean_csv), str(elev_csv))
    assert len(elev_df) == 1
    assert elev_stats["valid_records"] == 1
    assert elev_stats["missing_elevation"] == 0
    assert elev_stats["minimum"] == 580.0

    # Test forecast date validator
    date_csv = tmp_path / "sample_date.csv"
    date_df, freq_df = validate_forecast_dates(str(clean_csv), str(date_csv))
    assert len(date_df) == 1
    assert date_df["lead_days"].iloc[0] == 1
    assert date_df["validation_status"].iloc[0] == "VALID"
    assert len(freq_df) == 1

    # Test block forecast validator
    fc_csv = tmp_path / "sample_fc.csv"
    fc_df, fc_stats = validate_block_forecasts(str(clean_csv), str(fc_csv))
    assert len(fc_df) == 1
    assert fc_stats["total_groups"] == 1
    assert fc_stats["missing_values"] == 0
    assert fc_df["validation_status"].iloc[0] == "VALID"

    # Test station ground-truth validator
    st_csv = tmp_path / "sample_st.csv"
    st_df, st_stats = validate_station_ground_truth(str(clean_csv), str(st_csv))
    assert len(st_df) == 1
    assert st_stats["unique_stations"] == 1
    assert st_stats["missing_station_ids"] == 0
    assert st_stats["missing_rainfall_records"] == 0
    assert st_df["validation_status"].iloc[0] == "VALID"

    # Test geospatial Haversine function
    h_dist = haversine_distance(20.0, 74.0, 20.0, 74.0)
    assert h_dist == 0.0
    h_dist_diff = haversine_distance(20.0, 74.0, 21.0, 74.0)
    assert 110.0 < h_dist_diff < 112.0

    # Test station distance validator
    dist_csv = tmp_path / "sample_dist.csv"
    dist_df, dist_stats = validate_station_distances(str(raw_csv), str(dist_csv))
    assert len(dist_df) == 1
    assert dist_stats["valid_records"] == 1
    assert dist_df["validation_status"].iloc[0] == "VALID"

    # Test station proximity auditor
    prox_csv = tmp_path / "sample_prox.csv"
    prox_df, block_prox_df, prox_stats = audit_station_proximity(str(clean_csv), str(prox_csv))
    assert len(prox_df) == 1
    assert len(block_prox_df) == 1
    assert prox_df["proximity_status"].iloc[0] == "NORMAL"
    assert prox_stats["total_records"] == 1

    # Test duplicate validator
    dup_csv = tmp_path / "sample_dup.csv"
    log_csv = tmp_path / "sample_dup_log.csv"
    dup_df, rem_df, dup_stats = validate_duplicates(str(clean_csv), str(dup_csv), str(log_csv))
    assert len(dup_df) == 1
    assert dup_stats["exact_duplicate_count"] == 0
    assert dup_stats["conflicting_duplicate_count"] == 0
    assert dup_df["validation_status"].iloc[0] == "VALID"

    # Test chronological data splitter
    train_csv = tmp_path / "sample_train.csv"
    test_csv = tmp_path / "sample_test.csv"
    split_sum_csv = tmp_path / "sample_split_summary.csv"
    train_df, test_df, split_sum_df, split_stats = split_features_chronologically(
        input_path=str(features_csv),
        train_output_path=str(train_csv),
        test_output_path=str(test_csv),
        summary_output_path=str(split_sum_csv),
        train_ratio=0.80
    )
    assert len(train_df) + len(test_df) == len(features_df)
    assert len(split_sum_df) == 1
    assert "train_start_date" in split_sum_df.columns
    assert "test_start_date" in split_sum_df.columns
    assert split_stats["temporal_leakage_free"] is True

    # Multi-row test for chronological ordering and zero leakage
    multi_features_csv = tmp_path / "multi_features.csv"
    multi_df = pd.DataFrame([
        {"panchayat_id": 101, "block_name": "Baglan", "date": "2026-01-01", "block_forecast_rainfall_mm": 5.0, "actual_rainfall_mm": 4.0},
        {"panchayat_id": 102, "block_name": "Baglan", "date": "2026-01-02", "block_forecast_rainfall_mm": 6.0, "actual_rainfall_mm": 5.0},
        {"panchayat_id": 103, "block_name": "Chandwad", "date": "2026-01-03", "block_forecast_rainfall_mm": 7.0, "actual_rainfall_mm": 6.0},
        {"panchayat_id": 104, "block_name": "Chandwad", "date": "2026-01-04", "block_forecast_rainfall_mm": 8.0, "actual_rainfall_mm": 7.0},
        {"panchayat_id": 105, "block_name": "Sinnar", "date": "2026-01-05", "block_forecast_rainfall_mm": 9.0, "actual_rainfall_mm": 8.0},
    ])
    multi_df.to_csv(multi_features_csv, index=False)
    m_train_csv = tmp_path / "m_train.csv"
    m_test_csv = tmp_path / "m_test.csv"
    m_summary_csv = tmp_path / "m_summary.csv"
    m_train, m_test, m_sum, m_stats = split_features_chronologically(
        input_path=str(multi_features_csv),
        train_output_path=str(m_train_csv),
        test_output_path=str(m_test_csv),
        summary_output_path=str(m_summary_csv),
        train_ratio=0.80
    )
    assert len(m_train) == 4
    assert len(m_test) == 1
    assert m_stats["train_start_date"] == "2026-01-01"
    assert m_stats["train_end_date"] == "2026-01-04"
    assert m_stats["test_start_date"] == "2026-01-05"
    assert m_stats["test_end_date"] == "2026-01-05"
    assert m_stats["temporal_leakage_free"] is True

    # Test Supabase verification report generator
    supa_verif_csv = tmp_path / "sample_supa_verif.csv"
    db_res = verify_supabase_data(summary_output_path=str(supa_verif_csv))
    assert db_res["row_count"] >= 1
    assert db_res["unique_panchayat_count"] >= 1
    assert "min_date" in db_res
    assert "max_date" in db_res

    # Test Day 2 final readiness audit
    audit_report = tmp_path / "sample_report.md"
    ready, issues = run_day2_final_readiness_audit(report_output_path=str(audit_report))
    assert ready is True
    assert len(issues) == 0
    assert os.path.exists(str(audit_report))








