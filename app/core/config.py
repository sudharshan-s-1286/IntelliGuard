from functools import lru_cache
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings powered by Pydantic v2 BaseSettings.
    Loads configurations from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core Application Settings
    APP_NAME: str = "Trust-Agent"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"

    # Security & CORS
    ALLOWED_HOSTS: Union[List[str], str] = ["*"]

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: Union[List[str], str]) -> List[str]:
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    return json.loads(value)
                except Exception:
                    pass
            return [host.strip() for host in value.split(",") if host.strip()]
        return value

    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.ENVIRONMENT.lower() in ("production", "prod")

    @property
    def is_development(self) -> bool:
        """Check if application is running in development mode."""
        return self.ENVIRONMENT.lower() in ("development", "dev")


@lru_cache
def get_settings() -> Settings:
    """
    Retrieves cached application settings instance.
    """
    return Settings()


settings = get_settings()
