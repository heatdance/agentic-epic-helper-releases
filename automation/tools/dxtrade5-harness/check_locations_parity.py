#!/usr/bin/env python3
"""Parity check: compass features in concept-map vs keys in locations/ctqa.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository root (default: inferred)",
    )
    args = p.parse_args()
    root: Path = args.repo
    concept = root / "docs" / "dxtrade5-harness" / "concept-map.json"
    ctqa = root / "docs" / "dxtrade5-harness" / "locations" / "ctqa.json"

    if not concept.is_file() or not ctqa.is_file():
        print("Missing concept-map.json or locations/ctqa.json", file=sys.stderr)
        return 2

    cm = json.loads(concept.read_text(encoding="utf-8"))
    loc = json.loads(ctqa.read_text(encoding="utf-8"))

    compass = {f["id"] for f in cm["features"] if f.get("priority") == "compass"}
    keys = set(loc.get("locations", {}).keys())

    missing = sorted(compass - keys)
    extra = sorted(keys - {f["id"] for f in cm["features"]})

    ok = not missing and not extra
    if missing:
        print("Missing location entries for compass features:", *missing, sep="\n  - ", file=sys.stderr)
    if extra:
        print("ctqa.json keys not in concept-map:", *extra, sep="\n  - ", file=sys.stderr)

    unverified = []
    for fid in sorted(compass & keys):
        entry = loc["locations"][fid]
        if not entry.get("primary_path_ok") and not entry.get("drift_notes"):
            unverified.append(fid)
    if unverified:
        print(
            "Compass entries without primary_path_ok and without drift_notes:",
            *unverified,
            sep="\n  - ",
            file=sys.stderr,
        )
        ok = False

    if ok:
        print(f"OK: {len(compass)} compass features present in ctqa.json with drift or verified.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
