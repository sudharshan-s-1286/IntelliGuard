from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.detectors.base import FindingDetail


class TrustAnalysisRequest(BaseModel):
    """
    Input request schema for Trust Agent analysis.
    """

    prompt: str = Field(
        ...,
        min_length=1,
        description="Target text prompt or payload to analyze for trust, security, and safety compliance",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional contextual metadata (e.g. user_id, session_id, model_name)",
    )


class TrustAnalysisResponse(BaseModel):
    """
    Output payload schema produced by Trust Agent analysis orchestration.
    """

    request_id: str = Field(..., description="Unique request context tracking identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Analysis completion UTC timestamp",
    )
    overall_status: str = Field(
        default="SAFE",
        description="Aggregated risk status classification (e.g. SAFE, RISK_DETECTED)",
    )
    trust_score: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Unified trust assessment score from 0.0 (high risk) to 100.0 (trusted)",
    )
    findings: List[FindingDetail] = Field(
        default_factory=list,
        description="Aggregated list of findings identified across all registered detectors",
    )
