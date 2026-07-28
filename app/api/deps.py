from functools import lru_cache
from fastapi import Request
from app.agents.trust_agent import TrustAgent
from app.core.config import Settings, get_settings
from app.detectors.pii_detector import PIIDetector
from app.detectors.prompt_injection import PromptInjectionDetector


def get_app_settings() -> Settings:
    """
    Dependency provider for application settings.
    Allows easy overriding during unit and integration testing.
    """
    return get_settings()


def get_request_id(request: Request) -> str:
    """
    Dependency provider for retrieving current request context ID.
    """
    return getattr(request.state, "request_id", "unknown")


@lru_cache
def get_trust_agent() -> TrustAgent:
    """
    Dependency provider for retrieving singleton TrustAgent orchestrator instance.
    Registers default production detectors cleanly into the orchestrator pipeline.
    Can be overridden in tests via app.dependency_overrides[get_trust_agent].
    """
    agent = TrustAgent()
    agent.register_detector(PromptInjectionDetector())
    agent.register_detector(PIIDetector())
    return agent

