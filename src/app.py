"""FastAPI application for ticket triage service."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .config import get_settings, public_docs_enabled, setup_logging
from .exceptions import TriageServiceException
from .middleware import RequestLoggingMiddleware, setup_cors
from .service import TriageService

# Initialize settings and logging
settings = get_settings()
setup_logging(settings)
logger = logging.getLogger(__name__)
docs_enabled = public_docs_enabled(settings)

# Global service instance
triage_service: TriageService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    global triage_service

    logger.info("Starting Ticket Triage Agent...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.llm_provider}")

    try:
        # Initialize service
        triage_service = TriageService.create(settings)
        logger.info("Service initialized successfully")

        yield

    except Exception as e:
        logger.error(f"Failed to initialize service: {e}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down Ticket Triage Agent...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Hybrid ML + LLM ticket routing and response generation service",
    lifespan=lifespan,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
setup_cors(app, settings.cors_origins, allow_credentials=settings.cors_allow_credentials)


# Request/Response Models
class TicketRequest(BaseModel):
    """Request model for ticket triage."""
    summary: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Brief summary of the issue"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Detailed description of the issue"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": "Cannot reset password",
                "description": "User is unable to reset their password through the Okta portal. "
                              "Error message: 'Invalid token'. Issue started this morning."
            }
        }
    )


class TriageResult(BaseModel):
    """Response model for ticket triage."""
    queue: str = Field(..., description="Assigned support queue")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    reply: str = Field(..., description="Generated response message")
    all_queues: dict[str, float] = Field(
        ...,
        description="Confidence scores for all queues"
    )
    correlation_id: str | None = Field(None, description="Request correlation ID")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str | None = None
    correlation_id: str | None = None


# Exception Handlers
@app.exception_handler(TriageServiceException)
async def triage_exception_handler(request: Request, exc: TriageServiceException):
    """Handle triage service exceptions."""
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.error(
        f"Triage error: {exc.message}",
        extra={
            "correlation_id": correlation_id,
            "details": exc.details
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.message,
            "detail": str(exc.details) if exc.details else None,
            "correlation_id": correlation_id
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.warning(
        "Validation error",
        extra={
            "correlation_id": correlation_id,
            "errors": exc.errors()
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "correlation_id": correlation_id
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.error(
        f"Unexpected error: {exc}",
        extra={"correlation_id": correlation_id},
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None,
            "correlation_id": correlation_id
        }
    )


# API Endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns basic service status and version information.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment
    )


@app.get("/ready", response_model=HealthResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint.

    Verifies that the service is ready to handle requests.
    """
    if triage_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not initialized"
        )

    return HealthResponse(
        status="ready",
        version=settings.app_version,
        environment=settings.environment
    )


@app.get("/queues", response_model=list[str], tags=["Info"])
async def list_queues():
    """
    List available ticket queues.

    Returns all queue names that tickets can be routed to.
    """
    if triage_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not initialized"
        )

    return triage_service.get_available_queues()


@app.post("/triage", response_model=TriageResult, tags=["Triage"])
async def triage_ticket(request: Request, ticket: TicketRequest):
    """
    Triage a support ticket.

    Routes the ticket to an appropriate queue using ML classification
    and generates an empathetic response using LLM.

    Args:
        ticket: Ticket with summary and description.

    Returns:
        Triage result with queue assignment, confidence, and generated reply.

    Raises:
        HTTPException: If service is unavailable or triage fails.
    """
    if triage_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not initialized"
        )

    correlation_id = getattr(request.state, "correlation_id", None)

    logger.info(
        "Received triage request",
        extra={
            "correlation_id": correlation_id,
            "summary_length": len(ticket.summary),
            "description_length": len(ticket.description),
        }
    )

    try:
        result = triage_service.triage_ticket(
            summary=ticket.summary,
            description=ticket.description,
            correlation_id=correlation_id
        )

        return TriageResult(
            queue=result.queue,
            confidence=result.confidence,
            reply=result.reply,
            all_queues=result.all_queues,
            correlation_id=correlation_id
        )

    except TriageServiceException:
        # Re-raise to be handled by exception handler
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error in triage: {e}",
            extra={"correlation_id": correlation_id},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Triage failed: {str(e)}"
        ) from e


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if docs_enabled else None,
        "health": "/health"
    }
