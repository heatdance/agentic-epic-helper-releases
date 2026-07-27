#!/usr/bin/env python3
"""
Verify CLOSE pipeline artefacts and post-archive layout.

Examples:
  python automation/tools/close_verify.py --mode preflight --epic-dir epics/CRT-639

  python automation/tools/close_verify.py --mode ladder_l0 --epic-dir epics/CRT-639 \\
    --close epics/CRT-639/CRT-639-close.json

  python automation/tools/close_verify.py --mode topology --strict-topology \\
    --epic-dir automation/tools/fixtures/close/topology-594-pass

  python automation/tools/close_verify.py --mode principal --strict-principal \\
    --epic-dir automation/tools/fixtures/close/principal-594-pass
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "close-contract.json"
TOPOLOGY_CONTRACT_PATH = REPO_ROOT / "docs" / "close-topology-contract.json"
PRINCIPAL_CONTRACT_PATH = REPO_ROOT / "docs" / "close-principal-contract.json"
_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
from test_prep_verify import verify_strict_test_prep_principal  # noqa: E402
from epic_paths import dependencies_dir, resolve_json  # noqa: E402
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
SECRET_LIKE_RE = re.compile(
    r"(password\s*[:=]|Bearer\s+|api[_-]?key\s*[:=])", re.I
)
PLACEHOLDER_TOKEN_RE = re.compile(r"<([a-zA-Z_][a-zA-Z0-9_]*)>")
DELIVERY_COVERAGE_STATUS = frozenset({"failed", "excluded"})


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _contract() -> dict[str, Any]:
    return _load_json(CONTRACT_PATH) or {}


def _topology_contract() -> dict[str, Any]:
    doc = _load_json(TOPOLOGY_CONTRACT_PATH) or {}
    raw = doc.get("oracle_rule_to_pattern_ref") or {}
    return {
        **doc,
        "oracle_map": {
            k: v
            for k, v in raw.items()
            if k != "inherits" and isinstance(v, str)
        },
    }


def _primary_check_ids(coverage: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if cid and chk.get("verification_role") == "primary":
            ids.add(str(cid))
    return ids


def _topology_loaded_any(
    discover: dict[str, Any],
    precon: dict[str, Any],
    tests: dict[str, Any],
) -> bool:
    for doc in (discover, precon, tests):
        src = doc.get("sources") or {}
        if isinstance(src, dict) and src.get("topology_loaded") is True:
            return True
    return False


def _delivery_blocked_check_ids(
    coverage: dict[str, Any],
    discover: dict[str, Any],
    precon: dict[str, Any],
) -> set[str]:
    blocked: set[str] = set()
    primary = _primary_check_ids(coverage)
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        if not cid or str(cid) not in primary:
            continue
        if str(chk.get("delivery_status") or "").lower() in DELIVERY_COVERAGE_STATUS:
            blocked.add(str(cid))
    for row in discover.get("obligation_ledger") or []:
        if not isinstance(row, dict):
            continue
        if row.get("disposition") == "tooling_blocked" and row.get("check_id"):
            cid = str(row["check_id"])
            if cid in primary:
                blocked.add(cid)
    for row in precon.get("excluded_checks_with_reason") or []:
        if isinstance(row, dict) and row.get("check_id"):
            reason = str(row.get("reason") or "")
            if reason in ("delivery_blocked", "deferred_ambiguous"):
                blocked.add(str(row["check_id"]))
    return blocked


def _outline_pattern_refs(precon: dict[str, Any]) -> dict[str, set[str]]:
    by_chk: dict[str, set[str]] = {}
    for row in precon.get("test_skeleton") or []:
        if not isinstance(row, dict):
            continue
        for item in row.get("case_outline") or []:
            if not isinstance(item, dict):
                continue
            chk = str(item.get("check_id") or "")
            pref = item.get("pattern_ref")
            if chk and pref:
                by_chk.setdefault(chk, set()).add(str(pref))
    return by_chk


def _affordance_oracle_binding_matches(
    discover: dict[str, Any], check_id: str, oracle_rule_id: str
) -> bool:
    aff_by_id: dict[str, dict[str, Any]] = {}
    for aff in discover.get("verification_affordances") or []:
        if isinstance(aff, dict) and aff.get("id"):
            aff_by_id[str(aff["id"])] = aff
    ledger_by_check: dict[str, dict[str, Any]] = {}
    for row in discover.get("obligation_ledger") or []:
        if isinstance(row, dict) and row.get("check_id"):
            ledger_by_check[str(row["check_id"])] = row
    row = ledger_by_check.get(check_id) or {}
    for aid in row.get("affordance_ids") or []:
        aff = aff_by_id.get(str(aid))
        if not aff:
            continue
        binding = aff.get("oracle_binding")
        if isinstance(binding, dict) and binding.get("oracle_rule_id") == oracle_rule_id:
            return True
    for aff in discover.get("verification_affordances") or []:
        if not isinstance(aff, dict):
            continue
        linked = [str(c) for c in (aff.get("linked_check_ids") or [])]
        binding = aff.get("oracle_binding")
        if (
            check_id in linked
            and isinstance(binding, dict)
            and binding.get("oracle_rule_id") == oracle_rule_id
        ):
            return True
    return False


def _discover_oracle_rule_for_check(
    discover: dict[str, Any], check_id: str
) -> str | None:
    for aff in discover.get("verification_affordances") or []:
        if not isinstance(aff, dict):
            continue
        linked = [str(c) for c in (aff.get("linked_check_ids") or [])]
        if check_id not in linked:
            continue
        binding = aff.get("oracle_binding")
        if isinstance(binding, dict) and binding.get("oracle_rule"):
            return str(binding["oracle_rule"])
    return None


def _excluded_test_ids(tests: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for row in tests.get("excluded_checks_with_reason") or []:
        if isinstance(row, dict) and row.get("check_id"):
            out.add(str(row["check_id"]))
    gaps = tests.get("reverse_validation") or {}
    for g in gaps.get("coverage_gaps") or []:
        if isinstance(g, dict) and g.get("check_id"):
            out.add(str(g["check_id"]))
    return out


def _ref_oracle_rule_ids(ref: dict[str, Any]) -> set[str]:
    topo = ref.get("verification_topology") or {}
    if not isinstance(topo, dict):
        return set()
    return {
        str(r["id"])
        for r in (topo.get("pricing_oracle_rules") or [])
        if isinstance(r, dict) and r.get("id")
    }


def _session_placeholder_keys(precon: dict[str, Any]) -> set[str]:
    sp = precon.get("session_placeholders") or {}
    if not isinstance(sp, dict):
        return set()
    return {str(k) for k in sp if not str(k).startswith("_")}


def _collect_placeholder_tokens(text: str) -> set[str]:
    return set(PLACEHOLDER_TOKEN_RE.findall(text))


def _verify_strict_topology(
    ref: dict[str, Any],
    coverage: dict[str, Any],
    discover: dict[str, Any],
    precon: dict[str, Any],
    tests: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not _topology_loaded_any(discover, precon, tests):
        return errors, warnings

    oracle_map = (_topology_contract()).get("oracle_map") or {}
    ref_rule_ids = _ref_oracle_rule_ids(ref)
    checks_by_id = {
        str(c.get("id")): c
        for c in (coverage.get("checks") or [])
        if isinstance(c, dict) and c.get("id")
    }
    primary = _primary_check_ids(coverage)
    blocked = _delivery_blocked_check_ids(coverage, discover, precon)
    outline_refs = _outline_pattern_refs(precon)
    precon_excluded = {
        str(r["check_id"])
        for r in (precon.get("excluded_checks_with_reason") or [])
        if isinstance(r, dict) and r.get("check_id")
    }
    test_excluded = _excluded_test_ids(tests)
    cluster_ids = {
        str(c.get("id"))
        for c in (precon.get("precon_clusters") or [])
        if isinstance(c, dict) and c.get("id")
    }

    for cid, chk in checks_by_id.items():
        oracle_id = chk.get("oracle_rule_id")
        if not oracle_id:
            continue
        oracle_id = str(oracle_id)
        if oracle_id not in ref_rule_ids:
            errors.append(
                f"strict-topology: check {cid} oracle_rule_id {oracle_id!r} "
                "not in ref pricing_oracle_rules"
            )
        if cid in primary and cid not in blocked:
            if not _affordance_oracle_binding_matches(discover, cid, oracle_id):
                errors.append(
                    f"strict-topology: primary {cid} missing discover affordance "
                    f"with oracle_binding {oracle_id!r}"
                )
            if not outline_refs.get(cid):
                errors.append(
                    f"strict-topology: check {cid} has oracle_rule_id but no "
                    "precon case_outline.pattern_ref"
                )
            else:
                rule_name = _discover_oracle_rule_for_check(discover, cid)
                if rule_name:
                    expected = oracle_map.get(rule_name)
                    if expected and expected not in (outline_refs.get(cid) or set()):
                        errors.append(
                            f"strict-topology: check {cid} oracle {rule_name!r} "
                            f"expects pattern_ref {expected!r}"
                        )

    skeleton_covered: set[str] = set()
    for row in precon.get("test_skeleton") or []:
        if isinstance(row, dict):
            for cid in row.get("covers_check_ids") or []:
                skeleton_covered.add(str(cid))

    for cid in blocked:
        if cid not in primary:
            continue
        for b in _bundles(tests):
            bid = str(b.get("bundle_id") or "?")
            covers = [str(x) for x in (b.get("covers_check_ids") or [])]
            if cid in covers:
                errors.append(
                    f"strict-topology: delivery-blocked check {cid} in bundle "
                    f"{bid} covers_check_ids"
                )
        if cid in skeleton_covered and cid not in precon_excluded:
            errors.append(
                f"strict-topology: delivery-blocked check {cid} still in "
                "precon test_skeleton covers_check_ids"
            )
        if cid not in precon_excluded:
            errors.append(
                f"strict-topology: delivery-blocked check {cid} missing from "
                "precon excluded_checks_with_reason"
            )
        if cid not in test_excluded:
            gap_ids = {
                str(g["check_id"])
                for g in ((tests.get("reverse_validation") or {}).get("coverage_gaps") or [])
                if isinstance(g, dict) and g.get("check_id")
            }
            if cid not in gap_ids:
                errors.append(
                    f"strict-topology: delivery-blocked check {cid} missing from "
                    "tests reverse_validation.coverage_gaps[]"
                )

    vt = ref.get("verification_topology") or {}
    candidates = vt.get("platform_reuse_candidates") if isinstance(vt, dict) else []
    if isinstance(candidates, list) and candidates:
        annex = tests.get("platform_reuse_annex")
        if not annex or not str(annex).strip():
            errors.append(
                "strict-topology: platform_reuse_annex required when ref has "
                "platform_reuse_candidates"
            )
        elif CRTQA_KEY_RE.search(str(annex)):
            errors.append("strict-topology: CRTQA keys forbidden in platform_reuse_annex")

    for b in _bundles(tests):
        bid = str(b.get("bundle_id") or "?")
        for pref in b.get("precon_cluster_refs") or []:
            pref_s = str(pref)
            if pref_s not in cluster_ids:
                errors.append(
                    f"strict-topology: bundle {bid} precon_cluster_refs {pref_s!r} "
                    "not in precon.precon_clusters"
                )

    loaded_flags = {
        "discover": bool((discover.get("sources") or {}).get("topology_loaded")),
        "precon": bool((precon.get("sources") or {}).get("topology_loaded")),
        "tests": bool((tests.get("sources") or {}).get("topology_loaded")),
    }
    if sum(loaded_flags.values()) >= 2:
        vals = set(loaded_flags.values())
        if vals != {True}:
            warnings.append(
                "WARN strict-topology: topology_loaded mismatch across "
                f"discover={loaded_flags['discover']} precon={loaded_flags['precon']} "
                f"tests={loaded_flags['tests']}"
            )

    ph_keys = _session_placeholder_keys(precon)
    for path, s in _walk_strings(precon.get("command_patterns") or {}):
        for tok in _collect_placeholder_tokens(s):
            if tok not in ph_keys and tok not in ("orderkey", "qty", "price"):
                warnings.append(
                    f"WARN strict-topology: precon command_patterns token "
                    f"<{tok}> not in session_placeholders at {path}"
                )
    for b in _bundles(tests):
        bid = str(b.get("bundle_id") or "?")
        draft = b.get("draft") or {}
        for section in ("actions", "results", "preconditions"):
            for i, s in enumerate(draft.get(section) or []):
                for tok in _collect_placeholder_tokens(str(s)):
                    if tok not in ph_keys and tok not in ("orderkey", "qty", "price"):
                        warnings.append(
                            f"WARN strict-topology: bundle {bid} draft.{section}[{i}] "
                            f"token <{tok}> not in session_placeholders"
                        )

    return errors, warnings


def _resolve_artifact_paths(
    epic_dir: Path,
    key: str | None,
    *,
    ref: Path | None,
    coverage: Path | None,
    discover: Path | None,
    precon: Path | None,
    tests: Path | None,
) -> dict[str, Path | None]:
    if all(p is not None for p in (ref, coverage, discover, precon, tests)):
        return {
            "ref": ref,
            "coverage": coverage,
            "discover": discover,
            "precon": precon,
            "tests": tests,
        }
    if not key:
        return {
            "ref": None,
            "coverage": None,
            "discover": None,
            "precon": None,
            "tests": None,
        }
    archived = _is_archived(epic_dir, key)
    base = epic_dir / "context" if archived else epic_dir
    return {
        "ref": ref or base / f"{key}-ref.json",
        "coverage": coverage or base / f"{key}-coverage.json",
        "discover": discover or base / f"{key}-discover.json",
        "precon": precon or base / f"{key}-precon.json",
        "tests": tests or base / f"{key}-tests.json",
    }


def verify_topology(
    epic_dir: Path,
    *,
    strict_topology: bool,
    ref_path: Path | None = None,
    coverage_path: Path | None = None,
    discover_path: Path | None = None,
    precon_path: Path | None = None,
    tests_path: Path | None = None,
) -> list[str]:
    if not strict_topology:
        return ["WARN strict-topology not set; topology mode no-op"]

    key = _epic_key_from_dir(epic_dir)
    paths = _resolve_artifact_paths(
        epic_dir,
        key,
        ref=ref_path,
        coverage=coverage_path,
        discover=discover_path,
        precon=precon_path,
        tests=tests_path,
    )
    ref = _load_json(paths["ref"]) if paths["ref"] and paths["ref"].is_file() else None
    cov = (
        _load_json(paths["coverage"])
        if paths["coverage"] and paths["coverage"].is_file()
        else None
    )
    discover = (
        _load_json(paths["discover"])
        if paths["discover"] and paths["discover"].is_file()
        else None
    )
    precon = (
        _load_json(paths["precon"])
        if paths["precon"] and paths["precon"].is_file()
        else None
    )
    tests = (
        _load_json(paths["tests"])
        if paths["tests"] and paths["tests"].is_file()
        else None
    )

    if not all([ref, cov, discover, precon, tests]):
        missing = [
            label
            for label, p in paths.items()
            if p is None or not p.is_file()
        ]
        return [f"topology requires ref, coverage, discover, precon, tests; missing: {missing}"]

    assert ref and cov and discover and precon and tests
    errors, warnings = _verify_strict_topology(ref, cov, discover, precon, tests)
    if not _topology_loaded_any(discover, precon, tests) and not errors:
        warnings.append("WARN strict-topology skipped: no downstream topology_loaded")
    return errors + warnings


def _principal_loaded_any(
    discover: dict[str, Any],
    precon: dict[str, Any],
    tests: dict[str, Any],
) -> bool:
    for doc in (discover, precon, tests):
        src = doc.get("sources") or {}
        if isinstance(src, dict) and src.get("principal_loaded") is True:
            return True
    return False


def _ref_has_provision_or_personas(ref: dict[str, Any]) -> bool:
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        hints = obl.get("downstream_hints") or {}
        if not isinstance(hints, dict):
            continue
        if hints.get("needs_environment_provision") or hints.get(
            "needs_dual_account_contrast"
        ):
            return True
        personas = hints.get("personas") or []
        if isinstance(personas, list) and personas:
            return True
    return False


def _precon_has_pc_setup(precon: dict[str, Any]) -> bool:
    for cluster in precon.get("precon_clusters") or []:
        if isinstance(cluster, dict) and str(cluster.get("id")) == "pc-setup":
            return True
    return False


def _provision_obligations(ref: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for obl in ref.get("obligations_proposed") or []:
        if not isinstance(obl, dict):
            continue
        oid = obl.get("id")
        if not oid:
            continue
        hints = obl.get("downstream_hints") or {}
        if isinstance(hints, dict) and hints.get("needs_environment_provision"):
            ids.add(str(oid))
        elif obl.get("kind") == "environment_setup":
            ids.add(str(oid))
    return ids


def _provision_fixtures_discover(discover: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fix in discover.get("fixture_needs") or []:
        if isinstance(fix, dict) and fix.get("derivation") == "ref_principal_provision":
            out.append(fix)
    return out


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


def _excluded_check_ids(
    doc: dict[str, Any],
    *,
    reason: str | None = None,
) -> set[str]:
    ids: set[str] = set()
    for row in doc.get("excluded_checks_with_reason") or []:
        if not isinstance(row, dict) or not row.get("check_id"):
            continue
        if reason is None or str(row.get("reason") or "") == reason:
            ids.add(str(row["check_id"]))
    return ids


def _skeleton_setup_row(precon: dict[str, Any]) -> dict[str, Any] | None:
    for row in precon.get("test_skeleton") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("bundle_id")) == "tb-setup" or str(
            row.get("precon_cluster_id")
        ) == "pc-setup":
            return row
    return None


def _tests_setup_bundle(tests: dict[str, Any]) -> dict[str, Any] | None:
    for b in _bundles(tests):
        bid = str(b.get("bundle_id") or "")
        refs = {str(x) for x in (b.get("precon_cluster_refs") or [])}
        if bid == "tb-setup" or "pc-setup" in refs:
            return b
    return None


def _principal_handoff_active(
    ref: dict[str, Any],
    discover: dict[str, Any],
    precon: dict[str, Any],
    tests: dict[str, Any],
) -> bool:
    if _principal_loaded_any(discover, precon, tests):
        return True
    if _precon_has_pc_setup(precon):
        return True
    return _ref_has_provision_or_personas(ref)


def _verify_strict_principal(
    ref: dict[str, Any],
    coverage: dict[str, Any],
    discover: dict[str, Any],
    precon: dict[str, Any],
    tests: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not _principal_handoff_active(ref, discover, precon, tests):
        return errors, warnings

    loaded_flags = {
        "discover": bool((discover.get("sources") or {}).get("principal_loaded")),
        "precon": bool((precon.get("sources") or {}).get("principal_loaded")),
        "tests": bool((tests.get("sources") or {}).get("principal_loaded")),
    }
    if sum(loaded_flags.values()) >= 2:
        if set(loaded_flags.values()) != {True}:
            warnings.append(
                "WARN strict-principal: principal_loaded mismatch across "
                f"discover={loaded_flags['discover']} precon={loaded_flags['precon']} "
                f"tests={loaded_flags['tests']}"
            )

    provision_fixtures = _provision_fixtures_discover(discover)
    if _precon_has_pc_setup(precon) and provision_fixtures:
        setup_cluster: dict[str, Any] | None = None
        for cluster in precon.get("precon_clusters") or []:
            if isinstance(cluster, dict) and str(cluster.get("id")) == "pc-setup":
                setup_cluster = cluster
                break
        if setup_cluster is None:
            errors.append(
                "strict-principal: precon_clusters missing pc-setup when "
                "discover has ref_principal_provision fixtures"
            )
        else:
            sat_fix = {
                str(x)
                for x in (setup_cluster.get("satisfies_fixture_ids") or [])
            }
            for fix in provision_fixtures:
                fix_id = str(fix.get("id") or "")
                if fix_id and fix_id not in sat_fix:
                    errors.append(
                        f"strict-principal: pc-setup must satisfy_fixture_ids "
                        f"include {fix_id!r} (provision_mismatch)"
                    )
            prov_obls = _provision_obligations(ref)
            if prov_obls:
                linked: set[str] = set()
                for fix in provision_fixtures:
                    for oid in fix.get("linked_obligation_ids") or []:
                        linked.add(str(oid))
                missing = prov_obls - linked
                if missing:
                    errors.append(
                        "strict-principal: ref provision obligations missing from "
                        f"discover fixture linked_obligation_ids: {sorted(missing)}"
                    )

    skel = _skeleton_setup_row(precon)
    setup_bundle = _tests_setup_bundle(tests)
    if skel is not None and _precon_has_pc_setup(precon):
        skel_ids = {str(x) for x in (skel.get("covers_check_ids") or [])}
        if setup_bundle is None:
            errors.append(
                "strict-principal: tests missing tb-setup bundle matching "
                "precon test_skeleton tb-setup"
            )
        else:
            test_ids = {
                str(x) for x in (setup_bundle.get("covers_check_ids") or [])
            }
            if skel_ids != test_ids:
                errors.append(
                    "strict-principal: precon tb-setup covers_check_ids "
                    f"{sorted(skel_ids)} != tests tb-setup {sorted(test_ids)}"
                )

    deferral_ids = _deferral_keyed_check_ids(coverage)
    if deferral_ids:
        precon_def = _excluded_check_ids(precon, reason="deferral_obligation_keyed")
        tests_def = _excluded_check_ids(tests, reason="deferral_obligation_keyed")
        gap_ids = {
            str(g["check_id"])
            for g in ((tests.get("reverse_validation") or {}).get("coverage_gaps") or [])
            if isinstance(g, dict) and g.get("check_id")
        }
        if deferral_ids != precon_def:
            errors.append(
                "strict-principal: deferral-keyed coverage checks != precon "
                f"excluded deferral_obligation_keyed: coverage={sorted(deferral_ids)} "
                f"precon={sorted(precon_def)} (deferral_drift)"
            )
        if deferral_ids != tests_def:
            errors.append(
                "strict-principal: deferral-keyed coverage checks != tests "
                f"excluded deferral_obligation_keyed: coverage={sorted(deferral_ids)} "
                f"tests={sorted(tests_def)} (deferral_drift)"
            )
        if deferral_ids - gap_ids:
            errors.append(
                "strict-principal: deferral-keyed checks missing from tests "
                "reverse_validation.coverage_gaps[] (deferral_drift)"
            )

    precon_ph = precon.get("session_placeholders") or {}
    tests_sources = tests.get("sources") or {}
    tests_ph = tests_sources.get("session_placeholders") if isinstance(
        tests_sources, dict
    ) else {}
    if isinstance(precon_ph, dict) and precon_ph:
        if not isinstance(tests_ph, dict):
            tests_ph = {}
        for key in precon_ph:
            if str(key).startswith("_"):
                continue
            if key not in tests_ph:
                errors.append(
                    f"strict-principal: tests sources.session_placeholders missing "
                    f"copied key {key!r} from precon (principal_drift)"
                )

    for msg in verify_strict_test_prep_principal(
        coverage, tests, precon=precon, ref=ref
    ):
        if msg.startswith("strict-principal:"):
            errors.append(msg)
        else:
            errors.append(f"strict-principal: {msg}")

    return errors, warnings


def verify_principal(
    epic_dir: Path,
    *,
    strict_principal: bool,
    ref_path: Path | None = None,
    coverage_path: Path | None = None,
    discover_path: Path | None = None,
    precon_path: Path | None = None,
    tests_path: Path | None = None,
) -> list[str]:
    if not strict_principal:
        return ["WARN strict-principal not set; principal mode no-op"]

    key = _epic_key_from_dir(epic_dir)
    paths = _resolve_artifact_paths(
        epic_dir,
        key,
        ref=ref_path,
        coverage=coverage_path,
        discover=discover_path,
        precon=precon_path,
        tests=tests_path,
    )
    ref = _load_json(paths["ref"]) if paths["ref"] and paths["ref"].is_file() else None
    cov = (
        _load_json(paths["coverage"])
        if paths["coverage"] and paths["coverage"].is_file()
        else None
    )
    discover = (
        _load_json(paths["discover"])
        if paths["discover"] and paths["discover"].is_file()
        else None
    )
    precon = (
        _load_json(paths["precon"])
        if paths["precon"] and paths["precon"].is_file()
        else None
    )
    tests = (
        _load_json(paths["tests"])
        if paths["tests"] and paths["tests"].is_file()
        else None
    )

    if not all([ref, cov, discover, precon, tests]):
        missing = [
            label
            for label, p in paths.items()
            if p is None or not p.is_file()
        ]
        return [f"principal requires ref, coverage, discover, precon, tests; missing: {missing}"]

    assert ref and cov and discover and precon and tests
    errors, warnings = _verify_strict_principal(ref, cov, discover, precon, tests)
    if not _principal_handoff_active(ref, discover, precon, tests) and not errors:
        warnings.append("WARN strict-principal skipped: no principal handoff")
    return errors + warnings


def _epic_key_from_dir(epic_dir: Path) -> str | None:
    name = epic_dir.name
    if re.match(r"^[A-Z]+-\d+$", name):
        return name
    deps = epic_dir / "dependencies"
    for base in (deps, epic_dir):
        if not base.is_dir() and base != epic_dir:
            continue
        for p in base.glob("*-ref.json"):
            stem = p.stem
            if stem.endswith("-ref"):
                return stem[: -len("-ref")]
    ctx = epic_dir / "context"
    if ctx.is_dir():
        for p in ctx.glob("*-ref.json"):
            stem = p.stem
            if stem.endswith("-ref"):
                return stem[: -len("-ref")]
    return None


def _artifact_paths(epic_dir: Path, key: str, archived: bool) -> dict[str, Path]:
    if archived:
        base = epic_dir / "context"
    else:
        base = dependencies_dir(key)
        if not base.is_absolute():
            base = epic_dir / "dependencies"
    paths = {
        "ref": base / f"{key}-ref.json",
        "coverage": base / f"{key}-coverage.json",
        "discover": base / f"{key}-discover.json",
        "precon": base / f"{key}-precon.json",
        "tests": base / f"{key}-tests.json",
        "analysis": base / f"{key}-analysis.json",
    }
    if not archived:
        for stem in ("ref", "coverage", "discover", "tests", "analysis", "precon"):
            leg = epic_dir / f"{key}-{stem}.json"
            if leg.is_file() and not paths[stem].is_file():
                paths[stem] = leg
    return paths


def _is_archived(epic_dir: Path, key: str) -> bool:
    ctx = epic_dir / "context"
    return (ctx / f"{key}-ref.json").is_file()


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


def _check_ids_from_coverage(cov: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for chk in cov.get("checks") or []:
        if isinstance(chk, dict) and chk.get("id"):
            ids.add(str(chk["id"]))
    return ids


def _bundles(tests: dict[str, Any]) -> list[dict[str, Any]]:
    raw = tests.get("test_bundles") or []
    return [b for b in raw if isinstance(b, dict)]


def verify_preflight(epic_dir: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    key = _epic_key_from_dir(epic_dir)
    if not key:
        errors.append("cannot determine epic_key from epic-dir")
        return errors

    if (epic_dir / "temp").exists():
        errors.append("temp/ must be deleted before CLOSE preflight")

    archived = _is_archived(epic_dir, key)
    if archived:
        errors.append(
            "epic appears already archived (context/*-ref.json); "
            "move JSON back to root to re-run upstream pipelines"
        )
        return errors

    paths = _artifact_paths(epic_dir, key, archived=False)
    pre = contract.get("preflight") or {}
    artifact_loc = pre.get("artifact_location") or "dependencies"
    deps = epic_dir / "dependencies"
    required = pre.get("required_artifacts") or []
    for pattern in required:
        name = pattern.replace("{epic_key}", key)
        if artifact_loc == "dependencies":
            candidates = [deps / name, epic_dir / name]
        else:
            candidates = [epic_dir / name]
        if not any(p.is_file() for p in candidates):
            errors.append(f"missing required artifact: {name}")

    optional = pre.get("optional_artifacts") or []
    for pattern in optional:
        name = pattern.replace("{epic_key}", key)
        if artifact_loc == "dependencies":
            candidates = [deps / name, epic_dir / name]
        else:
            candidates = [epic_dir / name]
        if not any(p.is_file() for p in candidates):
            errors.append(f"WARN optional missing: {name}")

    cov_md = epic_dir / f"{key}-coverage.md"
    if not cov_md.is_file():
        errors.append(f"missing root coverage md: {key}-coverage.md")

    for label, p in paths.items():
        if label == "analysis":
            continue
        if p.is_file():
            doc = _load_json(p)
            if doc is None:
                errors.append(f"invalid json: {p.name}")

    return errors


def _ladder_l0_checks(
    tests: dict[str, Any],
    cov: dict[str, Any],
    bundle_id: str | None,
) -> list[str]:
    errors: list[str] = []
    check_ids = _check_ids_from_coverage(cov)
    bundles = _bundles(tests)
    if bundle_id:
        bundles = [b for b in bundles if b.get("bundle_id") == bundle_id]
        if not bundles:
            errors.append(f"bundle_id not found: {bundle_id!r}")

    seen_bids: set[str] = set()
    gen_mode = (tests.get("sources") or {}).get("generation_mode") is True

    for b in bundles:
        bid = b.get("bundle_id")
        if not bid:
            errors.append("bundle missing bundle_id")
            continue
        if str(bid) in seen_bids:
            errors.append(f"duplicate bundle_id {bid!r}")
        seen_bids.add(str(bid))

        covers = b.get("covers_check_ids") or []
        if not isinstance(covers, list) or not covers:
            errors.append(f"{bid}: empty covers_check_ids")
        for cid in covers:
            if str(cid) not in check_ids:
                errors.append(f"{bid}: covers_check_ids references unknown {cid!r}")

        draft = b.get("draft") or {}
        actions = draft.get("actions") or []
        results = draft.get("results") or []
        if actions or results:
            if len(actions) != len(results):
                errors.append(
                    f"{bid}: draft actions/results count mismatch "
                    f"({len(actions)} vs {len(results)})"
                )

        if gen_mode:
            blob = json.dumps(b, ensure_ascii=False)
            if CRTQA_KEY_RE.search(blob):
                errors.append(f"{bid}: CRTQA key in bundle (generation_mode)")

    return errors


def _ladder_l1_checks(
    precon: dict[str, Any],
    tests: dict[str, Any],
    bundle_id: str | None,
) -> list[str]:
    errors: list[str] = []
    bundles = _bundles(tests)
    if bundle_id:
        bundles = [b for b in bundles if b.get("bundle_id") == bundle_id]

    skeleton = precon.get("test_skeleton") or []
    sk_by_bundle: dict[str, dict[str, Any]] = {}
    for row in skeleton:
        if isinstance(row, dict) and row.get("bundle_id"):
            sk_by_bundle[str(row["bundle_id"])] = row

    for path, s in _walk_strings(precon.get("session_placeholders") or {}):
        if SECRET_LIKE_RE.search(s):
            errors.append(f"precon session_placeholders secret-like at {path}")

    for b in bundles:
        bid = str(b.get("bundle_id") or "")
        sk = sk_by_bundle.get(bid)
        if not sk:
            errors.append(f"{bid}: no test_skeleton row in precon")
            continue
        outline = sk.get("case_outline") or []
        if not outline:
            errors.append(f"{bid}: empty case_outline in precon")

    return errors


def _ladder_l2_checks(
    discover: dict[str, Any],
    tests: dict[str, Any],
    bundle_id: str | None,
) -> list[str]:
    errors: list[str] = []
    gates = discover.get("test_prep_gates") or {}
    if isinstance(gates, dict) and gates.get("blocked") is True:
        src = tests.get("sources") or {}
        if not src.get("discover_blocked_acknowledged"):
            errors.append("discover test_prep_gates.blocked but tests.sources.discover_blocked_acknowledged not true")
    return errors


def _ladder_l3_checks(
    cov: dict[str, Any],
    tests: dict[str, Any],
    bundle_id: str | None,
) -> list[str]:
    errors: list[str] = []
    check_ids = _check_ids_from_coverage(cov)
    bundles = _bundles(tests)
    if bundle_id:
        bundles = [b for b in bundles if b.get("bundle_id") == bundle_id]

    for b in bundles:
        bid = b.get("bundle_id")
        for cid in b.get("covers_check_ids") or []:
            if str(cid) not in check_ids:
                errors.append(f"{bid}: L3 unknown check {cid!r}")
    return errors


def _ladder_l4_checks(ref: dict[str, Any], tests: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for req in ref.get("requirements") or []:
        if not isinstance(req, dict):
            continue
        st = req.get("snippet_status")
        if st in ("missing", "failed"):
            errors.append(
                f"WARN snippet_status={st} for {req.get('key') or req.get('requirement_key')}"
            )
    return errors


def verify_ladder(
    level: str,
    epic_dir: Path,
    bundle_id: str | None,
) -> list[str]:
    key = _epic_key_from_dir(epic_dir)
    if not key:
        return ["cannot determine epic_key"]
    paths = _artifact_paths(epic_dir, key, archived=False)
    tests = _load_json(paths["tests"])
    cov = _load_json(paths["coverage"])
    precon = _load_json(paths["precon"])
    discover = _load_json(paths["discover"])
    ref = _load_json(paths["ref"])
    if not all([tests, cov, precon, discover, ref]):
        return ["ladder requires ref, coverage, discover, precon, tests at epic root"]

    if level == "L0":
        return _ladder_l0_checks(tests, cov, bundle_id)
    if level == "L1":
        return _ladder_l1_checks(precon, tests, bundle_id)
    if level == "L2":
        return _ladder_l2_checks(discover, tests, bundle_id)
    if level == "L3":
        return _ladder_l3_checks(cov, tests, bundle_id)
    if level == "L4":
        return _ladder_l4_checks(ref, tests)
    return [f"unknown level {level!r}"]


def verify_findings(doc: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if int(doc.get("schema_version") or 0) < 1:
        errors.append("close schema_version must be >= 1")

    kinds = set(contract.get("finding_kinds") or [])
    severities = set(contract.get("finding_severities") or [])
    max_f = int(contract.get("max_findings_emit") or 200)

    findings = doc.get("findings") or []
    if not isinstance(findings, list):
        errors.append("findings must be an array")
        return errors
    if len(findings) > max_f:
        errors.append(f"findings count {len(findings)} exceeds max {max_f}")

    seen: set[str] = set()
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"findings[{i}]: not an object")
            continue
        fid = f.get("id")
        if not fid:
            errors.append(f"findings[{i}]: missing id")
        elif str(fid) in seen:
            errors.append(f"duplicate finding id {fid!r}")
        else:
            seen.add(str(fid))
        if f.get("kind") not in kinds:
            errors.append(f"findings[{i}]: invalid kind {f.get('kind')!r}")
        if f.get("severity") not in severities:
            errors.append(f"findings[{i}]: invalid severity {f.get('severity')!r}")
        if not f.get("summary"):
            errors.append(f"findings[{i}]: missing summary")

    whitelist = set(
        (contract.get("correction_whitelist") or {}).get("allowed_kinds") or []
    )
    for i, c in enumerate(doc.get("corrections") or []):
        if not isinstance(c, dict):
            errors.append(f"corrections[{i}]: not an object")
            continue
        if c.get("kind") not in whitelist:
            errors.append(f"corrections[{i}]: kind not in whitelist")

    for path, s in _walk_strings(doc):
        if TEMP_PATH_RE.search(s):
            errors.append(f"close json contains /temp/ at {path}")

    return errors


def verify_finalize(doc: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors = verify_findings(doc, contract)
    forbidden = set(
        (contract.get("correction_whitelist") or {}).get("forbidden") or []
    )
    for i, c in enumerate(doc.get("corrections") or []):
        if not isinstance(c, dict):
            continue
        kind = c.get("kind")
        if kind in forbidden:
            errors.append(f"corrections[{i}]: forbidden kind {kind!r}")
    return errors


def verify_md_regen(epic_dir: Path, key: str) -> list[str]:
    errors: list[str] = []
    contract = _contract()
    manifest = contract.get("archive_manifest") or {}
    for pattern in manifest.get("root_human_md") or []:
        name = pattern.replace("{epic_key}", key)
        p = epic_dir / name
        if not p.is_file():
            errors.append(f"missing root md: {name}")
            continue
        try:
            body = p.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"cannot read md: {name}")
            continue
        if not body.strip():
            errors.append(f"empty md: {name}")
        if TEMP_PATH_RE.search(body):
            errors.append(f"md contains /temp/: {name}")
    return errors


def verify_archive(epic_dir: Path, key: str, close_path: Path | None) -> list[str]:
    errors: list[str] = []
    ctx = epic_dir / "context"
    if not ctx.is_dir():
        errors.append("missing context/ directory")
        return errors

    for name in (
        f"{key}-ref.json",
        f"{key}-coverage.json",
        f"{key}-discover.json",
        f"{key}-tests.json",
    ):
        if not (ctx / name).is_file():
            errors.append(f"context missing {name}")
        if (epic_dir / name).is_file():
            errors.append(f"stale root json should be archived: {name}")
        deps_stale = epic_dir / "dependencies" / name
        if deps_stale.is_file():
            errors.append(f"stale dependencies json should be archived: {name}")

    precon_ctx = ctx / f"{key}-precon.json"
    if precon_ctx.is_file() and (epic_dir / f"{key}-precon.json").is_file():
        errors.append(f"stale root json should be archived: {key}-precon.json")
    deps_precon = epic_dir / "dependencies" / f"{key}-precon.json"
    if precon_ctx.is_file() and deps_precon.is_file():
        errors.append(f"stale dependencies json should be archived: {key}-precon.json")

    close_in_ctx = ctx / f"{key}-close.json"
    if close_path and close_path.is_file():
        if close_path.resolve() != close_in_ctx.resolve():
            errors.append("-close.json must live under context/ after archive")
    elif not close_in_ctx.is_file():
        errors.append(f"missing context/{key}-close.json")

    if (epic_dir / f"{key}-close.json").is_file():
        errors.append(f"{key}-close.json must not remain at epic root after archive")

    for pattern in (f"{key}-coverage.md", f"{key}-analysis.md", f"{key}-tests.md"):
        if not (epic_dir / pattern).is_file():
            errors.append(f"missing root human md: {pattern}")

    return errors


def _is_console_check_close(chk: dict[str, Any]) -> bool:
    shells = chk.get("shell") or []
    if "console" in shells:
        return True
    detail = " ".join(str(x) for x in (chk.get("detail_lines") or []))
    return bool(re.search(r"\bconsole\b", detail, re.I))


def verify_draft_truth_close(
    epic_dir: Path,
    coverage_path: Path | None,
    ref_path: Path | None,
) -> list[str]:
    """Draft+truth close lint: frozen coverage, round cap, console runtime_probes."""
    key = _epic_key_from_dir(epic_dir)
    if not key:
        return ["cannot determine epic_key"]

    archived = _is_archived(epic_dir, key)
    paths = _artifact_paths(epic_dir, key, archived=archived)
    cov_path = coverage_path or paths["coverage"]
    cov = _load_json(cov_path) if cov_path and cov_path.is_file() else None
    if cov is None:
        return ["missing or invalid coverage for draft_truth close"]

    errors: list[str] = []
    sources = cov.get("sources") if isinstance(cov.get("sources"), dict) else {}
    if not sources.get("coverage_frozen_at"):
        errors.append("coverage.sources.coverage_frozen_at required at close")

    round_n = cov.get("draft_truth_round")
    if round_n is not None and int(round_n) > 2:
        errors.append("draft_truth_round exceeds max_rounds (2)")

    scen_map = cov.get("scenario_coverage_map")
    if not isinstance(scen_map, list):
        errors.append("scenario_coverage_map must be an array at close")

    ref_p = ref_path or paths["ref"]
    ref = _load_json(ref_p) if ref_p and ref_p.is_file() else None
    if ref:
        ref_rows = (ref.get("verification_topology") or {}).get(
            "scenario_capability_rows"
        ) or []
        map_by_scr = {
            str(e["scenario_row_id"]): e
            for e in (scen_map or [])
            if isinstance(e, dict) and e.get("scenario_row_id")
        }
        for row in ref_rows:
            if not isinstance(row, dict):
                continue
            if row.get("promotion") not in ("primary_candidate", "platform_invariant"):
                continue
            rid = str(row.get("id") or "")
            entry = map_by_scr.get(rid)
            if not entry:
                errors.append(f"scenario_coverage_map missing row for {rid} at close")
            elif entry.get("disposition") in (None, "uncovered"):
                errors.append(f"scenario_coverage_map {rid} still uncovered at close")

    for chk in cov.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        if not _is_console_check_close(chk):
            continue
        cid = chk.get("id")
        if chk.get("probe_waived"):
            continue
        probes = chk.get("runtime_probes") or []
        if not probes:
            errors.append(f"{cid}: console check missing runtime_probes at close")

    return errors


def verify_emit(epic_dir: Path, close_path: Path | None) -> list[str]:
    errors: list[str] = []
    key = _epic_key_from_dir(epic_dir)
    if not key:
        return ["cannot determine epic_key"]

    archived = _is_archived(epic_dir, key)
    if archived:
        if not close_path:
            close_path = epic_dir / "context" / f"{key}-close.json"
        if not close_path or not close_path.is_file():
            errors.append("missing --close for archived emit")
        else:
            doc = _load_json(close_path)
            if doc is None:
                errors.append("invalid close json")
            else:
                errors.extend(verify_findings(doc, _contract()))
                verdict = doc.get("epic_verdict")
                if verdict not in ("pass", "pass_with_warnings", "fail"):
                    errors.append(f"invalid epic_verdict {verdict!r}")
        errors.extend(verify_md_regen(epic_dir, key))
        errors.extend(verify_archive(epic_dir, key, close_path))
    else:
        errors.append(
            "emit on pre-archive tree: run archive first or use preflight/ladder modes"
        )

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify CLOSE pipeline artefacts")
    ap.add_argument("--mode", required=True)
    ap.add_argument("--epic-dir", type=Path, required=True)
    ap.add_argument("--close", type=Path, default=None)
    ap.add_argument("--bundle-id", default=None)
    ap.add_argument("--strict-topology", action="store_true")
    ap.add_argument("--strict-principal", action="store_true")
    ap.add_argument("--ref", type=Path, default=None)
    ap.add_argument("--coverage", type=Path, default=None)
    ap.add_argument("--discover", type=Path, default=None)
    ap.add_argument("--precon", type=Path, default=None)
    ap.add_argument("--tests", type=Path, default=None)
    args = ap.parse_args()

    strict_princ = args.strict_principal or args.mode == "principal"

    modes = (
        "preflight",
        "ladder_l0",
        "ladder_l1",
        "ladder_l2",
        "ladder_l3",
        "ladder_l4",
        "topology",
        "principal",
        "findings",
        "finalize",
        "md_regen",
        "archive",
        "emit",
        "draft_truth",
    )
    if args.mode not in modes:
        print(f"unknown mode {args.mode!r}; expected one of {modes}", file=sys.stderr)
        return 2

    epic_dir = args.epic_dir.resolve()
    contract = _contract()
    key = _epic_key_from_dir(epic_dir)

    if args.mode == "preflight":
        errors = verify_preflight(epic_dir, contract)
    elif args.mode.startswith("ladder_"):
        level = args.mode.replace("ladder_", "").upper()
        if level not in ("L0", "L1", "L2", "L3", "L4"):
            print(f"bad ladder mode {args.mode}", file=sys.stderr)
            return 2
        errors = verify_ladder(level, epic_dir, args.bundle_id)
    elif args.mode == "topology":
        errors = verify_topology(
            epic_dir,
            strict_topology=args.strict_topology,
            ref_path=args.ref,
            coverage_path=args.coverage,
            discover_path=args.discover,
            precon_path=args.precon,
            tests_path=args.tests,
        )
    elif args.mode == "principal":
        errors = verify_principal(
            epic_dir,
            strict_principal=strict_princ,
            ref_path=args.ref,
            coverage_path=args.coverage,
            discover_path=args.discover,
            precon_path=args.precon,
            tests_path=args.tests,
        )
    elif args.mode == "findings":
        if not args.close:
            print("--close required for findings mode", file=sys.stderr)
            return 2
        doc = _load_json(args.close.resolve())
        errors = verify_findings(doc, contract) if doc else ["invalid close json"]
    elif args.mode == "finalize":
        if not args.close:
            print("--close required for finalize mode", file=sys.stderr)
            return 2
        doc = _load_json(args.close.resolve())
        errors = verify_finalize(doc, contract) if doc else ["invalid close json"]
    elif args.mode == "md_regen":
        if not key:
            errors = ["cannot determine epic_key"]
        else:
            errors = verify_md_regen(epic_dir, key)
    elif args.mode == "archive":
        if not key:
            errors = ["cannot determine epic_key"]
        else:
            errors = verify_archive(epic_dir, key, args.close)
    elif args.mode == "draft_truth":
        errors = verify_draft_truth_close(
            epic_dir,
            args.coverage,
            args.ref,
        )
    else:
        errors = verify_emit(epic_dir, args.close)

    warnings = [e for e in errors if e.startswith("WARN ")]
    hard = [e for e in errors if not e.startswith("WARN ")]

    if hard:
        print(f"close_verify ({args.mode}) failures:", file=sys.stderr)
        for e in hard:
            print(f"  - {e}", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"  note: {w}")
    print(f"OK close_verify mode={args.mode} epic_dir={epic_dir.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
