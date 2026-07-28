from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, UTC
from .enums import AgentStatus

class AgentResponse(BaseModel):
    """
    Standardized response model for all IntelliGuard agents.
    Wraps the specific agent's execution payload inside the `result` field.
    """
    agent: str
    status: AgentStatus
    version: str
    processing_time_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat().replace('+00:00', 'Z'))
    result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
