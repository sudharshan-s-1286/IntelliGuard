"""Configuration Module.

Contains configurable weights, thresholds, rewrite templates, and priorities
for the Risk Assessment, Decision, and Remediation engines.
"""

# Attack Weights (0-100 scale)
ATTACK_WEIGHTS = {
    "Prompt Injection": 30,
    "System Prompt Extraction": 35,
    "Jailbreak": 25,
    "Data Exfiltration": 40,
    "Tool Abuse": 35,
    "Role Escalation": 30,
    "Instruction Override": 25,
    "Prompt Leakage": 30,
    "Obfuscated Prompt": 20,
    "Encoding-based Attacks": 30,
    "Multi-step Attack Chains": 40,
    "Suspicious Command Patterns": 35
}

# Penalty modifiers
PENALTY_MULTI_ATTACK_MULTIPLIER = 1.2
PENALTY_ENCODED_PAYLOAD = 15

# Risk Category Thresholds
RISK_THRESHOLDS = {
    "SAFE": 25,
    "SUSPICIOUS": 50,
    "DANGEROUS": 75,
    "CRITICAL": 100
}

# Decision Thresholds
DECISION_THRESHOLDS = {
    "ALLOW": 25,
    "WARN": 50,
    "MODIFY": 75,
    "BLOCK": 100
}

# Remediation Rewrite Templates (Phase 6)
REWRITE_TEMPLATES = {
    "Prompt Injection": "Explain how AI safety mechanisms and role-based prompting work.",
    "System Prompt Extraction": "Explain what a system prompt is and how it is used in AI systems.",
    "Jailbreak": "Explain how AI safety mechanisms and role-based prompting work.",
    "Role Escalation": "Explain the concept of role-based access control and why privilege escalation is prevented.",
    "Instruction Override": "Explain the importance of following instructions and constraints in AI systems.",
    "Data Exfiltration": "Explain best practices for securely managing sensitive data and API keys.",
    "Prompt Leakage": "Discuss data privacy and why system-level instructions are not disclosed.",
    "Tool Abuse": "Explain the principles of secure execution environments and command safety.",
    "Obfuscated Prompt": "Explain why clear, unencoded text is required for safe processing.",
    "Encoding-based Attacks": "Explain why encoded payloads cannot be processed for security reasons.",
    "Suspicious Command Patterns": "Explain the principles of secure execution environments and command safety.",
    "Multi-step Attack Chains": "Explain how multi-layered security prevents complex attack chains."
}
