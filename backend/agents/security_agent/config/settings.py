"""Configuration Module.

Contains configurable weights, thresholds, rewrite templates, and priorities
for the Risk Assessment, Decision, and Remediation engines.
"""

# Attack Weights (0-100 scale)
ATTACK_WEIGHTS = {
    "Data Exfiltration": 100,
    "Tool Abuse": 90,
    "Prompt Injection": 85,
    "System Prompt Extraction": 80,
    "Jailbreak": 75,
    "Role Escalation": 70,
    "Prompt Leakage": 65,
    "Suspicious Command Patterns": 65,
    "Instruction Override": 60,
    "Multi-step Attack Chains": 50,
    "Encoding-based Attacks": 50,
    "Obfuscated Prompt": 40
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

import os

# AI Infrastructure Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "10000"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
DEVICE_SELECTION = os.getenv("DEVICE_SELECTION", "cuda")
FALLBACK_TO_CPU = os.getenv("FALLBACK_TO_CPU", "True").lower() in ("true", "1", "yes")

# Qdrant Database Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_HTTPS = os.getenv("QDRANT_HTTPS", "False").lower() in ("true", "1", "yes")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "security_patterns")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "384"))
DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", "Cosine")
VECTOR_BATCH_SIZE = int(os.getenv("VECTOR_BATCH_SIZE", "100"))
