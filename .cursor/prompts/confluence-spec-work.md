# Prompt scaffold: Confluence spec / doc (Corner Trader)

Copy or adapt this into chat. **All Confluence search and page retrieval must go through user-mcp-atlassian** (read tool schemas before calling). Do not invent page content.

## Inputs (fill in)

- **Page title, URL, or ID** (as your MCP tools require): <!-- -->
- **Goal**: <!-- e.g. summarize decisions, list open questions, map to test scope -->

## Instructions for the agent

1. Follow [docs/harness-map.json](../../docs/harness-map.json): **T0**; read [docs/qa-project.json](../../docs/qa-project.json) when the page is under **QAPORTAL Corner** (page **497097273** subtree)—scope MCP search there, not the whole QA portal unless the user widens scope.
2. Read [qa-handoff.md](../../qa-handoff.md) if continuing prior work.
3. Use **user-mcp-atlassian** to **search** or **fetch** the relevant page(s).
4. Deliver:
   - **Decision / requirement summary** (bullets; functional/process only—omit people rosters from Confluence).
   - **Open questions** or contradictions vs other sources.
   - **Suggested traceability**: how this ties to Jira issues or test artifacts (reference [epics/templates/tests-ref.json](../../epics/templates/tests-ref.json) **format_norms** or Epic coverage / Smart Checklist via [`.cursor/pipelines/coverage.md`](../pipelines/coverage.md) when producing outputs).
5. Keep excerpts **short**; prefer synthesis over pasting full page HTML or markdown walls. Do **not** paste credentials or secrets into chat or repo files.

## Forbidden

- Guessing Confluence text or using generic product knowledge instead of MCP-fetched content.
