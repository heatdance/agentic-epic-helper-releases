"""Emit CRT-594-discover.json from principal fixture + Phase 0c smoke (no creds in output)."""
from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json"
OUT = ROOT / "epics/CRT-594/CRT-594-discover.json"
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

doc = json.loads(FIXTURE.read_text(encoding="utf-8"))

doc["sources"].update(
    {
        "ref_path": "epics/CRT-594/CRT-594-ref.json",
        "coverage_path": "epics/CRT-594/CRT-594-coverage.json",
        "analysis_path": "epics/CRT-594/CRT-594-analysis.json",
        "discover_run_started_at": NOW,
    }
)
doc["principal_provenance"]["ref_path"] = "epics/CRT-594/CRT-594-ref.json"
doc["principal_provenance"]["copied_at"] = NOW

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
doc["session_gates"]["fe_login_human_gate"] = "success"

# chk-004: no delivery suppression in production ref/analysis
for row in doc["obligation_ledger"]:
    if row["check_id"] == "chk-004":
        row["disposition"] = "affordance_mapped"
        row["affordance_ids"] = ["aff-008"]
        row["fixture_need_ids"] = ["fix-004"]
        row.pop("disposition_note", None)
        break

aff_008 = {
    "id": "aff-008",
    "competency": "frontend",
    "summary": "Derivatives widget bid/ask uses first_tier_quote on Quote stream",
    "linked_check_ids": ["chk-004"],
    "topology_surface_id": "jss-004",
    "evidence_grade": "observed_runtime",
    "setup_role": "observation",
    "setup_depth": "shell_only",
    "artifacts": [],
    "status": "partial",
    "blocked_reason": None,
    "oracle_binding": {
        "oracle_rule_id": "por-003",
        "oracle_rule": "first_tier_quote",
        "volume_control": "first_tier",
        "surface": "dxtrade5_derivatives",
        "source": "ref",
    },
}
doc["verification_affordances"].append(aff_008)

doc["fixture_needs"].append(
    {
        "id": "fix-004",
        "kind": "dxtrade5_retail_positions",
        "surfaces": ["dxtrade5"],
        "topology_surface_id": "jss-004",
        "linked_check_ids": ["chk-004"],
        "derivation": "check_surfaces",
        "setup_depth": "shell_only",
        "affordance_ids": ["aff-008"],
        "notes": "Derivatives widget shell batch",
    }
)

base = NOW
doc["validation_log"] = [
    {"step": "phaseA", "at": base, "action": "11 primary ledger rows"},
    {
        "step": "phaseA-principal",
        "at": base,
        "action": "principal_loaded: 2 provision obligations (obl-001, obl-005)",
    },
    {
        "step": "phaseA-topology",
        "at": base,
        "action": "6 oracle rules; chk-004 affordance_mapped jss-004",
    },
    {
        "step": "phaseC-principal",
        "at": base,
        "action": "1 provision fixture (fix-env-001) for obl-001, obl-005",
    },
    {"step": "phaseB-oracle", "at": base, "action": "6 oracle_binding affordances"},
    {
        "step": "phase0c",
        "at": base,
        "action": "dxtrade5+webbroker authenticated smoke; widgets Positions/FX Spot/Orders/Client Area",
    },
    {
        "step": "phaseE-oracle",
        "at": base,
        "action": "4 surface batches jss-001/002/003/004 + webbroker jss-005",
    },
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
