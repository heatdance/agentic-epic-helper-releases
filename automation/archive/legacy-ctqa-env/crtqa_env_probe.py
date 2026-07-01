#!/usr/bin/env python3
"""
Probe CTQA environment gates (Postgres tunnel + crtqa console multiplex).

Used by /crtqa-env and TEST-DISCOVER Phase 0. Always checks both gates; optional
--coverage labels which are required for a given epic per test-discover.md rubric.

Examples:
  python automation/tools/crtqa_env_probe.py
  python automation/tools/crtqa_env_probe.py --coverage epics/CRT-639/CRT-639-coverage.json
  python automation/tools/crtqa_env_probe.py --format text
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from crtqa_env_common import build_gate_results, load_coverage, repo_root_from_here


def main() -> int:
    parser = argparse.ArgumentParser(description="CTQA environment gate probe")
    parser.add_argument(
        "--coverage",
        type=Path,
        help="Epic coverage JSON for tooling_intent labels (required_for_epic)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text", "both"),
        default="both",
        help="Output format (default: both JSON stdout + checklist on stderr)",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository root (default: parent of automation/)",
    )
    args = parser.parse_args()

    repo = args.repo or repo_root_from_here()
    coverage = load_coverage(args.coverage) if args.coverage else None
    if args.coverage and coverage is None:
        print(f"Failed to load coverage: {args.coverage}", file=sys.stderr)
        return 2

    doc = build_gate_results(coverage, repo=repo)

    if args.format in ("json", "both"):
        print(json.dumps(doc, indent=2, ensure_ascii=False))

    if args.format in ("text", "both"):
        md = doc.get("checklist_markdown") or ""
        stream = sys.stderr if args.format == "both" else sys.stdout
        print(md, file=stream)

    if doc.get("blocking_fail"):
        return 1
    if doc.get("overall") == "fail":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
