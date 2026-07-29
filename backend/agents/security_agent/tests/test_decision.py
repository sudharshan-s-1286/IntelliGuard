import pytest
from backend.agents.security_agent.detectors.decision_engine import make_decision

@pytest.mark.asyncio
async def test_make_decision_allow():
    assessment = {
        "risk_score": 10,
        "confidence": 0.1,
        "severity": "Low",
        "risk_category": "Safe",
        "attack_summary": {}
    }
    decision = make_decision(assessment)
    assert decision["decision"] == "ALLOW"
    assert "safe" in decision["explanation"].lower()

@pytest.mark.asyncio
async def test_make_decision_block():
    assessment = {
        "risk_score": 90,
        "confidence": 0.9,
        "severity": "Critical",
        "risk_category": "Critical",
        "attack_summary": {"Prompt Injection": {"confidence": 0.9, "signatures_matched": 1}}
    }
    decision = make_decision(assessment)
    assert decision["decision"] == "BLOCK"
    assert "reject" in decision["recommended_action"].lower()
