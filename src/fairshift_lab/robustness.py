"""Preregistered synthetic specification-stress study comparing two model families.

See ``docs/robustness-protocol.md`` for the frozen hypotheses, stressor definitions, and
split design this module implements. Every population here is synthetic; this module never
reads or writes anything from the governed external (UCI Adult) study.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from fairshift_lab.data import FloatArray, IntArray
from fairshift_lab.model import LogisticBaseline, ShallowDecisionTree
from fairshift_lab.policy import PolicyMetrics, evaluate_policy, select_cost_threshold
from fairshift_lab.study import REGISTRY_DECIMALS, StudyEstimate

STRESSORS: tuple[str, ...] = (
    "symmetric_label_noise",
    "group_conditional_label_noise",
    "protected_field_measurement_error",
    "unobserved_subgroup",
    "sample_size_stress",
    "structural_misspecification",
)
MODEL_FAMILIES: tuple[str, ...] = ("logistic_regression", "shallow_decision_tree")
GROUP_METRICS = (
    "demographic_parity_difference",
    "equal_opportunity_difference",
    "equalized_odds_difference",
)
FALSE_NEGATIVE_COST = 1.0


@dataclass(frozen=True)
class RobustnessStudyConfig:
    """Inputs fixed before running any stressed cell."""

    seeds: tuple[int, ...] = tuple(range(300, 312))
    magnitudes: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
    samples: int = 2_000

    def __post_init__(self) -> None:
        if len(self.seeds) < 2 or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("robustness study requires at least two unique seeds")
        if not self.magnitudes or any(not 0.0 <= value <= 1.0 for value in self.magnitudes):
            raise ValueError("robustness study magnitudes must be between 0 and 1")
        if 0.0 not in self.magnitudes:
            raise ValueError("robustness study magnitudes must include the 0.0 control")
        if self.samples < 200:
            raise ValueError("robustness study samples must be at least 200")


@dataclass(frozen=True)
class RobustPopulation:
    """A synthetic population with true labels, true sensitive value, and a subgroup flag."""

    features: FloatArray
    labels: IntArray
    sensitive: IntArray
    subgroup: IntArray


SAMPLE_SIZE_BY_MAGNITUDE = {0.0: 2_000, 0.25: 800, 0.5: 300, 0.75: 120, 1.0: 60}


def _sigmoid(values: FloatArray) -> FloatArray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -35.0, 35.0)))


def generate_robust_population(
    samples: int,
    seed: int,
    *,
    subgroup_effect: float = 0.0,
    interaction_coefficient: float = 0.0,
) -> RobustPopulation:
    """Sample from the v1.0 structural equation extended with two optional mechanisms.

    ``subgroup_effect`` and ``interaction_coefficient`` are zero for every stressor except
    the one they belong to; the unobserved subgroup indicator is always computed so its
    no-effect behavior is itself a reported null result.
    """

    rng = np.random.default_rng(seed)
    sensitive = rng.binomial(1, 0.5, size=samples).astype(np.int64)
    feature_one = rng.normal(0.0, 1.0, size=samples) + 0.35 * sensitive
    feature_two = rng.normal(0.0, 1.0, size=samples)
    subgroup = ((sensitive == 1) & (feature_two > float(np.median(feature_two)))).astype(np.int64)

    logits = -0.15 + 1.1 * feature_one - 0.7 * feature_two - 0.45 * sensitive
    logits = logits + interaction_coefficient * feature_one * sensitive
    logits = logits - subgroup_effect * subgroup
    labels = rng.binomial(1, _sigmoid(logits), size=samples).astype(np.int64)
    features = np.column_stack((feature_one, feature_two, sensitive)).astype(np.float64)
    return RobustPopulation(
        features=features, labels=labels, sensitive=sensitive, subgroup=subgroup
    )


def apply_symmetric_label_noise(
    labels: IntArray, rng: np.random.Generator, flip_probability: float
) -> IntArray:
    """Flip each label independently of the protected attribute with fixed probability."""

    flips = rng.random(labels.size) < flip_probability
    return np.where(flips, 1 - labels, labels).astype(np.int64)


def apply_group_conditional_label_noise(
    labels: IntArray,
    sensitive: IntArray,
    rng: np.random.Generator,
    flip_probability_group_zero: float,
    flip_probability_group_one: float,
) -> IntArray:
    """Flip labels with a probability that depends on the (true) protected attribute."""

    flip_probability = np.where(
        sensitive == 0, flip_probability_group_zero, flip_probability_group_one
    )
    flips = rng.random(labels.size) < flip_probability
    return np.where(flips, 1 - labels, labels).astype(np.int64)


def apply_measurement_error(
    sensitive: IntArray, rng: np.random.Generator, flip_probability: float
) -> IntArray:
    """Flip the observed protected attribute with fixed probability, independent of labels."""

    flips = rng.random(sensitive.size) < flip_probability
    return np.where(flips, 1 - sensitive, sensitive).astype(np.int64)


def _symmetric_noise_rate(magnitude: float) -> float:
    return 0.35 * magnitude


def _group_conditional_rates(magnitude: float) -> tuple[float, float]:
    return 0.05, 0.05 + 0.40 * magnitude


def _measurement_error_rate(magnitude: float) -> float:
    return 0.35 * magnitude


def _subgroup_effect(magnitude: float) -> float:
    return 1.5 * magnitude


def _interaction_coefficient(magnitude: float) -> float:
    return 1.5 * magnitude


def _build_model(model_family: str) -> LogisticBaseline | ShallowDecisionTree:
    if model_family == "logistic_regression":
        return LogisticBaseline()
    if model_family == "shallow_decision_tree":
        return ShallowDecisionTree(max_depth=3, min_samples_leaf=20)
    raise ValueError(f"unknown model family: {model_family}")


def _estimate(values: list[float]) -> StudyEstimate:
    array = np.asarray(values, dtype=np.float64)
    lower, upper = np.quantile(array, [0.025, 0.975])
    return StudyEstimate(
        mean=round(float(np.mean(array)), REGISTRY_DECIMALS),
        standard_deviation=round(float(np.std(array, ddof=1)), REGISTRY_DECIMALS),
        replication_lower=round(float(lower), REGISTRY_DECIMALS),
        replication_upper=round(float(upper), REGISTRY_DECIMALS),
    )


@dataclass(frozen=True)
class OptionalEstimate:
    """A descriptive estimate that is explicitly ``None`` when no replication defines it.

    This is this module's own missing/undefined convention, distinct from the ``0.0``
    zero-denominator convention used by ``fairshift_lab.metrics.group_rates`` in v1.0-v1.2,
    which this module does not modify.
    """

    mean: float | None
    standard_deviation: float | None
    replication_lower: float | None
    replication_upper: float | None
    defined_replications: int
    total_replications: int


def _optional_estimate(values: list[float | None]) -> OptionalEstimate:
    total = len(values)
    defined = [value for value in values if value is not None]
    if not defined:
        return OptionalEstimate(None, None, None, None, 0, total)
    array = np.asarray(defined, dtype=np.float64)
    if len(defined) >= 2:
        lower, upper = np.quantile(array, [0.025, 0.975])
        standard_deviation: float | None = round(float(np.std(array, ddof=1)), REGISTRY_DECIMALS)
    else:
        lower = upper = array[0]
        standard_deviation = None
    return OptionalEstimate(
        mean=round(float(np.mean(array)), REGISTRY_DECIMALS),
        standard_deviation=standard_deviation,
        replication_lower=round(float(lower), REGISTRY_DECIMALS),
        replication_upper=round(float(upper), REGISTRY_DECIMALS),
        defined_replications=len(defined),
        total_replications=total,
    )


def _optional_rate(numerator_mask: IntArray, denominator_mask: IntArray) -> float | None:
    denominator = int(np.sum(denominator_mask))
    if denominator == 0:
        return None
    return float(np.sum(numerator_mask & denominator_mask)) / denominator


def _conditional_rates(
    labels: IntArray, predictions: IntArray, mask: IntArray
) -> dict[str, float | None]:
    """Selection, true-positive and false-positive rate for one mask, ``None`` if undefined."""

    positive_predictions = predictions == 1
    positive_labels = labels == 1
    negative_labels = labels == 0
    selection = _optional_rate(positive_predictions.astype(np.int64), mask)
    tpr = _optional_rate(
        positive_predictions.astype(np.int64), (mask & positive_labels).astype(np.int64)
    )
    fpr = _optional_rate(
        positive_predictions.astype(np.int64), (mask & negative_labels).astype(np.int64)
    )
    return {"selection_rate": selection, "true_positive_rate": tpr, "false_positive_rate": fpr}


DEFAULT_ROBUSTNESS_STUDY_CONFIG = RobustnessStudyConfig()


def run_robustness_study(
    config: RobustnessStudyConfig = DEFAULT_ROBUSTNESS_STUDY_CONFIG,
) -> dict[str, object]:
    """Run the preregistered six-stressor, two-model-family robustness grid."""

    core_store: dict[tuple[str, float, str], dict[str, list[float]]] = {}
    true_group_store: dict[tuple[str, float, str], dict[str, list[float]]] = {}
    threshold_store: dict[tuple[str, float, str], list[float]] = {}
    diagnostic_store: dict[tuple[str, float, str], list[float | None]] = {}
    rate_store: dict[tuple[str, float, str], dict[str, dict[str, list[float | None]]]] = {}
    train_size_by_cell: dict[tuple[str, float], int] = {}
    test_size_by_cell: dict[tuple[str, float], int] = {}

    for stressor in STRESSORS:
        for magnitude in config.magnitudes:
            subgroup_effect = (
                _subgroup_effect(magnitude) if stressor == "unobserved_subgroup" else 0.0
            )
            interaction_coefficient = (
                _interaction_coefficient(magnitude)
                if stressor == "structural_misspecification"
                else 0.0
            )
            train_tuning_size = (
                SAMPLE_SIZE_BY_MAGNITUDE[magnitude]
                if stressor == "sample_size_stress"
                else config.samples
            )
            # sample_size_stress shrinks every split, including test: its estimand is what
            # happens when the whole available population is small, not only training data.
            test_size = train_tuning_size if stressor == "sample_size_stress" else config.samples
            train_size_by_cell[(stressor, magnitude)] = train_tuning_size
            test_size_by_cell[(stressor, magnitude)] = test_size

            for seed in config.seeds:
                training = generate_robust_population(
                    train_tuning_size,
                    seed,
                    subgroup_effect=subgroup_effect,
                    interaction_coefficient=interaction_coefficient,
                )
                tuning = generate_robust_population(
                    train_tuning_size,
                    seed + 1,
                    subgroup_effect=subgroup_effect,
                    interaction_coefficient=interaction_coefficient,
                )
                adaptation = generate_robust_population(
                    train_tuning_size,
                    seed + 2,
                    subgroup_effect=subgroup_effect,
                    interaction_coefficient=interaction_coefficient,
                )
                test = generate_robust_population(
                    test_size,
                    seed + 3,
                    subgroup_effect=subgroup_effect,
                    interaction_coefficient=interaction_coefficient,
                )
                stress_rng = np.random.default_rng(seed + 1_000_000)

                train_labels, tuning_labels = training.labels, tuning.labels
                train_sensitive, tuning_sensitive, test_sensitive_observed = (
                    training.sensitive,
                    tuning.sensitive,
                    test.sensitive,
                )
                diagnostic: float | None = None

                if stressor == "symmetric_label_noise":
                    rate = _symmetric_noise_rate(magnitude)
                    train_labels = apply_symmetric_label_noise(training.labels, stress_rng, rate)
                    tuning_labels = apply_symmetric_label_noise(tuning.labels, stress_rng, rate)
                    adaptation_observed = apply_symmetric_label_noise(
                        adaptation.labels, stress_rng, rate
                    )
                    diagnostic = float(np.mean(adaptation_observed != adaptation.labels))
                elif stressor == "group_conditional_label_noise":
                    rate_zero, rate_one = _group_conditional_rates(magnitude)
                    train_labels = apply_group_conditional_label_noise(
                        training.labels, training.sensitive, stress_rng, rate_zero, rate_one
                    )
                    tuning_labels = apply_group_conditional_label_noise(
                        tuning.labels, tuning.sensitive, stress_rng, rate_zero, rate_one
                    )
                    adaptation_observed = apply_group_conditional_label_noise(
                        adaptation.labels, adaptation.sensitive, stress_rng, rate_zero, rate_one
                    )
                    diagnostic = float(np.mean(adaptation_observed != adaptation.labels))
                elif stressor == "protected_field_measurement_error":
                    rate = _measurement_error_rate(magnitude)
                    train_sensitive = apply_measurement_error(training.sensitive, stress_rng, rate)
                    tuning_sensitive = apply_measurement_error(tuning.sensitive, stress_rng, rate)
                    test_sensitive_observed = apply_measurement_error(
                        test.sensitive, stress_rng, rate
                    )
                    adaptation_observed = apply_measurement_error(
                        adaptation.sensitive, stress_rng, rate
                    )
                    diagnostic = float(np.mean(adaptation_observed != adaptation.sensitive))
                elif stressor == "unobserved_subgroup":
                    subgroup_mask = adaptation.subgroup == 1
                    rest_mask = (adaptation.sensitive == 1) & (adaptation.subgroup == 0)
                    subgroup_rate = _optional_rate(
                        adaptation.labels.astype(np.int64), subgroup_mask.astype(np.int64)
                    )
                    rest_rate = _optional_rate(
                        adaptation.labels.astype(np.int64), rest_mask.astype(np.int64)
                    )
                    diagnostic = (
                        None
                        if subgroup_rate is None or rest_rate is None
                        else subgroup_rate - rest_rate
                    )
                elif stressor == "sample_size_stress":
                    diagnostic = float(train_tuning_size)
                elif stressor == "structural_misspecification":
                    median_feature_one = float(np.median(adaptation.features[:, 0]))
                    high = adaptation.features[:, 0] > median_feature_one
                    group_one = adaptation.sensitive == 1
                    group_zero = adaptation.sensitive == 0
                    interaction_cells: dict[str, float | None] = {}
                    for label_name, mask in (
                        ("high_group_one", high & group_one),
                        ("low_group_one", ~high & group_one),
                        ("high_group_zero", high & group_zero),
                        ("low_group_zero", ~high & group_zero),
                    ):
                        interaction_cells[label_name] = _optional_rate(
                            adaptation.labels.astype(np.int64), mask.astype(np.int64)
                        )
                    if any(value is None for value in interaction_cells.values()):
                        diagnostic = None
                    else:
                        diagnostic = (
                            interaction_cells["high_group_one"]  # type: ignore[operator]
                            - interaction_cells["low_group_one"]
                        ) - (
                            interaction_cells["high_group_zero"]  # type: ignore[operator]
                            - interaction_cells["low_group_zero"]
                        )

                for model_family in MODEL_FAMILIES:
                    model = _build_model(model_family)
                    training_features = np.column_stack(
                        (training.features[:, 0], training.features[:, 1], train_sensitive)
                    ).astype(np.float64)
                    tuning_features = np.column_stack(
                        (tuning.features[:, 0], tuning.features[:, 1], tuning_sensitive)
                    ).astype(np.float64)
                    test_features_observed = np.column_stack(
                        (test.features[:, 0], test.features[:, 1], test_sensitive_observed)
                    ).astype(np.float64)
                    model.fit(training_features, train_labels)
                    tuning_probabilities = model.predict_proba(tuning_features)
                    threshold = select_cost_threshold(
                        tuning_labels, tuning_probabilities, FALSE_NEGATIVE_COST
                    )
                    test_probabilities = model.predict_proba(test_features_observed)
                    predictions = (test_probabilities >= threshold).astype(np.int64)

                    observed_metrics = evaluate_policy(
                        test.labels,
                        test_probabilities,
                        test_sensitive_observed,
                        threshold,
                        threshold,
                        FALSE_NEGATIVE_COST,
                    )
                    true_metrics = evaluate_policy(
                        test.labels,
                        test_probabilities,
                        test.sensitive,
                        threshold,
                        threshold,
                        FALSE_NEGATIVE_COST,
                    )

                    key = (stressor, magnitude, model_family)
                    core_bucket = core_store.setdefault(
                        key, {name: [] for name in PolicyMetrics.__dataclass_fields__}
                    )
                    for name in PolicyMetrics.__dataclass_fields__:
                        core_bucket[name].append(float(getattr(observed_metrics, name)))
                    true_bucket = true_group_store.setdefault(
                        key, {name: [] for name in GROUP_METRICS}
                    )
                    for name in GROUP_METRICS:
                        true_bucket[name].append(float(getattr(true_metrics, name)))
                    threshold_store.setdefault(key, []).append(threshold)
                    diagnostic_store.setdefault(key, []).append(diagnostic)

                    conditional = {
                        "observed_group_0": _conditional_rates(
                            test.labels,
                            predictions,
                            (test_sensitive_observed == 0).astype(np.int64),
                        ),
                        "observed_group_1": _conditional_rates(
                            test.labels,
                            predictions,
                            (test_sensitive_observed == 1).astype(np.int64),
                        ),
                        "true_group_0": _conditional_rates(
                            test.labels, predictions, (test.sensitive == 0).astype(np.int64)
                        ),
                        "true_group_1": _conditional_rates(
                            test.labels, predictions, (test.sensitive == 1).astype(np.int64)
                        ),
                        "subgroup": _conditional_rates(
                            test.labels, predictions, (test.subgroup == 1).astype(np.int64)
                        ),
                        "group_one_excluding_subgroup": _conditional_rates(
                            test.labels,
                            predictions,
                            ((test.sensitive == 1) & (test.subgroup == 0)).astype(np.int64),
                        ),
                    }
                    rate_bucket = rate_store.setdefault(key, {})
                    for group_name, rates in conditional.items():
                        group_bucket = rate_bucket.setdefault(
                            group_name,
                            {
                                "selection_rate": [],
                                "true_positive_rate": [],
                                "false_positive_rate": [],
                            },
                        )
                        for rate_name, value in rates.items():
                            group_bucket[rate_name].append(value)

    cells = []
    for stressor in STRESSORS:
        for magnitude in config.magnitudes:
            for model_family in MODEL_FAMILIES:
                key = (stressor, magnitude, model_family)
                core_values = core_store[key]
                true_values = true_group_store[key]
                cells.append(
                    {
                        "stressor": stressor,
                        "magnitude": magnitude,
                        "model_family": model_family,
                        "false_negative_cost": FALSE_NEGATIVE_COST,
                        "replications": len(config.seeds),
                        "train_tuning_samples": train_size_by_cell[(stressor, magnitude)],
                        "test_samples": test_size_by_cell[(stressor, magnitude)],
                        "threshold": asdict(_estimate(threshold_store[key])),
                        "stress_diagnostic": asdict(_optional_estimate(diagnostic_store[key])),
                        "estimates": {
                            name: asdict(_estimate(values))
                            for name, values in sorted(core_values.items())
                        },
                        "estimates_true_group": {
                            name: asdict(_estimate(values))
                            for name, values in sorted(true_values.items())
                        },
                        "conditional_rates": {
                            group_name: {
                                rate_name: asdict(_optional_estimate(values))
                                for rate_name, values in sorted(rates.items())
                            }
                            for group_name, rates in sorted(rate_store[key].items())
                        },
                    }
                )

    return {
        "schema_version": "1.3",
        "study_type": "synthetic_specification_stress",
        "seeds": list(config.seeds),
        "magnitudes": list(config.magnitudes),
        "stressors": list(STRESSORS),
        "model_families": list(MODEL_FAMILIES),
        "interval_definition": (
            "Empirical 2.5th to 97.5th percentile range across independent seeded "
            "replications; descriptive, not a population confidence interval."
        ),
        "missing_semantics": (
            "Fields under 'conditional_rates' and 'stress_diagnostic' are null when no "
            "replication has a defined denominator for that quantity (for example an empty "
            "group-label cell at small sample sizes). A null aggregate means zero "
            "replications defined the quantity, not that the rate is zero. This differs from "
            "fairshift_lab.metrics.group_rates, whose unmodified v1.0-v1.2 convention reports "
            "0.0 for an empty denominator inside 'estimates' and 'estimates_true_group'."
        ),
        "cells": cells,
    }
