"""Patterns Module.

Contains centralized attack signatures, regular expressions, keyword lists,
and configurable detection thresholds/weights.
"""

# Confidence Weights for different attack types
ATTACK_WEIGHTS = {
    "Prompt Injection": 0.35,
    "System Prompt Extraction": 0.40,
    "Jailbreak": 0.30,
    "Tool Abuse": 0.45,
    "Data Exfiltration": 0.50,
    "Role Escalation": 0.40,
    "Instruction Override": 0.35,
    "Prompt Leakage": 0.40,
    "Obfuscated Prompt": 0.30,
    "Encoding-based Attacks": 0.45,
    "Multi-step Attack Chains": 0.50,
    "Suspicious Command Patterns": 0.45
}

# Regex and Keyword Patterns
PATTERNS = {
    "Prompt Injection": [
        r"(?i)\bignore\s+(all\s+)?(previous\s+)?instructions\b",
        r"(?i)\bdisregard\s+(the\s+)?(previous\s+)?prompt\b",
        r"(?i)\bforget\s+everything\b",
        r"(?i)\bnew\s+instructions\b"
    ],
    "Jailbreak": [
        r"(?i)\bDAN\b",
        r"(?i)\bdo\s+anything\s+now\b",
        r"(?i)\bhypothetical\s+scenario\b",
        r"(?i)\bpretend\s+to\s+be\b",
        r"(?i)\balways\s+answer\b",
        r"(?i)\broleplay\s+as\b"
    ],
    "System Prompt Extraction": [
        r"(?i)\bwhat\s+are\s+your\s+(initial\s+)?instructions\b",
        r"(?i)\brepeat\s+the\s+prompt\b",
        r"(?i)\bprint\s+your\s+system\s+prompt\b",
        r"(?i)\bwhat\s+were\s+you\s+told\b"
    ],
    "Role Escalation": [
        r"(?i)\badmin\s+mode\b",
        r"(?i)\bdeveloper\s+mode\b",
        r"(?i)\bsystem\s+administrator\b",
        r"(?i)\broot\s+access\b",
        r"(?i)\bsudo\b"
    ],
    "Instruction Override": [
        r"(?i)\binstead\s+do\s+this\b",
        r"(?i)\boverride\s+protocol\b",
        r"(?i)\bbypass\s+rules\b",
        r"(?i)\bdisregard\s+rules\b"
    ],
    "Tool Abuse": [
        r"(?i)\brm\s+-rf\b",
        r"(?i)\bdrop\s+table\b",
        r"(?i)\bexecute\s+command\b",
        r"(?i)\brun\s+script\b",
        r"(?i)\bcurl\b",
        r"(?i)\bwget\b",
        r"(?i)chmod\s+\+x"
    ],
    "Data Exfiltration": [
        r"(?i)\bsend\s+data\s+to\b",
        r"(?i)\bemail\s+passwords\b",
        r"(?i)\bexport\s+database\b",
        r"(?i)\bexfiltrate\b",
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    ],
    "Prompt Leakage": [
        r"(?i)\btell\s+me\s+your\s+secrets\b",
        r"(?i)\bwhat\s+did\s+you\s+say\s+earlier\b",
        r"(?i)\breveal\s+hidden\b",
        r"(?i)\boutput\s+the\s+preceding\b"
    ],
    "Suspicious Command Patterns": [
        r"(?i)(bash|sh)\s+-i",
        r"(?i)nc\s+-e",
        r"(?i)powershell(\.exe)?\s+-nop",
        r"(?i)/dev/tcp/"
    ]
}

# Configurable detection thresholds
CONFIDENCE_THRESHOLDS = {
    "HIGH": 0.8,
    "MEDIUM": 0.5,
    "LOW": 0.2
}
