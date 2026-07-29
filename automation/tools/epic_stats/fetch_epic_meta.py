#!/usr/bin/env python3
"""Backfill epic_meta on existing CRTQA stats v5 state files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from epic_stats.ingest import load_state, save_state  # noqa: E402
from epic_stats.jira_rest import fetch_epic_meta_map  # noqa: E402


def epic_keys_from_state(state: dict) -> list[str]:
    keys: set[str] = set(state.get("corpus_epic_keys") or [])
    for row in state.get("rows") or []:
        ek = row.get("epic_link")
        if ek:
            keys.add(str(ek).upper())
    att = state.get("attestation_by_epic") or {}
    for ek, v in att.items():
        if v.get("ai_assisted"):
            keys.add(str(ek).upper())
    return sorted(keys)


def backfill(jira_user: str, *, force: bool = False) -> dict:
    state = load_state(jira_user)
    existing = state.get("epic_meta") or {}
    needed = epic_keys_from_state(state)
    to_fetch = needed if force else [k for k in needed if k not in existing]
    if to_fetch:
        fetched = fetch_epic_meta_map(to_fetch)
        merged = dict(existing)
        merged.update(fetched)
        state["epic_meta"] = merged
        save_state(state)
    return {
        "jira_user": jira_user,
        "epic_keys_total": len(needed),
        "fetched": len(to_fetch),
        "epic_meta_count": len(state.get("epic_meta") or {}),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Backfill epic_meta on last-sync-<user>.json")
    p.add_argument("--jira-user", required=True)
    p.add_argument("--force", action="store_true", help="Re-fetch all epic keys")
    args = p.parse_args()
    report = backfill(args.jira_user, force=args.force)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
