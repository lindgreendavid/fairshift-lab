"""Compact the post-hoc external audit into the small file the site imports."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean

POLICIES = ("baseline", "source_cost_threshold", "reweighed_training", "group_threshold")


def build(audit: dict) -> dict:  # type: ignore[type-arg]
    groups: dict[tuple[str, str], list[dict]] = {}  # type: ignore[type-arg]
    for cell in audit["cells"]:
        groups.setdefault((cell["cohort"], cell["missingness"]), []).append(cell)
    out = []
    for (cohort, missingness), cells in groups.items():
        policies = {}
        for policy in POLICIES:
            eod = [c["policies"][policy]["equalized_odds_difference"] for c in cells]
            entry = {
                "equalized_odds": round(fmean(e["estimate"] for e in eod), 4),
                "lower": round(fmean(e["interval_95"][0] for e in eod), 4),
                "upper": round(fmean(e["interval_95"][1] for e in eod), 4),
                "noise_floor": round(
                    fmean(c["noise_floor_equalized_odds"][policy]["mean"] for c in cells), 4
                ),
            }
            if policy != "baseline":
                paired = [c["policies"][policy]["paired_difference_from_baseline"] for c in cells]
                entry["gap_reduction"] = round(
                    fmean(p["equalized_odds_difference"]["baseline_minus_policy"] for p in paired),
                    4,
                )
                entry["gap_reduction_lower"] = round(
                    fmean(p["equalized_odds_difference"]["interval_95"][0] for p in paired), 4
                )
                entry["gap_reduction_upper"] = round(
                    fmean(p["equalized_odds_difference"]["interval_95"][1] for p in paired), 4
                )
                entry["gap_intervals_excluding_zero"] = sum(
                    p["equalized_odds_difference"]["interval_excludes_zero"] for p in paired
                )
                entry["accuracy_intervals_excluding_zero"] = sum(
                    p["accuracy"]["interval_excludes_zero"] for p in paired
                )
            policies[policy] = entry
        out.append(
            {
                "cohort": cohort,
                "missingness": missingness,
                "test_size": cells[0]["test_size"],
                "seeds": len(cells),
                "policies": policies,
            }
        )
    return {
        "label": audit["label"],
        "false_negative_cost": audit["false_negative_cost"],
        "resamples": audit["cells"][0]["resamples"],
        "cohorts": out,
    }


def main() -> int:
    audit = json.loads(Path("reports/post-release-external-audit.json").read_text(encoding="utf-8"))
    target = Path("site/app/external-audit-summary.json")
    target.write_text(json.dumps(build(audit), indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
