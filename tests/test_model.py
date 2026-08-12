import numpy as np
import pytest

from fairshift_lab.model import LogisticBaseline, ShallowDecisionTree


def test_model_learns_linearly_separable_data() -> None:
    features = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    labels = np.array([0, 0, 1, 1])
    model = LogisticBaseline(iterations=1_000).fit(features, labels)
    assert np.array_equal(model.predict(features), labels)


def test_predict_proba_requires_fit() -> None:
    with pytest.raises(RuntimeError, match="must be fitted"):
        LogisticBaseline().predict_proba(np.zeros((2, 1)))


def test_custom_threshold_changes_predictions() -> None:
    features = np.array([[-1.0], [0.0], [1.0]])
    labels = np.array([0, 0, 1])
    model = LogisticBaseline(iterations=500).fit(features, labels)
    assert model.predict(features, 0.8).sum() <= model.predict(features, 0.2).sum()


def _separable_tree_fixture() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    left = rng.normal(-2.0, 0.3, size=(60, 2))
    right = rng.normal(2.0, 0.3, size=(60, 2))
    features = np.vstack([left, right])
    labels = np.array([0] * 60 + [1] * 60)
    return features, labels


def test_tree_learns_a_separable_split() -> None:
    features, labels = _separable_tree_fixture()
    tree = ShallowDecisionTree(max_depth=3, min_samples_leaf=5).fit(features, labels)
    predictions = tree.predict(features)
    assert float(np.mean(predictions == labels)) > 0.9


def test_tree_predict_proba_requires_fit() -> None:
    with pytest.raises(RuntimeError, match="must be fitted"):
        ShallowDecisionTree().predict_proba(np.zeros((2, 1)))


def test_tree_leaf_probabilities_never_saturate() -> None:
    features, labels = _separable_tree_fixture()
    tree = ShallowDecisionTree(max_depth=3, min_samples_leaf=5).fit(features, labels)
    probabilities = tree.predict_proba(features)
    assert np.all(probabilities > 0.0)
    assert np.all(probabilities < 1.0)


def test_tree_respects_sample_weights() -> None:
    features = np.array([[-1.0], [-1.0], [1.0], [1.0]])
    labels = np.array([0, 1, 1, 1])
    unweighted = ShallowDecisionTree(max_depth=1, min_samples_leaf=1).fit(features, labels)
    weighted = ShallowDecisionTree(max_depth=1, min_samples_leaf=1).fit(
        features, labels, sample_weights=np.array([1.0, 0.0, 1.0, 1.0])
    )
    assert unweighted.predict_proba(features[:1])[0] != weighted.predict_proba(features[:1])[0]


def test_tree_rejects_invalid_configuration_and_weights() -> None:
    features = np.array([[0.0], [1.0]])
    labels = np.array([0, 1])
    with pytest.raises(ValueError, match="max_depth"):
        ShallowDecisionTree(max_depth=-1).fit(features, labels)
    with pytest.raises(ValueError, match="min_samples_leaf"):
        ShallowDecisionTree(min_samples_leaf=0).fit(features, labels)
    with pytest.raises(ValueError, match="must match"):
        ShallowDecisionTree().fit(features, labels, sample_weights=np.array([1.0]))
    with pytest.raises(ValueError, match="non-negative"):
        ShallowDecisionTree().fit(features, labels, sample_weights=np.array([-1.0, 1.0]))


def test_tree_stops_at_min_samples_leaf_and_stays_a_single_leaf() -> None:
    features, labels = _separable_tree_fixture()
    tree = ShallowDecisionTree(max_depth=3, min_samples_leaf=1_000).fit(features, labels)
    assert tree.root is not None
    assert tree.root.is_leaf


def test_tree_handles_constant_features_without_splitting() -> None:
    features = np.ones((30, 2))
    labels = np.array([0, 1] * 15)
    tree = ShallowDecisionTree(max_depth=3, min_samples_leaf=2).fit(features, labels)
    assert tree.root is not None
    assert tree.root.is_leaf
    probabilities = tree.predict_proba(features)
    assert np.allclose(probabilities, probabilities[0])
