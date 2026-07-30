import os
def load_env(filepath):
    with open(filepath) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v
load_env('.env')

from agents.security_agent.llm.providers import get_provider
from agents.security_agent.config import settings

print(f"LLM_PROVIDER setting: {settings.LLM_PROVIDER}")
provider = get_provider()
print(f"Provider class: {provider.__class__.__name__}")
print(f"Health: {provider.health()}")
