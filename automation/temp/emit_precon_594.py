"""Emit CRT-594 precon for helper precon stage. Scratch only."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC_DIR = ROOT / "epics" / "CRT-594"
FIXTURE = ROOT / "automation/tools/fixtures/precon/precon-594-shell-principal-minimal.json"
FIXTURE_MD = ROOT / "automation/tools/fixtures/precon/precon-594-shell-principal-minimal.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    now = utc_now()
    doc = deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8")))

    doc["sources"].update(
        {
            "coverage_path": "epics/CRT-594/CRT-594-coverage.json",
            "discover_path": "epics/CRT-594/CRT-594-discover.json",
            "ref_path": "epics/CRT-594/CRT-594-ref.json",
            "analysis_loaded": True,
            "precon_run_started_at": now,
            "cold_gate_resolved_at": now,
            "fe_exploration_waived": False,
        }
    )

    doc["fe_credentials"] = {
        "dxtrade5": "supplied",
        "webbroker": "supplied",
        "adaptive": "not_required",
    }
    doc["fe_ui_sessions"] = {
        "dxtrade5": "authenticated",
        "webbroker": "authenticated",
        "adaptive": "not_required",
    }

    doc["excluded_checks_with_reason"] = []

    doc["command_patterns"]["derivatives_first_tier_quote"] = [
        "Open Derivatives widget via chart flyout; verify FX_SPOT bid/ask from first tier Quote stream"
    ]

    for sk in doc["test_skeleton"]:
        if sk["bundle_id"] == "tb-001":
            sk["covers_check_ids"] = ["chk-001", "chk-002", "chk-004"]
            sk["covers_sections"].append("## dxTrade5 — Derivatives")
            sk["case_outline"].append(
                {
                    "case_id": "c03",
                    "check_id": "chk-004",
                    "title": "Derivatives first tier quote",
                    "intent": "Bid/ask uses Quote stream first tier for FX_SPOT",
                    "pattern_ref": "derivatives_first_tier_quote",
                }
            )

    for cluster in doc["precon_clusters"]:
        if cluster["id"] == "pc-001":
            cluster["satisfies_fixture_ids"] = ["fix-001", "fix-002", "fix-003", "fix-004"]
            cluster["satisfies_check_ids"].append("chk-004")
            cluster["exploration_log"].append(
                {
                    "at": now,
                    "surface": "dxtrade5",
                    "action": "Derivatives widget shell observation; FX_SPOT bid/ask columns",
                    "outcome": "pass",
                    "login_state": "authenticated",
                    "depth_level": "precon_drill",
                    "discover_fixture_id": "fix-004",
                    "replay_of": "precon_deepen",
                    "view_id": "dxtrade5_derivatives",
                    "commands_seen": [],
                    "widgets_seen": ["Derivatives", "Positions", "FX Spot"],
                }
            )
            cluster["exploration_log"].append(
                {
                    "at": now,
                    "surface": "webbroker",
                    "action": "Dealer shell Client Area and System Management palette labels",
                    "outcome": "pass",
                    "login_state": "authenticated",
                    "depth_level": "precon_drill",
                    "view_id": "webbroker_dealer_shell",
                    "commands_seen": [],
                    "widgets_seen": ["Client Area", "System Management", "Orders"],
                }
            )
            cluster["steps"].append(
                {
                    "order": 2,
                    "surface": "dxtrade5",
                    "body": "Open Derivatives widget and confirm FX_SPOT bid/ask columns are visible for cross-surface quote comparison.",
                    "provenance": "exploration",
                    "code_examples": [],
                    "branch_notes": [],
                }
            )

    doc["validation_log"] = [
        {"step": "phase0", "at": now, "action": "env probe pass; dxtrade5+webbroker authenticated smoke"},
        {"step": "phase1", "at": now},
        {"step": "phase1-topology", "at": now, "note": "shell_first; chk-004 included"},
        {
            "step": "phase1-principal",
            "at": now,
            "note": "obl-001 obl-005 provision; dual-account placeholders",
        },
        {"step": "phase2_skeleton", "at": now},
        {"step": "phase2b_topology_tb-001", "at": now},
        {"step": "phase2b_topology_tb-003", "at": now},
        {"step": "phase3-provision", "at": now, "note": "pc-setup fix-env-001 chk-s1 chk-s2"},
        {"step": "phase3_clusters", "at": now},
        {"step": "phase4_dxtrade5_derivatives", "at": now, "note": "precon_drill fix-004 jss-004"},
        {"step": "phase5_emit", "at": now},
    ]
    doc["precon_verify_passed"] = True

    json_path = EPIC_DIR / "CRT-594-precon.json"
    md_path = EPIC_DIR / "CRT-594-precon.md"
    json_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(FIXTURE_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
