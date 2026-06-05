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
RELEASE_BRANCH_RE = re.compile(r"^release-")
FORBIDDEN_CLEAN_BRANCH_RE = re.compile(r"^clean/")
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


def _worktree_paths(root: Path) -> list[str]:
    code, out = _git("worktree", "list", "--porcelain", cwd=root)
    if code != 0:
        return []
    paths: list[str] = []
    for line in out.splitlines():
        if line.startswith("worktree "):
            paths.append(line.split(" ", 1)[1].strip())
    return paths


def _has_extra_worktrees(root: Path) -> bool:
    paths = _worktree_paths(root)
    root_resolved = root.resolve()
    return len(paths) > 1 or any(
        Path(p).resolve() != root_resolved for p in paths
    )


def _branches_matching_remote(
    remote: str, patterns: list[str], cwd: Path | None = None
) -> list[str]:
    branches = _remote_branches(remote, cwd)
    matched: list[str] = []
    for name in branches:
        for pat in patterns:
            if fnmatch(name, pat):
                matched.append(name)
                break
    return matched


def _public_branches_on_releases(contract: dict[str, Any], cwd: Path | None = None) -> list[str]:
    remote = contract["remotes"]["public"]["remote"]
    return [b for b in _remote_branches(remote, cwd) if _public_branch_tuple(b)]


def _check_branch_policy_remotes(contract: dict[str, Any], cwd: Path) -> int | None:
    policy = contract.get("branch_policy", {})
    forbidden = policy.get("forbidden_remote_patterns", ["clean/*", "release-*"])

    team_remote = contract["remotes"]["team"]["remote"]
    allowed_team = {contract["remotes"]["team"]["branch"]}
    team_heads = _remote_branches(team_remote, cwd)
    extra_team = [b for b in team_heads if b not in allowed_team]
    if extra_team:
        return _fail(f"extra branches on {team_remote} (allowed {allowed_team}): {extra_team}")

    releases_remote = contract["remotes"]["public"]["remote"]
    for name in _branches_matching_remote(releases_remote, forbidden, cwd):
        return _fail(f"forbidden branch on {releases_remote}: {name}")

    public_heads = _public_branches_on_releases(contract, cwd)
    max_count = policy.get("max_public_branches_on_releases", 1)
    if len(public_heads) > max_count:
        return _fail(
            f"releases has {len(public_heads)} public-* branches, max {max_count}: {public_heads}"
        )

    origin_remote = contract["remotes"]["personal"]["remote"]
    origin_heads = _remote_branches(origin_remote, cwd)
    personal_branch = contract["remotes"]["personal"]["branch"]
    extra_origin = [b for b in origin_heads if b != personal_branch]
    if extra_origin and policy.get("warn_extra_origin_branches", False):
        print(f"WARN: extra branches on {origin_remote}: {extra_origin}", file=sys.stderr)

    return None


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

    if _has_extra_worktrees(root):
        return _fail(
            "extra git worktrees present; remove cursor-corner-*-build dirs and run git worktree prune"
        )

    for rel in contract.get("branch_policy", {}).get(
        "known_worktree_paths_forbidden", []
    ):
        if (root.parent / Path(rel).name).exists() and rel.startswith("../"):
            candidate = (root / rel).resolve()
            if candidate.exists():
                return _fail(f"forbidden worktree path exists: {rel}")

    return _ok("preflight")


def mode_team_tip(root: Path, contract: dict[str, Any], expected_sha: str | None) -> int:
    if not expected_sha:
        return _fail("team_tip mode requires --sha")
    expected = expected_sha.strip().lower()
    code, out = _git("rev-parse", contract.get("public", {}).get("source_ref", "team/team"), cwd=root)
    if code != 0:
        return _fail(f"cannot resolve team tip: {out.strip()}")
    actual = out.strip().lower()
    if actual != expected and not (
        len(expected) >= 7 and actual.startswith(expected[:7])
    ):
        return _fail(f"team/team is {actual[:12]}, expected {expected[:12]}")
    return _ok(f"team_tip ({actual[:12]})")


def mode_legacy_remote(contract: dict[str, Any], cwd: Path) -> int:
    sem = contract.get("semver", {})
    if not sem.get("legacy_branches_delete_required", True):
        return _ok("legacy_remote (not required)")
    remote = contract["remotes"]["public"]["remote"]
    legacy = sem.get("legacy_branches_delete", [])
    remaining = [b for b in _remote_branches(remote, cwd) if b in legacy or RELEASE_BRANCH_RE.match(b)]
    if remaining:
        return _fail(f"legacy release-* branches still on {remote}: {remaining}")
    return _ok("legacy_remote")


def mode_prune_team_remote(contract: dict[str, Any], cwd: Path) -> int:
    """Delete all team-remote heads except the canonical team branch."""
    team_remote = contract["remotes"]["team"]["remote"]
    allowed = contract["remotes"]["team"]["branch"]
    deleted: list[str] = []
    for name in _remote_branches(team_remote, cwd):
        if name == allowed:
            continue
        code, err = _git("push", team_remote, "--delete", name, cwd=cwd)
        if code != 0:
            print(f"WARN: could not delete {team_remote}/{name}: {err.strip()}", file=sys.stderr)
        else:
            deleted.append(name)
    if deleted:
        print(f"pruned team remote branches: {deleted}")
    return _ok("prune_team_remote")


def mode_postflight(root: Path, contract: dict[str, Any]) -> int:
    post = contract.get("postflight", {})
    required = post.get("required_branch", contract.get("required_branch", "personal"))
    branch = _current_branch(root)
    if branch != required:
        return _fail(f"postflight: branch must be {required!r}, got {branch!r}")

    if post.get("require_empty_worktrees", True) and _has_extra_worktrees(root):
        return _fail("postflight: extra git worktrees still present")

    if post.get("enforce_branch_policy_on_remotes", True):
        err = _check_branch_policy_remotes(contract, root)
        if err is not None:
            return err

    err = mode_legacy_remote(contract, root)
    if err != 0:
        return err

    return _ok("postflight")


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


def _public_branch_tuple(name: str) -> tuple[int, int] | None:
    m = PUBLIC_BRANCH_RE.match(name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def _branch_from_tuple(major: int, minor: int) -> str:
    return f"public-{major}.{minor}"


def _superseded_branch(
    target: tuple[int, int],
    public_versions: list[tuple[int, int]],
    republish_same: bool,
) -> str | None:
    if republish_same:
        return None
    older = [v for v in public_versions if v < target]
    if not older:
        return None
    m, n = max(older)
    return _branch_from_tuple(m, n)


def compute_semver_next(
    contract: dict[str, Any],
    version_override: str | None,
    confirm_major: bool,
) -> tuple[str | None, str | None, str | None]:
    """Returns (target_branch, superseded_branch, error_message)."""
    sem = contract["semver"]
    remote = contract["remotes"]["public"]["remote"]
    branches = _remote_branches(remote)
    public_versions: list[tuple[int, int]] = []
    branch_names: dict[tuple[int, int], str] = {}
    for b in branches:
        t = _public_branch_tuple(b)
        if t:
            public_versions.append(t)
            branch_names[t] = b

    if version_override:
        parts = version_override.split(".")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            return None, None, f"invalid version override: {version_override!r}"
        major, minor = int(parts[0]), int(parts[1])
        target_t = (major, minor)
        name = _branch_from_tuple(major, minor)
        republish = target_t in public_versions
        superseded = _superseded_branch(target_t, public_versions, republish)
        return name, superseded, None

    if not public_versions:
        default = sem.get("default_when_no_public_branch", "public-1.2")
        return default, None, None

    major, minor = max(public_versions)
    minor_max = sem.get("minor_max_before_gate", 9)
    if minor >= minor_max:
        if not confirm_major:
            return (
                None,
                None,
                f"latest public-{major}.{minor}; need confirm_major=yes for public-{major + 1}.0",
            )
        major += 1
        minor = 0
    else:
        minor += 1
    target_t = (major, minor)
    name = _branch_from_tuple(major, minor)
    superseded = _superseded_branch(target_t, public_versions, False)
    return name, superseded, None


def mode_semver_next(
    contract: dict[str, Any],
    version_override: str | None,
    confirm_major: bool,
    json_output: bool,
) -> int:
    target, superseded, err = compute_semver_next(
        contract, version_override, confirm_major
    )
    if err:
        return _fail(err)
    if json_output:
        export_version = None
        if target:
            m = PUBLIC_BRANCH_RE.match(target)
            if m:
                export_version = f"{m.group(1)}.{m.group(2)}.0"
        print(
            json.dumps(
                {
                    "target_branch": target,
                    "superseded_branch": superseded,
                    "export_version": export_version,
                },
                indent=2,
            )
        )
        return 0
    print(target)
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
            return _fail(f"entry {i} bad tier: {row['tier']!r}")

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
    for rel in team.get("required_mcp_examples", []):
        if not (root / rel).is_file():
            return _fail(f"team MCP example missing: {rel}")

    router = _read_text(root / ".cursor/rules/pipeline-router.mdc")
    if "CLEAN:" in router:
        return _fail("team router must not include CLEAN:")

    agents = _read_text(root / "AGENTS.md")
    if "clean.md" in agents and "pipelines/clean" in agents:
        return _fail("AGENTS.md must not reference clean.md")

    howto = _read_text(root / "HOW-TO.md")
    if "CLEAN:" in howto:
        return _fail("HOW-TO.md must not contain CLEAN:")

    readme = _read_text(root / "README.md")
    if "agentic-epic-helper-releases" in readme:
        return _fail("README.md must not reference releases repo")
    if re.search(r"heatdance/agentic-epic-helper(?!-team)", readme):
        return _fail("README.md must not reference personal repo URL")

    if (root / "qa-handoff.md").is_file():
        return _fail("qa-handoff.md must not exist on team tree")

    cal = root / ".cursor/calibrate"
    if cal.is_dir():
        for gold in cal.glob("*-gold"):
            if gold.is_dir():
                return _fail(f"calibrate gold present: {gold.relative_to(root)}")
        for rep in (cal / "reports").glob("*") if (cal / "reports").is_dir() else []:
            if rep.is_file():
                return _fail(f"calibrate report present: {rep.relative_to(root)}")

    cmd = root / ".cursor/commands/crtqa-calibrate.md"
    if not cmd.is_file():
        return _fail("team tree missing .cursor/commands/crtqa-calibrate.md")

    helper_cmd = root / ".cursor/commands/crtqa-helper.md"
    if not helper_cmd.is_file():
        return _fail("team tree missing .cursor/commands/crtqa-helper.md")
    for rel in (
        "docs/crtqa-helper-contract.json",
        "automation/tools/crtqa_helper_affordances.py",
        ".cursor/pipelines/coverage-reinforce.md",
    ):
        if not (root / rel).is_file():
            return _fail(f"team tree missing helper artefact: {rel}")

    for rel in (
        ".cursor/commands/crtqa-stats.md",
        "docs/crtqa-stats-contract.json",
        "automation/tools/crtqa_stats_rollup.py",
        ".cursor/commands/better-prompt.md",
        ".cursor/commands/better-skill.md",
        "docs/operator-assist-contract.json",
        "docs/skill-authoring-patterns.json",
    ):
        if (root / rel).exists():
            return _fail(f"personal-only artefact present on team tree: {rel}")
    stats_dir = root / "stats/crtqa-stats"
    if stats_dir.is_dir():
        return _fail("team tree must not include stats/crtqa-stats/")

    for rel in (
        ".cursor/commands/release-notes.md",
        "docs/release-notes-contract.json",
        "automation/tools/release_notes.py",
    ):
        if (root / rel).exists():
            return _fail(f"release-notes artefact present on team tree: {rel}")
    if (root / "releases").is_dir() and any((root / "releases").iterdir()):
        return _fail("releases/ must be empty or absent on team tree")

    try:
        with (root / "docs/harness-map.json").open(encoding="utf-8") as f:
            hmap = json.load(f)
        packages = hmap.get("tiers", [{}])[1].get("match_any_package", []) if hmap.get("tiers") else []
        ids = [p.get("id") for p in packages if isinstance(p, dict)]
        if "clean_pipeline" in ids:
            return _fail("harness-map must not include clean_pipeline on team tree")
        if "release_notes" in ids:
            return _fail("harness-map must not include release_notes on team tree")
        for forbidden_pkg in ("crtqa_stats", "operator_assist", "auto_tests_teach"):
            if forbidden_pkg in ids:
                return _fail(f"harness-map must not include {forbidden_pkg} on team tree")
    except (OSError, json.JSONDecodeError) as e:
        return _fail(f"harness-map.json: {e}")

    forbidden = team.get("forbidden_substrings", [])
    allow_map = team.get("forbidden_substrings_allow_if", {})
    scan_files = ["README.md", "HOW-TO.md", "AGENTS.md", ".cursor/rules/pipeline-router.mdc"]
    for rel in scan_files:
        text = _read_text(root / rel)
        lower = text.lower()
        for sub in forbidden:
            sub_l = sub.lower()
            if sub_l not in lower:
                continue
            allowed = False
            for key, replacements in allow_map.items():
                if sub_l in key.lower():
                    for rep in replacements:
                        if rep.lower() in lower:
                            allowed = True
                            break
            if not allowed:
                return _fail(f"forbidden substring {sub!r} in {rel}")

    if ".cursor/benchmark" in readme or ".cursor/benchmark" in howto:
        return _fail("team docs must not reference .cursor/benchmark/")

    return _ok("team")


def mode_public_remote(
    contract: dict[str, Any],
    superseded_branch: str | None,
) -> int:
    if not superseded_branch:
        return _ok("public_remote (no supersede expected)")
    remote = contract["remotes"]["public"]["remote"]
    branches = _remote_branches(remote)
    if superseded_branch in branches:
        return _fail(f"superseded branch still on remote: {superseded_branch}")
    return _ok("public_remote")


def _allowed_blocklist_path(rel: str, allow_globs: list[str]) -> bool:
    if "epics/templates" in rel:
        return True
    for g in allow_globs:
        if fnmatch(rel, g) or fnmatch(Path(rel).name, g):
            return True
    return False


def _rg_blocklist(root: Path, contract: dict[str, Any]) -> int:
    block = contract.get("blocklist", {})
    patterns = [re.compile(p, re.I) for p in block.get("rg_patterns", [])]
    allow = block.get("rg_allow_globs", [])
    compiled = patterns

    for rel in _git_tracked_files(root):
        if _allowed_blocklist_path(rel, allow):
            continue
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rx in compiled:
            if rx.search(text):
                return _fail(f"blocklist hit {rx.pattern!r} in {rel}")
    return 0


def _stack_allow_path(rel: str, allow_globs: list[str]) -> bool:
    norm = rel.replace("\\", "/")
    for g in allow_globs:
        if fnmatch(norm, g) or fnmatch(Path(norm).name, g):
            return True
    return False


def _section_word_count(text: str, heading: str) -> int:
    marker = f"## {heading}"
    if marker not in text:
        return 0
    start = text.index(marker) + len(marker)
    rest = text[start:].lstrip("\n")
    nxt = rest.find("\n## ")
    body = rest[:nxt] if nxt >= 0 else rest
    return len(body.split())


def _public_readme_depth(root: Path, contract: dict[str, Any]) -> int | None:
    pub = contract.get("public", {})
    mins = pub.get("readme_min_words", {})
    required_sections = [
        ("Purpose", mins.get("section_purpose", 25)),
        ("Process steps", mins.get("section_process_steps", 40)),
        ("Outputs", mins.get("section_outputs", 10)),
        ("Build your own", mins.get("section_build_your_own", 15)),
    ]
    pipelines = root / ".cursor/pipelines"
    for pid in pub.get("required_readmes", []):
        readme = pipelines / f"{pid}-readme.md"
        if not readme.is_file():
            return _fail(f"missing readme for depth check: {pid}")
        text = _read_text(readme)
        for heading, min_w in required_sections:
            wc = _section_word_count(text, heading)
            if wc < min_w:
                return _fail(
                    f"{readme.name} section {heading!r} has {wc} words, min {min_w}"
                )
    for rel, min_total in (
        ("README.md", mins.get("entry_readme", 80)),
        ("HOW-TO.md", mins.get("entry_howto", 60)),
        ("AGENTS.md", mins.get("entry_agents", 40)),
    ):
        p = root / rel
        if not p.is_file():
            return _fail(f"missing entry doc: {rel}")
        wc = len(_read_text(p).split())
        if wc < min_total:
            return _fail(f"{rel} has {wc} words, min {min_total}")
    return None


def _public_forbidden_stack(root: Path, contract: dict[str, Any]) -> int | None:
    pub = contract.get("public", {})
    patterns = [re.compile(p, re.I) for p in pub.get("forbidden_stack_patterns", [])]
    allow = pub.get("forbidden_stack_allow_path_globs", [])
    if not patterns:
        return None
    for rel in _git_tracked_files(root):
        if _stack_allow_path(rel, allow):
            continue
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rx in patterns:
            if rx.search(text):
                return _fail(f"forbidden stack pattern {rx.pattern!r} in {rel}")
    return None


def _public_mcp_files_absent(root: Path, contract: dict[str, Any]) -> int | None:
    tracked = set(_git_tracked_files(root))
    for rel in contract.get("public", {}).get(
        "delete_paths", [".cursor/mcp.json.example", ".cursor/mcp.json"]
    ):
        if rel in tracked:
            return _fail(f"MCP config must not be tracked on public tree: {rel}")
        if rel == ".cursor/mcp.json":
            continue
        if (root / rel).is_file():
            return _fail(f"MCP config must not exist on public tree: {rel}")
    return None


def mode_public(root: Path, contract: dict[str, Any]) -> int:
    pub = contract.get("public", {})
    verify_self = {"automation/tools/clean_verify.py", "automation/tools/clean_apply_public.py"}
    for pat in pub.get("delete_globs", []):
        for p in _glob_exists(root, pat):
            rel = p.relative_to(root).as_posix()
            if rel in verify_self:
                continue
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

    err = _public_mcp_files_absent(root, contract)
    if err is not None:
        return err
    err = _public_forbidden_stack(root, contract)
    if err is not None:
        return err
    err = _public_readme_depth(root, contract)
    if err is not None:
        return err

    overlay_dir = root / "epics/templates/public"
    if overlay_dir.exists():
        return _fail("epics/templates/public must not ship on public tree")

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
            "team_tip",
            "public",
            "public_remote",
            "legacy_remote",
            "prune_team_remote",
            "postflight",
        ],
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON output for semver_next",
    )
    parser.add_argument(
        "--superseded",
        type=str,
        default=None,
        help="superseded branch name for public_remote mode",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--map", type=Path, default=REPO_ROOT / "automation/temp/clean/file-map.json")
    parser.add_argument("--version", type=str, default=None, help="M.N override for semver_next")
    parser.add_argument(
        "--confirm-major",
        choices=["yes", "no"],
        default="no",
    )
    parser.add_argument(
        "--sha",
        type=str,
        default=None,
        help="expected team/team SHA for team_tip mode",
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
            contract, args.version, args.confirm_major == "yes", args.json
        )
    if args.mode == "public_remote":
        return mode_public_remote(contract, args.superseded)
    if args.mode == "file_map":
        return mode_file_map(args.map.resolve())
    if args.mode == "align":
        return mode_align(root, contract)
    if args.mode == "team":
        return mode_team(root, contract)
    if args.mode == "public":
        return mode_public(root, contract)
    if args.mode == "team_tip":
        return mode_team_tip(root, contract, args.sha)
    if args.mode == "legacy_remote":
        return mode_legacy_remote(contract, root)
    if args.mode == "prune_team_remote":
        return mode_prune_team_remote(contract, root)
    if args.mode == "postflight":
        return mode_postflight(root, contract)
    return _fail(f"unknown mode {args.mode}")


if __name__ == "__main__":
    sys.exit(main())
