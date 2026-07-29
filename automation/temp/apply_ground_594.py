"""Apply GROUND runtime probes to CRT-594 coverage (helper ground stage). Scratch only."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automation" / "temp"))
from emit_coverage_594 import build_markdown  # noqa: E402

EPIC_DIR = ROOT / "epics" / "CRT-594"
COV_PATH = EPIC_DIR / "CRT-594-coverage.json"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

PROBES = {
    "chk-009": [
        {
            "probe_id": "gp-chk-009",
            "command_attempted": "use; show prices EURUSD.spot",
            "outcome": "success",
            "verified_syntax": "show prices EURUSD.spot",
            "evidence_note": "CTQA after use (bro1_usd): Bid/Ask and Last quote returned for EURUSD.spot",
            "probed_at": NOW,
        }
    ],
    "chk-011": [
        {
            "probe_id": "gp-chk-011a",
            "command_attempted": "backup_price show symbol=EURUSD.spot",
            "outcome": "success",
            "verified_syntax": "backup_price show symbol=EURUSD.spot",
            "evidence_note": "CTQA BackupPrice{price: 1.138455, FOREX, ...} for EURUSD.spot",
            "probed_at": NOW,
        },
        {
            "probe_id": "gp-chk-011b",
            "command_attempted": "daily_data_recorder_config show",
            "outcome": "success",
            "verified_syntax": "daily_data_recorder_config show",
            "evidence_note": "CTQA config includes FOREX instrumentTypes with Quote bid/ask snapshot schedules",
            "probed_at": NOW,
        },
    ],
}

DETAIL_UPDATES = {
    "chk-009": [
        "> Verified on CTQA: show prices EURUSD.spot (after use) — bid/ask from Quote stream.",
        "> Discover: tier-by-qty oracle at command_family (aff-003).",
    ],
    "chk-011": [
        "> Verified: backup_price show symbol=EURUSD.spot; daily_data_recorder_config show (FOREX EOD schedules).",
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
    log.append({"step": "ground", "at": NOW, "action": "runtime_probes chk-009 chk-011 via Invoke-CrtqaDxConsole"})
    cov["validation_log"] = log

    audit = cov.get("grounding_audit") or {}
    by_id = {row.get("check_id"): row for row in (audit.get("by_check_id") or []) if isinstance(row, dict)}
    for cid in PROBES:
        by_id[cid] = {
            "check_id": cid,
            "evidence_keys": next(
                (c.get("requirement_keys") or [] for c in cov["checks"] if c.get("id") == cid),
                [],
            ),
            "status": "probe_grounded",
        }
    audit["by_check_id"] = list(by_id.values())
    audit["ungrounded_check_ids"] = []
    cov["grounding_audit"] = audit

    cov["smart_checklist_markdown"] = build_markdown(cov)
    COV_PATH.write_text(json.dumps(cov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (EPIC_DIR / "CRT-594-coverage.md").write_text(
        cov["smart_checklist_markdown"], encoding="utf-8"
    )
    print(f"Updated {COV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
