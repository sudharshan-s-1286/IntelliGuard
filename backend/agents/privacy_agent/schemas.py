"""Pydantic v2 schemas for Privacy Agent input/output validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_MAX_ENTITIES_PER_SCAN,
    DEFAULT_RISK_SCORE_CAP,
)


class PIIEntitySchema(BaseModel):
    """Schema for a detected PII entity."""

    model_config = ConfigDict(extra="ignore")

    entity_type: str
    value: str
    start: int
    end: int
    confidence: float = Field(ge=0.0, le=1.0)
    sensitivity: str = Field(default="medium")
    context: str = ""

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        """Validate entity type is non-empty."""
        if not v.strip():
            msg: str = "entity_type must not be empty"
            raise ValueError(msg)
        return v


class PrivacyScanRequestSchema(BaseModel):
    """Schema for a privacy scan request."""

    model_config = ConfigDict(extra="ignore")

    text: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    options: dict[str, Any] = Field(default_factory=dict)


class PrivacyScanResponseSchema(BaseModel):
    """Schema for a privacy scan response."""

    model_config = ConfigDict(extra="ignore")

    entities: list[PIIEntitySchema] = Field(default_factory=list)
    masked_text: str = ""
    risk_score: float = 0.0
    findings: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    scan_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_entities: int = 0


class OrchestratorRequestSchema(BaseModel):
    """Schema for an Orchestrator Agent privacy scan request."""

    model_config = ConfigDict(extra="ignore")

    request_id: str = ""
    text: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrchestratorResponseSchema(BaseModel):
    """Schema for an Orchestrator Agent privacy scan response."""

    model_config = ConfigDict(extra="ignore")

    status: str = "success"
    agent: str = "PrivacyAgent"
    request_id: str = ""
    risk_score: float = 0.0
    risk_level: str = ""
    findings: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class FindingSchema(BaseModel):
    """Schema for a privacy finding."""

    model_config = ConfigDict(extra="ignore")

    severity: str
    category: str
    description: str
    entity_count: int = 0
    remediation: str = ""


class RecommendationSchema(BaseModel):
    """Schema for a privacy recommendation."""

    model_config = ConfigDict(extra="ignore")

    priority: str
    description: str
    action: str
    related_entity_types: list[str] = Field(default_factory=list)

