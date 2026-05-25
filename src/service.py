"""Business logic layer for ticket triage service."""
import logging
from dataclasses import dataclass

from .config import Settings
from .exceptions import TriageServiceException
from .llm import BaseLLM, get_llm
from .router import Router

logger = logging.getLogger(__name__)


@dataclass
class TriageResponse:
    """Complete triage response with routing and reply."""
    queue: str
    confidence: float
    reply: str
    all_queues: dict[str, float]
    correlation_id: str | None = None


class TriageService:
    """Service for triaging tickets with ML routing and LLM responses."""

    def __init__(
        self,
        router: Router,
        llm: BaseLLM,
        settings: Settings
    ):
        """
        Initialize triage service.

        Args:
            router: Trained ML router for ticket classification.
            llm: LLM instance for generating responses.
            settings: Application settings.
        """
        self.router = router
        self.llm = llm
        self.settings = settings
        logger.info("TriageService initialized")

    @classmethod
    def create(cls, settings: Settings | None = None) -> "TriageService":
        """
        Factory method to create service with default components.

        Args:
            settings: Application settings. Uses default if None.

        Returns:
            Initialized TriageService instance.

        Raises:
            TriageServiceException: If initialization fails.
        """
        if settings is None:
            from .config import get_settings
            settings = get_settings()

        try:
            # Initialize router
            logger.info("Initializing router...")
            router = Router.bootstrap()

            # Initialize LLM
            logger.info("Initializing LLM...")
            llm = get_llm(settings)

            return cls(router, llm, settings)

        except Exception as e:
            logger.error(f"Service initialization failed: {e}", exc_info=True)
            raise TriageServiceException(
                f"Failed to initialize service: {e}"
            ) from e

    def triage_ticket(
        self,
        summary: str,
        description: str,
        correlation_id: str | None = None
    ) -> TriageResponse:
        """
        Triage a ticket with ML routing and LLM response generation.

        Args:
            summary: Ticket summary/title.
            description: Detailed ticket description.
            correlation_id: Optional correlation ID for tracking.

        Returns:
            TriageResponse with queue, confidence, and generated reply.

        Raises:
            TriageServiceException: If triage fails.
        """
        try:
            # Combine summary and description
            ticket_text = f"{summary}\n{description}"

            logger.info(
                "Triaging ticket",
                extra={
                    "correlation_id": correlation_id,
                    "summary_length": len(summary),
                    "description_length": len(description)
                }
            )

            # Route ticket
            routing_result = self.router.predict(ticket_text)

            logger.info(
                f"Ticket routed to {routing_result.queue}",
                extra={
                    "correlation_id": correlation_id,
                    "queue": routing_result.queue,
                    "confidence": routing_result.confidence
                }
            )

            # Generate LLM response
            prompt = self._create_prompt(routing_result.queue, summary, description)
            reply = self.llm.complete(prompt)

            logger.info(
                "LLM response generated",
                extra={
                    "correlation_id": correlation_id,
                    "reply_length": len(reply)
                }
            )

            return TriageResponse(
                queue=routing_result.queue,
                confidence=routing_result.confidence,
                reply=reply,
                all_queues=routing_result.all_predictions,
                correlation_id=correlation_id
            )

        except Exception as e:
            logger.error(
                f"Triage failed: {e}",
                extra={"correlation_id": correlation_id},
                exc_info=True
            )
            raise TriageServiceException(f"Triage failed: {e}") from e

    def _create_prompt(self, queue: str, summary: str, description: str) -> str:
        """
        Create prompt for LLM response generation.

        Args:
            queue: Assigned queue name.
            summary: Ticket summary.
            description: Ticket description.

        Returns:
            Formatted prompt string.
        """
        return (
            f"You are a helpful IT support assistant. A support ticket has been "
            f"routed to the '{queue}' queue.\n\n"
            f"Ticket Summary: {summary}\n"
            f"Ticket Description: {description}\n\n"
            f"Write a professional, empathetic response that:\n"
            f"1. Acknowledges the ticket and confirms the routing\n"
            f"2. Asks 2 clarifying questions to better understand the issue\n"
            f"3. Lists the next steps the team will take\n\n"
            f"Keep the response concise and professional."
        )

    def get_available_queues(self) -> list[str]:
        """
        Get list of available ticket queues.

        Returns:
            List of queue names.
        """
        return self.router.labels
