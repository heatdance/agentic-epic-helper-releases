#!/usr/bin/env python3
"""
Recompute and render stats/epic-stats/latest-<jira_user>.md (schema v5).

Examples:
  python automation/tools/epic_stats_rollup.py --jira-user mshpak
  python automation/tools/epic_stats_rollup.py --jira-user mshpak --append-longitudinal
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "automation" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from epic_stats.ingest import (  # noqa: E402
    load_contract,
    load_state,
    latest_path_for_user,
    save_state,
)
from epic_stats.apply_categories import apply_epic_categories_to_state  # noqa: E402
from epic_stats.render_report import render_latest_markdown  # noqa: E402


def _longitudinal_path(contract: dict) -> Path:
    rel = (contract.get("paths") or {}).get(
        "longitudinal", "stats/epic-stats/state/longitudinal.json"
    )
    return REPO_ROOT / rel


def _append_longitudinal(state: dict, contract: dict) -> None:
    path = _longitudinal_path(contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"schema_version": 1, "snapshots": []}
    snap = {
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "jira_user": state.get("jira_user"),
        "corpus_epics": len(state.get("corpus_epic_keys") or []),
        "corpus_rows": sum(1 for r in state.get("rows") or [] if r.get("role") == "corpus"),
        "comparison_rows": sum(
            1 for r in state.get("rows") or [] if r.get("role") == "comparison"
        ),
    }
    data.setdefault("snapshots", []).append(snap)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="CRTQA stats v5 rollup")
    parser.add_argument("--jira-user", required=True, help="Jira username (e.g. mshpak)")
    parser.add_argument(
        "--append-longitudinal",
        action="store_true",
        help="Append snapshot to gitignored longitudinal.json",
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        help="Override state file (default: last-sync-<user>.json)",
    )
    args = parser.parse_args()
    user = args.jira_user.strip()
    contract = load_contract()

    if args.state_path:
        state = json.loads(args.state_path.read_text(encoding="utf-8"))
    else:
        state = load_state(user, contract)

    apply_epic_categories_to_state(state, contract)
    md = render_latest_markdown(state)
    out = latest_path_for_user(user, contract)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")

    meta = state.setdefault("report_meta", {})
    meta["last_sync_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_state(state, contract)

    if args.append_longitudinal:
        _append_longitudinal(state, contract)

    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
