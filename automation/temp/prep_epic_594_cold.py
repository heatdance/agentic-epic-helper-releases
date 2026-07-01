"""Scratch: save Jira + MCP Confluence exports for CRT-594 cold EPIC-PREP."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMP = ROOT / "epics" / "CRT-594" / "temp"
AGENT_PAGE = Path(
    r"C:\Users\arodzevich\.cursor\projects\c-Media-Work-cursor-corner\agent-tools\7f187278-5a29-4ef8-ae4b-4fa675babe4c.txt"
)

JIRA = {
    "id": "1856985",
    "key": "CRT-594",
    "summary": "FX_SPOT Pricing (groups and mapping to dxFeed)",
    "url": "https://jira.in.devexperts.com/browse/CRT-594",
    "labels": ["ct_ph5"],
    "status": {"name": "Pending resolution"},
    "issue_type": {"name": "Epic"},
}

# MCP confluence_get_page for 518015112 — metadata.content.value only referenced by emit via MCP_SNIPPETS
PAGE_518 = ROOT / "automation" / "temp" / "mcp-page-518015112.json"


def main() -> int:
    TEMP.mkdir(parents=True, exist_ok=True)
    (TEMP / "jira-issue.json").write_text(json.dumps(JIRA, indent=2), encoding="utf-8")
    if PAGE_518.exists():
        (TEMP / "mcp-page-518015112.json").write_text(
            PAGE_518.read_text(encoding="utf-8"), encoding="utf-8"
        )
    if AGENT_PAGE.exists():
        (TEMP / "mcp-page-345722716.json").write_text(
            AGENT_PAGE.read_text(encoding="utf-8"), encoding="utf-8"
        )
    print("Prepared temp inputs under", TEMP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
