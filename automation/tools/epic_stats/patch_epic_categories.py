#!/usr/bin/env python3
"""Patch manual category corrections after heuristic seed."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from epic_stats.apply_categories import load_epic_categories, save_epic_categories  # noqa: E402

PATCHES: dict[str, tuple[str, str, list[str]]] = {
    "CRT-403": (
        "fe",
        "Watchlist edit actions in client UI.",
        ["summary:Watchlist Edit Actions"],
    ),
    "CRT-427": (
        "fe",
        "Transactions account selector in client/dealer UI.",
        ["summary:Account Selector"],
    ),
    "CRT-41": (
        "be",
        "Withdrawal balance metric and liquidation-domain limit calculation (CRT-069, CRT-091).",
        ["CRT-069", "CRT-091"],
    ),
    "CRT-49": (
        "be",
        "Instrument master field for IG instrument ID.",
        ["summary:IG instrument ID"],
    ),
    "CRT-521": (
        "be",
        "Default time-in-force rules per order type (trading configuration).",
        ["summary:Default TIF"],
    ),
    "CRT-588": (
        "be",
        "2FA exclusion configuration for autotest environments.",
        ["summary:2FA exclusion"],
    ),
    "CRT-237": (
        "api",
        "IG DMA routing change using ExpireTime for CFD_STOCK (broker integration).",
        ["summary:IG DMA"],
    ),
    "CRT-286": (
        "be",
        "CPS commission rules per underlying for FUTURE/OPTION.",
        ["summary:CPS commission"],
    ),
    "CRT-347": (
        "api",
        "FIX tag 55 encoding update for US Options (external protocol).",
        ["summary:FIX tag 55"],
    ),
    "CRT-264": (
        "api",
        "dxFeed LAST_TRADE_TIME in IPF and platform trading-end logic (external market data).",
        ["CRT-871", "MDD-8089"],
    ),
    "CRT-46": (
        "api",
        "FIX trading integration with IG OTC (CRT-096).",
        ["CRT-096"],
    ),
    "CRT-386": (
        "api",
        "Caronte venue integration: STOCK/ETF order routing and FIX encoding (CRT-1193–1199).",
        ["CRT-1193", "CRT-1194"],
    ),
    "CRT-440": (
        "api",
        "REST API for pre-trade order validation and commission calculation.",
        ["summary:REST API"],
    ),
    "CRT-617": (
        "api",
        "FX_SPOT trading and FIX integration with ET venue.",
        ["summary:FIX Integration with ET"],
    ),
    "CRT-672": (
        "api",
        "Extend Apply CA Transactions API with tax, commission, and fee fields (CRT-1918–1920).",
        ["CRT-1918", "CRT-1250"],
    ),
}


def main() -> int:
    data = load_epic_categories()
    reviews = data.setdefault("reviews", {})
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for ek, (cid, rationale, evidence) in PATCHES.items():
        reviews[ek] = {
            "category_id": cid,
            "rationale": rationale,
            "evidence": evidence,
            "reviewed_utc": utc,
        }
    path = save_epic_categories(data)
    print(f"patched {len(PATCHES)} entries -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
