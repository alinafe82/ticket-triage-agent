"""Tests for configuration module."""
from src.config import Settings, get_settings


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
