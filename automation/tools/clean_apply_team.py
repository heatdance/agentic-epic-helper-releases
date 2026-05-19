#!/usr/bin/env python3
"""Apply team-tier deletes/transforms per docs/clean-contract.json."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/clean-contract.json"
EPIC_KEY_RE = re.compile(r"^(CRT|CRTQA|CRTBL)-\d+$", re.I)


def _load() -> dict:
    with CONTRACT.open(encoding="utf-8") as f:
        return json.load(f)


def _delete_glob(root: Path, pattern: str) -> None:
    for p in root.glob(pattern):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.is_file():
            p.unlink(missing_ok=True)


def apply(root: Path) -> None:
    contract = _load()
    team = contract["team"]
    for pat in team.get("delete_globs", []):
        _delete_glob(root, pat)
    for rel in team.get("delete_paths", []):
        p = root / rel
        if p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    epics = root / "epics"
    if epics.is_dir():
        for child in epics.iterdir():
            if child.is_dir() and EPIC_KEY_RE.match(child.name):
                shutil.rmtree(child, ignore_errors=True)
    clean_md = root / ".cursor/pipelines/clean.md"
    if clean_md.is_file():
        clean_md.unlink()
    router = root / ".cursor/rules/pipeline-router.mdc"
    if router.is_file():
        text = router.read_text(encoding="utf-8")
        lines = [
            ln
            for ln in text.splitlines()
            if "CLEAN:" not in ln and "clean.md" not in ln and "clean_pipeline" not in ln
        ]
        filtered = []
        skip = False
        for ln in lines:
            if ln.strip().startswith("5. **`CLEAN:`**"):
                skip = True
                continue
            if skip and ln.strip().startswith("6."):
                skip = False
            if skip:
                continue
            filtered.append(ln)
        router.write_text("\n".join(filtered) + "\n", encoding="utf-8")
    for t in team.get("transform_paths", []):
        src = root / t["path"]
        dst = root / t["target"]
        if src.is_file():
            shutil.copy2(src, dst)
            src.unlink(missing_ok=True)
    cal = contract.get("calibrate", {})
    for pat in cal.get("team_delete_globs", []):
        _delete_glob(root, pat)

    # Tier-specific T1 docs + harness-map strip
    t1_script = REPO_ROOT / "automation/tools/clean_apply_t1_docs.py"
    subprocess.run(
        [sys.executable, str(t1_script), "--root", str(root), "--tier", "team"],
        check=True,
        cwd=REPO_ROOT,
    )


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    args = p.parse_args()
    apply(args.root.resolve())
    print(f"Applied team strip to {args.root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
