import numpy as np

from fairshift_lab.uncertainty import bootstrap_intervals


def test_bootstrap_is_reproducible_and_contains_estimate() -> None:
    labels = np.array([0, 1, 0, 1, 0, 1, 1, 0])
    probabilities = np.array([0.1, 0.8, 0.6, 0.9, 0.2, 0.7, 0.4, 0.3])
    sensitive = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    first = bootstrap_intervals(
        labels,
        probabilities,
        sensitive,
        0.5,
        resamples=50,
        confidence_level=0.9,
        seed=7,
    )
    second = bootstrap_intervals(
        labels,
        probabilities,
        sensitive,
        0.5,
        resamples=50,
        confidence_level=0.9,
        seed=7,
    )
    assert first == second
    assert set(first) == {
        "accuracy",
        "demographic_parity_difference",
        "equal_opportunity_difference",
        "equalized_odds_difference",
    }
    for interval in first.values():
        assert interval["lower"] <= interval["estimate"] <= interval["upper"]
        assert interval["confidence_level"] == 0.9
        assert interval["resamples"] == 50


def test_bootstrap_handles_one_observed_group() -> None:
    result = bootstrap_intervals(
        np.array([0, 1, 1, 0]),
        np.array([0.2, 0.8, 0.7, 0.1]),
        np.zeros(4, dtype=np.int64),
        0.5,
        resamples=20,
        confidence_level=0.95,
        seed=3,
    )
    assert result["accuracy"]["estimate"] == 1.0
    assert result["demographic_parity_difference"]["estimate"] == 0.5
