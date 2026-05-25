"""Custom middleware for request processing."""
import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and adding correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging and timing."""
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Log request
        start_time = time.time()
        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )

        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Add headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(duration)

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "status_code": response.status_code,
                    "duration": duration
                }
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "correlation_id": correlation_id,
                    "error": str(e),
                    "duration": duration
                },
                exc_info=True
            )
            raise


def setup_cors(app, origins: list[str], allow_credentials: bool = False) -> None:
    """Configure CORS middleware."""
    if allow_credentials and "*" in origins:
        raise ValueError("CORS cannot allow credentials with a wildcard origin")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
