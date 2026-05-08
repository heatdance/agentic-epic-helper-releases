#!/usr/bin/env python3
"""
Run benchmark_verify then benchmark_aggregate for one hub suite (repo root cwd).

Keeps finalize non-interactive logs small: one subprocess chain, tee-friendly.
Does **not** write **report.md** or **pipeline-delta-queue.json** — those belong under
``.cursor/benchmark/run-results/<run-key>/`` (see ``run-results/README.md`` and
``FINALIZE_PROMPT.example.md`` §4).

Usage::

  python automation/tools/benchmark_finalize_hub.py \\
    --suite-dir .cursor/benchmark/runs/<suite_id> [--gold-root <dir>] [--skip-verify]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _repo_root_containing(parts_up: Path) -> Path:
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


def main() -> int:
    ap = argparse.ArgumentParser(
        description="benchmark_verify --strict-manifest + benchmark_aggregate for a hub suite.",
    )
    ap.add_argument(
        "--suite-dir",
        type=Path,
        required=True,
        help="Suite folder (.cursor/benchmark/runs/<suite_id>/)",
    )
    ap.add_argument(
        "--gold-root",
        type=Path,
        default=None,
        help="Passed through to benchmark_aggregate/compare_runs (optional)",
    )
    ap.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip benchmark_verify.py (compare only)",
    )
    args = ap.parse_args()

    suite_dir = args.suite_dir.resolve()
    repo_root = _repo_root_containing(suite_dir)
    tools = repo_root / "automation" / "tools"
    verify = tools / "benchmark_verify.py"
    aggregate = tools / "benchmark_aggregate.py"

    if not verify.is_file() or not aggregate.is_file():
        print("benchmark_verify.py or benchmark_aggregate.py not found under automation/tools/", file=sys.stderr)
        return 2

    worst = 0
    try:
        rel_suite = suite_dir.relative_to(repo_root).as_posix()
    except ValueError:
        rel_suite = str(suite_dir)

    if not args.skip_verify:
        cmd_v = [
            sys.executable,
            str(verify),
            "--suite-dir",
            rel_suite,
            "--strict-manifest",
        ]
        print(f"+ {' '.join(cmd_v)}", flush=True)
        proc_v = subprocess.run(cmd_v, cwd=repo_root)
        worst = max(worst, proc_v.returncode)
        if proc_v.returncode != 0:
            return proc_v.returncode

    cmd_a = [
        sys.executable,
        str(aggregate),
        "--suite-dir",
        rel_suite,
    ]
    if args.gold_root is not None:
        gr = args.gold_root.resolve()
        try:
            cmd_a.extend(["--gold-root", gr.relative_to(repo_root).as_posix()])
        except ValueError:
            cmd_a.extend(["--gold-root", str(gr)])
    print(f"+ {' '.join(cmd_a)}", flush=True)
    proc_a = subprocess.run(cmd_a, cwd=repo_root)
    worst = max(worst, proc_a.returncode)
    return worst if worst else 0


if __name__ == "__main__":
    raise SystemExit(main())
