"""Tests for configuration module."""
import json
import logging

import pytest
from fastapi import FastAPI

from src.config import JsonFormatter, Settings, get_settings, public_docs_enabled
from src.middleware import setup_cors


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.app_name == "Ticket Triage Agent"
        assert settings.environment == "development"
        assert settings.llm_provider == "mock"
        assert settings.port == 8000

    def test_custom_settings(self):
        """Test custom settings values."""
        settings = Settings(
            environment="production",
            llm_provider="openai",
            port=9000
        )

        assert settings.environment == "production"
        assert settings.llm_provider == "openai"
        assert settings.port == 9000

    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_docs_disabled_in_production_by_default(self):
        """Test that public docs are not exposed in production."""
        settings = Settings(environment="production")

        assert public_docs_enabled(settings) is False

    def test_docs_can_be_disabled_explicitly(self):
        """Test that docs can be disabled outside production."""
        settings = Settings(environment="development", expose_docs=False)

        assert public_docs_enabled(settings) is False

    def test_cors_rejects_wildcard_origin_with_credentials(self):
        """Test unsafe browser credential configuration is rejected."""
        app = FastAPI()

        with pytest.raises(ValueError, match="wildcard origin"):
            setup_cors(app, ["*"], allow_credentials=True)

    def test_json_formatter_escapes_log_messages(self):
        """Test structured logs remain valid JSON when messages contain quotes."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg='HTTP "quoted" message',
            args=(),
            exc_info=None,
        )

        formatted = JsonFormatter().format(record)

        assert json.loads(formatted)["message"] == 'HTTP "quoted" message'
