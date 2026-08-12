"""Multi-seed replication studies for the public research report."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind
from fairshift_lab.experiment import run_experiment

REPORT_METRICS = (
    "accuracy",
    "roc_auc",
    "demographic_parity_difference",
    "equal_opportunity_difference",
    "equalized_odds_difference",
    "brier_score",
    "expected_calibration_error",
)


@dataclass(frozen=True)
class StudyConfig:
    """Inputs for a deterministic multi-seed, multi-magnitude study."""

    seeds: tuple[int, ...] = tuple(range(100, 120))
    magnitudes: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
    samples: int = 1_000

    def __post_init__(self) -> None:
        if len(self.seeds) < 2:
            raise ValueError("a study requires at least two seeds")
        if len(set(self.seeds)) != len(self.seeds):
            raise ValueError("study seeds must be unique")
        if self.samples < 100:
            raise ValueError("study samples must be at least 100")
        if not self.magnitudes:
            raise ValueError("a study requires at least one magnitude")
        if any(not 0.0 <= magnitude <= 1.0 for magnitude in self.magnitudes):
            raise ValueError("study magnitudes must be between 0 and 1")


@dataclass(frozen=True)
class StudyEstimate:
    """A descriptive estimate across independent seeded replications."""

    mean: float
    standard_deviation: float
    replication_lower: float
    replication_upper: float


@dataclass(frozen=True)
class StudyCell:
    """Summary for one intervention and magnitude."""

    shift: str
    magnitude: float
    replications: int
    target: dict[str, StudyEstimate]
    source_to_target_change: dict[str, StudyEstimate]


@dataclass(frozen=True)
class StudyResult:
    """Serializable research-report result."""

    config: StudyConfig
    interval_definition: str
    cells: tuple[StudyCell, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


DEFAULT_STUDY_CONFIG = StudyConfig()


def _estimate(values: list[float]) -> StudyEstimate:
    array = np.asarray(values, dtype=np.float64)
    lower, upper = np.quantile(array, [0.025, 0.975])
    return StudyEstimate(
        mean=float(np.mean(array)),
        standard_deviation=float(np.std(array, ddof=1)),
        replication_lower=float(lower),
        replication_upper=float(upper),
    )


def _extract(result: dict[str, object], population: str) -> dict[str, float]:
    metrics = result[population]
    calibration = result["calibration"]
    assert isinstance(metrics, dict)
    assert isinstance(calibration, dict)
    calibration_population = calibration[population]
    assert isinstance(calibration_population, dict)
    calibrated = calibration_population["calibrated"]
    assert isinstance(calibrated, dict)
    return {
        "accuracy": float(metrics["accuracy"]),
        "roc_auc": float(metrics["roc_auc"]),
        "demographic_parity_difference": float(metrics["demographic_parity_difference"]),
        "equal_opportunity_difference": float(metrics["equal_opportunity_difference"]),
        "equalized_odds_difference": float(metrics["equalized_odds_difference"]),
        "brier_score": float(calibrated["brier_score"]),
        "expected_calibration_error": float(calibrated["expected_calibration_error"]),
    }


def run_study(config: StudyConfig = DEFAULT_STUDY_CONFIG) -> StudyResult:
    """Run the preregistered descriptive replication grid.

    Each target population has its own training, calibration, source-evaluation, and
    target-evaluation samples. The interval is an empirical 2.5th--97.5th percentile
    range across seeded replications, not a population confidence interval.
    """

    cells: list[StudyCell] = []
    for shift in (ShiftKind.COVARIATE, ShiftKind.CONCEPT, ShiftKind.PREVALENCE):
        for magnitude in config.magnitudes:
            target_values: dict[str, list[float]] = {metric: [] for metric in REPORT_METRICS}
            changes: dict[str, list[float]] = {metric: [] for metric in REPORT_METRICS}
            for seed in config.seeds:
                result = run_experiment(
                    ExperimentConfig(
                        samples=config.samples,
                        seed=seed,
                        bootstrap_samples=20,
                        target_shift=ShiftConfig(shift, magnitude),
                    )
                ).as_dict()
                source = _extract(result, "source")
                target = _extract(result, "target")
                for metric in REPORT_METRICS:
                    target_values[metric].append(target[metric])
                    changes[metric].append(target[metric] - source[metric])
            cells.append(
                StudyCell(
                    shift=shift.value,
                    magnitude=magnitude,
                    replications=len(config.seeds),
                    target={metric: _estimate(values) for metric, values in target_values.items()},
                    source_to_target_change={
                        metric: _estimate(values) for metric, values in changes.items()
                    },
                )
            )
    return StudyResult(
        config=config,
        interval_definition=(
            "Empirical 2.5th to 97.5th percentile range across independent seeded "
            "replications; descriptive, not a population confidence interval."
        ),
        cells=tuple(cells),
    )
