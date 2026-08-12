import numpy as np
import pytest

from fairshift_lab.calibration import (
    apply_temperature,
    brier_score,
    calibration_summary,
    fit_temperature,
    log_loss,
)


def test_temperature_one_preserves_probabilities() -> None:
    probabilities = np.array([0.0, 0.2, 0.8, 1.0])
    scaled = apply_temperature(probabilities, 1.0)
    assert np.allclose(scaled[1:3], probabilities[1:3])
    assert np.all((scaled > 0.0) & (scaled < 1.0))


def test_temperature_fit_reduces_source_calibration_loss() -> None:
    labels = np.array([0, 1, 0, 1])
    probabilities = np.array([0.1, 0.9, 0.9, 0.1])
    temperature = fit_temperature(labels, probabilities)
    assert temperature > 1.0
    assert log_loss(labels, apply_temperature(probabilities, temperature)) < log_loss(
        labels, probabilities
    )


def test_calibration_summary_reports_reliability_bins() -> None:
    labels = np.array([0, 0, 1, 1])
    probabilities = np.array([0.1, 0.2, 0.8, 0.9])
    summary = calibration_summary(labels, probabilities, bins=3)
    assert brier_score(labels, probabilities) == pytest.approx(0.025)
    assert summary["expected_calibration_error"] == pytest.approx(0.15)
    bins = summary["bins"]
    assert isinstance(bins, list)
    assert len(bins) == 2
    assert bins[0]["count"] == 2


def test_calibration_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="temperature must be positive"):
        apply_temperature(np.array([0.5]), 0.0)
    with pytest.raises(ValueError, match="at least 2"):
        calibration_summary(np.array([1]), np.array([0.5]), bins=1)
