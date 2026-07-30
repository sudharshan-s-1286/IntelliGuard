"""LLM Classifier."""
import asyncio
import json
import logging

from agents.security_agent.config import settings
from agents.security_agent.llm.providers import get_provider
from agents.security_agent.llm.templates import build_classification_prompt
from agents.security_agent.models.domain import (
    DetectionResult,
    Finding,
    LLMClassificationResponse,
    Metadata,
    Recommendation,
    RiskScore,
    RoutingDecision,
    Threat,
)

logger = logging.getLogger(__name__)

class LLMClassifier:
    """Fallback analysis stage for ambiguous or low-confidence security prompts."""

    def __init__(self) -> None:
        self.provider = get_provider()
        self.max_retries = settings.LLM_MAX_RETRIES
        self.timeout = settings.LLM_TIMEOUT

    def _safe_parse(self, raw_json: str) -> LLMClassificationResponse:
        """Parse and validate the JSON output from the LLM."""
        try:
            # LLMs sometimes wrap json in markdown blocks like ```json ... ```
            cleaned = raw_json.strip()
            cleaned = cleaned.removeprefix("```json")
            cleaned = cleaned.removesuffix("```")
            
            data = json.loads(cleaned.strip())
            return LLMClassificationResponse(
                attack_category=data.get("attack_category", "Unknown"),
                confidence=float(data.get("confidence", 0.0)),
                reasoning=data.get("reasoning", "No reasoning provided"),
                evidence=data.get("evidence", ""),
                recommendations=data.get("recommendations", []),
                uncertainty=data.get("uncertainty", "High")
            )
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM JSON response: {e}\nRaw: {raw_json}")
            raise ValueError(f"Malformed JSON: {e}")

    async def classify(self, prompt: str, prior_findings: list[Finding]) -> DetectionResult:
        """
        Consult the LLM to make a final classification on the prompt.
        """
        logger.info("LLM Classifier: Starting classification fallback.")
        full_prompt = build_classification_prompt(prompt, prior_findings)

        parsed_response = None
        attempt = 0
        last_error = None

        while attempt <= self.max_retries:
            try:
                # Add timeout protection
                raw_response = await asyncio.wait_for(
                    self.provider.generate(full_prompt), 
                    timeout=self.timeout
                )
                parsed_response = self._safe_parse(raw_response)
                break
            except asyncio.TimeoutError:
                logger.error(f"LLM Provider timeout after {self.timeout}s.")
                last_error = "Timeout"
                break
            except Exception as e:
                logger.warning(f"LLM Provider failure (Attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                last_error = str(e)
                attempt += 1

        if not parsed_response:
            logger.error("LLM Classifier exhausted retries. Returning safe fallback.")
            parsed_response = LLMClassificationResponse(
                attack_category="Unknown LLM Failure",
                confidence=0.0,
                reasoning=f"LLM classification failed: {last_error}",
                evidence="",
                recommendations=["Manual review required"],
                uncertainty="High"
            )

        # Convert to DetectionResult
        severity = 0.8 if parsed_response.confidence >= 0.8 else 0.5
        
        finding = Finding(
            threat=Threat(
                category=parsed_response.attack_category,
                description=parsed_response.reasoning
            ),
            severity=severity,
            evidence=parsed_response.evidence,
            detector="LLMClassifier",
            confidence=parsed_response.confidence
        )

        recs = [Recommendation(action=r, priority="High") for r in parsed_response.recommendations]
        
        explainability = [
            "LLM Classification invoked.",
            f"Category: {parsed_response.attack_category}, Confidence: {parsed_response.confidence}",
            f"Uncertainty: {parsed_response.uncertainty}",
            f"Reasoning: {parsed_response.reasoning}"
        ]

        return DetectionResult(
            risk_score=RiskScore(score=severity * parsed_response.confidence, factors=["LLM analysis applied"]),
            findings=[finding],
            recommendations=recs,
            metadata=Metadata(execution_time_ms=0.0, model_versions={"llm": settings.LLM_MODEL_NAME}),
            routing=RoutingDecision(needs_llm=True, reason="LLM Classification completed"),
            explainability=explainability
        )

    def health(self) -> dict:
        return {
            "status": "healthy",
            "provider": self.provider.health(),
            "max_retries": self.max_retries,
            "timeout": self.timeout
        }
