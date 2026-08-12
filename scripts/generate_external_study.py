"""Generate the immutable v1.2 observational reference-data registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fairshift_lab.external_study import run_external_study


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/external/adult"))
    parser.add_argument("--output", type=Path, default=Path("reports/v1.2-external-study.json"))
    args = parser.parse_args()
    payload = run_external_study(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
