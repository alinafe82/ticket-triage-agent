"""Basic integration tests."""
import pytest
from src.router import Router


def test_router_predict():
    """Test basic router prediction."""
    router = Router.bootstrap()
    result = router.predict("Need to reset a password")

    assert isinstance(result.queue, str)
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.all_predictions) > 0


def test_router_helpdesk_routing():
    """Test that password issues route to helpdesk."""
    router = Router.bootstrap()
    result = router.predict("Password reset failing Okta MFA issue")

    assert result.queue == "IT-Helpdesk"
    assert result.confidence > 0.0
