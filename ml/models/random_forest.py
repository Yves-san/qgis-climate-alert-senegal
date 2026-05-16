"""Random Forest classifier for drought / risk classification."""
from __future__ import annotations
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib


class DroughtClassifier:
    LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def __init__(self, n_estimators: int = 200, random_state: int = 42):
        self.model   = RandomForestClassifier(n_estimators=n_estimators,
                                              random_state=random_state,
                                              class_weight="balanced")
        self.scaler  = StandardScaler()
        self.trained = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs, y)
        self.trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.trained:
            # Heuristic fallback
            scores = X[:, 0] / 40 + (1 - X[:, 1] / 100)
            return np.array([self.LABELS[min(int(s * 2), 3)] for s in scores])
        return self.model.predict(self.scaler.transform(X))

    def save(self, path: str = "ml/saved_models/rf_model.pkl") -> None:
        joblib.dump({"model": self.model, "scaler": self.scaler}, path)

    @classmethod
    def load(cls, path: str = "ml/saved_models/rf_model.pkl") -> "DroughtClassifier":
        d = joblib.load(path)
        obj = cls()
        obj.model, obj.scaler, obj.trained = d["model"], d["scaler"], True
        return obj
