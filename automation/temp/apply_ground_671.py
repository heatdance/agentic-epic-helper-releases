"""Apply GROUND runtime probes to CRT-671 coverage (helper ground stage). Scratch only."""
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC = "CRT-671"
EPIC_DIR = ROOT / "epics" / EPIC
COV_PATH = EPIC_DIR / f"{EPIC}-coverage.json"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

PROBES = {
    "chk-e1": [
        {
            "probe_id": "gp-chk-e1a",
            "command_attempted": "show order",
            "outcome": "success",
            "verified_syntax": "show order last [n] [open]",
            "evidence_note": (
                "CTQA console prints usage: show order <id> | show order last [n] [open]; "
                "requires prior use <account>"
            ),
            "probed_at": NOW,
        },
        {
            "probe_id": "gp-chk-e1b",
            "command_attempted": "use bro1_usd; show order last 5 open",
            "outcome": "blocked",
            "verified_syntax": None,
            "evidence_note": (
                "use bro1_usd rejected (Couldn't parse account key); operator selects live "
                "CTQA account at test time before ACCEPTED UI observation"
            ),
            "probed_at": NOW,
        },
    ],
}

DETAIL_UPDATES = {
    "chk-e1": [
        "> Verified on CTQA: show order last [n] [open] after use <account> — inspect dxCore status for ACCEPTED before UI Sending check.",
        "> Harness: CTQA retail account with order-entry entitlement; issue order via dxTrade5 OE or API path per env profile.",
    ],
}


def main() -> int:
    cov = json.loads(COV_PATH.read_text(encoding="utf-8"))
    for chk in cov.get("checks") or []:
        cid = chk.get("id")
        if cid in PROBES:
            chk["runtime_probes"] = deepcopy(PROBES[cid])
        if cid in DETAIL_UPDATES:
            chk["detail_lines"] = DETAIL_UPDATES[cid]

    log = cov.get("validation_log") or []
    log.append(
        {
            "step": "ground",
            "at": NOW,
            "action": (
                "runtime_probes chk-e1 via Invoke-CrtqaDxConsole; "
                "show order syntax verified; account-specific use deferred to test time"
            ),
        }
    )
    cov["validation_log"] = log

    audit = cov.get("grounding_audit") or {}
    by_id = {
        row.get("check_id"): row
        for row in (audit.get("by_check_id") or [])
        if isinstance(row, dict)
    }
    by_id["chk-e1"] = {
        "check_id": "chk-e1",
        "evidence_keys": ["CRT-671", "CRT-1902"],
        "status": "probe_grounded",
    }
    audit["by_check_id"] = list(by_id.values())
    audit["ungrounded_check_ids"] = []
    cov["grounding_audit"] = audit

    COV_PATH.write_text(json.dumps(cov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sync = subprocess.run(
        [
            sys.executable,
            str(ROOT / "automation/tools/coverage_md_sync.py"),
            "--coverage",
            str(COV_PATH),
            "--write",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if sync.returncode != 0:
        print(sync.stderr, file=sys.stderr)
        return sync.returncode
    print(f"Updated {COV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
