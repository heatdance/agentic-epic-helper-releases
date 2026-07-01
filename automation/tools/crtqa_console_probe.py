#!/usr/bin/env python3
"""
Probe crtqa dxCore console multiplex (epic-helper env gate + GROUND preflight).

Examples:
  python automation/tools/crtqa_console_probe.py
  python automation/tools/crtqa_console_probe.py --format text
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from crtqa_console_common import build_console_gate_results, repo_root_from_here


def main() -> int:
    parser = argparse.ArgumentParser(description="CTQA console multiplex gate probe")
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
    doc = build_console_gate_results(repo=repo)

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
