import numpy as np
import pytest

from fairshift_lab.sensitivity import threshold_sweep


def test_threshold_sweep_exposes_metric_trajectory() -> None:
    result = threshold_sweep(
        np.array([0, 1, 0, 1]),
        np.array([0.1, 0.4, 0.6, 0.9]),
        np.array([0, 0, 1, 1]),
        thresholds=(0.25, 0.75),
    )
    assert [point["threshold"] for point in result] == [0.25, 0.75]
    assert result[0]["accuracy"] == result[1]["accuracy"] == 0.75
    assert result[0]["roc_auc"] == result[1]["roc_auc"]
    assert result[0]["equal_opportunity_difference"] != result[1]["equal_opportunity_difference"]


@pytest.mark.parametrize("thresholds", [(), (0.0,), (1.0,)])
def test_threshold_sweep_rejects_invalid_grid(thresholds: tuple[float, ...]) -> None:
    with pytest.raises(ValueError, match="strictly between"):
        threshold_sweep(np.array([0]), np.array([0.5]), np.array([0]), thresholds)
