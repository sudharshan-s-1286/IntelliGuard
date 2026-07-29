"""Security Report Generator."""

from backend.agents.security_agent.models.communication import SecurityAgentResponse
from backend.agents.security_agent.models.domain import DetectionResult


class ReportGenerator:
    """Generates standardized security reports from DetectionResults."""
    
    def __init__(self, agent_version: str):
        self.agent_version = agent_version
        
    def generate(self, result: DetectionResult, original_prompt: str, was_encoded: bool) -> SecurityAgentResponse:
        """
        Convert a core DetectionResult into the standardized SecurityAgentResponse 
        expected by the broader IntelliGuard API.
        """
        # Format findings for the legacy schema
        formatted_findings = []
        for f in result.findings:
            formatted_findings.append({
                "detector": f.detector,
                "confidence": f.confidence,
                "severity": f.severity,
                "reason": f.threat.description,
                "attack": f.threat.category,
                "matched_patterns": [f.evidence] if f.evidence else []
            })
            
        # Decision Logic
        if result.risk_score.score >= 50:
            decision = "BLOCK"
            explanation = f"High risk score ({result.risk_score.score}) warrants blocking."
            justification = f"Detected {len(result.findings)} severe threats."
            recommended_action = "Reject input and flag user."
        elif result.risk_score.score > 0:
            decision = "FLAG"
            explanation = f"Suspicious activity detected (score: {result.risk_score.score})."
            justification = "Findings require manual review."
            recommended_action = "Allow but flag for human review."
        else:
            decision = "ALLOW"
            explanation = "No threats detected."
            justification = "Prompt appears safe."
            recommended_action = "Process prompt normally."

        # Merge new explanations with legacy explanation
        if result.explainability:
            explanation = explanation + "\n\nAudit Trail:\n" + "\n".join(result.explainability)
            
        # Deduplicate attack categories for summary
        attack_categories = list(set([f.threat.category for f in result.findings]))
        
        # Build the final response
        return SecurityAgentResponse(
            agent="SecurityAgent",
            risk_score=result.risk_score.score,
            confidence=0.0, # Will be set by agent.py using risk_assessment
            severity="Low", # Will be set by agent.py
            risk_category="Calculated", # This will be overridden by the caller
            decision=decision,
            findings=formatted_findings,
            attack_summary={cat: {} for cat in attack_categories}, # Mocking old structure
            explanation=explanation,
            justification=[justification],
            recommended_action=recommended_action,
            safe_prompt=original_prompt, # Remediation handles this later if hooked in
            remediation={
                "applied": False,
                "changes": [],
                "confidence": 0.0,
                "reason": "Remediation engine skipped.",
                "safe_prompt": original_prompt
            }
        )
