"""Pytest fixtures and configuration."""
import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.config import Settings
from src.router import Router
from src.llm import MockLLM
from src.service import TriageService


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        environment="test",
        debug=True,
        llm_provider="mock",
        log_level="DEBUG"
    )


@pytest.fixture
def mock_router():
    """Create mock router with test data."""
    return Router.bootstrap()


@pytest.fixture
def mock_llm(test_settings):
    """Create mock LLM."""
    return MockLLM(test_settings)


@pytest.fixture
def triage_service(mock_router, mock_llm, test_settings):
    """Create triage service with mocks."""
    return TriageService(mock_router, mock_llm, test_settings)


@pytest.fixture
def client():
    """Create test client with properly initialized app."""
    # Initialize the service before creating the client
    from src.app import app, settings
    from src.service import TriageService

    # Set the global triage_service
    app_module.triage_service = TriageService.create(settings)

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app_module.triage_service = None
