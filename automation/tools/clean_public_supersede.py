#!/usr/bin/env python3
"""Delete superseded public-* branch on releases remote and locally after successful push."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/clean-contract.json"


def _git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(
        ["git", *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _load_contract() -> dict:
    with CONTRACT.open(encoding="utf-8") as f:
        return json.load(f)


def supersede(
    target_branch: str,
    superseded_branch: str | None,
    repo_root: Path | None = None,
) -> int:
    root = repo_root or REPO_ROOT
    pub = _load_contract().get("public", {})
    if not pub.get("supersede_previous_branch", True):
        print("SKIP: supersede_previous_branch false")
        return 0
    if not superseded_branch:
        print("SKIP: no superseded_branch")
        return 0
    if superseded_branch == target_branch:
        print("SKIP: superseded equals target")
        return 0

    remote = _load_contract()["remotes"]["public"]["remote"]
    releases_url = _load_contract()["remotes"]["public"]["url"]

    # Try set default branch via gh when available (heatdance/agentic-epic-helper-releases)
    if "github.com" in releases_url:
        slug = releases_url.rstrip("/").split("github.com/")[-1].replace(".git", "")
        owner_repo = slug
        code, _ = _git("gh", "api", f"repos/{owner_repo}", cwd=root)
        if code == 0:
            _git(
                "gh",
                "api",
                f"repos/{owner_repo}",
                "-X",
                "PATCH",
                "-f",
                f"default_branch={target_branch}",
                cwd=root,
            )

    code, err = _git("push", remote, "--delete", superseded_branch, cwd=root)
    if code != 0 and "remote ref does not exist" not in err.lower():
        print(f"WARN: remote delete {superseded_branch}: {err.strip()}", file=sys.stderr)
    else:
        print(f"Deleted remote branch {superseded_branch}")

    _git("branch", "-D", superseded_branch, cwd=root)
    _git("worktree", "prune", cwd=root)
    print(f"Supersede complete: {superseded_branch} -> {target_branch}")
    return 0


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True, help="e.g. public-1.2")
    p.add_argument("--superseded", default=None, help="e.g. public-1.1")
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    args = p.parse_args()
    return supersede(args.target, args.superseded, args.root.resolve())


if __name__ == "__main__":
    sys.exit(main())
