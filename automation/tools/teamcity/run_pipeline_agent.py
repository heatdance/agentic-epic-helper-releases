#!/usr/bin/env python3
"""TeamCity pipeline agent runner — MCP + project rules + required artefacts."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import sys
from pathlib import Path

ENABLED_TOOLS = (
    "confluence_search,confluence_get_page,jira_search,jira_get_issue,"
    "bitbucket_list_repositories,bitbucket_search_code,bitbucket_get_file_content,"
    "bitbucket_browse_directory,bitbucket_list_pull_requests,bitbucket_get_pull_request,"
    "bitbucket_get_pull_request_diff,bitbucket_list_commits,bitbucket_get_commit"
)


def _env(name: str, default: str) -> str:
    return (os.environ.get(name) or default).strip()


def _mcp_env() -> dict[str, str]:
    token = (os.environ.get("JIRA_API_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("JIRA_API_TOKEN empty (Atlassian MCP PAT)")

    jira_url = _env("ATLASSIAN_MCP_JIRA_URL", _env("JIRA_BASE_URL", "https://jira.in.devexperts.com"))
    confluence_url = _env("ATLASSIAN_MCP_CONFLUENCE_URL", "https://confluence.in.devexperts.com")
    bitbucket_url = _env("ATLASSIAN_MCP_BITBUCKET_URL", "https://stash.in.devexperts.com")

    return {
        "CONFLUENCE_URL": confluence_url.rstrip("/"),
        "CONFLUENCE_PERSONAL_TOKEN": token,
        "CONFLUENCE_SSL_VERIFY": "false",
        "JIRA_URL": jira_url.rstrip("/"),
        "JIRA_PERSONAL_TOKEN": token,
        "JIRA_SSL_VERIFY": "false",
        "BITBUCKET_URL": bitbucket_url.rstrip("/"),
        "BITBUCKET_PERSONAL_TOKEN": token,
        "BITBUCKET_SSL_VERIFY": "false",
        "READ_ONLY_MODE": "true",
        "ENABLED_TOOLS": ENABLED_TOOLS,
    }


def _expand_path(pattern: str, epic_key: str) -> Path:
    expanded = pattern.replace("%EPIC_KEY%", epic_key).replace("{EPIC_KEY}", epic_key)
    return Path(expanded)


def _check_required(paths: list[Path]) -> int:
    missing = [str(p) for p in paths if not p.is_file()]
    if not missing:
        return 0
    print("ERROR: required output file(s) missing:", file=sys.stderr)
    for path in missing:
        print(f"  - {path}", file=sys.stderr)
    return 3


def _build_options(repo_root: Path):
    from cursor_sdk import AgentOptions, LocalAgentOptions, StdioMcpServerConfig

    return AgentOptions(
        api_key=os.environ["CURSOR_API_KEY"],
        model=os.environ.get("AGENT_MODEL", "composer-2.5"),
        local=LocalAgentOptions(
            cwd=str(repo_root),
            setting_sources=["project"],
        ),
        mcp_servers={
            "user-mcp-atlassian": StdioMcpServerConfig(
                command="uvx",
                args=["--with", "fakeredis<2.35", "mcp-atlassian-with-bitbucket"],
                env=_mcp_env(),
            ),
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a Corner pipeline Cursor agent step")
    parser.add_argument("--prompt", required=True, help="Agent prompt (pipeline trigger text)")
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="PATH",
        help="Required output file after agent (repeatable; %%EPIC_KEY%% expanded)",
    )
    parser.add_argument(
        "--dry-check",
        action="store_true",
        help="Validate env and --require path expansion only (no SDK call)",
    )
    args = parser.parse_args(argv)

    epic = (os.environ.get("EPIC_KEY") or "").strip()
    if not epic:
        print("ERROR: EPIC_KEY empty", file=sys.stderr)
        return 1

    api_key = (os.environ.get("CURSOR_API_KEY") or "").strip()
    if not api_key:
        print("ERROR: CURSOR_API_KEY empty", file=sys.stderr)
        return 1

    repo_root = Path(os.environ.get("REPO_ROOT", os.getcwd())).resolve()
    max_wait_min = int(os.environ.get("AGENT_MAX_WAIT_MINUTES", "45"))
    max_wait_sec = max_wait_min * 60

    required = [_expand_path(p, epic) for p in args.require]
    if args.dry_check:
        print(f"repo_root={repo_root}")
        print(f"epic={epic}")
        print(f"max_wait_minutes={max_wait_min}")
        for path in required:
            print(f"require={path}")
        return 0

    try:
        options = _build_options(repo_root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    from cursor_sdk import Agent, CursorAgentError

    print(f"Starting agent (timeout {max_wait_min} min)…")
    print(f"Prompt: {args.prompt[:200]}{'…' if len(args.prompt) > 200 else ''}")

    try:
        agent = Agent.create(options)
        run = agent.send(args.prompt)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(run.wait)
            try:
                result = future.result(timeout=max_wait_sec)
            except concurrent.futures.TimeoutError:
                print(f"ERROR: agent wait exceeded {max_wait_min} minutes", file=sys.stderr)
                try:
                    run.cancel()
                except Exception:
                    pass
                return 2
    except CursorAgentError as exc:
        print(f"ERROR: CursorAgentError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: agent failed: {exc}", file=sys.stderr)
        return 1

    status = getattr(result, "status", None) or getattr(run, "status", None)
    print(f"status: {status}")

    if status != "finished":
        return 2

    return _check_required(required)


if __name__ == "__main__":
    raise SystemExit(main())
