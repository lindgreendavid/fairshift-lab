import numpy as np

from fairshift_lab.metrics import evaluate, group_rates, roc_auc


def test_roc_auc_is_one_for_perfect_ranking() -> None:
    assert roc_auc(np.array([0, 1]), np.array([0.1, 0.9])) == 1.0


def test_roc_auc_gives_half_credit_to_ties() -> None:
    assert roc_auc(np.array([0, 1]), np.array([0.5, 0.5])) == 0.5


def test_roc_auc_returns_neutral_value_for_single_class() -> None:
    assert roc_auc(np.array([1, 1]), np.array([0.2, 0.8])) == 0.5


def test_group_rates_handle_missing_condition() -> None:
    rates = group_rates(np.array([1, 1]), np.array([1, 0]), np.array([0, 0]), 1)
    assert rates.selection_rate == rates.true_positive_rate == rates.false_positive_rate == 0.0


def test_evaluate_reports_performance_and_fairness() -> None:
    metrics = evaluate(
        np.array([0, 1, 0, 1]),
        np.array([0.1, 0.9, 0.8, 0.9]),
        np.array([0, 0, 1, 1]),
        0.5,
    )
    assert metrics["accuracy"] == 0.75
    assert metrics["demographic_parity_difference"] == 0.5
    assert metrics["equalized_odds_difference"] == 1.0
    assert set(metrics["groups"]) == {"0", "1"}  # type: ignore[arg-type]
