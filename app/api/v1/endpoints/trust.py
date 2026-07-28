from fastapi import APIRouter, Depends, status

from app.agents.trust_agent import TrustAgent
from app.api.deps import get_request_id, get_trust_agent
from app.schemas.base import APIResponse
from app.schemas.trust import TrustAnalysisRequest, TrustAnalysisResponse

router = APIRouter()


@router.post(
    "/analyze",
    response_model=APIResponse[TrustAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Analyze Prompt Trust",
    description="Orchestrates trust analysis pipeline against prompt payload across registered detectors.",
)
async def analyze_prompt_trust(
    request_payload: TrustAnalysisRequest,
    request_id: str = Depends(get_request_id),
    trust_agent: TrustAgent = Depends(get_trust_agent),
) -> APIResponse[TrustAnalysisResponse]:
    """
    Executes Trust Agent orchestration pipeline for an incoming prompt request.
    """
    analysis_result = await trust_agent.analyze(
        request=request_payload,
        request_id=request_id,
    )
    return APIResponse.ok(data=analysis_result)
