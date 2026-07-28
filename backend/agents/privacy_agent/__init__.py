"""Privacy Agent for the IntelliGuard platform.

The Privacy Agent is responsible for detecting, classifying,
masking, and scoring Personally Identifiable Information (PII)
in text data. It follows Clean Architecture and SOLID principles.
"""

from __future__ import annotations

from .agent import PrivacyAgent
from .config import PrivacyAgentConfig

__all__ = [
    "PrivacyAgent",
    "PrivacyAgentConfig",
]
__version__ = "1.0.0"
