"""ML-based ticket routing using scikit-learn."""
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .exceptions import ModelNotTrainedException, RouterException

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """Result of ticket routing prediction."""
    queue: str
    confidence: float
    all_predictions: dict[str, float]


@dataclass
class Router:
    """ML-based ticket router with TF-IDF and LogisticRegression."""

    vec: TfidfVectorizer
    clf: LogisticRegression
    labels: list[str]

    @classmethod
    def bootstrap(cls, training_data: list[tuple[str, str]] | None = None) -> "Router":
        """
        Bootstrap router with training data.

        Args:
            training_data: List of (text, label) tuples. Uses default if None.

        Returns:
            Trained Router instance.

        Raises:
            RouterException: If training fails.
        """
        try:
            if training_data is None:
                training_data = cls._get_default_training_data()

            if len(training_data) < 2:
                raise RouterException(
                    "Insufficient training data",
                    details={"required": 2, "provided": len(training_data)}
                )

            texts, labels = zip(*training_data, strict=False)
            unique_labels = list(set(labels))

            logger.info(
                f"Training router with {len(training_data)} examples "
                f"across {len(unique_labels)} queues"
            )

            # Train vectorizer and classifier
            vec = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
            X = vec.fit_transform(texts)

            clf = LogisticRegression(
                max_iter=200,
                class_weight='balanced',
                random_state=42
            )
            clf.fit(X, labels)

            logger.info("Router training completed successfully")
            return cls(vec, clf, unique_labels)

        except Exception as e:
            logger.error(f"Router training failed: {e}", exc_info=True)
            raise RouterException(f"Training failed: {e}") from e

    @staticmethod
    def _get_default_training_data() -> list[tuple[str, str]]:
        """Get default training data for bootstrapping."""
        return [
            ("Password reset failing repeatedly", "IT-Helpdesk"),
            ("Cannot login with Okta MFA", "IT-Helpdesk"),
            ("Okta MFA device change request", "IT-Helpdesk"),
            ("Email not syncing on mobile", "IT-Helpdesk"),
            ("New laptop request for developer", "IT-Procurement"),
            ("Need monitor and keyboard", "IT-Procurement"),
            ("Request software license for IntelliJ", "IT-Procurement"),
            ("Access to production S3 bucket", "Cloud-Access"),
            ("Need AWS IAM role for service", "Cloud-Access"),
            ("Azure resource group permissions", "Cloud-Access"),
            ("VPN connection unstable on Mac", "Network"),
            ("Cannot connect to office network", "Network"),
            ("Slow internet connection", "Network"),
            ("Request new Slack channel for team", "Collaboration"),
            ("Add users to Microsoft Teams", "Collaboration"),
            ("Zoom meeting room access", "Collaboration"),
        ]

    def predict(self, text: str) -> RoutingResult:
        """
        Predict queue and confidence for ticket text.

        Args:
            text: Ticket text to classify.

        Returns:
            RoutingResult with queue, confidence, and all predictions.

        Raises:
            RouterException: If prediction fails.
            ValidationException: If input is invalid.
        """
        try:
            if not text or not text.strip():
                raise RouterException("Empty ticket text provided")

            # Transform and predict
            X = self.vec.transform([text])
            proba = self.clf.predict_proba(X)[0]

            # Get all predictions
            all_predictions = {
                label: float(prob)
                for label, prob in zip(self.clf.classes_, proba, strict=False)
            }

            # Get best prediction
            idx = int(np.argmax(proba))
            best_label = self.clf.classes_[idx]
            best_confidence = float(proba[idx])

            logger.debug(
                f"Predicted queue: {best_label} "
                f"(confidence: {best_confidence:.2%})"
            )

            return RoutingResult(
                queue=best_label,
                confidence=best_confidence,
                all_predictions=all_predictions
            )

        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            raise RouterException(f"Prediction failed: {e}") from e

    def save(self, path: str) -> None:
        """
        Save router model to disk.

        Args:
            path: File path to save model.

        Raises:
            RouterException: If save fails.
        """
        try:
            model_path = Path(path)
            model_path.parent.mkdir(parents=True, exist_ok=True)

            with open(model_path, 'wb') as f:
                pickle.dump(self, f)

            logger.info(f"Router model saved to {path}")

        except Exception as e:
            logger.error(f"Failed to save model: {e}", exc_info=True)
            raise RouterException(f"Save failed: {e}") from e

    @classmethod
    def load(cls, path: str) -> "Router":
        """
        Load router model from disk.

        Args:
            path: File path to load model from.

        Returns:
            Loaded Router instance.

        Raises:
            RouterException: If load fails.
            ModelNotTrainedException: If model file doesn't exist.
        """
        try:
            model_path = Path(path)

            if not model_path.exists():
                raise ModelNotTrainedException(
                    f"Model not found at {path}",
                    details={"path": str(model_path.absolute())}
                )

            with open(model_path, 'rb') as f:
                router = pickle.load(f)

            logger.info(f"Router model loaded from {path}")
            return router

        except ModelNotTrainedException:
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise RouterException(f"Load failed: {e}") from e
