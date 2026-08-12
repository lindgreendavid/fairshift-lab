"""Stratified bootstrap intervals for subgroup-sensitive measurements."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from fairshift_lab.data import FloatArray, IntArray
from fairshift_lab.metrics import group_rates


@dataclass(frozen=True)
class MetricInterval:
    """A point estimate and two-sided percentile-bootstrap interval."""

    estimate: float
    lower: float
    upper: float
    confidence_level: float
    resamples: int


def _metric_values(
    labels: IntArray,
    probabilities: FloatArray,
    sensitive: IntArray,
    threshold: float,
) -> dict[str, float]:
    predictions = (probabilities >= threshold).astype(np.int64)
    group_zero = group_rates(labels, predictions, sensitive, 0)
    group_one = group_rates(labels, predictions, sensitive, 1)
    tpr_gap = abs(group_one.true_positive_rate - group_zero.true_positive_rate)
    fpr_gap = abs(group_one.false_positive_rate - group_zero.false_positive_rate)
    return {
        "accuracy": float(np.mean(predictions == labels)),
        "demographic_parity_difference": abs(group_one.selection_rate - group_zero.selection_rate),
        "equal_opportunity_difference": tpr_gap,
        "equalized_odds_difference": max(tpr_gap, fpr_gap),
    }


def _stratified_indices(sensitive: IntArray, rng: np.random.Generator) -> IntArray:
    sampled_groups: list[IntArray] = []
    for group in np.unique(sensitive):
        indices = np.flatnonzero(sensitive == group)
        sampled_groups.append(rng.choice(indices, size=indices.size, replace=True))
    return np.concatenate(sampled_groups).astype(np.int64)


def bootstrap_intervals(
    labels: IntArray,
    probabilities: FloatArray,
    sensitive: IntArray,
    threshold: float,
    *,
    resamples: int,
    confidence_level: float,
    seed: int,
) -> dict[str, dict[str, float | int]]:
    """Estimate uncertainty while preserving observed protected-group sizes.

    Stratification prevents group-composition noise from obscuring conditional-rate
    uncertainty. Percentile intervals are descriptive and do not correct model-selection,
    dataset-construction, or deployment uncertainty.
    """

    estimates = _metric_values(labels, probabilities, sensitive, threshold)
    distributions = {name: np.empty(resamples, dtype=np.float64) for name in estimates}
    rng = np.random.default_rng(seed)
    for position in range(resamples):
        indices = _stratified_indices(sensitive, rng)
        values = _metric_values(
            labels[indices], probabilities[indices], sensitive[indices], threshold
        )
        for name, value in values.items():
            distributions[name][position] = value

    tail = (1.0 - confidence_level) / 2.0
    result: dict[str, dict[str, float | int]] = {}
    for name, estimate in estimates.items():
        lower, upper = np.quantile(distributions[name], [tail, 1.0 - tail])
        result[name] = asdict(
            MetricInterval(
                estimate=estimate,
                lower=float(lower),
                upper=float(upper),
                confidence_level=confidence_level,
                resamples=resamples,
            )
        )
    return result
