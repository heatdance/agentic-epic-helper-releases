#!/usr/bin/env python3
"""
Verify TEST-PREP verification plan (temp) and -tests.json drafts.

Examples:
  python automation/tools/test_prep_verify.py --mode plan \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --plan epics/CRT-639/temp/test-prep-plan.json

  python automation/tools/test_prep_verify.py --mode draft \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --tests epics/CRT-639/CRT-639-tests.json \\
    --bundle-id tb-002 \\
    --plan epics/CRT-639/temp/test-prep-plan.json

  python automation/tools/test_prep_verify.py --mode tests \\
    --coverage epics/CRT-639/CRT-639-coverage.json \\
    --tests epics/CRT-639/CRT-639-tests.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "docs" / "test-verification-classes.json"
PROFILES_PATH = REPO_ROOT / "docs" / "test-prep-draft-profiles.json"
TBD_CONTRACT_PATH = REPO_ROOT / "docs" / "test-prep-tbd-contract.json"
TOPOLOGY_PATH = REPO_ROOT / "docs" / "test-prep-topology-contract.json"
PREP_PRINCIPAL_CONTRACT_PATH = REPO_ROOT / "docs" / "test-prep-principal-contract.json"
SCENARIO_INTENT_CONTRACT_PATH = REPO_ROOT / "docs" / "test-prep-scenario-intent-contract.json"
LADDER_PATH = REPO_ROOT / "docs" / "exploration-depth-ladder.json"
DEPTH_ORDER = ["smoke", "discover_probe", "precon_drill", "prep_verify_view"]
FE_SURFACES = frozenset({"dxtrade5", "webbroker", "adaptive", "chrome"})

TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
CRTQA_REQUIRES_RE = re.compile(r"\[REQUIRES:\s*CRTQA-", re.I)
YOGI_TAG_RE = re.compile(r"#req-|/requirements/|CRT-\d{3,5}", re.I)
EXECUTION_TRADE_RE = re.compile(r"\bexecution\s+trade\b", re.I)
LADDER_TBD_RE = re.compile(r"\[TBD[^\]]*ladder", re.I)
PRECON_CITE_RE = re.compile(r"precon\.md|precon cluster|Account & system configuration", re.I)
NUMBERED_LINE_RE = re.compile(r"^\s*\d+\.\s+", re.M)
POSITION_METRICS_RE = re.compile(r"show\s+position_metrics_from_publisher", re.I)
PLACEHOLDER_RE = re.compile(r"<[a-z_]+>", re.I)
ORACLE_TBD_RE = re.compile(r"\[oracle:TBD\]", re.I)
PLATFORM_REUSE_HEADING = "## Platform reuse candidates (verify in Jira)"
MACHINE_LINE_RE = re.compile(r"^\s*>\s*(Discover|Discovery):", re.M | re.I)


def verify_tests_md_hygiene(md_path: Path | None) -> list[str]:
    errors: list[str] = []
    if md_path is None or not md_path.is_file():
        return errors
    try:
        md_body = md_path.read_text(encoding="utf-8")
    except OSError:
        errors.append(f"cannot read tests markdown: {md_path}")
        return errors
    if PLATFORM_REUSE_HEADING in md_body:
        errors.append(
            "tests markdown must not contain platform reuse heading (JSON-only annex)"
        )
    if MACHINE_LINE_RE.search(md_body):
        errors.append(
            "tests markdown must not contain > Discover: or > Discovery: lines"
        )
    return errors

SINGLE_PAIR_CLASSES = frozenset({"stateful_ladder", "rounding_matrix"})
SINGLE_PAIR_PATTERN_REFS_DEFAULT = frozenset({"ladder_step"})


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _load_registry() -> dict[str, Any]:
    reg = _load_json(REGISTRY_PATH)
    return reg if reg else {}


def _load_profiles() -> dict[str, Any]:
    prof = _load_json(PROFILES_PATH)
    return prof if prof else {}


def _load_tbd_contract() -> dict[str, Any]:
    tbd = _load_json(TBD_CONTRACT_PATH)
    return tbd if tbd else {}


def _single_pair_pattern_refs() -> frozenset[str]:
    tbd = _load_tbd_contract()
    exp = (tbd.get("expansion_policy") or {}).get("single_pair_per_case_outline_row") or {}
    applies = exp.get("applies_when") or {}
    refs = applies.get("pattern_ref_any") or []
    if isinstance(refs, list) and refs:
        return frozenset(str(x) for x in refs)
    return SINGLE_PAIR_PATTERN_REFS_DEFAULT


def _delivery_blocked_check_ids(
    coverage: dict[str, Any],
    precon: dict[str, Any] | None,
) -> set[str]:
    blocked: set[str] = set()
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if not cid:
            continue
        if str(chk.get("delivery_status") or "").lower() in ("failed", "excluded"):
            blocked.add(str(cid))
    if precon:
        for row in precon.get("excluded_checks_with_reason") or []:
            if isinstance(row, dict) and row.get("check_id"):
                reason = str(row.get("reason") or "")
                if reason in ("delivery_blocked", "deferred_ambiguous"):
                    blocked.add(str(row["check_id"]))
    return blocked


def _pattern_substrings(pattern_key: str, command_patterns: dict[str, Any]) -> list[str]:
    lines = command_patterns.get(pattern_key) or []
    if not isinstance(lines, list):
        return []
    out: list[str] = []
    for line in lines:
        s = str(line).strip()
        if len(s) >= 12:
            out.append(s[:40].lower())
        elif s:
            out.append(s.lower())
    return out


def _verify_strict_topology(
    coverage: dict[str, Any],
    tests: dict[str, Any],
    *,
    precon: dict[str, Any] | None,
    ref: dict[str, Any] | None,
    plan: dict[str, Any] | None,
    bundle_id: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if precon is None or ref is None:
        errors.append("strict-topology: --precon and --ref required")
        return errors

    tests_sources = tests.get("sources") or {}
    precon_sources = precon.get("sources") or {}
    topology_loaded = bool(tests_sources.get("topology_loaded")) or bool(
        precon_sources.get("topology_loaded")
    )
    if not topology_loaded:
        return errors

    command_patterns = precon.get("command_patterns") or {}
    if not isinstance(command_patterns, dict):
        command_patterns = {}

    blocked = _delivery_blocked_check_ids(coverage, precon)
    primary = set(_primary_check_ids(coverage))
    excluded = _excluded_ids(tests)

    for b in tests.get("test_bundles") or []:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bundle_id") or "?")
        if bundle_id and bid != bundle_id:
            continue
        for cid in b.get("covers_check_ids") or []:
            cid = str(cid)
            if cid in blocked and cid in primary:
                errors.append(
                    f"strict-topology: delivery-blocked check {cid} in bundle {bid} "
                    "covers_check_ids"
                )

    for cid in blocked:
        if cid not in primary:
            continue
        if cid in excluded:
            continue
        gaps = tests.get("reverse_validation") or {}
        gap_ids = {
            str(g["check_id"])
            for g in (gaps.get("coverage_gaps") or [])
            if isinstance(g, dict) and g.get("check_id")
        }
        if cid not in gap_ids:
            errors.append(
                f"strict-topology: delivery/deferred check {cid} must be in "
                "reverse_validation.coverage_gaps[]"
            )

    if plan:
        for pb in plan.get("bundles") or []:
            if not isinstance(pb, dict):
                continue
            bid = str(pb.get("bundle_id") or "?")
            if bundle_id and bid != bundle_id:
                continue
            bundle = None
            for b in tests.get("test_bundles") or []:
                if isinstance(b, dict) and str(b.get("bundle_id")) == bid:
                    bundle = b
                    break
            if not bundle:
                continue
            act = _draft_section(bundle, "actions")
            outline_items: list[dict[str, Any]] = []
            for row in pb.get("verification_plan") or []:
                if not isinstance(row, dict):
                    continue
                for item in row.get("case_outline") or []:
                    if isinstance(item, dict):
                        outline_items.append(item)
            for i, item in enumerate(outline_items):
                pref = str(item.get("pattern_ref") or "")
                if not pref or pref not in _single_pair_pattern_refs():
                    continue
                subs = _pattern_substrings(pref, command_patterns)
                if not subs:
                    errors.append(
                        f"strict-topology: bundle {bid} pattern_ref {pref!r} "
                        "missing precon command_patterns key"
                    )
                    continue
                action_text = str(act[i] if i < len(act) else "").lower()
                if not action_text:
                    errors.append(
                        f"strict-topology: bundle {bid} missing action for "
                        f"pattern_ref row {pref!r}"
                    )
                    continue
                if not any(sub in action_text for sub in subs):
                    errors.append(
                        f"strict-topology: bundle {bid} action[{i}] must include "
                        f"sub-bullets from command_patterns.{pref}"
                    )

    vt = ref.get("verification_topology") or {}
    candidates = vt.get("platform_reuse_candidates") or []
    if isinstance(candidates, list) and candidates:
        annex = tests.get("platform_reuse_annex")
        if not annex or not str(annex).strip():
            errors.append(
                "strict-topology: platform_reuse_annex required when ref has "
                "platform_reuse_candidates"
            )
        elif CRTQA_KEY_RE.search(str(annex)):
            errors.append("strict-topology: CRTQA keys forbidden in platform_reuse_annex")

    return errors


def _tests_validation_log_steps(tests: dict[str, Any]) -> set[str]:
    steps: set[str] = set()
    for row in tests.get("validation_log") or []:
        if isinstance(row, dict) and row.get("step"):
            steps.add(str(row["step"]))
    return steps


def _precon_has_pc_setup(precon: dict[str, Any]) -> bool:
    for cluster in precon.get("precon_clusters") or []:
        if isinstance(cluster, dict) and str(cluster.get("id")) == "pc-setup":
            return True
    return False


def _ref_has_provision_or_personas(ref: dict[str, Any]) -> bool:
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        hints = obl.get("downstream_hints") or {}
        if not isinstance(hints, dict):
            continue
        if hints.get("needs_environment_provision") or hints.get("needs_dual_account_contrast"):
            return True
        personas = hints.get("personas") or []
        if isinstance(personas, list) and personas:
            return True
    return False


def _ref_needs_dual_account_contrast(ref: dict[str, Any]) -> bool:
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        hints = obl.get("downstream_hints") or {}
        if isinstance(hints, dict) and hints.get("needs_dual_account_contrast"):
            return True
    return False


def _deferral_keyed_check_ids(coverage: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if not cid:
            continue
        if chk.get("verification_role") == "out_of_epic" and chk.get(
            "coverage_thread"
        ) == "deferral_only":
            ids.add(str(cid))
    return ids


def _obligation_personas(ref: dict[str, Any]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        oid = obl.get("id")
        if not oid:
            continue
        hints = obl.get("downstream_hints") or {}
        personas = hints.get("personas") if isinstance(hints, dict) else None
        if isinstance(personas, list):
            out[str(oid)] = {str(p) for p in personas}
    return out


def _check_persona_map(
    ref: dict[str, Any],
    coverage: dict[str, Any],
) -> dict[str, set[str]]:
    obl_personas = _obligation_personas(ref)
    mapping: dict[str, set[str]] = {}
    for oid, row in (coverage.get("obligations_coverage") or {}).items():
        if not isinstance(row, dict):
            continue
        cid = row.get("check_id")
        if cid:
            mapping[str(cid)] = set(obl_personas.get(str(oid), set()))
    checks = _checks_by_id(coverage)
    for cid, chk in checks.items():
        if cid in mapping and mapping[cid]:
            continue
        section = str(chk.get("section") or "").lower()
        if "client area" in section or "webbroker (client)" in section:
            mapping[cid] = {"retail"}
        elif "dealer" in section or "backup prices" in section:
            mapping[cid] = {"dealer"}
    return mapping


def _personas_retail_dealer_conflict(personas_a: set[str], personas_b: set[str]) -> bool:
    if "cross_persona" in personas_a or "cross_persona" in personas_b:
        return False
    retail_a = "retail" in personas_a
    dealer_a = "dealer" in personas_a
    retail_b = "retail" in personas_b
    dealer_b = "dealer" in personas_b
    return (retail_a and dealer_b) or (dealer_a and retail_b)


def _principal_handoff_active(precon: dict[str, Any], ref: dict[str, Any]) -> bool:
    precon_sources = precon.get("sources") or {}
    if isinstance(precon_sources, dict) and precon_sources.get("principal_loaded"):
        return True
    if _precon_has_pc_setup(precon):
        return True
    return _ref_has_provision_or_personas(ref)


def _draft_text_for_tests(tests: dict[str, Any], bundle_id: str | None = None) -> str:
    parts: list[str] = []
    for b in tests.get("test_bundles") or []:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bundle_id") or "")
        if bundle_id and bid != bundle_id:
            continue
        draft = b.get("draft") or {}
        if isinstance(draft, dict):
            for key in ("preconditions", "actions", "results", "peculiarities"):
                val = draft.get(key)
                if isinstance(val, list):
                    parts.extend(str(x) for x in val)
                elif val:
                    parts.append(str(val))
    return "\n".join(parts)


def verify_strict_test_prep_principal(
    coverage: dict[str, Any],
    tests: dict[str, Any],
    *,
    precon: dict[str, Any] | None,
    ref: dict[str, Any] | None,
    bundle_id: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if precon is None or ref is None:
        errors.append("strict-principal: --precon and --ref required")
        return errors

    if not _principal_handoff_active(precon, ref):
        return errors

    tests_sources = tests.get("sources") or {}
    if not isinstance(tests_sources, dict):
        tests_sources = {}
    log_steps = _tests_validation_log_steps(tests)

    if not tests_sources.get("principal_loaded"):
        errors.append(
            "strict-principal: sources.principal_loaded must be true when principal handoff active"
        )

    if "phase1-principal" not in log_steps:
        errors.append("strict-principal: validation_log missing phase1-principal")

    if "phase8b_principal_paste" not in log_steps:
        errors.append(
            "strict-principal: validation_log missing phase8b_principal_paste"
        )

    if _precon_has_pc_setup(precon):
        setup_bundle: dict[str, Any] | None = None
        for b in tests.get("test_bundles") or []:
            if not isinstance(b, dict):
                continue
            bid = str(b.get("bundle_id") or "")
            if bundle_id and bid != bundle_id:
                continue
            refs = {str(x) for x in (b.get("precon_cluster_refs") or [])}
            if "pc-setup" in refs or bid == "tb-setup":
                setup_bundle = b
                break
        if setup_bundle is None:
            errors.append(
                "strict-principal: test_bundles missing setup row with "
                "precon_cluster_refs pc-setup (tb-setup)"
            )
        else:
            refs = {str(x) for x in (setup_bundle.get("precon_cluster_refs") or [])}
            if "pc-setup" not in refs:
                errors.append(
                    "strict-principal: setup bundle must cite precon_cluster_refs pc-setup"
                )
            covered_setup = {
                str(x) for x in (setup_bundle.get("covers_check_ids") or [])
            }
            for cid in ("chk-s1", "chk-s2"):
                if cid not in covered_setup:
                    errors.append(
                        f"strict-principal: setup bundle must cover {cid!r}"
                    )

        if _ref_needs_dual_account_contrast(ref):
            ph = precon.get("session_placeholders") or {}
            tests_ph = tests_sources.get("session_placeholders") or {}
            if not isinstance(ph, dict):
                ph = {}
            if not isinstance(tests_ph, dict):
                tests_ph = {}
            for token in ("group_key_enrg", "group_key_oppt"):
                if token not in ph:
                    errors.append(
                        f"strict-principal: precon session_placeholders missing {token!r}"
                    )
                elif token not in tests_ph:
                    errors.append(
                        f"strict-principal: sources.session_placeholders missing "
                        f"copied {token!r} from precon"
                    )
            draft_text = _draft_text_for_tests(tests, bundle_id)
            for angle in ("<group_key_enrg>", "<group_key_oppt>"):
                if angle not in draft_text:
                    errors.append(
                        f"strict-principal: draft must reference dual-account token {angle}"
                    )

        persona_map = _check_persona_map(ref, coverage)
        for b in tests.get("test_bundles") or []:
            if not isinstance(b, dict):
                continue
            bid = str(b.get("bundle_id") or "?")
            if bundle_id and bid != bundle_id:
                continue
            if bid == "tb-setup" or "pc-setup" in {
                str(x) for x in (b.get("precon_cluster_refs") or [])
            }:
                continue
            cids = [str(x) for x in (b.get("covers_check_ids") or [])]
            for i, cid_a in enumerate(cids):
                pa = persona_map.get(cid_a, set())
                for cid_b in cids[i + 1 :]:
                    pb = persona_map.get(cid_b, set())
                    if _personas_retail_dealer_conflict(pa, pb):
                        errors.append(
                            f"strict-principal: bundle {bid} mixes disjoint personas "
                            f"({cid_a} vs {cid_b}); split retail vs dealer primaries"
                        )

        if "phase8a_persona_split" not in log_steps:
            errors.append(
                "strict-principal: validation_log missing phase8a_persona_split "
                "when pc-setup persona split expected"
            )

        for b in tests.get("test_bundles") or []:
            if not isinstance(b, dict):
                continue
            bid = str(b.get("bundle_id") or "?")
            if bundle_id and bid != bundle_id:
                continue
            refs = {str(x) for x in (b.get("precon_cluster_refs") or [])}
            if "pc-setup" in refs or bid == "tb-setup":
                continue
            pre = _draft_section(b, "preconditions")
            if not pre:
                errors.append(
                    f"strict-principal: bundle {bid} missing preconditions for pc-setup ordering"
                )
                continue
            first_pre = str(pre[0]).lower()
            if "pc-setup" not in first_pre and "quote publication" not in first_pre:
                errors.append(
                    f"strict-principal: bundle {bid} first precondition must cite "
                    "pc-setup completion before pc-001"
                )

    deferral_ids = _deferral_keyed_check_ids(coverage)
    if deferral_ids:
        excluded = _excluded_ids(tests)
        covered: set[str] = set()
        for b in tests.get("test_bundles") or []:
            if isinstance(b, dict):
                for cid in b.get("covers_check_ids") or []:
                    covered.add(str(cid))
        gap_ids = {
            str(g["check_id"])
            for g in (tests.get("reverse_validation") or {}).get("coverage_gaps") or []
            if isinstance(g, dict) and g.get("check_id")
        }
        for cid in deferral_ids:
            if cid in covered:
                errors.append(
                    f"strict-principal: deferral-keyed check {cid} in "
                    "test_bundles covers_check_ids"
                )
            if cid not in excluded:
                errors.append(
                    f"strict-principal: deferral-keyed check {cid} missing from "
                    "excluded_checks_with_reason"
                )
            if cid not in gap_ids:
                errors.append(
                    f"strict-principal: deferral-keyed check {cid} missing from "
                    "reverse_validation.coverage_gaps[]"
                )

    return errors


def _plan_profile(plan: dict[str, Any], tests: dict[str, Any] | None = None) -> str:
    if isinstance(plan.get("draft_profile"), str):
        return str(plan["draft_profile"])
    if tests:
        src = tests.get("sources") or {}
        if isinstance(src, dict) and src.get("draft_profile"):
            return str(src["draft_profile"])
    prof = _load_profiles()
    return str(prof.get("default_profile") or "crtqa_outline")


def _min_case_count(
    verification_class: str,
    calculation_contract: str | None,
    reg: dict[str, Any],
    profiles: dict[str, Any],
) -> int:
    cc = str(calculation_contract) if calculation_contract else None
    fallback: int | None = None
    for row in profiles.get("min_case_count_matrix") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("verification_class")) != verification_class:
            continue
        row_cc = row.get("calculation_contract")
        if row_cc is not None and cc is not None and str(row_cc) == cc:
            return int(row.get("min_case_count") or 2)
        if row_cc is None:
            fallback = int(row.get("min_case_count") or 2)
    if fallback is not None:
        return fallback
    vc = (reg.get("verification_classes") or {}).get(verification_class) or {}
    if isinstance(vc, dict) and vc.get("default_min_case_count") is not None:
        return int(vc["default_min_case_count"])
    return int(profiles.get("default_min_case_count") or reg.get("default_min_case_count") or 2)


def _case_outline_for_check(plan_row: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in plan_row.get("case_outline") or []:
        if isinstance(item, dict):
            out.append(item)
    return out


def _normalize_action_line(line: str) -> str:
    return re.sub(r"\s+", " ", str(line).strip()).lower()


def _bundle_plan_rows(plan: dict[str, Any], bundle_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pb in plan.get("bundles") or []:
        if not isinstance(pb, dict) or str(pb.get("bundle_id")) != bundle_id:
            continue
        for row in pb.get("verification_plan") or []:
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _bundle_case_outline_count(plan: dict[str, Any], bundle_id: str) -> int:
    total = 0
    for row in _bundle_plan_rows(plan, bundle_id):
        total += len(_case_outline_for_check(row))
    return total


def _bundle_requires_single_pair(plan: dict[str, Any], bundle_id: str) -> bool:
    for row in _bundle_plan_rows(plan, bundle_id):
        if str(row.get("verification_class") or "") in SINGLE_PAIR_CLASSES:
            return True
        for item in _case_outline_for_check(row):
            if str(item.get("pattern_ref") or "") in _single_pair_pattern_refs():
                return True
    return False


def _verify_outline_cardinality(
    act: list[str],
    res: list[str],
    plan: dict[str, Any],
    bundle_id: str,
) -> list[str]:
    errors: list[str] = []
    if not _bundle_requires_single_pair(plan, bundle_id):
        return errors
    expected = _bundle_case_outline_count(plan, bundle_id)
    if expected <= 0:
        return errors
    if len(act) != expected:
        errors.append(
            f"bundle {bundle_id}: actions count {len(act)} != case_outline rows {expected} "
            "(single_pair_per_case_outline_row; ladder_step lines are sub-bullets, not separate pairs)"
        )
    if len(res) != expected:
        errors.append(
            f"bundle {bundle_id}: results count {len(res)} != case_outline rows {expected}"
        )
    return errors


def _verify_no_duplicate_actions(actions: list[str], bundle_id: str) -> list[str]:
    errors: list[str] = []
    if len(actions) < 2:
        return errors
    normalized = [_normalize_action_line(a) for a in actions]
    unique = set(normalized)
    if len(unique) < len(actions):
        errors.append(
            f"bundle {bundle_id}: duplicate action lines detected "
            f"({len(actions)} actions, {len(unique)} unique); expand one pair per case_outline row"
        )
    return errors


def _rule_matches(
    chk: dict[str, Any],
    rule: dict[str, Any],
    plan_row: dict[str, Any] | None = None,
) -> bool:
    match = rule.get("match") or {}
    if match.get("fallback"):
        return True

    scenario = str(chk.get("scenario_line") or "")
    section = str(chk.get("section") or "")
    cc = str(chk.get("calculation_contract") or "")

    cc_rule = match.get("calculation_contract")
    if cc_rule is not None and cc == str(cc_rule):
        return True

    scenario_pats = list(match.get("scenario_regex_any") or [])
    section_pats = list(match.get("section_regex_any") or [])
    surfaces_req = list(match.get("surfaces_any") or [])

    scenario_hit = bool(scenario_pats) and any(
        re.search(p, scenario, re.I) for p in scenario_pats
    )
    section_hit = bool(section_pats) and any(re.search(p, section, re.I) for p in section_pats)

    if scenario_pats and section_pats:
        matched = scenario_hit or section_hit
    elif scenario_pats:
        matched = scenario_hit
    elif section_pats:
        matched = section_hit
    else:
        matched = False

    if not matched:
        return False

    if surfaces_req:
        obs: list[str] = []
        if plan_row:
            obs.extend(str(s).lower() for s in (plan_row.get("observation_surfaces") or []))
        combined = f"{scenario} {section}".lower()
        return any(s.lower() in obs or s.lower() in combined for s in surfaces_req)

    return True


def _expected_verification_class(
    chk: dict[str, Any],
    reg: dict[str, Any],
    plan_row: dict[str, Any] | None = None,
) -> tuple[str, int]:
    machine = reg.get("selection_rules_machine") or []
    rules = [r for r in machine if isinstance(r, dict)]
    rules.sort(key=lambda r: int(r.get("priority") or 999))
    for rule in rules:
        if _rule_matches(chk, rule, plan_row):
            return str(rule.get("class") or "journey_smoke"), int(rule.get("priority") or 99)
    return "journey_smoke", 99


def _forbidden_tbd_errors(text: str, prefix: str) -> list[str]:
    errors: list[str] = []
    contract = _load_tbd_contract()
    for rule in contract.get("tbd_forbidden_patterns") or []:
        if not isinstance(rule, dict):
            continue
        pat = rule.get("regex")
        if not pat:
            continue
        try:
            if re.search(str(pat), text, re.I):
                errors.append(f"{prefix}: {rule.get('message') or rule.get('id')}")
        except re.error:
            continue
    return errors


def _load_ladder() -> dict[str, Any]:
    reg = _load_json(LADDER_PATH)
    return reg if reg else {}


def _depth_rank(level: str | None) -> int:
    if not level:
        return -1
    try:
        return DEPTH_ORDER.index(str(level))
    except ValueError:
        return -1


def _precon_widgets_by_surface(precon: dict[str, Any] | None) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    if not precon:
        return out
    for cluster in precon.get("precon_clusters") or []:
        if not isinstance(cluster, dict):
            continue
        for log in cluster.get("exploration_log") or []:
            if not isinstance(log, dict):
                continue
            if _depth_rank(str(log.get("depth_level"))) < _depth_rank("precon_drill"):
                continue
            surf = str(log.get("surface") or "").lower()
            if surf == "chrome":
                surf = "dxtrade5"
            out.setdefault(surf, set())
            for w in log.get("widgets_seen") or []:
                out[surf].add(str(w))
    return out


def _registry_classes(reg: dict[str, Any]) -> frozenset[str]:
    vc = reg.get("verification_classes") or {}
    if isinstance(vc, dict):
        return frozenset(str(k) for k in vc.keys())
    return frozenset()


def _primary_check_ids(coverage: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if not cid:
            continue
        role = chk.get("verification_role")
        if role == "primary" or role is None:
            ids.append(str(cid))
    return sorted(set(ids))


def _load_scenario_intent_patterns() -> list[re.Pattern[str]]:
    if not SCENARIO_INTENT_CONTRACT_PATH.is_file():
        return []
    doc = _load_json(SCENARIO_INTENT_CONTRACT_PATH) or {}
    raw = doc.get("forbidden_ui_patterns") or []
    out: list[re.Pattern[str]] = []
    for p in raw:
        try:
            out.append(re.compile(str(p), re.I))
        except re.error:
            continue
    return out


def _checks_by_id_cov(coverage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(c["id"]): c
        for c in (coverage.get("checks") or [])
        if isinstance(c, dict) and c.get("id")
    }


def _primary_check_ids_cov(coverage: dict[str, Any]) -> list[str]:
    return [
        str(c["id"])
        for c in (coverage.get("checks") or [])
        if isinstance(c, dict)
        and c.get("id")
        and c.get("verification_role", "primary") == "primary"
    ]


def verify_scenario_intent(
    coverage: dict[str, Any],
    tests: dict[str, Any],
) -> list[str]:
    """scenario_intent profile per docs/test-prep-scenario-intent-contract.json."""
    errors: list[str] = []
    sources_cov = coverage.get("sources") if isinstance(coverage.get("sources"), dict) else {}
    if not sources_cov.get("coverage_frozen_at"):
        errors.append("coverage.sources.coverage_frozen_at required for scenario_intent")

    groups = coverage.get("scenario_groups")
    if not isinstance(groups, list) or not groups:
        errors.append("coverage.scenario_groups[] required for scenario_intent")
        return errors

    src_tests = tests.get("sources") if isinstance(tests.get("sources"), dict) else {}
    profile = src_tests.get("draft_profile")
    if profile and profile != "scenario_intent":
        errors.append(f"sources.draft_profile must be scenario_intent (got {profile!r})")

    group_ids = {str(g.get("group_id")) for g in groups if isinstance(g, dict) and g.get("group_id")}
    group_checks: dict[str, set[str]] = {}
    for g in groups:
        if not isinstance(g, dict):
            continue
        gid = str(g.get("group_id") or "")
        group_checks[gid] = {str(x) for x in (g.get("check_ids") or [])}

    excluded = {
        str(r.get("check_id"))
        for r in (tests.get("excluded_checks_with_reason") or [])
        if isinstance(r, dict) and r.get("check_id")
    }

    bundles = tests.get("test_bundles") or []
    bundle_group_refs: set[str] = set()
    covered_in_bundles: set[str] = set()
    forbidden = _load_scenario_intent_patterns()
    checks_by_id = _checks_by_id_cov(coverage)

    for i, b in enumerate(bundles):
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bundle_id") or f"bundle[{i}]")
        covers = {str(x) for x in (b.get("covers_check_ids") or [])}
        covered_in_bundles |= covers
        gref = b.get("scenario_group_ref")
        if gref:
            gref_s = str(gref)
            bundle_group_refs.add(gref_s)
            expected = group_checks.get(gref_s, set()) - excluded
            if covers != expected and expected:
                missing = expected - covers
                extra = covers - expected
                if missing or extra:
                    errors.append(
                        f"{bid}: covers_check_ids mismatch vs scenario_group {gref_s} "
                        f"(missing={sorted(missing)} extra={sorted(extra)})"
                    )

        draft = b.get("draft") or {}
        actions = draft.get("actions") or []
        results = draft.get("results") or []
        if actions and results and len(actions) != len(results):
            errors.append(f"{bid}: actions/results count mismatch")

        for j, action in enumerate(actions):
            text = str(action)
            if any(
                checks_by_id.get(cid, {}).get("grounding_certainty") == "observed"
                for cid in covers
            ):
                continue
            for pat in forbidden:
                if pat.search(text):
                    errors.append(
                        f"{bid} action[{j}]: forbidden UI/harness pattern without observed certainty"
                    )
                    break

        for j, result in enumerate(results):
            rs = str(result)
            if not re.search(r"\[CRT-\d+\]", rs):
                errors.append(f"{bid} result[{j}]: missing [CRT-####] requirement tag")

        for cid in covers:
            if cid in excluded:
                errors.append(f"{bid}: covers excluded check {cid}")

    if bundle_group_refs != group_ids:
        missing_g = group_ids - bundle_group_refs
        extra_g = bundle_group_refs - group_ids
        if missing_g:
            errors.append(f"missing bundles for scenario_groups: {sorted(missing_g)}")
        if extra_g:
            errors.append(f"unknown scenario_group_ref on bundles: {sorted(extra_g)}")

    primary_ids = set(_primary_check_ids_cov(coverage))
    accountable = covered_in_bundles | excluded
    missing_primary = primary_ids - accountable
    if missing_primary:
        errors.append(
            f"primary checks not in bundles or excluded: {sorted(missing_primary)}"
        )

    if not tests.get("shared_preconditions") and bundles:
        errors.append("shared_preconditions[] recommended for scenario_intent emit")

    return errors


def verify_draft_truth_test_prep(
    coverage: dict[str, Any],
    tests: dict[str, Any],
) -> list[str]:
    """Draft+truth test-prep: frozen coverage; bundles reference existing checks only."""
    errors: list[str] = []
    sources = coverage.get("sources") if isinstance(coverage.get("sources"), dict) else {}
    if not sources.get("coverage_frozen_at"):
        errors.append(
            "coverage.sources.coverage_frozen_at required for draft_truth test_prep"
        )
    if not isinstance(coverage.get("scenario_groups"), list):
        errors.append("coverage.scenario_groups[] required for draft_truth test_prep")

    valid_ids = set(_primary_check_ids(coverage)) | _excluded_ids(tests)
    for i, b in enumerate(tests.get("test_bundles") or []):
        if not isinstance(b, dict):
            continue
        for cid in b.get("covers_check_ids") or []:
            if str(cid) not in valid_ids:
                errors.append(
                    f"test_bundles[{i}]: covers_check_ids {cid!r} not in coverage checks"
                )

    return errors


def _checks_by_id(coverage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for chk in coverage.get("checks") or []:
        if isinstance(chk, dict) and chk.get("id"):
            out[str(chk["id"])] = chk
    return out


def _excluded_ids(tests: dict[str, Any]) -> set[str]:
    ex: set[str] = set()
    for row in tests.get("excluded_checks_with_reason") or []:
        if isinstance(row, dict) and row.get("check_id"):
            ex.add(str(row["check_id"]))
    return ex


def _walk_strings(obj: Any, path: str = "$", skip_keys: frozenset[str] | None = None) -> list[tuple[str, str]]:
    skip = skip_keys or frozenset()
    found: list[tuple[str, str]] = []
    if isinstance(obj, str):
        found.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_") or k in skip:
                continue
            found.extend(_walk_strings(v, f"{path}.{k}", skip_keys))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(_walk_strings(v, f"{path}[{i}]", skip_keys))
    return found


def verify_plan(
    coverage: dict[str, Any],
    plan: dict[str, Any],
    *,
    excluded: set[str] | None = None,
    tests: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    reg = _load_registry()
    profiles = _load_profiles()
    valid_classes = _registry_classes(reg)
    profile = _plan_profile(plan, tests)
    checks_map = _checks_by_id(coverage)

    primary = _primary_check_ids(coverage)
    exc = excluded or set()
    in_scope = [c for c in primary if c not in exc]

    bundles = plan.get("bundles") or []
    if not isinstance(bundles, list) or not bundles:
        errors.append("plan: bundles[] must be non-empty")
        return errors

    planned_checks: dict[str, list[str]] = {}
    for b in bundles:
        if not isinstance(b, dict):
            continue
        bid = b.get("bundle_id")
        if not bid:
            errors.append("plan: bundle missing bundle_id")
            continue
        for row in b.get("verification_plan") or []:
            if not isinstance(row, dict):
                continue
            cid = row.get("check_id")
            if not cid:
                errors.append(f"plan {bid}: verification_plan row missing check_id")
                continue
            cid = str(cid)
            planned_checks.setdefault(cid, []).append(str(bid))
            vclass = row.get("verification_class")
            if not vclass or str(vclass) not in valid_classes:
                errors.append(
                    f"plan {bid} chk {cid}: invalid verification_class {vclass!r}"
                )
            if CRTQA_KEY_RE.search(json.dumps(row)):
                errors.append(f"plan {bid} chk {cid}: must not reference CRTQA keys in generation")

            if profile == "crtqa_outline":
                vclass = str(row.get("verification_class") or "")
                chk = checks_map.get(cid) or {}
                cc = chk.get("calculation_contract")
                cc_str = str(cc) if cc else None
                min_cases = int(
                    row.get("min_case_count")
                    or _min_case_count(vclass, cc_str, reg, profiles)
                )
                outline = _case_outline_for_check(row)
                if len(outline) < min_cases:
                    errors.append(
                        f"plan {bid} chk {cid}: case_outline has {len(outline)} rows, "
                        f"need >= {min_cases} for {vclass}"
                    )
                for i, item in enumerate(outline):
                    for field in ("case_id", "title", "intent"):
                        if not item.get(field):
                            errors.append(
                                f"plan {bid} chk {cid}: case_outline[{i}] missing {field}"
                            )

                chk = checks_map.get(cid) or {}
                expected_class, expected_priority = _expected_verification_class(
                    chk, reg, row
                )
                override = str(row.get("selection_override_reason") or "").strip()
                actual_class = str(row.get("verification_class") or "")
                if not override and actual_class != expected_class:
                    errors.append(
                        f"plan {bid} chk {cid}: verification_class {actual_class!r} "
                        f"!= expected {expected_class!r} (priority {expected_priority}); "
                        "set selection_override_reason to document override"
                    )
                doc_priority = row.get("selection_rule_priority")
                if not override and doc_priority is not None:
                    try:
                        if int(doc_priority) != expected_priority:
                            errors.append(
                                f"plan {bid} chk {cid}: selection_rule_priority {doc_priority} "
                                f"!= expected {expected_priority} for {expected_class}"
                            )
                    except (TypeError, ValueError):
                        errors.append(
                            f"plan {bid} chk {cid}: selection_rule_priority must be integer"
                        )

    for cid, bids in planned_checks.items():
        if len(bids) > 1:
            errors.append(f"plan: check {cid} mapped to multiple bundles: {', '.join(bids)}")

    for cid in in_scope:
        if cid not in planned_checks:
            errors.append(f"plan: in-scope primary check {cid} missing from verification_plan")

    for cid, row_bundle in planned_checks.items():
        if cid in exc:
            continue
        # ladder_present check
        chk = _checks_by_id(coverage).get(cid) or {}
        for b in bundles:
            if b.get("bundle_id") not in row_bundle:
                continue
            for row in b.get("verification_plan") or []:
                if row.get("check_id") != cid:
                    continue
                vclass = str(row.get("verification_class") or "")
                if vclass == "stateful_ladder":
                    if not b.get("ladder_dependency_declared") and not chk.get(
                        "calculation_contract"
                    ) == "ladder_present":
                        # allow if bundle has ladder_in_test from precon skeleton - check plan flag
                        if not b.get("ladder_dependency_declared"):
                            errors.append(
                                f"plan {b.get('bundle_id')}: stateful_ladder for {cid} "
                                "requires ladder_dependency_declared on bundle"
                            )
                if vclass == "cross_surface_parity":
                    surfaces = row.get("observation_surfaces") or []
                    if not isinstance(surfaces, list) or len(surfaces) < 1:
                        errors.append(
                            f"plan {b.get('bundle_id')}: cross_surface_parity for {cid} "
                            "requires observation_surfaces[]"
                        )

    plan_str = json.dumps(plan)
    if CRTQA_REQUIRES_RE.search(plan_str):
        errors.append("plan: [REQUIRES: CRTQA-*] forbidden in generation mode")

    return errors


def verify_explore(
    coverage: dict[str, Any],
    plan: dict[str, Any],
    *,
    precon: dict[str, Any] | None = None,
    bundle_id: str | None = None,
) -> list[str]:
    errors: list[str] = []
    ladder = _load_ladder()
    reg = _load_registry()
    vc_reg = reg.get("verification_classes") or {}
    prep_req = (ladder.get("prep_requires") or {}).get("by_verification_class") or {}
    precon_widgets = _precon_widgets_by_surface(precon)

    bundles = plan.get("bundles") or []
    if bundle_id:
        bundles = [b for b in bundles if isinstance(b, dict) and b.get("bundle_id") == bundle_id]
        if not bundles:
            errors.append(f"explore: bundle_id {bundle_id!r} not in plan")
            return errors

    for b in bundles:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bundle_id") or "?")
        vex = b.get("verification_exploration") or []
        if not isinstance(vex, list):
            vex = []

        classes: set[str] = set()
        surfaces_needed: set[str] = set()
        for row in b.get("verification_plan") or []:
            if not isinstance(row, dict):
                continue
            vclass = str(row.get("verification_class") or "")
            if vclass:
                classes.add(vclass)
            if vclass == "cross_surface_parity":
                for s in row.get("observation_surfaces") or []:
                    surfaces_needed.add(str(s).lower())

        needs_prep_view = False
        for vclass in classes:
            req = prep_req.get(vclass) if isinstance(prep_req.get(vclass), dict) else {}
            min_d = str(req.get("min_depth") or "")
            if _depth_rank(min_d) >= _depth_rank("prep_verify_view"):
                needs_prep_view = True
            vc = vc_reg.get(vclass) if isinstance(vc_reg.get(vclass), dict) else {}
            for s in vc.get("fe_probe_surfaces") or []:
                surfaces_needed.add(str(s).lower())

        if not needs_prep_view and "stateful_ladder" not in classes:
            if "doc_or_pr_only" in classes and len(classes) == 1:
                continue

        prep_rows = [
            x
            for x in vex
            if isinstance(x, dict)
            and _depth_rank(str(x.get("depth_level"))) >= _depth_rank("prep_verify_view")
        ]
        if needs_prep_view and not prep_rows:
            errors.append(
                f"explore {bid}: verification_exploration[] missing prep_verify_view rows"
            )

        for vclass in classes:
            if vclass in ("cross_surface_parity", "derived_metric") and not prep_rows:
                errors.append(
                    f"explore {bid}: class {vclass} requires prep_verify_view exploration"
                )

        smoke_only = [
            x
            for x in vex
            if isinstance(x, dict) and str(x.get("depth_level")) == "smoke"
        ]
        if needs_prep_view and len(prep_rows) == 0 and len(smoke_only) > 0:
            errors.append(
                f"explore {bid}: only smoke-level exploration; need navigated verification views"
            )

        for surf in surfaces_needed:
            surf_rows = [
                x
                for x in prep_rows
                if str(x.get("surface") or "").lower() == surf
            ]
            if not surf_rows:
                errors.append(
                    f"explore {bid}: missing prep_verify_view for surface {surf!r}"
                )
                continue
            if "cross_surface_parity" in classes or "derived_metric" in classes:
                has_metrics = any(
                    (x.get("metric_columns") or x.get("widgets_seen"))
                    for x in surf_rows
                )
                if not has_metrics:
                    errors.append(
                        f"explore {bid}: surface {surf!r} needs metric_columns or widgets_seen"
                    )
            precon_set = precon_widgets.get(surf, set())
            if precon_set:
                for x in surf_rows:
                    prep_labels = set(str(w) for w in (x.get("metric_columns") or x.get("widgets_seen") or []))
                    if prep_labels and not prep_labels >= precon_set:
                        missing = precon_set - prep_labels
                        if missing:
                            errors.append(
                                f"explore {bid}: surface {surf!r} prep labels should be "
                                f"superset of precon drill widgets; missing {sorted(missing)}"
                            )

        if "stateful_ladder" in classes:
            console_rows = [
                x
                for x in vex
                if str(x.get("surface") or "").lower() == "console"
                and _depth_rank(str(x.get("depth_level"))) >= _depth_rank("precon_drill")
            ]
            if not console_rows:
                errors.append(
                    f"explore {bid}: stateful_ladder needs console verification_exploration"
                )

    return errors


def _draft_section(bundle: dict[str, Any], key: str) -> list[str]:
    draft = bundle.get("draft") or {}
    if not isinstance(draft, dict):
        return []
    sec = draft.get(key) or []
    return [str(x) for x in sec] if isinstance(sec, list) else []


def _yogi_outside_results(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("preconditions", "actions", "peculiarities"):
        for i, line in enumerate(_draft_section(bundle, key)):
            if YOGI_TAG_RE.search(line) and "/requirements/" in line:
                errors.append(
                    f"bundle {bundle.get('bundle_id')}: Yogi/requirement URL in {key}[{i}] "
                    "(allowed in results only)"
                )
            elif key != "results" and re.search(r"\bCRT-\d{3,5}\b", line):
                # allow CRT-639 epic key in preconditions; flag requirement keys in actions
                if key == "actions" and re.search(r"\bCRT-\d{4}\b", line):
                    errors.append(
                        f"bundle {bundle.get('bundle_id')}: requirement key in actions[{i}] "
                        "(use results only for Yogi/requirement tags)"
                    )
    return errors


def verify_draft_bundle(
    coverage: dict[str, Any],
    tests: dict[str, Any],
    bundle_id: str,
    plan: dict[str, Any] | None,
    *,
    precon: dict[str, Any] | None = None,
    ref: dict[str, Any] | None = None,
    strict_topology: bool = False,
    strict_principal: bool = False,
) -> list[str]:
    errors: list[str] = []
    reg = _load_registry()
    profiles = _load_profiles()
    profile = _plan_profile(plan or {}, tests)
    bundles = tests.get("test_bundles") or []
    bundle = None
    for b in bundles:
        if isinstance(b, dict) and b.get("bundle_id") == bundle_id:
            bundle = b
            break
    if bundle is None:
        return [f"tests: bundle_id {bundle_id!r} not found"]

    pre = _draft_section(bundle, "preconditions")
    act = _draft_section(bundle, "actions")
    res = _draft_section(bundle, "results")

    if not pre:
        errors.append(f"bundle {bundle_id}: empty preconditions")
    elif not any(PRECON_CITE_RE.search(p) for p in pre):
        errors.append(
            f"bundle {bundle_id}: preconditions must cite -precon.md or precon cluster"
        )

    if not act:
        errors.append(f"bundle {bundle_id}: empty actions")
    if not res:
        errors.append(f"bundle {bundle_id}: empty results")

    if len(act) != len(res):
        errors.append(
            f"bundle {bundle_id}: actions count ({len(act)}) != results count ({len(res)})"
        )

    errors.extend(_yogi_outside_results(bundle))

    # Plan cross-check
    vclasses: list[str] = []
    plan_rows: list[dict[str, Any]] = []
    if plan:
        for pb in plan.get("bundles") or []:
            if pb.get("bundle_id") == bundle_id:
                for row in pb.get("verification_plan") or []:
                    if isinstance(row, dict) and row.get("verification_class"):
                        vclasses.append(str(row["verification_class"]))
                        plan_rows.append(row)

    draft_body = "\n".join(act + res + pre)

    if profile == "crtqa_outline":
        errors.extend(_forbidden_tbd_errors(draft_body, f"bundle {bundle_id}"))
        if CRTQA_KEY_RE.search(draft_body):
            errors.append(f"bundle {bundle_id}: CRTQA keys forbidden in durable draft (generation)")

        total_min = 0
        for row in plan_rows:
            cid = str(row.get("check_id") or "")
            chk = _checks_by_id(coverage).get(cid) or {}
            cc = chk.get("calculation_contract")
            cc_str = str(cc) if cc else None
            vclass = str(row.get("verification_class") or "")
            total_min += int(
                row.get("min_case_count")
                or _min_case_count(vclass, cc_str, reg, profiles)
            )
        if total_min > 0 and len(act) < total_min:
            errors.append(
                f"bundle {bundle_id}: actions count {len(act)} < plan min_case_count sum {total_min}"
            )

        if plan:
            errors.extend(_verify_outline_cardinality(act, res, plan, bundle_id))
            if _bundle_requires_single_pair(plan, bundle_id):
                errors.extend(_verify_no_duplicate_actions(act, bundle_id))

    if "doc_or_pr_only" in vclasses:
        body = "\n".join(act)
        if EXECUTION_TRADE_RE.search(body):
            errors.append(
                f"bundle {bundle_id}: doc_or_pr_only plan forbids execution trade in actions"
            )

    if "stateful_ladder" in vclasses:
        body = "\n".join(act)
        if profile == "teaching":
            has_vignette = "@" in body or "buy " in body.lower() or "sell " in body.lower()
            has_tbd = bool(LADDER_TBD_RE.search(body))
            if not has_vignette and not has_tbd:
                errors.append(
                    f"bundle {bundle_id}: stateful_ladder requires illustrative vignette or [TBD: ladder]"
                )
        else:
            contract = _load_tbd_contract()
            req = contract.get("stateful_ladder_requirements") or {}
            markers = req.get("template_markers_any") or [
                "execution trade",
                "show position_metrics_from_publisher",
                "buy ",
                "sell ",
            ]
            min_markers = int(req.get("min_template_markers_per_case") or 2)
            case_count = max(len(act), 1)
            marker_hits = sum(
                1 for m in markers if re.search(re.escape(str(m)), body, re.I)
            )
            if marker_hits < min_markers:
                errors.append(
                    f"bundle {bundle_id}: stateful_ladder needs ladder template markers "
                    f"({marker_hits} < {min_markers})"
                )
            if not (
                EXECUTION_TRADE_RE.search(body)
                or POSITION_METRICS_RE.search(body)
            ):
                errors.append(
                    f"bundle {bundle_id}: stateful_ladder requires execution trade template "
                    "or show position_metrics_from_publisher"
                )

    jts = tests.get("jira_test_search") or {}
    if isinstance(jts, dict) and jts.get("skipped") is not True:
        errors.append("tests: jira_test_search.skipped should be true in generation mode")

    existing = tests.get("existing_tests_considered") or []
    if isinstance(existing, list) and len(existing) > 0:
        errors.append("generation: existing_tests_considered must be [] (greenfield)")

    for path, s in _walk_strings(bundle, skip_keys=frozenset({"validation_log"})):
        if TEMP_PATH_RE.search(s):
            errors.append(f"bundle {bundle_id}: /temp/ path in {path}")

    if CRTQA_REQUIRES_RE.search(json.dumps(bundle.get("draft") or {})):
        errors.append(f"bundle {bundle_id}: [REQUIRES: CRTQA-*] forbidden in generation")

    if strict_topology:
        errors.extend(
            _verify_strict_topology(
                coverage,
                tests,
                precon=precon,
                ref=ref,
                plan=plan,
                bundle_id=bundle_id,
            )
        )

    if strict_principal:
        errors.extend(
            verify_strict_test_prep_principal(
                coverage,
                tests,
                precon=precon,
                ref=ref,
                bundle_id=bundle_id,
            )
        )

    return errors


def verify_merge(
    tests: dict[str, Any],
    plan: dict[str, Any] | None,
    *,
    coverage: dict[str, Any] | None = None,
    precon: dict[str, Any] | None = None,
    ref: dict[str, Any] | None = None,
    strict_topology: bool = False,
    strict_principal: bool = False,
) -> list[str]:
    """Post-8c: merged bundle drafts match plan case counts."""
    errors: list[str] = []
    if _plan_profile(plan or {}, tests) != "crtqa_outline":
        return errors
    reg = _load_registry()
    profiles = _load_profiles()
    plan_by_bundle: dict[str, list[dict[str, Any]]] = {}
    for pb in (plan or {}).get("bundles") or []:
        if isinstance(pb, dict) and pb.get("bundle_id"):
            plan_by_bundle[str(pb["bundle_id"])] = [
                r for r in (pb.get("verification_plan") or []) if isinstance(r, dict)
            ]
    for b in tests.get("test_bundles") or []:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bundle_id") or "")
        act = _draft_section(b, "actions")
        res = _draft_section(b, "results")
        rows = plan_by_bundle.get(bid) or []
        total_min = 0
        for row in rows:
            vclass = str(row.get("verification_class") or "")
            total_min += int(
                row.get("min_case_count")
                or _min_case_count(vclass, None, reg, profiles)
            )
        if _bundle_requires_single_pair(plan or {}, bid):
            errors.extend(_verify_outline_cardinality(act, res, plan or {}, bid))
            errors.extend(_verify_no_duplicate_actions(act, bid))
        elif total_min and len(act) < total_min:
            errors.append(
                f"merge {bid}: actions {len(act)} < expected min {total_min} after 8c"
            )
    if strict_topology and coverage is not None:
        errors.extend(
            _verify_strict_topology(
                coverage,
                tests,
                precon=precon,
                ref=ref,
                plan=plan,
            )
        )
    if strict_principal and coverage is not None:
        errors.extend(
            verify_strict_test_prep_principal(
                coverage,
                tests,
                precon=precon,
                ref=ref,
            )
        )
    return errors


def verify_tests_emit(
    coverage: dict[str, Any],
    tests: dict[str, Any],
    plan: dict[str, Any] | None = None,
    *,
    precon: dict[str, Any] | None = None,
    ref: dict[str, Any] | None = None,
    strict_topology: bool = False,
    strict_principal: bool = False,
    md_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    profile = _plan_profile(plan or {}, tests)

    primary = _primary_check_ids(coverage)
    exc = _excluded_ids(tests)
    in_scope = [c for c in primary if c not in exc]

    covered: set[str] = set()
    for b in tests.get("test_bundles") or []:
        if not isinstance(b, dict):
            continue
        for cid in b.get("covers_check_ids") or []:
            covered.add(str(cid))

    gaps = tests.get("reverse_validation") or {}
    gap_rows = [
        g for g in (gaps.get("coverage_gaps") or []) if isinstance(g, dict) and g.get("check_id")
    ]
    gap_ids = {str(g["check_id"]) for g in gap_rows}
    gap_by_id = {str(g["check_id"]): g for g in gap_rows}

    for row in tests.get("excluded_checks_with_reason") or []:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("check_id") or "")
        if not cid or cid not in primary:
            continue
        if cid not in gap_by_id:
            errors.append(
                f"emit: excluded primary {cid} must have reverse_validation.coverage_gaps[] row"
            )
        elif not str(gap_by_id[cid].get("reason") or "").strip():
            errors.append(
                f"emit: coverage_gaps[{cid}] missing reason (mirror excluded_checks_with_reason)"
            )

    for cid in in_scope:
        if cid not in covered and cid not in gap_ids:
            errors.append(f"emit: primary check {cid} not covered and not in coverage_gaps")

    if tests.get("jira_test_search", {}).get("skipped") is not True:
        errors.append("emit: jira_test_search.skipped must be true")

    existing = tests.get("existing_tests_considered") or []
    if existing:
        errors.append("emit: existing_tests_considered must be [] in generation")

    for path, s in _walk_strings(tests, skip_keys=frozenset({"validation_log", "format_norms"})):
        if TEMP_PATH_RE.search(s):
            errors.append(f"emit: /temp/ path in {path}")

    if profile == "crtqa_outline":
        for b in tests.get("test_bundles") or []:
            if not isinstance(b, dict):
                continue
            bid = str(b.get("bundle_id") or "?")
            body = json.dumps(b.get("draft") or {})
            errors.extend(_forbidden_tbd_errors(body, f"emit {bid}"))
            if CRTQA_KEY_RE.search(body):
                errors.append(f"emit {bid}: CRTQA keys in draft")
            if plan:
                act = _draft_section(b, "actions")
                res = _draft_section(b, "results")
                errors.extend(_verify_outline_cardinality(act, res, plan, bid))
                if _bundle_requires_single_pair(plan, bid):
                    errors.extend(_verify_no_duplicate_actions(act, bid))

    if strict_topology:
        errors.extend(
            _verify_strict_topology(
                coverage,
                tests,
                precon=precon,
                ref=ref,
                plan=plan,
            )
        )

    if strict_principal:
        errors.extend(
            verify_strict_test_prep_principal(
                coverage,
                tests,
                precon=precon,
                ref=ref,
            )
        )

    errors.extend(verify_tests_md_hygiene(md_path))

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify TEST-PREP plan and tests artefacts.")
    ap.add_argument(
        "--mode",
        choices=("plan", "explore", "draft", "merge", "tests", "principal", "draft_truth", "scenario_intent"),
        required=True,
        help="plan | explore (8a-three-quarter) | draft | merge (8c) | tests | principal",
    )
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--plan", type=Path, default=None)
    ap.add_argument("--tests", type=Path, default=None)
    ap.add_argument("--precon", type=Path, default=None)
    ap.add_argument("--ref", type=Path, default=None, help="Epic ref for topology strict mode")
    ap.add_argument(
        "--strict-topology",
        action="store_true",
        help="Enforce test-prep-topology-contract (requires --precon and --ref)",
    )
    ap.add_argument(
        "--strict-principal",
        action="store_true",
        help="Enforce test-prep-principal-contract (requires --precon and --ref)",
    )
    ap.add_argument("--bundle-id", type=str, default=None)
    ap.add_argument(
        "--md",
        type=Path,
        default=None,
        help="Optional -tests.md path for operator md hygiene (mode tests)",
    )
    args = ap.parse_args()

    strict_princ = args.strict_principal or args.mode == "principal"

    if args.strict_topology and (args.precon is None or args.ref is None):
        print("strict-topology requires --precon and --ref", file=sys.stderr)
        return 2

    if strict_princ and (args.precon is None or args.ref is None):
        print("--ref and --precon required with --strict-principal / --mode principal", file=sys.stderr)
        return 2

    if args.mode == "principal" and args.tests is None:
        print("--tests required for mode principal", file=sys.stderr)
        return 2

    coverage = _load_json(args.coverage.resolve())
    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2

    precon = _load_json(args.precon.resolve()) if args.precon else None
    ref = _load_json(args.ref.resolve()) if args.ref else None

    excluded = _excluded_ids(_load_json(args.tests.resolve()) or {}) if args.tests else set()

    errors: list[str] = []
    if args.mode == "principal":
        if not args.tests:
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        errors = verify_strict_test_prep_principal(
            coverage,
            tests,
            precon=precon,
            ref=ref,
        )
    elif args.mode == "draft_truth":
        if not args.tests:
            print("--tests required for mode draft_truth", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        errors = verify_draft_truth_test_prep(coverage, tests)
    elif args.mode == "scenario_intent":
        if not args.tests:
            print("--tests required for mode scenario_intent", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        errors = verify_scenario_intent(coverage, tests)
    elif args.mode == "plan":
        if not args.plan:
            print("--plan required for mode plan", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve())
        if plan is None:
            print(f"cannot read plan: {args.plan}", file=sys.stderr)
            return 2
        tests_obj = _load_json(args.tests.resolve()) if args.tests else None
        errors = verify_plan(coverage, plan, excluded=excluded, tests=tests_obj)
    elif args.mode == "explore":
        if not args.plan:
            print("--plan required for mode explore", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve())
        if plan is None:
            print(f"cannot read plan: {args.plan}", file=sys.stderr)
            return 2
        precon = _load_json(args.precon.resolve()) if args.precon else None
        errors = verify_explore(
            coverage,
            plan,
            precon=precon,
            bundle_id=args.bundle_id,
        )
    elif args.mode == "draft":
        if not args.tests or not args.bundle_id:
            print("--tests and --bundle-id required for mode draft", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve()) if args.plan else None
        if _plan_profile(plan or {}, tests) == "crtqa_outline" and plan is None:
            print("--plan required for mode draft when draft_profile=crtqa_outline", file=sys.stderr)
            return 2
        errors = verify_draft_bundle(
            coverage,
            tests,
            args.bundle_id,
            plan,
            precon=precon,
            ref=ref,
            strict_topology=args.strict_topology,
            strict_principal=strict_princ,
        )
    elif args.mode == "merge":
        if not args.tests or not args.plan:
            print("--tests and --plan required for mode merge", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve())
        if plan is None:
            print(f"cannot read plan: {args.plan}", file=sys.stderr)
            return 2
        errors = verify_merge(
            tests,
            plan,
            coverage=coverage,
            precon=precon,
            ref=ref,
            strict_topology=args.strict_topology,
            strict_principal=strict_princ,
        )
    else:
        if not args.tests:
            print("--tests required for mode tests", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve()) if args.plan else None
        profile = _plan_profile(plan or {}, tests)
        if profile == "crtqa_outline" and plan is None:
            print("--plan required for mode tests when draft_profile=crtqa_outline", file=sys.stderr)
            return 2
        errors = verify_tests_emit(
            coverage,
            tests,
            plan,
            precon=precon,
            ref=ref,
            strict_topology=args.strict_topology,
            strict_principal=strict_princ,
            md_path=args.md,
        )

    if errors:
        print(f"test_prep_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK test_prep_verify mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
