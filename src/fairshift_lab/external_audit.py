"""POST-HOC (not preregistered): test-set sampling uncertainty for the v1.2 external study.

The frozen study varies only the 80/20 development split (five seeds) and reports the mean and
the replication range of that split-seed variation. It never resamples the held-out test file
itself, so differences such as an equalized-odds gap of 0.037 versus 0.017 are quoted without any
estimate of how much they would move for a different draw of test people. This module adds:

* per-policy and paired-difference percentile-bootstrap intervals that resample test people
  (paired across policies, since every policy is evaluated on the same people);
* a finite-sample noise floor for the equalized-odds difference, the expected value of the
  statistic when the protected attribute is permuted at random among test people, which
  separates a real gap from the positive bias of a maximum of two absolute differences.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from fairshift_lab.data import FloatArray, IntArray
from fairshift_lab.external_study import (
    POLICIES,
    ExternalStudyConfig,
    _standardize,
    _subset,
    load_adult,
)
from fairshift_lab.model import LogisticBaseline
from fairshift_lab.policy import (
    joint_reweighing_weights,
    predictions_for_thresholds,
    select_cost_threshold,
    select_group_thresholds,
)

BOOTSTRAP_RESAMPLES = 2_000
BOOTSTRAP_SEED = 20_261_009
PERMUTATIONS = 500
CHUNK = 250
DECIMALS = 6
ALPHA = 0.05
COHORTS = (
    ("provider_eligible", 17, "complete_case", True),
    ("provider_eligible", 17, "numeric_complete", False),
    ("age_25_plus", 25, "complete_case", True),
    ("age_25_plus", 25, "numeric_complete", False),
)


@dataclass(frozen=True)
class TestPredictions:
    """Held-out decisions of all four policies on one fixed test population."""

    __test__ = False  # not a pytest test class

    labels: IntArray
    sensitive: IntArray
    decisions: dict[str, IntArray]


def held_out_decisions(
    data_dir: Path,
    *,
    minimum_age: int,
    complete_case: bool,
    seed: int,
    false_negative_cost: float,
    fairness_penalty: float = 1.0,
) -> TestPredictions:
    """Re-run one frozen cell and return the decisions instead of only the summary metrics."""

    development = load_adult(
        data_dir / "adult.data", minimum_age=minimum_age, complete_case=complete_case
    )
    testing_raw = load_adult(
        data_dir / "adult.test", minimum_age=minimum_age, complete_case=complete_case
    )
    order = np.random.default_rng(seed).permutation(development.labels.size)
    cut = int(0.8 * order.size)
    training, tuning, testing = _standardize(
        _subset(development, order[:cut]), _subset(development, order[cut:]), testing_raw
    )
    baseline = LogisticBaseline(iterations=300).fit(training.features, training.labels)
    reweighed = LogisticBaseline(iterations=300).fit(
        training.features,
        training.labels,
        joint_reweighing_weights(training.labels, training.sensitive),
    )
    tuning_prob = baseline.predict_proba(tuning.features)
    test_prob = baseline.predict_proba(testing.features)
    cost = false_negative_cost
    source = select_cost_threshold(tuning.labels, tuning_prob, cost)
    reweighed_threshold = select_cost_threshold(
        tuning.labels, reweighed.predict_proba(tuning.features), cost
    )
    group = select_group_thresholds(
        tuning.labels, tuning_prob, tuning.sensitive, cost, fairness_penalty
    )
    sensitive = testing.sensitive
    decisions = {
        "baseline": predictions_for_thresholds(test_prob, sensitive, 0.5, 0.5),
        "source_cost_threshold": predictions_for_thresholds(test_prob, sensitive, source, source),
        "reweighed_training": predictions_for_thresholds(
            reweighed.predict_proba(testing.features),
            sensitive,
            reweighed_threshold,
            reweighed_threshold,
        ),
        "group_threshold": predictions_for_thresholds(test_prob, sensitive, *group),
    }
    return TestPredictions(testing.labels, sensitive, decisions)


def _indicator_matrix(labels: IntArray, sensitive: IntArray, decisions: IntArray) -> FloatArray:
    """Columns whose weighted sums give every rate the frozen metrics are built from."""

    columns = []
    for group in (0, 1):
        in_group = sensitive == group
        positive = in_group & (labels == 1)
        negative = in_group & (labels == 0)
        columns += [positive, negative, positive & (decisions == 1), negative & (decisions == 1)]
    columns += [
        decisions == labels,
        (labels == 1) & (decisions == 0),
        (labels == 0) & (decisions == 1),
    ]
    return np.column_stack(columns).astype(np.float64)


def _metrics_from_sums(sums: FloatArray, cost: float) -> dict[str, FloatArray]:
    total = sums[:, 0] + sums[:, 1] + sums[:, 4] + sums[:, 5]
    with np.errstate(divide="ignore", invalid="ignore"):
        tpr0, fpr0 = sums[:, 2] / sums[:, 0], sums[:, 3] / sums[:, 1]
        tpr1, fpr1 = sums[:, 6] / sums[:, 4], sums[:, 7] / sums[:, 5]
    tpr_gap, fpr_gap = np.abs(tpr1 - tpr0), np.abs(fpr1 - fpr0)
    raw = cost * sums[:, 9] + sums[:, 10]
    return {
        "accuracy": sums[:, 8] / total,
        "expected_cost": raw / (total * max(cost, 1.0)),
        "equal_opportunity_difference": tpr_gap,
        "equalized_odds_difference": np.maximum(tpr_gap, fpr_gap),
    }


def _interval(values: FloatArray) -> list[float]:
    lower, upper = np.quantile(values, [ALPHA / 2, 1 - ALPHA / 2])
    return [round(float(lower), DECIMALS), round(float(upper), DECIMALS)]


def bootstrap_policies(
    predictions: TestPredictions,
    cost: float,
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Paired person-level bootstrap of every policy and of baseline-minus-policy differences."""

    rng = np.random.default_rng(seed)
    size = predictions.labels.size
    matrices = {
        policy: _indicator_matrix(
            predictions.labels, predictions.sensitive, predictions.decisions[policy]
        )
        for policy in POLICIES
    }
    draws: dict[str, dict[str, list[FloatArray]]] = {
        policy: {name: [] for name in _metrics_from_sums(matrices[policy][:1], cost)}
        for policy in POLICIES
    }
    remaining = resamples
    while remaining:
        step = min(CHUNK, remaining)
        counts = rng.multinomial(size, np.full(size, 1.0 / size), size=step).astype(np.float64)
        for policy in POLICIES:
            for name, values in _metrics_from_sums(counts @ matrices[policy], cost).items():
                draws[policy][name].append(values)
        remaining -= step
    stacked = {
        policy: {name: np.concatenate(parts) for name, parts in metrics.items()}
        for policy, metrics in draws.items()
    }
    point = {
        policy: {
            name: float(values[0])
            for name, values in _metrics_from_sums(
                matrices[policy].sum(axis=0)[None, :], cost
            ).items()
        }
        for policy in POLICIES
    }
    result: dict[str, Any] = {"test_size": int(size), "resamples": resamples, "policies": {}}
    for policy in POLICIES:
        entry: dict[str, Any] = {}
        for name, estimate in point[policy].items():
            entry[name] = {
                "estimate": round(estimate, DECIMALS),
                "interval_95": _interval(stacked[policy][name]),
            }
        if policy != "baseline":
            diffs = {}
            for name in ("equalized_odds_difference", "accuracy", "expected_cost"):
                delta = stacked["baseline"][name] - stacked[policy][name]
                diffs[name] = {
                    "baseline_minus_policy": round(
                        point["baseline"][name] - point[policy][name], DECIMALS
                    ),
                    "interval_95": _interval(delta),
                    "interval_excludes_zero": bool(
                        _interval(delta)[0] > 0.0 or _interval(delta)[1] < 0.0
                    ),
                }
            entry["paired_difference_from_baseline"] = diffs
        result["policies"][policy] = entry
    return result


def permutation_noise_floor(
    predictions: TestPredictions,
    cost: float,
    *,
    permutations: int = PERMUTATIONS,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, dict[str, float]]:
    """Equalized-odds difference expected when the protected attribute carries no information."""

    rng = np.random.default_rng(seed)
    floors: dict[str, dict[str, float]] = {}
    for policy in POLICIES:
        values = []
        for _ in range(permutations):
            shuffled = rng.permutation(predictions.sensitive)
            matrix = _indicator_matrix(predictions.labels, shuffled, predictions.decisions[policy])
            metrics = _metrics_from_sums(matrix.sum(axis=0)[None, :], cost)
            values.append(float(metrics["equalized_odds_difference"][0]))
        array = np.asarray(values)
        floors[policy] = {
            "mean": round(float(array.mean()), DECIMALS),
            "upper_95": round(float(np.quantile(array, 0.95)), DECIMALS),
        }
    return floors


def build_external_audit(
    data_dir: Path,
    config: ExternalStudyConfig | None = None,
    *,
    cost: float = 1.0,
    resamples: int = BOOTSTRAP_RESAMPLES,
    permutations: int = PERMUTATIONS,
) -> dict[str, Any]:
    config = config or ExternalStudyConfig()
    cells = []
    for cohort, minimum_age, missingness, complete_case in COHORTS:
        for seed in config.seeds:
            predictions = held_out_decisions(
                data_dir,
                minimum_age=minimum_age,
                complete_case=complete_case,
                seed=seed,
                false_negative_cost=cost,
                fairness_penalty=config.fairness_penalty,
            )
            cell = bootstrap_policies(predictions, cost, resamples=resamples)
            cell["noise_floor_equalized_odds"] = permutation_noise_floor(
                predictions, cost, permutations=permutations
            )
            cell.update(cohort=cohort, missingness=missingness, split_seed=seed)
            cells.append(cell)
    return {
        "schema_version": 1,
        "label": "POST-HOC (not preregistered): test-set sampling uncertainty, external study",
        "false_negative_cost": cost,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "cells": cells,
    }
