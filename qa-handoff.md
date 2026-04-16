# QA session handoff — Corner Trader

Read at the start of substantive QA work; **update before ending** (date, focus, next steps). Detail lives in **`epics/<KEY>/`** and **[AGENTS.md](AGENTS.md)** — do not duplicate long pipeline logs here.

## Last updated

- **Date**: 2026-04-16 — Trimmed handoff noise; state snapshot refreshed below.

## Current focus

- **CRT-642** (*Non-trading hours*): [CRT-642-ref.json](epics/CRT-642/CRT-642-ref.json), [CRT-642-coverage.md](epics/CRT-642/CRT-642-coverage.md), [CRT-642-analysis.md](epics/CRT-642/CRT-642-analysis.md). **Next**: `TEST-PREP: CRT-642` (optional `TEST-EXEC:` when env is ready). Open gaps called out in analysis: CRT-1481 pointer; chk-015 DxFeed deferral; Stash `bitbucket_search_code` **404** (use browse fallback per playbooks).
- **CRT-639** (cash settlement / weighted average): ref through test drafts in [epics/CRT-639/](epics/CRT-639/). Optional: re-run **`COVERAGE: CRT-639 repo=…`** if code search works, to fill `implementation_hits`; optional **`TEST-EXEC: CRT-639`**.

Tiered context and MCP scope: **[AGENTS.md](AGENTS.md)** → **[docs/harness-map.json](docs/harness-map.json)**. Hosts and dashboards (no secrets in git): **[docs/corner-platform-map.json](docs/corner-platform-map.json)**.

## Blockers

- **user-mcp-atlassian** must be healthy for live Jira/Confluence; retry or check MCP in Cursor settings.
- **Figma MCP**: re-auth OAuth if design tools fail.

## Next steps

1. **`TEST-PREP: CRT-642`** when regression drafts are the priority.
2. Before **`PUBLIC-SCRUB:`**: ensure branch **`release`** exists from **`main`** per [README.md](README.md) (operator workflow if `release` was removed).
3. If Corner env URLs or Jira links change materially on Confluence, bump **`last_reviewed`** in [docs/corner-platform-map.json](docs/corner-platform-map.json).

## Notes

- Ordered workflow scaffold: [.cursor/prompts/combined-qa-task.md](.cursor/prompts/combined-qa-task.md). Credentials stay on Confluence, not in repo files.
