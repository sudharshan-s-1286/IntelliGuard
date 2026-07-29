"""Shared Models for Agent Communication."""

from typing import Any
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    """Schema for the analyze request."""

    prompt: str


class SecurityAgentResponse(BaseModel):
    """Schema for the final response of the Security Agent."""

    agent: str
    risk_score: float
    confidence: float
    severity: str
    risk_category: str
    decision: str
    findings: list[dict[str, Any]]
    attack_summary: dict[str, Any]
    explanation: str
    justification: list[str]
    recommended_action: str
    safe_prompt: str | None = None
    remediation: dict[str, Any]
