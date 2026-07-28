"""Structured logging configuration for the Privacy Agent."""

from __future__ import annotations

import logging
import sys
from typing import Any


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_string: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    date_format: str = "%Y-%m-%dT%H:%M:%S%z",
) -> logging.Logger:
    """Configure and return a structured logger.

    Args:
        name: Logger name, typically __name__.
        level: Logging level.
        format_string: Log message format.
        date_format: Date format string.

    Returns:
        Configured logger instance.
    """
    logger: logging.Logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter: logging.Formatter = logging.Formatter(
        fmt=format_string,
        datefmt=date_format,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_structured_logger(name: str) -> logging.Logger:
    """Get a pre-configured structured logger.

    Args:
        name: Logger name.

    Returns:
        Logger configured for structured output.
    """
    return setup_logger(name)

