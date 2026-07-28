#!/usr/bin/env python3
"""Failure comment on CRTQA (no API attachment)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from jira_comment import (
    STATUS_FAILED,
    artifact_status,
    coverage_metrics,
    last_completed_stage,
    render_comment,
    resolve_epic_json,
)
from read_teamcity_params import resolve_teamcity_build_url

RERUN_ACTION = (
    "open the build log at the failing step, then rerun Manual Pipeline with the "
    "same EPIC_KEY and QA_TASK_KEY"
)


def _fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _stage(repo_root: Path, current_step: str | None) -> str:
    if current_step:
        return f"failed at {current_step}"
    last_ok = last_completed_stage(repo_root / ".teamcity-ci" / "state")
    return f"failed after {last_ok}" if last_ok else "failed before the first step marker"


def build_failure_comment(
    *,
    epic: str,
    build_url: str,
    repo_root: Path,
    current_step: str | None = None,
) -> str:
    epic_dir = repo_root / "epics" / epic
    have_epic_dir = epic != "?" and epic_dir.is_dir()
    status = artifact_status(epic_dir, epic) if have_epic_dir else None

    notes: list[str] = []
    metrics = None
    if status and status["coverage.json"]:
        metrics = coverage_metrics(
            repo_root,
            resolve_epic_json(epic_dir, epic, "ref"),
            resolve_epic_json(epic_dir, epic, "coverage"),
        )
        notes.append(
            "on a COVERAGE verify failure, check smart_checklist_markdown for forbidden "
            "oracle enum tokens and use human-readable > lines in -coverage.md only"
        )

    return render_comment(
        status=STATUS_FAILED,
        epic=epic,
        build_url=build_url,
        stage=_stage(repo_root, current_step),
        artifacts=status,
        metrics=metrics,
        next_action=RERUN_ACTION,
        notes=tuple(notes),
    )


def main() -> int:
    epic = os.environ.get("EPIC_KEY", "").strip() or "?"
    qa = os.environ.get("QA_TASK_KEY", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    base = os.environ.get("JIRA_BASE_URL", "https://jira.in.devexperts.com").rstrip("/")
    build_url = (
        os.environ.get("TEAMCITY_BUILD_URL", "").strip()
        or resolve_teamcity_build_url()
        or "unknown"
    )
    repo_root = Path(os.environ.get("REPO_ROOT", os.getcwd()))

    if not qa:
        _fail("QA_TASK_KEY required")
    if not token:
        _fail("JIRA_API_TOKEN required")

    comment = build_failure_comment(
        epic=epic,
        build_url=build_url,
        repo_root=repo_root,
        current_step=os.environ.get("CORNER_CI_STEP", "").strip() or None,
    )

    print(f"Jira failure comment on {qa} (epic {epic})")
    url = f"{base}/rest/api/2/issue/{qa}/comment"
    req = Request(
        url,
        data=json.dumps({"body": comment}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req) as resp:
            print("comment status:", resp.status)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        _fail(f"comment HTTP {exc.code}: {detail}")

    print("Jira failure comment posted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
