"""Tests for LLM module."""
import pytest

from src.config import Settings
from src.exceptions import LLMException
from src.llm import MockLLM, get_llm


class TestMockLLM:
    """Test cases for MockLLM."""

    def test_complete_valid_prompt(self):
        """Test completion with valid prompt."""
        settings = Settings(llm_provider="mock")
        llm = MockLLM(settings)

        result = llm.complete("Test prompt")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Thank you" in result

    def test_complete_extracts_queue(self):
        """Test that completion extracts queue from prompt."""
        settings = Settings(llm_provider="mock")
        llm = MockLLM(settings)

        result = llm.complete("Route to 'IT-Helpdesk' queue")

        assert "IT-Helpdesk" in result

    def test_complete_empty_prompt(self):
        """Test completion fails with empty prompt."""
        settings = Settings(llm_provider="mock")
        llm = MockLLM(settings)

        with pytest.raises(LLMException) as exc_info:
            llm.complete("")

        assert "Empty prompt" in str(exc_info.value)

    def test_complete_long_prompt(self):
        """Test completion fails with overly long prompt."""
        settings = Settings(llm_provider="mock")
        llm = MockLLM(settings)

        long_prompt = "a" * 10001

        with pytest.raises(LLMException) as exc_info:
            llm.complete(long_prompt)

        assert "too long" in str(exc_info.value)

    def test_complete_includes_questions(self):
        """Test that response includes clarifying questions."""
        settings = Settings(llm_provider="mock")
        llm = MockLLM(settings)

        result = llm.complete("Generate response")

        assert "1." in result
        assert "2." in result
        assert "?" in result

    def test_complete_includes_next_steps(self):
        """Test that response includes next steps."""
        settings = Settings(llm_provider="mock")
        llm = MockLLM(settings)

        result = llm.complete("Generate response")

        assert "Next steps:" in result or "Next" in result


class TestGetLLM:
    """Test cases for get_llm factory function."""

    def test_get_llm_mock_provider(self):
        """Test getting mock LLM provider."""
        settings = Settings(llm_provider="mock")
        llm = get_llm(settings)

        assert isinstance(llm, MockLLM)

    def test_get_llm_unknown_provider(self):
        """Test getting unknown provider raises exception."""
        settings = Settings(llm_provider="unknown")

        with pytest.raises(LLMException) as exc_info:
            get_llm(settings)

        assert "Unknown LLM provider" in str(exc_info.value)

    def test_get_llm_default_settings(self):
        """Test getting LLM with default settings."""
        llm = get_llm()

        assert llm is not None
        assert isinstance(llm, MockLLM)
