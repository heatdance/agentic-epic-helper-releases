#!/usr/bin/env python3
"""
Render stats/crtqa-stats/latest-team.md from user state files.

Examples:
  python automation/tools/crtqa_stats_team_rollup.py
  python automation/tools/crtqa_stats_team_rollup.py --users mshpak,amukanova
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "automation" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from crtqa_stats.apply_categories import apply_epic_categories_to_state  # noqa: E402
from crtqa_stats.ingest import (  # noqa: E402
    discover_team_users_with_state,
    latest_team_path,
    load_contract,
    load_state,
    team_users_from_contract,
)
from crtqa_stats.render_team_report import render_team_markdown  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="CRTQA stats team rollup")
    parser.add_argument(
        "--users",
        default="",
        help="Comma-separated Jira users (default: roster with state on disk)",
    )
    args = parser.parse_args()
    contract = load_contract()

    if args.users.strip():
        users = [u.strip() for u in args.users.split(",") if u.strip()]
    else:
        users = discover_team_users_with_state(contract)
        if not users:
            users = team_users_from_contract(contract)

    states = []
    loaded_users: list[str] = []
    for user in users:
        try:
            state = load_state(user, contract)
        except FileNotFoundError:
            print(f"skip {user}: no state", file=sys.stderr)
            continue
        apply_epic_categories_to_state(state, contract)
        states.append(state)
        loaded_users.append(user)

    if not states:
        raise SystemExit("No user state files loaded; run initial_assessment first.")

    md = render_team_markdown(states, users=loaded_users)
    out = latest_team_path(contract)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out} ({len(loaded_users)} users)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
