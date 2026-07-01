#!/usr/bin/env python3
"""
Apply CLOSE archive manifest: move JSON (and tests/) into context/, keep four md at root.

Idempotent when layout already matches contract.

Example:
  python automation/tools/close_archive.py --epic-dir epics/CRT-639 \\
    --close epics/CRT-639/CRT-639-close.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "close-contract.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _save_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _epic_key(epic_dir: Path, close_path: Path) -> str:
    stem = close_path.stem
    if stem.endswith("-close"):
        return stem[: -len("-close")]
    return epic_dir.name


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply CLOSE archive manifest")
    ap.add_argument("--epic-dir", type=Path, required=True)
    ap.add_argument("--close", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    epic_dir = args.epic_dir.resolve()
    close_path = args.close.resolve()
    key = _epic_key(epic_dir, close_path)

    doc = _load_json(close_path)
    if doc is None:
        print(f"cannot read close json: {close_path}", file=sys.stderr)
        return 2

    ctx = epic_dir / "context"
    moved: list[str] = []

    def _move(src: Path, dst: Path) -> None:
        if not src.exists():
            return
        if dst.exists() and src.resolve() == dst.resolve():
            return
        if dst.exists():
            print(f"skip (dest exists): {dst}", file=sys.stderr)
            return
        moved.append(f"{src.name} -> context/{dst.name}")
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

    if not args.dry_run:
        ctx.mkdir(parents=True, exist_ok=True)

    for p in sorted(epic_dir.glob(f"{key}-*.json")):
        if p.name.endswith("-close.json") and p == close_path:
            dst = ctx / p.name
            _move(p, dst)
            continue
        if p.parent == epic_dir:
            _move(p, ctx / p.name)

    tests_dir = epic_dir / "tests"
    if tests_dir.is_dir():
        _move(tests_dir, ctx / "tests")

    helper_dir = epic_dir / "helper"
    if helper_dir.is_dir():
        dst_helper = ctx / "helper"
        if dst_helper.exists():
            print(f"skip helper archive: {dst_helper} exists", file=sys.stderr)
        else:
            _move(helper_dir, dst_helper)

    # close.json written at root during pipeline — ensure it ends in context
    root_close = epic_dir / f"{key}-close.json"
    ctx_close = ctx / f"{key}-close.json"
    if close_path.is_file() and close_path.parent == epic_dir:
        _move(close_path, ctx_close)
    elif root_close.is_file() and not ctx_close.is_file():
        _move(root_close, ctx_close)

    archive = doc.setdefault("archive", {})
    archive["layout_version"] = 1
    archive["archived_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    archive["manifest_applied"] = not args.dry_run
    archive["root_md"] = [
        f"{key}-coverage.md",
        f"{key}-analysis.md",
        f"{key}-tests.md",
    ]
    archive["context_json"] = sorted(
        p.name for p in ctx.glob("*.json")
    ) if ctx.is_dir() else []

    if not args.dry_run:
        target = ctx_close if ctx_close.is_file() else close_path
        _save_json(target, doc)

    print(f"OK close_archive dry_run={args.dry_run} moved={len(moved)}")
    for m in moved:
        print(f"  {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
