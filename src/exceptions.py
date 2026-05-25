"""Custom application exceptions."""
from typing import Any


class TriageServiceException(Exception):
    """Base exception for triage service."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RouterException(TriageServiceException):
    """Exception raised during ticket routing."""
    pass


class LLMException(TriageServiceException):
    """Exception raised during LLM operations."""
    pass


class ModelNotTrainedException(RouterException):
    """Exception raised when router model is not trained."""
    pass


class ConfigurationException(TriageServiceException):
    """Exception raised for configuration errors."""
    pass


class ValidationException(TriageServiceException):
    """Exception raised for input validation errors."""
    pass
