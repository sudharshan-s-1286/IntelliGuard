"""Risk Scorer."""
from typing import List, Any

class RiskScorer:
    """Normalizes confidence levels and severity into a final risk score."""

    def __init__(self) -> None:
        pass

    def compute_score(self, findings: List[Any]) -> float:
        """
        Compute a risk score between 0 and 100.
        :param findings: A list of Findings.
        :return: Float representing the risk score.
        """
        # TODO: Implement scoring formula based on finding severity
        pass
