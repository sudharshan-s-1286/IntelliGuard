import uuid
from abc import ABC, abstractmethod
from typing import Any

from backend.agents.security_agent.models.domain import NormalizedDatasetRecord

class BaseNormalizer(ABC):
    @abstractmethod
    def normalize(self, raw_record: dict[str, Any]) -> NormalizedDatasetRecord | None:
        """
        Normalize a raw dataset record into the standard schema.
        Return None if the record should be skipped (e.g., malformed).
        """
        pass

    def _generate_id(self, source: str) -> str:
        return f"{source}-{uuid.uuid4().hex[:8]}"


class HackAPromptNormalizer(BaseNormalizer):
    def normalize(self, raw_record: dict[str, Any]) -> NormalizedDatasetRecord | None:
        prompt = raw_record.get("prompt")
        if not prompt:
            return None
            
        level = raw_record.get("level", 1)
        severity = "HIGH" if level > 3 else "MEDIUM"
        
        return NormalizedDatasetRecord(
            id=self._generate_id("hackaprompt"),
            category="Prompt Injection",
            subcategory="HackAPrompt",
            severity=severity,
            owasp="LLM01",
            text=prompt,
            source="hackaprompt",
            tags=[f"level_{level}"]
        )

class GarakNormalizer(BaseNormalizer):
    def normalize(self, raw_record: dict[str, Any]) -> NormalizedDatasetRecord | None:
        prompt = raw_record.get("prompt")
        if not prompt:
            return None
            
        plugin = raw_record.get("plugin", "unknown")
        goal = raw_record.get("goal", "unknown")
        
        return NormalizedDatasetRecord(
            id=self._generate_id("garak"),
            category="Vulnerability Probe",
            subcategory=plugin,
            severity="MEDIUM",
            owasp="LLM01",
            text=prompt,
            source="garak",
            tags=["garak", goal]
        )

class OWASPNormalizer(BaseNormalizer):
    def normalize(self, raw_record: dict[str, Any]) -> NormalizedDatasetRecord | None:
        text = raw_record.get("text")
        if not text:
            return None
            
        category = raw_record.get("category", "Prompt Injection")
        owasp_id = raw_record.get("owasp_id", "LLM01")
        
        return NormalizedDatasetRecord(
            id=self._generate_id("owasp"),
            category=category,
            subcategory="OWASP Example",
            severity="HIGH",
            owasp=owasp_id,
            text=text,
            source="owasp",
            tags=["owasp"]
        )

class ProtectAINormalizer(BaseNormalizer):
    def normalize(self, raw_record: dict[str, Any]) -> NormalizedDatasetRecord | None:
        # Sometimes 'input' or 'text' depending on the exact dataset from Protect AI
        text = raw_record.get("input") or raw_record.get("text")
        if not text:
            return None
            
        label = raw_record.get("label", "unknown")
        
        return NormalizedDatasetRecord(
            id=self._generate_id("protect_ai"),
            category="Prompt Injection",
            subcategory=label,
            severity="MEDIUM",
            owasp="LLM01",
            text=text,
            source="protect_ai",
            tags=["protect_ai", label]
        )
