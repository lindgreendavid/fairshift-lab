"""A small, inspectable logistic-regression baseline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fairshift_lab.data import FloatArray, IntArray


def _sigmoid(values: FloatArray) -> FloatArray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -35.0, 35.0)))


@dataclass
class LogisticBaseline:
    """Binary logistic regression trained with full-batch gradient descent."""

    learning_rate: float = 0.2
    iterations: int = 800
    weights: FloatArray | None = None

    def fit(self, features: FloatArray, labels: IntArray) -> LogisticBaseline:
        design = np.column_stack((np.ones(features.shape[0]), features))
        weights = np.zeros(design.shape[1], dtype=np.float64)
        for _ in range(self.iterations):
            errors = _sigmoid(design @ weights) - labels
            weights -= self.learning_rate * (design.T @ errors) / labels.size
        self.weights = weights
        return self

    def predict_proba(self, features: FloatArray) -> FloatArray:
        if self.weights is None:
            raise RuntimeError("the model must be fitted before prediction")
        design = np.column_stack((np.ones(features.shape[0]), features))
        return _sigmoid(design @ self.weights)

    def predict(self, features: FloatArray, threshold: float = 0.5) -> IntArray:
        return (self.predict_proba(features) >= threshold).astype(np.int64)
