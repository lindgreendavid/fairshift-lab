"""Command-line interface for one reproducible experiment."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from fairshift_lab.config import ExperimentConfig, ShiftConfig, ShiftKind
from fairshift_lab.experiment import run_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shift", choices=[kind.value for kind in ShiftKind], default="none")
    parser.add_argument("--magnitude", type=float, default=0.0)
    parser.add_argument("--samples", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    shift = ShiftConfig(kind=ShiftKind(args.shift), magnitude=args.magnitude)
    result = run_experiment(
        ExperimentConfig(samples=args.samples, seed=args.seed, target_shift=shift)
    )
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
