import pytest
import asyncio
from agents.compliance_agent.agent import ComplianceAgent
from shared.response_models import ComplianceCheckRequest

@pytest.fixture
def agent():
    return ComplianceAgent()

@pytest.mark.asyncio
async def test_analyze_clean_text(agent):
    text = "This is a completely clean and benign text. No issues here."
    report = await agent.analyze(ComplianceCheckRequest(text=text))
    
    assert report.status == "Compliant"
    assert report.score == 0
    assert report.risk_level == "NONE"
    assert report.decision == "ALLOW"
    assert len(report.violations) == 0
    assert len(report.recommendations) == 0

@pytest.mark.asyncio
async def test_analyze_with_pii(agent):
    text = "Please contact me at test@example.com."
    report = await agent.analyze(ComplianceCheckRequest(text=text))
    
    # Assuming Email is HIGH severity in PII detector (which gives score 25 -> REVIEW)
    assert report.score > 0
    assert report.decision in ["WARNING", "REVIEW", "BLOCK"]
    assert len(report.violations) > 0
    assert any(v["type"] == "EMAIL" for v in report.violations)
    
    assert "Mask Email" in report.recommendations

@pytest.mark.asyncio
async def test_analyze_with_critical_data(agent):
    text = "My AWS access key is AKIAFAKE123456789012 and password is 'supersecretpassword123'."
    report = await agent.analyze(ComplianceCheckRequest(text=text))
    
    # AWS key alone is 40 points (CRITICAL), Password is 25 (HIGH) if matched
    # But even with just 40 points, status is Non-Compliant. We'll check for either REVIEW or BLOCK.
    assert report.status == "Non-Compliant"
    assert report.decision in ["REVIEW", "BLOCK"]
    assert report.score >= 40
    assert report.risk_level in ["HIGH", "CRITICAL", "MEDIUM"]
    assert len(report.violations) >= 1
    
    types = [v.get("type", "") for v in report.violations]
    assert "AWS_ACCESS_KEY" in types
    
    assert "Remove API Keys" in report.recommendations

@pytest.mark.asyncio
async def test_analyze_with_policy_violation(agent):
    # Rule 001 triggers on role=guest and contains=confidential
    text = "This is a confidential document."
    context = {"role": "guest"}
    
    report = await agent.analyze(ComplianceCheckRequest(text=text), context)
    
    assert report.status == "Non-Compliant"
    # Rule 001 is HIGH severity (25 points -> REVIEW/BLOCK)
    assert report.score >= 25
    assert any(v.get("type") == "POLICY_VIOLATION" for v in report.violations)
    
    types = [v.get("type", "") for v in report.violations]
    assert "POLICY_VIOLATION" in types
