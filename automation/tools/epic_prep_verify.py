#!/usr/bin/env python3
"""
Verify EPIC-PREP -ref.json (schema v4 obligations).

Examples:
  python automation/tools/epic_prep_verify.py --mode ref \\
    --ref epics/CRT-639/CRT-639-ref.json

  python automation/tools/epic_prep_verify.py --mode reconcile \\
    --ref epics/CRT-639/CRT-639-ref.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
KINDS_PATH = REPO_ROOT / "docs" / "epic-obligation-kinds.json"
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
VALID_KINDS = frozenset(
    {
        "invariant",
        "ladder",
        "formula",
        "config_posture",
        "settlement",
        "rounding",
        "parity",
        "explicit_deferral",
    }
)
VALID_DISPOSITION = frozenset({"primary_candidate", "deferral_candidate"})
VALID_CONFIG_VS = frozenset(
    {
        "instrument_type_config",
        "account_group_assignment",
        "position_state",
        "routing_or_markup",
        "not_applicable",
    }
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _walk_strings(obj: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(obj, str):
        found.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            found.extend(_walk_strings(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(_walk_strings(v, f"{path}[{i}]"))
    return found


def _jira_linked_keys(ref: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for row in ref.get("requirements") or []:
        if isinstance(row, dict) and row.get("key"):
            keys.add(str(row["key"]))
    return keys


def _deferral_accepted(ref: dict[str, Any]) -> bool:
    for entry in ref.get("validation_log") or []:
        if isinstance(entry, dict) and entry.get("deferral_accepted") is True:
            return True
        if isinstance(entry, str) and "deferral_accepted" in entry.lower():
            return True
    return False


def verify_ref(ref: dict[str, Any], kinds_doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema_v = int(ref.get("schema_version") or 0)
    if schema_v < 4:
        errors.append(f"schema_version must be >= 4 (got {schema_v})")

    valid_kinds = set(kinds_doc.get("kinds") or VALID_KINDS)
    linked = _jira_linked_keys(ref)
    defer_ok = _deferral_accepted(ref)

    for row in ref.get("requirements") or []:
        if not isinstance(row, dict):
            continue
        key = str(row.get("key") or "")
        if key not in linked:
            continue
        status = row.get("snippet_status")
        if status != "ok" and not defer_ok:
            errors.append(
                f"requirements {key}: snippet_status {status!r} "
                "(need ok or validation_log deferral_accepted)"
            )

    obligations = ref.get("obligations_proposed") or []
    if not isinstance(obligations, list):
        errors.append("obligations_proposed must be an array")
        obligations = []

    seen_ids: set[str] = set()
    for i, obl in enumerate(obligations):
        if not isinstance(obl, dict):
            errors.append(f"obligations_proposed[{i}]: not an object")
            continue
        oid = obl.get("id")
        if not oid:
            errors.append(f"obligations_proposed[{i}]: missing id")
        elif str(oid) in seen_ids:
            errors.append(f"obligations_proposed: duplicate id {oid!r}")
        else:
            seen_ids.add(str(oid))
        kind = obl.get("kind")
        if not kind or str(kind) not in valid_kinds:
            errors.append(f"obligations_proposed[{i}]: invalid kind {kind!r}")
        if not obl.get("statement") or not str(obl.get("statement")).strip():
            errors.append(f"obligations_proposed[{i}]: missing statement")
        rkeys = obl.get("requirement_keys") or []
        if not isinstance(rkeys, list) or not rkeys:
            errors.append(f"obligations_proposed[{i}]: requirement_keys must be non-empty")
        disp = obl.get("disposition")
        if disp not in VALID_DISPOSITION:
            errors.append(f"obligations_proposed[{i}]: invalid disposition {disp!r}")
        cvp = obl.get("config_vs_position")
        if cvp and str(cvp) not in VALID_CONFIG_VS:
            errors.append(f"obligations_proposed[{i}]: invalid config_vs_position {cvp!r}")

    reconcile = ref.get("obligations_reconcile")
    if not isinstance(reconcile, dict):
        errors.append("obligations_reconcile must be an object")
    elif reconcile.get("epic_summary_aligned") is not True:
        errors.append("obligations_reconcile.epic_summary_aligned must be true for emit")

    for path, s in _walk_strings(ref):
        if TEMP_PATH_RE.search(s):
            errors.append(f"ref contains /temp/ path at {path}")
        if CRTQA_KEY_RE.search(s):
            errors.append(f"ref contains CRTQA key at {path} (forbidden in generation)")

    return errors


def verify_reconcile(ref: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    obligations = ref.get("obligations_proposed") or []
    reconcile = ref.get("obligations_reconcile") or {}
    if not isinstance(reconcile, dict):
        return ["obligations_reconcile missing"]

    primary_ids = {
        str(o["id"])
        for o in obligations
        if isinstance(o, dict)
        and o.get("disposition") == "primary_candidate"
        and o.get("id")
    }
    conflict_ids = {
        str(c.get("obligation_id"))
        for c in (reconcile.get("conflicts") or [])
        if isinstance(c, dict) and c.get("obligation_id")
    }
    for pid in primary_ids:
        if pid in conflict_ids:
            continue
        stmt = next(
            (o.get("statement") for o in obligations if isinstance(o, dict) and o.get("id") == pid),
            "",
        )
        if not stmt or len(str(stmt)) < 10:
            errors.append(f"reconcile: primary_candidate {pid} has weak statement")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify EPIC-PREP -ref.json")
    ap.add_argument("--mode", choices=("ref", "reconcile"), required=True)
    ap.add_argument("--ref", type=Path, required=True)
    args = ap.parse_args()

    ref = _load_json(args.ref.resolve())
    if ref is None:
        print(f"cannot read ref: {args.ref}", file=sys.stderr)
        return 2

    kinds_doc = _load_json(KINDS_PATH) or {}

    if args.mode == "ref":
        errors = verify_ref(ref, kinds_doc)
    else:
        errors = verify_reconcile(ref)
        errors = verify_ref(ref, kinds_doc) + errors

    if errors:
        print(f"epic_prep_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_obl = len(ref.get("obligations_proposed") or [])
    print(f"OK epic_prep_verify mode={args.mode} obligations={n_obl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
