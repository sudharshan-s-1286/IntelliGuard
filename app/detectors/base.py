from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DetectorSeverity(str, Enum):
    """
    Standard severity classifications for detector findings.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class FindingDetail(BaseModel):
    """
    Schema representing an individual finding identified by a detector.
    """

    detector_name: str = Field(..., description="Name of the detector that generated the finding")
    category: str = Field(..., description="Classification category of the finding")
    severity: DetectorSeverity = Field(
        default=DetectorSeverity.LOW, description="Severity level of the finding"
    )
    description: str = Field(..., description="Human-readable description of the finding")
    confidence_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional contextual attributes"
    )


class DetectorResult(BaseModel):
    """
    Result payload produced by an individual detector execution.
    """

    detector_name: str = Field(..., description="Unique name of the executing detector")
    is_triggered: bool = Field(
        default=False, description="Flag indicating if a risk or anomaly was detected"
    )
    score: float = Field(
        default=100.0, ge=0.0, le=100.0, description="Individual detector trust or risk score"
    )
    findings: List[FindingDetail] = Field(
        default_factory=list, description="List of findings identified during analysis"
    )
    execution_time_ms: float = Field(
        default=0.0, ge=0.0, description="Execution duration in milliseconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Detector execution metadata"
    )


class BaseDetector(ABC):
    """
    Abstract Base Class for all future detector modules.
    
    Future detectors (Prompt Injection, Jailbreak, PII, Toxicity, Hallucination, Bias,
    Citation, Compliance) must extend this class and implement the required interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name of the detector."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version string of the detector implementation."""
        pass

    @property
    def is_enabled(self) -> bool:
        """Indicates whether the detector is currently enabled in pipeline."""
        return True

    async def is_ready(self) -> bool:
        """
        Check if detector resources/models are loaded and ready for analysis.
        """
        return True

    @abstractmethod
    async def analyze(
        self, prompt: str, metadata: Optional[Dict[str, Any]] = None
    ) -> DetectorResult:
        """
        Executes analysis on the target prompt and context metadata.
        Must return a valid DetectorResult instance.
        """
        pass
