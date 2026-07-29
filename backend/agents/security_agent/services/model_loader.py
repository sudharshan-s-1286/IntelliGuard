"""Model Loader."""
from typing import Any

class ModelLoader:
    """Safely loads and unloads heavy AI models."""

    def __init__(self) -> None:
        pass

    async def load_model(self, model_name: str) -> Any:
        """Load a model into VRAM."""
        # TODO: Load model
        pass

    async def unload_model(self, model_name: str) -> None:
        """Unload a model from VRAM."""
        # TODO: Unload model
        pass
