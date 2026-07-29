from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.security_agent.detectors.decision_engine import DecisionEngine
from backend.agents.security_agent.detectors.semantic_detector import SemanticDetector
from backend.agents.security_agent.models.domain import Finding, Threat


@pytest.fixture
def semantic_detector():
    detector = MagicMock(spec=SemanticDetector)
    detector.evaluate = AsyncMock(return_value=[])
    return detector

@pytest.fixture
def decision_engine(semantic_detector):
    engine = DecisionEngine(semantic_detector)
    # Ensure default configurations for tests
    engine.llm_routing_threshold = 0.6
    engine.fusion_strategy = "max"
    engine.route_on_conflict = True
    return engine

@pytest.mark.asyncio
@patch('backend.agents.security_agent.detectors.decision_engine.run_all_detectors')
async def test_decision_engine_no_findings(mock_run_all, decision_engine):
    # Rule engine finds nothing
    mock_run_all.return_value = {
        "prompt_injection": {"detected": False}
    }
    # Semantic detector finds nothing (default fixture)
    
    result = await decision_engine.analyze("hello")
    assert not result.routing.needs_llm
    assert len(result.findings) == 0

@pytest.mark.asyncio
@patch('backend.agents.security_agent.detectors.decision_engine.run_all_detectors')
async def test_decision_engine_routing_low_confidence(mock_run_all, decision_engine, semantic_detector):
    # Rule engine returns a low confidence finding
    mock_run_all.return_value = {
        "prompt_injection": {
            "attack": "Prompt Injection",
            "detected": True,
            "severity": "LOW",
            "confidence": 0.4,
            "reason": "Suspicious pattern",
            "matched_patterns": ["ignore"]
        }
    }
    # Semantic detector finds nothing
    
    result = await decision_engine.analyze("test")
    # Threshold is 0.6, so max confidence (0.4) should trigger LLM
    assert result.routing.needs_llm is True
    assert "below routing threshold" in result.routing.reason

@pytest.mark.asyncio
@patch('backend.agents.security_agent.detectors.decision_engine.run_all_detectors')
async def test_decision_engine_duplicate_resolution(mock_run_all, decision_engine, semantic_detector):
    # Rule Engine finds Prompt Injection
    mock_run_all.return_value = {
        "prompt_injection": {
            "attack": "Prompt Injection",
            "detected": True,
            "severity": "HIGH",
            "confidence": 0.85,
            "reason": "Rule match",
            "matched_patterns": ["test_pattern"]
        }
    }
    
    # Semantic Detector finds Prompt Injection too
    sem_finding = Finding(
        threat=Threat(category="Prompt Injection", description="Semantic match"),
        severity=1.0, # CRITICAL
        evidence="Pattern ID: 123",
        detector="SemanticDetector",
        confidence=0.95
    )
    semantic_detector.evaluate = AsyncMock(return_value=[sem_finding])
    
    result = await decision_engine.analyze("test")
    
    # Should resolve into exactly 1 finding
    assert len(result.findings) == 1
    f = result.findings[0]
    
    # Assert merged properties
    assert f.threat.category == "Prompt Injection"
    assert f.detector == "Merged"
    assert f.confidence == 0.95  # max strategy
    assert f.severity == 1.0     # max severity
    assert "test_pattern" in f.evidence
    assert "Pattern ID: 123" in f.evidence

@pytest.mark.asyncio
@patch('backend.agents.security_agent.detectors.decision_engine.run_all_detectors')
async def test_decision_engine_conflict_routing(mock_run_all, decision_engine, semantic_detector):
    # Rule Engine finds nothing
    mock_run_all.return_value = {
        "prompt_injection": {"detected": False}
    }
    
    # Semantic Detector finds a High severity threat
    sem_finding = Finding(
        threat=Threat(category="Data Exfiltration", description="Semantic match"),
        severity=0.9, # High severity
        evidence="Pattern ID: 99",
        detector="SemanticDetector",
        confidence=0.95 # High confidence (bypasses threshold check)
    )
    semantic_detector.evaluate = AsyncMock(return_value=[sem_finding])
    
    result = await decision_engine.analyze("test")
    
    # Should trigger LLM due to conflict (Semantic found High severity, Rule found nothing)
    assert result.routing.needs_llm is True
    assert "Conflict: SemanticDetector found high-severity" in result.routing.reason
