#!/usr/bin/env python3
"""Failure comment on CRTQA (no API attachment)."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def _fail(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def main() -> int:
    epic = os.environ.get("EPIC_KEY", "").strip() or "?"
    qa = os.environ.get("QA_TASK_KEY", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    base = os.environ.get("JIRA_BASE_URL", "https://jira.in.devexperts.com").rstrip("/")
    build_url = os.environ.get("TEAMCITY_BUILD_URL", "").strip() or "unknown"

    if not qa:
        _fail("QA_TASK_KEY required")
    if not token:
        _fail("JIRA_API_TOKEN required")

    comment = (
        f"Corner Epic QA: pipeline failed for {epic}.\n\n"
        f"Build: {build_url}\n\n"
        f"Open the build log for the failing step. "
        f"If the run got far enough, partial outputs may be in TeamCity artifacts epic-work."
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
