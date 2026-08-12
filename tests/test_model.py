import numpy as np
import pytest

from fairshift_lab.model import LogisticBaseline


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
