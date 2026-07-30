"""Risk Assessment Engine.

Enterprise-grade Risk Assessment Engine. Calculates comprehensive risk score,
severity, confidence, risk category, and attack summary based on Findings.
"""
from agents.security_agent.config.settings import (
    ATTACK_WEIGHTS,
    PENALTY_ENCODED_PAYLOAD,
    MULTI_ATTACK_FAMILY_WEIGHT,
    OWASP_MATCH_WEIGHT,
    SEMANTIC_SIMILARITY_WEIGHT,
    RULE_MATCH_WEIGHT,
    RISK_THRESHOLDS,
)
from agents.security_agent.models.domain import Finding


def calculate_attack_weight(finding: Finding) -> float:
    """Calculate the weighted contribution of a single attack."""
    base_weight = ATTACK_WEIGHTS.get(finding.threat.category, 20)
    
    # Base calculation
    weight = base_weight * finding.confidence
    
    # Apply configured multipliers based on semantic/rule matches
    if finding.detector == "RuleEngine":
        weight *= RULE_MATCH_WEIGHT
    elif finding.detector == "SemanticDetector":
        # Semantic only
        if finding.metadata:
            similarity = finding.metadata.get("similarity_score", 1.0)
            weight *= (similarity * SEMANTIC_SIMILARITY_WEIGHT)
    elif finding.detector == "Merged":
        # Both rule and semantic
        weight *= RULE_MATCH_WEIGHT
        if finding.metadata:
            similarity = finding.metadata.get("similarity_score", 1.0)
            weight *= (similarity * SEMANTIC_SIMILARITY_WEIGHT)
            
    # Apply OWASP mapping weight if available
    if finding.metadata and finding.metadata.get("owasp_mapping") and finding.metadata.get("owasp_mapping") != "Unknown":
        weight *= OWASP_MATCH_WEIGHT
        
    # LLM Classifier context
    if finding.detector == "LLMClassifier":
        weight *= 1.2
        
    return weight

def calculate_confidence(findings: list[Finding]) -> float:
    """Calculate an overall confidence score based on individual detection confidences."""
    if not findings:
        return 0.0
    return round(sum(f.confidence for f in findings) / len(findings), 2)

def generate_attack_summary(findings: list[Finding]) -> dict:
    """Generate a summary of which attacks contributed most to the score."""
    summary = {}
    for finding in findings:
        summary[finding.threat.category] = {
            "confidence": finding.confidence,
            "detector": finding.detector,
            "severity": finding.severity
        }
    # Sort by confidence descending
    sorted_summary = dict(sorted(summary.items(), key=lambda item: item[1]["confidence"], reverse=True))
    return sorted_summary

def calculate_severity(risk_score: float) -> str:
    """Calculate the severity string based on the final risk score."""
    if risk_score <= RISK_THRESHOLDS["SAFE"]:
        return "Low"
    elif risk_score <= RISK_THRESHOLDS["SUSPICIOUS"]:
        return "Medium"
    elif risk_score <= RISK_THRESHOLDS["DANGEROUS"]:
        return "High"
    else:
        return "Critical"

def get_risk_category(risk_score: float) -> str:
    """Determine the risk category (Safe, Suspicious, Dangerous, Critical)."""
    if risk_score <= RISK_THRESHOLDS["SAFE"]:
        return "Safe"
    elif risk_score <= RISK_THRESHOLDS["SUSPICIOUS"]:
        return "Suspicious"
    elif risk_score <= RISK_THRESHOLDS["DANGEROUS"]:
        return "Dangerous"
    else:
        return "Critical"

def calculate_risk_score(findings: list[Finding], was_encoded: bool = False, was_multi_step: bool = False) -> dict:
    """Provide the main entry point for the Risk Assessment Engine.

    Args:
        findings (List[Finding]): Detected attacks and their metadata.
        was_encoded (bool): True if the payload was obfuscated/encoded.
        was_multi_step (bool): True if it was a multi-step payload.

    Returns:
        dict: Assessment results including score, severity, category, confidence, and summary.
    """
    raw_score = 0.0
    detected_count = len(findings)

    # Calculate base score from individual attacks
    for finding in findings:
        raw_score += calculate_attack_weight(finding)

    # Apply multipliers and penalties for multiple attack families
    if detected_count > 1:
        raw_score *= MULTI_ATTACK_FAMILY_WEIGHT

    if was_encoded:
        raw_score += PENALTY_ENCODED_PAYLOAD

    if was_multi_step:
        raw_score *= 1.1

    # Cap score at 100
    final_score = min(int(raw_score), 100)

    overall_confidence = calculate_confidence(findings)
    severity = calculate_severity(final_score)
    category = get_risk_category(final_score)
    summary = generate_attack_summary(findings)

    return {
        "risk_score": final_score,
        "severity": severity,
        "confidence": overall_confidence,
        "risk_category": category,
        "attack_summary": summary
    }
