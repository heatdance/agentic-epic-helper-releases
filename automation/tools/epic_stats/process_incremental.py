#!/usr/bin/env python3
"""Apply scoped incremental TCD candidates to v5 state as comparison rows."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from epic_stats.apply_categories import apply_epic_categories_to_state  # noqa: E402
from epic_stats.ingest import load_contract, load_state, save_state  # noqa: E402


def apply_incremental(
    jira_user: str,
    candidates_path: Path,
    *,
    include_keys: set[str] | None = None,
    issues_dir: Path | None = None,
) -> dict:
    contract = load_contract()
    state = load_state(jira_user, contract)
    data = json.loads(candidates_path.read_text(encoding="utf-8"))
    pool = data.get("candidates") or []
    chosen = []
    for c in pool:
        key = str(c.get("key") or "").upper()
        if not key:
            continue
        if include_keys is not None and key not in include_keys:
            continue
        chosen.append(c)

    added: list[str] = []
    for c in chosen:
        key = str(c["key"]).upper()
        epic = str(c.get("epic") or "").upper()
        row = {
            "issue": key,
            "epic_link": epic,
            "lane": "tcd",
            "role": "comparison",
            "category_id": c.get("category_id") or "other",
            "size_id": c.get("size_id"),
            "draft_estimate_hours": float(c.get("estimate_hours") or 8),
            "estimate_source": c.get("estimate_source") or "jira_field",
            "hours_logged": float(c.get("logged_hours") or 0),
            "others_logged_hours": float(c.get("others_logged_hours") or 0),
            "summary": c.get("summary") or "",
            "anomalies": c.get("anomalies") or [],
        }
        if issues_dir:
            issue_file = issues_dir / f"{key}.json"
            if issue_file.is_file():
                issue = json.loads(issue_file.read_text(encoding="utf-8"))
                from epic_stats.ingest import enrich_row_from_issue

                row = enrich_row_from_issue(
                    issue,
                    jira_user=jira_user,
                    epic_link=epic,
                    role="comparison",
                    contract=contract,
                )
        state.setdefault("rows", []).append(row)
        included = set(str(k).upper() for k in (state.get("included_issue_keys") or []))
        included.add(key)
        state["included_issue_keys"] = sorted(included)
        added.append(key)

    apply_epic_categories_to_state(state, contract)
    meta = state.setdefault("report_meta", {})
    meta["last_mode"] = "incremental_update"
    meta["last_sync_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta["incremental_added_keys"] = added
    save_state(state, contract)
    return {"jira_user": jira_user, "added": added, "added_count": len(added)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--jira-user", required=True)
    p.add_argument("--candidates", type=Path, required=True)
    p.add_argument(
        "--include-keys",
        nargs="*",
        default=None,
        help="Subset of candidate keys; omit with --all to take every candidate",
    )
    p.add_argument("--all", action="store_true", help="Include all candidates from file")
    p.add_argument("--issues-dir", type=Path, default=None)
    args = p.parse_args()
    if args.all:
        keys = None
    elif args.include_keys:
        keys = {k.upper() for k in args.include_keys}
    else:
        raise SystemExit("Specify --all or --include-keys KEY ...")
    issues_dir = args.issues_dir
    if issues_dir is None:
        default = args.candidates.parent / "issues"
        if default.is_dir():
            issues_dir = default
    report = apply_incremental(
        args.jira_user,
        args.candidates,
        include_keys=keys,
        issues_dir=issues_dir,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
