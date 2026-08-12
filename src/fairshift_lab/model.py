"""Small, inspectable model families: logistic regression and a shallow decision tree."""

from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass(frozen=True)
class _TreeNode:
    """One node of a deterministic, depth-limited binary decision tree."""

    positive_rate: float
    feature_index: int | None = None
    threshold: float | None = None
    left: _TreeNode | None = None
    right: _TreeNode | None = None

    @property
    def is_leaf(self) -> bool:
        return self.feature_index is None


def _weighted_gini(weights_positive: float, weights_total: float) -> float:
    if weights_total <= 0.0:
        return 0.0
    proportion = weights_positive / weights_total
    return 2.0 * proportion * (1.0 - proportion)


def _leaf_rate(weights_positive: float, weights_total: float) -> float:
    """Return a Laplace-smoothed leaf probability that never saturates to 0 or 1."""

    return (weights_positive + 1.0) / (weights_total + 2.0)


@dataclass
class ShallowDecisionTree:
    """A greedy, deterministic, depth-limited CART-style classifier.

    Splits are chosen to minimize weighted Gini impurity. Ties in the search break on the
    lowest feature index, then the lowest candidate threshold — a deterministic tie-break
    rule, not a substantive fairness or performance judgment. Leaf probabilities use add-one
    Laplace smoothing so probabilistic metrics such as Brier score and expected calibration
    error remain well defined even for pure leaves.
    """

    max_depth: int = 3
    min_samples_leaf: int = 20
    root: _TreeNode | None = field(default=None, repr=False)

    def fit(
        self,
        features: FloatArray,
        labels: IntArray,
        sample_weights: FloatArray | None = None,
    ) -> ShallowDecisionTree:
        if self.max_depth < 0:
            raise ValueError("max_depth must be non-negative")
        if self.min_samples_leaf < 1:
            raise ValueError("min_samples_leaf must be at least one")
        if sample_weights is None:
            sample_weights = np.ones(labels.size, dtype=np.float64)
        if sample_weights.shape != labels.shape:
            raise ValueError("sample weights must match labels")
        if np.any(sample_weights < 0.0) or not np.any(sample_weights > 0.0):
            raise ValueError("sample weights must be non-negative with positive total weight")
        indices = np.arange(labels.size, dtype=np.int64)
        self.root = self._build(features, labels, sample_weights, indices, depth=0)
        return self

    def _build(
        self,
        features: FloatArray,
        labels: IntArray,
        weights: FloatArray,
        indices: IntArray,
        depth: int,
    ) -> _TreeNode:
        node_weights = weights[indices]
        node_total = float(np.sum(node_weights))
        node_is_positive = (labels[indices] == 1).astype(np.float64)
        node_positive = float(np.sum(node_weights * node_is_positive))
        leaf_rate = _leaf_rate(node_positive, node_total)
        if depth >= self.max_depth or indices.size < 2 * self.min_samples_leaf or node_total <= 0.0:
            return _TreeNode(positive_rate=leaf_rate)
        parent_impurity = _weighted_gini(node_positive, node_total)

        best: tuple[float, int, float, IntArray, IntArray] | None = None
        for feature_index in range(features.shape[1]):
            column = features[indices, feature_index]
            order = np.argsort(column, kind="stable")
            sorted_indices = indices[order]
            sorted_values = column[order]
            sorted_weights = node_weights[order]
            sorted_positive = node_is_positive[order] * sorted_weights

            cumulative_total = np.cumsum(sorted_weights)
            cumulative_positive = np.cumsum(sorted_positive)
            left_total = cumulative_total[:-1]
            left_positive = cumulative_positive[:-1]
            right_total = node_total - left_total
            right_positive = node_positive - left_positive

            counts = np.arange(1, sorted_values.size)
            valid = (
                (sorted_values[:-1] != sorted_values[1:])
                & (counts >= self.min_samples_leaf)
                & ((sorted_values.size - counts) >= self.min_samples_leaf)
            )
            if not np.any(valid):
                continue

            safe_left_total = np.where(left_total > 0, left_total, 1.0)
            safe_right_total = np.where(right_total > 0, right_total, 1.0)
            left_proportion = left_positive / safe_left_total
            right_proportion = right_positive / safe_right_total
            left_gini = np.where(
                left_total > 0, 2.0 * left_proportion * (1.0 - left_proportion), 0.0
            )
            right_gini = np.where(
                right_total > 0, 2.0 * right_proportion * (1.0 - right_proportion), 0.0
            )
            impurity = (left_total * left_gini + right_total * right_gini) / node_total
            impurity = np.where(valid, impurity, np.inf)
            position = int(np.argmin(impurity))
            if not np.isfinite(impurity[position]):
                continue
            threshold = float((sorted_values[position] + sorted_values[position + 1]) / 2.0)
            left_indices = sorted_indices[: position + 1]
            right_indices = sorted_indices[position + 1 :]
            candidate = (
                float(impurity[position]),
                feature_index,
                threshold,
                left_indices,
                right_indices,
            )
            if best is None or (candidate[0], candidate[1], candidate[2]) < (
                best[0],
                best[1],
                best[2],
            ):
                best = candidate

        if best is None:
            return _TreeNode(positive_rate=leaf_rate)
        impurity_value, feature_index, threshold, left_indices, right_indices = best
        if impurity_value >= parent_impurity:
            return _TreeNode(positive_rate=leaf_rate)
        left_child = self._build(features, labels, weights, left_indices, depth + 1)
        right_child = self._build(features, labels, weights, right_indices, depth + 1)
        return _TreeNode(
            positive_rate=leaf_rate,
            feature_index=feature_index,
            threshold=threshold,
            left=left_child,
            right=right_child,
        )

    def predict_proba(self, features: FloatArray) -> FloatArray:
        if self.root is None:
            raise RuntimeError("the model must be fitted before prediction")
        result = np.empty(features.shape[0], dtype=np.float64)
        for row in range(features.shape[0]):
            node = self.root
            while not node.is_leaf:
                assert node.feature_index is not None and node.threshold is not None
                if features[row, node.feature_index] <= node.threshold:
                    assert node.left is not None
                    node = node.left
                else:
                    assert node.right is not None
                    node = node.right
            result[row] = node.positive_rate
        return result

    def predict(self, features: FloatArray, threshold: float = 0.5) -> IntArray:
        return (self.predict_proba(features) >= threshold).astype(np.int64)
