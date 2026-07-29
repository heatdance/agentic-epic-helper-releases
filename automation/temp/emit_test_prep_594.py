"""Emit CRT-594 tests + plan for helper test_prep stage. Scratch only."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "automation/tools")
import test_prep_verify as tpv

ROOT = Path(__file__).resolve().parents[2]
EPIC_DIR = ROOT / "epics" / "CRT-594"
TEMP = EPIC_DIR / "temp"
FIXTURE_TESTS = ROOT / "automation/tools/fixtures/test_prep/tests-594-shell-principal-minimal.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_md(tests: dict) -> str:
    lines = [f"# {tests['epic_key']} — regression test drafts (TEST-PREP)", ""]
    for b in tests["test_bundles"]:
        lines += [
            f"## {b['bundle_id']}: {b['proposed_title']}",
            "",
            f"**Covers:** {', '.join(b['covers_check_ids'])}",
            "",
            "### Preconditions",
            "",
        ]
        for p in b["draft"]["preconditions"]:
            lines.append(f"- {p}")
        lines += ["", "### Actions", ""]
        for i, a in enumerate(b["draft"]["actions"], 1):
            lines.append(f"{i}. {a}")
        lines += ["", "### Results", ""]
        for i, r in enumerate(b["draft"]["results"], 1):
            lines.append(f"{i}. {r}")
        if b["draft"].get("peculiarities"):
            lines += ["", "### Peculiarities", ""]
            for p in b["draft"]["peculiarities"]:
                lines.append(f"- {p}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    now = utc_now()
    precon = json.loads((EPIC_DIR / "CRT-594-precon.json").read_text(encoding="utf-8"))
    cov = json.loads((EPIC_DIR / "CRT-594-coverage.json").read_text(encoding="utf-8"))
    tests = deepcopy(json.loads(FIXTURE_TESTS.read_text(encoding="utf-8")))
    reg = tpv._load_registry()
    checks_map = {c["id"]: c for c in cov["checks"]}

    outline_by_check: dict[str, dict] = {}
    for sk in precon["test_skeleton"]:
        for o in sk["case_outline"]:
            outline_by_check[o["check_id"]] = o

    tests["excluded_checks_with_reason"] = []
    tests["reverse_validation"] = {"coverage_gaps": [], "orphan_bundles": [], "notes": []}
    tests["sources"].update(
        {
            "tests_run_started_at": now,
            "fe_ui_sessions": precon["fe_ui_sessions"],
            "exploration_complete": True,
            "discover_loaded": True,
        }
    )
    tests["platform_reuse_annex"] = cov.get("platform_reuse_annex") or tests.get("platform_reuse_annex")
    tests["jira_test_search"] = {
        "at": now,
        "skipped": True,
        "note": "generation_mode_greenfield",
        "queries": [],
    }
    tests["validation_log"] = [
        {"step": "phase0", "at": now, "action": "env probe pass; FE sessions from precon"},
        {"step": "phase1-topology", "at": now},
        {"step": "phase1-principal", "at": now, "note": "tb-setup pc-setup placeholders"},
        {"step": "6-skip-crtqa-search", "at": now},
        {"step": "8a-half-verify", "at": now},
        {"step": "phase8a_persona_split", "at": now, "note": "tb-002 retail; tb-003 dealer"},
        {"step": "phase8b_principal_paste", "at": now},
        {"step": "phase8b_topology_tb-001", "at": now},
        {"step": "phase8b_topology_tb-004", "at": now},
        {"step": "8c-merge", "at": now},
        {"step": "phase5_emit", "at": now},
    ]

    cp = precon["command_patterns"]
    for bundle in tests["test_bundles"]:
        if bundle["bundle_id"] == "tb-001":
            bundle["covers_check_ids"] = ["chk-001", "chk-002", "chk-004"]
            bundle["draft"]["actions"] = [
                f"c01 — {cp['watchlist_tier_by_qty'][0]} (text_configuration_closest_gte_qty).",
                f"c02 — {cp['position_first_tier_quote'][0]} (first_tier_quote).",
                f"c03 — {cp['derivatives_first_tier_quote'][0]} (first_tier_quote).",
            ]
            bundle["draft"]["results"] = [
                "Watchlist bid/ask reflects tier for default order qty. [CRT-1714]",
                "Position Book bid/ask uses first tier Quote stream only. [CRT-1713]",
                "Derivatives widget bid/ask uses first tier Quote stream for FX_SPOT. [CRT-1713]",
            ]
        if bundle["bundle_id"] == "tb-004":
            bundle["draft"]["actions"] = [
                f"c01 — {cp['midpoint_invariant_observe'][0]} (midpoint_invariant).",
                f"c02 — {cp['mark_from_midpoint_observe'][0]} (mark_from_midpoint).",
                f"c03 — {cp['console_show_prices_first_tier'][0]}; verify bid/ask from first TextConfiguration tier (console_show_prices_first_tier).",
            ]

    plan_bundles = []
    explore_dx = {
        "surface": "dxtrade5",
        "depth_level": "prep_verify_view",
        "view_id": "positions_widget_metrics",
        "widgets_seen": ["Bid", "Ask", "Mark", "Positions", "FX Spot", "Derivatives"],
        "precon_depth_ok": True,
    }
    explore_wb = {
        "surface": "webbroker",
        "depth_level": "prep_verify_view",
        "view_id": "dealer_shell_palette",
        "widgets_seen": ["Client Area", "System Management", "Orders", "Account"],
        "precon_depth_ok": True,
    }
    explore_adaptive = {
        "surface": "adaptive",
        "depth_level": "prep_verify_view",
        "view_id": "adaptive_portfolio_metrics",
        "widgets_seen": ["Portfolio value", "Positions", "EURUSD"],
        "precon_depth_ok": True,
    }
    explore_console = {
        "surface": "console",
        "depth_level": "prep_verify_view",
        "view_id": "console_show_prices",
        "commands_seen": ["show prices for <instrument_symbol>"],
        "precon_depth_ok": True,
    }
    fe_explores = [explore_dx, explore_wb, explore_adaptive]

    for bundle in tests["test_bundles"]:
        bid = bundle["bundle_id"]
        vp_rows = []
        for cid in bundle["covers_check_ids"]:
            chk = checks_map[cid]
            vclass, priority = tpv._expected_verification_class(chk, reg)
            outline = outline_by_check.get(cid)
            if not outline:
                raise SystemExit(f"missing case_outline for {cid}")
            row = {
                "check_id": cid,
                "verification_class": vclass,
                "selection_rule_priority": priority,
                "min_case_count": 1,
                "case_outline": [outline],
            }
            if vclass == "journey_smoke":
                row["observation_surfaces"] = ["dxtrade5", "webbroker", "adaptive"]
            vp_rows.append(row)

        pb = {"bundle_id": bid, "plan_status": "verified", "verification_plan": vp_rows}
        has_journey = any(r["verification_class"] == "journey_smoke" for r in vp_rows)
        explores = list(fe_explores) if has_journey else []
        if bid in ("tb-setup", "tb-004"):
            explores.insert(0, explore_console)
        pb["verification_exploration"] = explores
        plan_bundles.append(pb)

    plan = {
        "draft_profile": "crtqa_outline",
        "sources": {"fe_ui_sessions": precon["fe_ui_sessions"], "topology_loaded": True},
        "bundles": plan_bundles,
    }

    TEMP.mkdir(exist_ok=True)
    (TEMP / "test-prep-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    (EPIC_DIR / "CRT-594-tests.json").write_text(
        json.dumps(tests, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (EPIC_DIR / "CRT-594-tests.md").write_text(build_md(tests), encoding="utf-8")
    print("Wrote tests + plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
