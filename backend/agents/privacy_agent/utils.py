"""Utility functions for the Privacy Agent."""

from __future__ import annotations

import hashlib
import re
from typing import Optional

from .logging_config import get_structured_logger
from .constants import (
    DEFAULT_MAX_ENTITIES_PER_SCAN,
    DEFAULT_CONFIDENCE_THRESHOLD,
)

logger = get_structured_logger(__name__)


def generate_scan_id() -> str:
    """Generate a unique scan identifier using SHA-256.

    Returns:
        A hexadecimal scan ID string.
    """
    return hashlib.sha256(
        str(id(None)).encode("utf-8")
    ).hexdigest()[:16]


def extract_context(
    text: str,
    start: int,
    end: int,
    window: int = 40,
) -> str:
    """Extract surrounding context around a matched span.

    Args:
        text: The full source text.
        start: Start position of the match.
        end: End position of the match.
        window: Number of characters to include on each side.

    Returns:
        Context string with ellipsis for truncated regions.
    """
    ctx_start: int = max(0, start - window)
    ctx_end: int = min(len(text), end + window)

    prefix: str = "..." if ctx_start > 0 else ""
    suffix: str = "..." if ctx_end < len(text) else ""

    return (
        prefix
        + text[ctx_start:ctx_end]
        + suffix
    )


def sanitize_text(text: str) -> str:
    """Normalize text for consistent processing.

    Args:
        text: Raw input text.

    Returns:
        Normalized text with standard whitespace.
    """
    return " ".join(text.split())


def validate_text_length(
    text: str,
    max_length: int = DEFAULT_MAX_ENTITIES_PER_SCAN * 100,
) -> bool:
    """Validate that text length is within acceptable bounds.

    Args:
        text: Input text to validate.
        max_length: Maximum allowed text length.

    Returns:
        True if text length is acceptable.
    """
    if len(text) > max_length:
        logger.warning(
            "Text length %d exceeds maximum %d",
            len(text),
            max_length,
        )
        return False
    return True


def truncate_text(text: str, max_len: int = 10000) -> str:
    """Truncate text to a maximum length.

    Args:
        text: Input text.
        max_len: Maximum allowed length.

    Returns:
        Truncated text.
    """
    if len(text) <= max_len:
        return text
    logger.warning(
        "Text truncated from %d to %d characters",
        len(text),
        max_len,
    )
    return text[:max_len]


def compute_entity_density(
    entity_count: int,
    text_length: int,
) -> float:
    """Compute the density of PII entities per character.

    Args:
        entity_count: Number of detected entities.
        text_length: Total length of the scanned text.

    Returns:
        Entity density as a ratio.
    """
    if text_length == 0:
        return 0.0
    return entity_count / text_length


def format_entity_for_log(
    entity_type: str,
    start: int,
    end: int,
    confidence: float,
) -> str:
    """Format entity details for structured logging.

    Args:
        entity_type: Type of PII entity.
        start: Start position.
        end: End position.
        confidence: Detection confidence.

    Returns:
        Formatted log string.
    """
    return (
        f"entity_type={entity_type},"
        f" range=[{start}:{end}],"
        f" confidence={confidence:.4f}"
    )

