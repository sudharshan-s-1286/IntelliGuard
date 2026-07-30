"""Detector Module.

Contains independent detection functions for various types of LLM attacks
using a centralized pattern-matching engine.
"""
import re

from agents.security_agent.knowledge.static_patterns import PATTERNS
from agents.security_agent.validators.request_validator import (
    calculate_confidence,
    match_patterns,
)


def _build_result(attack_name: str, matched_patterns: list, custom_confidence: float | None = None) -> dict:
    detected = len(matched_patterns) > 0
    confidence = custom_confidence if custom_confidence is not None else calculate_confidence(matched_patterns, len(PATTERNS.get(attack_name, [])))
    
    # Assign severity based on confidence
    if confidence >= 0.8:
        severity = "High"
    elif confidence >= 0.5:
        severity = "Medium"
    elif confidence > 0:
        severity = "Low"
    else:
        severity = "None"
        
    return {
        "attack": attack_name,
        "detected": detected,
        "confidence": confidence if detected else 0.0,
        "severity": severity,
        "reason": f"Matched {len(matched_patterns)} signature(s)" if detected else "",
        "matched_patterns": matched_patterns
    }

def detect_prompt_injection(prompt: str) -> dict:
    """Detect prompt injection patterns."""
    name = "Prompt Injection"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_jailbreak(prompt: str) -> dict:
    """Detect jailbreak attempts."""
    name = "Jailbreak"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_system_prompt_extraction(prompt: str) -> dict:
    """Detect system prompt extraction."""
    name = "System Prompt Extraction"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_role_escalation(prompt: str) -> dict:
    """Detect role escalation attempts."""
    name = "Role Escalation"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_instruction_override(prompt: str) -> dict:
    """Detect instruction override."""
    name = "Instruction Override"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_tool_abuse(prompt: str) -> dict:
    """Detect tool abuse patterns."""
    name = "Tool Abuse"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_data_exfiltration(prompt: str) -> dict:
    """Detect data exfiltration attempts."""
    name = "Data Exfiltration"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_prompt_leakage(prompt: str) -> dict:
    """Detect prompt leakage patterns."""
    name = "Prompt Leakage"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_suspicious_command_patterns(prompt: str) -> dict:
    """Detect suspicious command usage."""
    name = "Suspicious Command Patterns"
    matches = match_patterns(PATTERNS.get(name, []), prompt)
    return _build_result(name, matches)

def detect_obfuscated_prompt(prompt: str) -> dict:
    """Detect obfuscated content like large gaps."""
    name = "Obfuscated Prompt"
    matched_patterns = []
    confidence = 0.0
    
    if len(prompt) > 20:
        non_alnum_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', prompt)) / len(prompt)
        if non_alnum_ratio > 0.3:
            matched_patterns.append("high_non_alphanumeric_ratio")
            confidence = min(1.0, non_alnum_ratio * 2)
            
    return _build_result(name, matched_patterns, custom_confidence=round(confidence, 2))

def detect_encoding_attacks(prompt: str, was_encoded: bool = False) -> dict:
    """Detect encoding attacks like base64 payloads."""
    name = "Encoding-based Attacks"
    matched = ["payload_was_encoded"] if was_encoded else []
    return _build_result(name, matched, custom_confidence=0.85 if was_encoded else 0.0)

def detect_multi_step_attack(findings: dict) -> dict:
    """Detect if multiple distinct attack vectors are present."""
    name = "Multi-step Attack Chains"
    detected_attacks = [finding["attack"] for finding in findings.values() if finding["detected"]]
    
    matched = []
    confidence = 0.0
    if len(detected_attacks) > 1:
        matched.append("multiple_attack_vectors")
        confidence = min(1.0, len(detected_attacks) * 0.3)
        
    return _build_result(name, matched, custom_confidence=round(confidence, 2))

def run_all_detectors(prompt: str, was_encoded: bool = False) -> dict:
    """Run all independent detectors on the given prompt and aggregates the results."""
    findings = {
        "prompt_injection": detect_prompt_injection(prompt),
        "jailbreak": detect_jailbreak(prompt),
        "system_prompt_extraction": detect_system_prompt_extraction(prompt),
        "role_escalation": detect_role_escalation(prompt),
        "instruction_override": detect_instruction_override(prompt),
        "tool_abuse": detect_tool_abuse(prompt),
        "data_exfiltration": detect_data_exfiltration(prompt),
        "prompt_leakage": detect_prompt_leakage(prompt),
        "suspicious_commands": detect_suspicious_command_patterns(prompt),
        "obfuscation": detect_obfuscated_prompt(prompt),
        "encoding": detect_encoding_attacks(prompt, was_encoded)
    }
    
    # Run multi-step chain detector which depends on the others
    findings["multi_step"] = detect_multi_step_attack(findings)
    
    return findings
