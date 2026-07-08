#!/usr/bin/env python3
"""Failure comment on CRTQA (no API attachment)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from read_teamcity_params import resolve_teamcity_build_url

EPIC_ARTIFACTS = (
    "ref.json",
    "coverage.json",
    "coverage.md",
    "analysis.json",
    "analysis.md",
)


def _fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _artifact_status(epic_dir: Path, epic: str) -> dict[str, bool]:
    return {
        name: (epic_dir / f"{epic}-{name}").is_file()
        for name in EPIC_ARTIFACTS
    }


def _generic_failure_comment(*, epic: str, build_url: str) -> str:
    return (
        f"Corner Epic QA: pipeline failed for {epic}.\n\n"
        f"Build: {build_url}\n\n"
        f"Open the build log for the failing step. "
        f"If the run got far enough, partial outputs may be in TeamCity artifacts epic-work."
    )


def build_failure_comment(*, epic: str, build_url: str, repo_root: Path) -> str:
    if epic == "?":
        return _generic_failure_comment(epic=epic, build_url=build_url)

    epic_dir = repo_root / "epics" / epic
    if not epic_dir.is_dir():
        return _generic_failure_comment(epic=epic, build_url=build_url)

    status = _artifact_status(epic_dir, epic)
    has_partial = status["ref.json"] or status["coverage.json"]
    if not has_partial:
        return _generic_failure_comment(epic=epic, build_url=build_url)

    lines = [
        f"Corner Epic QA: pipeline failed for {epic} (partial outputs available).",
        "",
        f"Build: {build_url}",
        "",
        "Partial artifacts in this build (download epic-work from TeamCity):",
    ]
    for name in EPIC_ARTIFACTS:
        flag = "yes" if status[name] else "no"
        lines.append(f"- {epic}-{name}: {flag}")

    lines.extend(
        [
            "",
            "Open the build log for the failing step.",
        ]
    )
    if status["coverage.json"]:
        lines.append(
            "If step 5 COVERAGE verify failed, check for forbidden oracle enum tokens "
            "in smart_checklist_markdown (e.g. first_tier_quote) — use human-readable "
            "> Oracle: lines in -coverage.md only."
        )
    lines.extend(
        [
            "",
            "Rerun: Manual Pipeline with the same EPIC_KEY and QA_TASK_KEY, "
            "or edit -coverage.md and re-run coverage_verify locally.",
        ]
    )
    return "\n".join(lines)


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

    comment = build_failure_comment(epic=epic, build_url=build_url, repo_root=repo_root)

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
