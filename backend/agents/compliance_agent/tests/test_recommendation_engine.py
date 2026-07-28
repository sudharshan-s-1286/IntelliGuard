import pytest
from agents.compliance_agent.remediation import RecommendationEngine

@pytest.fixture
def engine():
    return RecommendationEngine()

def test_generate_recommendations_email(engine):
    findings = [{"type": "EMAIL", "severity": "HIGH"}]
    recs = engine.generate_recommendations(findings)
    assert "Mask Email" in recs
    assert "Request Human Review" in recs

def test_generate_recommendations_medical(engine):
    findings = [{"category": "MEDICAL_INFORMATION", "severity": "MEDIUM"}]
    recs = engine.generate_recommendations(findings)
    assert "Redact Medical Information" in recs
    assert "Request Human Review" not in recs

def test_generate_recommendations_api_keys(engine):
    findings = [{"type": "API_KEY", "severity": "CRITICAL"}]
    recs = engine.generate_recommendations(findings)
    assert "Remove API Keys" in recs
    assert "Request Human Review" in recs

def test_deduplication(engine):
    findings = [
        {"type": "EMAIL", "severity": "MEDIUM"},
        {"type": "EMAIL", "severity": "LOW"},
        {"type": "API_KEY", "severity": "HIGH"}
    ]
    recs = engine.generate_recommendations(findings)
    assert len(recs) == 3
    assert "Mask Email" in recs
    assert "Remove API Keys" in recs
    assert "Request Human Review" in recs

def test_fallback_for_unknown_high_severity(engine):
    findings = [{"type": "UNKNOWN_WEIRD_THING", "severity": "HIGH"}]
    recs = engine.generate_recommendations(findings)
    assert "Remove Confidential Text" in recs
    assert "Request Human Review" in recs

def test_human_review_forced_by_decision(engine):
    findings = [{"type": "UNKNOWN_WEIRD_THING", "severity": "LOW"}]
    recs = engine.generate_recommendations(findings, risk_decision="REVIEW")
    assert "Request Human Review" in recs
    # Low severity shouldn't trigger "Remove Confidential Text" fallback
    assert "Remove Confidential Text" not in recs

def test_no_recommendations_for_clean_input(engine):
    recs = engine.generate_recommendations([], risk_decision="ALLOW")
    assert len(recs) == 0
