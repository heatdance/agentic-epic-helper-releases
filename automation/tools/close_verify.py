#!/usr/bin/env python3
"""
Verify CLOSE pipeline artefacts and post-archive layout.

Examples:
  python automation/tools/close_verify.py --mode preflight --epic-dir epics/CRT-639

  python automation/tools/close_verify.py --mode ladder_l0 --epic-dir epics/CRT-639 \\
    --close epics/CRT-639/CRT-639-close.json

  python automation/tools/close_verify.py --mode emit --epic-dir epics/CRT-639 \\
    --close epics/CRT-639/context/CRT-639-close.json
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
TEMP_PATH_RE = re.compile(r"(?:^|[/\\])temp(?:[/\\]|$)|/temp/", re.I)
CRTQA_KEY_RE = re.compile(r"\bCRTQA-\d+\b", re.I)
SECRET_LIKE_RE = re.compile(
    r"(password\s*[:=]|Bearer\s+|api[_-]?key\s*[:=])", re.I
)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _contract() -> dict[str, Any]:
    return _load_json(CONTRACT_PATH) or {}


def _epic_key_from_dir(epic_dir: Path) -> str | None:
    name = epic_dir.name
    if re.match(r"^[A-Z]+-\d+$", name):
        return name
    for p in epic_dir.glob("*-ref.json"):
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
    base = epic_dir / "context" if archived else epic_dir
    return {
        "ref": base / f"{key}-ref.json",
        "coverage": base / f"{key}-coverage.json",
        "discover": base / f"{key}-discover.json",
        "precon": base / f"{key}-precon.json",
        "tests": base / f"{key}-tests.json",
        "analysis": base / f"{key}-analysis.json",
    }


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
    required = pre.get("required_artifacts") or []
    for pattern in required:
        name = pattern.replace("{epic_key}", key)
        if not (epic_dir / name).is_file():
            errors.append(f"missing required artifact: {name}")

    optional = pre.get("optional_artifacts") or []
    for pattern in optional:
        name = pattern.replace("{epic_key}", key)
        if not (epic_dir / name).is_file():
            errors.append(f"WARN optional missing: {name}")

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
        f"{key}-precon.json",
        f"{key}-tests.json",
    ):
        if not (ctx / name).is_file():
            errors.append(f"context missing {name}")
        if (epic_dir / name).is_file():
            errors.append(f"stale root json should be archived: {name}")

    close_in_ctx = ctx / f"{key}-close.json"
    if close_path and close_path.is_file():
        if close_path.resolve() != close_in_ctx.resolve():
            errors.append("-close.json must live under context/ after archive")
    elif not close_in_ctx.is_file():
        errors.append(f"missing context/{key}-close.json")

    if (epic_dir / f"{key}-close.json").is_file():
        errors.append(f"{key}-close.json must not remain at epic root after archive")

    for pattern in (f"{key}-coverage.md", f"{key}-analysis.md", f"{key}-tests.md", f"{key}-precon.md"):
        if not (epic_dir / pattern).is_file():
            errors.append(f"missing root human md: {pattern}")

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
    args = ap.parse_args()

    modes = (
        "preflight",
        "ladder_l0",
        "ladder_l1",
        "ladder_l2",
        "ladder_l3",
        "ladder_l4",
        "findings",
        "finalize",
        "md_regen",
        "archive",
        "emit",
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
