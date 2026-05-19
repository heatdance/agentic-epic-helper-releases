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

    return errors


def verify_merge(
    tests: dict[str, Any],
    plan: dict[str, Any] | None,
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
        rows = plan_by_bundle.get(bid) or []
        total_min = 0
        for row in rows:
            cid = str(row.get("check_id") or "")
            chk = {}  # coverage optional at merge
            vclass = str(row.get("verification_class") or "")
            total_min += int(
                row.get("min_case_count")
                or _min_case_count(vclass, None, reg, profiles)
            )
        if total_min and len(act) < total_min:
            errors.append(
                f"merge {bid}: actions {len(act)} < expected min {total_min} after 8c"
            )
    return errors


def verify_tests_emit(
    coverage: dict[str, Any],
    tests: dict[str, Any],
    plan: dict[str, Any] | None = None,
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
    gap_ids = {
        str(g["check_id"])
        for g in (gaps.get("coverage_gaps") or [])
        if isinstance(g, dict) and g.get("check_id")
    }

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

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify TEST-PREP plan and tests artefacts.")
    ap.add_argument(
        "--mode",
        choices=("plan", "explore", "draft", "merge", "tests"),
        required=True,
        help="plan | explore (8a-three-quarter) | draft | merge (8c) | tests",
    )
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--plan", type=Path, default=None)
    ap.add_argument("--tests", type=Path, default=None)
    ap.add_argument("--precon", type=Path, default=None)
    ap.add_argument("--bundle-id", type=str, default=None)
    args = ap.parse_args()

    coverage = _load_json(args.coverage.resolve())
    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2

    excluded = _excluded_ids(_load_json(args.tests.resolve()) or {}) if args.tests else set()

    errors: list[str] = []
    if args.mode == "plan":
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
        errors = verify_draft_bundle(coverage, tests, args.bundle_id, plan)
    elif args.mode == "merge":
        if not args.tests:
            print("--tests required for mode merge", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve()) if args.plan else None
        errors = verify_merge(tests, plan)
    else:
        if not args.tests:
            print("--tests required for mode tests", file=sys.stderr)
            return 2
        tests = _load_json(args.tests.resolve())
        if tests is None:
            print(f"cannot read tests: {args.tests}", file=sys.stderr)
            return 2
        plan = _load_json(args.plan.resolve()) if args.plan else None
        errors = verify_tests_emit(coverage, tests, plan)

    if errors:
        print(f"test_prep_verify ({args.mode}) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK test_prep_verify mode={args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
