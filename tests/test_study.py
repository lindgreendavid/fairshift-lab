import pytest

from fairshift_lab.study import StudyConfig, run_study


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"seeds": (1,)}, "at least two"),
        ({"seeds": (1, 1)}, "unique"),
        ({"samples": 99}, "at least 100"),
        ({"magnitudes": ()}, "at least one"),
        ({"magnitudes": (1.1,)}, "between 0 and 1"),
    ],
)
def test_study_config_validates_inputs(kwargs: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        StudyConfig(**kwargs)  # type: ignore[arg-type]


def test_study_is_reproducible_and_summarizes_changes() -> None:
    config = StudyConfig(seeds=(7, 11), magnitudes=(0.0, 1.0), samples=100)
    first = run_study(config)
    second = run_study(config)
    assert first == second
    assert len(first.cells) == 6
    assert first.cells[0].replications == 2
    assert set(first.cells[0].target) == {
        "accuracy",
        "roc_auc",
        "demographic_parity_difference",
        "equal_opportunity_difference",
        "equalized_odds_difference",
        "brier_score",
        "expected_calibration_error",
    }
    assert first.as_dict()["config"]["seeds"] == (7, 11)  # type: ignore[index]
    estimate = first.cells[-1].source_to_target_change["accuracy"]
    assert estimate.replication_lower <= estimate.mean <= estimate.replication_upper
