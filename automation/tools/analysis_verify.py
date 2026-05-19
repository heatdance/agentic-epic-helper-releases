#!/usr/bin/env python3
"""
Verify ANALYSE -analysis.json (schema v2).

Examples:
  python automation/tools/analysis_verify.py --mode gaps \\
    --analysis epics/CRT-642/CRT-642-analysis.json

  python automation/tools/analysis_verify.py --mode emit \\
    --analysis epics/CRT-642/CRT-642-analysis.json \\
    --md epics/CRT-642/CRT-642-analysis.md
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
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
FORBIDDEN_MD_HEADINGS = re.compile(
    r"^##\s+(Summary|Questions)\s*$", re.I | re.M
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


def _contract() -> dict[str, Any]:
    return _load_json(CONTRACT_PATH) or {}


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
            ptr.get(k) for k in ("check_id", "obligation_id", "requirement_key")
        ):
            errors.append(f"gaps[{i}]: pointers need check_id, obligation_id, or requirement_key")
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
    errors = verify_gaps(doc, _contract()) + verify_downstream(doc)
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify ANALYSE artifacts")
    ap.add_argument("--mode", choices=("gaps", "downstream", "emit"), required=True)
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--md", type=Path, default=None)
    args = ap.parse_args()

    doc = _load_json(args.analysis.resolve())
    if doc is None:
        print(f"cannot read analysis: {args.analysis}", file=sys.stderr)
        return 2

    contract = _contract()
    if args.mode == "gaps":
        errors = verify_gaps(doc, contract)
    elif args.mode == "downstream":
        errors = verify_downstream(doc)
    else:
        errors = verify_emit(doc, args.md)

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
