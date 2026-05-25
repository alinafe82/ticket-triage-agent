"""Application configuration management."""
import logging
from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Ticket Triage Agent"
    app_version: str = "0.2.0"
    environment: str = "development"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # LLM
    llm_provider: str = "mock"  # mock, openai, anthropic
    llm_api_key: str = ""
    llm_model: str = "gpt-3.5-turbo"
    llm_timeout: int = 30
    llm_max_retries: int = 3

    # ML Router
    router_model_path: str = "models/router.pkl"
    router_confidence_threshold: float = 0.5

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Monitoring
    enable_metrics: bool = True

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging(settings: Settings) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
