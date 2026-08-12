"""Formal decision-threshold sensitivity analysis."""

from __future__ import annotations

import numpy as np

from fairshift_lab.data import FloatArray, IntArray
from fairshift_lab.metrics import evaluate, roc_auc

DEFAULT_THRESHOLDS: tuple[float, ...] = tuple(float(value) for value in np.linspace(0.05, 0.95, 19))


def threshold_sweep(
    labels: IntArray,
    probabilities: FloatArray,
    sensitive: IntArray,
    thresholds: tuple[float, ...] = DEFAULT_THRESHOLDS,
) -> list[dict[str, object]]:
    """Evaluate performance and group measurements across declared thresholds."""

    if not thresholds or any(not 0.0 < threshold < 1.0 for threshold in thresholds):
        raise ValueError("thresholds must contain values strictly between 0 and 1")
    ranking = roc_auc(labels, probabilities)
    result: list[dict[str, object]] = []
    for threshold in thresholds:
        metrics = evaluate(labels, probabilities, sensitive, threshold, include_roc_auc=False)
        metrics["roc_auc"] = ranking
        result.append({"threshold": threshold, **metrics})
    return result
