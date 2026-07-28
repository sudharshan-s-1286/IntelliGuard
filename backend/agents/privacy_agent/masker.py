"""Information masking module for the Privacy Agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import PIIEntity
from .exceptions import MaskingError
from .constants import MASK_CHAR, DEFAULT_MASK_PATTERN
from .logging_config import get_structured_logger

if TYPE_CHECKING:
    from .config import PrivacyAgentConfig

logger = get_structured_logger(__name__)


class MaskingStrategy:
    """Strategy interface for information masking."""

    def mask(self, value: str) -> str:
        """Mask a sensitive value. Must be overridden."""
        raise NotImplementedError


@dataclass
class RedactionMasker(MaskingStrategy):
    """Redacts the entire value with a placeholder."""

    placeholder: str = DEFAULT_MASK_PATTERN

    def mask(self, value: str) -> str:
        """Replace the entire value with the placeholder."""
        if not value:
            return value
        return self.placeholder


@dataclass
class PartialMasker(MaskingStrategy):
    """Masks part of the value, keeping a prefix and suffix visible."""

    prefix_chars: int = 2
    suffix_chars: int = 2
    mask_char: str = MASK_CHAR

    def mask(self, value: str) -> str:
        """Mask the middle portion of the value."""
        if not value:
            return value
        if len(value) <= self.prefix_chars + self.suffix_chars:
            return self.mask_char * len(value)
        prefix: str = value[:self.prefix_chars]
        suffix: str = value[-self.suffix_chars:]
        masked_len: int = len(value) - self.prefix_chars - self.suffix_chars
        return prefix + (self.mask_char * masked_len) + suffix


@dataclass
class MaskingResult:
    """Result of a masking operation."""

    original_text: str
    masked_text: str
    masked_count: int
    entities: list[PIIEntity]


class PrivacyMasker:
    """Applies masking to detected PII entities in text."""

    def __init__(
        self,
        config: "PrivacyAgentConfig",
        strategy: "MaskingStrategy | None" = None,
    ) -> None:
        """Initialize the masker.

        Args:
            config: Privacy agent configuration.
            strategy: Masking strategy to use. Defaults to RedactionMasker.
        """
        self._config: "PrivacyAgentConfig" = config
        self._strategy: MaskingStrategy = (
            strategy if strategy is not None else RedactionMasker()
        )

    def mask(
        self, text: str, entities: list[PIIEntity]
    ) -> MaskingResult:
        """Mask all PII entities in the text.

        Applies masking in reverse order of entity positions
        to preserve correct offsets.

        Args:
            text: Original text containing PII.
            entities: Detected PII entities to mask.

        Returns:
            MaskingResult with the masked text and count.

        Raises:
            MaskingError: If masking fails.
        """
        if not entities:
            return MaskingResult(
                original_text=text,
                masked_text=text,
                masked_count=0,
                entities=entities,
            )

        try:
            sorted_entities: list[PIIEntity] = sorted(
                entities, key=lambda e: e.start, reverse=True
            )
            masked_text: str = text

            for entity in sorted_entities:
                masked_value: str = self._strategy.mask(
                    entity.value
                )
                masked_text = (
                    masked_text[: entity.start]
                    + masked_value
                    + masked_text[entity.end :]
                )

            masked_count: int = len(entities)

            logger.info(
                "Masked %d entities in text of length %d",
                masked_count,
                len(text),
            )

            return MaskingResult(
                original_text=text,
                masked_text=masked_text,
                masked_count=masked_count,
                entities=entities,
            )
        except Exception as exc:
            msg: str = f"Masking operation failed: {exc}"
            raise MaskingError(msg) from exc


