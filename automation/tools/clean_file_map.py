#!/usr/bin/env python3
"""Generate automation/temp/clean/file-map.json for CLEAN Phase S1."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "automation/temp/clean/file-map.json"
MATRIX_PATH = REPO_ROOT / "docs/clean-publish-tier-matrix.json"
CLEAN_MD = ".cursor/pipelines/clean.md"
EPIC_KEY_RE = re.compile(r"^(CRT|CRTQA|CRTBL)-\d+$", re.I)


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
    return [line.strip().replace("\\", "/") for line in r.stdout.splitlines() if line.strip()]


def _load_matrix() -> dict:
    if not MATRIX_PATH.is_file():
        return {"rules": [], "default": {}}
    with MATRIX_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _path_matches_rule(rel: str, rule: dict) -> bool:
    pattern = rule.get("match", "")
    if not pattern:
        return False
    exclude = rule.get("exclude") or []
    if any(fnmatch(rel, ex) for ex in exclude):
        return False
    if "**" in pattern:
        # simple glob: convert ** to match segments
        parts = pattern.replace("**", "*").split("/")
        if len(parts) == 1:
            return fnmatch(rel, pattern) or fnmatch(Path(rel).name, pattern.split("/")[-1])
        return fnmatch(rel, pattern)
    if pattern.endswith("/*"):
        prefix = pattern[:-2]
        return rel.startswith(prefix + "/") or rel == prefix
    return fnmatch(rel, pattern) or rel == pattern


def _resolve_from_matrix(rel: str, matrix: dict) -> dict | None:
    for rule in matrix.get("rules", []):
        if _path_matches_rule(rel, rule):
            return rule
    return None


def _tier_action_for_rel(rel: str, matrix: dict) -> dict:
    """Return per-tier summary for file-map entry."""
    rule = _resolve_from_matrix(rel, matrix)
    default = matrix.get("default", {})
    personal = (rule or {}).get("personal") or default.get("personal", {"action": "keep"})
    team = (rule or {}).get("team") or default.get("team", {"action": "keep"})
    public = (rule or {}).get("public") or default.get("public", {"action": "keep"})

    # Heuristic fallbacks when matrix has no rule
    if rule is None:
        if rel == CLEAN_MD:
            personal, team, public = {"action": "keep"}, {"action": "delete"}, {"action": "delete"}
        elif rel.startswith("epics/") and "/templates/" not in rel and rel != "epics/README.md":
            if rel.count("/") >= 2 or EPIC_KEY_RE.match(Path(rel).parts[1] if len(Path(rel).parts) > 1 else ""):
                personal = {"action": "keep"}
                team = {"action": "delete"}
                public = {"action": "delete"}
        elif rel in ("qa-handoff.md",) or rel.startswith(("temp/", "automation/temp/")):
            personal = {"action": "keep"}
            team = {"action": "delete"}
            public = {"action": "delete"}
        elif "-gold/" in rel and rel.startswith(".cursor/calibrate/"):
            personal = {"action": "keep"}
            team = {"action": "delete"}
            public = {"action": "delete"}

    # Collapse to primary tier + action for file-map schema
    action = personal.get("action", "keep")
    if team.get("action") == "delete" and public.get("action") == "delete" and action == "keep":
        tier = "personal"
        action = "delete_team_public"
    elif team.get("action") == "rewrite":
        tier = "all"
        action = "team_rewrite"
    elif public.get("action") == "public_readme_replace":
        tier = "all"
        action = "public_readme_replace"
    elif team.get("action") == "example_only":
        tier = "team"
        action = "transform_example"
    elif public.get("action") == "delete" and personal.get("action") == "keep":
        tier = "public"
        action = "delete_public"
    else:
        tier = "all"

    audience = personal.get("t1_variant") or ""
    entry = {
        "path": rel,
        "tier": tier,
        "action": action,
        "role": "tracked",
        "consumers": [],
        "personal": personal,
        "team": team,
        "public": public,
    }
    if audience:
        entry["t1_variant"] = audience
        entry["audience"] = audience
    return entry


def main() -> int:
    root = REPO_ROOT
    matrix = _load_matrix()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    for rel in sorted(_tracked_files(root)):
        entries.append(_tier_action_for_rel(rel, matrix))
    payload = {
        "schema_version": 2,
        "repo_root": str(root),
        "tier_matrix": str(MATRIX_PATH.relative_to(root)).replace("\\", "/"),
        "entry_count": len(entries),
        "entries": entries,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
