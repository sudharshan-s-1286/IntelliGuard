"""Request Validator."""
from typing import Any

class RequestValidator:
    """Sanitizes prompt inputs."""

    @staticmethod
    def validate(request: Any) -> None:
        """
        Validate incoming AgentRequest payload.
        :raises ValidationError: If invalid.
        """
        # TODO: Implement length checks, character encoding validation
        pass
