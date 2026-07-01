#!/usr/bin/env python3
"""
Verify ANALYSE -analysis.json (schema v2).

Examples:
  python automation/tools/analysis_verify.py --mode gaps \\
    --analysis epics/CRT-642/CRT-642-analysis.json

  python automation/tools/analysis_verify.py --mode emit \\
    --analysis epics/CRT-642/CRT-642-analysis.json \\
    --md epics/CRT-642/CRT-642-analysis.md

  python automation/tools/analysis_verify.py --mode emit --strict-topology \\
    --analysis automation/tools/fixtures/analysis/analysis-594-shell-minimal.json \\
    --ref epics/CRT-594/CRT-594-ref.json \\
    --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json \\
    --md automation/tools/fixtures/analysis/analysis-594-shell-minimal.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "analysis-gap-contract.json"
TOPOLOGY_CONTRACT_PATH = REPO_ROOT / "docs" / "analysis-topology-contract.json"
PRINCIPAL_CONTRACT_PATH = REPO_ROOT / "docs" / "analysis-principal-contract.json"
COVERAGE_TOPOLOGY_PATH = REPO_ROOT / "docs" / "coverage-topology-contract.json"
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
FORBIDDEN_MD_HEADINGS = re.compile(
    r"^##\s+(Summary|Questions)\s*$", re.I | re.M
)
POINTER_KEYS = (
    "check_id",
    "obligation_id",
    "requirement_key",
    "delivery_note_id",
    "oracle_rule_id",
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


def _merged_contract() -> dict[str, Any]:
    base = _load_json(CONTRACT_PATH) or {}
    topo = _load_json(TOPOLOGY_CONTRACT_PATH) or {}
    principal = _load_json(PRINCIPAL_CONTRACT_PATH) or {}
    kinds = list(base.get("gap_kinds") or [])
    for k in topo.get("gap_kinds_extension") or []:
        if k not in kinds:
            kinds.append(k)
    for k in principal.get("gap_kinds_extension") or []:
        if k not in kinds:
            kinds.append(k)
    actions = dict(base.get("recommended_action_by_kind") or {})
    actions.update(topo.get("recommended_action_by_kind") or {})
    actions.update(principal.get("recommended_action_by_kind") or {})
    return {
        **base,
        "gap_kinds": kinds,
        "recommended_action_by_kind": actions,
    }


def verify_gaps(doc: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema_v = int(doc.get("schema_version") or 0)
    if schema_v < 2:
        errors.append(f"schema_version must be >= 2 (got {schema_v})")

    valid_kinds = set(contract.get("gap_kinds") or [])
    valid_actions = set(contract.get("recommended_actions") or [])
    forbidden_conf = set(contract.get("emit_forbidden_confidence") or ["low"])
    max_open = int(contract.get("max_open_gaps_emit") or 15)

    gaps = doc.get("gaps") or []
    if not isinstance(gaps, list):
        errors.append("gaps must be an array")
        return errors

    open_count = 0
    seen_ids: set[str] = set()
    for i, g in enumerate(gaps):
        if not isinstance(g, dict):
            errors.append(f"gaps[{i}]: not an object")
            continue
        gid = g.get("id")
        if not gid:
            errors.append(f"gaps[{i}]: missing id")
        elif str(gid) in seen_ids:
            errors.append(f"duplicate gap id {gid!r}")
        else:
            seen_ids.add(str(gid))
        kind = g.get("kind")
        if kind not in valid_kinds:
            errors.append(f"gaps[{i}]: invalid kind {kind!r}")
        conf = g.get("confidence")
        if conf in forbidden_conf:
            errors.append(f"gaps[{i}]: confidence {conf!r} forbidden in emit")
        elif conf not in ("high", "medium"):
            errors.append(f"gaps[{i}]: invalid confidence {conf!r}")
        if not g.get("summary"):
            errors.append(f"gaps[{i}]: missing summary")
        ptr = g.get("pointers")
        if not isinstance(ptr, dict) or not any(
            ptr.get(k) for k in POINTER_KEYS
        ):
            errors.append(
                f"gaps[{i}]: pointers need one of {', '.join(POINTER_KEYS)}"
            )
        action = g.get("recommended_action")
        if action not in valid_actions:
            errors.append(f"gaps[{i}]: invalid recommended_action {action!r}")
        status = g.get("status")
        if status not in ("open", "resolved", "confirmed_gap"):
            errors.append(f"gaps[{i}]: invalid status {status!r}")
        if status == "open":
            open_count += 1

    if open_count > max_open:
        defer = any(
            isinstance(e, dict) and "gap_cap_deferral" in str(e.get("action", ""))
            for e in (doc.get("validation_log") or [])
        )
        if not defer:
            errors.append(f"open gaps count {open_count} exceeds max {max_open}")

    questions = doc.get("questions") or []
    for i, q in enumerate(questions):
        if isinstance(q, dict) and q.get("kind") == "hypothesis":
            errors.append(f"questions[{i}]: hypothesis questions forbidden in v2 generation")

    return errors


def _ref_has_topology(ref: dict[str, Any]) -> bool:
    topo = ref.get("verification_topology") or {}
    if not isinstance(topo, dict):
        return False
    notes = topo.get("delivery_notes") or []
    rules = topo.get("pricing_oracle_rules") or []
    return bool(notes or rules)


def verify_strict_topology(
    doc: dict[str, Any],
    ref: dict[str, Any],
    coverage: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not _ref_has_topology(ref):
        return errors

    topo = ref.get("verification_topology") or {}
    if not isinstance(topo, dict):
        return errors

    gaps = doc.get("gaps") or []
    suppressed_ids = {
        str(r.get("check_id"))
        for r in (doc.get("exploration_suppressed") or [])
        if isinstance(r, dict) and r.get("check_id")
    }

    for note in topo.get("delivery_notes") or []:
        if not isinstance(note, dict):
            continue
        note_status = note.get("status")
        note_id = note.get("id")
        if note_status not in ("known_fail", "excluded") or not note_id:
            continue
        expected_kind = (
            "delivery_known_fail"
            if note_status == "known_fail"
            else "delivery_excluded"
        )
        matching = [
            g
            for g in gaps
            if isinstance(g, dict)
            and g.get("kind") == expected_kind
            and (g.get("pointers") or {}).get("delivery_note_id") == note_id
        ]
        if not matching:
            errors.append(
                f"topology: missing {expected_kind} gap for delivery_note {note_id!r}"
            )

    for rule in topo.get("pricing_oracle_rules") or []:
        if not isinstance(rule, dict):
            continue
        if rule.get("oracle_rule") != "unresolved":
            continue
        rid = rule.get("id")
        if not rid:
            continue
        matching = [
            g
            for g in gaps
            if isinstance(g, dict)
            and g.get("kind") == "surface_oracle_unresolved"
            and (g.get("pointers") or {}).get("oracle_rule_id") == rid
        ]
        if not matching:
            errors.append(
                f"topology: missing surface_oracle_unresolved gap for rule {rid!r}"
            )

    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        ds = chk.get("delivery_status")
        if ds not in ("failed", "excluded"):
            continue
        cid = chk.get("id")
        if cid and str(cid) not in suppressed_ids:
            errors.append(
                f"topology: check {cid!r} delivery_status={ds!r} "
                "missing exploration_suppressed row"
            )

    action_map = contract.get("recommended_action_by_kind") or {}
    for g in gaps:
        if not isinstance(g, dict):
            continue
        kind = g.get("kind")
        expected = action_map.get(kind)
        if expected and g.get("recommended_action") != expected:
            errors.append(
                f"gap {g.get('id')}: recommended_action {g.get('recommended_action')!r} "
                f"!= expected {expected!r} for kind {kind!r}"
            )

    return errors


def _deferral_obligations(ref: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        oid = obl.get("id")
        if not oid:
            continue
        if obl.get("kind") == "explicit_deferral" or obl.get("disposition") == "deferral_candidate":
            out[str(oid)] = obl
    return out


def _ref_has_principal(ref: dict[str, Any]) -> bool:
    if _deferral_obligations(ref):
        return True
    focus = ref.get("verification_focus_proposed")
    if isinstance(focus, dict) and focus.get("statement"):
        return True
    topo = ref.get("verification_topology") or {}
    if isinstance(topo, dict):
        threads = topo.get("principal_coverage_threads") or []
        if isinstance(threads, list) and threads:
            return True
    return False


def verify_strict_principal(
    doc: dict[str, Any],
    ref: dict[str, Any],
    coverage: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if not _ref_has_principal(ref):
        return errors

    deferrals = _deferral_obligations(ref)
    gaps = doc.get("gaps") or []
    cov_map = coverage.get("obligations_coverage") or {}
    if not isinstance(cov_map, dict):
        cov_map = {}

    def _deferral_gap_for_oid(oid: str) -> list[dict[str, Any]]:
        return [
            g
            for g in gaps
            if isinstance(g, dict)
            and g.get("kind") == "deferred_check"
            and (g.get("pointers") or {}).get("obligation_id") == oid
        ]

    for oid in deferrals:
        matching = _deferral_gap_for_oid(oid)
        if not matching:
            errors.append(
                f"principal: missing deferred_check gap for deferral obligation {oid!r}"
            )
        else:
            for g in matching:
                ptr = g.get("pointers") or {}
                if not ptr.get("obligation_id"):
                    errors.append(
                        f"principal: gap {g.get('id')}: deferred_check missing "
                        "pointers.obligation_id (--strict-principal)"
                    )

    for oid, entry in cov_map.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "deferred_in_check":
            continue
        matching = _deferral_gap_for_oid(str(oid))
        if not matching:
            errors.append(
                f"principal: missing deferred_check gap for "
                f"obligations_coverage.deferred_in_check {oid!r}"
            )

    deferral_ids = set(deferrals.keys())
    for g in gaps:
        if not isinstance(g, dict):
            continue
        if g.get("kind") != "obligation_uncovered":
            continue
        oid = (g.get("pointers") or {}).get("obligation_id")
        if oid and str(oid) in deferral_ids:
            entry = cov_map.get(str(oid))
            if isinstance(entry, dict) and entry.get("status") == "deferred_in_check":
                errors.append(
                    f"principal: forbidden obligation_uncovered gap {g.get('id')!r} "
                    f"for deferral obligation {oid!r}"
                )

    topo = ref.get("verification_topology") or {}
    if isinstance(topo, dict):
        for note in topo.get("delivery_notes") or []:
            if not isinstance(note, dict):
                continue
            note_id = note.get("id")
            linked = note.get("linked_obligation_ids") or []
            if not note_id or not isinstance(linked, list) or len(linked) != 1:
                continue
            oid = str(linked[0])
            note_status = note.get("status")
            if note_status not in ("known_fail", "excluded"):
                continue
            expected_kind = (
                "delivery_known_fail"
                if note_status == "known_fail"
                else "delivery_excluded"
            )
            delivery_gaps = [
                g
                for g in gaps
                if isinstance(g, dict)
                and g.get("kind") == expected_kind
                and (g.get("pointers") or {}).get("delivery_note_id") == note_id
            ]
            for g in delivery_gaps:
                ptr = g.get("pointers") or {}
                if ptr.get("obligation_id") != oid:
                    errors.append(
                        f"principal: delivery gap {g.get('id')}: missing or wrong "
                        f"pointers.obligation_id (expected {oid!r} from linked_obligation_ids)"
                    )

    if deferrals:
        has_step = any(
            isinstance(e, dict) and e.get("step") == "3-principal"
            for e in (doc.get("validation_log") or [])
        )
        if not has_step:
            errors.append(
                "validation_log missing step 3-principal when ref has deferral obligations "
                "(--strict-principal)"
            )

    action_map = contract.get("recommended_action_by_kind") or {}
    for g in gaps:
        if not isinstance(g, dict):
            continue
        kind = g.get("kind")
        if kind not in ("deferred_check", "deferral_coverage_drift"):
            continue
        expected = action_map.get(kind)
        if expected and g.get("recommended_action") != expected:
            errors.append(
                f"gap {g.get('id')}: recommended_action {g.get('recommended_action')!r} "
                f"!= expected {expected!r} for kind {kind!r}"
            )

    return errors


def _check_no_crtqa(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ki_enabled = (doc.get("sources") or {}).get("known_issues_enabled") is True

    def _allowed_path(path: str) -> bool:
        if not ki_enabled:
            return False
        return (
            ".known_issues[" in path
            or ".unmapped_known_issues[" in path
            or ".known_issues_search" in path
            or ".coverage_mutations[" in path
        )

    for path, s in _walk_strings(doc):
        if TEMP_PATH_RE.search(s):
            errors.append(f"analysis contains /temp/ at {path}")
        if CRTQA_KEY_RE.search(s) and not _allowed_path(path):
            errors.append(f"analysis contains CRTQA key at {path} (forbidden outside known_issues)")
    return errors


def verify_downstream(doc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_check_no_crtqa(doc))
    for i, row in enumerate(doc.get("exploration_suppressed") or []):
        if not isinstance(row, dict):
            errors.append(f"exploration_suppressed[{i}]: not an object")
            continue
        if not row.get("check_id"):
            errors.append(f"exploration_suppressed[{i}]: missing check_id")
        if not row.get("reason"):
            errors.append(f"exploration_suppressed[{i}]: missing reason")

    return errors


def verify_emit(doc: dict[str, Any], md_path: Path | None) -> list[str]:
    errors = verify_gaps(doc, _merged_contract()) + verify_downstream(doc)
    md_body = ""
    if md_path and md_path.is_file():
        try:
            md_body = md_path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"cannot read md: {md_path}")

    if FORBIDDEN_MD_HEADINGS.search(md_body):
        errors.append("analysis.md must not contain ## Summary or ## Questions sections")

    if "## Gaps" not in md_body:
        errors.append("analysis.md must contain ## Gaps section")

    ki_enabled = (doc.get("sources") or {}).get("known_issues_enabled") is True
    if ki_enabled and "## Known issues" not in md_body:
        errors.append("known_issues=yes but md missing ## Known issues")
    if not ki_enabled and "## Known issues" in md_body:
        errors.append("Known issues section present but known_issues_enabled is false")

    return errors


DRAFT_TRUTH_PATH = REPO_ROOT / "docs" / "analysis-draft-truth-contract.json"
DRAFT_TRUTH_MAX_ROUNDS = 2
VALID_SCENARIO_DISPOSITIONS = frozenset({"covered", "deferred", "excluded"})


def verify_draft_truth(
    analysis: dict[str, Any],
    coverage: dict[str, Any],
    ref: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    rec = analysis.get("draft_truth_recommendation")
    if rec not in ("rerun_coverage", "human_coverage_review"):
        errors.append(
            "draft_truth_recommendation must be rerun_coverage or human_coverage_review"
        )

    round_n = analysis.get("draft_truth_round")
    if round_n not in (1, 2):
        errors.append("analysis draft_truth_round must be 1 or 2")

    scen_map = coverage.get("scenario_coverage_map") or []
    map_by_scr: dict[str, dict[str, Any]] = {}
    if isinstance(scen_map, list):
        for entry in scen_map:
            if isinstance(entry, dict) and entry.get("scenario_row_id"):
                map_by_scr[str(entry["scenario_row_id"])] = entry

    ref_rows = (ref.get("verification_topology") or {}).get("scenario_capability_rows") or []
    required = [
        r
        for r in ref_rows
        if isinstance(r, dict)
        and r.get("promotion") in ("primary_candidate", "platform_invariant")
    ]
    uncovered: list[str] = []
    for row in required:
        rid = str(row.get("id") or "")
        entry = map_by_scr.get(rid)
        if not entry or entry.get("disposition") not in VALID_SCENARIO_DISPOSITIONS:
            uncovered.append(rid)

    gaps = analysis.get("gaps") or []
    if uncovered:
        if not gaps:
            errors.append("gaps[] empty while scenario_coverage_map has uncovered rows")
        if not any(
            isinstance(g, dict) and g.get("kind") == "scenario_row_uncovered" for g in gaps
        ):
            errors.append("missing scenario_row_uncovered gap for uncovered rows")

    if rec == "rerun_coverage" and round_n is not None and round_n >= DRAFT_TRUTH_MAX_ROUNDS:
        errors.append("rerun_coverage recommendation invalid when draft_truth_round at max")

    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        for probe in chk.get("runtime_probes") or []:
            if not isinstance(probe, dict):
                continue
            if probe.get("outcome") in ("failed", "blocked") and not chk.get("ambiguity"):
                if not any(
                    isinstance(g, dict)
                    and g.get("kind") == "console_probe_failed"
                    and (g.get("pointers") or {}).get("check_id") == cid
                    for g in gaps
                ):
                    errors.append(
                        f"{cid}: failed/blocked probe without console_probe_failed gap"
                    )

    _ = DRAFT_TRUTH_PATH
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify ANALYSE artifacts")
    ap.add_argument(
        "--mode",
        choices=("gaps", "downstream", "emit", "principal", "draft_truth"),
        required=True,
    )
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--md", type=Path, default=None)
    ap.add_argument("--ref", type=Path, default=None)
    ap.add_argument("--coverage", type=Path, default=None)
    ap.add_argument(
        "--strict-topology",
        action="store_true",
        help="Lint delivery/oracle gaps and exploration_suppressed vs ref+coverage",
    )
    ap.add_argument(
        "--strict-principal",
        action="store_true",
        help="Lint deferral gaps vs ref+coverage principal handoff",
    )
    args = ap.parse_args()

    strict_princ = args.strict_principal or args.mode == "principal"
    if strict_princ and (args.ref is None or args.coverage is None):
        print(
            "--ref and --coverage required with --strict-principal / --mode principal",
            file=sys.stderr,
        )
        return 2

    if args.strict_topology and (args.ref is None or args.coverage is None):
        print("--ref and --coverage required with --strict-topology", file=sys.stderr)
        return 2

    doc = _load_json(args.analysis.resolve())
    if doc is None:
        print(f"cannot read analysis: {args.analysis}", file=sys.stderr)
        return 2

    contract = _merged_contract()
    if args.mode == "gaps":
        errors = verify_gaps(doc, contract)
    elif args.mode == "downstream":
        errors = verify_downstream(doc)
    elif args.mode == "principal":
        ref = _load_json(args.ref.resolve()) if args.ref else None
        coverage = _load_json(args.coverage.resolve()) if args.coverage else None
        if ref is None or coverage is None:
            return 2
        errors = verify_strict_principal(doc, ref, coverage, contract)
    elif args.mode == "draft_truth":
        if args.ref is None or args.coverage is None:
            print("--ref and --coverage required for draft_truth mode", file=sys.stderr)
            return 2
        ref = _load_json(args.ref.resolve())
        coverage = _load_json(args.coverage.resolve())
        if ref is None or coverage is None:
            return 2
        errors = verify_draft_truth(doc, coverage, ref)
    else:
        errors = verify_emit(doc, args.md)

    if args.strict_topology:
        ref = _load_json(args.ref.resolve()) if args.ref else None
        coverage = _load_json(args.coverage.resolve()) if args.coverage else None
        if ref is None:
            print(f"cannot read ref: {args.ref}", file=sys.stderr)
            return 2
        if coverage is None:
            print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
            return 2
        errors += verify_strict_topology(doc, ref, coverage, contract)

    if strict_princ and args.mode != "principal":
        ref = _load_json(args.ref.resolve()) if args.ref else None
        coverage = _load_json(args.coverage.resolve()) if args.coverage else None
        if ref is None or coverage is None:
            return 2
        errors += verify_strict_principal(doc, ref, coverage, contract)

    if errors:
        print(f"analysis_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_gaps = len(doc.get("gaps") or [])
    n_sup = len(doc.get("exploration_suppressed") or [])
    print(f"OK analysis_verify mode={args.mode} gaps={n_gaps} suppressed={n_sup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
