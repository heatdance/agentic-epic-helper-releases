#!/usr/bin/env python3
"""Emit CRT-671-coverage.json + .md for COVERAGE v1 (draft_truth pass 1)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC = "CRT-671"
EPIC_DIR = ROOT / "epics" / EPIC
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

FOCUS = (
    "Verify that when dxCore order status is ACCEPTED, client shells show UI label "
    "'Sending' (not 'Working') on dxTrade5 web, WebBroker, and Adaptive, and that "
    "Adaptive lists Sending orders in Working orders on Portfolio and Account pages."
)

checks = [
    {
        "id": "chk-e1",
        "section": "## Order placement and ACCEPTED state reachability",
        "scenario_line": (
            "- [CRT-671] Issue a market or limit order on CTQA and observe dxCore status "
            "ACCEPTED before external execution confirmation."
        ),
        "requirement_keys": ["CRT-671", "CRT-1902"],
        "obligation_ids": ["obl-003"],
        "coverage_thread": "environment_setup",
        "verification_role": "primary",
        "detail_lines": [
            "> Prerequisite (console): Confirm order reaches ACCEPTED (external child pending) via order status query before UI check.",
            "> Harness: CTQA retail account with order-entry entitlement; issue order via dxTrade5 OE or API path per env profile.",
        ],
        "linker_trace_lines": [
            "> Discover: order_accepted_window env-001; dxCore ACCEPTED before external confirm; linked obl-003."
        ],
    },
    {
        "id": "chk-e2",
        "section": "## Order placement and ACCEPTED state reachability",
        "scenario_line": (
            "- [CRT-1902] ACCEPTED means validation-to-execution passed and brokerage backend accepted; "
            "external party confirmation not yet received — UI must show Sending during this window."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-003"],
        "coverage_thread": "environment_setup",
        "verification_role": "primary",
        "detail_lines": [
            "> Note: Timing-sensitive — capture UI while dxCore remains ACCEPTED and before WORKING transition.",
        ],
    },
    {
        "id": "chk-t1",
        "section": "## Cross-shell Sending label when dxCore is ACCEPTED",
        "scenario_line": (
            "- [CRT-1902] [CRT-1726] When dxCore order status is ACCEPTED, all in-scope client shells "
            "map the GUI label to Sending per updated order statuses table."
        ),
        "requirement_keys": ["CRT-1902", "CRT-1726"],
        "obligation_ids": ["obl-001"],
        "coverage_thread": "mapping_routing",
        "verification_role": "primary",
        "detail_lines": [
            "> Contrast: legacy XT manuals mapped ACCEPTED to Working; Corner delta requires Sending label.",
        ],
    },
    {
        "id": "chk-t2",
        "section": "## Adaptive Working orders list membership for Sending",
        "scenario_line": (
            "- [CRT-671] Adaptive orders with UI status Sending appear in Working orders on Portfolio "
            "tab and Account page (not only in a terminal/history view)."
        ),
        "requirement_keys": ["CRT-671"],
        "obligation_ids": ["obl-002"],
        "coverage_thread": "surface_quotes",
        "verification_role": "primary",
        "detail_lines": [
            "> Harness: Adaptive Portfolio tab → Working orders; repeat on Account page.",
            "> Note: Harness maps do not yet sample Sending label — live CTQA probe required.",
        ],
    },
    {
        "id": "chk-001",
        "section": "## dxTrade5 — Orders",
        "topology_surface_id": "jss-001",
        "scenario_line": (
            "- [CRT-1902] [FAILED] dxTrade5 Orders widget Status column shows Sending (not Working) "
            "when dxCore order status is ACCEPTED."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "delivery_status": "known_fail",
        "verification_role": "primary",
        "detail_lines": [
            "> Harness: Chart title-bar icon switcher → Orders widget; Status column beside Instrument/Side.",
            "> Verified on CTQA: Orders grid exposes Status column; in-flight Sending label not in harness samples — probe with ACCEPTED order.",
        ],
        "linker_trace_lines": [
            "> Discover: delivery_note dn-001 known_fail XT-8496 Working instead of Sending."
        ],
    },
    {
        "id": "chk-002",
        "section": "## WebBroker (dealer) — Order Book",
        "topology_surface_id": "jss-002",
        "scenario_line": (
            "- [CRT-1902] [FAILED] WebBroker Order Book displays order with Status Sending when "
            "dxCore is ACCEPTED and order is visible in the book."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "delivery_status": "known_fail",
        "verification_role": "primary",
        "detail_lines": [
            "> Harness: Workspace 1 → Order Book tile; Status column with Filter by Status.",
            "> Note: Epic validation XT-8494 — Sending orders not displayed in Order Book.",
        ],
        "linker_trace_lines": [
            "> Discover: delivery_note dn-002 known_fail XT-8494 Sending orders not displayed."
        ],
    },
    {
        "id": "chk-011",
        "section": "## Adaptive — Orders status display",
        "topology_surface_id": "jss-003",
        "scenario_line": (
            "- [CRT-1902] Adaptive order status label shows Sending when dxCore order status is ACCEPTED."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "verification_role": "primary",
        "detail_lines": [
            "> Harness: Adaptive order detail / status field during ACCEPTED window.",
        ],
    },
    {
        "id": "chk-004",
        "section": "## Adaptive — Working orders (Portfolio tab)",
        "topology_surface_id": "jss-004",
        "scenario_line": (
            "- [CRT-671] Sending order appears in Working orders list on Adaptive Portfolio tab."
        ),
        "requirement_keys": ["CRT-671"],
        "obligation_ids": ["obl-002"],
        "verification_role": "primary",
        "detail_lines": [
            "> Harness: Adaptive Portfolio → Working orders section.",
        ],
    },
    {
        "id": "chk-005",
        "section": "## Adaptive — Working orders (Account page)",
        "topology_surface_id": "jss-005",
        "scenario_line": (
            "- [CRT-671] Sending order appears in Working orders list on Adaptive Account page."
        ),
        "requirement_keys": ["CRT-671"],
        "obligation_ids": ["obl-002"],
        "verification_role": "primary",
        "detail_lines": [
            "> Harness: Adaptive Account page → Working orders section.",
        ],
    },
    {
        "id": "chk-006",
        "section": "## dxTrade5 — Order History",
        "scenario_line": (
            "- [CRT-1902] [FAILED] Order History status filter and row labels include Sending "
            "(not Working-only filter set)."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "delivery_status": "known_fail",
        "verification_role": "supporting",
        "detail_lines": [
            "> Harness: Orders widget lower pane Order History; status filter list.",
            "> Note: Epic validation XT-8615 incorrect status filter list.",
        ],
        "linker_trace_lines": [
            "> Discover: delivery_note dn-003 known_fail XT-8615 status filter list."
        ],
    },
    {
        "id": "chk-012",
        "section": "## dxTrade5 — Orders",
        "scenario_line": (
            "- [CRT-1902] [FAILED] Modify and Cancel actions remain available for orders in Sending status."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "delivery_status": "known_fail",
        "verification_role": "supporting",
        "detail_lines": [
            "> Note: Epic validation XT-8616 actions unavailable for Sending orders.",
        ],
        "linker_trace_lines": [
            "> Discover: delivery_note dn-004 known_fail XT-8616 modify/cancel unavailable."
        ],
    },
    {
        "id": "chk-013",
        "section": "## Adaptive — Order History",
        "scenario_line": (
            "- [CRT-1902] [FAILED] Adaptive Order History shows Sending label consistently for ACCEPTED-phase orders."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "delivery_status": "known_fail",
        "verification_role": "supporting",
        "detail_lines": [
            "> Note: Epic validation CAN-14623 incorrect Sending display in Order History.",
        ],
        "linker_trace_lines": [
            "> Discover: delivery_note dn-005 known_fail CAN-14623 Adaptive order history."
        ],
    },
    {
        "id": "chk-014",
        "section": "## WebBroker (dealer) — Order Book",
        "scenario_line": (
            "- [CRT-1902] [FAILED] Order Book does not show duplicated OrderStatus and CtOrderStatus columns for Corner."
        ),
        "requirement_keys": ["CRT-1902"],
        "obligation_ids": ["obl-001"],
        "delivery_status": "known_fail",
        "verification_role": "supporting",
        "detail_lines": [
            "> Note: Epic validation XT-8216 duplicated status columns.",
        ],
        "linker_trace_lines": [
            "> Discover: delivery_note dn-006 known_fail XT-8216 duplicated columns."
        ],
    },
    {
        "id": "chk-010",
        "section": "## Cross-shell order status mapping",
        "scenario_line": (
            "- [CRT-1726] Platform order-status mapping regression: ACCEPTED → Sending label family "
            "consistent with CT order statuses table (not upstream Working-only label)."
        ),
        "requirement_keys": ["CRT-1726"],
        "obligation_ids": ["obl-001"],
        "verification_role": "primary",
        "detail_lines": [
            "> Note: XT upstream manuals reference Sending for NEW and Working for ACCEPTED; Corner table maps ACCEPTED→Sending.",
        ],
    },
]

scenario_coverage_map = [
    {"scenario_row_id": "scr-001", "check_id": "chk-001", "disposition": "covered"},
    {"scenario_row_id": "scr-002", "check_id": "chk-002", "disposition": "covered"},
    {"scenario_row_id": "scr-003", "check_id": "chk-011", "disposition": "covered"},
    {"scenario_row_id": "scr-004", "check_id": "chk-004", "disposition": "covered"},
    {"scenario_row_id": "scr-005", "check_id": "chk-005", "disposition": "covered"},
    {"scenario_row_id": "scr-006", "check_id": "chk-010", "disposition": "covered"},
]

coverage = {
    "schema_version": 2,
    "epic_key": EPIC,
    "epic_ref_path": f"epics/{EPIC}/{EPIC}-ref.json",
    "draft_truth_round": 1,
    "coverage_pass": 1,
    "sources": {
        "jira_fetched_at": NOW,
        "epic_ref_loaded_at": NOW,
        "bitbucket_repo": "BRO/xt",
        "note": "repo from epic_ref BRO/xt",
    },
    "archetype": "widget_ui",
    "emit_layout": "shell_first",
    "topology_provenance": {
        "ref_path": f"epics/{EPIC}/{EPIC}-ref.json",
        "fields_consumed": [
            "epic_archetype.value",
            "verification_topology.jira_scenario_surfaces",
            "verification_topology.shell_roles",
            "verification_topology.delivery_notes",
            "verification_topology.principal_coverage_threads",
            "verification_topology.platform_reuse_candidates",
            "verification_focus_proposed",
            "obligations_proposed",
            "implementation.hits",
        ],
        "archetype_source": "copied_from_ref",
        "copied_at": NOW,
    },
    "principal_provenance": {
        "focus_source": "epic_ref_proposed",
        "copied_at": NOW,
        "threads_consumed": [
            {
                "thread_id": "pct-001",
                "section_heading": "## Order placement and ACCEPTED state reachability",
                "obligation_ids": ["obl-003"],
            },
            {
                "thread_id": "pct-002",
                "section_heading": "## Cross-shell Sending label when dxCore is ACCEPTED",
                "obligation_ids": ["obl-001"],
            },
            {
                "thread_id": "pct-003",
                "section_heading": "## Adaptive Working orders list membership for Sending",
                "obligation_ids": ["obl-002"],
            },
        ],
    },
    "platform_reuse_annex": (
        "- Order status label mapping regression — platform regression TC family for "
        "dxCore-to-UI order status mapping (verify in Jira)."
    ),
    "epic_verification_focus": {
        "statement": FOCUS,
        "source": "epic_ref_proposed",
        "keywords": ["ACCEPTED", "Sending", "Working orders", "order status"],
    },
    "coverage_matrix": [
        {
            "id": "m-001",
            "capability": "ACCEPTED→Sending UI label on client shells",
            "semantic_variants": [],
            "verification_role": "primary",
            "aggregation_level": None,
            "surfaces": ["dxtrade5", "webbroker_dealer", "adaptive"],
            "requirement_keys": ["CRT-1902", "CRT-1726"],
            "obligation_ids": ["obl-001"],
        },
        {
            "id": "m-002",
            "capability": "Adaptive Working orders list includes Sending",
            "semantic_variants": [],
            "verification_role": "primary",
            "aggregation_level": None,
            "surfaces": ["adaptive"],
            "requirement_keys": ["CRT-671"],
            "obligation_ids": ["obl-002"],
        },
        {
            "id": "m-003",
            "capability": "Order placement to ACCEPTED state",
            "semantic_variants": [],
            "verification_role": "primary",
            "aggregation_level": None,
            "surfaces": ["console", "dxtrade5"],
            "requirement_keys": ["CRT-1902", "CRT-671"],
            "obligation_ids": ["obl-003"],
        },
        {
            "id": "m-004",
            "capability": "Order History and actions for Sending status",
            "semantic_variants": [],
            "verification_role": "supporting",
            "aggregation_level": None,
            "surfaces": ["dxtrade5", "adaptive", "webbroker_dealer"],
            "requirement_keys": ["CRT-1902"],
            "obligation_ids": ["obl-001"],
            "notes_from_epic": "Epic validation comment defects XT-8615, XT-8616, CAN-14623, XT-8216",
        },
        {
            "id": "m-005",
            "capability": "Platform order status mapping invariant",
            "semantic_variants": [],
            "verification_role": "primary",
            "aggregation_level": None,
            "surfaces": ["dxtrade5", "webbroker_dealer", "adaptive"],
            "requirement_keys": ["CRT-1726"],
            "obligation_ids": ["obl-001"],
        },
        {
            "id": "m-006",
            "capability": "dxTrade5 Orders widget Sending display",
            "semantic_variants": [],
            "verification_role": "primary",
            "aggregation_level": None,
            "surfaces": ["dxtrade5"],
            "requirement_keys": ["CRT-1902"],
            "obligation_ids": ["obl-001"],
        },
    ],
    "obligations_coverage": {
        "obl-001": {"status": "covered", "check_id": "chk-t1"},
        "obl-002": {"status": "covered", "check_id": "chk-t2"},
        "obl-003": {"status": "covered", "check_id": "chk-e1"},
    },
    "checks": checks,
    "scenario_coverage_map": scenario_coverage_map,
    "scenario_groups": [
        {
            "group_id": "sg-001",
            "title": "Reach ACCEPTED and observe Sending window",
            "check_ids": ["chk-e1", "chk-e2"],
            "combinatorics": "single_flow",
            "source": "principal_thread",
            "source_ref": "pct-001",
        },
        {
            "group_id": "sg-002",
            "title": "Cross-shell Sending label",
            "check_ids": ["chk-t1", "chk-001", "chk-002", "chk-011", "chk-010"],
            "combinatorics": "variant_sequence",
            "source": "section",
            "source_ref": "## Cross-shell Sending label when dxCore is ACCEPTED",
        },
        {
            "group_id": "sg-003",
            "title": "Adaptive Working orders lists",
            "check_ids": ["chk-t2", "chk-004", "chk-005"],
            "combinatorics": "variant_sequence",
            "source": "principal_thread",
            "source_ref": "pct-003",
        },
        {
            "group_id": "sg-004",
            "title": "Known validation defects (retest)",
            "check_ids": ["chk-006", "chk-012", "chk-013", "chk-014"],
            "combinatorics": "variant_sequence",
            "source": "section",
            "source_ref": "epic validation comment",
        },
    ],
    "implementation_hits": [
        {
            "id": "impl-001",
            "search_query": "epic_prep browse dxtf",
            "path": "dxtf/",
            "fragment": "dxtf module in BRO/xt",
            "note": "dxTrade5 Orders widget status mapping likely under dxtf.",
            "source_phase": "epic_prep",
        },
        {
            "id": "impl-002",
            "search_query": "epic_prep browse webbroker",
            "path": "webbroker/",
            "fragment": "webbroker module in BRO/xt",
            "note": "WebBroker Order Book status columns.",
            "source_phase": "epic_prep",
        },
    ],
    "nested_requirement_refs": [],
    "xt_confluence_hits": [
        {
            "page_id": "416527036",
            "url": "https://confluence.in.devexperts.com/pages/viewpage.action?pageId=416527036",
            "title": "XT BRO Internal/External orders details",
            "why_relevant": "ACCEPTED triggers external order — context for Sending window.",
            "summary": "Internal ACCEPTED creates external order awaiting confirmation.",
        }
    ],
    "explicitly_out_of_scope": [],
    "anti_pattern_findings": [],
    "grounding_audit": {"ungrounded_check_ids": []},
    "validation_log": [
        {"step": "1", "at": NOW, "action": "loaded ref; bitbucket_repo BRO/xt from epic_ref"},
        {"step": "1.5", "at": NOW, "action": "obligations 3 primary 0 deferral"},
        {"step": "3", "at": NOW, "action": "archetype widget_ui emit_layout shell_first copied_from_ref"},
        {"step": "3a", "at": NOW, "action": "epic_verification_focus copied verbatim from ref"},
        {"step": "4", "at": NOW, "action": "coverage_matrix 6 rows from scenario_capability_rows"},
        {"step": "8", "at": NOW, "action": "shell_first spine primary focus + principal + surfaces"},
        {"step": "8.5", "at": NOW, "action": "principal threads materialized pct-001..003"},
        {"step": "8.6", "at": NOW, "action": "scenario_groups 4 draft groups"},
        {"step": "9", "at": NOW, "action": "checks 14 merged; delivery known_fail markers on 6 defects"},
        {"step": "7", "at": NOW, "action": "implementation_hits 2 from epic_prep merge"},
    ],
    "smart_checklist_markdown": "",
}

EPIC_DIR.mkdir(parents=True, exist_ok=True)
cov_path = EPIC_DIR / f"{EPIC}-coverage.json"
cov_path.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {cov_path}")

sync = subprocess.run(
    [
        sys.executable,
        str(ROOT / "automation/tools/coverage_md_sync.py"),
        "--coverage",
        str(cov_path),
        "--write",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
print(sync.stdout)
if sync.returncode != 0:
    print(sync.stderr, file=sys.stderr)
    sys.exit(sync.returncode)
