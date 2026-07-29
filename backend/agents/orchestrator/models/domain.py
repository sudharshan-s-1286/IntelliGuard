"""Orchestrator domain models."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentMetadata(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    capabilities: Dict[str, Any] = {}

class AgentCapability(BaseModel):
    id: str
    description: str

class AgentHealth(BaseModel):
    status: str
    latency_ms: float
    last_check: str
    details: Dict[str, Any] = {}

class ExecutionContext(BaseModel):
    trace_id: str
    request_id: str
    metadata: Dict[str, Any] = {}

class RoutingDecision(BaseModel):
    selected_agents: List[str]
    strategy: str

class ExecutionResult(BaseModel):
    agent_name: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0

class AggregatedResponse(BaseModel):
    trace_id: str
    global_risk_score: float
    global_decision: str
    security_findings: List[Any] = []
    privacy_findings: List[Any] = []
    trust_findings: List[Any] = []
    compliance_findings: List[Any] = []
    execution_summary: Dict[str, Any] = {}
    explainability: List[str] = []

class AgentStatus(BaseModel):
    state: str
    is_active: bool
