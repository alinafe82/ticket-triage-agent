"""Application configuration management."""
import json
import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    api_key: str = ""
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = False
    expose_docs: bool = True

    # LLM
    llm_provider: str = "mock"  # mock, openai, anthropic
    llm_api_key: str = ""
    llm_model: str = ""
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


class JsonFormatter(logging.Formatter):
    """Small JSON formatter for local structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in (
            "correlation_id",
            "method",
            "path",
            "status_code",
            "duration",
            "queue",
            "confidence",
            "needs_review",
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def public_docs_enabled(settings: Settings) -> bool:
    """Return whether interactive API docs should be publicly exposed."""
    production_envs = {"prod", "production"}
    return settings.expose_docs and settings.environment.lower() not in production_envs


def setup_logging(settings: Settings) -> None:
    """Configure application logging."""
    if settings.log_format == "json":
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            handlers=[handler],
            force=True,
        )
        return

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
