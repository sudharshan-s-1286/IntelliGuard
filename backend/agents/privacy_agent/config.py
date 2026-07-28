"""Configuration management for the Privacy Agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_MAX_ENTITIES_PER_SCAN,
    DEFAULT_RISK_SCORE_CAP,
)


class PrivacyAgentConfig(BaseModel):
    """Configuration model for the Privacy Agent.

    Attributes:
        confidence_threshold: Minimum confidence score for PII detection.
        max_entities_per_scan: Maximum number of entities to detect per scan.
        risk_score_cap: Upper bound for the computed risk score.
        enable_masking: Whether to perform information masking.
        enable_classification: Whether to classify detected entities.
        enable_scoring: Whether to compute a privacy risk score.
        log_level: Logging verbosity level.
        extra_config: Optional additional configuration keys.
    """

    confidence_threshold: float = Field(
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
    )
    max_entities_per_scan: int = Field(
        default=DEFAULT_MAX_ENTITIES_PER_SCAN,
        ge=1,
    )
    risk_score_cap: float = Field(
        default=DEFAULT_RISK_SCORE_CAP,
        ge=0.0,
    )
    enable_masking: bool = Field(default=True)
    enable_classification: bool = Field(default=True)
    enable_scoring: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    extra_config: dict[str, Any] = Field(default_factory=dict)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that the log level is a recognized logging level."""
        valid: frozenset[str] = frozenset(
            {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        )
        upper: str = v.upper()
        if upper not in valid:
            msg: str = (
                f"Invalid log level %r. Must be one of {valid}"
                % v
            )
            raise ValueError(msg)
        return upper

