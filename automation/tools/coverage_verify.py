#!/usr/bin/env python3
"""
Verify COVERAGE -coverage.json (schema v2 obligations).

Examples:
  python automation/tools/coverage_verify.py --mode matrix \\
    --coverage epics/CRT-639/CRT-639-coverage.json

  python automation/tools/coverage_verify.py --mode obligations \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --ref epics/CRT-639/CRT-639-ref.json

  python automation/tools/coverage_verify.py --mode emit \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --md epics/CRT-639/CRT-639-coverage.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "coverage-obligation-contract.json"
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
SCENARIO_BANG_ONLY = re.compile(r"^\s*-\s*!\s", re.I)


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


def _primary_obligations(ref: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        if obl.get("disposition") != "primary_candidate":
            continue
        oid = obl.get("id")
        if oid:
            out[str(oid)] = obl
    return out


def verify_matrix(coverage: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema_v = int(coverage.get("schema_version") or 0)
    if schema_v < 2:
        errors.append(f"schema_version must be >= 2 (got {schema_v})")

    matrix = coverage.get("coverage_matrix") or []
    if not isinstance(matrix, list) or not matrix:
        errors.append("coverage_matrix must be non-empty")
        return errors

    seen_ids: set[str] = set()
    focus = coverage.get("epic_verification_focus") or {}
    focus_stmt = (focus.get("statement") or "").strip() if isinstance(focus, dict) else ""

    for i, row in enumerate(matrix):
        if not isinstance(row, dict):
            errors.append(f"coverage_matrix[{i}]: not an object")
            continue
        mid = row.get("id")
        if not mid:
            errors.append(f"coverage_matrix[{i}]: missing id")
        elif str(mid) in seen_ids:
            errors.append(f"coverage_matrix: duplicate id {mid!r}")
        else:
            seen_ids.add(str(mid))
        role = row.get("verification_role")
        if role not in ("primary", "supporting", "out_of_epic"):
            errors.append(f"coverage_matrix[{i}]: invalid verification_role {role!r}")

    if focus_stmt:
        primary_rows = [
            r
            for r in matrix
            if isinstance(r, dict) and r.get("verification_role") == "primary"
        ]
        if not primary_rows:
            errors.append("epic_verification_focus set but no primary matrix rows")

    return errors


def verify_obligations(
    coverage: dict[str, Any], ref: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    primary = _primary_obligations(ref)
    cov_map = coverage.get("obligations_coverage") or {}
    if not isinstance(cov_map, dict):
        errors.append("obligations_coverage must be an object")
        cov_map = {}

    for oid, obl in primary.items():
        entry = cov_map.get(oid)
        if not isinstance(entry, dict):
            errors.append(f"obligation {oid}: missing obligations_coverage entry")
            continue
        status = entry.get("status")
        ok_status = set(contract.get("obligations_coverage_status") or [])
        if status not in ok_status:
            errors.append(f"obligation {oid}: invalid status {status!r}")

    excluded = coverage.get("excluded_checks_with_reason") or []
    excluded_obl_ids = {
        str(e.get("obligation_id"))
        for e in excluded
        if isinstance(e, dict) and e.get("obligation_id")
    }
    for oid in primary:
        entry = cov_map.get(oid)
        if isinstance(entry, dict) and entry.get("status") == "excluded_with_reason":
            if oid not in excluded_obl_ids and not entry.get("excluded_checks_with_reason"):
                errors.append(
                    f"obligation {oid}: excluded_with_reason needs exclusion pointer"
                )

    inv_heading = (contract.get("section_requirements") or {}).get(
        "invariants_section_heading", "## Invariants under configuration change"
    )
    md_body = coverage.get("smart_checklist_markdown") or ""
    has_inv_obl = any(o.get("kind") == "invariant" for o in primary.values())
    if has_inv_obl and inv_heading not in md_body:
        errors.append(f"smart_checklist_markdown missing section {inv_heading!r}")

    rounding_heading = (contract.get("section_requirements") or {}).get(
        "rounding_section_heading", "## Rounding and display policy"
    )
    has_round_obl = any(o.get("kind") == "rounding" for o in primary.values())
    if has_round_obl and rounding_heading not in md_body:
        errors.append(f"smart_checklist_markdown missing section {rounding_heading!r}")

    forbidden = contract.get("forbidden_scenario_patterns") or []
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        line = str(chk.get("scenario_line") or "")
        for pat in forbidden:
            if not isinstance(pat, dict):
                continue
            rx = pat.get("regex")
            if rx and re.search(rx, line, re.I):
                when = pat.get("when")
                if when == "ref_has_primary_candidate_invariant" and has_inv_obl:
                    errors.append(
                        f"check {chk.get('id')}: forbidden pattern {pat.get('id')}"
                    )
                elif not when:
                    errors.append(
                        f"check {chk.get('id')}: forbidden pattern {pat.get('id')}"
                    )

    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        role = chk.get("verification_role")
        if role != "primary":
            continue
        line = str(chk.get("scenario_line") or "")
        rkeys = chk.get("requirement_keys") or []
        obl_ids = chk.get("obligation_ids") or []
        if not rkeys and not obl_ids:
            errors.append(f"primary check {chk.get('id')}: missing requirement_keys and obligation_ids")
        if SCENARIO_BANG_ONLY.match(line) and not chk.get("ambiguity"):
            errors.append(
                f"primary check {chk.get('id')}: !-only line without ambiguity object"
            )

    anti_ids = {a.get("pattern") for a in (coverage.get("anti_pattern_findings") or []) if isinstance(a, dict)}
    contract_anti = set(contract.get("anti_pattern_ids") or [])
    for aid in contract_anti:
        if aid in anti_ids:
            errors.append(f"anti_pattern_findings contains {aid}")

    return errors


def verify_emit(
    coverage: dict[str, Any], md_path: Path | None
) -> list[str]:
    errors: list[str] = []
    ungrounded = (coverage.get("grounding_audit") or {}).get("ungrounded_check_ids") or []
    if ungrounded:
        errors.append(f"ungrounded_check_ids not empty: {ungrounded}")

    focus = coverage.get("epic_verification_focus") or {}
    focus_stmt = (focus.get("statement") or "").strip() if isinstance(focus, dict) else ""
    md_body = coverage.get("smart_checklist_markdown") or ""
    if md_path and md_path.is_file():
        try:
            md_body = md_path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"cannot read md: {md_path}")

    if focus_stmt and focus_stmt not in md_body:
        errors.append("epic_verification_focus.statement not verbatim in markdown")

    if not md_body.strip():
        errors.append("smart_checklist_markdown empty")

    for path, s in _walk_strings(coverage):
        if TEMP_PATH_RE.search(s):
            errors.append(f"coverage contains /temp/ at {path}")
        if CRTQA_KEY_RE.search(s):
            errors.append(f"coverage contains CRTQA key at {path}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify COVERAGE artifacts")
    ap.add_argument("--mode", choices=("matrix", "obligations", "checks", "emit"), required=True)
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--ref", type=Path, default=None)
    ap.add_argument("--md", type=Path, default=None)
    args = ap.parse_args()

    coverage = _load_json(args.coverage.resolve())
    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2

    contract = _load_json(CONTRACT_PATH) or {}
    errors: list[str] = []

    if args.mode == "matrix":
        errors = verify_matrix(coverage)
    elif args.mode in ("obligations", "checks"):
        if args.ref is None:
            print("--ref required for obligations/checks mode", file=sys.stderr)
            return 2
        ref = _load_json(args.ref.resolve())
        if ref is None:
            print(f"cannot read ref: {args.ref}", file=sys.stderr)
            return 2
        errors = verify_matrix(coverage)
        errors += verify_obligations(coverage, ref, contract)
        if args.mode == "checks":
            errors += verify_emit(coverage, None)
    else:
        errors = verify_matrix(coverage)
        errors += verify_emit(coverage, args.md)

    if errors:
        print(f"coverage_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK coverage_verify mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
