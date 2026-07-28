import pytest
from agents.privacy_agent.agent import PrivacyAgent

def test_full_pipeline_safe():
    agent = PrivacyAgent()
    response = agent.run({"text": "Hello world!", "metadata": {}})
    
    assert response["status"] == "success"
    assert response["agent"] == "PrivacyAgent"
    assert response["risk_level"] == "low"

def test_full_pipeline_with_pii():
    agent = PrivacyAgent()
    response = agent.run({
        "text": "My SSN is 123-45-6789 and email is john@example.com",
        "metadata": {}
    })
    
    assert response["status"] == "success"
    assert response["agent"] == "PrivacyAgent"
    assert response["risk_score"] > 0
    assert len(response["findings"]) > 0
