"""Performance and group-fairness metrics with explicit edge-case semantics."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from fairshift_lab.data import FloatArray, IntArray


def _rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


@dataclass(frozen=True)
class GroupRates:
    selection_rate: float
    true_positive_rate: float
    false_positive_rate: float


def group_rates(
    labels: IntArray, predictions: IntArray, sensitive: IntArray, group: int
) -> GroupRates:
    mask = sensitive == group
    actual = labels[mask]
    predicted = predictions[mask]
    positives = actual == 1
    negatives = actual == 0
    return GroupRates(
        selection_rate=_rate(int(predicted.sum()), predicted.size),
        true_positive_rate=_rate(int(predicted[positives].sum()), int(positives.sum())),
        false_positive_rate=_rate(int(predicted[negatives].sum()), int(negatives.sum())),
    )


def roc_auc(labels: IntArray, probabilities: FloatArray) -> float:
    """Compute AUROC as the probability that a positive outranks a negative."""

    positive = probabilities[labels == 1]
    negative = probabilities[labels == 0]
    if positive.size == 0 or negative.size == 0:
        return 0.5
    comparisons = positive[:, None] - negative[None, :]
    return float(
        (np.count_nonzero(comparisons > 0) + 0.5 * np.count_nonzero(comparisons == 0))
        / comparisons.size
    )


def evaluate(
    labels: IntArray, probabilities: FloatArray, sensitive: IntArray, threshold: float
) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(np.int64)
    group_zero = group_rates(labels, predictions, sensitive, 0)
    group_one = group_rates(labels, predictions, sensitive, 1)
    dp = abs(group_one.selection_rate - group_zero.selection_rate)
    eo = abs(group_one.true_positive_rate - group_zero.true_positive_rate)
    fpr_gap = abs(group_one.false_positive_rate - group_zero.false_positive_rate)
    return {
        "accuracy": float(np.mean(predictions == labels)),
        "roc_auc": roc_auc(labels, probabilities),
        "demographic_parity_difference": dp,
        "equal_opportunity_difference": eo,
        "equalized_odds_difference": max(eo, fpr_gap),
        "groups": {"0": asdict(group_zero), "1": asdict(group_one)},
    }
