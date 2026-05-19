#!/usr/bin/env python3
"""Generate automation/temp/clean/file-map.json for CLEAN Phase S1."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "automation/temp/clean/file-map.json"
CLEAN_MD = ".cursor/pipelines/clean.md"


def _tracked_files(root: Path) -> list[str]:
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


def _tier_and_action(rel: str) -> tuple[str, str]:
    if rel == CLEAN_MD:
        return "personal", "keep"
    if rel.startswith("epics/") and "/templates/" not in rel and rel != "epics/README.md":
        if rel.count("/") >= 2:
            return "personal", "delete_team_public"
    if rel in ("qa-handoff.md",) or rel.startswith("temp/") or rel.startswith("automation/temp/"):
        return "personal", "delete_team_public"
    if rel.startswith(".cursor/benchmark/runs/"):
        return "personal", "delete_team_public"
    if rel.startswith(".cursor/pipelines/") and rel.endswith(".md") and not rel.endswith("-readme.md"):
        pid = Path(rel).stem
        if pid != "clean":
            return "all", "public_readme_replace"
    if rel.startswith("automation/tools/") and rel.endswith("_verify.py"):
        return "public", "delete_public"
    if rel in (
        "docs/project.json",
        "docs/qa-project.json",
        "docs/corner-platform-map.json",
    ):
        return "team", "transform_example"
    return "all", "keep"


def main() -> int:
    root = REPO_ROOT
    OUT.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    for rel in sorted(_tracked_files(root)):
        tier, action = _tier_and_action(rel)
        entries.append(
            {
                "path": rel.replace("\\", "/"),
                "tier": tier,
                "action": action,
                "role": "tracked",
                "consumers": [],
            }
        )
    payload = {
        "schema_version": 1,
        "repo_root": str(root),
        "entry_count": len(entries),
        "entries": entries,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
