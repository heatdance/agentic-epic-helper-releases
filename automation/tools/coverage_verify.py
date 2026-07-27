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

  python automation/tools/coverage_verify.py --mode emit --strict-topology \\
    --coverage automation/tools/fixtures/coverage/coverage-594-shell-minimal.json \\
    --ref epics/CRT-594/CRT-594-ref.json \\
    --md automation/tools/fixtures/coverage/coverage-594-shell-minimal.md

  python automation/tools/coverage_verify.py --mode reinforce \\
    --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-minimal.json \\
    --ref epics/CRT-594/CRT-594-ref.json \\
    --discover automation/tools/fixtures/discover/discover-594-shell-minimal.json
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
TOPOLOGY_CONTRACT_PATH = REPO_ROOT / "docs" / "coverage-topology-contract.json"
PRINCIPAL_CONTRACT_PATH = REPO_ROOT / "docs" / "coverage-principal-contract.json"
REINFORCE_TOPOLOGY_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "coverage-reinforce-topology-contract.json"
)
REINFORCE_PRINCIPAL_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "coverage-reinforce-principal-contract.json"
)
OPERATOR_HINTS_PATH = REPO_ROOT / "docs" / "coverage-operator-hints.json"
DRAFT_TRUTH_CONTRACT_PATH = REPO_ROOT / "docs" / "coverage-draft-truth-contract.json"
FORBIDDEN_MD_ORACLE_TOKENS = frozenset(
    {
        "console_show_prices_first_tier",
        "first_tier_quote",
        "text_configuration_closest_gte_qty",
        "midpoint_invariant",
        "mark_from_midpoint",
        "console_agent_event_quote",
        "console_agent_event_text_configuration",
        "backup_midpoint_at_eod",
        "unresolved",
    }
)
VALID_SCENARIO_DISPOSITIONS = frozenset({"covered", "deferred", "excluded"})
DELIVERY_LEDGER_DISPOSITION = "tooling_blocked"
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
SCENARIO_BANG_ONLY = re.compile(r"^\s*-\s*!\s", re.I)
OPERATOR_PREFIX_RE = re.compile(
    r"^\s*>\s*(Oracle|Harness|Verified|Prerequisite|Contrast|Note)\b",
    re.M | re.I,
)
MACHINE_LINE_RE = re.compile(r"^\s*>\s*(Discover|Discovery):", re.M | re.I)
PLATFORM_REUSE_HEADING = "## Platform reuse candidates (verify in Jira)"
PRIMARY_FOCUS_HEADING = "## Primary focus"
TAG_STUB_PATTERNS = [
    re.compile(r"card is available", re.I),
    re.compile(r"is present and visible", re.I),
    re.compile(r"must expose .+ per linked", re.I),
    re.compile(r"details card is available", re.I),
    re.compile(r"trade card is available", re.I),
]


def _operator_hints() -> dict[str, Any]:
    return _load_json(OPERATOR_HINTS_PATH) or {}


def _verify_operator_md_hygiene(md_body: str) -> list[str]:
    errors: list[str] = []
    if PLATFORM_REUSE_HEADING in md_body:
        errors.append(
            "smart_checklist_markdown must not contain platform reuse heading "
            "(JSON-only platform_reuse_annex)"
        )
    if MACHINE_LINE_RE.search(md_body):
        errors.append(
            "smart_checklist_markdown must not contain > Discover: or > Discovery: lines"
        )
    return errors


def _verify_detail_lines_no_machine_prefix(checks: list[Any]) -> list[str]:
    errors: list[str] = []
    for chk in checks:
        if not isinstance(chk, dict):
            continue
        cid = str(chk.get("id") or "?")
        for i, line in enumerate(chk.get("detail_lines") or []):
            if MACHINE_LINE_RE.search(str(line)):
                errors.append(
                    f"check {cid} detail_lines[{i}]: machine line must be "
                    "in linker_trace_lines only"
                )
    return errors


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
    coverage: dict[str, Any], ref: dict[str, Any], contract: dict[str, Any],
    md_path: Path | None = None,
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
    md_body = _md_body(coverage, md_path)
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

    if ref:
        errors.extend(verify_atomic_checks(coverage, ref, contract))

    return errors


def _req_snippet_ok(ref: dict[str, Any], key: str) -> bool:
    for row in ref.get("requirements") or []:
        if isinstance(row, dict) and str(row.get("key") or "") == key:
            return row.get("snippet_status") == "ok"
    return False


def verify_atomic_checks(
    coverage: dict[str, Any], ref: dict[str, Any], contract: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    primary = _primary_obligations(ref)
    cov_map = coverage.get("obligations_coverage") or {}
    checks_by_id = {
        str(c.get("id")): c
        for c in (coverage.get("checks") or [])
        if isinstance(c, dict) and c.get("id")
    }

    for oid, obl in primary.items():
        entry = cov_map.get(oid)
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "covered":
            continue
        cid = entry.get("check_id")
        if not cid or str(cid) not in checks_by_id:
            errors.append(f"obligation_without_atomic_check: {oid} missing check_id")
            continue
        chk = checks_by_id[str(cid)]
        obl_ids = chk.get("obligation_ids") or []
        if len(obl_ids) != 1 or str(obl_ids[0]) != oid:
            errors.append(
                f"check {cid}: expected exactly one obligation_id {oid}, got {obl_ids!r}"
            )

    stub_patterns = contract.get("tag_level_stub_patterns") or []
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        line = str(chk.get("scenario_line") or "")
        rkeys = chk.get("requirement_keys") or []
        if not any(_req_snippet_ok(ref, str(k)) for k in rkeys):
            continue
        for pat in stub_patterns:
            if re.search(pat, line, re.I):
                errors.append(
                    f"tag_level_stub_check: check {chk.get('id')}: stub wording with ok snippet"
                )
                break

        subsection = str(chk.get("subsection") or "").strip()
        if subsection:
            sub_plain = subsection.lstrip("#").strip().lower()
            line_lower = line.lower()
            if sub_plain and sub_plain in line_lower:
                errors.append(
                    f"redundant_context_prefix: check {chk.get('id')}: "
                    "scenario_line repeats subsection context"
                )

    return errors


def verify_collapsed_intro(md_body: str) -> list[str]:
    errors: list[str] = []
    if PRIMARY_FOCUS_HEADING in md_body:
        errors.append("collapsed_intro_violation: ## Primary focus must not appear in paste")
    return errors


def _md_body(coverage: dict[str, Any], md_path: Path | None) -> str:
    md_body = coverage.get("smart_checklist_markdown") or ""
    if md_path and md_path.is_file():
        try:
            md_body = md_path.read_text(encoding="utf-8")
        except OSError:
            return ""
    return md_body


def _expected_emit_layout(archetype: str | None, topo_contract: dict[str, Any]) -> str | None:
    mapping = (topo_contract.get("emit_layout") or {}).get("map_from_archetype") or {}
    if not archetype:
        return None
    return mapping.get(str(archetype))


def _surface_heading(shell: str, widget: str, topo_contract: dict[str, Any]) -> str:
    labels = (
        ((topo_contract.get("section_spine") or {}).get("shell_first") or {}).get(
            "shell_labels"
        )
        or {}
    )
    shell_label = labels.get(shell, shell)
    return f"## {shell_label} — {widget}"


def verify_strict_topology(
    coverage: dict[str, Any],
    ref: dict[str, Any],
    topo_contract: dict[str, Any],
    md_path: Path | None,
) -> list[str]:
    errors: list[str] = []
    ref_arch = ref.get("epic_archetype") or {}
    ref_arch_val = ref_arch.get("value") if isinstance(ref_arch, dict) else None
    ref_topo = ref.get("verification_topology") or {}
    if not isinstance(ref_topo, dict):
        ref_topo = {}

    if not ref_arch_val and not ref_topo:
        return errors

    expected_layout = _expected_emit_layout(
        str(ref_arch_val) if ref_arch_val else None, topo_contract
    )
    emit_layout = coverage.get("emit_layout")
    if expected_layout and emit_layout != expected_layout:
        errors.append(
            f"emit_layout {emit_layout!r} != expected {expected_layout!r} "
            f"for archetype {ref_arch_val!r}"
        )

    md_body = _md_body(coverage, md_path)
    if emit_layout == "formula_first":
        spine = (topo_contract.get("section_spine") or {}).get("formula_first") or {}
        for fragment in spine.get("required_h2_contains") or []:
            if fragment not in md_body:
                errors.append(
                    f"formula_first markdown missing required H2 fragment {fragment!r}"
                )
    elif emit_layout == "shell_first":
        surfaces = ref_topo.get("jira_scenario_surfaces") or []
        checks = coverage.get("checks") or []
        bound_surface_ids = {
            str(c.get("topology_surface_id"))
            for c in checks
            if isinstance(c, dict) and c.get("topology_surface_id")
        }
        for surf in surfaces:
            if not isinstance(surf, dict):
                continue
            sid = surf.get("id")
            if not sid:
                continue
            if str(sid) not in bound_surface_ids:
                shell = str(surf.get("shell") or "")
                widget = str(surf.get("widget") or "")
                heading = _surface_heading(shell, widget, topo_contract)
                section_match = any(
                    isinstance(c, dict)
                    and str(c.get("section") or "").strip() == heading
                    for c in checks
                )
                if not section_match:
                    errors.append(
                        f"shell_first: no check bound to surface {sid!r} "
                        f"(expected section {heading!r} or topology_surface_id)"
                    )

        spine = (topo_contract.get("section_spine") or {}).get("shell_first") or {}
        for surf in surfaces:
            if not isinstance(surf, dict):
                continue
            heading = _surface_heading(
                str(surf.get("shell") or ""),
                str(surf.get("widget") or ""),
                topo_contract,
            )
            if heading not in md_body:
                errors.append(f"shell_first markdown missing section {heading!r}")

    ref_oracle_ids = {
        str(r.get("id"))
        for r in (ref_topo.get("pricing_oracle_rules") or [])
        if isinstance(r, dict) and r.get("id")
    }
    if ref_oracle_ids:
        check_oracle_ids = {
            str(c.get("oracle_rule_id"))
            for c in (coverage.get("checks") or [])
            if isinstance(c, dict) and c.get("oracle_rule_id")
        }
        unknown = check_oracle_ids - ref_oracle_ids
        if unknown:
            errors.append(f"oracle_rule_id not in ref: {sorted(unknown)}")
        primary_oracle = {
            str(r.get("id"))
            for r in (ref_topo.get("pricing_oracle_rules") or [])
            if isinstance(r, dict)
            and r.get("id")
            and r.get("disposition") == "primary_candidate"
        }
        unbound = primary_oracle - check_oracle_ids
        if unbound:
            errors.append(f"oracle_unbound: primary ref rules without check binding: {sorted(unbound)}")

    delivery_map = (
        (topo_contract.get("check_extensions") or {})
        .get("delivery_status", {})
        .get("maps_from_delivery_note_status")
        or {}
    )
    delivery_notes = ref_topo.get("delivery_notes") or []
    if delivery_notes:
        checks = coverage.get("checks") or []
        for note in delivery_notes:
            if not isinstance(note, dict):
                continue
            status = note.get("status")
            if status not in ("known_fail", "excluded"):
                continue
            expected_ds = delivery_map.get(str(status))
            if not expected_ds:
                continue
            has_marker = any(
                isinstance(c, dict) and c.get("delivery_status") == expected_ds
                for c in checks
            )
            if not has_marker:
                errors.append(
                    f"delivery_silent: ref delivery_note {note.get('id')!r} "
                    f"({status}) has no check with delivery_status={expected_ds!r}"
                )
            if status == "known_fail" and "[FAILED]" not in md_body:
                errors.append("delivery_silent: markdown missing [FAILED] marker")
            if status == "excluded" and not re.search(
                r"\bx\b|excluded", md_body, re.I
            ):
                errors.append("delivery_silent: markdown missing excluded/x marker")

    prov = coverage.get("topology_provenance")
    if isinstance(prov, dict):
        if not prov.get("ref_path"):
            errors.append("topology_provenance.ref_path missing")
        if not prov.get("copied_at"):
            errors.append("topology_provenance.copied_at missing")

    return errors


def _provision_obligations(ref: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        oid = obl.get("id")
        if not oid:
            continue
        hints = obl.get("downstream_hints") or {}
        if isinstance(hints, dict) and hints.get("needs_environment_provision"):
            out[str(oid)] = obl
        elif obl.get("kind") == "environment_setup":
            out[str(oid)] = obl
    return out


def _provision_fixtures_from_discover(discover: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fix in discover.get("fixture_needs") or []:
        if not isinstance(fix, dict):
            continue
        if fix.get("derivation") == "ref_principal_provision":
            out.append(fix)
            continue
        oids = fix.get("linked_obligation_ids") or []
        if isinstance(oids, list) and len(oids) > 0:
            out.append(fix)
    return out


def _validation_log_steps(coverage: dict[str, Any]) -> set[str]:
    steps: set[str] = set()
    for row in coverage.get("validation_log") or []:
        if isinstance(row, dict) and row.get("step"):
            steps.add(str(row["step"]))
    return steps


def _discover_deferral_keyed_skip(discover: dict[str, Any]) -> bool:
    for row in discover.get("validation_log") or []:
        if isinstance(row, dict) and row.get("step") == "phaseE_skipped_deferral_keyed":
            return True
    return False


def _ref_has_principal_reinforce(ref: dict[str, Any]) -> bool:
    if _ref_focus_proposed(ref):
        return True
    ref_topo = ref.get("verification_topology") or {}
    if not isinstance(ref_topo, dict):
        ref_topo = {}
    threads = ref_topo.get("principal_coverage_threads") or []
    if isinstance(threads, list) and len(threads) > 0:
        return True
    if _provision_obligations(ref):
        return True
    if _deferral_obligations(ref):
        return True
    return False


def verify_strict_reinforce_principal(
    coverage: dict[str, Any],
    ref: dict[str, Any],
    discover: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if discover is None:
        return errors

    discover_sources = discover.get("sources") or {}
    principal_on_discover = (
        isinstance(discover_sources, dict)
        and discover_sources.get("principal_loaded") is True
    )
    if not principal_on_discover and not _ref_has_principal_reinforce(ref):
        return errors

    sources = coverage.get("sources") or {}
    if not isinstance(sources, dict):
        sources = {}

    if principal_on_discover and not sources.get("reinforce_principal_loaded"):
        errors.append(
            "reinforce: sources.reinforce_principal_loaded must be true "
            "when discover principal_loaded (--strict-principal)"
        )

    provision_fixtures = _provision_fixtures_from_discover(discover)
    provision_obls = _provision_obligations(ref)
    log_steps = _validation_log_steps(coverage)

    if provision_obls and provision_fixtures:
        if "reinforce-2-fixture-provision" not in log_steps and "reinforce-1-principal" not in log_steps:
            errors.append(
                "reinforce: validation_log missing reinforce-2-fixture-provision "
                "or reinforce-1-principal (--strict-principal)"
            )

        checks_by_id = _checks_by_id(coverage)
        for fix in provision_fixtures:
            fix_id = str(fix.get("id") or "")
            kind = str(fix.get("kind") or "")
            oids = [str(x) for x in (fix.get("linked_obligation_ids") or [])]
            linked = fix.get("linked_check_ids") or []
            if not isinstance(linked, list):
                continue
            for cid in linked:
                cid_s = str(cid)
                chk = checks_by_id.get(cid_s)
                if chk is None:
                    errors.append(
                        f"reinforce: provision fixture {fix_id!r} links missing check {cid_s!r}"
                    )
                    continue
                detail_lines = chk.get("detail_lines") or []
                trace_lines = chk.get("linker_trace_lines") or []
                trace_text = (
                    "\n".join(str(d) for d in trace_lines)
                    if isinstance(trace_lines, list)
                    else ""
                )
                detail_text = (
                    "\n".join(str(d) for d in detail_lines)
                    if isinstance(detail_lines, list)
                    else ""
                )
                has_fixture_ref = (
                    (fix_id and fix_id in trace_text)
                    or (kind and kind in trace_text)
                    or any(oid in trace_text for oid in oids)
                )
                if not has_fixture_ref:
                    errors.append(
                        f"reinforce: {cid_s} linker_trace_lines must mention provision fixture "
                        f"kind/id/linked_obligation_ids (--strict-principal)"
                    )
                hints = _operator_hints()
                allowed = hints.get("line_prefixes", {}).get("operator_allowed") or []
                if cid_s.startswith("chk-s") and allowed:
                    allowed_pat = "|".join(re.escape(a) for a in allowed)
                    if not re.search(rf"^\s*>\s*({allowed_pat})\b", detail_text, re.M | re.I):
                        errors.append(
                            f"reinforce: setup check {cid_s} detail_lines need >=1 "
                            f"operator-allowed prefix (--strict-principal)"
                        )

    if _discover_deferral_keyed_skip(discover):
        if "reinforce-2-skipped-deferral-keyed" not in log_steps:
            errors.append(
                "reinforce: validation_log missing reinforce-2-skipped-deferral-keyed "
                "(--strict-principal)"
            )
        for chk in coverage.get("checks") or []:
            if not isinstance(chk, dict):
                continue
            if chk.get("verification_role") != "out_of_epic" and chk.get(
                "coverage_thread"
            ) != "deferral_only":
                continue
            scenario = str(chk.get("scenario_line") or "")
            if scenario.strip() and not SCENARIO_BANG_ONLY.match(scenario):
                errors.append(
                    f"reinforce: deferral-keyed check {chk.get('id')} must retain ! "
                    "scenario_line (--strict-principal)"
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


def _ref_archetype_value(ref: dict[str, Any]) -> str | None:
    arch = ref.get("epic_archetype")
    if isinstance(arch, dict) and arch.get("value"):
        return str(arch["value"])
    return None


def _ref_focus_proposed(ref: dict[str, Any]) -> str:
    focus = ref.get("verification_focus_proposed")
    if isinstance(focus, dict):
        return str(focus.get("statement") or "").strip()
    return ""


def _thread_section_heading(
    thread: dict[str, Any], principal_contract: dict[str, Any]
) -> str:
    title = str(thread.get("title") or "").strip()
    if title:
        return title if title.startswith("##") else f"## {title}"
    ct = str(thread.get("coverage_thread") or "")
    section_map = principal_contract.get("thread_section_map") or {}
    mapped = section_map.get(ct)
    if mapped:
        return str(mapped)
    return f"## {ct.replace('_', ' ').title()}"


def verify_strict_principal(
    coverage: dict[str, Any],
    ref: dict[str, Any],
    principal_contract: dict[str, Any],
    obl_contract: dict[str, Any],
    topo_contract: dict[str, Any],
    md_path: Path | None,
) -> list[str]:
    errors: list[str] = []
    ref_topo = ref.get("verification_topology") or {}
    if not isinstance(ref_topo, dict):
        ref_topo = {}

    proposed_focus = _ref_focus_proposed(ref)
    threads = ref_topo.get("principal_coverage_threads") or []
    has_principal = bool(proposed_focus) or (
        isinstance(threads, list) and len(threads) > 0
    )
    if not has_principal:
        return errors

    cov_focus = coverage.get("epic_verification_focus") or {}
    cov_stmt = (
        str(cov_focus.get("statement") or "").strip()
        if isinstance(cov_focus, dict)
        else ""
    )
    if proposed_focus and cov_stmt != proposed_focus:
        prov = coverage.get("principal_provenance") or {}
        focus_src = (
            str(prov.get("focus_source") or cov_focus.get("source") or "")
            if isinstance(prov, dict) and isinstance(cov_focus, dict)
            else ""
        )
        if focus_src != "user_trigger_focus":
            errors.append(
                "epic_verification_focus.statement must match "
                "ref.verification_focus_proposed verbatim (--strict-principal)"
            )

    md_body = _md_body(coverage, md_path)
    setup_heading = (obl_contract.get("section_requirements") or {}).get(
        "environment_setup_section_heading",
        "## Data setup — account groups and quote publication",
    )
    archetype = _ref_archetype_value(ref)
    metrics_short = archetype == "metrics_calculation"
    emit_layout = coverage.get("emit_layout")

    has_env_thread = any(
        isinstance(t, dict) and t.get("coverage_thread") == "environment_setup"
        for t in (threads if isinstance(threads, list) else [])
    )

    if (
        has_env_thread
        and not metrics_short
        and emit_layout == "shell_first"
        and setup_heading not in md_body
    ):
        errors.append(
            f"shell_first: missing environment_setup section {setup_heading!r}"
        )

    if (
        has_env_thread
        and not metrics_short
        and emit_layout == "shell_first"
        and setup_heading in md_body
    ):
        surfaces = ref_topo.get("jira_scenario_surfaces") or []
        if surfaces and isinstance(surfaces[0], dict):
            first_surface_heading = _surface_heading(
                str(surfaces[0].get("shell") or ""),
                str(surfaces[0].get("widget") or ""),
                topo_contract,
            )
            setup_pos = md_body.find(setup_heading)
            surf_pos = md_body.find(first_surface_heading)
            if surf_pos >= 0 and setup_pos >= 0 and setup_pos > surf_pos:
                errors.append(
                    "environment_setup section must appear before first surface H2"
                )

    checks = coverage.get("checks") or []
    for thread in threads if isinstance(threads, list) else []:
        if not isinstance(thread, dict):
            continue
        heading = _thread_section_heading(thread, principal_contract)
        heading_norm = heading.strip()
        oids = thread.get("obligation_ids") or []
        if not isinstance(oids, list):
            continue
        for oid in oids:
            oid_s = str(oid)
            has_check = any(
                isinstance(c, dict)
                and oid_s in [str(x) for x in (c.get("obligation_ids") or [])]
                and (
                    str(c.get("section") or "").strip() == heading_norm
                    or c.get("coverage_thread") == thread.get("coverage_thread")
                )
                for c in checks
            )
            if not has_check:
                errors.append(
                    f"principal thread {thread.get('thread_id')}: "
                    f"obligation {oid_s} missing check in section {heading_norm!r}"
                )

    deferrals = _deferral_obligations(ref)
    cov_map = coverage.get("obligations_coverage") or {}
    excluded = coverage.get("excluded_checks_with_reason") or []
    excluded_obl_ids = {
        str(e.get("obligation_id"))
        for e in excluded
        if isinstance(e, dict) and e.get("obligation_id")
    }

    for oid, obl in deferrals.items():
        entry = cov_map.get(oid) if isinstance(cov_map, dict) else None
        if not isinstance(entry, dict):
            errors.append(f"deferral obligation {oid}: missing obligations_coverage")
            continue
        status = entry.get("status")
        if status not in ("deferred_in_check", "excluded_with_reason"):
            errors.append(
                f"deferral obligation {oid}: status must be deferred_in_check "
                f"or excluded_with_reason (got {status!r})"
            )
        if status == "excluded_with_reason" and oid not in excluded_obl_ids:
            errors.append(
                f"deferral obligation {oid}: excluded_with_reason needs exclusion pointer"
            )
        keyed_check = any(
            isinstance(c, dict)
            and oid in [str(x) for x in (c.get("obligation_ids") or [])]
            for c in checks
        )
        if status == "deferred_in_check" and not keyed_check:
            errors.append(
                f"deferral obligation {oid}: missing check with obligation_ids"
            )

    if deferrals or any(
        o.get("kind") == "invariant"
        for o in (_primary_obligations(ref).values())
    ):
        for pat in principal_contract.get("forbidden_deferral_patterns") or []:
            if not isinstance(pat, dict):
                continue
            rx = pat.get("regex")
            if not rx:
                continue
            for chk in checks:
                if not isinstance(chk, dict):
                    continue
                line = str(chk.get("scenario_line") or "")
                if re.search(rx, line, re.I):
                    obl_ids = chk.get("obligation_ids") or []
                    if not obl_ids:
                        errors.append(
                            f"check {chk.get('id')}: forbidden blanket deferral "
                            f"pattern {pat.get('id')!r} without obligation_ids"
                        )

    return errors


def _checks_by_id(coverage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for chk in coverage.get("checks") or []:
        if isinstance(chk, dict) and chk.get("id"):
            out[str(chk["id"])] = chk
    return out


def _delivery_blocked_from_discover(discover: dict[str, Any]) -> set[str]:
    blocked: set[str] = set()
    for row in discover.get("obligation_ledger") or []:
        if not isinstance(row, dict):
            continue
        if row.get("disposition") != DELIVERY_LEDGER_DISPOSITION:
            continue
        note = str(row.get("disposition_note") or "")
        if "delivery_known_fail" in note or "delivery_excluded" in note or "dn-" in note:
            cid = row.get("check_id")
            if cid:
                blocked.add(str(cid))
        elif row.get("check_id"):
            blocked.add(str(row["check_id"]))
    return blocked


def _affordances_with_oracle(discover: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for aff in discover.get("verification_affordances") or []:
        if not isinstance(aff, dict):
            continue
        binding = aff.get("oracle_binding")
        if isinstance(binding, dict) and binding.get("oracle_rule_id"):
            out.append(aff)
    return out


def verify_reinforce(
    coverage: dict[str, Any],
    ref: dict[str, Any],
    discover: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if coverage.get("coverage_pass") != 2:
        errors.append("reinforce: coverage_pass must be 2")
        return errors

    if not coverage.get("reinforced_at"):
        errors.append("reinforce: reinforced_at missing")

    sources = coverage.get("sources") or {}
    if not isinstance(sources, dict):
        sources = {}
    reinforce_inputs = sources.get("reinforce_inputs") or []
    if not isinstance(reinforce_inputs, list) or not reinforce_inputs:
        errors.append("reinforce: sources.reinforce_inputs must be non-empty")

    if discover is None:
        if sources.get("reinforce_topology_loaded"):
            errors.append("reinforce: reinforce_topology_loaded but --discover omitted")
        if sources.get("reinforce_principal_loaded"):
            errors.append("reinforce: reinforce_principal_loaded but --discover omitted")
        return errors

    discover_sources = discover.get("sources") or {}
    topology_on_discover = (
        isinstance(discover_sources, dict) and discover_sources.get("topology_loaded") is True
    )
    if topology_on_discover and not sources.get("reinforce_topology_loaded"):
        errors.append("reinforce: discover topology_loaded but sources.reinforce_topology_loaded false")

    checks_by_id = _checks_by_id(coverage)
    oracle_affordances = _affordances_with_oracle(discover)

    for aff in oracle_affordances:
        binding = aff.get("oracle_binding") or {}
        oracle_rule_id = str(binding.get("oracle_rule_id") or "")
        oracle_rule = str(binding.get("oracle_rule") or "")
        linked = aff.get("linked_check_ids") or []
        if not isinstance(linked, list):
            continue
        for cid in linked:
            cid_s = str(cid)
            chk = checks_by_id.get(cid_s)
            if chk is None:
                errors.append(f"reinforce: oracle affordance links missing check {cid_s!r}")
                continue
            if chk.get("oracle_rule_id") != oracle_rule_id:
                errors.append(
                    f"reinforce: {cid_s} oracle_rule_id {chk.get('oracle_rule_id')!r} "
                    f"!= discover binding {oracle_rule_id!r}"
                )
            detail_lines = chk.get("detail_lines") or []
            detail_text = "\n".join(str(d) for d in detail_lines) if isinstance(detail_lines, list) else ""
            if oracle_rule and oracle_rule not in detail_text:
                errors.append(
                    f"reinforce: {cid_s} detail_lines must mention oracle_rule {oracle_rule!r}"
                )

    delivery_blocked = _delivery_blocked_from_discover(discover)
    for cid in delivery_blocked:
        chk = checks_by_id.get(cid)
        if chk is None:
            continue
        ds = chk.get("delivery_status")
        if ds not in ("failed", "excluded"):
            errors.append(
                f"reinforce: delivery-blocked discover ledger {cid} "
                f"missing delivery_status failed/excluded on coverage"
            )

    return errors


VALID_SCENARIO_DISPOSITIONS = frozenset({"covered", "deferred", "excluded"})
VALID_COMBINATORICS = frozenset({"variant_sequence", "single_flow", "matrix"})
VALID_GROUP_SOURCE = frozenset({"principal_thread", "section", "operator_merge"})


def _primary_check_ids(coverage: dict[str, Any]) -> list[str]:
    return [
        str(c["id"])
        for c in (coverage.get("checks") or [])
        if isinstance(c, dict)
        and c.get("id")
        and c.get("verification_role", "primary") == "primary"
    ]


def verify_scenario_groups(coverage: dict[str, Any]) -> list[str]:
    """scenario_groups[] partition lint when coverage frozen (draft_truth_v3)."""
    errors: list[str] = []
    sources = coverage.get("sources") if isinstance(coverage.get("sources"), dict) else {}
    if not sources.get("coverage_frozen_at"):
        return errors

    groups = coverage.get("scenario_groups")
    if not isinstance(groups, list) or not groups:
        errors.append("scenario_groups[] required when sources.coverage_frozen_at is set")
        return errors

    primary_ids = set(_primary_check_ids(coverage))
    seen: set[str] = set()
    group_ids: set[str] = set()

    for i, g in enumerate(groups):
        if not isinstance(g, dict):
            errors.append(f"scenario_groups[{i}] must be an object")
            continue
        gid = str(g.get("group_id") or "")
        if not gid:
            errors.append(f"scenario_groups[{i}] missing group_id")
        elif gid in group_ids:
            errors.append(f"duplicate scenario_groups group_id {gid!r}")
        else:
            group_ids.add(gid)

        comb = g.get("combinatorics")
        if comb is not None and comb not in VALID_COMBINATORICS:
            errors.append(f"scenario_groups[{i}] invalid combinatorics {comb!r}")

        src = g.get("source")
        if src is not None and src not in VALID_GROUP_SOURCE:
            errors.append(f"scenario_groups[{i}] invalid source {src!r}")

        cids = g.get("check_ids") or []
        if not isinstance(cids, list) or not cids:
            errors.append(f"scenario_groups[{i}] check_ids must be non-empty array")
            continue
        for cid in cids:
            sc = str(cid)
            if sc in seen:
                errors.append(f"check_id {sc} appears in more than one scenario_group")
            seen.add(sc)
            if sc not in primary_ids:
                errors.append(
                    f"scenario_groups[{i}] check_id {sc} not a primary check in coverage"
                )

    missing = primary_ids - seen
    if missing:
        errors.append(
            f"scenario_groups missing primary checks: {sorted(missing)}"
        )

    return errors


def verify_draft_truth(
    coverage: dict[str, Any],
    ref: dict[str, Any],
    md_path: Path | None,
) -> list[str]:
    """Draft+truth breadth and markdown oracle lint per coverage-draft-truth-contract."""
    errors: list[str] = []

    cov_pass = coverage.get("coverage_pass")
    if cov_pass not in (1, 2):
        errors.append("coverage_pass must be 1 or 2 for draft_truth emit")

    round_n = coverage.get("draft_truth_round")
    if round_n not in (1, 2):
        errors.append("draft_truth_round must be 1 or 2")

    scen_map = coverage.get("scenario_coverage_map")
    if not isinstance(scen_map, list):
        errors.append("scenario_coverage_map must be an array")
        scen_map = []

    ref_rows = (ref.get("verification_topology") or {}).get("scenario_capability_rows") or []
    if not isinstance(ref_rows, list):
        ref_rows = []

    map_by_scr: dict[str, dict[str, Any]] = {}
    for entry in scen_map:
        if isinstance(entry, dict) and entry.get("scenario_row_id"):
            map_by_scr[str(entry["scenario_row_id"])] = entry

    required_rows = [
        r
        for r in ref_rows
        if isinstance(r, dict)
        and r.get("promotion") in ("primary_candidate", "platform_invariant")
    ]

    for row in required_rows:
        rid = str(row.get("id") or "")
        if not rid:
            continue
        entry = map_by_scr.get(rid)
        if not entry:
            errors.append(f"scenario_coverage_map missing entry for {rid}")
            continue
        disp = entry.get("disposition")
        if disp not in VALID_SCENARIO_DISPOSITIONS:
            errors.append(
                f"scenario_coverage_map {rid}: invalid disposition {disp!r}"
            )
        if row.get("promotion") == "platform_invariant" and disp == "covered":
            if not entry.get("check_id"):
                errors.append(
                    f"platform_invariant {rid}: covered without check_id"
                )

    arch = coverage.get("archetype") or (ref.get("epic_archetype") or {}).get("value")
    if arch == "widget_ui" and required_rows:
        matrix = coverage.get("coverage_matrix") or []
        if len(matrix) < len(required_rows):
            errors.append(
                f"coverage_matrix length {len(matrix)} < required scenario rows "
                f"{len(required_rows)}"
            )

    md_body = _md_body(coverage, md_path)
    for token in FORBIDDEN_MD_ORACLE_TOKENS:
        if token in md_body:
            errors.append(
                f"smart_checklist_markdown contains forbidden oracle token {token!r}"
            )

    annex = str(coverage.get("platform_reuse_annex") or "")
    for row in required_rows:
        if row.get("promotion") != "platform_invariant":
            continue
        rid = str(row.get("id") or "")
        entry = map_by_scr.get(rid)
        if entry and entry.get("disposition") == "covered" and entry.get("check_id"):
            continue
        topic = str(row.get("source_quote") or "")[:40]
        if annex and topic and topic.split()[0].lower() in annex.lower():
            errors.append(
                f"platform_invariant {rid} appears annex-only without primary check"
            )

    errors.extend(verify_emit(coverage, md_path))
    errors.extend(verify_scenario_groups(coverage))
    return errors


def verify_emit(
    coverage: dict[str, Any], md_path: Path | None
) -> list[str]:
    errors: list[str] = []
    ungrounded = (coverage.get("grounding_audit") or {}).get("ungrounded_check_ids") or []
    if ungrounded:
        errors.append(f"ungrounded_check_ids not empty: {ungrounded}")

    md_body = _md_body(coverage, md_path)

    if not md_body.strip():
        errors.append("smart_checklist_markdown empty")

    errors.extend(verify_collapsed_intro(md_body))
    errors.extend(_verify_operator_md_hygiene(md_body))
    checks = coverage.get("checks") or []
    if isinstance(checks, list):
        errors.extend(_verify_detail_lines_no_machine_prefix(checks))

    for path, s in _walk_strings(coverage):
        if TEMP_PATH_RE.search(s):
            errors.append(f"coverage contains /temp/ at {path}")
        if CRTQA_KEY_RE.search(s):
            errors.append(f"coverage contains CRTQA key at {path}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify COVERAGE artifacts")
    ap.add_argument("--mode", choices=("matrix", "obligations", "checks", "emit", "reinforce", "principal", "draft_truth"), required=True)
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--ref", type=Path, default=None)
    ap.add_argument("--md", type=Path, default=None)
    ap.add_argument(
        "--discover",
        type=Path,
        default=None,
        help="Path to -discover.json for --mode reinforce",
    )
    ap.add_argument(
        "--strict-topology",
        action="store_true",
        help="Lint emit_layout, surface spine, oracle/delivery binding vs ref topology",
    )
    ap.add_argument(
        "--strict-principal",
        action="store_true",
        help="Lint focus copy, principal threads, keyed deferrals vs ref principal fields",
    )
    args = ap.parse_args()

    if args.strict_topology and args.ref is None:
        print("--ref required with --strict-topology", file=sys.stderr)
        return 2
    if (args.strict_principal or args.mode == "principal" or args.mode == "draft_truth") and args.ref is None:
        print("--ref required with --strict-principal / --mode principal / --mode draft_truth", file=sys.stderr)
        return 2

    coverage = _load_json(args.coverage.resolve())
    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2

    contract = _load_json(CONTRACT_PATH) or {}
    topo_contract = _load_json(TOPOLOGY_CONTRACT_PATH) or {}
    principal_contract = _load_json(PRINCIPAL_CONTRACT_PATH) or {}
    strict_princ = args.strict_principal or args.mode == "principal"
    errors: list[str] = []

    if args.mode == "principal":
        ref = _load_json(args.ref.resolve())
        if ref is None:
            print(f"cannot read ref: {args.ref}", file=sys.stderr)
            return 2
        errors = verify_strict_principal(
            coverage, ref, principal_contract, contract, topo_contract, args.md
        )
    elif args.mode == "matrix":
        errors = verify_matrix(coverage)
    elif args.mode == "reinforce":
        if args.ref is None:
            print("--ref required for reinforce mode", file=sys.stderr)
            return 2
        ref = _load_json(args.ref.resolve())
        if ref is None:
            print(f"cannot read ref: {args.ref}", file=sys.stderr)
            return 2
        discover = _load_json(args.discover.resolve()) if args.discover else None
        if args.discover and discover is None:
            print(f"cannot read discover: {args.discover}", file=sys.stderr)
            return 2
        errors = verify_matrix(coverage)
        errors += verify_reinforce(coverage, ref, discover)
        if args.strict_topology:
            errors += verify_strict_topology(
                coverage, ref, topo_contract, args.md
            )
        if strict_princ:
            errors += verify_strict_principal(
                coverage, ref, principal_contract, contract, topo_contract, args.md
            )
            errors += verify_strict_reinforce_principal(coverage, ref, discover)
    elif args.mode == "draft_truth":
        ref = _load_json(args.ref.resolve())
        if ref is None:
            print(f"cannot read ref: {args.ref}", file=sys.stderr)
            return 2
        errors = verify_draft_truth(coverage, ref, args.md)
    elif args.mode in ("obligations", "checks"):
        if args.ref is None:
            print("--ref required for obligations/checks mode", file=sys.stderr)
            return 2
        ref = _load_json(args.ref.resolve())
        if ref is None:
            print(f"cannot read ref: {args.ref}", file=sys.stderr)
            return 2
        errors = verify_matrix(coverage)
        errors += verify_obligations(coverage, ref, contract, args.md)
        if args.mode == "checks":
            errors += verify_emit(coverage, None)
        if args.strict_topology:
            errors += verify_strict_topology(
                coverage, ref, topo_contract, args.md
            )
        if strict_princ:
            errors += verify_strict_principal(
                coverage, ref, principal_contract, contract, topo_contract, args.md
            )
    else:
        errors = verify_matrix(coverage)
        errors += verify_emit(coverage, args.md)
        if args.strict_topology:
            ref = _load_json(args.ref.resolve()) if args.ref else None
            if ref is None:
                print("--ref required with --strict-topology", file=sys.stderr)
                return 2
            errors += verify_strict_topology(
                coverage, ref, topo_contract, args.md
            )
        if strict_princ:
            ref = _load_json(args.ref.resolve()) if args.ref else None
            if ref is None:
                print("--ref required with --strict-principal", file=sys.stderr)
                return 2
            errors += verify_strict_principal(
                coverage, ref, principal_contract, contract, topo_contract, args.md
            )

    if errors:
        print(f"coverage_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK coverage_verify mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
