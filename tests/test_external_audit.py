from pathlib import Path

import numpy as np

from fairshift_lab.external_audit import (
    POLICIES,
    TestPredictions,
    bootstrap_policies,
    build_external_audit,
    held_out_decisions,
    permutation_noise_floor,
)
from fairshift_lab.external_study import ExternalStudyConfig


def _row(rng: np.random.Generator, suffix: str) -> str:
    age = int(rng.integers(17, 70))
    sex = "Male" if rng.random() < 0.6 else "Female"
    hours = int(rng.integers(10, 60))
    score = 0.04 * (age - 40) + 0.05 * (hours - 40) + (0.6 if sex == "Male" else 0.0)
    label = ">50K" if rng.random() < 1 / (1 + np.exp(-score)) else "<=50K"
    workclass = "?" if rng.random() < 0.05 else "Private"
    return (
        f"{age}, {workclass}, {int(rng.integers(1e4, 4e5))}, HS-grad, 9, Never-married, "
        f"Sales, Own-child, White, {sex}, {int(rng.integers(0, 3))}, 0, {hours}, "
        f"United-States, {label}{suffix}"
    )


def _fixture(tmp_path: Path) -> Path:
    rng = np.random.default_rng(3)
    data = tmp_path / "adult"
    data.mkdir()
    (data / "adult.data").write_text("\n".join(_row(rng, "") for _ in range(500)) + "\n")
    (data / "adult.test").write_text(
        "|header\n" + "\n".join(_row(rng, ".") for _ in range(300)) + "\n"
    )
    return data


def test_decisions_and_bootstrap_are_consistent(tmp_path: Path) -> None:
    data = _fixture(tmp_path)
    predictions = held_out_decisions(
        data, minimum_age=17, complete_case=True, seed=200, false_negative_cost=1.0
    )
    assert isinstance(predictions, TestPredictions)
    assert set(predictions.decisions) == set(POLICIES)
    result = bootstrap_policies(predictions, 1.0, resamples=300)
    baseline = result["policies"]["baseline"]
    accuracy = float(np.mean(predictions.decisions["baseline"] == predictions.labels))
    assert abs(baseline["accuracy"]["estimate"] - accuracy) < 1e-5
    low, high = baseline["accuracy"]["interval_95"]
    assert low <= accuracy <= high
    assert "paired_difference_from_baseline" not in baseline
    paired = result["policies"]["group_threshold"]["paired_difference_from_baseline"]
    accuracy_change = paired["accuracy"]["baseline_minus_policy"]
    cost_change = paired["expected_cost"]["baseline_minus_policy"]
    gap = accuracy_change + cost_change
    assert abs(gap) < 1e-5  # equal costs: accuracy loss is cost gain
    assert isinstance(paired["equalized_odds_difference"]["interval_excludes_zero"], bool)


def test_noise_floor_is_positive_and_bounded(tmp_path: Path) -> None:
    data = _fixture(tmp_path)
    predictions = held_out_decisions(
        data, minimum_age=17, complete_case=False, seed=201, false_negative_cost=2.0
    )
    floors = permutation_noise_floor(predictions, 2.0, permutations=40)
    for policy in POLICIES:
        assert 0.0 <= floors[policy]["mean"] <= floors[policy]["upper_95"] <= 1.0


def test_full_audit_structure(tmp_path: Path) -> None:
    data = _fixture(tmp_path)
    audit = build_external_audit(
        data, ExternalStudyConfig(seeds=(200, 201)), resamples=50, permutations=10
    )
    assert len(audit["cells"]) == 8
    assert audit["label"].startswith("POST-HOC")
