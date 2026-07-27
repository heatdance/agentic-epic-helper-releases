#!/usr/bin/env python3
"""TeamCity pipeline agent runner — MCP + project rules + required artefacts."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ENABLED_TOOLS = (
    "confluence_search,confluence_get_page,jira_search,jira_get_issue,"
    "bitbucket_list_repositories,bitbucket_search_code,bitbucket_get_file_content,"
    "bitbucket_browse_directory,bitbucket_list_pull_requests,bitbucket_get_pull_request,"
    "bitbucket_get_pull_request_diff,bitbucket_list_commits,bitbucket_get_commit"
)

# Heuristic min wall time before WARN (seconds) — inferred from prompt prefix, no TC params.
_MIN_DURATION_SEC: dict[str, int] = {
    "EPIC-PREP:": 300,
    "COVERAGE:": 300,
    "GROUND:": 120,
    "ANALYSE:": 180,
}


@dataclass
class RunLogStats:
    tool_started: int = 0
    tool_done: int = 0
    tool_error: int = 0
    mcp_tool_started: int = 0
    assistant_chars: int = 0
    usage_events: int = 0


def _env(name: str, default: str) -> str:
    return (os.environ.get(name) or default).strip()


def _mcp_env() -> dict[str, str]:
    jira_token = (os.environ.get("JIRA_API_TOKEN") or "").strip()
    confluence_token = (os.environ.get("CONFLUENCE_API_TOKEN") or "").strip()
    bitbucket_token = (os.environ.get("BITBUCKET_API_TOKEN") or "").strip()
    missing = [
        name
        for name, val in (
            ("JIRA_API_TOKEN", jira_token),
            ("CONFLUENCE_API_TOKEN", confluence_token),
            ("BITBUCKET_API_TOKEN", bitbucket_token),
        )
        if not val
    ]
    if missing:
        raise RuntimeError(
            "missing Atlassian PATs (Data Center requires one per app): "
            + ", ".join(missing)
        )

    jira_url = _env("ATLASSIAN_MCP_JIRA_URL", _env("JIRA_BASE_URL", "https://jira.in.devexperts.com"))
    confluence_url = _env("ATLASSIAN_MCP_CONFLUENCE_URL", "https://confluence.in.devexperts.com")
    bitbucket_url = _env("ATLASSIAN_MCP_BITBUCKET_URL", "https://stash.in.devexperts.com")

    return {
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
    }


def _expand_path(pattern: str, epic_key: str) -> Path:
    expanded = pattern.replace("%EPIC_KEY%", epic_key).replace("{EPIC_KEY}", epic_key)
    return Path(expanded)


def _iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_mcp_tool(name: str) -> bool:
    lowered = name.lower()
    markers = ("mcp", "jira", "confluence", "bitbucket", "stash")
    return any(m in lowered for m in markers)


def _min_duration_hint(prompt: str) -> int | None:
    head = prompt.lstrip()[:32]
    for prefix, seconds in _MIN_DURATION_SEC.items():
        if head.startswith(prefix):
            return seconds
    return None


def _log_usage(usage) -> None:
    if usage is None:
        print("token_usage: (not reported by runtime)")
        return
    print(
        "token_usage: "
        f"in={getattr(usage, 'input_tokens', 0)} "
        f"out={getattr(usage, 'output_tokens', 0)} "
        f"cache_read={getattr(usage, 'cache_read_tokens', 0)} "
        f"cache_write={getattr(usage, 'cache_write_tokens', 0)} "
        f"total={getattr(usage, 'total_tokens', 0)}"
    )


def _consume_run_stream(run, deadline_mono: float, stats: RunLogStats) -> None:
    """Drain agent stream into TeamCity log until complete or deadline."""
    for message in run.messages():
        if time.monotonic() > deadline_mono:
            try:
                run.cancel()
            except Exception:
                pass
            raise TimeoutError("agent stream exceeded AGENT_MAX_WAIT_MINUTES")

        msg_type = getattr(message, "type", None)

        if msg_type == "tool_call":
            name = getattr(message, "name", "?")
            status = getattr(message, "status", "?")
            if status == "running":
                stats.tool_started += 1
                if _is_mcp_tool(name):
                    stats.mcp_tool_started += 1
                print(f"tool_call: {name} (running)")
            elif status == "completed":
                stats.tool_done += 1
                note = " truncated" if getattr(message, "truncated", False) else ""
                print(f"tool_call: {name} (completed{note})")
            elif status == "error":
                stats.tool_error += 1
                print(f"tool_call: {name} (ERROR)", file=sys.stderr)

        elif msg_type == "assistant":
            text = getattr(message, "text", "") or ""
            stats.assistant_chars += len(text)

        elif msg_type == "usage":
            stats.usage_events += 1
            turn_usage = getattr(message, "usage", None)
            if turn_usage is not None:
                _log_usage(turn_usage)

        elif msg_type == "error":
            text = getattr(message, "message", None) or getattr(message, "text", None) or message
            print(f"agent_error_event: {text}", file=sys.stderr)


def _report_required_files(paths: list[Path], step_started_unix: float) -> tuple[int, bool]:
    """Log artefact stats; return (exit_code, any_stale)."""
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print("ERROR: required output file(s) missing:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        return 3, False

    any_stale = False
    started_label = _iso_utc(step_started_unix)
    for path in paths:
        st = path.stat()
        mtime_label = _iso_utc(st.st_mtime)
        stale = st.st_mtime < (step_started_unix - 2)
        if stale:
            any_stale = True
        stale_flag = " STALE" if stale else ""
        print(
            f"REQUIRE OK: {path} ({st.st_size} bytes, mtime={mtime_label}, "
            f"step_started={started_label}){stale_flag}"
        )
        if stale:
            print(
                f"WARN: {path} mtime predates this agent step — likely reused checkout artefact",
                file=sys.stderr,
            )
    return 0, any_stale


def _mcp_command() -> tuple[str, list[str]]:
    """Resolve MCP launcher from bootstrap (absolute uvx path on dxAgent)."""
    uvx_bin = (os.environ.get("UVX_BIN") or "uvx").strip()
    uvx_mode = (os.environ.get("UVX_MODE") or "uvx").strip()
    pkg_args = ["--with", "fakeredis<2.35", "mcp-atlassian-with-bitbucket"]
    if uvx_mode == "uv-x":
        return uvx_bin, ["x", *pkg_args]
    return uvx_bin, pkg_args


def _build_options(repo_root: Path):
    from cursor_sdk import AgentOptions, LocalAgentOptions, StdioMcpServerConfig

    mcp_cmd, mcp_args = _mcp_command()
    return AgentOptions(
        api_key=os.environ["CURSOR_API_KEY"],
        model=os.environ.get("AGENT_MODEL", "composer-2.5"),
        local=LocalAgentOptions(
            cwd=str(repo_root),
            setting_sources=["project"],
        ),
        mcp_servers={
            "user-mcp-atlassian": StdioMcpServerConfig(
                command=mcp_cmd,
                args=mcp_args,
                env=_mcp_env(),
            ),
        },
    ), mcp_cmd, mcp_args


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
        options, mcp_cmd, mcp_args = _build_options(repo_root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    from cursor_sdk import Agent, CursorAgentError

    print(f"runner: epic={epic} repo_root={repo_root}")
    print(f"runner: model={options.model} timeout={max_wait_min}min setting_sources=project")
    print(f"runner: mcp_cmd={mcp_cmd} mcp_args={' '.join(mcp_args)}")
    for path in required:
        print(f"runner: require={path}")

    print(f"Starting agent (timeout {max_wait_min} min)…")
    print(f"Prompt: {args.prompt[:200]}{'…' if len(args.prompt) > 200 else ''}")

    step_started_unix = time.time()
    started_mono = time.monotonic()
    deadline_mono = started_mono + max_wait_sec
    stats = RunLogStats()

    try:
        create_started = time.monotonic()
        agent = Agent.create(options)
        print(f"agent_create: {time.monotonic() - create_started:.1f}s")

        run = agent.send(args.prompt)
        run_id = getattr(run, "run_id", None) or getattr(run, "id", None)
        agent_id = getattr(run, "agent_id", None) or getattr(agent, "id", None)
        if run_id:
            print(f"run_id: {run_id}")
        if agent_id:
            print(f"agent_id: {agent_id}")

        _consume_run_stream(run, deadline_mono, stats)
        result = run.wait()
    except TimeoutError:
        print(f"ERROR: agent wait exceeded {max_wait_min} minutes", file=sys.stderr)
        return 2
    except CursorAgentError as exc:
        print(f"ERROR: CursorAgentError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: agent failed: {exc}", file=sys.stderr)
        return 1

    elapsed = time.monotonic() - started_mono
    status = getattr(result, "status", None) or getattr(run, "status", None)
    duration_ms = getattr(result, "duration_ms", None) or getattr(run, "duration_ms", None)

    print(f"status: {status}")
    print(f"wall_seconds: {elapsed:.1f}")
    if duration_ms is not None:
        print(f"runtime_duration_ms: {duration_ms}")

    usage = getattr(run, "usage", None) or getattr(result, "usage", None)
    _log_usage(usage)

    print(
        "run_stats: "
        f"tool_started={stats.tool_started} tool_done={stats.tool_done} "
        f"tool_error={stats.tool_error} mcp_tool_started={stats.mcp_tool_started} "
        f"assistant_chars={stats.assistant_chars}"
    )

    if stats.mcp_tool_started == 0:
        print("WARN: no MCP/Atlassian tool calls observed — playbook may not have used user-mcp-atlassian", file=sys.stderr)

    min_hint = _min_duration_hint(args.prompt)
    if min_hint is not None and elapsed < min_hint:
        print(
            f"WARN: agent finished in {elapsed:.0f}s (< {min_hint}s typical minimum for this step)",
            file=sys.stderr,
        )

    try:
        final_text = run.text()
    except Exception:
        final_text = getattr(result, "text", None) or ""
    if final_text:
        preview = " ".join(final_text.split())[:500]
        print(f"assistant_final_preview: {preview}{'…' if len(preview) >= 500 else ''}")

    if status != "finished":
        return 2

    exit_code, any_stale = _report_required_files(required, step_started_unix)
    if any_stale:
        print("WARN: one or more required files predate this step — verify step output may still pass on stale data", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
