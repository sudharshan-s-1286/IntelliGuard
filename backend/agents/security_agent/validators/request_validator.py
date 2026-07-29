"""Utilities Module.

Helper functions for pattern matching, string normalization,
encoding detection, keyword scoring, and confidence calculation.
"""
import base64
import binascii
import re
import unicodedata
import urllib.parse


def normalize_string(text: str) -> str:
    """Normalize unicode and whitespace in the string."""
    if not text:
        return ""
    # Normalize unicode to NFKC
    text = unicodedata.normalize('NFKC', text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_encodings(text: str) -> tuple[bool, str]:
    """Detect and attempts to decode base64, hex, and URL encodings."""
    decoded_text = text
    encoded = False
    
    # Try Base64
    if len(text) % 4 == 0 and len(text) > 8 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', text):
        try:
            decoded_bytes = base64.b64decode(text, validate=True)
            decoded_text = decoded_bytes.decode('utf-8')
            encoded = True
            return encoded, decoded_text
        except (ValueError, TypeError, binascii.Error):
            pass

    # Try Hex
    if re.match(r'^([a-fA-F0-9]{2})+$', text) or re.match(r'^(\\x[a-fA-F0-9]{2})+$', text):
        try:
            clean_hex = text.replace('\\x', '')
            decoded_bytes = bytes.fromhex(clean_hex)
            decoded_text = decoded_bytes.decode('utf-8')
            encoded = True
            return encoded, decoded_text
        except (ValueError, TypeError):
            pass

    # Try URL Encode
    if '%' in text:
        unquoted = urllib.parse.unquote(text)
        if unquoted != text:
            encoded = True
            return encoded, unquoted

    return encoded, decoded_text

def match_patterns(patterns: list[str], text: str) -> list[str]:
    """Match a list of regex patterns against text and returns matched signatures."""
    matched = []
    for pattern in patterns:
        if re.search(pattern, text):
            matched.append(pattern)
    return matched

def score_keywords(keywords: list[str], text: str) -> float:
    """Calculate a score based on keyword occurrences."""
    score = 0.0
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            score += 0.2
    return min(1.0, score)

def calculate_confidence(matched_patterns: list[str], total_patterns: int) -> float:
    """Calculate confidence based on the number of matched patterns."""
    if not total_patterns or not matched_patterns:
        return 0.0
    # Base confidence per match, caps at 1.0
    confidence = min(1.0, len(matched_patterns) * 0.4) 
    return round(confidence, 2)

def parse_prompt(prompt: str) -> dict:
    normalized = normalize_string(prompt)
    is_encoded, decoded = detect_encodings(normalized)
    if is_encoded and decoded != normalized:
        normalized = normalize_string(decoded)
    return {
        "original": prompt,
        "normalized": normalized,
        "was_encoded": is_encoded
    }
