"""Fetch the pinned UCI Adult archive and verify it before extraction."""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
import zipfile
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/2/adult.zip"
SHA256 = "7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb"
MEMBERS = ("adult.data", "adult.test", "adult.names")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/external/adult"))
    args = parser.parse_args()
    archive = args.output.parent / "adult.zip"
    args.output.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(URL, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != SHA256:
        archive.unlink(missing_ok=True)
        raise RuntimeError(f"Adult archive checksum mismatch: {digest}")
    with zipfile.ZipFile(archive) as source:
        for member in MEMBERS:
            source.extract(member, args.output)
    archive.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
