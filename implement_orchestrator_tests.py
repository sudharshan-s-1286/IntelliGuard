import os
from pathlib import Path

BASE_DIR = Path("/home/pranav/Desktop/IntelliGaurd/backend/agents/orchestrator")

def implement_tests():
    test_content = '''import pytest
import asyncio
from typing import Any, Dict
from backend.shared.interfaces import BaseAgent
from backend.shared.response_models import AgentResponse
from backend.agents.orchestrator.agent import OrchestratorAgent
from backend.agents.orchestrator.utils.context import ContextManager
from backend.agents.orchestrator.config import settings

# --- Mocks ---

class MockBaseAgent(BaseAgent):
    def __init__(self, name="mock", should_timeout=False, should_fail=False):
        self._name = name
        self.should_timeout = should_timeout
        self.should_fail = should_fail
        
    def process(self, request: Any) -> AgentResponse:
        if self.should_fail:
            raise ValueError("Intentional Failure")
        if self.should_timeout:
            import time
            time.sleep(2) # Sleep longer than timeout
        return AgentResponse(
            agent=self._name,
            status="SUCCESS",
            version="1.0",
            processing_time_ms=10.0,
            result={"risk_score": 0.5, "decision": "ALLOW", "findings": []}
        )
        
    def health(self) -> Dict[str, Any]:
        return {"status": "healthy"}
        
    def ready(self) -> Dict[str, Any]:
        return {"ready": True}
        
    def version(self) -> str:
        return "1.0.0"
        
    def capabilities(self) -> Dict[str, Any]:
        return {"scan": True}
        
    def metrics(self) -> Dict[str, Any]:
        return {}


# --- Tests ---

@pytest.mark.asyncio
async def test_agent_registry():
    agent = OrchestratorAgent()
    mock_agent = MockBaseAgent("security")
    agent.registry.register("security", mock_agent)
    
    assert "security" in agent.registry.list_agents()
    
    meta = agent.registry.get_metadata("security")
    assert meta.name == "security"
    assert meta.version == "1.0.0"
    assert meta.capabilities["scan"] is True
    
    retrieved = agent.registry.get_agent("security")
    assert retrieved is mock_agent
    
    agent.registry.deregister("security")
    assert "security" not in agent.registry.list_agents()

@pytest.mark.asyncio
async def test_agent_discovery():
    agent = OrchestratorAgent()
    # It should discover the actual SecurityAgent if it's there, but we won't assert exact numbers
    discovered = agent.discovery.discover_agents()
    assert isinstance(discovered, list)
    # The real system has 'security_agent' in backend.agents
    # so we expect at least 'security_agent' to be discovered.

@pytest.mark.asyncio
async def test_context_propagation():
    cm = ContextManager()
    ctx1 = cm.create_context({"user": "admin"})
    
    assert ctx1.trace_id is not None
    assert ctx1.metadata["user"] == "admin"
    
    ctx2 = cm.get_context()
    assert ctx2.trace_id == ctx1.trace_id

@pytest.mark.asyncio
async def test_router():
    agent = OrchestratorAgent()
    agent.registry.register("security_agent", MockBaseAgent("security_agent"))
    agent.registry.register("privacy_agent", MockBaseAgent("privacy_agent"))
    
    # Test metadata-based routing rule
    route_sec = agent.router.determine_route("req", {"mode": "security_only"})
    assert "security_agent" in route_sec.selected_agents
    assert "privacy_agent" not in route_sec.selected_agents
    
    route_all = agent.router.determine_route("req", {})
    assert "security_agent" in route_all.selected_agents
    assert "privacy_agent" in route_all.selected_agents

@pytest.mark.asyncio
async def test_scheduler_success():
    agent = OrchestratorAgent()
    mock_agent = MockBaseAgent("test")
    agent_map = {"test": mock_agent}
    
    results = await agent.scheduler.schedule(agent_map, "req")
    assert len(results) == 1
    assert results[0].status == "SUCCESS"
    assert results[0].data["result"]["risk_score"] == 0.5

@pytest.mark.asyncio
async def test_scheduler_timeout_and_fault_tolerance():
    agent = OrchestratorAgent()
    settings.AGENT_TIMEOUT = 1 # 1 second timeout
    settings.RETRY_COUNT = 1
    
    # Mock timeout agent
    bad_agent = MockBaseAgent("bad", should_timeout=True)
    good_agent = MockBaseAgent("good")
    
    agent_map = {"bad": bad_agent, "good": good_agent}
    
    results = await agent.scheduler.schedule(agent_map, "req")
    
    # Assert graceful degradation: good succeeds, bad errors
    bad_res = next(r for r in results if r.agent_name == "bad")
    good_res = next(r for r in results if r.agent_name == "good")
    
    assert good_res.status == "SUCCESS"
    assert bad_res.status == "ERROR"
    assert "Max retries exceeded" in bad_res.error

@pytest.mark.asyncio
async def test_aggregation():
    agent = OrchestratorAgent()
    
    from backend.agents.orchestrator.models.domain import ExecutionResult
    results = [
        ExecutionResult(agent_name="sec", status="SUCCESS", data={"result": {"risk_score": 0.8, "decision": "BLOCK", "findings": ["A"]}}),
        ExecutionResult(agent_name="priv", status="SUCCESS", data={"result": {"risk_score": 0.2, "decision": "ALLOW", "findings": ["B"]}}),
        ExecutionResult(agent_name="fail", status="ERROR", error="Timeout")
    ]
    
    agg = agent.aggregator.aggregate(results)
    
    assert agg.global_risk_score == 0.8
    assert agg.global_decision == "BLOCK"
    assert "A" in agg.security_findings
    assert "B" in agg.security_findings
    assert agg.execution_summary["fail"]["status"] == "ERROR"

@pytest.mark.asyncio
async def test_health_monitor():
    agent = OrchestratorAgent()
    agent.registry.register("mock", MockBaseAgent())
    
    health = agent.health()
    assert health["status"] == "healthy"
    assert "mock" in health["agents"]
    assert health["agents"]["mock"]["status"] == "healthy"

@pytest.mark.asyncio
async def test_full_pipeline():
    agent = OrchestratorAgent()
    agent.registry.register("sec", MockBaseAgent("sec"))
    agent.registry.register("priv", MockBaseAgent("priv"))
    
    # Override router just for this test
    agent.router.determine_route = lambda req, meta: __import__('backend.agents.orchestrator.models.domain', fromlist=['RoutingDecision']).RoutingDecision(selected_agents=["sec", "priv"], strategy="parallel")
    
    response = await agent.process("hello", metadata={})
    
    assert response.global_risk_score == 0.5
    assert response.global_decision == "ALLOW"
    assert "sec" in response.execution_summary
    assert "priv" in response.execution_summary
    assert response.execution_summary["sec"]["status"] == "SUCCESS"
'''
    (BASE_DIR / "tests" / "test_orchestrator.py").write_text(test_content)

if __name__ == "__main__":
    implement_tests()
    print("Tests generated.")
