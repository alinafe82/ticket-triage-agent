from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class Router:
    vec: TfidfVectorizer
    clf: LogisticRegression
    labels: List[str]

    @classmethod
    def bootstrap(cls) -> "Router":
        data = [
            ("Password reset failing", "IT-Helpdesk"),
            ("Okta MFA device change", "IT-Helpdesk"),
            ("New laptop request", "IT-Procurement"),
            ("Access to S3 bucket", "Cloud-Access"),
            ("VPN unstable on Mac", "Network"),
            ("Request new Slack channel", "Collaboration"),
        ]
        texts, labels = zip(*data)
        vec = TfidfVectorizer()
        X = vec.fit_transform(texts)
        clf = LogisticRegression(max_iter=200).fit(X, labels)
        return cls(vec, clf, list(set(labels)))

    def predict(self, text: str) -> Tuple[str, float]:
        X = self.vec.transform([text])
        proba = self.clf.predict_proba(X)[0]
        idx = proba.argmax()
        return self.clf.classes_[idx], float(proba[idx])
