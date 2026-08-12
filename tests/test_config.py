import pytest

from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind


def test_default_shift_is_unshifted() -> None:
    assert ShiftConfig() == ShiftConfig(ShiftKind.NONE, 0.0)


@pytest.mark.parametrize("magnitude", [-0.1, 1.1])
def test_shift_rejects_invalid_magnitude(magnitude: float) -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        ShiftConfig(ShiftKind.COVARIATE, magnitude)


def test_none_shift_rejects_nonzero_magnitude() -> None:
    with pytest.raises(ValueError, match="magnitude 0"):
        ShiftConfig(ShiftKind.NONE, 0.2)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"samples": 99}, "at least 100"),
        ({"decision_threshold": 0.0}, "strictly between"),
        ({"learning_rate": 0.0}, "positive"),
        ({"iterations": 0}, "positive"),
        ({"bootstrap_samples": 19}, "at least 20"),
        ({"confidence_level": 0.49}, "between 0.5 and 1"),
        ({"confidence_level": 1.0}, "between 0.5 and 1"),
        ({"calibration_bins": 1}, "between 2 and 50"),
        ({"calibration_bins": 51}, "between 2 and 50"),
    ],
)
def test_experiment_rejects_invalid_inputs(changes: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        ExperimentConfig(**changes)  # type: ignore[arg-type]
