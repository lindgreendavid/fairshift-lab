"""Preregistered multi-seed benchmark for transparent decision policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace

import numpy as np

from fairshift_lab.calibration import apply_temperature, fit_temperature
from fairshift_lab.config import ShiftConfig, ShiftKind
from fairshift_lab.data import generate_population
from fairshift_lab.model import LogisticBaseline
from fairshift_lab.policy import (
    PolicyMetrics,
    evaluate_policy,
    joint_reweighing_weights,
    select_cost_threshold,
    select_group_thresholds,
)
from fairshift_lab.study import REGISTRY_DECIMALS, StudyEstimate

POLICY_METRICS = tuple(PolicyMetrics.__dataclass_fields__)
FAIRNESS_PENALTIES = (0.1, 0.3, 1.0, 3.0)


@dataclass(frozen=True)
class PolicyStudyConfig:
    """Inputs fixed before running the policy benchmark."""

    seeds: tuple[int, ...] = tuple(range(100, 120))
    samples: int = 1_000
    magnitude: float = 1.0
    false_negative_costs: tuple[float, ...] = (0.5, 1.0, 2.0)

    def __post_init__(self) -> None:
        if len(self.seeds) < 2 or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("policy study requires at least two unique seeds")
        if self.samples < 100:
            raise ValueError("policy study samples must be at least 100")
        if not 0.0 <= self.magnitude <= 1.0:
            raise ValueError("policy study magnitude must be between 0 and 1")
        if not self.false_negative_costs or any(cost <= 0.0 for cost in self.false_negative_costs):
            raise ValueError("false-negative costs must be positive")


@dataclass(frozen=True)
class PolicyDefinition:
    """Stable identity and disclosure for a benchmarked policy family."""

    key: str
    label: str
    access: str
    selection: str


@dataclass(frozen=True)
class PolicyCell:
    """Aggregate result for one shift, cost declaration, and policy."""

    shift: str
    magnitude: float
    false_negative_cost: float
    false_positive_cost: float
    policy: str
    replications: int
    pareto_efficient: bool
    metrics: dict[str, StudyEstimate]
    threshold_group_zero: StudyEstimate
    threshold_group_one: StudyEstimate


@dataclass(frozen=True)
class PolicyStudyResult:
    """Serializable benchmark with enough metadata to prevent silent policy choice."""

    config: PolicyStudyConfig
    policies: tuple[PolicyDefinition, ...]
    interval_definition: str
    pareto_definition: str
    cells: tuple[PolicyCell, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


POLICY_DEFINITIONS = (
    PolicyDefinition(
        "baseline",
        "Fixed baseline",
        "Source labels only",
        "Source-calibrated score at threshold 0.50.",
    ),
    PolicyDefinition(
        "source_cost_threshold",
        "Cost-sensitive threshold",
        "Source labels only",
        "One global threshold minimizes declared error cost on source tuning data.",
    ),
    PolicyDefinition(
        "target_recalibration",
        "Target recalibration",
        "Requires recent labeled target data",
        "Temperature and global cost threshold are selected on an independent "
        "target adaptation sample.",
    ),
    PolicyDefinition(
        "reweighed_training",
        "Reweighed training",
        "Source labels and protected attribute",
        "Training weights balance group-label cells; a source cost threshold is then selected.",
    ),
    *tuple(
        PolicyDefinition(
            f"group_threshold_{str(penalty).replace('.', '_')}",
            f"Group thresholds · λ={penalty:g}",
            "Source labels and protected attribute",
            "Two source-tuned thresholds minimize normalized error cost plus λ times "
            "the equalized-odds gap.",
        )
        for penalty in FAIRNESS_PENALTIES
    ),
)


def _estimate(values: list[float]) -> StudyEstimate:
    array = np.asarray(values, dtype=np.float64)
    lower, upper = np.quantile(array, [0.025, 0.975])
    return StudyEstimate(
        mean=round(float(np.mean(array)), REGISTRY_DECIMALS),
        standard_deviation=round(float(np.std(array, ddof=1)), REGISTRY_DECIMALS),
        replication_lower=round(float(lower), REGISTRY_DECIMALS),
        replication_upper=round(float(upper), REGISTRY_DECIMALS),
    )


def _record(
    store: dict[tuple[str, float, str], dict[str, list[float]]],
    shift: ShiftKind,
    cost: float,
    policy: str,
    metrics: PolicyMetrics,
    threshold_zero: float,
    threshold_one: float,
) -> None:
    bucket = store.setdefault(
        (shift.value, cost, policy),
        {
            **{metric: [] for metric in POLICY_METRICS},
            "threshold_group_zero": [],
            "threshold_group_one": [],
        },
    )
    for metric in POLICY_METRICS:
        bucket[metric].append(float(getattr(metrics, metric)))
    bucket["threshold_group_zero"].append(threshold_zero)
    bucket["threshold_group_one"].append(threshold_one)


def _mark_pareto(cells: list[PolicyCell]) -> list[PolicyCell]:
    result: list[PolicyCell] = []
    for cell in cells:
        cost = cell.metrics["expected_cost"].mean
        gap = cell.metrics["equalized_odds_difference"].mean
        dominated = any(
            other.shift == cell.shift
            and other.false_negative_cost == cell.false_negative_cost
            and other.policy != cell.policy
            and other.metrics["expected_cost"].mean <= cost
            and other.metrics["equalized_odds_difference"].mean <= gap
            and (
                other.metrics["expected_cost"].mean < cost
                or other.metrics["equalized_odds_difference"].mean < gap
            )
            for other in cells
        )
        result.append(replace(cell, pareto_efficient=not dominated))
    return result


DEFAULT_POLICY_STUDY_CONFIG = PolicyStudyConfig()


def run_policy_study(
    config: PolicyStudyConfig = DEFAULT_POLICY_STUDY_CONFIG,
) -> PolicyStudyResult:
    """Run the fixed benchmark using disjoint training, tuning, adaptation, and test sets."""

    store: dict[tuple[str, float, str], dict[str, list[float]]] = {}
    for shift in (ShiftKind.COVARIATE, ShiftKind.CONCEPT, ShiftKind.PREVALENCE):
        intervention = ShiftConfig(shift, config.magnitude)
        for seed in config.seeds:
            training = generate_population(config.samples, seed, ShiftConfig())
            source_tuning = generate_population(config.samples, seed + 1, ShiftConfig())
            target_test = generate_population(config.samples, seed + 3, intervention)
            target_adaptation = generate_population(config.samples, seed + 7, intervention)

            baseline = LogisticBaseline().fit(training.features, training.labels)
            reweighed = LogisticBaseline().fit(
                training.features,
                training.labels,
                joint_reweighing_weights(training.labels, training.sensitive),
            )

            baseline_tuning_raw = baseline.predict_proba(source_tuning.features)
            baseline_source_temperature = fit_temperature(source_tuning.labels, baseline_tuning_raw)
            baseline_tuning = apply_temperature(baseline_tuning_raw, baseline_source_temperature)
            baseline_target_raw = baseline.predict_proba(target_test.features)
            baseline_target = apply_temperature(baseline_target_raw, baseline_source_temperature)
            baseline_adaptation_raw = baseline.predict_proba(target_adaptation.features)

            reweighed_tuning_raw = reweighed.predict_proba(source_tuning.features)
            reweighed_temperature = fit_temperature(source_tuning.labels, reweighed_tuning_raw)
            reweighed_tuning = apply_temperature(reweighed_tuning_raw, reweighed_temperature)
            reweighed_target = apply_temperature(
                reweighed.predict_proba(target_test.features), reweighed_temperature
            )

            for cost in config.false_negative_costs:
                baseline_metrics = evaluate_policy(
                    target_test.labels,
                    baseline_target,
                    target_test.sensitive,
                    0.5,
                    0.5,
                    cost,
                )
                _record(store, shift, cost, "baseline", baseline_metrics, 0.5, 0.5)

                source_threshold = select_cost_threshold(
                    source_tuning.labels, baseline_tuning, cost
                )
                source_metrics = evaluate_policy(
                    target_test.labels,
                    baseline_target,
                    target_test.sensitive,
                    source_threshold,
                    source_threshold,
                    cost,
                )
                _record(
                    store,
                    shift,
                    cost,
                    "source_cost_threshold",
                    source_metrics,
                    source_threshold,
                    source_threshold,
                )

                target_temperature = fit_temperature(
                    target_adaptation.labels, baseline_adaptation_raw
                )
                target_adaptation_probabilities = apply_temperature(
                    baseline_adaptation_raw, target_temperature
                )
                target_threshold = select_cost_threshold(
                    target_adaptation.labels, target_adaptation_probabilities, cost
                )
                target_probabilities = apply_temperature(baseline_target_raw, target_temperature)
                target_metrics = evaluate_policy(
                    target_test.labels,
                    target_probabilities,
                    target_test.sensitive,
                    target_threshold,
                    target_threshold,
                    cost,
                )
                _record(
                    store,
                    shift,
                    cost,
                    "target_recalibration",
                    target_metrics,
                    target_threshold,
                    target_threshold,
                )

                reweighed_threshold = select_cost_threshold(
                    source_tuning.labels, reweighed_tuning, cost
                )
                reweighed_metrics = evaluate_policy(
                    target_test.labels,
                    reweighed_target,
                    target_test.sensitive,
                    reweighed_threshold,
                    reweighed_threshold,
                    cost,
                )
                _record(
                    store,
                    shift,
                    cost,
                    "reweighed_training",
                    reweighed_metrics,
                    reweighed_threshold,
                    reweighed_threshold,
                )

                for penalty in FAIRNESS_PENALTIES:
                    threshold_zero, threshold_one = select_group_thresholds(
                        source_tuning.labels,
                        baseline_tuning,
                        source_tuning.sensitive,
                        cost,
                        penalty,
                    )
                    group_metrics = evaluate_policy(
                        target_test.labels,
                        baseline_target,
                        target_test.sensitive,
                        threshold_zero,
                        threshold_one,
                        cost,
                    )
                    key = f"group_threshold_{str(penalty).replace('.', '_')}"
                    _record(
                        store,
                        shift,
                        cost,
                        key,
                        group_metrics,
                        threshold_zero,
                        threshold_one,
                    )

    cells: list[PolicyCell] = []
    for (shift_name, cost, policy), values in sorted(store.items()):
        cells.append(
            PolicyCell(
                shift=shift_name,
                magnitude=config.magnitude,
                false_negative_cost=cost,
                false_positive_cost=1.0,
                policy=policy,
                replications=len(config.seeds),
                pareto_efficient=False,
                metrics={metric: _estimate(values[metric]) for metric in POLICY_METRICS},
                threshold_group_zero=_estimate(values["threshold_group_zero"]),
                threshold_group_one=_estimate(values["threshold_group_one"]),
            )
        )
    return PolicyStudyResult(
        config=config,
        policies=POLICY_DEFINITIONS,
        interval_definition=(
            "Empirical 2.5th to 97.5th percentile range across independent seeded replications; "
            "descriptive, not a population confidence interval."
        ),
        pareto_definition=(
            "A policy is efficient within one shift and cost declaration when no benchmarked "
            "policy has both lower mean normalized expected cost and lower mean "
            "equalized-odds gap, with at least one strict improvement. This is "
            "benchmark-relative, not globally optimal."
        ),
        cells=tuple(_mark_pareto(cells)),
    )
