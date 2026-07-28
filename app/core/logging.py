import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Produces clean, machine-readable JSON logs for production observability.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Context attributes attached via extra={...} or middleware
        if hasattr(record, "request_id"):
            log_data["request_id"] = getattr(record, "request_id")

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_data["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for local development logging.
    """

    DEFAULT_FORMAT = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s"
    )

    def __init__(self, fmt: str = DEFAULT_FORMAT, datefmt: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__(fmt=fmt, datefmt=datefmt)


def setup_logging() -> None:
    """
    Configures application-wide logging based on settings.
    Sets up formatters, handlers, and log levels for root and third-party loggers.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Determine formatter based on configuration
    if settings.LOG_FORMAT.lower() == "json":
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Stream Handler to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Configure specific framework loggers
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        framework_logger = logging.getLogger(logger_name)
        framework_logger.handlers.clear()
        framework_logger.addHandler(handler)
        framework_logger.setLevel(log_level)
        framework_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Utility factory function to retrieve configured named loggers.
    """
    return logging.getLogger(name)
