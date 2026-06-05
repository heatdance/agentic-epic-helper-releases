#!/usr/bin/env python3
"""Merge epic_meta from user state files into epic-categories.json reviews."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.classify_epic_from_text import suggest_category  # noqa: E402
from crtqa_stats.apply_categories import epic_categories_path, load_epic_categories, save_epic_categories  # noqa: E402

USERS = ("mshram", "mtavadze", "amukanova", "mshpak")
MANUAL_OVERRIDES: dict[str, tuple[str, str]] = {
    "CRT-525": (
        "be",
        "DAY order auto-expiration rules and allowedJobs (CRT-1211/1248); core trading engine logic.",
    ),
    "CRT-572": (
        "fe",
        "Port Chart Trading panel from upstream (HORN-1196 / DXBROBL-1227); client trading UI.",
    ),
    "CRT-593": (
        "be",
        "FX_SPOT instrument/account/portfolio metrics and margin formulas (CRT-856, CRT-004, CRT-574).",
    ),
    "CRT-601": (
        "fe",
        "Est. AF Effect on FX_SPOT order-entry form; UI fields with BE-sourced values (DXINV-028).",
    ),
    "CRT-609": (
        "fe",
        "FX_SPOT charts on midpoint in web and WebBroker client area (CRT-1737).",
    ),
    "CRT-594": (
        "fe",
        "FX_SPOT pricing groups and mapping UI/configuration for client pricing (AI-assisted epic).",
    ),
    "CRT-290": (
        "fe",
        "DXTF charting update using Candle.bid when instrument flagged (CRT-983); client chart UI.",
    ),
}


def merge_meta() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for user in USERS:
        path = REPO / "stats/crtqa-stats/state" / f"last-sync-{user}.json"
        if not path.is_file():
            continue
        state = json.loads(path.read_text(encoding="utf-8"))
        for ek, meta in (state.get("epic_meta") or {}).items():
            merged[ek.upper()] = meta
    return merged


def main() -> int:
    data = load_epic_categories()
    reviews = data.setdefault("reviews", {})
    merged = merge_meta()
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for ek, meta in sorted(merged.items()):
        if ek in reviews:
            continue
        summary = str(meta.get("summary") or "")
        desc = str(meta.get("description") or "")
        if ek in MANUAL_OVERRIDES:
            cid, rationale = MANUAL_OVERRIDES[ek]
        else:
            cid, rationale = suggest_category(summary, desc)
        reviews[ek] = {
            "category_id": cid,
            "rationale": rationale,
            "evidence": [f"epic_meta:{ek}"],
            "reviewed_utc": utc,
        }

    path = save_epic_categories(data)
    print(f"wrote {len(reviews)} reviews to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
