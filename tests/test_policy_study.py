import pytest

from fairshift_lab.policy_study import PolicyStudyConfig, run_policy_study


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"seeds": (1,)}, "unique seeds"),
        ({"seeds": (1, 1)}, "unique seeds"),
        ({"samples": 99}, "at least 100"),
        ({"magnitude": 1.1}, "between 0 and 1"),
        ({"false_negative_costs": ()}, "positive"),
        ({"false_negative_costs": (0.0,)}, "positive"),
    ],
)
def test_policy_study_config_validates(kwargs: object, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        PolicyStudyConfig(**kwargs)  # type: ignore[arg-type]


def test_policy_study_is_reproducible_and_marks_relative_frontier() -> None:
    config = PolicyStudyConfig(seeds=(7, 11), samples=100, false_negative_costs=(1.0,))
    first = run_policy_study(config)
    second = run_policy_study(config)
    assert first == second
    assert len(first.cells) == 24
    assert len(first.policies) == 8
    assert first.as_dict()["config"]["samples"] == 100  # type: ignore[index]
    assert any(cell.pareto_efficient for cell in first.cells)
    assert all(cell.replications == 2 for cell in first.cells)
    assert all(
        cell.metrics["expected_cost"].replication_lower
        <= cell.metrics["expected_cost"].mean
        <= cell.metrics["expected_cost"].replication_upper
        for cell in first.cells
    )
