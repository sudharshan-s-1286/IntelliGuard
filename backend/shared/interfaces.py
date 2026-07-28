from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

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


class DetectorSeverity(str, Enum):
    """Supported severity classifications for detector findings."""
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectorResult(BaseModel):
    """Structured result produced by a single detector execution."""
    detector_name: str = Field(..., description="Unique name of the detector")
    is_triggered: bool = Field(..., description="Whether the detector flagged any finding")
    score: float = Field(..., description="Detector-specific score (0.0-100.0)")
    findings: List["FindingDetail"] = Field(default_factory=list, description="List of findings produced")
    execution_time_ms: float = Field(..., description="Execution latency in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary detector metadata")


class FindingDetail(BaseModel):
    """Detailed finding produced by a detector."""
    detector_name: str = Field(..., description="Name of the detector that produced the finding")
    category: str = Field(..., description="Category or tag describing the finding type")
    severity: DetectorSeverity = Field(..., description="Severity classification")
    description: str = Field(..., description="Human-readable description of the finding")
    confidence_score: float = Field(default=0.0, description="Confidence in the finding (0.0-1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional finding context")


class BaseDetector(ABC):
    """
    Standard interface that all detection modules must implement.
    Ensures compatibility with the AnalysisPipeline orchestrator.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the detector."""
        pass
         
    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version of the detector."""
        pass
         
    @property
    def is_enabled(self) -> bool:
        """Whether the detector is active. Override to add toggles."""
        return True
         
    @abstractmethod
    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        """Execute detection logic against the provided prompt."""
        pass
         
    async def is_ready(self) -> bool:
        """Readiness check before execution. Override if detector has async setup."""
        return True
