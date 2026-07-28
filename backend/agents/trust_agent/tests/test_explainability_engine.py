import pytest

from agents.trust_agent.decision import ComplianceDecision
from agents.trust_agent.remediation import ExplainabilityEngine, ExplanationTemplateConfig
from shared.interfaces import DetectorSeverity, FindingDetail
from agents.trust_agent.schemas import ScoreExplanation, TrustRiskLevel


def test_explainability_clean_prompt():
    engine = ExplainabilityEngine()
    
    score_exp = ScoreExplanation(
        base_score=100.0,
        total_deduction=0.0,
        detector_contributions={},
        severity_contributions={},
        risk_level=TrustRiskLevel.SAFE
    )
    
    report = engine.generate_report(
        findings=[],
        score_explanation=score_exp,
        compliance_decision=ComplianceDecision.ALLOW,
        policy_id="default-enterprise-policy"
    )
    
    assert report.summary == "Analysis complete: No risks found. Decision is ALLOW."
    assert "cleanly passed" in report.detailed_explanation
    assert len(report.detector_explanations) == 0
    assert report.remediation_steps == ["No remediation required."]
    assert report.recommended_actions == ["Proceed with standard processing."]


def test_explainability_single_finding():
    engine = ExplainabilityEngine()
    
    finding = FindingDetail(
        detector_name="prompt_injection_detector",
        category="prompt_injection.override",
        severity=DetectorSeverity.CRITICAL,
        description="Ignore instructions",
        confidence_score=0.9,
    )
    
    score_exp = ScoreExplanation(
        base_score=100.0,
        total_deduction=90.0,
        detector_contributions={"prompt_injection_detector": 90.0},
        severity_contributions={"CRITICAL": 90.0},
        risk_level=TrustRiskLevel.CRITICAL_RISK
    )
    
    report = engine.generate_report(
        findings=[finding],
        score_explanation=score_exp,
        compliance_decision=ComplianceDecision.BLOCK,
        policy_id="default-enterprise-policy"
    )
    
    assert "1 finding(s) detected resulting in a CRITICAL_RISK" in report.summary
    assert "reduced by 90.0 points" in report.detailed_explanation
    assert "prompt_injection_detector" in report.detailed_explanation
    assert len(report.detector_explanations) == 1
    
    det_exp = report.detector_explanations[0]
    assert det_exp.detector_name == "prompt_injection_detector"
    assert "prompt_injection.override" in det_exp.what_was_detected
    assert "immediate and severe threat" in det_exp.why_it_is_risky
    assert "reduced the overall trust score by 90.0" in det_exp.score_impact
    
    assert any("Sanitize user inputs" in s for s in report.remediation_steps)
    assert any("Halt processing immediately" in s for s in report.recommended_actions)


def test_explainability_multiple_findings():
    engine = ExplainabilityEngine()
    
    f1 = FindingDetail(
        detector_name="pii_detector",
        category="pii.email",
        severity=DetectorSeverity.MEDIUM,
        description="Found email",
        confidence_score=1.0,
    )
    f2 = FindingDetail(
        detector_name="toxicity_detector",
        category="toxicity.profanity",
        severity=DetectorSeverity.LOW,
        description="Found profanity",
        confidence_score=0.8,
    )
    
    score_exp = ScoreExplanation(
        base_score=100.0,
        total_deduction=30.0,
        detector_contributions={"pii_detector": 24.0, "toxicity_detector": 6.0},
        severity_contributions={"MEDIUM": 24.0, "LOW": 6.0},
        risk_level=TrustRiskLevel.LOW_RISK
    )
    
    report = engine.generate_report(
        findings=[f1, f2],
        score_explanation=score_exp,
        compliance_decision=ComplianceDecision.ALLOW_WITH_WARNING,
        policy_id="default-enterprise-policy"
    )
    
    assert "2 finding(s) detected" in report.summary
    assert len(report.detector_explanations) == 2
    assert len(report.remediation_steps) == 2


def test_custom_explanation_template():
    custom_config = ExplanationTemplateConfig(
        risk_summaries={TrustRiskLevel.SAFE: "All good!"},
        decision_recommendations={ComplianceDecision.ALLOW: ["Go ahead."]}
    )
    engine = ExplainabilityEngine(config=custom_config)
    
    score_exp = ScoreExplanation(
        base_score=100.0,
        total_deduction=0.0,
        detector_contributions={},
        severity_contributions={},
        risk_level=TrustRiskLevel.SAFE
    )
    
    report = engine.generate_report(
        findings=[],
        score_explanation=score_exp,
        compliance_decision=ComplianceDecision.ALLOW,
        policy_id="default-enterprise-policy"
    )
    
    assert report.risk_summary == "All good!"
    assert report.recommended_actions == ["Go ahead."]
