"""Generate the immutable v1.1 decision-policy benchmark registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fairshift_lab.policy_study import PolicyStudyConfig, run_policy_study


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/v1.1-policy-study.json"))
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--samples", type=int, default=1_000)
    args = parser.parse_args()
    config = PolicyStudyConfig(
        seeds=tuple(range(100, 100 + args.seeds)),
        samples=args.samples,
    )
    payload = run_policy_study(config).as_dict()
    payload["schema_version"] = "1.1"
    payload["generator"] = "fairshift_lab.policy_study.run_policy_study"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
