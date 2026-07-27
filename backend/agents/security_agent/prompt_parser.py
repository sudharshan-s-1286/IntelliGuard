"""Prompt Parser Module.

Responsible for taking the raw input prompt and normalizing it for analysis.
Removes unnecessary formatting, normalizes whitespace, decodes payloads,
and preserves the original prompt.
"""
from .utils import detect_encodings, normalize_string


def parse_prompt(prompt: str) -> dict:
    """Normalize the input prompt and handle encodings.

    Strips extra whitespace, handles unicode, and decodes simple encoded payloads.

    Args:
        prompt (str): The raw input prompt.
        
    Returns:
        dict: A dictionary containing the original, normalized, and potentially decoded prompts.

    """
    normalized = normalize_string(prompt)
    
    # Check for basic full-string encodings
    is_encoded, decoded = detect_encodings(normalized)
    
    if is_encoded and decoded != normalized:
        # If it was encoded, normalize the decoded payload too
        normalized = normalize_string(decoded)

    return {
        "original": prompt,
        "normalized": normalized,
        "was_encoded": is_encoded
    }
