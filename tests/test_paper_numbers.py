import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
TEX = (ROOT / "paper" / "paper.tex").read_text(encoding="utf-8")
AUDIT = json.loads((ROOT / "reports" / "post-release-external-audit.json").read_text())
FROZEN = json.loads((ROOT / "reports" / "v1.2-external-study.json").read_text())
PRIMARY = [
    cell
    for cell in AUDIT["cells"]
    if cell["cohort"] == "provider_eligible" and cell["missingness"] == "complete_case"
]
POLICIES = ("baseline", "source_cost_threshold", "reweighed_training", "group_threshold")


def mean(values: list[float]) -> float:
    return float(np.mean(values))


def test_table_one_matches_audit() -> None:
    for policy in POLICIES:
        entries = [cell["policies"][policy]["equalized_odds_difference"] for cell in PRIMARY]
        assert f"{mean([e['estimate'] for e in entries]):.3f}" in TEX
        assert f"{mean([e['interval_95'][0] for e in entries]):.3f}" in TEX
        assert f"{mean([e['interval_95'][1] for e in entries]):.3f}" in TEX
    floor = mean([c["noise_floor_equalized_odds"][p]["mean"] for c in PRIMARY for p in POLICIES])
    assert f"{floor:.3f}" in TEX


def test_frozen_means_match_audit_point_estimates() -> None:
    cells = {
        (c["cohort"], c["missingness"], c["false_negative_cost"], c["policy"]): c
        for c in FROZEN["cells"]
    }
    for policy in POLICIES:
        frozen = cells[("provider_eligible", "complete_case", 1.0, policy)]["estimates"]
        audited = mean(
            [c["policies"][policy]["equalized_odds_difference"]["estimate"] for c in PRIMARY]
        )
        assert abs(frozen["equalized_odds_difference"]["mean"] - audited) < 1e-6


def test_headline_counts() -> None:
    comparisons = excluded = accuracy_excluded = 0
    for cell in AUDIT["cells"]:
        for policy in POLICIES[1:]:
            paired = cell["policies"][policy]["paired_difference_from_baseline"]
            comparisons += 1
            excluded += paired["equalized_odds_difference"]["interval_excludes_zero"]
        accuracy_excluded += cell["policies"]["group_threshold"]["paired_difference_from_baseline"][
            "accuracy"
        ]["interval_excludes_zero"]
    assert (comparisons, excluded) == (60, 0) and "60 paired" in TEX
    assert accuracy_excluded == 18 and "18 of 20" in TEX
    ratios = [
        cell["policies"][p]["equalized_odds_difference"]["estimate"]
        / cell["noise_floor_equalized_odds"][p]["mean"]
        for cell in AUDIT["cells"]
        for p in POLICIES
    ]
    assert f"{min(ratios):.2f}" in TEX and f"{max(ratios):.1f}" in TEX
    assert f"about {mean(ratios):.1f}" in TEX or f"{mean(ratios):.1f}" in TEX


def test_paired_difference_table() -> None:
    for policy in ("reweighed_training", "group_threshold"):
        for metric in ("accuracy", "equalized_odds_difference"):
            diffs = [
                c["policies"][policy]["paired_difference_from_baseline"][metric] for c in PRIMARY
            ]
            assert f"{abs(mean([d['baseline_minus_policy'] for d in diffs])):.3f}" in TEX
