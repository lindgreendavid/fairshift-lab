import numpy as np
import pytest

from fairshift_lab import robustness
from fairshift_lab.robustness import (
    MODEL_FAMILIES,
    STRESSORS,
    RobustnessStudyConfig,
    apply_group_conditional_label_noise,
    apply_measurement_error,
    apply_symmetric_label_noise,
    generate_robust_population,
    run_robustness_study,
)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"seeds": (1,)}, "unique seeds"),
        ({"seeds": (1, 1)}, "unique seeds"),
        ({"magnitudes": ()}, "between 0 and 1"),
        ({"magnitudes": (1.1,)}, "between 0 and 1"),
        ({"magnitudes": (0.25, 0.5)}, "0.0 control"),
        ({"samples": 100}, "at least 200"),
    ],
)
def test_robustness_config_validates(kwargs: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RobustnessStudyConfig(**kwargs)  # type: ignore[arg-type]


def test_generate_robust_population_is_reproducible_and_shapes_match() -> None:
    first = generate_robust_population(200, seed=1)
    second = generate_robust_population(200, seed=1)
    assert np.array_equal(first.labels, second.labels)
    assert np.array_equal(first.sensitive, second.sensitive)
    assert np.array_equal(first.subgroup, second.subgroup)
    assert first.features.shape == (200, 3)
    assert set(np.unique(first.subgroup)).issubset({0, 1})


def test_subgroup_effect_lowers_subgroup_outcome_rate() -> None:
    unaffected = generate_robust_population(4_000, seed=5, subgroup_effect=0.0)
    affected = generate_robust_population(4_000, seed=5, subgroup_effect=1.5)
    unaffected_rate = float(np.mean(unaffected.labels[unaffected.subgroup == 1]))
    affected_rate = float(np.mean(affected.labels[affected.subgroup == 1]))
    assert affected_rate < unaffected_rate


def test_apply_symmetric_label_noise_flips_approximately_the_declared_rate() -> None:
    labels = np.zeros(20_000, dtype=np.int64)
    rng = np.random.default_rng(0)
    noisy = apply_symmetric_label_noise(labels, rng, 0.3)
    rate = float(np.mean(noisy != labels))
    assert 0.27 < rate < 0.33


def test_apply_group_conditional_label_noise_differs_by_group() -> None:
    labels = np.zeros(20_000, dtype=np.int64)
    sensitive = np.array([0, 1] * 10_000, dtype=np.int64)
    rng = np.random.default_rng(0)
    noisy = apply_group_conditional_label_noise(labels, sensitive, rng, 0.05, 0.45)
    flips = noisy != labels
    rate_zero = float(np.mean(flips[sensitive == 0]))
    rate_one = float(np.mean(flips[sensitive == 1]))
    assert rate_zero < 0.1
    assert rate_one > 0.4


def test_apply_measurement_error_flips_approximately_the_declared_rate() -> None:
    sensitive = np.zeros(20_000, dtype=np.int64)
    rng = np.random.default_rng(0)
    noisy = apply_measurement_error(sensitive, rng, 0.2)
    rate = float(np.mean(noisy != sensitive))
    assert 0.17 < rate < 0.23


def test_robustness_study_is_reproducible_and_covers_every_cell() -> None:
    config = RobustnessStudyConfig(seeds=(1, 2), magnitudes=(0.0, 1.0), samples=200)
    first = run_robustness_study(config)
    second = run_robustness_study(config)
    assert first == second
    assert len(first["cells"]) == len(STRESSORS) * 2 * len(MODEL_FAMILIES)
    assert first["schema_version"] == "1.3"
    stressors_seen = {cell["stressor"] for cell in first["cells"]}
    assert stressors_seen == set(STRESSORS)
    families_seen = {cell["model_family"] for cell in first["cells"]}
    assert families_seen == set(MODEL_FAMILIES)


def test_robustness_study_reports_defined_replication_counts() -> None:
    config = RobustnessStudyConfig(seeds=(1, 2), magnitudes=(0.0, 1.0), samples=200)
    result = run_robustness_study(config)
    for cell in result["cells"]:
        for group_rates in cell["conditional_rates"].values():
            for estimate in group_rates.values():
                assert estimate["total_replications"] == cell["replications"]
                assert 0 <= estimate["defined_replications"] <= estimate["total_replications"]
                if estimate["defined_replications"] == 0:
                    assert estimate["mean"] is None
                else:
                    assert estimate["mean"] is not None


def test_sample_size_stress_shrinks_every_split_including_test() -> None:
    config = RobustnessStudyConfig(seeds=(1, 2), magnitudes=(0.0, 1.0), samples=2_000)
    result = run_robustness_study(config)
    stressed = [
        cell
        for cell in result["cells"]
        if cell["stressor"] == "sample_size_stress" and cell["magnitude"] == 1.0
    ]
    assert stressed
    for cell in stressed:
        assert cell["train_tuning_samples"] == 60
        assert cell["test_samples"] == 60
    control = [
        cell
        for cell in result["cells"]
        if cell["stressor"] == "sample_size_stress" and cell["magnitude"] == 0.0
    ]
    for cell in control:
        assert cell["train_tuning_samples"] == 2_000
        assert cell["test_samples"] == 2_000


def test_other_stressors_keep_test_split_fixed() -> None:
    config = RobustnessStudyConfig(seeds=(1, 2), magnitudes=(0.0, 1.0), samples=200)
    result = run_robustness_study(config)
    for cell in result["cells"]:
        if cell["stressor"] != "sample_size_stress":
            assert cell["test_samples"] == 200


def test_build_model_rejects_unknown_family() -> None:
    with pytest.raises(ValueError, match="unknown model family"):
        robustness._build_model("nearest_neighbors")


def test_optional_rate_returns_none_for_empty_denominator() -> None:
    empty = np.zeros(5, dtype=np.int64)
    numerator = np.ones(5, dtype=np.int64)
    assert robustness._optional_rate(numerator, empty) is None


def test_optional_rate_computes_conditional_proportion() -> None:
    numerator = np.array([1, 0, 1, 1], dtype=np.int64)
    denominator = np.array([1, 1, 1, 0], dtype=np.int64)
    assert robustness._optional_rate(numerator, denominator) == pytest.approx(2 / 3)


def test_optional_estimate_is_none_for_no_data() -> None:
    estimate = robustness._optional_estimate([None, None])
    assert estimate.mean is None
    assert estimate.defined_replications == 0
    assert estimate.total_replications == 2


def test_optional_estimate_has_no_deviation_for_a_single_replication() -> None:
    estimate = robustness._optional_estimate([0.4, None])
    assert estimate.mean == pytest.approx(0.4)
    assert estimate.standard_deviation is None
    assert estimate.replication_lower == estimate.replication_upper == pytest.approx(0.4)
    assert estimate.defined_replications == 1
    assert estimate.total_replications == 2


def test_measurement_error_control_matches_true_and_observed_groups() -> None:
    config = RobustnessStudyConfig(seeds=(1, 2), magnitudes=(0.0,), samples=400)
    result = run_robustness_study(config)
    for cell in result["cells"]:
        if cell["stressor"] == "protected_field_measurement_error":
            for metric in cell["estimates_true_group"]:
                observed = cell["estimates"][metric]["mean"]
                true_group = cell["estimates_true_group"][metric]["mean"]
                assert observed == true_group
