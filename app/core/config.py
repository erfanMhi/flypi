"""
Configuration settings for the application.

This module defines the Settings class, which holds configuration
parameters for the application. It uses Pydantic's BaseSettings to
load environment variables and provides a cached function to access
these settings.
"""

from functools import lru_cache
from typing import Dict

from pydantic_settings import BaseSettings

from .component_config import get_component_config


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    LLM_API_TIMEOUT: float = 30.0
    MODEL_NAME: str = "gpt-4o"
    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 1024
    SEED: int = 42

    # Network settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # SSL/TLS Settings
    SSL_KEYFILE: str = "certs/key.pem"
    SSL_CERTFILE: str = "certs/cert.pem"
    USE_HTTPS: bool = True

    # Arize Phoenix settings
    PHOENIX_ENDPOINT: str = "http://localhost:4317"
    PHOENIX_PROJECT_NAME: str = "llm-service"

    # Concurrency settings
    MAX_PARALLEL_REQUESTS: int = 1

    @property
    def COMPONENT_DESCRIPTIONS(self) -> Dict[str, Dict[str, str]]:
        """Get component descriptions from individual TOML files."""
        return get_component_config().component_descriptions

    class Config:
        """Pydantic configuration for the Settings class."""
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 