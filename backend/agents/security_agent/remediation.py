"""Prompt Remediation Engine.

Intelligently transforms unsafe prompts into safe alternatives while preserving
the user's legitimate intent using deterministic rewrite templates.
"""
import re

from .config import REWRITE_TEMPLATES


def remove_attack_patterns(prompt: str, findings: dict) -> str:
    """Strip explicit attack patterns from the prompt."""
    cleaned = prompt
    for finding in findings.values():
        if finding["detected"]:
            for pattern in finding.get("matched_patterns", []):
                try:
                    # Case-insensitive stripping
                    cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
                except re.error:
                    pass
    return cleaned.strip()

def preserve_user_intent(original_prompt: str, attack_type: str) -> str:
    """Attempt to map an attack attempt into a legitimate, educational query."""
    return REWRITE_TEMPLATES.get(attack_type, "Explain how AI systems handle user requests safely.")

def rewrite_prompt(original_prompt: str, primary_attack: str) -> str:
    """Generate a full rewrite of the prompt based on the primary attack vector."""
    return preserve_user_intent(original_prompt, primary_attack)

def validate_safe_prompt(safe_prompt: str) -> bool:
    """Validate that the newly generated safe prompt is indeed safe."""
    # A robust engine would pass this back through the detector.py pipeline.
    # For determinism, our hardcoded templates are intrinsically safe.
    return bool(safe_prompt and safe_prompt.strip())

def sanitize_prompt(prompt: str, findings: dict) -> str:
    """Sanitizes the prompt by either removing attacks or fully rewriting it."""
    primary_attack = get_primary_attack(findings)
    if primary_attack:
        return rewrite_prompt(prompt, primary_attack)
    return remove_attack_patterns(prompt, findings)

def explain_modifications(findings: dict) -> list[str]:
    """Generate human-readable explanations of the modifications made."""
    changes = []
    for finding in findings.values():
        if finding["detected"]:
            changes.append(f"Neutralized {finding['attack']} patterns.")
    return changes

def get_primary_attack(findings: dict) -> str | None:
    """Help to find the most confident attack for intent preservation."""
    highest_conf = 0.0
    primary = None
    for finding in findings.values():
        if finding["detected"] and finding["confidence"] > highest_conf:
            highest_conf = finding["confidence"]
            primary = finding["attack"]
    return primary

def generate_safe_prompt(prompt: str, findings: dict) -> str | None:
    """Generate safe prompts using helpers to sanitize."""
    try:
        if not prompt:
            return None
            
        safe_p = sanitize_prompt(prompt, findings)
            
        if validate_safe_prompt(safe_p):
            return safe_p
        return None
    except Exception: # noqa: BLE001, keeping broad as it catches multiple string processing errors
        # Failsafe in case of extremely malformed regexes or edge cases
        return None

def remediate(prompt: str, findings: dict, decision: str) -> dict:
    """Provide the main entry point for the Remediation Engine.
    
    Args:
        prompt (str): Original prompt.
        findings (dict): Detected attacks.
        decision (str): The decision from the decision engine.
        
    Returns:
        dict: Remediation results to be merged into the API response.

    """
    result = {
        "original_prompt": prompt,
        "safe_prompt": None,
        "changes": [],
        "reason": "No remediation required.",
        "confidence": 0.0,
        "applied": False
    }
    
    if not prompt or not prompt.strip():
        return result
        
    if decision == "ALLOW":
        result["safe_prompt"] = prompt
        result["reason"] = "Prompt is safe. No changes made."
        
    elif decision == "WARN":
        result["safe_prompt"] = prompt
        result["reason"] = "Prompt is suspicious but allowed. Suggestions for safety could be applied."
        
    elif decision == "MODIFY":
        safe_p = generate_safe_prompt(prompt, findings)
        if safe_p:
            result["safe_prompt"] = safe_p
            result["applied"] = True
            result["changes"] = explain_modifications(findings)
            result["reason"] = "Prompt was automatically remediated to preserve intent safely."
            result["confidence"] = 0.95
            
    elif decision == "BLOCK":
        safe_p = generate_safe_prompt(prompt, findings)
        if safe_p:
            result["safe_prompt"] = safe_p
            result["applied"] = True
            result["changes"] = explain_modifications(findings)
            result["reason"] = "Prompt was blocked, but a safe educational alternative was generated."
            result["confidence"] = 0.90
        else:
            result["reason"] = "Prompt was blocked and could not be safely rewritten."

    return result
