#!/usr/bin/env python3
"""
Rebuild coverage Smart Checklist markdown from checks[]; operator md hygiene.

Examples:
  python automation/tools/coverage_md_sync.py --coverage epics/CRT-594/CRT-594-coverage.json --write
  python automation/tools/coverage_md_sync.py --coverage epics/CRT-594/CRT-594-coverage.json --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OPERATOR_HINTS_PATH = REPO_ROOT / "docs" / "coverage-operator-hints.json"

PLATFORM_REUSE_HEADING = "## Platform reuse candidates (verify in Jira)"
DISCOVER_LINE_RE = re.compile(r"^\s*>\s*(Discover|Discovery):", re.M | re.I)
OPERATOR_PREFIX_RE = re.compile(
    r"^\s*>\s*(Oracle|Harness|Verified|Prerequisite|Contrast|Note)\b",
    re.M | re.I,
)
MACHINE_PREFIX_RE = re.compile(
    r"^\s*>\s*(Discover|Discovery):",
    re.M | re.I,
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def load_operator_hints() -> dict[str, Any]:
    return _load_json(OPERATOR_HINTS_PATH) or {}


def verify_operator_md_hygiene(md_body: str) -> list[str]:
    errors: list[str] = []
    if PLATFORM_REUSE_HEADING in md_body:
        errors.append(
            "smart_checklist_markdown must not contain platform reuse heading "
            "(JSON-only platform_reuse_annex)"
        )
    if DISCOVER_LINE_RE.search(md_body):
        errors.append(
            "smart_checklist_markdown must not contain > Discover: or > Discovery: lines"
        )
    return errors


def verify_checks_detail_lines_operator_only(checks: list[Any]) -> list[str]:
    errors: list[str] = []
    for chk in checks:
        if not isinstance(chk, dict):
            continue
        cid = str(chk.get("id") or "?")
        for i, line in enumerate(chk.get("detail_lines") or []):
            line_s = str(line)
            if MACHINE_PREFIX_RE.search(line_s):
                errors.append(
                    f"check {cid} detail_lines[{i}]: machine Discover line "
                    "must be in linker_trace_lines only"
                )
    return errors


def verify_setup_checks_have_operator_hint(checks: list[Any], hints: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    allowed = hints.get("line_prefixes", {}).get("operator_allowed") or []
    allowed_pat = "|".join(re.escape(a) for a in allowed)
    if not allowed_pat:
        return errors
    setup_re = re.compile(rf"^\s*>\s*({allowed_pat})\b", re.M | re.I)
    for chk in checks:
        if not isinstance(chk, dict):
            continue
        cid = str(chk.get("id") or "")
        if not cid.startswith("chk-s"):
            continue
        detail_text = "\n".join(str(x) for x in (chk.get("detail_lines") or []))
        if not setup_re.search(detail_text):
            errors.append(
                f"setup check {cid}: detail_lines need >=1 operator-allowed prefix "
                f"({', '.join(allowed)})"
            )
    return errors


def _section_order(checks: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for chk in checks:
        sec = str(chk.get("section") or "").strip()
        if sec and sec not in seen:
            seen.append(sec)
    return seen


def build_smart_checklist_markdown(coverage: dict[str, Any]) -> str:
    epic_key = str(coverage.get("epic_key") or "EPIC")
    focus = coverage.get("epic_verification_focus") or {}
    focus_stmt = (
        str(focus.get("statement") or "").strip()
        if isinstance(focus, dict)
        else ""
    )
    checks = [c for c in (coverage.get("checks") or []) if isinstance(c, dict)]

    title_line = f"# {epic_key}"
    existing_md = str(coverage.get("smart_checklist_markdown") or "")
    for line in existing_md.splitlines():
        if line.startswith("# "):
            title_line = line.strip()
            break

    lines: list[str] = [title_line, ""]

    if focus_stmt:
        lines.extend(["## Primary focus", "", f"- {focus_stmt}", ""])

    sections = _section_order(checks)
    primary_focus_heading = "## Primary focus"
    for section in sections:
        if section == primary_focus_heading:
            continue
        section_checks = [c for c in checks if str(c.get("section") or "").strip() == section]
        if not section_checks:
            continue
        lines.append(section)
        lines.append("")
        for chk in section_checks:
            scenario = str(chk.get("scenario_line") or "").strip()
            if scenario:
                lines.append(scenario)
            for dl in chk.get("detail_lines") or []:
                dl_s = str(dl).strip()
                if dl_s:
                    lines.append(dl_s)
            lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines) + "\n"


def migrate_discover_lines_to_trace(coverage: dict[str, Any]) -> int:
    """Move > Discover:/Discovery: from detail_lines to linker_trace_lines. Returns count moved."""
    moved = 0
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        detail = list(chk.get("detail_lines") or [])
        trace = list(chk.get("linker_trace_lines") or [])
        keep: list[str] = []
        for line in detail:
            line_s = str(line)
            if MACHINE_PREFIX_RE.search(line_s):
                if line_s not in trace:
                    trace.append(line_s)
                moved += 1
            else:
                keep.append(line_s)
        chk["detail_lines"] = keep
        if trace:
            chk["linker_trace_lines"] = trace
    return moved


def apply_fixture_operator_hints(coverage: dict[str, Any], hints: dict[str, Any]) -> None:
    """Ensure setup checks have human lines from fixture_kinds catalog when empty."""
    kinds = hints.get("fixture_kinds") or {}
    setup_kind = kinds.get("account_group_environment_setup") or {}
    operator_lines = setup_kind.get("operator_lines") or []
    if not operator_lines:
        return
    for chk in coverage.get("checks") or []:
        if not isinstance(chk, dict):
            continue
        cid = str(chk.get("id") or "")
        if not cid.startswith("chk-s"):
            continue
        detail = list(chk.get("detail_lines") or [])
        existing = {str(x).strip() for x in detail}
        for ol in operator_lines:
            ol_s = str(ol).strip()
            if ol_s and ol_s not in existing:
                detail.append(ol_s)
                existing.add(ol_s)
        chk["detail_lines"] = detail


def apply_affordance_operator_hints(coverage: dict[str, Any], hints: dict[str, Any]) -> None:
    """Replace bare Discover-only invariant/adaptive/console checks with human hints."""
    patterns = hints.get("affordance_patterns") or {}
    checks_by_id = {
        str(c.get("id")): c
        for c in (coverage.get("checks") or [])
        if isinstance(c, dict) and c.get("id")
    }

    mapping = {
        "chk-003": "adaptive_instrument_shell",
        "chk-007": "midpoint_invariant",
        "chk-008": "mark_from_midpoint",
        "chk-009": "console_tier_oracle",
    }
    for cid, pat_key in mapping.items():
        chk = checks_by_id.get(cid)
        if not chk:
            continue
        pat = patterns.get(pat_key) or {}
        operator_lines = pat.get("operator_lines") or []
        detail = [str(x) for x in (chk.get("detail_lines") or []) if not MACHINE_PREFIX_RE.search(str(x))]
        existing = {x.strip() for x in detail}
        for ol in operator_lines:
            ol_s = str(ol).strip()
            if ol_s and ol_s not in existing:
                detail.append(ol_s)
        chk["detail_lines"] = detail


def sync_coverage(
    coverage: dict[str, Any],
    *,
    migrate: bool = True,
    apply_hints: bool = True,
) -> dict[str, Any]:
    hints = load_operator_hints()
    if migrate:
        migrate_discover_lines_to_trace(coverage)
    if apply_hints:
        apply_fixture_operator_hints(coverage, hints)
        apply_affordance_operator_hints(coverage, hints)
    coverage["smart_checklist_markdown"] = build_smart_checklist_markdown(coverage)
    return coverage


def verify_coverage_operator_hygiene(
    coverage: dict[str, Any], md_path: Path | None = None
) -> list[str]:
    hints = load_operator_hints()
    md_body = str(coverage.get("smart_checklist_markdown") or "")
    if md_path and md_path.is_file():
        try:
            md_body = md_path.read_text(encoding="utf-8")
        except OSError:
            pass
    errors = verify_operator_md_hygiene(md_body)
    checks = coverage.get("checks") or []
    errors.extend(verify_checks_detail_lines_operator_only(checks))
    if any(
        isinstance(c, dict) and str(c.get("id", "")).startswith("chk-s")
        for c in checks
    ):
        errors.extend(verify_setup_checks_have_operator_hint(checks, hints))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync coverage Smart Checklist markdown")
    ap.add_argument("--coverage", type=Path, required=True)
    ap.add_argument("--write", action="store_true", help="Write -coverage.json and -coverage.md")
    ap.add_argument("--check", action="store_true", help="Verify operator md hygiene only")
    ap.add_argument("--md", type=Path, default=None, help="Optional md path for --check")
    ap.add_argument("--no-hints", action="store_true", help="Skip applying operator hint catalog")
    ap.add_argument("--no-migrate", action="store_true", help="Skip moving Discover lines to trace")
    args = ap.parse_args()

    cov_path = args.coverage.resolve()
    coverage = _load_json(cov_path)
    if coverage is None:
        print(f"cannot read coverage: {cov_path}", file=sys.stderr)
        return 2

    if args.check:
        errors = verify_coverage_operator_hygiene(coverage, args.md)
        if errors:
            print("coverage_md_sync (check) failures:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
        print("OK coverage_md_sync --check")
        return 0

    sync_coverage(
        coverage,
        migrate=not args.no_migrate,
        apply_hints=not args.no_hints,
    )
    md_body = coverage["smart_checklist_markdown"]
    errors = verify_coverage_operator_hygiene(coverage)
    if errors:
        print("coverage_md_sync hygiene failures after sync:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if args.write:
        with cov_path.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(coverage, f, indent=2, ensure_ascii=False)
            f.write("\n")
        md_path = args.md or cov_path.with_suffix(".md")
        md_path.write_text(md_body, encoding="utf-8", newline="\n")
        print(f"Wrote {cov_path}")
        print(f"Wrote {md_path}")
    else:
        print(md_body)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
