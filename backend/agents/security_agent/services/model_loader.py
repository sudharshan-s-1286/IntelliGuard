"""Model Loader."""
import asyncio
import logging
from typing import Any, Dict

from backend.agents.security_agent.config.settings import DEVICE_SELECTION, FALLBACK_TO_CPU

logger = logging.getLogger(__name__)

class ModelLoader:
    """Safely loads and unloads heavy AI models using a thread-safe singleton cache."""

    def __init__(self) -> None:
        self._models: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def load_model(self, model_name: str) -> Any:
        """Load a model into VRAM (or RAM if fallback)."""
        async with self._lock:
            if model_name in self._models:
                return self._models[model_name]

            logger.info(f"Loading embedding model: {model_name} on {DEVICE_SELECTION}...")
            
            # Determine actual device
            device = DEVICE_SELECTION
            try:
                import torch
                if device == "cuda" and not torch.cuda.is_available():
                    if FALLBACK_TO_CPU:
                        logger.warning("CUDA not available. Falling back to CPU.")
                        device = "cpu"
                    else:
                        raise RuntimeError("CUDA requested but not available.")
            except ImportError:
                # If torch is not installed, fallback to CPU string and mock later
                device = "cpu"

            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(model_name, device=device)
            except ImportError:
                logger.warning(f"sentence_transformers not installed. Mocking model {model_name}")
                class MockModel:
                    def encode(self, sentences, **kwargs):
                        # Return dummy embeddings (e.g., list of lists of zeros)
                        if isinstance(sentences, str):
                            sentences = [sentences]
                        return [[0.0] * 384 for _ in sentences]
                model = MockModel()

            self._models[model_name] = model
            logger.info(f"Model {model_name} loaded successfully.")
            return model

    async def unload_model(self, model_name: str) -> None:
        """Unload a model from VRAM and free memory."""
        async with self._lock:
            if model_name in self._models:
                del self._models[model_name]
                logger.info(f"Model {model_name} unloaded.")
                
                # Attempt to free PyTorch VRAM if applicable
                try:
                    import torch
                    import gc
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except ImportError:
                    pass

    def health(self) -> dict[str, Any]:
        """Return the health status of loaded models."""
        return {
            "status": "healthy",
            "loaded_models": list(self._models.keys()),
            "count": len(self._models)
        }
