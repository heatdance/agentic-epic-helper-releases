# Prompt scaffold: codebase context (Corner Trader)

Copy or adapt this into chat. **Discovery in code**: use targeted search and small file reads—not whole-repo dumps. **Jira/Confluence**: not covered here; use the Jira or Confluence scaffolds with **user-mcp-atlassian**.

## Inputs (fill in)

- **Area / hypothesis**: <!-- e.g. order entry validation -->
- **Repo or path scope**: <!-- if known -->
- **Max files to inspect deeply**: <!-- e.g. 5–10 -->

## Instructions for the agent

1. Follow [docs/harness-map.json](../../docs/harness-map.json): **T0** always; add **T1** `docs/project.json` if the task touches product, fork, XT, or platform context.
2. Read [qa-handoff.md](../../qa-handoff.md) if this session continues prior QA work.
3. Use **semantic or narrow text search** to locate entry points; if results are huge, **narrow the query** before reading more.
4. For in-repo **`*.json`** inspection (~60+ lines or subset need): **MUST** run **`jq`** per [automation/docs/jq.md](../../automation/docs/jq.md) before bounded Read; summarize stdout in chat.
5. Open only **relevant** files; use **line-bounded** reads for large files.
6. Reply with a **compact summary table**: `file` → `role / finding` (no mega-pastes).
7. List **open questions** and suggested **next files** to read—do not exhaust the context window in one step.

## Out of scope

- Do not invent Jira/Confluence content; use MCP when tickets or specs are needed.
