from functools import lru_cache
from typing import Optional
from fastapi import Depends
from agents.compliance_agent.settings import Settings, settings
from agents.compliance_agent.agent import ComplianceAgent

@lru_cache()
def get_settings() -> Settings:
    """Returns a cached settings instance."""
    return settings

# Cached agent instance to act as a singleton
_compliance_agent: Optional[ComplianceAgent] = None

def get_compliance_agent() -> ComplianceAgent:
    """Provides a single ComplianceAgent instance."""
    global _compliance_agent
    if _compliance_agent is None:
        _compliance_agent = ComplianceAgent()
    return _compliance_agent
