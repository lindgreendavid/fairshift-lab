"""Generate the post-hoc test-set uncertainty audit of the v1.2 external study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fairshift_lab.external_audit import build_external_audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/external/adult"))
    parser.add_argument(
        "--output", type=Path, default=Path("reports/post-release-external-audit.json")
    )
    args = parser.parse_args()
    payload = build_external_audit(args.data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
