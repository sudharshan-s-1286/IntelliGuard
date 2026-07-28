import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agents.trust_agent.agent import TrustAgent
from agents.trust_agent.decision import ComplianceEngine, CompliancePolicy
from agents.trust_agent.detector import (
    BiasDetector,
    HallucinationDetector,
    PIIDetector,
    PromptInjectionDetector,
    ToxicityDetector,
)
from agents.trust_agent.remediation import ExplainabilityEngine
from agents.trust_agent.scorer import TrustScoreEngine
from agents.trust_agent.schemas import (
    DetectorsResponse,
    MetricsResponse,
    OverviewResponse,
    TrendBucket,
    TrendsResponse,
    TrustAnalysisRequest,
    TrustAnalysisResponse,
)
from agents.trust_agent.utils import AuditLogger, AuditStore, DashboardService
from shared.interfaces import BaseDetector

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/trust",
    tags=["Trust"],
)


def _build_success(payload: Any) -> Dict[str, Any]:
    return {"success": True, "data": payload}


_pipeline_registered = False
_trust_agent: Optional[TrustAgent] = None
_audit_store: Optional[AuditStore] = None
_audit_logger: Optional[AuditLogger] = None
_dashboard_service: Optional[DashboardService] = None


def get_trust_agent() -> TrustAgent:
    global _pipeline_registered, _trust_agent, _audit_store, _audit_logger, _dashboard_service
    if _trust_agent is not None:
        return _trust_agent

    _audit_store = AuditStore()
    _audit_logger = AuditLogger(store=_audit_store)
    _dashboard_service = DashboardService(audit_logger=_audit_logger)

    compliance_policy = CompliancePolicy()
    trust_score_engine = TrustScoreEngine()
    explainability_engine = ExplainabilityEngine()
    compliance_engine = ComplianceEngine(policy=compliance_policy)
    _trust_agent = TrustAgent(
        compliance_engine=compliance_engine,
        trust_score_engine=trust_score_engine,
        explainability_engine=explainability_engine,
    )

    if not _pipeline_registered:
        _register_default_detectors(_trust_agent)
        _pipeline_registered = True

    _trust_agent.audit_logger = _audit_logger
    _trust_agent.dashboard_service = _dashboard_service
    return _trust_agent


def _register_default_detectors(agent: TrustAgent) -> None:
    detectors: List[BaseDetector] = [
        PromptInjectionDetector(),
        PIIDetector(),
        ToxicityDetector(),
        HallucinationDetector(),
        BiasDetector(),
    ]
    for detector in detectors:
        agent.register_detector(detector)
        logger.info(
            "Registered detector '%s' (v%s) for Trust API",
            detector.name,
            detector.version,
        )


@router.get("/health")
async def trust_health() -> Dict[str, Any]:
    """Health check for the Trust Agent API."""
    return {"status": "online", "service": "Trust Agent", "agent": "TrustAgent"}


@router.post("/analyze")
async def analyze_prompt(request: TrustAnalysisRequest) -> Dict[str, Any]:
    """
    Analyzes a prompt using the Trust Agent and returns the standardized API response.
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt cannot be empty.")

    agent = get_trust_agent()
    try:
        result: TrustAnalysisResponse = await agent.analyze(request)
        return _build_success(result.model_dump())
    except Exception as exc:
        logger.exception("Trust analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/audit")
async def get_audit_logs(
    page: int = 1,
    page_size: int = 20,
    compliance_decision: Optional[str] = None,
    overall_status: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve paginated audit records from the Trust Agent audit log."""
    agent = get_trust_agent()
    try:
        result = await agent.audit_logger.query(
            compliance_decision=compliance_decision,
            overall_status=overall_status,
            page=page,
            page_size=page_size,
        )
        return _build_success(result)
    except Exception as exc:
        logger.exception("Audit query failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/dashboard/overview")
async def dashboard_overview() -> Dict[str, Any]:
    """Return platform KPI overview snapshot for the dashboard."""
    agent = get_trust_agent()
    try:
        overview: OverviewResponse = await agent.dashboard_service.get_overview()
        return _build_success(overview.model_dump())
    except Exception as exc:
        logger.exception("Dashboard overview failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/dashboard/metrics")
async def dashboard_metrics() -> Dict[str, Any]:
    """Return detailed statistical metrics for the dashboard."""
    agent = get_trust_agent()
    try:
        metrics: MetricsResponse = await agent.dashboard_service.get_metrics()
        return _build_success(metrics.model_dump())
    except Exception as exc:
        logger.exception("Dashboard metrics failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/dashboard/detectors")
async def dashboard_detectors() -> Dict[str, Any]:
    """Return per-detector performance statistics."""
    agent = get_trust_agent()
    try:
        stats: DetectorsResponse = await agent.dashboard_service.get_detector_stats()
        return _build_success(stats.model_dump())
    except Exception as exc:
        logger.exception("Dashboard detectors failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get("/dashboard/trends")
async def dashboard_trends(granularity: str = "hour") -> Dict[str, Any]:
    """Return time-series trend data bucketed by hour or day."""
    agent = get_trust_agent()
    try:
        trends: TrendsResponse = await agent.dashboard_service.get_trends(granularity=granularity)
        return _build_success(trends.model_dump())
    except Exception as exc:
        logger.exception("Dashboard trends failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
