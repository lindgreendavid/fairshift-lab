"""Synthetic structural data-generating process with explicit interventions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from fairshift_lab.config import ShiftConfig, ShiftKind

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True)
class Population:
    """A generated population and its protected attribute."""

    features: FloatArray
    labels: IntArray
    sensitive: IntArray


def _sigmoid(values: FloatArray) -> FloatArray:
    clipped = np.clip(values, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def generate_population(samples: int, seed: int, shift: ShiftConfig) -> Population:
    """Generate a population from a documented structural process.

    The protected attribute influences one observed feature and the label. A target
    intervention changes exactly one mechanism, which makes experiments auditable.
    """

    rng = np.random.default_rng(seed)
    protected_probability = 0.5
    if shift.kind is ShiftKind.PREVALENCE:
        protected_probability = 0.5 + 0.4 * shift.magnitude

    sensitive = rng.binomial(1, protected_probability, size=samples).astype(np.int64)
    feature_one = rng.normal(0.0, 1.0, size=samples) + 0.35 * sensitive
    feature_two = rng.normal(0.0, 1.0, size=samples)

    if shift.kind is ShiftKind.COVARIATE:
        feature_one = feature_one + shift.magnitude * (0.5 + sensitive)
        feature_two = feature_two - 0.75 * shift.magnitude

    coefficient = 1.1
    group_effect = -0.45
    if shift.kind is ShiftKind.CONCEPT:
        coefficient -= 1.8 * shift.magnitude
        group_effect += 1.2 * shift.magnitude

    logits = -0.15 + coefficient * feature_one - 0.7 * feature_two + group_effect * sensitive
    labels = rng.binomial(1, _sigmoid(logits), size=samples).astype(np.int64)
    features = np.column_stack((feature_one, feature_two, sensitive)).astype(np.float64)
    return Population(features=features, labels=labels, sensitive=sensitive)
