import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RiskScoringEngine:
    """
    Engine to aggregate findings and calculate the overall Compliance Score,
    Risk Level, and Actionable Decision.
    """

    SEVERITY_WEIGHTS = {
        "CRITICAL": 40,
        "HIGH": 25,
        "MEDIUM": 15,
        "LOW": 5
    }

    def evaluate(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates risk based on all detector findings.
        
        Args:
            findings: List of dictionary findings, each containing at least a 'severity' key.
            
        Returns:
            Dictionary containing 'compliance_score', 'risk_level', and 'decision'.
        """
        score = 0
        
        for finding in findings:
            severity = str(finding.get("severity", "")).upper()
            weight = self.SEVERITY_WEIGHTS.get(severity, 0)
            score += weight

        if score == 0:
            risk_level = "NONE"
            decision = "ALLOW"
        elif score <= 20:
            risk_level = "LOW"
            decision = "WARNING"
        elif score <= 50:
            risk_level = "MEDIUM"
            decision = "REVIEW"
        else:
            risk_level = "HIGH"
            decision = "BLOCK"
            
        logger.info(f"Risk Evaluation - Score: {score}, Level: {risk_level}, Decision: {decision}")
            
        return {
            "compliance_score": score,
            "risk_level": risk_level,
            "decision": decision
        }
