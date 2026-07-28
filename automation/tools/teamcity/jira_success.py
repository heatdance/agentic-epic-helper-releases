#!/usr/bin/env python3
"""Success comment on CRTQA after green pipeline (no API attachment)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from jira_comment import (
    STATUS_READY,
    artifact_status,
    coverage_metrics,
    last_completed_stage,
    render_comment,
    resolve_epic_json,
)
from read_teamcity_params import resolve_teamcity_build_url

# This file sits three levels below the repo root (automation/tools/teamcity/),
# so parents[2] resolves to automation/ and hid every epic under automation/epics/.
REPO_ROOT = Path(os.environ.get("REPO_ROOT") or Path(__file__).resolve().parents[3])


def _fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _post_comment(*, base: str, qa: str, token: str, body: str) -> None:
    url = f"{base}/rest/api/2/issue/{qa}/comment"
    req = Request(
        url,
        data=json.dumps({"body": body}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req) as resp:
        print("comment status:", resp.status)


def _resolve_ref(epic: str, repo_root: Path | None = None) -> Path:
    root = repo_root or REPO_ROOT
    return resolve_epic_json(root / "epics" / epic, epic, "ref")


def _failed_snippet_keys(epic: str) -> list[str]:
    """Return requirement keys with snippet_status != ok."""
    ref_path = _resolve_ref(epic)
    if not ref_path.is_file():
        _fail(f"ref missing for success gate: {ref_path}")
    try:
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(f"cannot read ref {ref_path}: {exc}")
    if not isinstance(ref, dict):
        _fail(f"invalid ref JSON: {ref_path}")

    failed: list[str] = []
    for row in ref.get("requirements") or []:
        if not isinstance(row, dict):
            continue
        key = str(row.get("key") or "").strip()
        if not key:
            continue
        if row.get("snippet_status") != "ok":
            failed.append(f"{key}:{row.get('snippet_status') or 'missing'}")
    return failed


def main() -> int:
    epic = os.environ.get("EPIC_KEY", "").strip()
    qa = os.environ.get("QA_TASK_KEY", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    base = os.environ.get("JIRA_BASE_URL", "https://jira.in.devexperts.com").rstrip("/")
    build_url = os.environ.get("TEAMCITY_BUILD_URL", "").strip() or resolve_teamcity_build_url()

    if not epic or not qa:
        _fail("EPIC_KEY and QA_TASK_KEY required")
    if not token:
        _fail("JIRA_API_TOKEN required")
    if not build_url:
        _fail(
            "TEAMCITY_BUILD_URL required "
            "(set env or ensure teamcity.build.url in TeamCity properties)"
        )

    bad = _failed_snippet_keys(epic)
    if bad:
        _fail(
            "refusing Jira success comment: requirement snippets not ok — "
            + ", ".join(bad)
            + " (fix Confluence/Bitbucket PATs and re-run EPIC-PREP)"
        )

    epic_dir = REPO_ROOT / "epics" / epic
    comment = render_comment(
        status=STATUS_READY,
        epic=epic,
        build_url=build_url,
        stage=f"green through {last_completed_stage(REPO_ROOT / '.teamcity-ci' / 'state') or 'ANALYSE verify'}",
        artifacts=artifact_status(epic_dir, epic),
        metrics=coverage_metrics(
            REPO_ROOT,
            _resolve_ref(epic),
            resolve_epic_json(epic_dir, epic, "coverage"),
        ),
        next_action=(
            f"download epic-work and extend {epic}-coverage.md on this ticket "
            "— the repo copy is machine-generated and is not edited in place"
        ),
    )

    print(f"Jira success comment on {qa} (epic {epic})")
    try:
        _post_comment(base=base, qa=qa, token=token, body=comment)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        _fail(f"comment HTTP {exc.code}: {detail}")

    print("Jira success OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
