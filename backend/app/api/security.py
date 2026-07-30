import logging

from fastapi import APIRouter, HTTPException

from agents.security_agent.agent import (
    AgentResponse,
    AgentStatus,
    SecurityAgent,
)
from agents.security_agent.models.communication import AnalyzeRequest

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
        
    logger.warning(f"API DEBUG (1) Incoming prompt: {request.prompt}")
    logger.warning(f"API DEBUG (2) Initialized singleton agent being used: {hasattr(agent, 'semantic_detector') and agent.semantic_detector is not None}")

    # Call the standardized process() orchestration method
    result = await agent.process(request)
    
    logger.warning(f"API DEBUG (3) Raw result from agent: {result.result}")
    
    if result.status == AgentStatus.ERROR:
        # 500 Internal Server Error using the standardized error message
        raise HTTPException(status_code=500, detail=result.message)
        
    logger.warning(f"API DEBUG (4) Exact JSON sent to frontend: {result.model_dump_json()}")
        
    return result
