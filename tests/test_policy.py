import numpy as np
import pytest

from fairshift_lab.model import LogisticBaseline
from fairshift_lab.policy import (
    evaluate_policy,
    joint_reweighing_weights,
    normalized_expected_cost,
    predictions_for_thresholds,
    ranking_auc,
    select_cost_threshold,
    select_group_thresholds,
)


def test_reweighing_balances_group_label_cells() -> None:
    labels = np.array([0, 0, 0, 1, 0, 1, 1, 1], dtype=np.int64)
    sensitive = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=np.int64)
    weights = joint_reweighing_weights(labels, sensitive)
    assert weights.shape == labels.shape
    weighted_joint = {
        (group, label): float(weights[(sensitive == group) & (labels == label)].sum())
        for group in (0, 1)
        for label in (0, 1)
    }
    assert len(set(weighted_joint.values())) == 1


@pytest.mark.parametrize(
    ("labels", "sensitive", "message"),
    [
        (np.array([], dtype=np.int64), np.array([], dtype=np.int64), "at least one"),
        (np.array([0, 1]), np.array([[0, 1]]), "matching"),
        (np.array([0, 0]), np.array([0, 1]), "every group-label"),
    ],
)
def test_reweighing_rejects_invalid_inputs(
    labels: np.ndarray, sensitive: np.ndarray, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        joint_reweighing_weights(labels, sensitive)


def test_group_thresholds_and_cost_metrics_are_explicit() -> None:
    labels = np.array([0, 1, 0, 1], dtype=np.int64)
    sensitive = np.array([0, 0, 1, 1], dtype=np.int64)
    probabilities = np.array([0.2, 0.7, 0.4, 0.8])
    predictions = predictions_for_thresholds(probabilities, sensitive, 0.5, 0.75)
    assert predictions.tolist() == [0, 1, 0, 1]
    assert normalized_expected_cost(labels, predictions, 2.0) == 0.0
    metrics = evaluate_policy(labels, probabilities, sensitive, 0.5, 0.75, 2.0, 2)
    assert metrics.accuracy == 1.0
    assert metrics.expected_cost == 0.0


def test_threshold_selectors_are_deterministic() -> None:
    labels = np.array([0, 0, 1, 1], dtype=np.int64)
    probabilities = np.array([0.1, 0.4, 0.6, 0.9])
    sensitive = np.array([0, 1, 0, 1], dtype=np.int64)
    assert select_cost_threshold(labels, probabilities, 1.0, (0.3, 0.5, 0.7)) == 0.5
    assert select_group_thresholds(labels, probabilities, sensitive, 1.0, 0.5, (0.3, 0.5, 0.7)) == (
        0.5,
        0.5,
    )
    with pytest.raises(ValueError, match="candidates"):
        select_cost_threshold(labels, probabilities, 1.0, ())
    with pytest.raises(ValueError, match="non-negative"):
        select_group_thresholds(labels, probabilities, sensitive, 1.0, -1.0)
    with pytest.raises(ValueError, match="candidates"):
        select_group_thresholds(labels, probabilities, sensitive, 1.0, 0.5, ())
    assert ranking_auc(labels, probabilities) == 1.0


def test_error_cost_and_weight_validation() -> None:
    labels = np.array([0, 1], dtype=np.int64)
    predictions = np.array([1, 0], dtype=np.int64)
    with pytest.raises(ValueError, match="positive"):
        normalized_expected_cost(labels, predictions, 0.0)
    model = LogisticBaseline(iterations=1)
    features = np.zeros((2, 3))
    with pytest.raises(ValueError, match="match labels"):
        model.fit(features, labels, np.ones(3))
    with pytest.raises(ValueError, match="positive total"):
        model.fit(features, labels, np.zeros(2))
