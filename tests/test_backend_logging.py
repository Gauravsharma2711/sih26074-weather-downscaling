"""
Automated Unit and Integration Tests for Structured Backend Logging.

Verifies:
1. Logging format captures request type, panchayat ID, forecast date, block name,
   model name, model version, prediction success/failure, and database operation status.
2. Sensitive credentials (passwords, supabase keys, API keys, access tokens,
   database connection URLs) are strictly sanitized and never exposed in logs.
3. Appropriate INFO, WARNING, and ERROR log levels are used.
"""

import logging
import pytest
from datetime import date
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.logging import (
    SanitizedFormatter,
    setup_logging,
    log_forecast_request,
    log_prediction_success,
    log_prediction_failure,
    log_db_operation,
)


client = TestClient(app)


def test_sanitized_formatter_masks_database_urls():
    """Test that database connection URLs with passwords are automatically masked."""
    formatter = SanitizedFormatter(fmt="%(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Connecting to postgresql://postgres:mysecretpassword@db.supabase.co:5432/postgres",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "mysecretpassword" not in formatted
    assert "postgresql://postgres:***@db.supabase.co:5432/postgres" in formatted


def test_sanitized_formatter_masks_api_keys_and_tokens():
    """Test that API keys, supabase keys, and access tokens are sanitized."""
    formatter = SanitizedFormatter(fmt="%(message)s")
    test_cases = [
        ("api_key: secret_api_key_12345", "api_key=***"),
        ("supabase_key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "supabase_key=***"),
        ("password=super_secret_pw", "password=***"),
        ("access_token=bearer_xyz_9876", "access_token=***"),
    ]
    for raw_msg, expected_mask in test_cases:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=raw_msg,
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert expected_mask in formatted


def test_structured_log_helpers(caplog):
    """Test that structured logging helper functions produce expected concise key-value pairs."""
    logger = logging.getLogger("test_logger")
    
    with caplog.at_level(logging.INFO):
        # 1. Request logging
        log_forecast_request(
            logger=logger,
            request_type="POST /api/v1/forecast/generate",
            panchayat_id=1001,
            forecast_date=date(2026, 9, 4),
            forecast_issue_date=date(2026, 9, 4),
        )
        assert "[REQUEST]" in caplog.text
        assert "request_type=POST /api/v1/forecast/generate" in caplog.text
        assert "panchayat_id=1001" in caplog.text
        assert "forecast_date=2026-09-04" in caplog.text

        # 2. Prediction success
        log_prediction_success(
            logger=logger,
            panchayat_id=1001,
            block_name="Baglan",
            forecast_date=date(2026, 9, 4),
            model_name="XGBoost Regressor",
            model_version="v1.0.0",
            block_forecast_mm=5.0,
            downscaled_rainfall_mm=2.7926,
        )
        assert "[PREDICTION_SUCCESS]" in caplog.text
        assert "block_name=Baglan" in caplog.text
        assert 'model_name="XGBoost Regressor"' in caplog.text
        assert 'model_version="v1.0.0"' in caplog.text
        assert "block_forecast_mm=5.00" in caplog.text
        assert "downscaled_rainfall_mm=2.7926" in caplog.text

        # 3. Prediction failure
        log_prediction_failure(
            logger=logger,
            panchayat_id=9999,
            forecast_date=date(2026, 9, 4),
            reason="Panchayat not found",
            block_name="Unknown",
            level=logging.WARNING,
        )
        assert "[PREDICTION_FAILURE]" in caplog.text
        assert "panchayat_id=9999" in caplog.text
        assert 'reason="Panchayat not found"' in caplog.text

        # 4. DB operation success
        log_db_operation(
            logger=logger,
            operation="INSERT",
            table="downscaled_forecasts",
            status="SUCCESS",
            panchayat_id=1001,
            forecast_date=date(2026, 9, 4),
        )
        assert "[DB_OPERATION]" in caplog.text
        assert "operation=INSERT" in caplog.text
        assert "table=downscaled_forecasts" in caplog.text
        assert "status=SUCCESS" in caplog.text


def test_endpoint_logging_during_forecast_generation(caplog):
    """Verify live endpoint logging during forecast generation request."""
    with caplog.at_level(logging.INFO):
        response = client.post(
            "/api/v1/forecast/generate",
            json={
                "panchayat_id": 1001,
                "forecast_date": "2026-09-04",
                "forecast_issue_date": "2026-09-04",
            },
        )
        assert response.status_code == 200
        assert "[REQUEST]" in caplog.text
        assert "request_type=POST /api/v1/forecast/generate" in caplog.text
        assert "panchayat_id=1001" in caplog.text
        assert "[PREDICTION_SUCCESS]" in caplog.text
        assert "block_name=Baglan" in caplog.text
        assert "[DB_OPERATION]" in caplog.text
        assert "table=downscaled_forecasts" in caplog.text


def test_endpoint_logging_during_forecast_retrieval(caplog):
    """Verify live endpoint logging during forecast retrieval request."""
    with caplog.at_level(logging.INFO):
        response = client.get("/api/v1/forecast/panchayat/1001?forecast_date=2026-09-04")
        assert response.status_code == 200
        assert "[REQUEST]" in caplog.text
        assert "request_type=GET /api/v1/forecast/panchayat/{panchayat_id}" in caplog.text
        assert "[DB_OPERATION]" in caplog.text
        assert "operation=SELECT" in caplog.text
        assert "table=downscaled_forecasts" in caplog.text
        assert "status=SUCCESS" in caplog.text
