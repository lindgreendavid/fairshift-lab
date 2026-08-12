import json

from fairshift_lab.cli import main
from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind
from fairshift_lab.experiment import run_experiment


def test_experiment_is_reproducible() -> None:
    config = ExperimentConfig(samples=200, seed=12)
    assert run_experiment(config) == run_experiment(config)


def test_experiment_serializes_shift_kind() -> None:
    config = ExperimentConfig(
        samples=200,
        target_shift=ShiftConfig(ShiftKind.CONCEPT, 0.5),
    )
    result = run_experiment(config).as_dict()
    assert result["config"]["target_shift"] == {"kind": "concept", "magnitude": 0.5}  # type: ignore[index]


def test_cli_prints_machine_readable_result(capsys: object) -> None:
    assert (
        main(["--samples", "200", "--seed", "2", "--shift", "covariate", "--magnitude", "0.4"]) == 0
    )
    output = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert output["config"]["target_shift"]["kind"] == "covariate"
