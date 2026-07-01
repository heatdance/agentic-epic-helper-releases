"""Emit CRT-671 analysis v2 — draft+truth after GROUND."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EPIC = "CRT-671"
EPIC_DIR = ROOT / "epics" / EPIC
REF_PATH = EPIC_DIR / f"{EPIC}-ref.json"
COV_PATH = EPIC_DIR / f"{EPIC}-coverage.json"

DELIVERY_NOTE_CHECKS = {
    "dn-001": "chk-001",
    "dn-002": "chk-002",
    "dn-003": "chk-006",
    "dn-004": "chk-012",
    "dn-005": "chk-013",
    "dn-006": "chk-014",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_md(analysis: dict) -> str:
    lines = ["## Gaps", ""]
    gaps = analysis.get("gaps") or []
    if not gaps:
        lines.append("- (none — mechanical scan clean after coverage v1)")
    else:
        for g in gaps:
            lines.append(
                f"- `{g['id']}` [{g['confidence']}] {g['kind']} — {g['summary']} — action: {g['recommended_action']}"
            )
    lines.extend(["", "## Actions", ""])
    actions = analysis["actions"]
    lines.append(f"- rerun_coverage: {'yes' if actions.get('rerun_coverage') else 'no'}")
    lines.append(f"- rerun_epic_prep: {'yes' if actions.get('rerun_epic_prep') else 'no'}")
    lines.append(f"- focus_hint: {actions.get('focus_hint') or 'null'}")
    lines.append(f"- draft_truth_recommendation: {analysis.get('draft_truth_recommendation')}")
    lines.extend(["", "## Exploration suppressed", ""])
    for row in analysis.get("exploration_suppressed") or []:
        lines.append(
            f"- `{row['check_id']}` reason={row['reason']} until={row['until_action']}"
        )
    return "\n".join(lines) + "\n"


def delivery_gaps(ref: dict) -> list[dict]:
    gaps = []
    idx = 1
    for note in (ref.get("verification_topology") or {}).get("delivery_notes") or []:
        if not isinstance(note, dict) or note.get("status") != "known_fail":
            continue
        nid = note.get("id")
        cid = DELIVERY_NOTE_CHECKS.get(str(nid))
        gaps.append(
            {
                "id": f"gap-{idx:03d}",
                "kind": "delivery_known_fail",
                "confidence": "high",
                "summary": f"Epic validation defect documented: {note.get('evidence', '')[:120]}",
                "pointers": {
                    "delivery_note_id": nid,
                    "check_id": cid,
                    "obligation_id": (note.get("linked_obligation_ids") or ["obl-001"])[0],
                },
                "evidence": f"ref.verification_topology.delivery_notes {nid}",
                "recommended_action": "human_ba",
                "status": "confirmed_gap",
            }
        )
        idx += 1
    return gaps


def main() -> int:
    ref = json.loads(REF_PATH.read_text(encoding="utf-8"))
    cov = json.loads(COV_PATH.read_text(encoding="utf-8"))
    now = utc_now()

    for chk in cov.get("checks") or []:
        if chk.get("delivery_status") == "known_fail":
            chk["delivery_status"] = "failed"

    gaps = delivery_gaps(ref)
    gaps.append(
        {
            "id": f"gap-{len(gaps) + 1:03d}",
            "kind": "console_probe_failed",
            "confidence": "high",
            "summary": (
                "Console probe blocked on chk-e1: CTQA account key must be selected at test time "
                "before show order last open"
            ),
            "pointers": {"check_id": "chk-e1"},
            "evidence": "checks[chk-e1].runtime_probes[gp-chk-e1b].outcome=blocked",
            "recommended_action": "human_operator",
            "status": "confirmed_gap",
        }
    )

    exploration_suppressed = [
        {
            "check_id": cid,
            "reason": "delivery_known_fail",
            "blocks_fixture_probe": True,
            "until_action": "human_ba",
        }
        for cid in DELIVERY_NOTE_CHECKS.values()
    ]

    topology = ref.get("verification_topology") or {}
    analysis = {
        "schema_version": 2,
        "epic_key": EPIC,
        "sources": {
            "ref_path": f"epics/{EPIC}/{EPIC}-ref.json",
            "ref_loaded": True,
            "coverage_path": f"epics/{EPIC}/{EPIC}-coverage.json",
            "coverage_loaded": True,
            "known_issues_enabled": False,
            "resolve_enabled": True,
            "topology_loaded": True,
            "ref_topology_fields": [
                "verification_topology.delivery_notes",
                "verification_topology.pricing_oracle_rules",
            ],
            "principal_loaded": True,
            "ref_principal_fields": [
                "verification_focus_proposed",
                "verification_topology.principal_coverage_threads",
            ],
            "draft_truth_loaded": True,
        },
        "draft_truth_round": cov.get("draft_truth_round") or 1,
        "draft_truth_recommendation": "human_coverage_review",
        "summary": {
            "text": cov["epic_verification_focus"]["statement"],
            "derived_from": ["coverage.epic_verification_focus"],
        },
        "gaps": gaps,
        "resolved_gaps": [],
        "exploration_suppressed": exploration_suppressed,
        "coverage_writebacks": [
            {
                "kind": "delivery_status_normalize",
                "target": "checks[].delivery_status known_fail→failed",
                "evidence": "docs/coverage-topology-contract.json maps_from_delivery_note_status",
            }
        ],
        "actions": {
            "rerun_coverage": False,
            "rerun_epic_prep": False,
            "focus_hint": None,
            "human_notes": [
                "Six epic-validation defects marked [FAILED] in coverage; retest expected per Jira comment."
            ],
        },
        "questions": [],
        "known_issues_search": {"at": None, "queries": []},
        "known_issues": [],
        "unmapped_known_issues": [],
        "coverage_mutations": [],
        "validation_log": [
            {"step": "1", "at": now, "action": "topology_loaded=true principal_loaded=true"},
            {"step": "2", "at": now, "action": f"work_queue={len(gaps)}"},
            {"step": "2-topology", "at": now, "action": f"topology_queue=6 delivery_known_fail"},
            {"step": "2-principal", "at": now, "action": "principal_queue=0"},
            {"step": "2c", "at": now, "action": "console probe scan — chk-e1 blocked probe → console_probe_failed gap"},
            {"step": "3", "at": now, "action": f"mechanical gaps={len(gaps)}"},
            {"step": "3-topology", "at": now, "action": "delivery_known_fail=6 confirmed_gap"},
            {"step": "5", "at": now, "action": f"exploration_suppressed={len(exploration_suppressed)}"},
            {"step": "9", "at": now, "action": "coverage writeback delivery_status failed normalization"},
        ],
    }

    cov_log = cov.get("validation_log") or []
    cov_log.append(
        {"step": "analyse_writeback", "at": now, "action": "delivery_status known_fail→failed per topology contract"}
    )
    cov["validation_log"] = cov_log

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

    json_path = EPIC_DIR / f"{EPIC}-analysis.json"
    md_path = EPIC_DIR / f"{EPIC}-analysis.md"
    json_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(build_md(analysis), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
