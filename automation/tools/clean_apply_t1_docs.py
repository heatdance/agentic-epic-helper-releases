#!/usr/bin/env python3
"""Render tier-specific T1 entry docs from docs/clean-entry-templates/."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/clean-contract.json"
TEMPLATES = REPO_ROOT / "docs/clean-entry-templates"

TEAM_MAP = {
    "README.md": "README.team.md",
    "HOW-TO.md": "HOW-TO.team.md",
    "AGENTS.md": "AGENTS.team.md",
}


def _load_contract() -> dict:
    with CONTRACT.open(encoding="utf-8") as f:
        return json.load(f)


def _substitute(text: str, contract: dict) -> str:
    team = contract["remotes"]["team"]
    url = team["url"].rstrip("/")
    if url.endswith(".git"):
        slug = url[:-4].split("/")[-1]
    else:
        slug = url.split("/")[-1]
    repl = {
        "{{TEAM_REPO_URL}}": url,
        "{{TEAM_REPO_SLUG}}": slug,
        "{{TEAM_BRANCH}}": team["branch"],
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text


def strip_harness_packages(root: Path, package_ids: list[str]) -> None:
    path = root / "docs/harness-map.json"
    if not path.is_file():
        return
    with path.open(encoding="utf-8") as f:
        hmap = json.load(f)
    tiers = hmap.get("tiers") or []
    for tier in tiers:
        if not isinstance(tier, dict):
            continue
        packages = tier.get("match_any_package")
        if not isinstance(packages, list):
            continue
        tier["match_any_package"] = [
            p for p in packages if isinstance(p, dict) and p.get("id") not in package_ids
        ]
    path.write_text(json.dumps(hmap, indent=2) + "\n", encoding="utf-8")


def apply_team(root: Path, contract: dict) -> None:
    for dest, tmpl_name in TEAM_MAP.items():
        tmpl = TEMPLATES / tmpl_name
        if not tmpl.is_file():
            raise FileNotFoundError(f"missing template: {tmpl}")
        text = _substitute(tmpl.read_text(encoding="utf-8"), contract)
        (root / dest).write_text(text, encoding="utf-8")
    strip_ids = contract.get("team", {}).get(
        "harness_map_strip_package_ids", ["clean_release"]
    )
    strip_harness_packages(root, strip_ids)


def apply_public_t1(root: Path) -> None:
    """Public T1 is written by clean_apply_public; ensure harness-map strip if file remains."""
    strip_harness_packages(root, ["clean_release", "calibrate_pipeline", "release_notes"])


def apply(root: Path, tier: str) -> None:
    contract = _load_contract()
    if tier == "team":
        apply_team(root, contract)
    elif tier == "public":
        apply_public_t1(root)
    elif tier == "personal":
        return
    else:
        raise ValueError(f"unknown tier: {tier}")


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    p.add_argument("--tier", choices=["personal", "team", "public"], required=True)
    args = p.parse_args()
    apply(args.root.resolve(), args.tier)
    print(f"Applied T1 docs tier={args.tier} to {args.root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
