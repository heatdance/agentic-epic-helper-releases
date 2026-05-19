#!/usr/bin/env python3
"""
Verify TEST-DISCOVER obligation closure before emitting -discover.json.

Exits non-zero when primary coverage obligations are not dispositioned,
complete status is inconsistent, required tooling is blocked without recovery,
CRTQA index hygiene fails (schema v3 generation mode), setup depth bar fails,
or durable JSON contains /temp/ path segments.

Examples:
  python automation/tools/discover_verify.py \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --ledger epics/CRT-639/temp/discover-ledger.json

  python automation/tools/discover_verify.py \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --discover epics/CRT-639/CRT-639-discover.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DISPOSITION_OK = frozenset(
    {
        "affordance_mapped",
        "fixture_need_mapped",
        "prerequisite_mapped",
        "tooling_blocked",
        "scope_gap",
    }
)

SHALLOW_SETUP_DEPTH = frozenset({"classified_only", "shell_only"})
SETUP_DEPTH_OK = frozenset({"command_family", "probe_executed"})
FE_FIXTURE_KIND_SURFACE = {
    "webbroker_dealer_client_metrics": "webbroker",
    "dxtrade5_retail_positions": "dxtrade5",
}
FE_UI_AUTHENTICATED_OK = frozenset({"authenticated", "waived"})
ADAPTIVE_AFFECTED_STATUSES = frozenset({"affected", "likely_affected"})
ADAPTIVE_NOT_PROBED_RE = re.compile(r"adaptive.*not.*probed|adaptive_surface_not_smoke_probed", re.I)
REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PROBES_PATH = REPO_ROOT / "docs" / "discover-fixture-probes.json"

ISSUE_KEY_RE = re.compile(r"\b(CRTQA|CRTBL|CRT|XT)-\d+\b", re.I)
CRTQA_KEY_RE = re.compile(r"^CRTQA-\d+$", re.I)
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
PASSWORDISH_RE = re.compile(
    r"(password\s*[:=]|postgresql://[^@\s]+:[^@\s]+@|Bearer\s+[A-Za-z0-9._-]{20,})",
    re.I,
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _primary_check_ids(coverage: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if not cid:
            continue
        role = chk.get("verification_role")
        if role == "primary":
            ids.append(str(cid))
    return sorted(set(ids))


def _ledger_by_check(ledger_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in ledger_doc.get("obligation_ledger") or []:
        if isinstance(row, dict) and row.get("check_id"):
            out[str(row["check_id"])] = row
    return out


def _load_fixture_probe_kinds() -> dict[str, dict[str, Any]]:
    data = _load_json(FIXTURE_PROBES_PATH)
    if not data:
        return {}
    kinds = data.get("kinds")
    return kinds if isinstance(kinds, dict) else {}


def _adaptive_affected(doc: dict[str, Any], ref_doc: dict[str, Any] | None) -> bool:
    env = doc.get("environment") or {}
    if isinstance(env, dict):
        csi = env.get("client_shell_impact") or {}
        if isinstance(csi, dict):
            adaptive = csi.get("adaptive")
            if isinstance(adaptive, dict):
                status = adaptive.get("status")
                if isinstance(status, str) and status.lower() in ADAPTIVE_AFFECTED_STATUSES:
                    return True
    if ref_doc:
        csi = ref_doc.get("client_shell_impact") or {}
        if isinstance(csi, dict):
            adaptive = csi.get("adaptive")
            if isinstance(adaptive, dict):
                status = adaptive.get("status")
                if isinstance(status, str) and status.lower() in ADAPTIVE_AFFECTED_STATUSES:
                    return True
    return False


def _primary_checks_with_adaptive_surface(
    coverage: dict[str, Any], by_check: dict[str, dict[str, Any]]
) -> list[str]:
    ids: list[str] = []
    for cid in _primary_check_ids(coverage):
        row = by_check.get(cid) or {}
        surfaces = row.get("surfaces") or []
        if isinstance(surfaces, list) and "adaptive" in [str(s).lower() for s in surfaces]:
            ids.append(cid)
    return ids


def _adaptive_affordance_probe_ok(doc: dict[str, Any], adaptive_check_ids: list[str]) -> bool:
    if not adaptive_check_ids:
        return True
    linked: set[str] = set(adaptive_check_ids)
    for aff in doc.get("verification_affordances") or []:
        if not isinstance(aff, dict):
            continue
        aff_checks = aff.get("linked_check_ids") or []
        if not isinstance(aff_checks, list):
            continue
        if not linked.intersection(str(c) for c in aff_checks):
            continue
        summary = str(aff.get("summary") or "").lower()
        if "adaptive" not in summary and aff.get("competency") != "frontend":
            continue
        if aff.get("status") == "skipped" and aff.get("blocked_reason"):
            continue
        depth = aff.get("setup_depth")
        grade = aff.get("evidence_grade")
        if depth == "probe_executed" and grade not in ("doc_only", "unknown", None):
            return True
        if depth == "probe_executed" and aff.get("artifacts"):
            return True
    return False


def _fixture_needs_by_id(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in doc.get("fixture_needs") or []:
        if isinstance(row, dict) and row.get("id"):
            out[str(row["id"])] = row
    return out


def _crtqa_index_enabled(doc: dict[str, Any], mode_override: str | None) -> bool:
    if mode_override == "benchmark":
        return True
    if mode_override == "generation":
        return False
    sources = doc.get("sources") or {}
    if isinstance(sources, dict) and "crtqa_index_enabled" in sources:
        return bool(sources.get("crtqa_index_enabled"))
    # v2 and older: treat as index allowed (legacy artefacts)
    schema_v = doc.get("schema_version")
    if schema_v is not None and int(schema_v) < 3:
        return True
    return False


def _discovery_mode(doc: dict[str, Any], mode_override: str | None) -> str:
    if mode_override in ("generation", "benchmark"):
        return mode_override
    sources = doc.get("sources") or {}
    if isinstance(sources, dict) and sources.get("discovery_mode") in (
        "generation",
        "benchmark",
    ):
        return str(sources["discovery_mode"])
    return "generation"


def _fe_ui_session_state(doc: dict[str, Any], surface: str) -> str | None:
    fe = doc.get("fe_ui_sessions")
    if not isinstance(fe, dict):
        return None
    val = fe.get(surface)
    return str(val) if val is not None else None


def _linked_primary_scope_gap(
    fn: dict[str, Any], by_check: dict[str, dict[str, Any]]
) -> bool:
    linked = fn.get("linked_check_ids") or []
    if not isinstance(linked, list) or not linked:
        return False
    for cid in linked:
        row = by_check.get(str(cid)) or {}
        if row.get("disposition") != "scope_gap":
            return False
    return True


def _verify_fe_ui_sessions(
    doc: dict[str, Any],
    fixture_by_id: dict[str, dict[str, Any]],
    by_check: dict[str, dict[str, Any]],
    *,
    strict_complete: bool,
    index_on: bool,
) -> list[str]:
    errors: list[str] = []
    for fid, fn in fixture_by_id.items():
        kind = fn.get("kind")
        if not kind or str(kind) not in FE_FIXTURE_KIND_SURFACE:
            continue
        surface = FE_FIXTURE_KIND_SURFACE[str(kind)]
        depth = fn.get("setup_depth")
        session = _fe_ui_session_state(doc, surface)
        if depth == "probe_executed" and session not in FE_UI_AUTHENTICATED_OK:
            if not _linked_primary_scope_gap(fn, by_check):
                errors.append(
                    f"fixture {fid} kind {kind!r} setup_depth=probe_executed but "
                    f"fe_ui_sessions.{surface}={session!r} (need authenticated or waived "
                    "with scope_gap on linked checks)"
                )

    if strict_complete and doc.get("discovery_status") == "complete" and not index_on:
        needs_fe = any(_check_needs_setup_depth(by_check.get(cid) or {}) for cid in by_check)
        if needs_fe:
            for surface in ("dxtrade5", "webbroker"):
                has_fe_fixture = any(
                    FE_FIXTURE_KIND_SURFACE.get(str(fn.get("kind") or "")) == surface
                    for fn in fixture_by_id.values()
                )
                if not has_fe_fixture:
                    continue
                session = _fe_ui_session_state(doc, surface)
                if session not in FE_UI_AUTHENTICATED_OK:
                    errors.append(
                        f"discovery_status complete but fe_ui_sessions.{surface}={session!r} "
                        "(need authenticated or waived for FE fixture kinds)"
                    )
    return errors


def _check_needs_setup_depth(row: dict[str, Any]) -> bool:
    evidence = row.get("evidence_need") or []
    if isinstance(evidence, list) and "console" in evidence:
        return True
    surfaces = row.get("surfaces") or []
    if not isinstance(surfaces, list):
        return False
    return bool({"dxtrade5", "webbroker"} & {str(s).lower() for s in surfaces})


def _parse_iso_at(value: str) -> str | None:
    """Return normalized string for comparison, or None if not parseable."""
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _verify_operator_recovery(recovery: list[Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(recovery, list):
        return errors
    for i, item in enumerate(recovery):
        if not isinstance(item, dict):
            errors.append(f"operator_recovery[{i}]: must be an object")
            continue
        if not item.get("gate_id"):
            errors.append(f"operator_recovery[{i}]: missing gate_id")
        if item.get("tool") and not item.get("gate_id"):
            errors.append(
                f"operator_recovery[{i}]: legacy 'tool' field without gate_id — use schema item shape"
            )
        if item.get("action") and not item.get("actions"):
            errors.append(
                f"operator_recovery[{i}]: legacy 'action' only — use actions[] list"
            )
        actions = item.get("actions")
        if not isinstance(actions, list) or len(actions) == 0:
            errors.append(f"operator_recovery[{i}]: actions[] must be non-empty")
        refs = item.get("documentation_refs")
        if not isinstance(refs, list) or len(refs) == 0:
            errors.append(f"operator_recovery[{i}]: documentation_refs[] must be non-empty")
    return errors


def _crtqa_intent_required(tooling: dict[str, Any]) -> bool:
    row = tooling.get("crtqa_dx_console")
    return isinstance(row, dict) and row.get("intent") == "required"


def _postgres_intent_required(tooling: dict[str, Any]) -> bool:
    row = tooling.get("postgres_ctqa")
    return isinstance(row, dict) and row.get("intent") == "required"


def _phase0_gates_failed(doc: dict[str, Any], tooling: dict[str, Any]) -> bool:
    gates = doc.get("session_gates") or {}
    if not isinstance(gates, dict):
        return False
    pg = gates.get("postgres_ctqa_tunnel")
    if _postgres_intent_required(tooling) and pg == "probe_required_operator":
        return True
    hs = gates.get("crtqa_console_handshake")
    if _crtqa_intent_required(tooling) and hs in (
        "failed",
        "pending_operator_session",
    ):
        return True
    return False


def _verify_validation_log_monotonicity(
    doc: dict[str, Any], sources: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    started = _parse_iso_at(str(sources.get("discover_run_started_at") or ""))
    log = doc.get("validation_log") or []
    if not isinstance(log, list):
        return errors
    phase0_count = 0
    seen_proceed = False
    for i, entry in enumerate(log):
        if not isinstance(entry, dict):
            continue
        step = entry.get("step")
        at = _parse_iso_at(str(entry.get("at") or ""))
        if started and at and at < started:
            errors.append(
                f"validation_log[{i}].at ({at}) is before sources.discover_run_started_at ({started})"
            )
        if step == "phase0_proceed":
            seen_proceed = True
        if step == "phase0":
            phase0_count += 1
            if phase0_count > 1 and not seen_proceed:
                errors.append(
                    "validation_log: multiple phase0 entries without phase0_proceed between "
                    "(merged_validation_log_from_prior_run)"
                )
    return errors


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


def verify(
    coverage: dict[str, Any],
    *,
    ledger: dict[str, Any] | None = None,
    discover: dict[str, Any] | None = None,
    strict_complete: bool = True,
    mode_override: str | None = None,
    ref_doc: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    primary_ids = _primary_check_ids(coverage)
    if not primary_ids:
        errors.append("coverage: no primary checks[] rows found")

    doc = discover if discover is not None else ledger
    if doc is None:
        errors.append("must provide --ledger or --discover")
        return errors

    schema_v = doc.get("schema_version")
    if discover is not None and schema_v == 1:
        warnings.append("discover schema_version is 1; v3 obligation_closure expected")
    elif discover is not None and schema_v == 2:
        warnings.append("discover schema_version is 2; v3 fixture_needs / crtqa_index rules apply on re-verify")

    index_on = _crtqa_index_enabled(doc, mode_override)
    mode = _discovery_mode(doc, mode_override)
    by_check = _ledger_by_check(doc)
    fixture_by_id = _fixture_needs_by_id(doc)
    probe_kinds = _load_fixture_probe_kinds()
    env = doc.get("environment") or {}
    if isinstance(env, dict) and not (env.get("client_shell_impact")) and ref_doc is None:
        warnings.append(
            "environment.client_shell_impact missing; Adaptive complete bar uses --ref if provided"
        )

    for cid in primary_ids:
        row = by_check.get(cid)
        if row is None:
            errors.append(f"obligation_ledger: missing row for primary check {cid}")
            continue
        disp = row.get("disposition")
        if disp is None or disp == "pending":
            errors.append(f"obligation_ledger: {cid} still pending")
        elif disp not in DISPOSITION_OK:
            errors.append(f"obligation_ledger: {cid} invalid disposition {disp!r}")
        elif disp == "prerequisite_mapped" and not index_on:
            errors.append(
                f"obligation_ledger: {cid} prerequisite_mapped not allowed when crtqa_index_enabled is false"
            )

    # CRTQA-off hygiene (schema v3 generation)
    if not index_on:
        ref_index = doc.get("reference_index") or []
        precond = doc.get("precondition_signals") or []
        edges = doc.get("prerequisite_edges") or []
        if ref_index:
            errors.append("reference_index must be [] when crtqa_index_enabled is false")
        if precond:
            errors.append("precondition_signals must be [] when crtqa_index_enabled is false")
        if edges:
            errors.append("prerequisite_edges must be [] when crtqa_index_enabled is false")
        for cid in primary_ids:
            row = by_check.get(cid) or {}
            keys = row.get("prerequisite_keys") or []
            if isinstance(keys, list):
                for key in keys:
                    if isinstance(key, str) and CRTQA_KEY_RE.match(key):
                        errors.append(
                            f"{cid}: prerequisite_keys must not cite {key} when crtqa_index_enabled is false"
                        )

    closure = doc.get("obligation_closure") or {}
    setup_depth_gaps: set[str] = set()
    if isinstance(closure, dict):
        for gap in closure.get("setup_depth_gaps") or []:
            if isinstance(gap, dict) and gap.get("check_id"):
                setup_depth_gaps.add(str(gap["check_id"]))
            elif isinstance(gap, str):
                setup_depth_gaps.add(gap)

        pc = closure.get("primary_count")
        dc = closure.get("dispositioned_count")
        if pc is not None and dc is not None and pc != len(primary_ids):
            warnings.append(
                f"obligation_closure.primary_count={pc} != coverage primary count {len(primary_ids)}"
            )
        if strict_complete:
            status = doc.get("discovery_status")
            if status == "complete":
                if not closure.get("verifier_passed"):
                    errors.append(
                        "discovery_status complete but obligation_closure.verifier_passed is false"
                    )
                pending = [
                    cid
                    for cid in primary_ids
                    if by_check.get(cid, {}).get("disposition") in (None, "pending")
                ]
                if pending:
                    errors.append(
                        f"discovery_status complete but pending obligations: {', '.join(pending)}"
                    )

    # Generation setup depth bar for complete
    if strict_complete and doc.get("discovery_status") == "complete" and not index_on:
        for cid in primary_ids:
            row = by_check.get(cid) or {}
            if not _check_needs_setup_depth(row):
                continue
            if cid in setup_depth_gaps:
                errors.append(
                    f"discovery_status complete but {cid} listed in setup_depth_gaps "
                    "(use incomplete or raise setup depth)"
                )
                continue
            need_ids = row.get("fixture_need_ids") or []
            if not isinstance(need_ids, list) or not need_ids:
                if row.get("disposition") == "scope_gap":
                    continue
                warnings.append(f"{cid}: no fixture_need_ids linked for setup-depth check")
                continue
            shallow = False
            for fid in need_ids:
                fn = fixture_by_id.get(str(fid))
                if fn is None:
                    continue
                depth = fn.get("setup_depth")
                if depth in SHALLOW_SETUP_DEPTH:
                    shallow = True
            if shallow:
                errors.append(
                    f"discovery_status complete but {cid} fixture needs still at shallow setup_depth "
                    f"(need {', '.join(SETUP_DEPTH_OK)})"
                )

        errors.extend(
            _verify_fe_ui_sessions(
                doc,
                fixture_by_id,
                by_check,
                strict_complete=strict_complete,
                index_on=index_on,
            )
        )

        # Registry-listed fixture kinds must meet complete_requires (typically probe_executed)
        for fid, fn in fixture_by_id.items():
            kind = fn.get("kind")
            if not kind or str(kind) not in probe_kinds:
                continue
            spec = probe_kinds[str(kind)]
            required = spec.get("complete_requires", "probe_executed")
            linked = fn.get("linked_check_ids") or []
            if not isinstance(linked, list):
                continue
            if not any(str(c) in primary_ids for c in linked):
                continue
            depth = fn.get("setup_depth")
            if required == "probe_executed" and depth != "probe_executed":
                errors.append(
                    f"discovery_status complete but fixture {fid} kind {kind!r} "
                    f"setup_depth={depth!r} (need {required})"
                )

        # Adaptive completeness when ref / snapshot marks affected
        if _adaptive_affected(doc, ref_doc):
            fe = doc.get("fe_credentials") or {}
            if isinstance(fe, dict) and fe.get("adaptive") == "missing":
                errors.append(
                    "fe_credentials.adaptive must be not_required for CTQA shared principal, not missing"
                )
            if isinstance(closure, dict):
                for gap in closure.get("closure_gaps") or []:
                    if not isinstance(gap, dict):
                        continue
                    reason = str(gap.get("reason") or "")
                    if ADAPTIVE_NOT_PROBED_RE.search(reason):
                        errors.append(
                            f"discovery_status complete but closure_gaps reason {reason!r} "
                            "(Adaptive smoke required when client_shell_impact.adaptive affected)"
                        )
            adaptive_checks = _primary_checks_with_adaptive_surface(coverage, by_check)
            if not _adaptive_affordance_probe_ok(doc, adaptive_checks):
                errors.append(
                    "discovery_status complete but Adaptive affected and no verification_affordance "
                    "with probe_executed runtime evidence for adaptive-linked primary checks"
                )

    # Generation warnings: doc_only fixture affordances with shallow linked fixtures
    if not index_on:
        for aff in doc.get("verification_affordances") or []:
            if not isinstance(aff, dict):
                continue
            if aff.get("setup_role") != "fixture":
                continue
            if aff.get("evidence_grade") != "doc_only":
                continue
            aff_id = aff.get("id")
            for fid, fn in fixture_by_id.items():
                aff_ids = fn.get("affordance_ids") or []
                if aff_id not in (aff_ids if isinstance(aff_ids, list) else []):
                    continue
                if fn.get("setup_depth") in SHALLOW_SETUP_DEPTH:
                    for cid in fn.get("linked_check_ids") or []:
                        row = by_check.get(str(cid)) or {}
                        evidence = row.get("evidence_need") or []
                        if isinstance(evidence, list) and "console" in evidence:
                            warnings.append(
                                f"{aff_id}: doc_only fixture affordance but {fid} still "
                                f"{fn.get('setup_depth')} for {cid} with console evidence_need"
                            )

    unresolved = doc.get("unresolved_precondition_refs") or []
    if isinstance(unresolved, list) and index_on:
        for cid in primary_ids:
            row = by_check.get(cid) or {}
            if row.get("disposition") != "prerequisite_mapped":
                continue
            prereq_keys = row.get("prerequisite_keys") or []
            if not isinstance(prereq_keys, list):
                continue
            for key in prereq_keys:
                if key in unresolved and not closure.get("reference_cap_hit"):
                    errors.append(
                        f"{cid}: prerequisite_mapped but {key} listed in unresolved_precondition_refs "
                        "without reference_cap_hit"
                    )

    tooling = doc.get("tooling") or {}
    if not isinstance(tooling, dict):
        tooling = {}
    cold_skip = False
    sources = doc.get("sources") or {}
    if not isinstance(sources, dict):
        sources = {}
    cold_skip = bool(sources.get("cold_gate_skip_token_used"))
    recovery = doc.get("operator_recovery") or []
    if isinstance(recovery, list) and recovery:
        errors.extend(_verify_operator_recovery(recovery))

    # Emitted discover must not exist if Phase 0 required gates failed (without cold skip)
    if discover is not None and not cold_skip and _phase0_gates_failed(doc, tooling):
        errors.append(
            "Phase 0 required gate failed but -discover.json exists — "
            "stop without emit until proceed after operator fix (see test-discover.md)"
        )

    # After Phase 0 pass, durable discover should not carry Phase-0-only recovery rows
    if discover is not None and isinstance(recovery, list) and recovery:
        if not _phase0_gates_failed(doc, tooling):
            errors.append(
                "operator_recovery must be [] on emitted -discover.json when Phase 0 passed "
                "(recovery belongs in chat only for hard stop)"
            )

    crtqa_row = tooling.get("crtqa_dx_console")
    if isinstance(crtqa_row, dict) and crtqa_row.get("intent") == "required":
        if crtqa_row.get("session_started") is False and crtqa_row.get("availability") == "available":
            errors.append(
                "tooling.crtqa_dx_console: session_started false but availability is available "
                "(forbidden when intent required)"
            )
        gates = doc.get("session_gates") or {}
        if isinstance(gates, dict):
            hs = gates.get("crtqa_console_handshake")
            if hs in ("failed", "pending_operator_session") and crtqa_row.get(
                "availability"
            ) == "available":
                errors.append(
                    "session_gates.crtqa_console_handshake failed/pending but "
                    "tooling.crtqa_dx_console.availability is available"
                )

    errors.extend(_verify_validation_log_monotonicity(doc, sources))

    has_recovery = isinstance(recovery, list) and len(recovery) > 0

    for tool_name, tool_row in tooling.items():
        if not isinstance(tool_row, dict):
            continue
        if tool_row.get("intent") != "required":
            continue
        avail = tool_row.get("availability")
        if avail == "available":
            continue
        if avail == "skipped" and cold_skip:
            continue
        if has_recovery:
            continue
        errors.append(
            f"tooling.{tool_name}: intent required but availability={avail!r} "
            "without operator_recovery or cold_gate_skip"
        )

    hygiene_target = discover if discover is not None else doc
    for path, s in _walk_strings(hygiene_target):
        if TEMP_PATH_RE.search(s):
            errors.append(f"schema hygiene: /temp/ path in {path}")
        if PASSWORDISH_RE.search(s):
            errors.append(f"schema hygiene: possible secret in {path}")

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify TEST-DISCOVER obligation closure.")
    ap.add_argument("--coverage", type=Path, required=True, help="Path to <KEY>-coverage.json")
    ap.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="Path to temp/discover-ledger.json or staging copy",
    )
    ap.add_argument(
        "--discover",
        type=Path,
        default=None,
        help="Path to emitted <KEY>-discover.json (post-projection check)",
    )
    ap.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Do not require discovery_status complete ↔ verifier_passed alignment",
    )
    ap.add_argument(
        "--mode",
        choices=("generation", "benchmark"),
        default=None,
        help="Override discovery_mode / crtqa_index_enabled inference from discover doc",
    )
    ap.add_argument(
        "--ref",
        type=Path,
        default=None,
        help="Optional epic-ref.json when environment.client_shell_impact snapshot is missing",
    )
    args = ap.parse_args()

    coverage = _load_json(args.coverage.resolve())
    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2

    ledger_doc = _load_json(args.ledger.resolve()) if args.ledger else None
    discover_doc = _load_json(args.discover.resolve()) if args.discover else None

    if args.ledger and ledger_doc is None:
        print(f"cannot read ledger: {args.ledger}", file=sys.stderr)
        return 2
    if args.discover and discover_doc is None:
        print(f"cannot read discover: {args.discover}", file=sys.stderr)
        return 2

    ref_doc = _load_json(args.ref.resolve()) if args.ref else None
    if args.ref and ref_doc is None:
        print(f"cannot read ref: {args.ref}", file=sys.stderr)
        return 2

    errors = verify(
        coverage,
        ledger=ledger_doc,
        discover=discover_doc,
        strict_complete=not args.allow_incomplete,
        mode_override=args.mode,
        ref_doc=ref_doc,
    )

    if errors:
        print("discover_verify failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    target = args.discover or args.ledger
    print(f"OK obligation closure ({len(_primary_check_ids(coverage))} primary checks) — {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
