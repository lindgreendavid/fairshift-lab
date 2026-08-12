# ruff: noqa: E501 -- literal CSV fixtures preserve the provider's 15-column shape.

from pathlib import Path

import numpy as np
import pytest

from fairshift_lab.external_study import ExternalStudyConfig, load_adult, run_external_study


def _write(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n")


ROWS = [
    "39, State-gov, 77516, Bachelors, 13, Never-married, Adm-clerical, Not-in-family, White, Male, 2174, 0, 40, United-States, <=50K",
    "50, ?, 83311, Bachelors, 13, Married-civ-spouse, Exec-managerial, Husband, White, Male, 0, 0, 13, United-States, >50K",
    "28, Private, 338409, Bachelors, 13, Married-civ-spouse, Prof-specialty, Wife, Black, Female, 0, 0, 40, Cuba, >50K",
    "23, Private, 215646, HS-grad, 9, Never-married, Other-service, Own-child, White, Female, 0, 0, 30, Mexico, <=50K",
]


def test_load_adult_applies_cohort_missingness_and_test_suffix(tmp_path: Path) -> None:
    source = tmp_path / "adult.test"
    _write(source, ["| header", *(row + "." for row in ROWS)])
    complete = load_adult(source, minimum_age=25, complete_case=True)
    numeric = load_adult(source, minimum_age=17, complete_case=False)
    assert complete.labels.tolist() == [0, 1]
    assert complete.sensitive.tolist() == [1, 0]
    assert numeric.features.shape == (4, 5)
    assert np.isfinite(numeric.features).all()


def test_load_adult_rejects_empty_file(tmp_path: Path) -> None:
    source = tmp_path / "empty"
    source.write_text("not,data\n")
    with pytest.raises(ValueError, match="no eligible"):
        load_adult(source, minimum_age=17, complete_case=True)


def test_external_config_requires_unique_replications(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="two unique"):
        run_external_study(tmp_path, ExternalStudyConfig(seeds=(1, 1)))


def test_external_study_emits_every_preregistered_sensitivity_cell(tmp_path: Path) -> None:
    data_dir = tmp_path / "adult"
    data_dir.mkdir()
    templates = [
        "39, Private, 1, HS-grad, 9, Never-married, Adm-clerical, Not-in-family, White, Male, 0, 0, 40, United-States, <=50K",
        "39, Private, 1, Bachelors, 13, Married, Exec-managerial, Husband, White, Male, 1000, 0, 40, United-States, >50K",
        "39, Private, 1, HS-grad, 9, Never-married, Service, Not-in-family, Black, Female, 0, 0, 30, United-States, <=50K",
        "39, Private, 1, Bachelors, 13, Married, Professional, Wife, Black, Female, 1000, 0, 40, United-States, >50K",
        "23, Private, 1, HS-grad, 9, Never-married, Service, Child, White, Male, 0, 0, 25, United-States, <=50K",
        "23, Private, 1, Bachelors, 13, Married, Professional, Husband, White, Male, 1000, 0, 40, United-States, >50K",
        "23, Private, 1, HS-grad, 9, Never-married, Service, Child, Black, Female, 0, 0, 25, United-States, <=50K",
        "23, Private, 1, Bachelors, 13, Married, Professional, Wife, Black, Female, 1000, 0, 40, United-States, >50K",
    ]
    development = [row for row in templates for _ in range(20)]
    testing = [row + "." for row in templates for _ in range(5)]
    _write(data_dir / "adult.data", development)
    _write(data_dir / "adult.test", ["| header", *testing])
    result = run_external_study(
        data_dir,
        ExternalStudyConfig(seeds=(1, 2), false_negative_costs=(1.0,)),
    )
    assert result["schema_version"] == "1.2"
    assert len(result["cells"]) == 16
    first = result["cells"][0]
    assert first["replications"] == 2
    assert first["subgroup_counts"]["test_total"] > 0
    assert set(first["estimates"]) >= {"accuracy", "equalized_odds_difference"}
