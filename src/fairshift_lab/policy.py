"""Transparent decision policies for cost and group-gap trade-off studies."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fairshift_lab.calibration import brier_score, calibration_summary
from fairshift_lab.data import FloatArray, IntArray
from fairshift_lab.metrics import group_rates, roc_auc
from fairshift_lab.sensitivity import DEFAULT_THRESHOLDS


@dataclass(frozen=True)
class PolicyMetrics:
    """Decision and probability measurements for one held-out population."""

    accuracy: float
    expected_cost: float
    demographic_parity_difference: float
    equal_opportunity_difference: float
    equalized_odds_difference: float
    brier_score: float
    expected_calibration_error: float


def joint_reweighing_weights(labels: IntArray, sensitive: IntArray) -> FloatArray:
    """Return Kamiran-Calders-style weights making A and Y independent in expectation."""

    if labels.shape != sensitive.shape or labels.ndim != 1:
        raise ValueError("labels and sensitive values must be matching one-dimensional arrays")
    if labels.size == 0:
        raise ValueError("reweighing requires at least one observation")
    weights = np.empty(labels.size, dtype=np.float64)
    total = float(labels.size)
    for group in (0, 1):
        group_count = int(np.sum(sensitive == group))
        for label in (0, 1):
            label_count = int(np.sum(labels == label))
            mask = (sensitive == group) & (labels == label)
            joint_count = int(np.sum(mask))
            if joint_count == 0:
                raise ValueError("reweighing requires every group-label cell to be populated")
            weights[mask] = (group_count * label_count) / (total * joint_count)
    return weights


def predictions_for_thresholds(
    probabilities: FloatArray,
    sensitive: IntArray,
    threshold_group_zero: float,
    threshold_group_one: float,
) -> IntArray:
    """Apply explicit group-conditional thresholds."""

    thresholds = np.where(sensitive == 0, threshold_group_zero, threshold_group_one)
    return (probabilities >= thresholds).astype(np.int64)


def normalized_expected_cost(
    labels: IntArray,
    predictions: IntArray,
    false_negative_cost: float,
    false_positive_cost: float = 1.0,
) -> float:
    """Return per-person error cost normalized to the larger declared unit cost."""

    if false_negative_cost <= 0.0 or false_positive_cost <= 0.0:
        raise ValueError("error costs must be positive")
    false_negatives = int(np.sum((labels == 1) & (predictions == 0)))
    false_positives = int(np.sum((labels == 0) & (predictions == 1)))
    raw = false_negative_cost * false_negatives + false_positive_cost * false_positives
    return float(raw / (labels.size * max(false_negative_cost, false_positive_cost)))


def evaluate_policy(
    labels: IntArray,
    probabilities: FloatArray,
    sensitive: IntArray,
    threshold_group_zero: float,
    threshold_group_one: float,
    false_negative_cost: float,
    calibration_bins: int = 10,
) -> PolicyMetrics:
    """Evaluate one declared policy without selecting or changing it."""

    predictions = predictions_for_thresholds(
        probabilities, sensitive, threshold_group_zero, threshold_group_one
    )
    group_zero = group_rates(labels, predictions, sensitive, 0)
    group_one = group_rates(labels, predictions, sensitive, 1)
    true_positive_gap = abs(group_one.true_positive_rate - group_zero.true_positive_rate)
    false_positive_gap = abs(group_one.false_positive_rate - group_zero.false_positive_rate)
    calibration = calibration_summary(labels, probabilities, calibration_bins)
    calibration_error = calibration["expected_calibration_error"]
    assert isinstance(calibration_error, float)
    return PolicyMetrics(
        accuracy=float(np.mean(predictions == labels)),
        expected_cost=normalized_expected_cost(labels, predictions, false_negative_cost),
        demographic_parity_difference=abs(group_one.selection_rate - group_zero.selection_rate),
        equal_opportunity_difference=true_positive_gap,
        equalized_odds_difference=max(true_positive_gap, false_positive_gap),
        brier_score=brier_score(labels, probabilities),
        expected_calibration_error=calibration_error,
    )


def select_cost_threshold(
    labels: IntArray,
    probabilities: FloatArray,
    false_negative_cost: float,
    thresholds: tuple[float, ...] = DEFAULT_THRESHOLDS,
) -> float:
    """Select a global threshold by declared empirical error cost on tuning data."""

    if not thresholds:
        raise ValueError("threshold selection requires candidates")
    scored = []
    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(np.int64)
        cost = normalized_expected_cost(labels, predictions, false_negative_cost)
        scored.append((cost, abs(threshold - 0.5), threshold))
    return min(scored)[2]


def select_group_thresholds(
    labels: IntArray,
    probabilities: FloatArray,
    sensitive: IntArray,
    false_negative_cost: float,
    fairness_penalty: float,
    thresholds: tuple[float, ...] = DEFAULT_THRESHOLDS,
) -> tuple[float, float]:
    """Select threshold pairs by a preregistered cost-plus-equalized-odds objective."""

    if fairness_penalty < 0.0:
        raise ValueError("fairness penalty must be non-negative")
    if not thresholds:
        raise ValueError("threshold selection requires candidates")
    candidates: list[tuple[float, float, float, float, float, float]] = []
    for threshold_zero in thresholds:
        for threshold_one in thresholds:
            metrics = evaluate_policy(
                labels,
                probabilities,
                sensitive,
                threshold_zero,
                threshold_one,
                false_negative_cost,
            )
            objective = metrics.expected_cost + fairness_penalty * metrics.equalized_odds_difference
            candidates.append(
                (
                    objective,
                    metrics.expected_cost,
                    metrics.equalized_odds_difference,
                    abs(threshold_zero - 0.5) + abs(threshold_one - 0.5),
                    threshold_zero,
                    threshold_one,
                )
            )
    selected = min(candidates)
    return selected[4], selected[5]


def ranking_auc(labels: IntArray, probabilities: FloatArray) -> float:
    """Expose ranking performance alongside policy metrics."""

    return roc_auc(labels, probabilities)
