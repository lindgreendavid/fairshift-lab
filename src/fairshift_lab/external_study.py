"""Preregistered observational reference-data study for UCI Adult."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from fairshift_lab.data import FloatArray, IntArray
from fairshift_lab.model import LogisticBaseline
from fairshift_lab.policy import (
    PolicyMetrics,
    evaluate_policy,
    joint_reweighing_weights,
    select_cost_threshold,
    select_group_thresholds,
)
from fairshift_lab.study import REGISTRY_DECIMALS, StudyEstimate

NUMERIC_COLUMNS = (0, 4, 10, 11, 12)
POLICIES = ("baseline", "source_cost_threshold", "reweighed_training", "group_threshold")


@dataclass(frozen=True)
class AdultRecords:
    """Provider-coded observations used only as a historical reference dataset."""

    features: FloatArray
    labels: IntArray
    sensitive: IntArray


@dataclass(frozen=True)
class ExternalStudyConfig:
    """Inputs fixed before looking at held-out results."""

    seeds: tuple[int, ...] = tuple(range(200, 205))
    false_negative_costs: tuple[float, ...] = (0.5, 1.0, 2.0)
    fairness_penalty: float = 1.0


def load_adult(path: Path, *, minimum_age: int, complete_case: bool) -> AdultRecords:
    """Parse an official Adult file with explicit missingness and cohort rules."""

    features: list[list[float]] = []
    labels: list[int] = []
    sensitive: list[int] = []
    with path.open(encoding="utf-8") as handle:
        for row in csv.reader(handle, skipinitialspace=True):
            if len(row) != 15 or not row[0].isdigit():
                continue
            if int(row[0]) < minimum_age or (complete_case and "?" in row):
                continue
            values = [float(row[index]) for index in NUMERIC_COLUMNS]
            values[2] = float(np.log1p(values[2]))
            values[3] = float(np.log1p(values[3]))
            features.append(values)
            labels.append(int(row[14].rstrip(".") == ">50K"))
            sensitive.append(int(row[9] == "Male"))
    if not features:
        raise ValueError("Adult file contains no eligible records")
    return AdultRecords(
        np.asarray(features, dtype=np.float64),
        np.asarray(labels, dtype=np.int64),
        np.asarray(sensitive, dtype=np.int64),
    )


def _subset(records: AdultRecords, indices: IntArray) -> AdultRecords:
    return AdultRecords(
        records.features[indices], records.labels[indices], records.sensitive[indices]
    )


def _standardize(
    training: AdultRecords, tuning: AdultRecords, testing: AdultRecords
) -> tuple[AdultRecords, AdultRecords, AdultRecords]:
    mean = np.mean(training.features, axis=0)
    scale = np.std(training.features, axis=0)
    scale[scale == 0.0] = 1.0

    def transform(records: AdultRecords) -> AdultRecords:
        return AdultRecords((records.features - mean) / scale, records.labels, records.sensitive)

    return transform(training), transform(tuning), transform(testing)


def _estimate(values: list[float]) -> StudyEstimate:
    array = np.asarray(values, dtype=np.float64)
    lower, upper = np.quantile(array, [0.025, 0.975])
    return StudyEstimate(
        mean=round(float(np.mean(array)), REGISTRY_DECIMALS),
        standard_deviation=round(float(np.std(array, ddof=1)), REGISTRY_DECIMALS),
        replication_lower=round(float(lower), REGISTRY_DECIMALS),
        replication_upper=round(float(upper), REGISTRY_DECIMALS),
    )


DEFAULT_EXTERNAL_STUDY_CONFIG = ExternalStudyConfig()


def run_external_study(
    data_dir: Path, config: ExternalStudyConfig = DEFAULT_EXTERNAL_STUDY_CONFIG
) -> dict[str, object]:
    """Run sensitivity analyses without treating historical labels as normative truth."""

    if len(config.seeds) < 2 or len(set(config.seeds)) != len(config.seeds):
        raise ValueError("external study requires at least two unique seeds")
    store: dict[tuple[str, str, float, str], dict[str, list[float]]] = {}
    counts: dict[tuple[str, str], dict[str, int]] = {}
    for cohort, minimum_age in (("provider_eligible", 17), ("age_25_plus", 25)):
        for missingness, complete_case in (("complete_case", True), ("numeric_complete", False)):
            development = load_adult(
                data_dir / "adult.data", minimum_age=minimum_age, complete_case=complete_case
            )
            testing_raw = load_adult(
                data_dir / "adult.test", minimum_age=minimum_age, complete_case=complete_case
            )
            counts[(cohort, missingness)] = {
                "test_total": int(testing_raw.labels.size),
                "test_group_female": int(np.sum(testing_raw.sensitive == 0)),
                "test_group_male": int(np.sum(testing_raw.sensitive == 1)),
                "test_label_above_50k": int(np.sum(testing_raw.labels == 1)),
            }
            for seed in config.seeds:
                rng = np.random.default_rng(seed)
                order = rng.permutation(development.labels.size)
                cut = int(0.8 * order.size)
                training_raw = _subset(development, order[:cut])
                tuning_raw = _subset(development, order[cut:])
                training, tuning, testing = _standardize(training_raw, tuning_raw, testing_raw)
                baseline = LogisticBaseline(iterations=300).fit(training.features, training.labels)
                reweighed = LogisticBaseline(iterations=300).fit(
                    training.features,
                    training.labels,
                    joint_reweighing_weights(training.labels, training.sensitive),
                )
                tuning_prob = baseline.predict_proba(tuning.features)
                test_prob = baseline.predict_proba(testing.features)
                reweighed_tuning = reweighed.predict_proba(tuning.features)
                reweighed_test = reweighed.predict_proba(testing.features)
                for cost in config.false_negative_costs:
                    source_threshold = select_cost_threshold(tuning.labels, tuning_prob, cost)
                    reweighed_threshold = select_cost_threshold(
                        tuning.labels, reweighed_tuning, cost
                    )
                    group_thresholds = select_group_thresholds(
                        tuning.labels,
                        tuning_prob,
                        tuning.sensitive,
                        cost,
                        config.fairness_penalty,
                    )
                    evaluations = {
                        "baseline": (
                            evaluate_policy(
                                testing.labels, test_prob, testing.sensitive, 0.5, 0.5, cost
                            ),
                            0.5,
                            0.5,
                        ),
                        "source_cost_threshold": (
                            evaluate_policy(
                                testing.labels,
                                test_prob,
                                testing.sensitive,
                                source_threshold,
                                source_threshold,
                                cost,
                            ),
                            source_threshold,
                            source_threshold,
                        ),
                        "reweighed_training": (
                            evaluate_policy(
                                testing.labels,
                                reweighed_test,
                                testing.sensitive,
                                reweighed_threshold,
                                reweighed_threshold,
                                cost,
                            ),
                            reweighed_threshold,
                            reweighed_threshold,
                        ),
                        "group_threshold": (
                            evaluate_policy(
                                testing.labels,
                                test_prob,
                                testing.sensitive,
                                *group_thresholds,
                                cost,
                            ),
                            *group_thresholds,
                        ),
                    }
                    for policy, (metrics, threshold_zero, threshold_one) in evaluations.items():
                        key = (cohort, missingness, cost, policy)
                        bucket = store.setdefault(
                            key,
                            {
                                name: []
                                for name in (
                                    *PolicyMetrics.__dataclass_fields__,
                                    "threshold_group_female",
                                    "threshold_group_male",
                                )
                            },
                        )
                        for name in PolicyMetrics.__dataclass_fields__:
                            bucket[name].append(float(getattr(metrics, name)))
                        bucket["threshold_group_female"].append(threshold_zero)
                        bucket["threshold_group_male"].append(threshold_one)
    cells = []
    for (cohort, missingness, cost, policy), values in sorted(store.items()):
        cells.append(
            {
                "cohort": cohort,
                "missingness": missingness,
                "false_negative_cost": cost,
                "false_positive_cost": 1.0,
                "policy": policy,
                "replications": len(config.seeds),
                "subgroup_counts": counts[(cohort, missingness)],
                "estimates": {
                    name: asdict(_estimate(series)) for name, series in sorted(values.items())
                },
            }
        )
    return {
        "schema_version": "1.2",
        "study_type": "observational_historical_reference",
        "dataset": "UCI Adult / Census Income",
        "provider_extraction_year": 1994,
        "seeds": list(config.seeds),
        "sensitive_field": "provider-coded binary sex field; not identity truth",
        "label": "historical annual income above USD 50,000; not qualification or deservingness",
        "policies": list(POLICIES),
        "cells": cells,
    }
