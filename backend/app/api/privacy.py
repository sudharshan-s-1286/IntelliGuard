import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from agents.privacy_agent.agent import PrivacyAgent
from agents.privacy_agent.schemas import OrchestratorRequestSchema

router = APIRouter(
    prefix="/api/v1/privacy",
    tags=["Privacy Agent"],
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

agent = PrivacyAgent()


@router.get("/health")
async def privacy_health():
    """Health check for the Privacy Agent API."""
    return {"status": "healthy", "agent": "PrivacyAgent"}


@router.post("/analyze")
async def analyze_privacy(request: dict[str, Any]):
    """
    Analyze text for PII exposure using the Privacy Agent.

    Accepts:
        - text (str): The text to analyze.
        - metadata (dict, optional): Additional context metadata.
        - request_id (str, optional): Unique request identifier.
            Auto-generated if not provided.

    Returns the PrivacyAgent.run() response exactly as produced.
    """
    if not request.get("text") or not str(request.get("text")).strip():
        logger.warning("Received empty text for privacy analysis.")
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    context: dict[str, Any] = {
        "request_id": request.get("request_id") or str(uuid.uuid4()),
        "text": request.get("text", ""),
        "metadata": request.get("metadata", {}),
    }

    try:
        result = agent.run(context)
    except Exception as exc:
        logger.error("Privacy analysis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result
