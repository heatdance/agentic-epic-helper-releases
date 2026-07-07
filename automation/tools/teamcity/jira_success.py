#!/usr/bin/env python3
"""Attach coverage.md + comment on CRTQA (Jira DC Bearer PAT)."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


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


def _try_attach(*, base: str, qa: str, token: str, md: Path) -> str | None:
    attach_url = f"{base}/rest/api/2/issue/{qa}/attachments"
    boundary = f"----cornerqa{uuid.uuid4().hex}"
    mime = mimetypes.guess_type(md.name)[0] or "text/markdown"
    file_bytes = md.read_bytes()
    payload = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{md.name}"\r\n'.encode(),
            f"Content-Type: {mime}\r\n\r\n".encode(),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    req = Request(
        attach_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Atlassian-Token": "no-check",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urlopen(req) as resp:
            print("attach status:", resp.status)
        return None
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        return f"HTTP {exc.code}: {detail}"


def main() -> int:
    epic = os.environ.get("EPIC_KEY", "").strip()
    qa = os.environ.get("QA_TASK_KEY", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    base = os.environ.get("JIRA_BASE_URL", "https://jira.in.devexperts.com").rstrip("/")
    build_url = os.environ.get("TEAMCITY_BUILD_URL", "").strip()

    if not epic or not qa:
        _fail("EPIC_KEY and QA_TASK_KEY required")
    if not token:
        _fail("JIRA_API_TOKEN required")

    md = Path(f"epics/{epic}/{epic}-coverage.md")
    if not md.is_file():
        _fail(f"missing {md}")

    print(f"Jira success: {qa} epic {epic} file {md}")

    attach_err = _try_attach(base=base, qa=qa, token=token, md=md)

    comment = f"Corner Epic QA: coverage for *{epic}* is ready."
    if build_url:
        comment += f"\n\nBuild: {build_url}"
        comment += (
            f"\n\nTeamCity artifacts: download *epic-work* from the build "
            f"(contains `{md.name}` and JSON)."
        )
    if attach_err:
        print(f"WARN: attach failed: {attach_err}", file=sys.stderr)
        comment += (
            "\n\n*Attachment via API failed* (often missing *Attach files* permission "
            "on CRTQA for the PAT user). Coverage is in TeamCity artifacts *epic-work*."
        )
    else:
        comment += f"\n\nAttached: `{md.name}`."

    try:
        _post_comment(base=base, qa=qa, token=token, body=comment)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        _fail(f"comment HTTP {exc.code}: {detail}")

    print("Jira success OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
