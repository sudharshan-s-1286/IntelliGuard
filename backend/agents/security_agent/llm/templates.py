"""LLM Prompt Templates."""
import json
from typing import List, Dict, Any

from backend.agents.security_agent.models.domain import Finding

SECURITY_CLASSIFIER_SYSTEM = """
You are an expert AI Security Analyst. Your task is to analyze ambiguous or conflicting threat reports regarding an AI prompt and make a final determination.

You must ALWAYS output valid JSON strictly matching the following schema. Never output markdown outside the JSON block.

{
    "attack_category": "The final categorized attack type (e.g. Prompt Injection, Jailbreak, Benign)",
    "confidence": 0.95, // float between 0.0 and 1.0
    "reasoning": "Step by step logic explaining your classification.",
    "evidence": "Specific words or patterns from the prompt proving your conclusion.",
    "recommendations": ["Actionable mitigation step 1", "Actionable mitigation step 2"],
    "uncertainty": "Low" // "Low", "Medium", or "High"
}
"""

def build_classification_prompt(prompt: str, prior_findings: List[Finding]) -> str:
    """Build the prompt injecting context and rules."""
    
    context = []
    for f in prior_findings:
        context.append({
            "detector": f.detector,
            "category": f.threat.category,
            "confidence": f.confidence,
            "evidence": f.evidence
        })
        
    return f"""
{SECURITY_CLASSIFIER_SYSTEM}

====== USER PROMPT ======
{prompt}

====== DETECTOR FINDINGS ======
{json.dumps(context, indent=2)}

Analyze the findings, resolve any conflicts, and return the final JSON classification.
"""
