from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agents.trust_agent.decision import ComplianceDecision
from shared.interfaces import FindingDetail


class TrustRiskLevel(str, Enum):
    """
    Standardized categorical risk classification levels.
    """
    SAFE = "SAFE"
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL_RISK = "CRITICAL_RISK"


class ScoreExplanation(BaseModel):
    """
    Metadata explaining how the final trust score was calculated.
    """
    base_score: float = Field(default=100.0, description="Starting trust score before deductions")
    total_deduction: float = Field(..., description="Total points deducted across all findings")
    detector_contributions: Dict[str, float] = Field(
        default_factory=dict, description="Points deducted grouped by detector name"
    )
    severity_contributions: Dict[str, float] = Field(
        default_factory=dict, description="Points deducted grouped by severity level"
    )
    risk_level: TrustRiskLevel = Field(..., description="Calculated final risk level mapping")


class DetectorExplanation(BaseModel):
    """
    Detailed explanation for a specific detector's findings.
    """
    detector_name: str = Field(..., description="Name of the detector that produced the finding")
    what_was_detected: str = Field(..., description="Plain-text description of the detected entity or behavior")
    why_it_is_risky: str = Field(..., description="Explanation of the risk associated with this finding")
    score_impact: str = Field(..., description="Sentence explaining how this finding affected the trust score")


class ExplainabilityReport(BaseModel):
    """
    Human-readable explanation report of the trust analysis.
    """
    summary: str = Field(..., description="High-level human-readable summary of the analysis")
    detailed_explanation: str = Field(..., description="In-depth explanation of findings and policy triggers")
    detector_explanations: List[DetectorExplanation] = Field(
        default_factory=list, description="Breakdown of explanations per detector"
    )
    remediation_steps: List[str] = Field(
        default_factory=list, description="Actionable steps to fix the identified issues"
    )
    risk_summary: str = Field(..., description="Human-readable explanation of the calculated risk level")
    recommended_actions: List[str] = Field(
        default_factory=list, description="Policy-driven next steps (e.g., 'Requires manual review')"
    )


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
    overall_status: TrustRiskLevel = Field(
        default=TrustRiskLevel.SAFE,
        description="Aggregated risk status classification (e.g. SAFE, CRITICAL_RISK)",
    )
    compliance_decision: ComplianceDecision = Field(
        default=ComplianceDecision.ALLOW,
        description="Enforced compliance policy decision (ALLOW, ALLOW_WITH_WARNING, REVIEW, BLOCK)",
    )
    policy_id: str = Field(
        default="default-enterprise-policy",
        description="Identifier of enforced enterprise compliance policy",
    )
    trust_score: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Unified trust assessment score from 0.0 (high risk) to 100.0 (trusted)",
    )
    score_explanation: Optional[ScoreExplanation] = Field(
        default=None,
        description="Detailed metadata explaining score calculation and finding deductions",
    )
    explainability_report: Optional[ExplainabilityReport] = Field(
        default=None,
        description="Human-readable explanation of the trust analysis, decisions, and remediation steps",
    )
    findings: List[FindingDetail] = Field(
        default_factory=list,
        description="Aggregated list of findings identified across all registered detectors",
    )


"""
Dashboard Schemas — Phase 12: Analytics & Observability

Pydantic response models for all dashboard API endpoints.
All schemas are computed from AuditStore data — no external dependencies.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class RiskDistribution(BaseModel):
    """Breakdown of requests by risk level."""
    SAFE: int = Field(default=0)
    LOW_RISK: int = Field(default=0)
    MEDIUM_RISK: int = Field(default=0)
    HIGH_RISK: int = Field(default=0)
    CRITICAL_RISK: int = Field(default=0)


class DecisionDistribution(BaseModel):
    """Breakdown of requests by compliance decision."""
    ALLOW: int = Field(default=0)
    ALLOW_WITH_WARNING: int = Field(default=0)
    REVIEW: int = Field(default=0)
    BLOCK: int = Field(default=0)


# ---------------------------------------------------------------------------
# Overview endpoint schema
# ---------------------------------------------------------------------------


class OverviewResponse(BaseModel):
    """
    High-level platform health snapshot.
    Suitable for a top-of-page KPI card row in a dashboard UI.
    """
    total_requests: int = Field(..., description="Total analysis requests processed")
    total_findings: int = Field(..., description="Total findings across all requests")
    average_trust_score: float = Field(..., description="Mean trust score across all requests (0.0–100.0)")
    blocked_requests: int = Field(..., description="Requests that resulted in a BLOCK decision")
    flagged_requests: int = Field(
        ..., description="Requests with at least one finding (is_triggered across any detector)"
    )
    safe_requests: int = Field(..., description="Requests classified as SAFE")
    risk_distribution: RiskDistribution = Field(..., description="Request count by risk level")
    decision_distribution: DecisionDistribution = Field(..., description="Request count by compliance decision")
    average_processing_ms: float = Field(..., description="Mean end-to-end processing latency in milliseconds")
    generated_at: str = Field(..., description="ISO-8601 UTC timestamp when this snapshot was computed")


# ---------------------------------------------------------------------------
# Metrics endpoint schema
# ---------------------------------------------------------------------------


class TrustScoreMetrics(BaseModel):
    """Statistical distribution of trust scores across processed requests."""
    min: float = Field(..., description="Minimum trust score observed")
    max: float = Field(..., description="Maximum trust score observed")
    mean: float = Field(..., description="Arithmetic mean trust score")
    median: float = Field(..., description="Median trust score")
    p10: float = Field(..., description="10th percentile trust score")
    p90: float = Field(..., description="90th percentile trust score")


class LatencyMetrics(BaseModel):
    """Statistical distribution of end-to-end processing latency."""
    min_ms: float = Field(..., description="Minimum processing duration in ms")
    max_ms: float = Field(..., description="Maximum processing duration in ms")
    mean_ms: float = Field(..., description="Arithmetic mean duration in ms")
    median_ms: float = Field(..., description="Median duration in ms")
    p95_ms: float = Field(..., description="95th percentile duration in ms")


class FindingsMetrics(BaseModel):
    """Breakdown of findings by category prefix."""
    total: int = Field(..., description="Total finding count")
    by_category_prefix: Dict[str, int] = Field(
        default_factory=dict,
        description="Finding counts grouped by top-level category (e.g. pii, toxicity)",
    )
    by_severity: Dict[str, int] = Field(
        default_factory=dict,
        description="Finding counts grouped by severity level",
    )


class MetricsResponse(BaseModel):
    """Comprehensive statistical metrics computed over the full audit dataset."""
    total_requests: int = Field(..., description="Total requests in the dataset")
    trust_score: TrustScoreMetrics = Field(..., description="Trust score distribution statistics")
    latency: LatencyMetrics = Field(..., description="Processing latency statistics")
    findings: FindingsMetrics = Field(..., description="Findings volume and breakdown")
    generated_at: str = Field(..., description="ISO-8601 UTC timestamp when metrics were computed")


# ---------------------------------------------------------------------------
# Detectors endpoint schema
# ---------------------------------------------------------------------------


class DetectorStats(BaseModel):
    """Per-detector performance and effectiveness statistics."""
    detector_name: str = Field(..., description="Name of the detector")
    total_executions: int = Field(..., description="Number of times this detector ran")
    total_triggers: int = Field(..., description="Number of times the detector flagged a risk")
    trigger_rate: float = Field(..., description="Fraction of executions that produced a finding (0.0–1.0)")
    total_findings: int = Field(..., description="Total findings produced by this detector")
    avg_execution_ms: float = Field(..., description="Mean detector execution latency in ms")
    max_execution_ms: float = Field(..., description="Maximum detector execution latency in ms")


class DetectorsResponse(BaseModel):
    """Aggregated per-detector statistics for the entire audit dataset."""
    detectors: List[DetectorStats] = Field(default_factory=list)
    generated_at: str = Field(..., description="ISO-8601 UTC timestamp when this data was computed")


# ---------------------------------------------------------------------------
# Trends endpoint schema
# ---------------------------------------------------------------------------


class TrendBucket(BaseModel):
    """A single time-bucket entry in a trend series."""
    bucket: str = Field(..., description="Time bucket label (e.g. '2026-07-28' or '2026-07-28T10')")
    total_requests: int = Field(default=0)
    avg_trust_score: float = Field(default=0.0)
    blocked_count: int = Field(default=0)
    findings_count: int = Field(default=0)


class TrendsResponse(BaseModel):
    """Time-series trend data bucketed by hour or day."""
    granularity: str = Field(..., description="Bucket granularity: 'hour' or 'day'")
    buckets: List[TrendBucket] = Field(default_factory=list)
    generated_at: str = Field(..., description="ISO-8601 UTC timestamp when this data was computed")

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from agents.trust_agent.utils import AuditRecord, DetectorAuditEntry


class AuditListResponse(BaseModel):
    """
    Paginated list response for audit records retrieval.
    """
    total: int = Field(..., description="Total number of records matching the filter criteria")
    page: int = Field(..., description="Current 1-indexed page number")
    page_size: int = Field(..., description="Number of records per page")
    pages: int = Field(..., description="Total number of pages")
    records: List[AuditRecord] = Field(default_factory=list, description="Audit records for this page")

