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

    def fit(
        self,
        features: FloatArray,
        labels: IntArray,
        sample_weights: FloatArray | None = None,
    ) -> LogisticBaseline:
        design = np.column_stack((np.ones(features.shape[0]), features))
        weights = np.zeros(design.shape[1], dtype=np.float64)
        if sample_weights is None:
            sample_weights = np.ones(labels.size, dtype=np.float64)
        if sample_weights.shape != labels.shape:
            raise ValueError("sample weights must match labels")
        if np.any(sample_weights < 0.0) or not np.any(sample_weights > 0.0):
            raise ValueError("sample weights must be non-negative with positive total weight")
        normalizer = float(np.sum(sample_weights))
        for _ in range(self.iterations):
            scores = np.einsum("ij,j->i", design, weights, optimize=True)
            errors = (_sigmoid(scores) - labels) * sample_weights
            gradient = np.einsum("ij,i->j", design, errors, optimize=True)
            weights -= self.learning_rate * gradient / normalizer
        self.weights = weights
        return self

    def predict_proba(self, features: FloatArray) -> FloatArray:
        if self.weights is None:
            raise RuntimeError("the model must be fitted before prediction")
        design = np.column_stack((np.ones(features.shape[0]), features))
        scores = np.einsum("ij,j->i", design, self.weights, optimize=True)
        return _sigmoid(scores)

    def predict(self, features: FloatArray, threshold: float = 0.5) -> IntArray:
        return (self.predict_proba(features) >= threshold).astype(np.int64)
