from backend.agents.security_agent.detectors.risk_scorer import calculate_risk_score
from backend.agents.security_agent.models.domain import Finding, Threat


def test_calculate_risk_score_safe():
    findings = []
    assessment = calculate_risk_score(findings)
    assert assessment["risk_score"] == 0
    assert assessment["risk_category"] == "Safe"

def test_calculate_risk_score_critical():
    findings = [
        Finding(
            threat=Threat(category="Data Exfiltration", description=""),
            severity=1.0,
            evidence="exfiltrate",
            detector="RuleEngine",
            confidence=1.0
        ),
        Finding(
            threat=Threat(category="Prompt Injection", description=""),
            severity=1.0,
            evidence="ignore",
            detector="LLMClassifier",
            confidence=1.0
        )
    ]
    assessment = calculate_risk_score(findings)
    assert assessment["risk_score"] > 0
    assert assessment["risk_category"] in ["Dangerous", "Critical"]
