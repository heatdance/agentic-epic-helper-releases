#!/usr/bin/env python3
"""
CLEAN pipeline verifier.

Contract: docs/clean-contract.json
Playbook: .cursor/pipelines/clean.md

Examples:
  python automation/tools/clean_verify.py --mode preflight
  python automation/tools/clean_verify.py --mode semver_next
  python automation/tools/clean_verify.py --mode semver_next --confirm-major yes
  python automation/tools/clean_verify.py --mode align --root .
  python automation/tools/clean_verify.py --mode team --root ../cursor-corner-team-build
  python automation/tools/clean_verify.py --mode public --root ../cursor-corner-public-build
  python automation/tools/clean_verify.py --mode file_map --map automation/temp/clean/file-map.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "clean-contract.json"
HIGH_RISK_SECRET_RE = re.compile(
    r"(Bearer\s+[A-Za-z0-9._-]{12,}|password\s*=\s*['\"][^'\"\\s]{8,}['\"])", re.I
)
PUBLIC_BRANCH_RE = re.compile(r"^public-(\d+)\.(\d+)$")
EPIC_KEY_RE = re.compile(r"^(CRT|CRTQA|CRTBL)-\d+$", re.I)


def _load_contract() -> dict[str, Any]:
    with CONTRACT_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _fail(msg: str) -> int:
    print(f"FAIL: {msg}", file=sys.stderr)
    return 1


def _ok(msg: str) -> int:
    print(f"OK: {msg}")
    return 0


def _git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(
        ["git", *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _current_branch(root: Path) -> str | None:
    code, out = _git("branch", "--show-current", cwd=root)
    if code != 0:
        return None
    return out.strip() or None


def _remote_branches(remote: str, cwd: Path | None = None) -> list[str]:
    code, out = _git("ls-remote", "--heads", remote, cwd=cwd or REPO_ROOT)
    if code != 0:
        return []
    branches: list[str] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith("refs/heads/"):
            branches.append(parts[1].replace("refs/heads/", "", 1))
    return branches


def _glob_exists(root: Path, pattern: str) -> list[Path]:
    if "**" in pattern:
        return [p for p in root.glob(pattern) if p.is_file() or p.is_dir()]
    return [p for p in root.glob(pattern)]


def _path_matches_glob(rel: str, pattern: str) -> bool:
    return fnmatch(rel.replace("\\", "/"), pattern)


def mode_preflight(root: Path, contract: dict[str, Any]) -> int:
    required = contract.get("required_branch", "personal")
    branch = _current_branch(root)
    if branch != required:
        return _fail(f"branch must be {required!r}, got {branch!r}")

    for key in ("personal", "team", "public"):
        remote = contract["remotes"][key]["remote"]
        code, _ = _git("remote", "get-url", remote, cwd=root)
        if code != 0:
            return _fail(f"git remote {remote!r} not configured")

    return _ok("preflight")


def _git_tracked_files(root: Path) -> list[str]:
    code, out = _git("ls-files", cwd=root)
    if code != 0:
        return []
    return [line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()]


def mode_secret_scan(root: Path) -> int:
    block = _load_contract().get("blocklist", {})
    forbidden = block.get("path_patterns", [])
    tracked = set(_git_tracked_files(root))
    for rel in tracked:
        for pat in forbidden:
            if _path_matches_glob(rel, pat) and "example" not in rel.lower():
                return _fail(f"forbidden tracked path: {rel}")

    for rel in tracked:
        path = root / rel
        if not path.is_file():
            continue
        if path.suffix in (".pyc", ".dpapi"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:50000]
        except OSError:
            continue
        if HIGH_RISK_SECRET_RE.search(text) and "example" not in rel.lower():
            return _fail(f"high-risk secret pattern in {rel}")
    return _ok("secret_scan")


def mode_semver_next(
    contract: dict[str, Any],
    version_override: str | None,
    confirm_major: bool,
) -> int:
    sem = contract["semver"]
    remote = contract["remotes"]["public"]["remote"]
    branches = _remote_branches(remote)
    public_versions: list[tuple[int, int]] = []
    for b in branches:
        m = PUBLIC_BRANCH_RE.match(b)
        if m:
            public_versions.append((int(m.group(1)), int(m.group(2))))

    if version_override:
        parts = version_override.split(".")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            return _fail(f"invalid version override: {version_override!r}")
        major, minor = int(parts[0]), int(parts[1])
        name = f"public-{major}.{minor}"
        print(name)
        return 0

    if not public_versions:
        default = sem.get("default_when_no_public_branch", "public-1.2")
        print(default)
        return 0

    major, minor = max(public_versions)
    minor_max = sem.get("minor_max_before_gate", 9)
    if minor >= minor_max:
        if not confirm_major:
            return _fail(
                f"latest public-{major}.{minor}; need confirm_major=yes for public-{major + 1}.0"
            )
        major += 1
        minor = 0
    else:
        minor += 1
    name = f"public-{major}.{minor}"
    print(name)
    return 0


def mode_file_map(map_path: Path) -> int:
    if not map_path.is_file():
        return _fail(f"file-map missing: {map_path}")
    try:
        with map_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return _fail(f"file-map invalid: {e}")

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        return _fail("file-map entries[] empty or missing")

    for i, row in enumerate(entries):
        if not isinstance(row, dict):
            return _fail(f"entry {i} not an object")
        for key in ("path", "tier", "action"):
            if key not in row:
                return _fail(f"entry {i} missing {key}")
        if row["tier"] not in ("personal", "team", "public", "all"):
            return _fail(f"entry {i} bad tier: {row['tier']}")

    return _ok(f"file_map ({len(entries)} entries)")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def mode_align(root: Path, contract: dict[str, Any]) -> int:
    align = contract.get("align", {})
    registry = align.get("registry_pipeline_ids", [])
    router_path = root / ".cursor/rules/pipeline-router.mdc"
    router_text = _read_text(router_path)
    if "CLEAN:" not in router_text:
        return _fail("pipeline-router.mdc missing CLEAN:")

    stale = align.get("stale_triggers_forbidden", [])
    for s in stale:
        if not s.endswith(":"):
            continue
        if s in router_text:
            return _fail(f"stale trigger in router: {s}")

    map_path = root / "docs/harness-map.json"
    try:
        with map_path.open(encoding="utf-8") as f:
            hmap = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return _fail(f"harness-map.json: {e}")

    packages = hmap.get("tiers", [{}])[1].get("match_any_package", []) if hmap.get("tiers") else []
    ids = [p.get("id") for p in packages if isinstance(p, dict)]
    if "clean_pipeline" not in ids:
        return _fail("harness-map missing clean_pipeline package")
    if "public_scrub_pipeline" in ids or "sync_pipeline" in ids:
        return _fail("harness-map still has public_scrub_pipeline or sync_pipeline")

    pipelines_dir = root / ".cursor/pipelines"
    playbooks = {p.stem for p in pipelines_dir.glob("*.md") if p.is_file()}
    if "clean" not in playbooks:
        return _fail("missing .cursor/pipelines/clean.md")
    if "public-scrub" in playbooks or "sync" in playbooks:
        return _fail("old playbooks public-scrub.md or sync.md still present")

    for pid in registry:
        if pid == "clean":
            continue
        if pid not in playbooks and pid != "test-exec":
            return _fail(f"registry pipeline {pid} missing playbook file")

    for t1 in align.get("t1_files", []):
        text = _read_text(root / t1)
        for stale in align.get("stale_triggers_forbidden", []):
            if stale.endswith(":") and stale in text:
                return _fail(f"stale {stale!r} in {t1}")
        for branch in align.get("stale_branch_names_forbidden_in_t1", []):
            if re.search(rf"`{re.escape(branch)}`", text):
                return _fail(f"stale branch name {branch!r} in {t1}")

    howto = _read_text(root / "HOW-TO.md")
    if "CLEAN:" not in howto:
        return _fail("HOW-TO.md missing CLEAN:")

    return _ok("align")


def mode_team(root: Path, contract: dict[str, Any]) -> int:
    team = contract.get("team", {})
    for pat in team.get("delete_globs", []):
        for p in _glob_exists(root, pat):
            rel = p.relative_to(root).as_posix()
            return _fail(f"team forbid present: {rel} (pattern {pat})")

    for rel in team.get("delete_paths", []):
        if (root / rel).exists():
            return _fail(f"team forbid path present: {rel}")

    if (root / ".cursor/pipelines/clean.md").is_file():
        return _fail("clean.md must not exist on team tree")

    epics_dir = root / "epics"
    if epics_dir.is_dir():
        for epic in epics_dir.iterdir():
            if epic.is_dir() and epic.name != "templates" and EPIC_KEY_RE.match(epic.name):
                return _fail(f"epic dir present: epics/{epic.name}")

    for req in team.get("required_after_strip", []):
        if not (root / req).is_file():
            return _fail(f"team required missing: {req}")

    router = _read_text(root / ".cursor/rules/pipeline-router.mdc")
    if "CLEAN:" in router:
        return _fail("team router must not include CLEAN:")

    return _ok("team")


def _rg_blocklist(root: Path, contract: dict[str, Any]) -> int:
    block = contract.get("blocklist", {})
    patterns = block.get("rg_patterns", [])
    allow = block.get("rg_allow_globs", [])
    glob_args: list[str] = []
    for g in allow:
        glob_args.extend(["--glob", f"!{g}"])

    skip_dirs = {".git", "epics/templates"}
    for pattern in patterns:
        cmd = ["rg", "-n", pattern, str(root), *glob_args]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if r.returncode == 0 and r.stdout.strip():
            for line in r.stdout.strip().splitlines():
                path_part = line.split(":", 1)[0] if ":" in line else line
                if any(s in path_part.replace("\\", "/") for s in skip_dirs):
                    continue
                if path_part.endswith(".example.json"):
                    continue
                return _fail(f"blocklist hit {pattern!r}: {line}")
    return 0


def mode_public(root: Path, contract: dict[str, Any]) -> int:
    pub = contract.get("public", {})
    for pat in pub.get("delete_globs", []):
        for p in _glob_exists(root, pat):
            rel = p.relative_to(root).as_posix()
            if rel.endswith("-readme.md"):
                continue
            if "templates" in rel:
                continue
            return _fail(f"public forbid present: {rel}")

    pipelines = root / ".cursor/pipelines"
    for md in pipelines.glob("*.md"):
        if md.name.endswith("-readme.md") or md.name == "clean.md":
            continue
        if not md.name.endswith("-readme.md"):
            return _fail(f"full playbook still present: {md.relative_to(root)}")

    for pid in pub.get("required_readmes", []):
        readme = pipelines / f"{pid}-readme.md"
        if not readme.is_file():
            return _fail(f"missing public readme: {readme.relative_to(root)}")

    if (root / ".cursor/pipelines/clean.md").is_file():
        return _fail("clean.md must not exist on public tree")

    if _rg_blocklist(root, contract) != 0:
        return 1

    manifest = root / pub.get("manifest_path", "docs/public-export-manifest.json")
    if not manifest.is_file():
        return _fail("missing docs/public-export-manifest.json on public tree")

    return _ok("public")


def main() -> int:
    parser = argparse.ArgumentParser(description="CLEAN pipeline verifier")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "preflight",
            "secret_scan",
            "semver_next",
            "file_map",
            "align",
            "team",
            "public",
        ],
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--map", type=Path, default=REPO_ROOT / "automation/temp/clean/file-map.json")
    parser.add_argument("--version", type=str, default=None, help="M.N override for semver_next")
    parser.add_argument(
        "--confirm-major",
        choices=["yes", "no"],
        default="no",
    )
    args = parser.parse_args()
    contract = _load_contract()
    root = args.root.resolve()

    if args.mode == "preflight":
        return mode_preflight(root, contract)
    if args.mode == "secret_scan":
        return mode_secret_scan(root)
    if args.mode == "semver_next":
        return mode_semver_next(
            contract, args.version, args.confirm_major == "yes"
        )
    if args.mode == "file_map":
        return mode_file_map(args.map.resolve())
    if args.mode == "align":
        return mode_align(root, contract)
    if args.mode == "team":
        return mode_team(root, contract)
    if args.mode == "public":
        return mode_public(root, contract)
    return _fail(f"unknown mode {args.mode}")


if __name__ == "__main__":
    sys.exit(main())
