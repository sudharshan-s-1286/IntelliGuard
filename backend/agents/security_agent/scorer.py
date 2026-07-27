"""Risk Assessment Engine.

Enterprise-grade Risk Assessment Engine. Calculates comprehensive risk score,
severity, confidence, risk category, and attack summary based on findings.
"""
from .config import (
    ATTACK_WEIGHTS,
    PENALTY_ENCODED_PAYLOAD,
    PENALTY_MULTI_ATTACK_MULTIPLIER,
    RISK_THRESHOLDS,
)


def calculate_attack_weight(attack_name: str, confidence: float) -> float:
    """Calculate the weighted contribution of a single attack."""
    base_weight = ATTACK_WEIGHTS.get(attack_name, 20)
    return base_weight * confidence

def calculate_confidence(findings: dict) -> float:
    """Calculate an overall confidence score based on individual detection confidences."""
    confidences = [f["confidence"] for f in findings.values() if f["detected"]]
    if not confidences:
        return 0.0
    return round(sum(confidences) / len(confidences), 2)

def generate_attack_summary(findings: dict) -> dict:
    """Generate a summary of which attacks contributed most to the score."""
    summary = {}
    for finding in findings.values():
        if finding["detected"]:
            summary[finding["attack"]] = {
                "confidence": finding["confidence"],
                "signatures_matched": len(finding.get("matched_patterns", []))
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

def calculate_risk_score(findings: dict) -> dict:
    """Provide the main entry point for the Risk Assessment Engine.
    
    Args:
        findings (dict): Detected attacks and their metadata.
        
    Returns:
        dict: Assessment results including score, severity, category, confidence, and summary.

    """
    raw_score = 0.0
    detected_count = 0
    has_encoded = findings.get("encoding", {}).get("detected", False)
    has_multi = findings.get("multi_step", {}).get("detected", False)
    
    # Calculate base score from individual attacks
    for finding in findings.values():
        if finding["detected"]:
            detected_count += 1
            raw_score += calculate_attack_weight(finding["attack"], finding["confidence"])
            
    # Apply multipliers and penalties
    if detected_count > 1:
        raw_score *= PENALTY_MULTI_ATTACK_MULTIPLIER
        
    if has_encoded:
        raw_score += PENALTY_ENCODED_PAYLOAD
        
    if has_multi:
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
