#!/usr/bin/env python3
"""Success comment on CRTQA after green pipeline (no API attachment)."""

from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from read_teamcity_params import resolve_teamcity_build_url


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

    md_name = f"{epic}-coverage.md"
    comment = (
        f"Corner Epic QA: coverage for {epic} is ready.\n\n"
        f"Build: {build_url}\n\n"
        f"TeamCity artifacts: download epic-work from the build "
        f"(contains `{md_name}` and JSON)."
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
