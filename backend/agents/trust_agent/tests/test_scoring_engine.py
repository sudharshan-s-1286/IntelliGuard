import pytest

from agents.trust_agent.scorer import DetectorWeightConfig, TrustScoreEngine
from shared.interfaces import DetectorSeverity, FindingDetail
from agents.trust_agent.schemas import TrustRiskLevel


def test_clean_prompt_returns_100():
    engine = TrustScoreEngine()
    result = engine.calculate([])
    
    assert result.base_score == 100.0
    assert result.total_deduction == 0.0
    assert result.risk_level == TrustRiskLevel.SAFE
    assert len(result.detector_contributions) == 0


def test_single_critical_finding():
    engine = TrustScoreEngine()
    
    finding = FindingDetail(
        detector_name="prompt_injection_detector",
        category="prompt_injection",
        severity=DetectorSeverity.CRITICAL,
        description="Ignore previous instructions",
        confidence_score=1.0,
    )
    
    result = engine.calculate([finding])
    
    # 100.0 (Base) * 1.0 (CRITICAL sev) * 1.0 (Prompt Injection Det) * 1.0 (conf) = 100.0 deduction
    assert result.total_deduction == 100.0
    assert result.risk_level == TrustRiskLevel.CRITICAL_RISK
    assert result.detector_contributions["prompt_injection_detector"] == 100.0


def test_diminishing_returns_multiple_duplicates():
    engine = TrustScoreEngine()
    
    findings = [
        FindingDetail(
            detector_name="pii_detector",
            category="pii.phone",
            severity=DetectorSeverity.MEDIUM,
            description="Found phone number",
            confidence_score=1.0,
        ) for _ in range(3)
    ]
    
    result = engine.calculate(findings)
    
    # Det Weight = 0.8, Sev Mult = 0.3
    # Base deduction for 1 = 100 * 0.3 * 0.8 * 1.0 = 24.0
    # First finding: 24.0 * (0.5^0) = 24.0
    # Second finding: 24.0 * (0.5^1) = 12.0
    # Third finding: 24.0 * (0.5^2) = 6.0
    # Total Deduction = 42.0
    
    assert result.total_deduction == 42.0
    assert result.risk_level == TrustRiskLevel.MEDIUM_RISK


def test_score_normalization_bounds():
    engine = TrustScoreEngine()
    
    findings = [
        FindingDetail(
            detector_name="prompt_injection_detector",
            category="prompt_injection",
            severity=DetectorSeverity.CRITICAL,
            description="Overwhelming attack",
            confidence_score=1.0,
        ) for _ in range(5)
    ]
    
    result = engine.calculate(findings)
    
    # Even with many critical attacks, the score should not go below 0
    assert result.base_score - result.total_deduction == 0.0
    assert result.risk_level == TrustRiskLevel.CRITICAL_RISK


def test_risk_level_mapping():
    engine = TrustScoreEngine()
    
    assert engine._map_risk_level(95.0) == TrustRiskLevel.SAFE
    assert engine._map_risk_level(80.0) == TrustRiskLevel.LOW_RISK
    assert engine._map_risk_level(60.0) == TrustRiskLevel.MEDIUM_RISK
    assert engine._map_risk_level(30.0) == TrustRiskLevel.HIGH_RISK
    assert engine._map_risk_level(10.0) == TrustRiskLevel.CRITICAL_RISK


def test_custom_detector_weights():
    # Set prompt_injection to a low weight 0.2 instead of 1.0
    custom_config = DetectorWeightConfig(weights={"prompt_injection_detector": 0.2})
    engine = TrustScoreEngine(config=custom_config)
    
    finding = FindingDetail(
        detector_name="prompt_injection_detector",
        category="prompt_injection",
        severity=DetectorSeverity.CRITICAL,
        description="Attack",
        confidence_score=1.0,
    )
    
    result = engine.calculate([finding])
    
    # 100 * 1.0 (sev) * 0.2 (det weight) = 20.0 deduction
    assert result.total_deduction == 20.0
    assert result.risk_level == TrustRiskLevel.LOW_RISK
