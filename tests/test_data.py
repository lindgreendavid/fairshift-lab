import numpy as np

from fairshift_lab.config import ShiftConfig, ShiftKind
from fairshift_lab.data import generate_population


def test_generation_is_reproducible() -> None:
    first = generate_population(500, 9, ShiftConfig())
    second = generate_population(500, 9, ShiftConfig())
    assert np.array_equal(first.features, second.features)
    assert np.array_equal(first.labels, second.labels)


def test_population_has_expected_shapes_and_types() -> None:
    population = generate_population(120, 3, ShiftConfig())
    assert population.features.shape == (120, 3)
    assert population.labels.shape == population.sensitive.shape == (120,)
    assert population.features.dtype == np.float64
    assert population.labels.dtype == np.int64


def test_covariate_shift_moves_observed_features() -> None:
    source = generate_population(10_000, 4, ShiftConfig())
    target = generate_population(10_000, 4, ShiftConfig(ShiftKind.COVARIATE, 1.0))
    assert target.features[:, 0].mean() > source.features[:, 0].mean() + 0.8
    assert target.features[:, 1].mean() < source.features[:, 1].mean() - 0.6


def test_prevalence_shift_changes_group_share() -> None:
    target = generate_population(10_000, 5, ShiftConfig(ShiftKind.PREVALENCE, 1.0))
    assert target.sensitive.mean() > 0.85


def test_concept_shift_changes_labels_without_features() -> None:
    source = generate_population(2_000, 6, ShiftConfig())
    target = generate_population(2_000, 6, ShiftConfig(ShiftKind.CONCEPT, 1.0))
    assert np.array_equal(source.features, target.features)
    assert not np.array_equal(source.labels, target.labels)
