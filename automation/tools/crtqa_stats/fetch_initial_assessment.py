#!/usr/bin/env python3
"""Fetch Jira data for CRTQA stats v5 initial_assessment (Jira REST, MCP creds)."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TOOLS = REPO / "automation" / "tools"
sys.path.insert(0, str(TOOLS))

from crtqa_stats.gather import extract_epics_from_issue  # noqa: E402
from crtqa_stats.jira_rest import fetch_epic_meta_map  # noqa: E402

QA_JQL_SUFFIX = (
    'AND ((issuetype = "Test Execution" AND summary ~ "Test Case Development") '
    'OR (issuetype = "Test Execution" AND (summary ~ "Epic Testing" OR summary ~ "Epic Validation")) '
    'OR (issuetype = "Test Execution" AND summary ~ "Release notes") '
    'OR (issuetype = "QA Task" AND summary ~ "Update test")) ORDER BY key ASC'
)
ISSUE_FIELDS = "summary,status,issuetype,worklog,timetracking,customfield_11250,customfield_10006"
EPIC_CHUNK = 40
EPIC_IN_SUMMARY = re.compile(r"\b(CRT-\d+)\b", re.I)


def _load_jira_env() -> tuple[str, str]:
    candidates = [
        Path(os.environ.get("USERPROFILE", "")) / ".cursor" / "mcp.json",
        REPO / ".cursor" / "mcp.json",
        Path.home() / ".cursor" / "mcp.json",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for name in ("user-mcp-atlassian", "mcp-atlassian", "project-0-cursor.corner-user-mcp-atlassian"):
            srv = data.get("mcpServers", {}).get(name, {})
            env = srv.get("env", {})
            url = env.get("JIRA_URL", "").rstrip("/")
            token = env.get("JIRA_PERSONAL_TOKEN") or env.get("JIRA_API_TOKEN")
            if url and token:
                return url, token
    raise SystemExit("Jira credentials not found in ~/.cursor/mcp.json")


def _request(base: str, token: str, path: str, params: dict | None = None) -> dict:
    qs = urllib.parse.urlencode(params or {})
    url = f"{base}{path}" + (f"?{qs}" if qs else "")
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def _search(base: str, token: str, jql: str, fields: str, start_at: int, limit: int = 50) -> dict:
    return _request(
        base,
        token,
        "/rest/api/2/search",
        {"jql": jql, "fields": fields, "startAt": str(start_at), "maxResults": str(limit)},
    )


def _normalize_links(raw: dict) -> dict:
    """REST camelCase issuelinks → MCP snake_case for gather.extract_epics_from_issue."""
    fields = raw.get("fields") or {}
    links = fields.get("issuelinks") or raw.get("issuelinks") or []
    norm_links = []
    for link in links:
        nl: dict = {"type": link.get("type") or {}}
        for rest_key, mcp_key in (("inwardIssue", "inward_issue"), ("outwardIssue", "outward_issue")):
            li = link.get(rest_key)
            if not li:
                continue
            lf = li.get("fields") or {}
            it = lf.get("issuetype") or {}
            nl[mcp_key] = {
                "key": li.get("key"),
                "fields": {
                    "summary": lf.get("summary"),
                    "issuetype": {"name": it.get("name") if isinstance(it, dict) else it},
                },
            }
        norm_links.append(nl)
    return {
        "key": raw.get("key"),
        "summary": fields.get("summary") or raw.get("summary"),
        "fields": {"summary": fields.get("summary"), "issuelinks": norm_links},
        "issuelinks": norm_links,
    }


def _normalize_issue(raw: dict) -> dict:
    fields = raw.get("fields", {})
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


def _epic_from_qa_raw(raw: dict) -> str | None:
    fields = raw.get("fields") or {}
    el = fields.get("customfield_10006")
    if isinstance(el, dict) and el.get("key"):
        return str(el["key"]).upper()
    if isinstance(el, str) and el.upper().startswith("CRT-"):
        return el.upper()
    m = EPIC_IN_SUMMARY.search(str(fields.get("summary") or ""))
    return m.group(1).upper() if m else None


def fetch(jira_user: str, out_dir: Path, exclude_epics: list[str]) -> dict:
    base, token = _load_jira_env()
    out_dir.mkdir(parents=True, exist_ok=True)
    exclude = {e.upper() for e in exclude_epics}

    test_jql = f"project = CRTQA AND issuetype = Test AND reporter = {jira_user} ORDER BY created ASC"
    first = _search(base, token, test_jql, "key,summary,issuelinks", 0, 50)
    total_tests = int(first.get("total") or 0)
    pages_dir = out_dir / "tests-pages"
    pages_dir.mkdir(exist_ok=True)

    all_tests: list[dict] = []
    for start in range(0, max(total_tests, 1), 50):
        page = first if start == 0 else _search(base, token, test_jql, "key,summary,issuelinks", start, 50)
        (pages_dir / f"page-{start}.json").write_text(json.dumps(page, indent=2), encoding="utf-8")
        all_tests.extend(page.get("issues") or [])

    epics: set[str] = set()
    for t in all_tests:
        norm = _normalize_links(t)
        found, _, _ = extract_epics_from_issue(norm)
        epics.update(found)
    epics_all = sorted(epics)
    epics_qa = sorted(e for e in epics_all if e not in exclude)

    (out_dir / "epics.json").write_text(
        json.dumps({"epics": epics_qa, "count": len(epics_qa), "all_with_excluded": epics_all}, indent=2),
        encoding="utf-8",
    )
    if exclude:
        (out_dir / "excluded.json").write_text(
            json.dumps({"excluded": sorted(exclude), "reason": "operator_excluded_initial_assessment"}, indent=2),
            encoding="utf-8",
        )

    qa_issues: list[dict] = []
    for i in range(0, len(epics_qa), EPIC_CHUNK):
        chunk = epics_qa[i : i + EPIC_CHUNK]
        in_clause = ", ".join(chunk)
        jql = f'"Epic Link" in ({in_clause}) {QA_JQL_SUFFIX}'
        start = 0
        while True:
            res = _search(base, token, jql, ISSUE_FIELDS, start, 50)
            batch = res.get("issues") or []
            for iss in batch:
                ek = _epic_from_qa_raw(iss)
                if ek and ek in exclude:
                    continue
                qa_issues.append(iss)
            if start + len(batch) >= int(res.get("total") or 0):
                break
            start += 50

    qa_path = out_dir / "qa-tasks-search.json"
    qa_path.write_text(json.dumps({"total": len(qa_issues), "issues": qa_issues}, indent=2), encoding="utf-8")

    issues_dir = out_dir / "issues"
    issues_dir.mkdir(exist_ok=True)
    fetched = 0
    for iss in qa_issues:
        key = iss.get("key")
        if not key:
            continue
        raw = _request(base, token, f"/rest/api/2/issue/{key}", {"fields": ISSUE_FIELDS})
        (issues_dir / f"{key}.json").write_text(
            json.dumps(_normalize_issue(raw), indent=2), encoding="utf-8"
        )
        fetched += 1

    meta_keys = sorted(set(epics_qa) | exclude)
    epic_meta = fetch_epic_meta_map(meta_keys)
    (out_dir / "epic-meta.json").write_text(json.dumps(epic_meta, indent=2), encoding="utf-8")

    report = {
        "jira_user": jira_user,
        "tests_total": total_tests,
        "epics_all": len(epics_all),
        "epics_qa": len(epics_qa),
        "qa_tasks": len(qa_issues),
        "issues_fetched": fetched,
        "excluded_epics": sorted(exclude),
        "epic_meta_fetched": len(epic_meta),
    }
    (out_dir / "fetch-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--jira-user", required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--exclude-epics", nargs="*", default=[])
    args = p.parse_args()
    report = fetch(args.jira_user, args.out_dir, args.exclude_epics)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
