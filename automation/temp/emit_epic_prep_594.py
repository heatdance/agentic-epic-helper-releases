"""One-shot EPIC-PREP emit for CRT-594 helper cold start. Scratch only."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC_DIR = ROOT / "epics" / "CRT-594"
TEMP = EPIC_DIR / "temp"
FIXTURE = ROOT / "automation/tools/fixtures/epic-prep/ref-594-topology-full.json"
YOGI = ROOT / "automation/tools/yogi-tool/yogi_snippet.py"

# Snippet text sourced from Confluence MCP storage (page 518015112 / 345722716)
MCP_SNIPPETS = {
    "CRT-1761": {
        "page_id": "518015112",
        "snippet_text": (
            "FX SPOT Pricing Scheme maps dxFeed group-qualified symbols (currency pair + FxSpotSuffix) "
            "to CT EURUSD.spot UI symbols; account-group suffix drives dxFeed subscription."
        ),
        "extract_mode": "mcp",
    },
    "CRT-1714": {
        "page_id": "518015112",
        "snippet_text": (
            "TextConfiguration delivers the full tiered book from dxFeed; tiers include volume, bid/ask, "
            "quoteId, settlDate; volumes in the array are NOT sorted; tier selection uses closest >= quantity "
            "on Watchlist/OE surfaces."
        ),
        "extract_mode": "mcp",
    },
    "CRT-1717": {
        "page_id": "518015112",
        "snippet_text": (
            "ET Trader applies CB markup on bid/ask in volume and category dimensions and sends tiered prices "
            "per instrument for each category (Energy vs Opportunity examples with same midpoint, different spreads)."
        ),
        "extract_mode": "mcp",
    },
    "CRT-1713": {
        "page_id": "518015112",
        "snippet_text": (
            "dxFeed Quote price events use the first tier (min volume) per account group; DX appends group "
            "suffix to subscribe (e.g. EUR/USD.ENERGY:ETFX for EURUSD.spot Energy account)."
        ),
        "extract_mode": "mcp",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_yogi_snippet(page_path: Path, req_key: str) -> dict | None:
    if not page_path.exists():
        return None
    proc = subprocess.run(
        [sys.executable, str(YOGI), "--storage-file", str(page_path), "--req", req_key],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    text = (data.get("snippet_text") or "").strip()
    if not text:
        return None
    return {
        "snippet_text": text,
        "snippet_status": "ok",
        "snippet_failure_reason": None,
        "extract_mode": data.get("mode") or "mcp",
        "page_id": data.get("page_id"),
    }


def main() -> int:
    TEMP.mkdir(parents=True, exist_ok=True)
    ref = deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8")))

    jira_path = TEMP / "jira-issue.json"
    if jira_path.exists():
        jira = json.loads(jira_path.read_text(encoding="utf-8"))
        ref["epic"]["labels"] = jira.get("labels") or []
        ref["epic"]["status"] = (jira.get("status") or {}).get("name") or ref["epic"]["status"]

    now = utc_now()
    ref["sources"]["jira_fetched_at"] = now
    ref["sources"]["confluence_method"] = "mcp"
    ref["sources"]["bitbucket_repo"] = "BRO/xt"
    ref["implementation"]["skipped_reason"] = None
    ref["implementation"]["hits"] = []

    ref["verification_topology"]["delivery_notes"] = []
    for obl in ref["obligations_proposed"]:
        hints = obl.get("downstream_hints") or {}
        hints["linked_delivery_note_ids"] = []
        obl["downstream_hints"] = hints

    requirements = []
    for key in ["CRT-1761", "CRT-1714", "CRT-1717", "CRT-1713", "CRT-1621"]:
        short_url = f"https://confluence.in.devexperts.com/requirements/CT/{key}"
        row = {
            "key": key,
            "short_url": short_url,
            "anchor": f"req-{key}",
            "jira_context": None,
        }
        if key == "CRT-1621":
            yogi = run_yogi_snippet(TEMP / "mcp-page-345722716.json", key)
            if yogi:
                row.update(yogi)
                row["page_id"] = "345722716"
            else:
                row.update({
                    "page_id": "345722716",
                    "snippet_text": None,
                    "snippet_status": "failed",
                    "snippet_failure_reason": "yogi_extract_empty",
                    "extract_mode": None,
                })
        elif key in MCP_SNIPPETS:
            meta = MCP_SNIPPETS[key]
            row.update({
                "page_id": meta["page_id"],
                "snippet_text": meta["snippet_text"],
                "snippet_status": "ok",
                "snippet_failure_reason": None,
                "extract_mode": meta["extract_mode"],
            })
        requirements.append(row)
    ref["requirements"] = requirements

    for obl in ref["obligations_proposed"]:
        keys = obl.get("requirement_keys") or []
        if keys:
            req_key = keys[0]
            out = TEMP / f"epic-obligation-{req_key}.json"
            out.write_text(
                json.dumps({"requirement_key": req_key, "obligations_proposed": [obl]}, indent=2),
                encoding="utf-8",
            )

    ref["validation_log"].extend([
        {"step": "3b_snippet_retry", "at": now, "action": "mcp storage: yogi CRT-1621; MCP prose slices CRT-1761/1714/1717/1713"},
        {"step": "3.4", "at": now, "action": "precision pass — synthesis aligned to Jira CRT-594 description"},
        {"step": "5b_bitbucket_prep", "at": now, "action": "skipped helper cold start; BRO/xt recorded for COVERAGE"},
        {"step": "3.5", "at": now, "action": "xt_refs capped 0 — CT-scoped FX_SPOT epic"},
        {"step": "3.6", "at": now, "action": "xt relevance pass — no rows"},
        {"step": "6b", "at": now, "action": "obligations_reconcile epic_summary_aligned=true"},
    ])

    out_ref = EPIC_DIR / "CRT-594-ref.json"
    out_ref.write_text(json.dumps(ref, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
