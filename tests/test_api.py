"""Tests for FastAPI endpoints."""
from fastapi import status

from src import app as app_module


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_ready_endpoint(self, client):
        """Test readiness check endpoint."""
        response = client.get("/ready")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "docs" in data


class TestQueueEndpoints:
    """Test cases for queue management endpoints."""

    def test_list_queues(self, client):
        """Test listing available queues."""
        response = client.get("/queues")

        assert response.status_code == status.HTTP_200_OK
        queues = response.json()
        assert isinstance(queues, list)
        assert len(queues) > 0
        assert "IT-Helpdesk" in queues


class TestTriageEndpoint:
    """Test cases for triage endpoint."""

    def test_triage_valid_ticket(self, client):
        """Test triaging a valid ticket."""
        ticket = {
            "summary": "Cannot reset password",
            "description": "User unable to reset password through Okta portal"
        }

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "queue" in data
        assert "confidence" in data
        assert "needs_review" in data
        assert "reply" in data
        assert "all_queues" in data
        assert 0.0 <= data["confidence"] <= 1.0

    def test_triage_returns_correlation_id(self, client):
        """Test that triage returns correlation ID."""
        ticket = {
            "summary": "VPN issue",
            "description": "VPN not connecting"
        }

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "correlation_id" in data
        assert data["correlation_id"] is not None

    def test_triage_has_correlation_id_header(self, client):
        """Test that response includes correlation ID header."""
        ticket = {
            "summary": "Test",
            "description": "Test description"
        }

        response = client.post("/triage", json=ticket)

        assert "x-correlation-id" in response.headers

    def test_triage_different_ticket_types(self, client):
        """Test triaging different types of tickets."""
        tickets = [
            {
                "summary": "Password reset",
                "description": "Need Okta password reset",
                "expected_queue": "IT-Helpdesk"
            },
            {
                "summary": "Laptop request",
                "description": "Need new MacBook Pro",
                "expected_queue": "IT-Procurement"
            },
            {
                "summary": "VPN problem",
                "description": "Cannot connect to VPN",
                "expected_queue": "Network"
            }
        ]

        for ticket_data in tickets:
            ticket = {
                "summary": ticket_data["summary"],
                "description": ticket_data["description"]
            }

            response = client.post("/triage", json=ticket)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["queue"] == ticket_data["expected_queue"]

    def test_triage_missing_summary(self, client):
        """Test triage fails with missing summary."""
        ticket = {"description": "Some description"}

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_missing_description(self, client):
        """Test triage fails with missing description."""
        ticket = {"summary": "Some summary"}

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_empty_summary(self, client):
        """Test triage fails with empty summary."""
        ticket = {
            "summary": "",
            "description": "Some description"
        }

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_empty_description(self, client):
        """Test triage fails with empty description."""
        ticket = {
            "summary": "Some summary",
            "description": ""
        }

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_summary_too_long(self, client):
        """Test triage fails with summary exceeding max length."""
        ticket = {
            "summary": "a" * 501,  # Max is 500
            "description": "Some description"
        }

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_description_too_long(self, client):
        """Test triage fails with description exceeding max length."""
        ticket = {
            "summary": "Some summary",
            "description": "a" * 5001  # Max is 5000
        }

        response = client.post("/triage", json=ticket)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_invalid_json(self, client):
        """Test triage fails with invalid JSON."""
        response = client.post(
            "/triage",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_triage_requires_api_key_when_configured(self, client, monkeypatch):
        """Test triage endpoint requires an API key only when configured."""
        monkeypatch.setattr(app_module.settings, "api_key", "test-key")
        ticket = {
            "summary": "VPN issue",
            "description": "VPN connection fails after password rotation",
        }

        missing_key = client.post("/triage", json=ticket)
        valid_key = client.post("/triage", json=ticket, headers={"X-API-Key": "test-key"})

        assert missing_key.status_code == status.HTTP_401_UNAUTHORIZED
        assert valid_key.status_code == status.HTTP_200_OK


class TestOpenAPIDocumentation:
    """Test cases for OpenAPI documentation."""

    def test_openapi_json_available(self, client):
        """Test that OpenAPI JSON is available."""
        response = client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_swagger_ui_available(self, client):
        """Test that Swagger UI is available."""
        response = client.get("/docs")

        assert response.status_code == status.HTTP_200_OK

    def test_redoc_available(self, client):
        """Test that ReDoc is available."""
        response = client.get("/redoc")

        assert response.status_code == status.HTTP_200_OK
