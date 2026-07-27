#!/usr/bin/env python3
"""Write gitignored .cursor/mcp.json for CI (user-mcp-atlassian only)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ENABLED_TOOLS = (
    "confluence_search,confluence_get_page,jira_search,jira_get_issue,"
    "bitbucket_list_repositories,bitbucket_search_code,bitbucket_get_file_content,"
    "bitbucket_browse_directory,bitbucket_list_pull_requests,bitbucket_get_pull_request,"
    "bitbucket_get_pull_request_diff,bitbucket_list_commits,bitbucket_get_commit"
)


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _require_token(name: str) -> str:
    value = _env(name)
    if not value:
        print(
            f"ERROR: {name} empty.\n"
            f"TeamCity: add password parameter {name} on Pipeline config, and set\n"
            f"  env.{name} = %{name}% under Environment variables.\n"
            "Data Center requires a separate PAT per application "
            "(Jira / Confluence / Bitbucket-Stash).",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return value


def main() -> int:
    jira_token = _require_token("JIRA_API_TOKEN")
    confluence_token = _require_token("CONFLUENCE_API_TOKEN")
    bitbucket_token = _require_token("BITBUCKET_API_TOKEN")

    jira_url = _env("ATLASSIAN_MCP_JIRA_URL", _env("JIRA_BASE_URL", "https://jira.in.devexperts.com"))
    confluence_url = _env("ATLASSIAN_MCP_CONFLUENCE_URL", "https://confluence.in.devexperts.com")
    bitbucket_url = _env("ATLASSIAN_MCP_BITBUCKET_URL", "https://stash.in.devexperts.com")

    for label, url in (
        ("JIRA", jira_url),
        ("CONFLUENCE", confluence_url),
        ("BITBUCKET", bitbucket_url),
    ):
        if not url.startswith("https://"):
            print(f"ERROR: invalid {label} URL: {url!r}", file=sys.stderr)
            return 1

    cfg = {
        "mcpServers": {
            "user-mcp-atlassian": {
                "command": "uvx",
                "args": ["--with", "fakeredis<2.35", "mcp-atlassian-with-bitbucket"],
                "env": {
                    "CONFLUENCE_URL": confluence_url.rstrip("/"),
                    "CONFLUENCE_PERSONAL_TOKEN": confluence_token,
                    "CONFLUENCE_SSL_VERIFY": "false",
                    "JIRA_URL": jira_url.rstrip("/"),
                    "JIRA_PERSONAL_TOKEN": jira_token,
                    "JIRA_SSL_VERIFY": "false",
                    "BITBUCKET_URL": bitbucket_url.rstrip("/"),
                    "BITBUCKET_PERSONAL_TOKEN": bitbucket_token,
                    "BITBUCKET_SSL_VERIFY": "false",
                    "READ_ONLY_MODE": "true",
                    "ENABLED_TOOLS": ENABLED_TOOLS,
                },
            }
        }
    }

    out = Path(".cursor") / "mcp.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {out} (user-mcp-atlassian; separate Jira/Confluence/Bitbucket PATs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
