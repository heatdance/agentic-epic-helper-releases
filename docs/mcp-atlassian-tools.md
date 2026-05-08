# Atlassian MCP in Cursor (`user-mcp-atlassian`)

Functional reference for **which tools exist**, **how safe they are**, and **which Bitbucket/Stash calls are reliable** on internal infrastructure. **No secrets** in this file.

## Where the server is implemented

This repository (**cursor.corner**) does **not** contain the MCP server source. Cursor loads **`user-mcp-atlassian`** (server label **`mcp-atlassian`**) from your **MCP configuration** (global and/or project — see org-wide setup in [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) and [HOW-TO.md](../HOW-TO.md)).

**Debugging or changing HTTP behavior** (wrong Stash search URL, auth, new REST routes) is done in the **MCP server’s own codebase or package**, then redeployed/upgraded in Cursor — not by editing QA playbooks alone.

Cursor caches **tool schemas** under the user’s Cursor project data (e.g. `.../mcps/user-mcp-atlassian/tools/*.json`). Those JSON files are the **argument contract** (`project_key`, `repo_slug`, `workspace`, etc.).

## Tool inventory (read-only surface)

From the descriptor set exposed to this workspace, **every** tool is **read-only** (no Jira transitions, no PR create/merge, no repo writes):

| Domain | Tools |
|--------|--------|
| **Jira** | `jira_get_issue`, `jira_search` |
| **Confluence** | `confluence_get_page`, `confluence_search` |
| **Bitbucket / Stash** | `bitbucket_list_repositories`, `bitbucket_browse_directory`, `bitbucket_get_file_content`, `bitbucket_search_code`, `bitbucket_list_commits`, `bitbucket_get_commit`, `bitbucket_list_pull_requests`, `bitbucket_get_pull_request`, `bitbucket_get_pull_request_diff` |

**“Safer” in practice** means: **narrow queries**, **prefer get/browse over global search**, **cap** PR diffs and file sizes, and **never paste tokens** into repo files or prompts that get committed.

## Recommended ladders

### Jira and Confluence

1. Prefer **`jira_get_issue`** / **`confluence_get_page`** when the key or `page_id` is already known.
2. Use **`jira_search`** / **`confluence_search`** only with **tight** JQL/CQL (see [.cursor/rules/mcp-atlassian-search.mdc](../.cursor/rules/mcp-atlassian-search.mdc)).
3. Avoid pulling `*all` fields or huge comment threads unless the task requires it.

### Bitbucket Server (`stash.in.devexperts.com`)

1. **Map** repo tokens **`PROJECT_KEY/repo_slug`** (e.g. `BRO/xt`) to MCP **`project_key`** + **`repo_slug`** separately. Passing `BRO/xt` as a single `repo_slug` without `project_key` fails Server/DC validation.
2. Prefer tools in this order for **grounding**:
   - **`bitbucket_list_repositories`** — confirm project/repo names.
   - **`bitbucket_browse_directory`** — bounded navigation from a known path.
   - **`bitbucket_get_file_content`** — small, targeted file reads (short fragments into artifacts only).
   - **`bitbucket_search_code`** — **optional**; on this host it may return **HTTP 404** for `/rest/api/1.0/search` even when browse succeeds. Treat 404 as **“code search API unavailable”**, not total Stash failure.
3. Commit / PR tools: use only for **evidence**, with explicit **limits** on how many objects and how large diffs are.

Playbooks already encode Stash mapping + **browse fallback** when search 404s: [.cursor/pipelines/epic-prep.md](../.cursor/pipelines/epic-prep.md) step **5b**, [.cursor/pipelines/coverage.md](../.cursor/pipelines/coverage.md) phase **7**.

## If you need “safer” or fewer tools in Cursor

- **Server-side:** maintain a fork or config of `mcp-atlassian` that registers only a subset of tools, or fixes `bitbucket_search_code` to call a **supported** code-search endpoint for your Bitbucket Server version.
- **Client-side:** Cursor MCP support for **per-tool disable** depends on Cursor version and server; if available, disable **`bitbucket_search_code`** and rely on browse/get only (aligns with the ladder above).

## Related repo files

- [docs/project.json](project.json) — `bitbucket.default_repo`, `stash_host`, operational note.
- [docs/corner-platform-map.json](corner-platform-map.json) — Stash ladder, code streams (no credentials).
