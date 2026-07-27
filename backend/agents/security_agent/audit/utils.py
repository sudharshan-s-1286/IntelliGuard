"""Audit Utilities.

Provides helper formatting and sanitization functions for the audit subsystem.
"""

def truncate_string(text: str, max_length: int = 500) -> str:
    """Truncate a string to prevent log explosion or storage overflow."""
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length] + "...[TRUNCATED]"
    return text
