import pytest
from backend.agents.security_agent.agent import SecurityAgent
from shared.enums import AgentStatus

@pytest.mark.asyncio
async def test_audit_logger_failure(monkeypatch):
    agent = SecurityAgent()
    # Force audit logger to raise an exception
    def mock_save(*args, **kwargs):
        raise Exception("Storage full")
    
    monkeypatch.setattr(agent.audit_logger.storage, "save", mock_save)
    
    request = type('Request', (), {'prompt': "Hello world!"})
    # Agent should not crash, it should gracefully swallow the audit error
    response = await agent.process(request)
    assert response.status == AgentStatus.SUCCESS

@pytest.mark.asyncio
async def test_detector_failure(monkeypatch):
    agent = SecurityAgent()
    def mock_run_all(*args, **kwargs):
        raise Exception("Detector crashed")
    
    import backend.agents.security_agent.agent
    monkeypatch.setattr(backend.agents.security_agent.agent, "run_all_detectors", mock_run_all)
    
    request = type('Request', (), {'prompt': "Hello world!"})
    # Agent process wrapper should catch it and return standard ERROR payload
    response = await agent.process(request)
    assert response.status == AgentStatus.ERROR
    assert response.error_code == "SECURITY_ANALYSIS_FAILED"
    assert "Detector crashed" in response.message
