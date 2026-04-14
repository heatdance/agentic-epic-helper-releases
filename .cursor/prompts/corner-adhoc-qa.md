# Prompt scaffold: ad-hoc Corner Q&A (tickets, incidents, metrics)

Copy into chat for **unstructured** questions where pipelines (`EPIC-PREP:`, `COVERAGE:`, …) are not in use. **Jira/Confluence/Bitbucket**: **user-mcp-atlassian** only (read tool schemas before calling).

## Inputs (fill in)

- **Issue key(s)** (if any): <!-- e.g. CRTQA-1234, XT-5678 -->
- **Environment** (if known): <!-- e.g. CT QA, CT UAT -->
- **Goal** (one sentence): <!-- what you need decided or explained -->

## Instructions for the agent

1. [docs/harness-map.json](../../docs/harness-map.json): **T0** (`qa-handoff.md`, `AGENTS.md`), then T1 packages that match; apply **`rules`** there (fetch Jira if a Corner-family key appears; add [docs/corner-platform-map.json](../../docs/corner-platform-map.json) when repro/env/repo/Jira-project scope matters).
2. If **Issue key(s)** are filled: **fetch each issue with MCP** before substantive analysis; do not invent fields.
3. On **follow-up** messages from the user: **restate the Goal above in one line**, then answer—avoid hyperfocus on the latest sentence only.
4. **Summarize**; cite ticket or Confluence only in short snippets.

## Forbidden

- Answering ticket-specific questions from memory without MCP fetch.
- Pasting large Confluence bodies or unbounded search dumps.
