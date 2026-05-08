#!/usr/bin/env python3
"""
Run compare_runs.py for every epic listed in a hub _manifest.json.

Kinds are chosen from **`_manifest.json` `modes`** when present:

- ``epic_prep`` → ``--kind prep``
- ``coverage`` → ``--kind coverage``
- ``test_prep`` → ``--kind test``

When ``modes`` is missing or empty, defaults to prep + coverage (legacy).

Usage (repo root)::

  python automation/tools/benchmark_aggregate.py --suite-dir .cursor/benchmark/runs/my-suite-id
  python automation/tools/benchmark_aggregate.py --suite-dir ... --gold-root data/CRT-639

Delegates to ``.cursor/benchmark/coverage-bench/scripts/compare_runs.py`` with
``--suite-run-dir`` (suite folder basename is the metrics suite_id).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _repo_root_containing(parts_up: Path) -> Path:
    """Walk up until `.git` or a minimal repo marker exists."""
    cur = parts_up.resolve()
    for _ in range(24):
        if (cur / ".git").is_dir():
            return cur
        if (cur / "README.md").is_file() and (cur / "docs").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return parts_up.resolve()


def _kinds_from_manifest_modes(spec: dict) -> list[str]:
    modes = spec.get("modes")
    if not isinstance(modes, list) or not modes:
        return ["prep", "coverage"]
    kinds: list[str] = []
    if "epic_prep" in modes:
        kinds.append("prep")
    if "coverage" in modes:
        kinds.append("coverage")
    if "test_prep" in modes:
        kinds.append("test")
    return kinds if kinds else ["prep", "coverage"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run compare_runs for each epic in a hub manifest (modes-aware).",
    )
    parser.add_argument(
        "--suite-dir",
        type=Path,
        required=True,
        help="Suite folder (.cursor/benchmark/runs/<suite_id>/) containing _manifest.json",
    )
    parser.add_argument(
        "--gold-root",
        type=Path,
        default=None,
        help=(
            "Directory containing <EPIC>-gold.json; forwarded to compare_runs "
            "(omit to use compare_runs defaults)"
        ),
    )
    args = parser.parse_args()

    suite_dir = args.suite_dir.resolve()
    repo_root = _repo_root_containing(suite_dir)
    manifest = suite_dir / "_manifest.json"

    if not manifest.is_file():
        print(f"manifest not found: {manifest}", file=sys.stderr)
        return 2

    try:
        with manifest.open(encoding="utf-8") as f:
            spec = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"manifest unreadable: {exc}", file=sys.stderr)
        return 2

    kinds = _kinds_from_manifest_modes(spec if isinstance(spec, dict) else {})

    epics_raw = spec.get("epics") if isinstance(spec, dict) else None
    if not isinstance(epics_raw, list) or not epics_raw:
        print("_manifest.json: missing non-empty epics array", file=sys.stderr)
        return 2

    epics: list[str] = []
    for e in epics_raw:
        if isinstance(e, str) and e.strip():
            epics.append(e.strip().upper())

    if not epics:
        print("_manifest.json: epics[] has no usable keys", file=sys.stderr)
        return 2

    compare_script = (
        repo_root
        / ".cursor"
        / "benchmark"
        / "coverage-bench"
        / "scripts"
        / "compare_runs.py"
    )
    if not compare_script.is_file():
        print(f"compare_runs.py not found: {compare_script}", file=sys.stderr)
        return 2

    worst = 0
    try:
        suite_run_flag = suite_dir.relative_to(repo_root).as_posix()
    except ValueError:
        suite_run_flag = str(suite_dir)

    gold_root_arg = args.gold_root.resolve() if args.gold_root is not None else None
    gold_flag: list[str] = []
    if gold_root_arg is not None:
        try:
            gold_flag = ["--gold-root", gold_root_arg.relative_to(repo_root).as_posix()]
        except ValueError:
            gold_flag = ["--gold-root", str(gold_root_arg)]

    for epic in sorted(set(epics)):
        for kind in kinds:
            cmd = [
                sys.executable,
                str(compare_script),
                "--epic",
                epic,
                "--kind",
                kind,
                "--suite-run-dir",
                suite_run_flag,
            ]
            cmd.extend(gold_flag)
            print(f"+ {' '.join(cmd)}", flush=True)
            proc = subprocess.run(cmd, cwd=repo_root)
            if proc.returncode != 0:
                worst = max(worst, proc.returncode)
                print(f"! exit {proc.returncode} epic={epic} kind={kind}", file=sys.stderr)

    return worst if worst else 0


if __name__ == "__main__":
    raise SystemExit(main())
