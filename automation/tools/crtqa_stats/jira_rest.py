#!/usr/bin/env python3
"""Jira REST helpers for CRTQA stats (shared creds with MCP)."""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]


def load_jira_env() -> tuple[str, str]:
    candidates = [
        Path(os.environ.get("USERPROFILE", "")) / ".cursor" / "mcp.json",
        REPO / ".cursor" / "mcp.json",
        Path.home() / ".cursor" / "mcp.json",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for name in (
            "user-mcp-atlassian",
            "mcp-atlassian",
            "project-0-cursor.corner-user-mcp-atlassian",
        ):
            srv = data.get("mcpServers", {}).get(name, {})
            env = srv.get("env", {})
            url = env.get("JIRA_URL", "").rstrip("/")
            token = env.get("JIRA_PERSONAL_TOKEN") or env.get("JIRA_API_TOKEN")
            if url and token:
                return url, token
    raise SystemExit("Jira credentials not found in ~/.cursor/mcp.json")


def jira_request(base: str, token: str, path: str, params: dict | None = None) -> dict:
    qs = urllib.parse.urlencode(params or {})
    url = f"{base}{path}" + (f"?{qs}" if qs else "")
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def jira_search(
    base: str,
    token: str,
    jql: str,
    fields: str,
    start_at: int = 0,
    limit: int = 50,
) -> dict:
    return jira_request(
        base,
        token,
        "/rest/api/2/search",
        {"jql": jql, "fields": fields, "startAt": str(start_at), "maxResults": str(limit)},
    )


ISSUE_DETAIL_FIELDS = (
    "summary,status,issuetype,worklog,timetracking,customfield_11250,customfield_10006"
)


def normalize_issue(raw: dict) -> dict:
    fields = raw.get("fields") or {}
    status = fields.get("status") or {}
    issuetype = fields.get("issuetype") or {}
    out: dict = {
        "id": raw.get("id"),
        "key": raw.get("key"),
        "summary": fields.get("summary"),
        "status": {
            "name": status.get("name"),
            "category": (status.get("statusCategory") or {}).get("key"),
        },
        "issue_type": {"name": issuetype.get("name")},
        "worklog": fields.get("worklog"),
        "timetracking": fields.get("timetracking"),
        "customfield_11250": fields.get("customfield_11250"),
        "customfield_10006": fields.get("customfield_10006"),
    }
    el = fields.get("customfield_10006")
    if isinstance(el, dict) and el.get("key"):
        out["customfield_10006"] = el.get("key")
    return out


EPIC_META_FIELDS = "summary,labels,components,description"


def normalize_epic_meta(raw: dict) -> dict[str, Any]:
    fields = raw.get("fields") or {}
    labels = fields.get("labels") or []
    components = []
    for comp in fields.get("components") or []:
        if isinstance(comp, dict):
            components.append(str(comp.get("name") or ""))
        else:
            components.append(str(comp))
    return {
        "summary": str(fields.get("summary") or raw.get("summary") or ""),
        "labels": labels,
        "components": components,
        "description": str(fields.get("description") or "")[:2000],
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def fetch_epic_meta_map(epic_keys: list[str]) -> dict[str, dict[str, Any]]:
    if not epic_keys:
        return {}
    base, token = load_jira_env()
    out: dict[str, dict[str, Any]] = {}
    for key in sorted({k.upper() for k in epic_keys}):
        try:
            raw = jira_request(base, token, f"/rest/api/2/issue/{key}", {"fields": EPIC_META_FIELDS})
            out[key] = normalize_epic_meta(raw)
        except Exception as exc:  # noqa: BLE001
            out[key] = {
                "summary": key,
                "labels": [],
                "components": [],
                "description": "",
                "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fetch_error": str(exc)[:200],
            }
    return out
