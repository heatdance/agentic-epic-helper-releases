#!/usr/bin/env python3
"""Apply public-tier mechanical transforms (readmes, deletes, template overlays) per clean-contract."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "docs/clean-contract.json"
CONTENT_ROOT = REPO_ROOT / "docs/clean-public-content"


def _load() -> dict:
    with CONTRACT.open(encoding="utf-8") as f:
        return json.load(f)


def _copy_seed(root: Path, rel: str) -> None:
    src = CONTENT_ROOT / rel
    if not src.is_file():
        raise FileNotFoundError(f"missing public content seed: {src}")
    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _apply_template_overlays(root: Path, contract: dict) -> None:
    overlays = contract.get("public", {}).get("template_overlays", {})
    for dest_rel, src_rel in overlays.items():
        src = REPO_ROOT / src_rel
        dest = root / dest_rel
        if not src.is_file():
            raise FileNotFoundError(f"template overlay source missing: {src}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def _is_gitignored(root: Path, rel: str) -> bool:
    """True when rel is ignored by git (operator-local paths must survive public strip)."""
    proc = subprocess.run(
        ["git", "check-ignore", "-q", rel],
        cwd=root,
        capture_output=True,
    )
    return proc.returncode == 0


def _delete_forbidden_paths(root: Path, contract: dict) -> None:
    for rel in contract.get("public", {}).get("delete_paths", []):
        if rel == ".cursor/mcp.json" and _is_gitignored(root, rel):
            continue
        p = root / rel
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p, ignore_errors=True)


def apply(root: Path, export_version: str, source_branch: str, source_sha: str) -> None:
    contract = _load()
    pub = contract["public"]

    _delete_forbidden_paths(root, contract)

    for pat in pub.get("delete_globs", []):
        for p in list(root.glob(pat)):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            elif p.is_file() and not str(p).endswith("-readme.md"):
                if "templates" in p.as_posix() and "public" in p.as_posix():
                    continue
                p.unlink(missing_ok=True)

    pipelines = root / ".cursor/pipelines"
    for md in list(pipelines.glob("*.md")):
        if md.name.endswith("-readme.md") or md.name == "clean.md":
            continue
        pid = md.stem
        seed = CONTENT_ROOT / "pipelines" / f"{pid}-readme.md"
        readme = pipelines / f"{pid}-readme.md"
        if seed.is_file():
            readme.write_text(seed.read_text(encoding="utf-8"), encoding="utf-8")
        md.unlink(missing_ok=True)

    for pid in pub.get("required_readmes", []):
        seed = CONTENT_ROOT / "pipelines" / f"{pid}-readme.md"
        readme = pipelines / f"{pid}-readme.md"
        if seed.is_file():
            readme.parent.mkdir(parents=True, exist_ok=True)
            readme.write_text(seed.read_text(encoding="utf-8"), encoding="utf-8")

    _apply_template_overlays(root, contract)

    _copy_seed(root, "README.md")
    _copy_seed(root, "HOW-TO.md")
    _copy_seed(root, "AGENTS.md")

    manifest = {
        "schema_version": 1,
        "export_version": export_version,
        "last_source_branch": source_branch,
        "last_source_sha": source_sha,
        "last_run_utc": __import__("datetime")
        .datetime.now(__import__("datetime").timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "validation_log": "clean_apply_public + clean_verify public",
        "notes": "Guide-only export per docs/clean-public-style.md",
    }
    (root / "docs/public-export-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    qh = root / "qa-handoff.md"
    if qh.is_file():
        qh.unlink()
    example = root / "qa-handoff.example.md"
    if not example.is_file():
        example.write_text(
            "# QA handoff (example)\n\n"
            "Session focus and next steps — copy to `qa-handoff.md` locally.\n",
            encoding="utf-8",
        )

    for rel in (
        "docs/harness-map.json",
        "docs/dxcore-console-harness.json",
        "docs/dxtrade5-harness",
        "docs/webbroker-harness",
        "docs/project.json",
        "docs/qa-project.json",
        "docs/corner-platform-map.json",
        "docs/calibrate-contract.json",
        "docs/clean-publish-tier-matrix.json",
        "docs/clean-publish-tier-matrix.md",
        "docs/release-notes-contract.json",
    ):
        p = root / rel
        if p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    for rel in (".cursor/calibrate", ".cursor/commands", ".cursor/prompts"):
        p = root / rel
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    tools = root / "automation" / "tools"
    if tools.is_dir():
        for py in tools.glob("*.py"):
            if py.name == "clean_verify.py":
                continue
            if py.name.endswith("_verify.py") or py.name in (
                "calibrate_verify.py",
                "close_archive.py",
                "release_notes.py",
                "clean_apply_public.py",
                "clean_apply_team.py",
                "clean_file_map.py",
            ):
                py.unlink(missing_ok=True)

    (root / "epics/README.md").write_text(
        "# Epics layout (guide)\n\n"
        "Use `epics/templates/` for JSON schemas. "
        "Create `epics/<YOUR-KEY>/` locally with artefacts from pipeline readmes.\n",
        encoding="utf-8",
    )

    docs_keep = {
        "clean-public-style.md",
        "public-export-manifest.json",
        "public-export-manifest.example.json",
    }
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for p in list(docs_dir.rglob("*")):
            if p.is_file() and p.name not in docs_keep:
                p.unlink(missing_ok=True)
        for p in sorted(docs_dir.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            if p.is_dir() and not any(p.iterdir()):
                p.rmdir()

    rules_dir = root / ".cursor/rules"
    if rules_dir.is_dir():
        shutil.rmtree(rules_dir, ignore_errors=True)
    router = root / ".cursor/rules/pipeline-router.mdc"
    router.parent.mkdir(parents=True, exist_ok=True)
    router.write_text(
        "---\ndescription: Public guide — no executable pipelines\nalwaysApply: true\n---\n\n"
        "# Pipeline router (public export)\n\n"
        "Guide-only tree. Read `.cursor/pipelines/*-readme.md`. "
        "Implement triggers in your private harness.\n",
        encoding="utf-8",
    )

    public_overlay_dir = root / "epics/templates/public"
    if public_overlay_dir.is_dir():
        shutil.rmtree(public_overlay_dir, ignore_errors=True)


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--export-version", default="1.2.0")
    p.add_argument("--source-branch", default="team")
    p.add_argument("--source-sha", default="0000000")
    args = p.parse_args()
    apply(args.root.resolve(), args.export_version, args.source_branch, args.source_sha)
    print(f"Applied public transform to {args.root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
