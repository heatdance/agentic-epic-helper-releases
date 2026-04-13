# Prompt scaffold: Jira ticket work (Corner Trader)

Copy or adapt this into chat. **All Jira discovery and retrieval must go through user-mcp-atlassian** (read tool schemas before calling). Do not fabricate issue fields or comments.

## Inputs (fill in)

- **Issue key(s)**: <!-- e.g. PROJ-1234 -->
- **Goal**: <!-- e.g. extract AC, assess testability, draft cases -->

## Instructions for the agent

1. Follow [docs/harness-map.json](../../docs/harness-map.json): **T0**; include **T1** [docs/qa-project.json](../../docs/qa-project.json) for Corner Jira project hints (CRTQA, CRT, etc.) when relevant.
2. Read [qa-handoff.md](../../qa-handoff.md) if continuing a multi-session task.
3. Use **user-mcp-atlassian** to fetch each issue’s authoritative data (summary, description, acceptance criteria, status, links as available).
4. Produce:
   - **Acceptance criteria** (explicit list; flag gaps or ambiguity).
   - **Risks / test ideas** mapped to criteria.
   - **Questions for the author** if the ticket is incomplete.
5. **Summarize**; quote ticket text only where a short snippet is necessary.

## Forbidden

- Web search or model memory as a substitute for the actual ticket content.
