#!/usr/bin/env python3
"""
Verify EPIC-PREP -ref.json (schema v4 obligations + optional topology).

Examples:
  python automation/tools/epic_prep_verify.py --mode ref \\
    --ref epics/CRT-639/CRT-639-ref.json

  python automation/tools/epic_prep_verify.py --mode ref --strict-topology \\
    --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json

  python automation/tools/epic_prep_verify.py --mode ref --strict-principal \\
    --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json

  python automation/tools/epic_prep_verify.py --mode principal \\
    --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json

  python automation/tools/epic_prep_verify.py --mode reconcile \\
    --ref epics/CRT-639/CRT-639-ref.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
KINDS_PATH = REPO_ROOT / "docs" / "epic-obligation-kinds.json"
TOPOLOGY_PATH = REPO_ROOT / "docs" / "epic-prep-topology-contract.json"
SCENARIO_PATH = REPO_ROOT / "docs" / "epic-prep-scenario-contract.json"
PRINCIPAL_PATH = REPO_ROOT / "docs" / "epic-prep-principal-contract.json"
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
VALID_ARCHETYPES = frozenset({"widget_ui", "metrics_calculation", "mixed"})
VALID_ARCHETYPE_SOURCES = frozenset(
    {
        "jira_summary",
        "jira_description",
        "jira_scenarios",
        "obligation_kinds",
        "user_trigger_focus",
        "inferred_from_jira",
    }
)
VALID_SHELLS = frozenset(
    {"console", "dxtrade5", "adaptive", "webbroker_dealer", "webbroker_client"}
)
VALID_SHELL_ROLE_STATUS = frozenset({"in_scope", "not_applicable"})
VALID_ORACLE_RULES = frozenset(
    {
        "first_tier_quote",
        "text_configuration_closest_gte_qty",
        "midpoint_invariant",
        "mark_from_midpoint",
        "console_show_prices_first_tier",
        "console_agent_event_quote",
        "console_agent_event_text_configuration",
        "backup_midpoint_at_eod",
        "unresolved",
    }
)
VALID_VOLUME_CONTROL = frozenset(
    {
        "order_default_qty",
        "order_qty",
        "position_qty",
        "first_tier",
        "not_applicable",
    }
)
VALID_DELIVERY_STATUS = frozenset(
    {"known_fail", "excluded", "waived", "pending_verification"}
)
VALID_DELIVERY_SOURCE = frozenset(
    {
        "jira_comment",
        "jira_description",
        "operator_focus",
        "post_implementation",
    }
)
VALID_REUSE_CONFIDENCE = frozenset({"high", "medium", "low"})
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
        "environment_setup",
    }
)
VALID_COVERAGE_THREADS = frozenset(
    {
        "environment_setup",
        "functional_config",
        "mapping_routing",
        "surface_quotes",
        "invariants",
        "backup_eod",
        "dimensions",
        "deferral_only",
    }
)
VALID_PERSONAS = frozenset(
    {"console", "retail", "dealer", "mobile", "cross_persona"}
)
VALID_SCENARIO_PROMOTION = frozenset(
    {"primary_candidate", "platform_invariant", "deferral_candidate"}
)
VALID_CAPABILITY_KIND = frozenset(
    {"jira_scenario", "platform_invariant", "cross_surface", "setup"}
)
SETUP_KEYWORDS = re.compile(
    r"\b(account\s+group|fxconfiguration|cornertraderfxconfiguration|publish|tier|suffix|fxspotsuffix)\b",
    re.I,
)
BACKUP_EOD_KEYWORDS = re.compile(
    r"\b(backup|eod|end\s+of\s+day|daily_data_recorder)\b",
    re.I,
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
PARAM_TABLE_RE = re.compile(
    r"\b(Side|Quantity|Description|Fill price|Commission|Fees|Taxes|Symbol|"
    r"Account name|Transaction date|Realized PL|Total cost|Cash effect)\b",
    re.I,
)
QUOTE_KEYWORDS = re.compile(
    r"\b(bid|ask|tier|textconfiguration|midpoint|mark|quote)\b", re.I
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


RECOVERABLE_SNIPPET_FAILURES = frozenset({"mcp_export_failed", "no_cookie"})


def _ci_strict_blocks_deferral(*, ci_strict: bool) -> bool:
    """True when CI must reject deferral_accepted for failed snippets."""
    if not ci_strict:
        return False
    if (os.environ.get("ALLOW_SNIPPET_DEFERRAL") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return True


def _epic_has_quote_keywords(ref: dict[str, Any]) -> bool:
    texts: list[str] = []
    epic = ref.get("epic") or {}
    if epic.get("summary"):
        texts.append(str(epic["summary"]))
    syn = ref.get("synthesis") or {}
    if syn.get("problem_gist"):
        texts.append(str(syn["problem_gist"]))
    for row in ref.get("requirements") or []:
        if isinstance(row, dict) and row.get("snippet_text"):
            texts.append(str(row["snippet_text"]))
    return any(QUOTE_KEYWORDS.search(t) for t in texts)


def _jira_has_scenario_block(ref: dict[str, Any]) -> bool:
    syn = ref.get("synthesis") or {}
    if syn.get("problem_gist") and "scenario" in str(syn["problem_gist"]).lower():
        return True
    for kw in syn.get("keywords") or []:
        text = kw.get("text", kw) if isinstance(kw, dict) else kw
        if "scenario" in str(text).lower():
            return True
    surfaces = (ref.get("verification_topology") or {}).get("jira_scenario_surfaces") or []
    return len(surfaces) > 0


def _epic_text_blob(ref: dict[str, Any]) -> str:
    texts: list[str] = []
    for row in ref.get("obligations_proposed") or []:
        if isinstance(row, dict):
            if row.get("statement"):
                texts.append(str(row["statement"]))
            if row.get("evidence_anchor"):
                texts.append(str(row["evidence_anchor"]))
    syn = ref.get("synthesis") or {}
    if syn.get("problem_gist"):
        texts.append(str(syn["problem_gist"]))
    for kw in syn.get("keywords") or []:
        text = kw.get("text", kw) if isinstance(kw, dict) else kw
        texts.append(str(text))
    return " ".join(texts)


def _has_setup_keywords(ref: dict[str, Any]) -> bool:
    return SETUP_KEYWORDS.search(_epic_text_blob(ref)) is not None


def _has_backup_eod_keywords(ref: dict[str, Any]) -> bool:
    return BACKUP_EOD_KEYWORDS.search(_epic_text_blob(ref)) is not None


def _archetype_value(ref: dict[str, Any]) -> str | None:
    arch = ref.get("epic_archetype")
    if isinstance(arch, dict):
        val = arch.get("value")
        return str(val) if val else None
    return None


def verify_principal(ref: dict[str, Any], strict: bool) -> list[str]:
    if not strict:
        return []

    errors: list[str] = []
    obligations = ref.get("obligations_proposed") or []
    topo = ref.get("verification_topology") or {}
    if not isinstance(topo, dict):
        topo = {}

    focus = ref.get("verification_focus_proposed")
    if not isinstance(focus, dict) or not str(focus.get("statement") or "").strip():
        errors.append(
            "verification_focus_proposed.statement required (--strict-principal)"
        )

    threads = topo.get("principal_coverage_threads")
    if threads is None:
        threads = []
    if not isinstance(threads, list):
        errors.append("principal_coverage_threads must be an array")
        threads = []

    thread_coverage: set[str] = set()
    seen_pct: set[str] = set()
    for i, row in enumerate(threads):
        if not isinstance(row, dict):
            errors.append(f"principal_coverage_threads[{i}]: not an object")
            continue
        tid = row.get("thread_id")
        if not tid:
            errors.append(f"principal_coverage_threads[{i}]: missing thread_id")
        elif str(tid) in seen_pct:
            errors.append(f"principal_coverage_threads: duplicate thread_id {tid!r}")
        else:
            seen_pct.add(str(tid))
        ct = row.get("coverage_thread")
        if ct not in VALID_COVERAGE_THREADS:
            errors.append(
                f"principal_coverage_threads[{i}]: invalid coverage_thread {ct!r}"
            )
        else:
            thread_coverage.add(str(ct))
        oids = row.get("obligation_ids") or []
        if not isinstance(oids, list) or not oids:
            errors.append(
                f"principal_coverage_threads[{i}]: obligation_ids must be non-empty"
            )

    has_env_setup_obl = False
    has_invariant_primary = False
    archetype = _archetype_value(ref)
    metrics_short_circuit = archetype == "metrics_calculation"

    for i, obl in enumerate(obligations):
        if not isinstance(obl, dict):
            continue
        kind = obl.get("kind")
        disp = obl.get("disposition")
        hints = obl.get("downstream_hints")

        if kind == "environment_setup":
            has_env_setup_obl = True

        if kind == "invariant" and disp == "primary_candidate":
            has_invariant_primary = True

        is_deferral = kind == "explicit_deferral" or disp == "deferral_candidate"
        if disp == "primary_candidate" and not is_deferral and not metrics_short_circuit:
            if not isinstance(hints, dict):
                errors.append(
                    f"obligations_proposed[{i}] ({obl.get('id')}): "
                    "downstream_hints required for primary_candidate"
                )
            else:
                ct = hints.get("coverage_thread")
                if not ct or str(ct).strip() == "":
                    errors.append(
                        f"obligations_proposed[{i}] ({obl.get('id')}): "
                        "downstream_hints.coverage_thread required"
                    )
                elif ct not in VALID_COVERAGE_THREADS:
                    errors.append(
                        f"obligations_proposed[{i}]: invalid coverage_thread {ct!r}"
                    )
                personas = hints.get("personas") or []
                if personas and not isinstance(personas, list):
                    errors.append(
                        f"obligations_proposed[{i}]: downstream_hints.personas must be array"
                    )
                else:
                    for p in personas:
                        if p not in VALID_PERSONAS:
                            errors.append(
                                f"obligations_proposed[{i}]: invalid persona {p!r}"
                            )
                if hints.get("needs_dual_account_contrast") is True:
                    cvp = obl.get("config_vs_position")
                    if cvp != "account_group_assignment":
                        errors.append(
                            f"obligations_proposed[{i}] ({obl.get('id')}): "
                            "needs_dual_account_contrast requires "
                            "config_vs_position account_group_assignment"
                        )

        if is_deferral and not metrics_short_circuit:
            if not isinstance(hints, dict) or hints.get("coverage_thread") != "deferral_only":
                errors.append(
                    f"obligations_proposed[{i}] ({obl.get('id')}): "
                    "deferral must have downstream_hints.coverage_thread deferral_only"
                )
            if not str(obl.get("deferral_reason") or "").strip():
                errors.append(
                    f"obligations_proposed[{i}] ({obl.get('id')}): "
                    "deferral_reason required (--strict-principal)"
                )

    for i, row in enumerate(topo.get("delivery_notes") or []):
        if not isinstance(row, dict):
            continue
        st = row.get("status")
        if st not in ("known_fail", "pending_verification", "excluded"):
            continue
        linked_o = row.get("linked_obligation_ids") or []
        linked_s = row.get("linked_surface_ids") or []
        if not linked_o and not linked_s:
            errors.append(
                f"delivery_notes[{i}] ({row.get('id')}): "
                "linked_obligation_ids or linked_surface_ids required "
                f"for status {st!r} (--strict-principal)"
            )

    archetype = _archetype_value(ref)
    surfaces = topo.get("jira_scenario_surfaces") or []

    if archetype in ("widget_ui", "mixed"):
        if _jira_has_scenario_block(ref) and len(surfaces) > 0 and _has_setup_keywords(ref):
            if "environment_setup" not in thread_coverage and not has_env_setup_obl:
                errors.append(
                    "widget_ui: environment_setup thread or environment_setup "
                    "obligation required when setup keywords present"
                )
        if has_invariant_primary and "invariants" not in thread_coverage:
            errors.append(
                "widget_ui: invariants principal_coverage_thread required "
                "when invariant primary_candidate present"
            )
        if _has_backup_eod_keywords(ref) and "backup_eod" not in thread_coverage:
            errors.append(
                "widget_ui: backup_eod principal_coverage_thread required "
                "when backup/EOD keywords present"
            )

    return errors


def verify_topology(ref: dict[str, Any], strict: bool) -> list[str]:
    errors: list[str] = []
    arch = ref.get("epic_archetype")
    topo = ref.get("verification_topology")

    if not strict and arch is None and topo is None:
        return []

    if strict:
        if not isinstance(arch, dict):
            errors.append("epic_archetype must be an object (--strict-topology)")
            arch = {}
        if topo is None:
            errors.append("verification_topology must be present (--strict-topology)")
            topo = {}
        elif not isinstance(topo, dict):
            errors.append("verification_topology must be an object")
            topo = {}

    if isinstance(arch, dict) and arch:
        val = arch.get("value")
        if val not in VALID_ARCHETYPES:
            errors.append(f"epic_archetype.value invalid: {val!r}")
        src = arch.get("source")
        if src and src not in VALID_ARCHETYPE_SOURCES:
            errors.append(f"epic_archetype.source invalid: {src!r}")
        if strict and not str(arch.get("evidence") or "").strip():
            errors.append("epic_archetype.evidence required (--strict-topology)")

    if not isinstance(topo, dict):
        return errors

    surfaces = topo.get("jira_scenario_surfaces")
    if surfaces is None and strict:
        errors.append("verification_topology.jira_scenario_surfaces missing")
    elif surfaces is not None:
        if not isinstance(surfaces, list):
            errors.append("jira_scenario_surfaces must be an array")
        else:
            seen_jss: set[str] = set()
            for i, row in enumerate(surfaces):
                if not isinstance(row, dict):
                    errors.append(f"jira_scenario_surfaces[{i}]: not an object")
                    continue
                rid = row.get("id")
                if not rid:
                    errors.append(f"jira_scenario_surfaces[{i}]: missing id")
                elif str(rid) in seen_jss:
                    errors.append(f"jira_scenario_surfaces: duplicate id {rid!r}")
                else:
                    seen_jss.add(str(rid))
                shell = row.get("shell")
                if shell and shell not in VALID_SHELLS:
                    errors.append(f"jira_scenario_surfaces[{i}]: invalid shell {shell!r}")
                if strict and not str(row.get("source_quote") or "").strip():
                    errors.append(f"jira_scenario_surfaces[{i}]: missing source_quote")

    roles = topo.get("shell_roles")
    if roles is not None:
        if not isinstance(roles, dict):
            errors.append("shell_roles must be an object")
        else:
            for key, row in roles.items():
                if key.startswith("_"):
                    continue
                if not isinstance(row, dict):
                    errors.append(f"shell_roles.{key}: not an object")
                    continue
                st = row.get("status")
                if st and st not in VALID_SHELL_ROLE_STATUS:
                    errors.append(f"shell_roles.{key}: invalid status {st!r}")

    rules = topo.get("pricing_oracle_rules")
    if rules is None and strict:
        errors.append("verification_topology.pricing_oracle_rules missing")
    elif rules is not None:
        if not isinstance(rules, list):
            errors.append("pricing_oracle_rules must be an array")
        else:
            seen_por: set[str] = set()
            for i, row in enumerate(rules):
                if not isinstance(row, dict):
                    errors.append(f"pricing_oracle_rules[{i}]: not an object")
                    continue
                rid = row.get("id")
                if not rid:
                    errors.append(f"pricing_oracle_rules[{i}]: missing id")
                elif str(rid) in seen_por:
                    errors.append(f"pricing_oracle_rules: duplicate id {rid!r}")
                else:
                    seen_por.add(str(rid))
                rule = row.get("oracle_rule")
                if rule not in VALID_ORACLE_RULES:
                    errors.append(f"pricing_oracle_rules[{i}]: invalid oracle_rule {rule!r}")
                vc = row.get("volume_control")
                if vc and vc not in VALID_VOLUME_CONTROL:
                    errors.append(
                        f"pricing_oracle_rules[{i}]: invalid volume_control {vc!r}"
                    )

    for arr_name in ("delivery_notes", "platform_reuse_candidates"):
        arr = topo.get(arr_name)
        if arr is None:
            if strict:
                errors.append(f"verification_topology.{arr_name} missing")
            continue
        if not isinstance(arr, list):
            errors.append(f"{arr_name} must be an array")
            continue
        for i, row in enumerate(arr):
            if not isinstance(row, dict):
                errors.append(f"{arr_name}[{i}]: not an object")
                continue
            if arr_name == "delivery_notes":
                st = row.get("status")
                if st not in VALID_DELIVERY_STATUS:
                    errors.append(f"delivery_notes[{i}]: invalid status {st!r}")
                src = row.get("source")
                if src and src not in VALID_DELIVERY_SOURCE:
                    errors.append(f"delivery_notes[{i}]: invalid source {src!r}")
                if st in ("known_fail", "excluded") and not str(
                    row.get("evidence") or ""
                ).strip():
                    errors.append(
                        f"delivery_notes[{i}]: evidence required for {st}"
                    )
            if arr_name == "platform_reuse_candidates":
                if row.get("binding") != "suggestion_only":
                    errors.append(
                        f"platform_reuse_candidates[{i}]: binding must be suggestion_only"
                    )
                conf = row.get("confidence")
                if conf and conf not in VALID_REUSE_CONFIDENCE:
                    errors.append(
                        f"platform_reuse_candidates[{i}]: invalid confidence {conf!r}"
                    )
                pattern = str(row.get("suggested_crtqa_pattern") or "")
                if CRTQA_KEY_RE.search(pattern):
                    errors.append(
                        f"platform_reuse_candidates[{i}]: must not contain CRTQA keys"
                    )

    if strict and isinstance(arch, dict):
        archetype = arch.get("value")
        if archetype in ("widget_ui", "mixed"):
            surf_list = surfaces if isinstance(surfaces, list) else []
            if _jira_has_scenario_block(ref) and len(surf_list) < 1:
                errors.append(
                    "widget_ui/mixed: jira_scenario_surfaces must be non-empty "
                    "when scenarios present"
                )
            if _epic_has_quote_keywords(ref) and isinstance(rules, list) and len(rules) < 1:
                errors.append(
                    "widget_ui/mixed: pricing_oracle_rules must be non-empty "
                    "when quote/tier keywords present"
                )

    return errors


def verify_scenario_inventory(ref: dict[str, Any]) -> list[str]:
    """Draft+truth breadth inventory per docs/epic-prep-scenario-contract.json."""
    errors: list[str] = []
    topo = ref.get("verification_topology")
    if not isinstance(topo, dict):
        return ["verification_topology missing for scenario inventory"]

    rows = topo.get("scenario_capability_rows")
    if not isinstance(rows, list):
        return ["verification_topology.scenario_capability_rows must be an array"]

    jss = topo.get("jira_scenario_surfaces") or []
    reuse = topo.get("platform_reuse_candidates") or []
    arch_val = (ref.get("epic_archetype") or {}).get("value")

    seen_ids: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"scenario_capability_rows[{i}]: not an object")
            continue
        rid = row.get("id")
        if not rid or not str(rid).startswith("scr-"):
            errors.append(f"scenario_capability_rows[{i}]: id must be scr-###")
        elif str(rid) in seen_ids:
            errors.append(f"duplicate scenario_capability_rows id {rid!r}")
        else:
            seen_ids.add(str(rid))
        prom = row.get("promotion")
        if prom not in VALID_SCENARIO_PROMOTION:
            errors.append(
                f"scenario_capability_rows[{i}]: invalid promotion {prom!r}"
            )
        kind = row.get("capability_kind")
        if kind not in VALID_CAPABILITY_KIND:
            errors.append(
                f"scenario_capability_rows[{i}]: invalid capability_kind {kind!r}"
            )
        if not row.get("source_quote") or not str(row.get("source_quote")).strip():
            errors.append(f"scenario_capability_rows[{i}]: missing source_quote")
        rkeys = row.get("linked_requirement_keys") or []
        if not isinstance(rkeys, list) or not rkeys:
            errors.append(
                f"scenario_capability_rows[{i}]: linked_requirement_keys required"
            )

    if arch_val == "widget_ui" and isinstance(jss, list) and len(jss) >= 1:
        if len(rows) < len(jss):
            errors.append(
                f"scenario_capability_rows count {len(rows)} < "
                f"jira_scenario_surfaces {len(jss)}"
            )

    for i, prc in enumerate(reuse):
        if not isinstance(prc, dict):
            continue
        if prc.get("binding") != "suggestion_only":
            continue
        prc_id = prc.get("id")
        if not prc_id:
            continue
        matched = any(
            isinstance(r, dict)
            and r.get("platform_reuse_id") == prc_id
            and r.get("capability_kind") == "platform_invariant"
            for r in rows
        )
        if not matched:
            errors.append(
                f"platform_reuse_candidates[{i}] {prc_id}: missing "
                "scenario_capability_rows platform_invariant row"
            )

    return errors


def _snippet_has_parameter_table(snippet: str) -> bool:
    return len(PARAM_TABLE_RE.findall(snippet)) >= 2


def _count_snippet_observables(snippet: str) -> int:
    """Distinct parameter-like tokens in snippet (observable_yield helper)."""
    found = {m.group(0).lower() for m in PARAM_TABLE_RE.finditer(snippet or "")}
    return len(found)


def _is_availability_obligation(obl: dict[str, Any]) -> bool:
    text = " ".join(
        [
            str(obl.get("assertion_fragment") or ""),
            str(obl.get("statement") or ""),
        ]
    ).lower()
    patterns = (
        "card is available",
        "details card is available",
        "trade card is available",
        "is present and visible",
        "not omitted",
    )
    return any(p in text for p in patterns)


def verify_widget_ui_atomic_obligations(ref: dict[str, Any]) -> list[str]:
    """widget_ui: multi-parameter snippets need field-level obligations."""
    errors: list[str] = []
    arch = (ref.get("epic_archetype") or {}).get("value")
    if arch not in ("widget_ui", "mixed"):
        return errors

    req_by_key: dict[str, dict[str, Any]] = {}
    for row in ref.get("requirements") or []:
        if isinstance(row, dict) and row.get("key"):
            req_by_key[str(row["key"])] = row

    obls_by_key: dict[str, list[dict[str, Any]]] = {}
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        for rk in obl.get("requirement_keys") or []:
            obls_by_key.setdefault(str(rk), []).append(obl)

    for key, row in req_by_key.items():
        status = row.get("snippet_status")
        snippet = str(row.get("snippet_text") or "")
        if status != "ok":
            continue

        try:
            yield_n = int(row.get("observable_yield")) if row.get("observable_yield") is not None else None
        except (TypeError, ValueError):
            yield_n = None
        if yield_n is None:
            # Backfill from snippet when agent omitted the field.
            inferred = _count_snippet_observables(snippet)
            yield_n = inferred if inferred >= 2 else 0
            if inferred >= 2 and row.get("observable_yield") is None:
                # Soft signal: prefer explicit field, but still enforce via inferred count.
                pass

        if yield_n < 2 and not _snippet_has_parameter_table(snippet):
            continue

        min_needed = max(yield_n, 2) if _snippet_has_parameter_table(snippet) or yield_n >= 2 else 0
        if min_needed < 2:
            continue

        obls = obls_by_key.get(key) or []
        primary = [
            o
            for o in obls
            if o.get("disposition") == "primary_candidate"
            and o.get("kind") not in ("explicit_deferral",)
            and o.get("kind") != "environment_setup"
            and not _is_availability_obligation(o)
        ]
        if len(primary) < min_needed:
            errors.append(
                f"observable_yield_shortfall: {key} needs >= {min_needed} "
                f"primary_candidate field obligation(s) "
                f"(observable_yield={yield_n}), got {len(primary)}"
            )
        elif len(primary) < 2 and _snippet_has_parameter_table(snippet):
            errors.append(
                f"requirement_tag_only_obligation: {key} snippet has parameter table "
                f"but only {len(primary)} primary_candidate obligation(s)"
            )
        for obl in primary:
            frag = str(obl.get("assertion_fragment") or "").strip()
            if not frag:
                errors.append(
                    f"obligation {obl.get('id')}: assertion_fragment required for "
                    f"widget_ui field obligation ({key})"
                )

    return errors


def verify_ref(
    ref: dict[str, Any],
    kinds_doc: dict[str, Any],
    strict_topology: bool,
    strict_principal: bool,
    *,
    ci_strict: bool = False,
) -> list[str]:
    errors: list[str] = []
    schema_v = int(ref.get("schema_version") or 0)
    if schema_v < 4:
        errors.append(f"schema_version must be >= 4 (got {schema_v})")

    valid_kinds = set(kinds_doc.get("kinds") or VALID_KINDS)
    linked = _jira_linked_keys(ref)
    defer_ok = _deferral_accepted(ref)
    block_deferral = _ci_strict_blocks_deferral(ci_strict=ci_strict)

    for row in ref.get("requirements") or []:
        if not isinstance(row, dict):
            continue
        key = str(row.get("key") or "")
        if key not in linked:
            continue
        status = row.get("snippet_status")
        if status == "ok":
            continue
        reason = str(row.get("snippet_failure_reason") or "").strip()
        if defer_ok and not block_deferral:
            continue
        if defer_ok and block_deferral:
            # Prefer naming recoverable reasons; still fail all non-ok under ci-strict.
            tag = reason if reason in RECOVERABLE_SNIPPET_FAILURES else (reason or "unknown")
            errors.append(
                f"requirements {key}: snippet_status {status!r} "
                f"(ci-strict rejects deferral_accepted for {tag}; "
                "set ALLOW_SNIPPET_DEFERRAL=yes to override)"
            )
            continue
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

    errors.extend(verify_topology(ref, strict_topology))
    errors.extend(verify_principal(ref, strict_principal))
    errors.extend(verify_widget_ui_atomic_obligations(ref))
    if (ref.get("verification_topology") or {}).get("scenario_capability_rows") is not None:
        errors.extend(verify_scenario_inventory(ref))
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
            (
                o.get("statement")
                for o in obligations
                if isinstance(o, dict) and o.get("id") == pid
            ),
            "",
        )
        if not stmt or len(str(stmt)) < 10:
            errors.append(f"reconcile: primary_candidate {pid} has weak statement")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify EPIC-PREP -ref.json")
    ap.add_argument(
        "--mode",
        choices=("ref", "reconcile", "topology", "principal", "scenario"),
        required=True,
    )
    ap.add_argument("--ref", type=Path, required=True)
    ap.add_argument(
        "--strict-topology",
        action="store_true",
        help="Require epic_archetype and verification_topology on emit",
    )
    ap.add_argument(
        "--strict-principal",
        action="store_true",
        help="Require principal hints (downstream_hints, threads, focus) on emit",
    )
    ap.add_argument(
        "--ci-strict",
        action="store_true",
        help="Reject self-issued deferral_accepted for failed snippets "
        "(TeamCity / CORNER_CI=1). Override with ALLOW_SNIPPET_DEFERRAL=yes.",
    )
    args = ap.parse_args()

    ref = _load_json(args.ref.resolve())
    if ref is None:
        print(f"cannot read ref: {args.ref}", file=sys.stderr)
        return 2

    kinds_doc = _load_json(KINDS_PATH) or {}
    _load_json(TOPOLOGY_PATH)
    _load_json(PRINCIPAL_PATH)

    _load_json(SCENARIO_PATH)

    strict_topo = args.strict_topology or args.mode == "topology"
    strict_princ = args.strict_principal or args.mode == "principal"
    ci_strict = bool(args.ci_strict) or (
        (os.environ.get("CORNER_CI") or "").strip() in ("1", "true", "yes")
    )

    if args.mode == "scenario":
        errors = verify_scenario_inventory(ref)
    elif args.mode == "topology":
        errors = verify_topology(ref, strict=True)
    elif args.mode == "principal":
        errors = verify_principal(ref, strict=True)
    elif args.mode == "ref":
        errors = verify_ref(
            ref, kinds_doc, strict_topo, strict_princ, ci_strict=ci_strict
        )
    else:
        errors = verify_reconcile(ref)
        errors = (
            verify_ref(ref, kinds_doc, strict_topo, strict_princ, ci_strict=ci_strict)
            + errors
        )

    if errors:
        print(f"epic_prep_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_obl = len(ref.get("obligations_proposed") or [])
    arch = (ref.get("epic_archetype") or {}).get("value", "n/a")
    print(f"OK epic_prep_verify mode={args.mode} obligations={n_obl} archetype={arch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
