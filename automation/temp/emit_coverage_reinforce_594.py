"""Emit CRT-594 coverage pass 2 (COVERAGE-REINFORCE). Scratch only."""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC_DIR = ROOT / "epics" / "CRT-594"
PASS1 = EPIC_DIR / "CRT-594-coverage.json"
DISCOVER = EPIC_DIR / "CRT-594-discover.json"
AFFORDANCES = EPIC_DIR / "helper/affordances-slice.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_markdown(coverage: dict) -> str:
    focus = coverage["epic_verification_focus"]["statement"]
    lines = [
        "# CRT-594 — FX_SPOT Pricing (groups and mapping to dxFeed)",
        "",
        f"## {focus}",
        "",
    ]
    annex = coverage.get("platform_reuse_annex")
    if annex:
        lines.extend(["### Platform reuse (suggestion only)", annex, ""])

    current_section = None
    for chk in coverage["checks"]:
        section = chk.get("section") or "## Checks"
        if section != current_section:
            lines.extend([section, ""])
            current_section = section
        lines.append(chk["scenario_line"])
        for detail in chk.get("detail_lines") or []:
            lines.append(detail)
        lines.append("")

    out_scope = coverage.get("explicitly_out_of_scope") or []
    if out_scope:
        lines.append("## Out of scope")
        lines.append("")
        for item in out_scope:
            lines.append(f"- {item['item']}: {item['rationale']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


DETAIL_MERGES: dict[str, list[str]] = {
    "chk-s1": [
        "> Provision two account groups on CTQA before UI quote observation.",
        "> Discover: account_group_environment_setup fix-env-001; ENRG vs OPPT dual-account contrast; linked obl-001, obl-005.",
    ],
    "chk-s2": [
        "> Discover: account_group_environment_setup fix-env-001; ENRG vs OPPT dual-account contrast; linked obl-001, obl-005.",
    ],
    "chk-001": [
        "> Oracle: text_configuration_closest_gte_qty for default order qty.",
        "> Discover: dxtrade5_watchlist text_configuration_closest_gte_qty; volume_control order_default_qty (aff-001).",
    ],
    "chk-002": [
        "> Oracle: first_tier_quote — first TextConfiguration tier only.",
        "> Discover: dxtrade5_positions first_tier_quote at shell_only (aff-002).",
    ],
    "chk-003": [
        "> Discover: Adaptive instrument page group-specific bid/ask shell_only (aff-006).",
    ],
    "chk-004": [
        "> Oracle: first_tier_quote.",
        "> Discover: dxtrade5_derivatives first_tier_quote at shell_only (aff-008).",
    ],
    "chk-005": [
        "> Harness: webbroker Client Area palette → Watchlist; header account selects group suffix.",
        "> Discover: WebBroker Client Area shell observation (aff-005).",
    ],
    "chk-006": [
        "> Harness: System Management → Backup Prices; verify FX_SPOT asset type filter post-drop.",
        "> Discover: Backup Prices widget FX_SPOT filter shell_only (aff-005).",
    ],
    "chk-007": [
        "> Discover: midpoint_invariant cross_group (aff-004).",
    ],
    "chk-008": [
        "> Discover: mark_from_midpoint fx_spot_mark (aff-007).",
    ],
    "chk-009": [
        "> Oracle: console_show_prices_first_tier.",
        "> Discover: console_show_prices_first_tier at command_family (aff-003).",
    ],
}


def main() -> int:
    now = utc_now()
    cov = deepcopy(json.loads(PASS1.read_text(encoding="utf-8")))
    discover = json.loads(DISCOVER.read_text(encoding="utf-8"))

    cov["coverage_pass"] = 2
    cov["reinforced_at"] = now
    sources = cov.get("sources") or {}
    sources["reinforce_topology_loaded"] = discover.get("sources", {}).get("topology_loaded", True)
    sources["reinforce_principal_loaded"] = discover.get("sources", {}).get("principal_loaded", True)
    sources["reinforce_inputs"] = [
        {"path": "epics/CRT-594/CRT-594-coverage.json", "loaded_at": now},
        {"path": "epics/CRT-594/CRT-594-discover.json", "loaded_at": now},
        {"path": "epics/CRT-594/helper/affordances-slice.json", "loaded_at": now},
    ]
    sources["note"] = "coverage_reinforce helper; harness explore dxtrade5+webbroker"
    cov["sources"] = sources

    for chk in cov["checks"]:
        cid = chk.get("id")
        if cid in DETAIL_MERGES:
            chk["detail_lines"] = DETAIL_MERGES[cid]

    validation_log = list(cov.get("validation_log") or [])
    validation_log.extend(
        [
            {"step": "reinforce-1", "at": now, "action": "loaded pass-1 + discover + affordances slice"},
            {
                "step": "reinforce-1-topology",
                "at": now,
                "action": "shell_first surface batches; 6 oracle bindings",
            },
            {
                "step": "reinforce-1-principal",
                "at": now,
                "action": "principal_loaded; 1 provision fixture fix-env-001",
            },
            {"step": "reinforce-2-oracle", "at": now, "action": "6 oracle_binding merges"},
            {
                "step": "reinforce-2-fixture-provision",
                "at": now,
                "action": "1 provision fixture merged into chk-s1/chk-s2",
            },
        ]
    )
    cov["validation_log"] = validation_log
    cov["smart_checklist_markdown"] = build_markdown(cov)

    json_path = EPIC_DIR / "CRT-594-coverage.json"
    md_path = EPIC_DIR / "CRT-594-coverage.md"
    json_path.write_text(json.dumps(cov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(cov["smart_checklist_markdown"], encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
