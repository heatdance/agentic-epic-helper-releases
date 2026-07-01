#!/usr/bin/env python3
"""
Preflight and compare gates for /epic-calibrate.

Examples:
  python automation/tools/calibrate_verify.py --mode gold_gate --epic CRT-639
  python automation/tools/calibrate_verify.py --mode gold_distinct --epic CRT-639
  python automation/tools/calibrate_verify.py --mode compare --epic CRT-639
  python automation/tools/calibrate_verify.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "calibrate-contract.json"
EPIC_KEY_RE = re.compile(r"^[A-Z]+-\d+$")
GOLD_AS_OF_RE = re.compile(r"gold_as_of:\s*(\d{4}-\d{2}-\d{2})", re.I)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _contract() -> dict[str, Any]:
    return _load_json(CONTRACT_PATH) or {}


def _gold_dir(repo_root: Path, epic_key: str, contract: dict[str, Any]) -> Path:
    pattern = (contract.get("gold_dir_pattern") or "{gold_root}/{epic_key}-gold").format(
        gold_root=contract.get("gold_root", ".cursor/calibrate"),
        epic_key=epic_key,
    )
    return repo_root / pattern.replace("\\", "/")


def _prod_dir(repo_root: Path, epic_key: str, contract: dict[str, Any]) -> Path:
    pattern = contract.get("prod_root_pattern") or "epics/{epic_key}"
    return repo_root / pattern.format(epic_key=epic_key)


def _resolve_artifact(
    repo_root: Path,
    epic_key: str,
    suffix: str,
    *,
    gold: bool,
    contract: dict[str, Any],
) -> Path | None:
    """suffix e.g. coverage -> <KEY>-coverage.json"""
    name = f"{epic_key}-{suffix}.json"
    if gold:
        path = _gold_dir(repo_root, epic_key, contract) / name
        return path if path.is_file() else None
    prod = _prod_dir(repo_root, epic_key, contract)
    ctx_path = prod / "context" / name
    if ctx_path.is_file():
        return ctx_path
    root_path = prod / name
    return root_path if root_path.is_file() else None


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_sha256(path: Path) -> str:
    obj = _load_json(path)
    if obj is None:
        raise ValueError(f"invalid JSON: {path}")
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_gold_gate(repo_root: Path, epic_key: str, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    gold = _gold_dir(repo_root, epic_key, contract)
    if not gold.is_dir():
        errors.append(f"missing gold directory: {gold.relative_to(repo_root)}")
        return errors
    for pattern in contract.get("required_gold_files") or []:
        name = pattern.format(epic_key=epic_key)
        path = gold / name
        if not path.is_file():
            errors.append(f"missing required gold file: {path.relative_to(repo_root)}")
    integrity = contract.get("gold_integrity") or {}
    if integrity.get("require_readme"):
        readme = gold / (integrity.get("readme_filename") or "README.md")
        if not readme.is_file():
            errors.append(f"missing gold README: {readme.relative_to(repo_root)}")
        else:
            text = readme.read_text(encoding="utf-8")
            pat = integrity.get("gold_as_of_pattern") or r"gold_as_of:\s*\d{4}-\d{2}-\d{2}"
            if not re.search(pat, text, re.I):
                errors.append(
                    f"gold README missing gold_as_of (YYYY-MM-DD): {readme.relative_to(repo_root)}"
                )
    return errors


def verify_gold_readme(repo_root: Path, epic_key: str, contract: dict[str, Any]) -> list[str]:
    """README + gold_as_of only (gold_gate includes this when require_readme)."""
    errors: list[str] = []
    gold = _gold_dir(repo_root, epic_key, contract)
    integrity = contract.get("gold_integrity") or {}
    readme = gold / (integrity.get("readme_filename") or "README.md")
    if not readme.is_file():
        errors.append(f"missing gold README: {readme.relative_to(repo_root)}")
        return errors
    text = readme.read_text(encoding="utf-8")
    if not GOLD_AS_OF_RE.search(text):
        errors.append(
            f"gold README missing gold_as_of: YYYY-MM-DD line in {readme.relative_to(repo_root)}"
        )
    return errors


def verify_gold_distinct(repo_root: Path, epic_key: str, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pairs: list[tuple[str, Path, Path]] = []
    for pattern in contract.get("required_gold_files") or []:
        name = pattern.format(epic_key=epic_key)
        if not name.endswith(".json"):
            continue
        suffix = name.replace(f"{epic_key}-", "").replace(".json", "")
        gold_path = _resolve_artifact(repo_root, epic_key, suffix, gold=True, contract=contract)
        prod_path = _resolve_artifact(repo_root, epic_key, suffix, gold=False, contract=contract)
        if gold_path is None:
            errors.append(f"missing gold file for distinct check: {name}")
            continue
        if prod_path is None:
            errors.append(f"missing prod file for distinct check: {name}")
            continue
        pairs.append((suffix, gold_path, prod_path))

    if errors:
        return errors

    for suffix, gold_path, prod_path in pairs:
        if _file_sha256(gold_path) == _file_sha256(prod_path):
            errors.append(
                f"GOLD_NOT_DISTINCT: {suffix} byte-identical to prod "
                f"({gold_path.relative_to(repo_root)} == {prod_path.relative_to(repo_root)})"
            )
            continue
        try:
            if _normalized_sha256(gold_path) == _normalized_sha256(prod_path):
                errors.append(
                    f"GOLD_NOT_DISTINCT: {suffix} normalized-json-identical to prod"
                )
        except ValueError as e:
            errors.append(str(e))
    return errors


def _check_ids_signal(prod_cov: dict[str, Any], gold_cov: dict[str, Any]) -> dict[str, Any]:
    prod_ids = {str(c.get("id")) for c in (prod_cov.get("checks") or []) if c.get("id")}
    gold_ids = {str(c.get("id")) for c in (gold_cov.get("checks") or []) if c.get("id")}
    only_prod = sorted(prod_ids - gold_ids)
    only_gold = sorted(gold_ids - prod_ids)
    actionable = bool(only_prod or only_gold)
    return {
        "id": "check_ids",
        "actionable": actionable,
        "detail": {"only_prod": only_prod, "only_gold": only_gold},
    }


def _bundle_covers_signal(prod_tests: dict[str, Any], gold_tests: dict[str, Any]) -> dict[str, Any]:
    def _map(tests: dict[str, Any]) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for b in tests.get("test_bundles") or []:
            if not isinstance(b, dict):
                continue
            bid = b.get("bundle_id")
            if not bid:
                continue
            ids = b.get("covers_check_ids") or []
            out[str(bid)] = sorted(str(x) for x in ids)
        return out

    prod_m = _map(prod_tests)
    gold_m = _map(gold_tests)
    diffs: list[dict[str, Any]] = []
    for bid in sorted(set(prod_m) | set(gold_m)):
        if prod_m.get(bid) != gold_m.get(bid):
            diffs.append(
                {
                    "bundle_id": bid,
                    "prod": prod_m.get(bid),
                    "gold": gold_m.get(bid),
                }
            )
    return {
        "id": "bundle_covers",
        "actionable": bool(diffs),
        "detail": {"diffs": diffs},
    }


def _excluded_checks_signal(prod_tests: dict[str, Any], gold_tests: dict[str, Any]) -> dict[str, Any]:
    def _map(tests: dict[str, Any]) -> dict[str, str]:
        out: dict[str, str] = {}
        for row in tests.get("excluded_checks_with_reason") or []:
            if not isinstance(row, dict):
                continue
            cid = row.get("check_id")
            if cid:
                out[str(cid)] = str(row.get("reason") or "")
        return out

    prod_m = _map(prod_tests)
    gold_m = _map(gold_tests)
    diffs: list[dict[str, Any]] = []
    for cid in sorted(set(prod_m) | set(gold_m)):
        if prod_m.get(cid) != gold_m.get(cid):
            diffs.append(
                {
                    "check_id": cid,
                    "prod_reason": prod_m.get(cid),
                    "gold_reason": gold_m.get(cid),
                }
            )
    return {
        "id": "excluded_checks",
        "actionable": bool(diffs),
        "detail": {"diffs": diffs},
    }


def _obligations_signal(prod_cov: dict[str, Any], gold_cov: dict[str, Any]) -> dict[str, Any]:
    def _snap(cov: dict[str, Any]) -> dict[str, dict[str, Any]]:
        raw = cov.get("obligations_coverage") or {}
        if not isinstance(raw, dict):
            return {}
        out: dict[str, dict[str, Any]] = {}
        for oid, row in raw.items():
            if not isinstance(row, dict):
                continue
            out[str(oid)] = {
                "status": row.get("status"),
                "check_id": row.get("check_id"),
                "excluded_reason": row.get("excluded_reason"),
            }
        return out

    prod_s = _snap(prod_cov)
    gold_s = _snap(gold_cov)
    diffs: list[dict[str, Any]] = []
    for oid in sorted(set(prod_s) | set(gold_s)):
        if prod_s.get(oid) != gold_s.get(oid):
            diffs.append({"obligation_id": oid, "prod": prod_s.get(oid), "gold": gold_s.get(oid)})
    return {
        "id": "obligations_coverage",
        "actionable": bool(diffs),
        "detail": {"diffs": diffs},
    }


def _checklist_hash_signal(prod_cov: dict[str, Any], gold_cov: dict[str, Any]) -> dict[str, Any]:
    prod_md = prod_cov.get("smart_checklist_markdown")
    gold_md = gold_cov.get("smart_checklist_markdown")
    if prod_md is None and gold_md is None:
        return {"id": "checklist_hash", "actionable": False, "detail": {"skipped": "both_missing"}}
    if prod_md is None or gold_md is None:
        return {
            "id": "checklist_hash",
            "actionable": True,
            "detail": {"prod_present": prod_md is not None, "gold_present": gold_md is not None},
        }
    ph = hashlib.sha256(str(prod_md).encode("utf-8")).hexdigest()
    gh = hashlib.sha256(str(gold_md).encode("utf-8")).hexdigest()
    return {
        "id": "checklist_hash",
        "actionable": ph != gh,
        "detail": {"prod_hash": ph[:12], "gold_hash": gh[:12]},
    }


def run_compare(
    repo_root: Path, epic_key: str, contract: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str]]:
    """Returns (report, errors). errors non-empty => exit 1."""
    errors: list[str] = []
    prod_cov_path = _resolve_artifact(repo_root, epic_key, "coverage", gold=False, contract=contract)
    prod_tests_path = _resolve_artifact(repo_root, epic_key, "tests", gold=False, contract=contract)
    gold_cov_path = _resolve_artifact(repo_root, epic_key, "coverage", gold=True, contract=contract)
    gold_tests_path = _resolve_artifact(repo_root, epic_key, "tests", gold=True, contract=contract)

    for label, path in (
        ("prod coverage", prod_cov_path),
        ("prod tests", prod_tests_path),
        ("gold coverage", gold_cov_path),
        ("gold tests", gold_tests_path),
    ):
        if path is None:
            errors.append(f"compare: missing {label}")

    if errors:
        return None, errors

    assert prod_cov_path and prod_tests_path and gold_cov_path and gold_tests_path
    prod_cov = _load_json(prod_cov_path)
    prod_tests = _load_json(prod_tests_path)
    gold_cov = _load_json(gold_cov_path)
    gold_tests = _load_json(gold_tests_path)
    if prod_cov is None or prod_tests is None or gold_cov is None or gold_tests is None:
        return None, ["compare: failed to parse required JSON"]

    signals = [
        _check_ids_signal(prod_cov, gold_cov),
        _bundle_covers_signal(prod_tests, gold_tests),
        _excluded_checks_signal(prod_tests, gold_tests),
        _obligations_signal(prod_cov, gold_cov),
        _checklist_hash_signal(prod_cov, gold_cov),
    ]
    actionable_count = sum(1 for s in signals if s.get("actionable"))
    outcome = "DELTA_REVIEW" if actionable_count > 0 else "NO_ACTIONABLE_DELTA"

    report = {
        "schema_version": 2,
        "epic_key": epic_key,
        "outcome": outcome,
        "actionable_delta_count": actionable_count,
        "signals": signals,
        "prod_paths": {
            "coverage": str(prod_cov_path.relative_to(repo_root)).replace("\\", "/"),
            "tests": str(prod_tests_path.relative_to(repo_root)).replace("\\", "/"),
        },
        "gold_paths": {
            "coverage": str(gold_cov_path.relative_to(repo_root)).replace("\\", "/"),
            "tests": str(gold_tests_path.relative_to(repo_root)).replace("\\", "/"),
        },
    }
    return report, []


def verify_prod_gate(repo_root: Path, epic_key: str, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prod = _prod_dir(repo_root, epic_key, contract)
    if not prod.is_dir():
        errors.append(f"missing production epic directory: {prod.relative_to(repo_root)}")
        return errors
    has_root_md = any(prod.glob("*.md"))
    ctx = prod / "context"
    has_ctx_json = ctx.is_dir() and any(ctx.glob("*.json"))
    if not has_root_md and not has_ctx_json:
        errors.append(
            "production gate: need at least one *.md at epic root or *.json under context/"
        )
    return errors


def _write_compare_report(
    repo_root: Path, epic_key: str, contract: dict[str, Any], report: dict[str, Any]
) -> Path | None:
    pattern = contract.get("compare_report_filename_pattern") or "{epic_key}-compare.json"
    reports_dir = repo_root / (contract.get("reports_dir") or ".cursor/calibrate/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / pattern.format(epic_key=epic_key)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def run_self_test() -> int:
    fixtures = REPO_ROOT / "automation" / "tools" / "fixtures" / "calibrate"
    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(f"{name}: {detail}")

    # identical
    root = fixtures / "identical"
    epic = "CRT-999"
    contract = _contract()
    d_err = verify_gold_distinct(root, epic, contract)
    check("identical gold_distinct fails", bool(d_err), str(d_err))
    report, c_err = run_compare(root, epic, contract)
    check("identical compare no err", not c_err, str(c_err))
    check(
        "identical compare outcome",
        report is not None and report.get("outcome") == "NO_ACTIONABLE_DELTA",
        str(report),
    )

    # diff_checks
    root = fixtures / "diff_checks"
    epic = "CRT-998"
    d_err = verify_gold_distinct(root, epic, contract)
    check("diff gold_distinct ok", not d_err, str(d_err))
    report, c_err = run_compare(root, epic, contract)
    check("diff compare outcome", report is not None and report.get("outcome") == "DELTA_REVIEW", str(report))
    check("diff actionable count", report is not None and (report.get("actionable_delta_count") or 0) >= 1, "")

    # missing_readme
    root = fixtures / "missing_readme"
    epic = "CRT-997"
    g_err = verify_gold_gate(root, epic, contract)
    check("missing_readme gold_gate fails", bool(g_err), str(g_err))

    if failures:
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        return 1
    print("OK self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate preflight and compare gates")
    parser.add_argument(
        "--mode",
        choices=(
            "gold_gate",
            "prod_gate",
            "gold_distinct",
            "gold_readme",
            "compare",
        ),
    )
    parser.add_argument("--epic", help="Epic key e.g. CRT-639")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: parent of automation/tools)",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="Optional path for compare JSON (default: .cursor/calibrate/reports/<KEY>-compare.json)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture self-tests",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if not args.mode or not args.epic:
        parser.error("--mode and --epic required unless --self-test")

    epic_key = args.epic.strip().upper()
    if not EPIC_KEY_RE.match(epic_key):
        print(f"invalid epic key: {args.epic}", file=sys.stderr)
        return 2
    contract = _contract()
    if not contract:
        print(f"missing or invalid contract: {CONTRACT_PATH}", file=sys.stderr)
        return 2
    repo_root = args.repo_root.resolve()

    if args.mode == "gold_gate":
        errors = verify_gold_gate(repo_root, epic_key, contract)
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print(f"OK gold_gate {epic_key}")
        return 0

    if args.mode == "gold_readme":
        errors = verify_gold_readme(repo_root, epic_key, contract)
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print(f"OK gold_readme {epic_key}")
        return 0

    if args.mode == "gold_distinct":
        errors = verify_gold_distinct(repo_root, epic_key, contract)
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            print("outcome=GOLD_NOT_DISTINCT", file=sys.stderr)
            return 1
        print(f"OK gold_distinct {epic_key}")
        return 0

    if args.mode == "prod_gate":
        errors = verify_prod_gate(repo_root, epic_key, contract)
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print(f"OK prod_gate {epic_key}")
        return 0

    if args.mode == "compare":
        report, errors = run_compare(repo_root, epic_key, contract)
        if errors or report is None:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        out_path = args.report_json
        if out_path is None:
            written = _write_compare_report(repo_root, epic_key, contract, report)
            if written:
                report = {**report, "report_path": str(written.relative_to(repo_root)).replace("\\", "/")}
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"outcome={report['outcome']}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
