import pytest
from agents.compliance_agent.scorer import RiskScoringEngine

@pytest.fixture
def scorer():
    return RiskScoringEngine()

def test_evaluate_no_findings(scorer):
    result = scorer.evaluate([])
    assert result["compliance_score"] == 0
    assert result["risk_level"] == "NONE"
    assert result["decision"] == "ALLOW"

def test_evaluate_low_risk(scorer):
    # Score = 5 + 5 = 10 (<= 20)
    findings = [
        {"severity": "LOW"},
        {"severity": "Low"} # Testing case insensitivity indirectly via upper()
    ]
    result = scorer.evaluate(findings)
    assert result["compliance_score"] == 10
    assert result["risk_level"] == "LOW"
    assert result["decision"] == "WARNING"

def test_evaluate_medium_risk(scorer):
    # Score = 15 + 15 = 30 (21-50)
    findings = [
        {"severity": "MEDIUM"},
        {"severity": "MEDIUM"}
    ]
    result = scorer.evaluate(findings)
    assert result["compliance_score"] == 30
    assert result["risk_level"] == "MEDIUM"
    assert result["decision"] == "REVIEW"

def test_evaluate_high_risk(scorer):
    # Score = 40 + 25 = 65 (> 50)
    findings = [
        {"severity": "CRITICAL"},
        {"severity": "HIGH"}
    ]
    result = scorer.evaluate(findings)
    assert result["compliance_score"] == 65
    assert result["risk_level"] == "HIGH"
    assert result["decision"] == "BLOCK"

def test_evaluate_unknown_severity(scorer):
    # Score = 40 + 0 = 40 (21-50 -> REVIEW)
    findings = [
        {"severity": "CRITICAL"},
        {"severity": "UNKNOWN"}
    ]
    result = scorer.evaluate(findings)
    assert result["compliance_score"] == 40
    assert result["risk_level"] == "MEDIUM"
    assert result["decision"] == "REVIEW"

def test_evaluate_missing_severity_key(scorer):
    # Missing severity key entirely should default to 0 weight
    findings = [
        {"issue": "Something without severity"}
    ]
    result = scorer.evaluate(findings)
    assert result["compliance_score"] == 0
    assert result["risk_level"] == "NONE"
    assert result["decision"] == "ALLOW"
