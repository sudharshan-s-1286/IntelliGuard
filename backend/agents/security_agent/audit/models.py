"""Audit Models.

Defines the structure of an Audit Event for structured logging and persistence.
"""
import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Represent a structured audit event."""

    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat().replace('+00:00', 'Z'))
    processing_time_ms: float
    original_prompt: str
    normalized_prompt: str
    detected_attacks: list[str]
    matched_signatures: list[str]
    risk_score: int
    confidence: float
    severity: str
    risk_category: str
    decision: str
    remediation_applied: bool
    safe_prompt: str | None
    explanation: str
    justification: list[str]
    recommended_action: str
    agent_version: str = "1.0.0"
