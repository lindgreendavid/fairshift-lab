"""Reproducible source-to-target experiment orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from fairshift_lab.calibration import (
    apply_temperature,
    calibration_summary,
    fit_temperature,
)
from fairshift_lab.config import ExperimentConfig, ShiftConfig
from fairshift_lab.data import generate_population
from fairshift_lab.metrics import evaluate
from fairshift_lab.model import LogisticBaseline
from fairshift_lab.sensitivity import threshold_sweep
from fairshift_lab.uncertainty import bootstrap_intervals


@dataclass(frozen=True)
class ExperimentResult:
    config: dict[str, object]
    source: dict[str, object]
    target: dict[str, object]
    source_uncertainty: dict[str, dict[str, float | int]]
    target_uncertainty: dict[str, dict[str, float | int]]
    calibration: dict[str, object]
    source_threshold_sensitivity: list[dict[str, object]]
    target_threshold_sensitivity: list[dict[str, object]]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    training = generate_population(config.samples, config.seed, ShiftConfig())
    calibration = generate_population(config.samples, config.seed + 1, ShiftConfig())
    source = generate_population(config.samples, config.seed + 2, ShiftConfig())
    target = generate_population(config.samples, config.seed + 3, config.target_shift)
    model = LogisticBaseline(config.learning_rate, config.iterations).fit(
        training.features, training.labels
    )
    calibration_raw = model.predict_proba(calibration.features)
    temperature = fit_temperature(calibration.labels, calibration_raw)
    source_raw = model.predict_proba(source.features)
    target_raw = model.predict_proba(target.features)
    source_probabilities = apply_temperature(source_raw, temperature)
    target_probabilities = apply_temperature(target_raw, temperature)
    source_metrics = evaluate(
        source.labels,
        source_probabilities,
        source.sensitive,
        config.decision_threshold,
    )
    target_metrics = evaluate(
        target.labels,
        target_probabilities,
        target.sensitive,
        config.decision_threshold,
    )
    source_uncertainty = bootstrap_intervals(
        source.labels,
        source_probabilities,
        source.sensitive,
        config.decision_threshold,
        resamples=config.bootstrap_samples,
        confidence_level=config.confidence_level,
        seed=config.seed + 4,
    )
    target_uncertainty = bootstrap_intervals(
        target.labels,
        target_probabilities,
        target.sensitive,
        config.decision_threshold,
        resamples=config.bootstrap_samples,
        confidence_level=config.confidence_level,
        seed=config.seed + 5,
    )
    calibration_payload: dict[str, object] = {
        "temperature": temperature,
        "selection": {
            "criterion": "source calibration negative log likelihood",
            "samples": config.samples,
            "seed": config.seed + 1,
        },
        "source": {
            "raw": calibration_summary(source.labels, source_raw, config.calibration_bins),
            "calibrated": calibration_summary(
                source.labels, source_probabilities, config.calibration_bins
            ),
        },
        "target": {
            "raw": calibration_summary(target.labels, target_raw, config.calibration_bins),
            "calibrated": calibration_summary(
                target.labels, target_probabilities, config.calibration_bins
            ),
        },
    }
    config_payload = asdict(config)
    target_shift = config_payload["target_shift"]
    assert isinstance(target_shift, dict)
    target_shift["kind"] = config.target_shift.kind.value
    return ExperimentResult(
        config=config_payload,
        source=source_metrics,
        target=target_metrics,
        source_uncertainty=source_uncertainty,
        target_uncertainty=target_uncertainty,
        calibration=calibration_payload,
        source_threshold_sensitivity=threshold_sweep(
            source.labels, source_probabilities, source.sensitive
        ),
        target_threshold_sensitivity=threshold_sweep(
            target.labels, target_probabilities, target.sensitive
        ),
    )
