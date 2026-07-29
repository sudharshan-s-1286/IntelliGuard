"""Configuration settings for Orchestrator."""
import os

AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", 10))
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT", 5))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", 3))
DISCOVERY_INTERVAL = int(os.getenv("DISCOVERY_INTERVAL", 60))
HEALTH_INTERVAL = int(os.getenv("HEALTH_INTERVAL", 30))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "True").lower() == "true"
ROUTING_RULES = os.getenv("ROUTING_RULES", "default")
