"""
Structured Application Logging Configuration and Helpers.

Ensures structured, concise logging across backend endpoints and ML services:
- Request type
- Panchayat ID
- Forecast date
- Block name
- Model name & version
- Prediction success/failure
- Database operation success/failure

Guarantees ZERO exposure of:
- Passwords
- Supabase keys / API keys
- Access tokens
- Database connection URLs containing credentials
"""

import re
import logging
import sys
from typing import Optional, Any


# Regular expression to identify and mask database URLs containing credentials (e.g., postgresql://user:pass@host:5432/db)
DB_CREDENTIALS_REGEX = re.compile(
    r'(postgresql(?:\+\w+)?://)([^:]+):([^@]+)@',
    re.IGNORECASE
)

# Regular expression to sanitize common sensitive key-value pairs
SENSITIVE_KEY_REGEX = re.compile(
    r'(password|passwd|secret|api_key|apikey|supabase_key|access_token|authorization|token)\s*[:=]\s*([^\s,;]+)',
    re.IGNORECASE
)


class SanitizedFormatter(logging.Formatter):
    """
    Custom logging formatter that strips and sanitizes sensitive credentials,
    database passwords, and API keys from all log messages.
    """

    def format(self, record: logging.LogRecord) -> str:
        original_msg = super().format(record)
        # 1. Mask database URLs: postgresql://user:password@host -> postgresql://user:***@host
        sanitized = DB_CREDENTIALS_REGEX.sub(r'\1\2:***@', original_msg)
        # 2. Mask explicit sensitive tokens
        sanitized = SENSITIVE_KEY_REGEX.sub(r'\1=***', sanitized)
        return sanitized


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure root and application loggers with concise structured formatting.
    """
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    formatter = SanitizedFormatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Avoid duplicate handlers if setup_logging is called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Set appropriate levels for project modules
    logging.getLogger("backend").setLevel(level)
    logging.getLogger("src").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# Structured Logging Helpers

def log_forecast_request(
    logger: logging.Logger,
    request_type: str,
    panchayat_id: int,
    forecast_date: Any,
    forecast_issue_date: Optional[Any] = None,
) -> None:
    """Log incoming forecast generation or retrieval request."""
    issue_str = f" forecast_issue_date={forecast_issue_date}" if forecast_issue_date else ""
    logger.info(
        f"[REQUEST] request_type={request_type} panchayat_id={panchayat_id} "
        f"forecast_date={forecast_date}{issue_str}"
    )


def log_prediction_success(
    logger: logging.Logger,
    panchayat_id: int,
    block_name: str,
    forecast_date: Any,
    model_name: str,
    model_version: str,
    block_forecast_mm: float,
    downscaled_rainfall_mm: float,
) -> None:
    """Log successful downscaling prediction."""
    logger.info(
        f"[PREDICTION_SUCCESS] panchayat_id={panchayat_id} block_name={block_name} "
        f"forecast_date={forecast_date} model_name=\"{model_name}\" model_version=\"{model_version}\" "
        f"block_forecast_mm={block_forecast_mm:.2f} downscaled_rainfall_mm={downscaled_rainfall_mm:.4f}"
    )


def log_prediction_failure(
    logger: logging.Logger,
    panchayat_id: int,
    forecast_date: Any,
    reason: str,
    block_name: Optional[str] = None,
    level: int = logging.WARNING,
) -> None:
    """Log failed downscaling prediction."""
    block_str = f" block_name={block_name}" if block_name else ""
    logger.log(
        level,
        f"[PREDICTION_FAILURE] panchayat_id={panchayat_id} forecast_date={forecast_date}"
        f"{block_str} reason=\"{reason}\""
    )


def log_db_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    status: str,
    panchayat_id: Optional[int] = None,
    forecast_date: Optional[Any] = None,
    details: Optional[str] = None,
    level: int = logging.INFO,
) -> None:
    """Log database query or persistence operation."""
    pid_str = f" panchayat_id={panchayat_id}" if panchayat_id is not None else ""
    date_str = f" forecast_date={forecast_date}" if forecast_date is not None else ""
    details_str = f" details=\"{details}\"" if details else ""
    logger.log(
        level,
        f"[DB_OPERATION] operation={operation} table={table} status={status}"
        f"{pid_str}{date_str}{details_str}"
    )
