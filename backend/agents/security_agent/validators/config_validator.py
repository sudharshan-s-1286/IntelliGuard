"""Config Validator."""
from typing import Any


class ConfigValidator:
    """Ensures configuration settings are valid before startup."""

    @staticmethod
    def validate(config: Any) -> None:
        """Validate agent configuration."""
