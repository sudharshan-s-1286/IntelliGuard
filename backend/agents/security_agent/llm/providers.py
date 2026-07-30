"""LLM Provider Abstractions."""
import json
import logging
from abc import ABC, abstractmethod

from agents.security_agent.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for all LLM integrations."""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a raw string response from the LLM."""
        
    @abstractmethod
    def health(self) -> dict:
        """Health check for the provider."""

class MockProvider(LLMProvider):
    """Mock provider for testing or fallback when no API key is provided."""
    
    def __init__(self):
        self.model_name = "mock-model"
        
    async def generate(self, prompt: str) -> str:
        """Return a simulated JSON string."""
        logger.info(f"MockProvider generating response for prompt length {len(prompt)}")
        
        # Simple heuristic to simulate returning Safe for benign prompts
        lower_prompt = prompt.lower()
        if "machine learning" in lower_prompt or "french" in lower_prompt or "reverse a string" in lower_prompt or "summarize" in lower_prompt or "hello" in lower_prompt:
            mock_response = {
                "attack_category": "Safe",
                "confidence": 0.99,
                "reasoning": "Prompt appears to be a benign request.",
                "evidence": "",
                "recommendations": [],
                "uncertainty": "Low"
            }
        else:
            mock_response = {
                "attack_category": "Prompt Injection",
                "confidence": 0.85,
                "reasoning": "Mocked analysis based on keyword similarity.",
                "evidence": "Mocked evidence from context.",
                "recommendations": ["Sanitize input", "Block IP"],
                "uncertainty": "Low"
            }
        return json.dumps(mock_response)

    def health(self) -> dict:
        return {"status": "healthy", "provider": "mock"}

class GroqProvider(LLMProvider):
    """Integration with Groq API."""
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL_NAME
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self._is_mock = False
        except ImportError:
            logger.warning("openai package not installed. Falling back to MockProvider internally.")
            self._is_mock = True
            self.mock_fallback = MockProvider()

    async def generate(self, prompt: str) -> str:
        if self._is_mock or not self.api_key:
            if not self._is_mock:
                logger.warning("Groq API key missing. Falling back to MockProvider.")
                self.mock_fallback = MockProvider()
                self._is_mock = True
            return await self.mock_fallback.generate(prompt)

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API request failed: {e}")
            raise

    def health(self) -> dict:
        if self._is_mock or not self.api_key:
            return {"status": "degraded", "provider": "groq", "reason": "API Key or package missing"}
        return {"status": "healthy", "provider": "groq", "model": self.model_name}

def get_provider() -> LLMProvider:
    """Factory method to get the configured LLM provider."""
    provider_name = settings.LLM_PROVIDER.lower()
    
    if provider_name == "groq" or provider_name == "openai":
        return GroqProvider()
    # future providers: azure, anthropic, hf
    else:
        return MockProvider()
