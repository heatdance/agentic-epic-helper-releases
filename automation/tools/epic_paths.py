#!/usr/bin/env python3
"""
Canonical epic workspace paths (dependencies layout).

Pre-CLOSE: coverage.md at epic root; JSON and other md under dependencies/.
Post-CLOSE: three md at root; JSON under context/.

Example:
  from epic_paths import epic_dir, dep_json, coverage_md, resolve_artifact
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parents[2]
EPICS_ROOT = REPO_ROOT / "epics"
DEPENDENCIES_DIR = "dependencies"
CONTEXT_DIR = "context"

ArtifactStem = Literal[
    "ref",
    "coverage",
    "analysis",
    "discover",
    "tests",
    "precon",
    "close",
]


def epic_dir(key: str, repo_root: Path | None = None) -> Path:
    root = repo_root if repo_root is not None else REPO_ROOT
    return root / "epics" / key


def dependencies_dir(key: str, repo_root: Path | None = None) -> Path:
    return epic_dir(key, repo_root) / DEPENDENCIES_DIR


def context_dir(key: str, repo_root: Path | None = None) -> Path:
    return epic_dir(key, repo_root) / CONTEXT_DIR


def artifact_basename(key: str, stem: ArtifactStem) -> str:
    return f"{key}-{stem}.json"


def dep_json(key: str, stem: ArtifactStem, repo_root: Path | None = None) -> Path:
    return dependencies_dir(key, repo_root) / artifact_basename(key, stem)


def coverage_md(key: str, repo_root: Path | None = None) -> Path:
    return epic_dir(key, repo_root) / f"{key}-coverage.md"


def analysis_md(key: str, repo_root: Path | None = None) -> Path:
    return dependencies_dir(key, repo_root) / f"{key}-analysis.md"


def tests_md(key: str, repo_root: Path | None = None) -> Path:
    return dependencies_dir(key, repo_root) / f"{key}-tests.md"


def precon_md(key: str, repo_root: Path | None = None) -> Path:
    return dependencies_dir(key, repo_root) / f"{key}-precon.md"


def root_json_legacy(key: str, stem: ArtifactStem, repo_root: Path | None = None) -> Path:
    return epic_dir(key, repo_root) / artifact_basename(key, stem)


def resolve_json(
    key: str,
    stem: ArtifactStem,
    repo_root: Path | None = None,
    *,
    allow_context: bool = False,
    allow_legacy_root: bool = True,
) -> Path:
    """Resolve JSON path: dependencies/ first, then optional fallbacks."""
    dep = dep_json(key, stem, repo_root)
    if dep.is_file():
        return dep
    if allow_context:
        ctx = context_dir(key, repo_root) / artifact_basename(key, stem)
        if ctx.is_file():
            return ctx
    if allow_legacy_root:
        leg = root_json_legacy(key, stem, repo_root)
        if leg.is_file():
            return leg
    return dep


def resolve_md(
    key: str,
    kind: Literal["coverage", "analysis", "tests", "precon"],
    repo_root: Path | None = None,
    *,
    allow_root_promoted: bool = True,
) -> Path:
    """Resolve md: pre-CLOSE dependencies/; post-CLOSE analysis/tests may be at root."""
    ed = epic_dir(key, repo_root)
    dep = dependencies_dir(key, repo_root)
    if kind == "coverage":
        return ed / f"{key}-coverage.md"
    name = f"{key}-{kind}.md"
    dep_path = dep / name
    if dep_path.is_file():
        return dep_path
    if allow_root_promoted:
        root_path = ed / name
        if root_path.is_file():
            return root_path
    return dep_path


def ensure_dependencies_dir(key: str, repo_root: Path | None = None) -> Path:
    d = dependencies_dir(key, repo_root)
    d.mkdir(parents=True, exist_ok=True)
    return d
