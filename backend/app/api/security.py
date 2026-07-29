import time
import logging
from fastapi import APIRouter, HTTPException

from agents.security_agent.agent import SecurityAgent
from agents.security_agent.schemas import AnalyzeRequest
from shared.response_models import AgentResponse
from shared.enums import AgentStatus

router = APIRouter(
    prefix="/api/security",
    tags=["Security"]
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Initialize Security Agent
agent = SecurityAgent()

@router.get("/health")
async def security_health():
    """Health check for the Security Agent API."""
    # Use the standardized health interface
    return agent.health()

@router.post("/analyze", response_model=AgentResponse)
async def analyze_prompt(request: AnalyzeRequest):
    """
    Analyzes a prompt using the Security Agent and returns the standard AgentResponse.
    """
    if not request.prompt or not request.prompt.strip():
        logger.warning("Received an empty prompt for analysis.")
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # Call the standardized process() orchestration method
    result = await agent.process(request)
    
    if result.status == AgentStatus.ERROR:
        # 500 Internal Server Error using the standardized error message
        raise HTTPException(status_code=500, detail=result.message)
        
    return result
