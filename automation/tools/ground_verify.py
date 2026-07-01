#!/usr/bin/env python3
"""
Verify GROUND mutations on -coverage.json (runtime probes).

Examples:
  python automation/tools/ground_verify.py --mode emit \\
    --coverage automation/tools/fixtures/ground/ground-594-pass-coverage-slice.json \\
    --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "ground-contract.json"
OPERATOR_HINTS_PATH = REPO_ROOT / "docs" / "coverage-operator-hints.json"
PLATFORM_REUSE_HEADING = "## Platform reuse candidates (verify in Jira)"
MACHINE_LINE_RE = re.compile(r"^\s*>\s*(Discover|Discovery):", re.M | re.I)
FORBIDDEN_MD_ORACLE = re.compile(
    r"\b(console_show_prices_first_tier|first_tier_quote|"
    r"text_configuration_closest_gte_qty)\b"
)
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CONSOLE_HINT = re.compile(
    r"\b(console|show\s+prices|backup_price|daily_data|agent_event)\b",
    re.I,
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _is_console_check(chk: dict[str, Any]) -> bool:
    if chk.get("verification_role") not in (None, "primary"):
        return False
    cid = str(chk.get("id") or "")
    if cid.startswith("chk-s"):
        return False
    if chk.get("coverage_thread") == "environment_setup":
        return False
    blob = " ".join(
        [
            str(chk.get("section") or ""),
            str(chk.get("scenario_line") or ""),
            "\n".join(str(x) for x in (chk.get("detail_lines") or [])),
        ]
    )
    return bool(CONSOLE_HINT.search(blob))


def verify_emit(coverage: dict[str, Any], ref: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    checks = coverage.get("checks") or []
    if not isinstance(checks, list):
        return ["checks must be an array"]

    cov_pass = coverage.get("coverage_pass")
    if cov_pass not in (1, 2):
        errors.append("coverage_pass must be 1 or 2 before ground")

    for i, chk in enumerate(checks):
        if not isinstance(chk, dict):
            continue
        if not _is_console_check(chk):
            continue
        cid = chk.get("id", f"index-{i}")
        probes = chk.get("runtime_probes") or []
        waived = chk.get("probe_waived") is True
        if waived:
            if not chk.get("waiver_reason"):
                errors.append(f"{cid}: probe_waived without waiver_reason")
            continue
        if not isinstance(probes, list) or len(probes) < 1:
            errors.append(f"{cid}: console-tagged check missing runtime_probes")
            continue
        for j, probe in enumerate(probes):
            if not isinstance(probe, dict):
                errors.append(f"{cid} runtime_probes[{j}]: not object")
                continue
            outcome = probe.get("outcome")
            if outcome not in ("success", "failed", "blocked"):
                errors.append(f"{cid} runtime_probes[{j}]: invalid outcome {outcome!r}")
            if outcome == "success" and not probe.get("verified_syntax"):
                errors.append(f"{cid} runtime_probes[{j}]: success without verified_syntax")

    md = str(coverage.get("smart_checklist_markdown") or "")
    if FORBIDDEN_MD_ORACLE.search(md):
        errors.append("smart_checklist_markdown still contains internal oracle enum tokens")
    if PLATFORM_REUSE_HEADING in md:
        errors.append(
            "smart_checklist_markdown must not contain platform reuse heading"
        )
    if MACHINE_LINE_RE.search(md):
        errors.append(
            "smart_checklist_markdown must not contain > Discover: or > Discovery: lines"
        )

    def walk(obj: Any, path: str = "$") -> None:
        if isinstance(obj, str):
            if TEMP_PATH_RE.search(obj):
                errors.append(f"coverage contains temp path at {path}")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for idx, v in enumerate(obj):
                walk(v, f"{path}[{idx}]")

    walk(coverage)
    _ = ref  # reserved for future console surface cross-check
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify GROUND coverage mutations")
    ap.add_argument("--mode", choices=("emit",), required=True)
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--ref", type=Path, required=True)
    args = ap.parse_args()

    coverage = _load_json(args.coverage.resolve())
    ref = _load_json(args.ref.resolve())
    if coverage is None:
        print(f"cannot read coverage: {args.coverage}", file=sys.stderr)
        return 2
    if ref is None:
        print(f"cannot read ref: {args.ref}", file=sys.stderr)
        return 2
    _load_json(CONTRACT_PATH)

    errors = verify_emit(coverage, ref)
    if errors:
        print("ground_verify (emit) failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK ground_verify mode=emit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
