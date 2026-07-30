from agents.security_agent.config import settings
from agents.security_agent.llm.providers import get_provider

print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"LLM_API_KEY: {settings.LLM_API_KEY[:5]}...")
provider = get_provider()
print(f"Provider class: {provider.__class__.__name__}")
print(f"Health: {provider.health()}")
