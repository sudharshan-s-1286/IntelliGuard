"""Decision Engine."""
from typing import Any, List

class DecisionEngine:
    """
    Aggregates outputs from detectors. Determines if the LLM Classifier is needed.
    """

    def __init__(self, detectors: List[Any], llm_classifier: Any, risk_scorer: Any) -> None:
        self.detectors = detectors
        self.llm_classifier = llm_classifier
        self.risk_scorer = risk_scorer

    async def process(self, prompt: str) -> Any:
        """
        Run all standard detectors and conditionally fallback to LLM.
        :param prompt: The input prompt.
        :return: DetectionResult.
        """
        # TODO: Run parallel detection, fallback to LLM, and compute risk score
        pass
