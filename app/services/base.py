from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseService(ABC):
    """
    Abstract Base Service interface for application domain services.
    Enforces clean separation of concerns and interface consistency.
    """

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Returns the identifier name of the service."""
        pass


class BaseEngineService(BaseService):
    """
    Abstract Base Class for future security, privacy, and evaluation engines.
    
    All future detector/engine modules (e.g. Prompt Injection, PII, Toxicity,
    Trust Score, Compliance) will extend this class to ensure contract compliance
    and dependency injection pluggability.
    """

    @abstractmethod
    async def is_ready(self) -> bool:
        """
        Check if the underlying model/resource of the engine is loaded and operational.
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Returns the version string of the engine module.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns metadata attributes about engine capabilities and configuration.
        """
        pass
