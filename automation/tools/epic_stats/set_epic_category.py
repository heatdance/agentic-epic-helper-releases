#!/usr/bin/env python3
"""Record a manual epic category review in stats/epic-stats/epic-categories.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from epic_stats.apply_categories import set_epic_review  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Set manual epic category in registry")
    p.add_argument("--epic", required=True, help="CRT-KEY")
    p.add_argument(
        "--category",
        required=True,
        choices=["fe", "be", "api", "other"],
        help="Top-level category",
    )
    p.add_argument("--rationale", required=True, help="1-2 sentence justification")
    p.add_argument("--evidence", nargs="*", default=[], help="CR keys, yogi paths, etc.")
    args = p.parse_args()
    path = set_epic_review(
        args.epic,
        args.category,
        args.rationale,
        evidence=args.evidence,
    )
    print(f"wrote {path} epic={args.epic.upper()} category={args.category}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
