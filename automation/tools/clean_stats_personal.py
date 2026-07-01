#!/usr/bin/env python3
"""Backup/restore personal-only CRTQA stats artefacts during CLEAN Phase T.

Team strip deletes stats/epic-stats/** in the shared working tree, which removes
gitignored state/, raw/, and latest-*.md even though personal tier keeps them.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/clean-contract.json"


def _load() -> dict:
    import json

    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _preserve_globs(contract: dict) -> list[str]:
    return list(contract.get("stats_personal_preserve", {}).get("globs", []))


def _backup_dir(contract: dict) -> Path:
    rel = contract.get("stats_personal_preserve", {}).get(
        "backup_dir", "automation/temp/clean/stats-personal-backup"
    )
    return REPO_ROOT / rel


def _copy_glob(root: Path, pattern: str, dest_root: Path) -> list[str]:
    copied: list[str] = []
    for src in root.glob(pattern):
        rel = src.relative_to(root)
        dst = dest_root / rel
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied.append(str(rel).replace("\\", "/"))
    return copied


def backup(root: Path, contract: dict) -> int:
    stats_root = root / "stats/epic-stats"
    if not stats_root.is_dir():
        print("stats/epic-stats missing — nothing to backup")
        return 0
    dest = _backup_dir(contract)
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    all_copied: list[str] = []
    for pat in _preserve_globs(contract):
        full = f"stats/epic-stats/{pat}"
        all_copied.extend(_copy_glob(root, full, dest))
    manifest = dest / "manifest.txt"
    manifest.write_text("\n".join(sorted(all_copied)) + ("\n" if all_copied else ""), encoding="utf-8")
    print(f"Backed up {len(all_copied)} path(s) to {dest.relative_to(REPO_ROOT)}")
    return 0


def restore(root: Path, contract: dict) -> int:
    src_root = _backup_dir(contract)
    if not src_root.is_dir() or not (src_root / "manifest.txt").is_file():
        print("No stats personal backup — skip restore", file=sys.stderr)
        return 0
    stats_dest = root / "stats/epic-stats"
    stats_dest.mkdir(parents=True, exist_ok=True)
    restored = 0
    for line in src_root.joinpath("manifest.txt").read_text(encoding="utf-8").splitlines():
        rel = line.strip()
        if not rel:
            continue
        src = src_root / rel
        dst = root / rel
        if not src.exists():
            continue
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        restored += 1
    print(f"Restored {restored} path(s) under stats/epic-stats/")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["backup", "restore"])
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    args = p.parse_args()
    contract = _load()
    root = args.root.resolve()
    if args.action == "backup":
        return backup(root, contract)
    return restore(root, contract)


if __name__ == "__main__":
    sys.exit(main())
