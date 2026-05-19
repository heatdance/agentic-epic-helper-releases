#!/usr/bin/env python3
"""Delete superseded public-* and legacy release-* branches on releases remote and locally."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/clean-contract.json"
RELEASE_BRANCH_RE = re.compile(r"^release-")


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


def _remote_branches(remote: str, cwd: Path) -> list[str]:
    code, out = _git("ls-remote", "--heads", remote, cwd=cwd)
    if code != 0:
        return []
    branches: list[str] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith("refs/heads/"):
            branches.append(parts[1].replace("refs/heads/", "", 1))
    return branches


def _delete_remote_branch(remote: str, branch: str, cwd: Path) -> None:
    code, err = _git("push", remote, "--delete", branch, cwd=cwd)
    if code != 0 and "remote ref does not exist" not in err.lower():
        print(f"WARN: remote delete {branch}: {err.strip()}", file=sys.stderr)
    else:
        print(f"Deleted remote branch {branch}")


def _delete_local_branch(branch: str, cwd: Path) -> None:
    _git("branch", "-D", branch, cwd=cwd)


def delete_legacy_branches(root: Path, contract: dict) -> int:
    sem = contract.get("semver", {})
    legacy = sem.get("legacy_branches_delete", [])
    remote = contract["remotes"]["public"]["remote"]
    for branch in legacy:
        if branch in _remote_branches(remote, root):
            _delete_remote_branch(remote, branch, root)
        _delete_local_branch(branch, root)
    return 0


def supersede(
    target_branch: str,
    superseded_branch: str | None,
    repo_root: Path | None = None,
    *,
    delete_legacy: bool = True,
) -> int:
    root = repo_root or REPO_ROOT
    contract = _load_contract()
    pub = contract.get("public", {})
    if not pub.get("supersede_previous_branch", True):
        print("SKIP: supersede_previous_branch false")
        return 0

    remote = contract["remotes"]["public"]["remote"]
    releases_url = contract["remotes"]["public"]["url"]

    if delete_legacy:
        delete_legacy_branches(root, contract)

    if not superseded_branch:
        print("SKIP: no superseded_branch")
        _git("worktree", "prune", cwd=root)
        return 0
    if superseded_branch == target_branch:
        print("SKIP: superseded equals target")
        return 0

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

    _delete_remote_branch(remote, superseded_branch, root)
    _delete_local_branch(superseded_branch, root)

    for local in _git("branch", "--format=%(refname:short)", cwd=root)[1].splitlines():
        name = local.strip()
        if name and RELEASE_BRANCH_RE.match(name):
            _delete_local_branch(name, root)

    _git("worktree", "prune", cwd=root)
    print(f"Supersede complete: {superseded_branch} -> {target_branch}")
    return 0


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--target", default=None, help="e.g. public-1.4 (required unless --legacy-only)")
    p.add_argument("--superseded", default=None, help="e.g. public-1.3")
    p.add_argument(
        "--legacy-only",
        action="store_true",
        help="delete semver.legacy_branches_delete only",
    )
    p.add_argument("--no-legacy", action="store_true", help="skip legacy branch deletes")
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    args = p.parse_args()
    root = args.root.resolve()
    if args.legacy_only:
        return delete_legacy_branches(root, _load_contract())
    if not args.target:
        print("error: --target required unless --legacy-only", file=sys.stderr)
        return 2
    return supersede(
        args.target,
        args.superseded,
        root,
        delete_legacy=not args.no_legacy,
    )


if __name__ == "__main__":
    sys.exit(main())
