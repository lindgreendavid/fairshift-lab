"""Probability calibration diagnostics and source-only temperature scaling."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from fairshift_lab.data import FloatArray, IntArray


@dataclass(frozen=True)
class CalibrationBin:
    """One populated equal-width reliability-diagram bin."""

    lower: float
    upper: float
    count: int
    mean_probability: float
    observed_rate: float
    absolute_gap: float


def brier_score(labels: IntArray, probabilities: FloatArray) -> float:
    """Return the mean squared error of probabilistic binary predictions."""

    return float(np.mean((probabilities - labels) ** 2))


def log_loss(labels: IntArray, probabilities: FloatArray) -> float:
    """Return binary negative log likelihood with stable probability clipping."""

    clipped = np.clip(probabilities, 1e-12, 1.0 - 1e-12)
    return float(-np.mean(labels * np.log(clipped) + (1 - labels) * np.log1p(-clipped)))


def apply_temperature(probabilities: FloatArray, temperature: float) -> FloatArray:
    """Scale binary logits without changing their ranking."""

    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    clipped = np.clip(probabilities, 1e-12, 1.0 - 1e-12)
    logits = np.log(clipped) - np.log1p(-clipped)
    scaled = logits / temperature
    return np.asarray(1.0 / (1.0 + np.exp(-np.clip(scaled, -35.0, 35.0))), dtype=np.float64)


def fit_temperature(labels: IntArray, probabilities: FloatArray) -> float:
    """Fit one source-only temperature by deterministic log-spaced NLL search."""

    candidates = np.exp(np.linspace(np.log(0.25), np.log(4.0), 151))
    losses = np.array(
        [log_loss(labels, apply_temperature(probabilities, value)) for value in candidates]
    )
    return float(candidates[int(np.argmin(losses))])


def calibration_summary(
    labels: IntArray, probabilities: FloatArray, bins: int
) -> dict[str, object]:
    """Summarize reliability with Brier score, ECE, and populated bins."""

    if bins < 2:
        raise ValueError("calibration bins must be at least 2")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.minimum((probabilities * bins).astype(np.int64), bins - 1)
    populated: list[CalibrationBin] = []
    weighted_gap = 0.0
    for index in range(bins):
        mask = assignments == index
        count = int(mask.sum())
        if count == 0:
            continue
        mean_probability = float(np.mean(probabilities[mask]))
        observed_rate = float(np.mean(labels[mask]))
        gap = abs(mean_probability - observed_rate)
        weighted_gap += count * gap
        populated.append(
            CalibrationBin(
                lower=float(edges[index]),
                upper=float(edges[index + 1]),
                count=count,
                mean_probability=mean_probability,
                observed_rate=observed_rate,
                absolute_gap=gap,
            )
        )
    return {
        "brier_score": brier_score(labels, probabilities),
        "expected_calibration_error": weighted_gap / labels.size,
        "bins": [asdict(item) for item in populated],
    }
