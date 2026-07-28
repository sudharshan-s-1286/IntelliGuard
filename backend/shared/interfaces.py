from abc import ABC, abstractmethod
from typing import Any, Dict
from .response_models import AgentResponse

class BaseAgent(ABC):
    """
    Standard interface that all IntelliGuard agents must implement.
    Ensures seamless compatibility with the central Orchestrator.
    """
    
    @abstractmethod
    def process(self, request: Any) -> AgentResponse:
        """The main entry point for the agent."""
        pass
        
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Returns the health status of the agent."""
        pass
        
    @abstractmethod
    def ready(self) -> Dict[str, Any]:
        """Checks if all resources are loaded and ready."""
        pass
        
    @abstractmethod
    def version(self) -> str:
        """Returns the agent version."""
        pass
        
    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Describes the features and capabilities of the agent."""
        pass
        
    @abstractmethod
    def metrics(self) -> Dict[str, Any]:
        """Returns operational metrics and statistics."""
        pass
