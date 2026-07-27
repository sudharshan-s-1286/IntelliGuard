"""Decision Engine Module.

Explainable decision engine. Determines action (ALLOW, WARN, MODIFY, BLOCK)
based on the assessment, and provides clear XAI justifications and recommended actions.
"""
from .config import DECISION_THRESHOLDS


def make_decision(assessment: dict) -> dict:
    """Determine the action to take based on the full risk assessment.
    
    Args:
        assessment (dict): The output from the scorer module.
        
    Returns:
        dict: The decision, explanation, justification, and recommended action.

    """
    risk_score = assessment["risk_score"]
    summary = assessment["attack_summary"]
    
    # Generate XAI justifications
    justification = []
    for attack, details in summary.items():
        justification.append(f"{attack} detected with {details['confidence']} confidence ({details['signatures_matched']} signatures matched).")
        
    if not justification:
        justification.append("No significant threats detected.")
        
    if risk_score <= DECISION_THRESHOLDS["ALLOW"]:
        decision = "ALLOW"
        explanation = "The prompt appears safe and exhibits minimal risk."
        recommended_action = "Process the request normally."
    elif risk_score <= DECISION_THRESHOLDS["WARN"]:
        decision = "WARN"
        explanation = "The prompt has some suspicious elements. Proceed with caution."
        recommended_action = "Allow the request but monitor the output closely."
    elif risk_score <= DECISION_THRESHOLDS["MODIFY"]:
        decision = "MODIFY"
        explanation = "High risk detected. The prompt contains dangerous patterns."
        recommended_action = "Sanitize the prompt to remove malicious instructions before processing."
    else:
        decision = "BLOCK"
        explanation = "Critical risk detected. The prompt exhibits clear attack patterns."
        recommended_action = "Reject the request and notify the orchestration layer."
        
    return {
        "decision": decision,
        "explanation": explanation,
        "justification": justification,
        "recommended_action": recommended_action
    }
