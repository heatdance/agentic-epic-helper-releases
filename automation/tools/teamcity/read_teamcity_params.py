#!/usr/bin/env python3
"""Emit shell export lines for TeamCity params missing from the step environment."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Password + text params used across Pipeline steps (config or env.* in properties file).
KEYS = (
    "JIRA_API_TOKEN",
    "CURSOR_API_KEY",
    "EPIC_KEY",
    "QA_TASK_KEY",
    "COMMENT_ID",
    "CRTQA_SSH_PRIVATE_KEY_B64",
    "CRTQA_SUDO_PASSWORD",
    "CRTQA_SSH_USER",
    "CRTQA_CONSOLE_TRANSPORT",
    "CRTQA_SSH_HOST",
    "CRTQA_SUDO_UNIX_USER",
    "AGENT_MAX_WAIT_MINUTES",
    "JIRA_BASE_URL",
    "ATLASSIAN_MCP_JIRA_URL",
    "ATLASSIAN_MCP_CONFLUENCE_URL",
    "ATLASSIAN_MCP_BITBUCKET_URL",
    "TEAMCITY_BUILD_URL",
)

# TeamCity built-in property names mapped to export keys when the target env var is empty.
BUILD_URL_ALIASES = ("teamcity.build.url",)


def _props_paths() -> list[Path]:
    seen: set[str] = set()
    paths: list[Path] = []
    for raw in (
        os.environ.get("TEAMCITY_BUILD_PROPERTIES_FILE"),
        os.environ.get("TEAMCITY_BUILD_PARAMETERS_FILE"),
        os.environ.get("BUILD_PROPERTIES_FILE"),
    ):
        if not raw or raw in seen:
            continue
        seen.add(raw)
        paths.append(Path(raw))
    return paths


def _parse_properties_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("env."):
            key = key[4:]
        out[key] = value
    return out


def _merged_properties() -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in _props_paths():
        if path.is_file():
            merged.update(_parse_properties_file(path))
    return merged


def resolve_teamcity_build_url(*, props: dict[str, str] | None = None) -> str:
    """Return build URL from env or TeamCity properties (teamcity.build.url alias)."""
    from_env = (os.environ.get("TEAMCITY_BUILD_URL") or "").strip()
    if from_env:
        return from_env
    merged = props if props is not None else _merged_properties()
    direct = (merged.get("TEAMCITY_BUILD_URL") or "").strip()
    if direct:
        return direct
    for alias in BUILD_URL_ALIASES:
        value = (merged.get(alias) or "").strip()
        if value:
            return value
    return ""


def _exports_from_properties(merged: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in KEYS:
        value = (merged.get(key) or "").strip()
        if value:
            out[key] = value
    if not out.get("TEAMCITY_BUILD_URL"):
        build_url = resolve_teamcity_build_url(props=merged)
        if build_url:
            out["TEAMCITY_BUILD_URL"] = build_url
    return out


def _shell_export(key: str, value: str) -> str:
    # Single-quoted with escaped single quotes — safe for passwords/special chars.
    escaped = value.replace("'", "'\"'\"'")
    return f"export {key}='{escaped}'"


def main() -> int:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    merged = _merged_properties()
    exports = _exports_from_properties(merged)

    lines: list[str] = []
    for key in KEYS:
        if os.environ.get(key, "").strip():
            continue
        if key in exports:
            lines.append(_shell_export(key, exports[key]))

    if out_path is not None:
        out_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    else:
        sys.stdout.write("\n".join(lines) + ("\n" if lines else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
