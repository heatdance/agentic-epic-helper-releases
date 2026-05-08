#!/usr/bin/env python3
"""
Lightweight verifier for `.cursor/benchmark/runs/<suite>/` hub layout.

Exits non-zero when required paths are missing. Intended from
`/crtqa-benchmark` and CI-style checks — see docs/benchmark-contract.md.

Examples:
  python automation/tools/benchmark_verify.py --suite-dir .cursor/benchmark/runs/my-suite
  python automation/tools/benchmark_verify.py --suite-dir .cursor/benchmark/runs/my-suite --strict-manifest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(20):
        if (cur / ".git").exists() or (cur / "README.md").exists() and (cur / "docs").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path.cwd()


def _load_json(path: Path) -> dict | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _attempt_has_prompt_stub(adir: Path) -> bool:
    """Hub attempts may use legacy PROMPT.md or phase stubs PROMPT-prep.md, etc."""
    if (adir / "PROMPT.md").is_file():
        return True
    for p in sorted(adir.glob("PROMPT-*.md")):
        if p.is_file():
            return True
    return False


def _check_artifacts(
    suite_dir: Path,
    attempt_dir: Path,
    done: dict,
    repo_root: Path,
    errors: list[str],
) -> None:
    arts = done.get("artifacts")
    if not isinstance(arts, list):
        errors.append(f"{attempt_dir.name}: DONE.json missing list 'artifacts'")
        return
    for i, rel in enumerate(arts):
        if not isinstance(rel, str) or not rel.strip():
            errors.append(f"{attempt_dir.name}: artifacts[{i}] invalid")
            continue
        raw = Path(rel)
        candidates = []
        if raw.is_absolute():
            candidates.append(raw)
        else:
            candidates.append((attempt_dir / raw).resolve())
            candidates.append((repo_root / raw).resolve())
        if not any(c.is_file() for c in candidates):
            errors.append(f"{attempt_dir.name}: missing artifact {rel}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify benchmark hub suite folder layout.")
    ap.add_argument(
        "--suite-dir",
        type=Path,
        required=True,
        help="Suite folder (.cursor/benchmark/runs/<suite_id>/)",
    )
    ap.add_argument(
        "--strict-manifest",
        action="store_true",
        help="Require _manifest.json to exist",
    )
    args = ap.parse_args()

    suite_dir = args.suite_dir.resolve()
    repo_root = _repo_root(suite_dir)
    errors: list[str] = []

    if not suite_dir.is_dir():
        print(f"suite-dir not found: {suite_dir}", file=sys.stderr)
        return 2

    manifest = suite_dir / "_manifest.json"
    if args.strict_manifest and not manifest.is_file():
        errors.append("_manifest.json missing (strict-manifest)")

    attempt_dirs = sorted(
        [d for d in suite_dir.iterdir() if d.is_dir() and d.name.startswith("attempt-")]
    )
    if not attempt_dirs:
        errors.append("no attempt-<nn>/ directories")

    seen_done = False
    for adir in attempt_dirs:
        done_path = adir / "DONE.json"
        if done_path.is_file():
            seen_done = True
            done_obj = _load_json(done_path)
            if done_obj is None:
                errors.append(f"{adir.name}: DONE.json unreadable")
            else:
                _check_artifacts(suite_dir, adir, done_obj, repo_root, errors)

    # Soft expectation: prompt pack exists unless operator deleted early
    for adir in attempt_dirs:
        if not _attempt_has_prompt_stub(adir):
            errors.append(
                f"{adir.name}: PROMPT.md or PROMPT-*.md missing (recommended)"
            )

    if attempt_dirs and not seen_done:
        errors.append("no DONE.json in any attempt (required before aggregate/verify gate)")

    if errors:
        print("benchmark_verify failures:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK hub layout under {suite_dir.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
