#!/usr/bin/env python3
"""Phase 1 staleness checklist for CRTQA stats incremental_update."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.ingest import (
    baseline_readiness_for_user,
    discover_team_users_with_state,
    load_contract,
    team_users_from_contract,
)


def readiness_report(
    users: list[str] | None = None,
    *,
    restrict_to_roster: bool = True,
) -> dict[str, Any]:
    contract = load_contract()
    roster = team_users_from_contract(contract)
    if users:
        target = sorted({u.strip() for u in users if u.strip()})
    elif restrict_to_roster:
        target = roster
    else:
        target = discover_team_users_with_state(contract, restrict_to_roster=False)

    rows = [baseline_readiness_for_user(u, contract) for u in target]
    missing_state = [r["jira_user"] for r in rows if not r["state_exists"]]
    missing_latest = [r["jira_user"] for r in rows if not r["latest_exists"]]
    return {
        "roster": roster,
        "users_checked": target,
        "rows": rows,
        "all_ready": all(r["ready"] for r in rows) if rows else False,
        "missing_state": missing_state,
        "missing_latest": missing_latest,
    }


def readiness_checklist_markdown(report: dict[str, Any]) -> str:
    lines = [
        "## CRTQA stats — baseline readiness (Phase 1)",
        "",
        "Confirm each colleague's corpus baseline is current before incremental AI update.",
        "",
        "| User | latest-* | Generated | state | last_sync_utc | Ready |",
        "|------|----------|-----------|-------|---------------|-------|",
    ]
    for r in report.get("rows") or []:
        latest = "yes" if r.get("latest_exists") else "**no**"
        state = "yes" if r.get("state_exists") else "**no**"
        ready = "yes" if r.get("ready") else "**no**"
        lines.append(
            f"| `{r['jira_user']}` | {latest} | {r.get('latest_generated') or '—'} | "
            f"{state} | {r.get('state_last_sync_utc') or '—'} | {ready} |"
        )
    lines.extend(["", f"**All ready:** `{report.get('all_ready')}`", ""])
    if report.get("missing_state"):
        lines.append(f"- Missing state: {', '.join(f'`{u}`' for u in report['missing_state'])}")
    if report.get("missing_latest"):
        lines.append(f"- Missing latest: {', '.join(f'`{u}`' for u in report['missing_latest'])}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--users", nargs="*", default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    report = readiness_report(args.users)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(readiness_checklist_markdown(report))
    return 0 if report.get("all_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
