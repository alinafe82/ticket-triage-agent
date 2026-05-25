"""Tests for service module."""

from src.config import Settings
from src.service import TriageResponse, TriageService


class TestTriageService:
    """Test cases for TriageService."""

    def test_create_service(self):
        """Test creating service with defaults."""
        settings = Settings(llm_provider="mock")
        service = TriageService.create(settings)

        assert service is not None
        assert service.router is not None
        assert service.llm is not None

    def test_triage_ticket_valid(self, triage_service):
        """Test triaging a valid ticket."""
        result = triage_service.triage_ticket(
            summary="Cannot reset password",
            description="User unable to reset password in Okta portal"
        )

        assert isinstance(result, TriageResponse)
        assert result.queue is not None
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.needs_review, bool)
        assert len(result.reply) > 0
        assert len(result.all_queues) > 0

    def test_triage_ticket_with_correlation_id(self, triage_service):
        """Test triaging with correlation ID."""
        correlation_id = "test-123"

        result = triage_service.triage_ticket(
            summary="VPN not working",
            description="Cannot connect to office VPN",
            correlation_id=correlation_id
        )

        assert result.correlation_id == correlation_id

    def test_triage_different_ticket_types(self, triage_service):
        """Test triaging different types of tickets."""
        # IT-Helpdesk ticket
        result1 = triage_service.triage_ticket(
            summary="Password reset",
            description="Need to reset Okta password"
        )
        assert result1.queue == "IT-Helpdesk"

        # IT-Procurement ticket
        result2 = triage_service.triage_ticket(
            summary="Equipment request",
            description="Need new laptop for development work"
        )
        assert result2.queue == "IT-Procurement"

        # Network ticket
        result3 = triage_service.triage_ticket(
            summary="VPN issue",
            description="VPN connection unstable on Mac"
        )
        assert result3.queue == "Network"

    def test_get_available_queues(self, triage_service):
        """Test getting available queues."""
        queues = triage_service.get_available_queues()

        assert isinstance(queues, list)
        assert len(queues) > 0
        assert "IT-Helpdesk" in queues

    def test_triage_validates_confidence(self, triage_service):
        """Test that confidence is always between 0 and 1."""
        for _ in range(10):
            result = triage_service.triage_ticket(
                summary="Random ticket",
                description="Some description"
            )
            assert 0.0 <= result.confidence <= 1.0

    def test_triage_all_queues_present(self, triage_service):
        """Test that all queues are included in results."""
        result = triage_service.triage_ticket(
            summary="Test",
            description="Test ticket"
        )

        available_queues = triage_service.get_available_queues()

        for queue in available_queues:
            assert queue in result.all_queues

    def test_triage_flags_low_confidence_for_review(self, mock_router, mock_llm):
        """Test confidence threshold creates a human review signal."""
        settings = Settings(llm_provider="mock", router_confidence_threshold=1.0)
        service = TriageService(mock_router, mock_llm, settings)

        result = service.triage_ticket(
            summary="Ambiguous issue",
            description="Something is slow somewhere",
        )

        assert result.needs_review is True
