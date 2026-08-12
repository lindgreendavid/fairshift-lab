"""Generate the immutable v1.3 synthetic specification-stress registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fairshift_lab.robustness import RobustnessStudyConfig, run_robustness_study


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/v1.3-robustness-study.json"))
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--samples", type=int, default=2_000)
    args = parser.parse_args()
    config = RobustnessStudyConfig(
        seeds=tuple(range(300, 300 + args.seeds)),
        samples=args.samples,
    )
    payload = run_robustness_study(config)
    payload["generator"] = "fairshift_lab.robustness.run_robustness_study"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
