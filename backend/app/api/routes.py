from fastapi import APIRouter, Depends
from shared.response_models import ComplianceCheckRequest, ComplianceCheckResponse
from agents.compliance_agent.agent import ComplianceAgent
from app.api.deps import get_compliance_agent

router = APIRouter()

@router.get("/health", tags=["Health"], response_model=dict)
async def health_check(agent: ComplianceAgent = Depends(get_compliance_agent)) -> dict:
    """
    Checks the status of the service.
    Returns status: ok if service is active.
    """
    health = agent.health()
    return {"status": health["status"], "service": "IntelliGuard Compliance Agent", "ready": agent.is_ready()}

@router.post(
    "/api/compliance/check",
    response_model=ComplianceCheckResponse,
    tags=["Compliance"],
)
async def check_compliance(
    request: ComplianceCheckRequest,
    agent: ComplianceAgent = Depends(get_compliance_agent),
) -> ComplianceCheckResponse:
    """
    Evaluates input text against compliance policies.
    Returns a comprehensive compliance scan summary and findings.
    """
    return await agent.analyze(request)
