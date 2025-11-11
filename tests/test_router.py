"""Tests for ML router module."""
import pytest
import tempfile
from pathlib import Path

from src.router import Router, RoutingResult
from src.exceptions import RouterException, ModelNotTrainedException


class TestRouter:
    """Test cases for Router class."""

    def test_bootstrap_default_data(self):
        """Test router bootstrapping with default data."""
        router = Router.bootstrap()

        assert router is not None
        assert router.vec is not None
        assert router.clf is not None
        assert len(router.labels) > 0

    def test_bootstrap_custom_data(self):
        """Test router bootstrapping with custom training data."""
        training_data = [
            ("Test ticket 1", "Queue-A"),
            ("Test ticket 2", "Queue-B"),
            ("Test ticket 3", "Queue-A"),
        ]

        router = Router.bootstrap(training_data)

        assert router is not None
        assert len(router.labels) == 2
        assert "Queue-A" in router.labels
        assert "Queue-B" in router.labels

    def test_bootstrap_insufficient_data(self):
        """Test router fails with insufficient training data."""
        training_data = [("Single ticket", "Queue-A")]

        with pytest.raises(RouterException) as exc_info:
            Router.bootstrap(training_data)

        assert "Insufficient training data" in str(exc_info.value)

    def test_predict_valid_text(self):
        """Test prediction with valid ticket text."""
        router = Router.bootstrap()
        result = router.predict("Cannot reset my password in Okta")

        assert isinstance(result, RoutingResult)
        assert isinstance(result.queue, str)
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.all_predictions) > 0
        assert result.queue == "IT-Helpdesk"

    def test_predict_different_queues(self):
        """Test predictions for different queue types."""
        router = Router.bootstrap()

        # Test IT-Helpdesk
        result1 = router.predict("MFA device not working Okta password")
        assert result1.queue == "IT-Helpdesk"

        # Test IT-Procurement
        result2 = router.predict("Need new monitor and keyboard equipment")
        assert result2.queue == "IT-Procurement"

        # Test Cloud-Access
        result3 = router.predict("Request AWS S3 bucket IAM role access")
        assert result3.queue == "Cloud-Access"

        # Test Network
        result4 = router.predict("VPN connection unstable network issue slow internet")
        assert result4.queue == "Network"

    def test_predict_empty_text(self):
        """Test prediction fails with empty text."""
        router = Router.bootstrap()

        with pytest.raises(RouterException) as exc_info:
            router.predict("")

        assert "Empty ticket text" in str(exc_info.value)

    def test_predict_whitespace_only(self):
        """Test prediction fails with whitespace-only text."""
        router = Router.bootstrap()

        with pytest.raises(RouterException):
            router.predict("   \n\t  ")

    def test_all_predictions_sum_to_one(self):
        """Test that all prediction probabilities sum to approximately 1.0."""
        router = Router.bootstrap()
        result = router.predict("Test ticket")

        total_prob = sum(result.all_predictions.values())
        assert abs(total_prob - 1.0) < 0.01

    def test_save_and_load_model(self):
        """Test saving and loading router model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "router.pkl"

            # Train and save
            router = Router.bootstrap()
            original_prediction = router.predict("Password reset issue")
            router.save(str(model_path))

            assert model_path.exists()

            # Load and compare
            loaded_router = Router.load(str(model_path))
            loaded_prediction = loaded_router.predict("Password reset issue")

            assert loaded_prediction.queue == original_prediction.queue
            assert abs(loaded_prediction.confidence - original_prediction.confidence) < 0.01

    def test_load_nonexistent_model(self):
        """Test loading non-existent model raises exception."""
        with pytest.raises(ModelNotTrainedException):
            Router.load("/nonexistent/path/model.pkl")

    def test_confidence_values(self):
        """Test that confidence values are reasonable."""
        router = Router.bootstrap()

        # High confidence prediction
        result = router.predict(
            "Cannot login with Okta MFA password reset failing repeatedly"
        )

        assert result.confidence > 0.3  # Should have decent confidence
        assert result.queue in router.labels
