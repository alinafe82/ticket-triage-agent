"""LLM interface for generating ticket responses."""
import logging
from abc import ABC, abstractmethod
from typing import Optional
from .exceptions import LLMException
from .config import Settings

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.timeout = settings.llm_timeout
        self.max_retries = settings.llm_max_retries

    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate completion for prompt.

        Args:
            prompt: Input prompt for LLM.
            max_tokens: Maximum tokens to generate.

        Returns:
            Generated text.

        Raises:
            LLMException: If generation fails.
        """
        pass

    def _validate_prompt(self, prompt: str) -> None:
        """Validate prompt input."""
        if not prompt or not prompt.strip():
            raise LLMException("Empty prompt provided")

        if len(prompt) > 10000:
            raise LLMException(
                "Prompt too long",
                details={"length": len(prompt), "max": 10000}
            )


class MockLLM(BaseLLM):
    """Mock LLM for testing and development."""

    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate mock response.

        Args:
            prompt: Input prompt (validated but not used).
            max_tokens: Maximum tokens (ignored in mock).

        Returns:
            Mock response text.
        """
        self._validate_prompt(prompt)

        logger.debug("Generating mock LLM response")

        # Extract queue from prompt if present
        queue = "the appropriate team"
        if "'" in prompt:
            try:
                queue = prompt.split("'")[1]
            except IndexError:
                pass

        return (
            f"Thank you for reaching out. I've routed your ticket to {queue}.\n\n"
            "To help us assist you better, I have a couple of questions:\n"
            "1. When did you first notice this issue?\n"
            "2. Is this blocking any critical work?\n\n"
            "Next steps:\n"
            "- We'll review your request and assess the priority\n"
            "- A team member will reach out within 4 business hours\n"
            "- In the meantime, please ensure all relevant details are documented"
        )


class OpenAILLM(BaseLLM):
    """OpenAI LLM integration (requires openai package)."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not settings.llm_api_key:
            raise LLMException(
                "OpenAI API key not configured",
                details={"provider": "openai"}
            )

        try:
            import openai
            self.client = openai.OpenAI(
                api_key=settings.llm_api_key,
                timeout=self.timeout
            )
            self.model = settings.llm_model
        except ImportError as e:
            raise LLMException(
                "OpenAI package not installed",
                details={"install": "pip install openai"}
            ) from e

    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate completion using OpenAI API."""
        self._validate_prompt(prompt)

        try:
            logger.debug(f"Calling OpenAI API with model {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )

            result = response.choices[0].message.content
            logger.info("OpenAI API call successful")

            return result or ""

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}", exc_info=True)
            raise LLMException(f"OpenAI API error: {e}") from e


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM integration (requires anthropic package)."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not settings.llm_api_key:
            raise LLMException(
                "Anthropic API key not configured",
                details={"provider": "anthropic"}
            )

        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=settings.llm_api_key,
                timeout=self.timeout
            )
            self.model = settings.llm_model or "claude-3-haiku-20240307"
        except ImportError as e:
            raise LLMException(
                "Anthropic package not installed",
                details={"install": "pip install anthropic"}
            ) from e

    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate completion using Anthropic API."""
        self._validate_prompt(prompt)

        try:
            logger.debug(f"Calling Anthropic API with model {self.model}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text
            logger.info("Anthropic API call successful")

            return result

        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}", exc_info=True)
            raise LLMException(f"Anthropic API error: {e}") from e


def get_llm(settings: Optional[Settings] = None) -> BaseLLM:
    """
    Factory function to get appropriate LLM instance.

    Args:
        settings: Application settings. Uses default if None.

    Returns:
        LLM instance based on configuration.

    Raises:
        LLMException: If provider is unknown.
    """
    if settings is None:
        from .config import get_settings
        settings = get_settings()

    provider = settings.llm_provider.lower()

    logger.info(f"Initializing LLM provider: {provider}")

    if provider == "mock":
        return MockLLM(settings)
    elif provider == "openai":
        return OpenAILLM(settings)
    elif provider == "anthropic":
        return AnthropicLLM(settings)
    else:
        raise LLMException(
            f"Unknown LLM provider: {provider}",
            details={
                "provider": provider,
                "supported": ["mock", "openai", "anthropic"]
            }
        )
