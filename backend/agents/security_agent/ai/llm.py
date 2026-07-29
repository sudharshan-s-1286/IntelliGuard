"""LLM Classifier."""
from typing import Any


class LLMClassifier:
    """Handles fallback classification using powerful LLMs."""

    def __init__(self, model_loader: Any) -> None:
        self.model_loader = model_loader

    async def classify(self, prompt: str) -> Any:
        """
        Classify a prompt using an LLM to extract threat semantics.
        :param prompt: The ambiguous prompt.
        :return: A list of Findings.
        """
