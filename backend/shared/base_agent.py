from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseDetector(ABC):
    """
    Abstract base class representing a generic scanner/detector.
    All detectors should implement the `detect` method.
    """

    @abstractmethod
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text and returns structured findings.

        Args:
            text: The raw text content to analyze.

        Returns:
            A list of dictionary findings, where each finding has:
            - 'type': Finding type name (str)
            - 'severity': Severity level (str)
            - 'text': The matched substring (str)
        """
        pass
