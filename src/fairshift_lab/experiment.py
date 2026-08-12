"""Reproducible source-to-target experiment orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from fairshift_lab.config import ExperimentConfig, ShiftConfig
from fairshift_lab.data import generate_population
from fairshift_lab.metrics import evaluate
from fairshift_lab.model import LogisticBaseline


@dataclass(frozen=True)
class ExperimentResult:
    config: dict[str, object]
    source: dict[str, object]
    target: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def run_experiment(config: ExperimentConfig) -> ExperimentResult:
    source = generate_population(config.samples, config.seed, ShiftConfig())
    target = generate_population(config.samples, config.seed + 1, config.target_shift)
    model = LogisticBaseline(config.learning_rate, config.iterations).fit(
        source.features, source.labels
    )
    source_metrics = evaluate(
        source.labels,
        model.predict_proba(source.features),
        source.sensitive,
        config.decision_threshold,
    )
    target_metrics = evaluate(
        target.labels,
        model.predict_proba(target.features),
        target.sensitive,
        config.decision_threshold,
    )
    config_payload = asdict(config)
    target_shift = config_payload["target_shift"]
    assert isinstance(target_shift, dict)
    target_shift["kind"] = config.target_shift.kind.value
    return ExperimentResult(config=config_payload, source=source_metrics, target=target_metrics)
