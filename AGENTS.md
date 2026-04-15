# AGENTS.md — Corner Trader QA workspace

Short map for coding agents. **Do not** treat this file as the full spec; follow links (**progressive disclosure**). Prose here is **functional/process only**—no people rosters (see [docs/project.json](docs/project.json) `content_policy`).

## Project

Devexperts — **Corner Trader**. This repository is a **QA workspace**: templates, harness, automation docs, and session continuity—not necessarily the application source tree. Product vs upstream relationship and Confluence anchors: **[docs/project.json](docs/project.json)** (Corner **CT** space; fork base **DXtrade XT** in **XT** space).

## Where things live

### Canonical JSON

| Area | Path |
|------|------|
| Product / fork context (Confluence-backed) | [docs/project.json](docs/project.json) |
| Corner QA scope, envs, Jira mapping (Confluence-backed) | [docs/qa-project.json](docs/qa-project.json) |
| Environments, code streams (Stash), Jira index, Confluence index (MCP-backed) | [docs/corner-platform-map.json](docs/corner-platform-map.json) |
| Atlassian MCP — tool list, safety ladder, Stash search vs browse | [docs/mcp-atlassian-tools.md](docs/mcp-atlassian-tools.md) |
| Tiered context escalation (keywords → which files to read) | [docs/harness-map.json](docs/harness-map.json) |
| Public export manifest (example; live file on `release` only) | [docs/public-export-manifest.example.json](docs/public-export-manifest.example.json) |

### Deliverables and references

| Area | Path |
|------|------|
| Jira Smart Checklist norms + COVERAGE playbook | [`.cursor/pipelines/coverage.md`](.cursor/pipelines/coverage.md) (*Smart Checklist markdown*) |
| Test case draft format (norms + schema template) | [epics/templates/tests-ref.json](epics/templates/tests-ref.json) (**format_norms**); pipeline [`.cursor/pipelines/test-prep.md`](.cursor/pipelines/test-prep.md) |
| Defect report format reference | [docs/dr-ref](docs/dr-ref) |
| Automation documentation | [automation/docs/](automation/docs/) |

### Pipelines (agent playbooks)

| Area | Path |
|------|------|
| All pipelines + triggers | [`.cursor/pipelines/`](.cursor/pipelines/) — [`epic-prep.md`](.cursor/pipelines/epic-prep.md) (`EPIC-PREP:` optional `repo=`), [`coverage.md`](.cursor/pipelines/coverage.md) (`COVERAGE:` optional `repo=` / `focus=`), [`analysis.md`](.cursor/pipelines/analysis.md) (`ANALYSE:`), [`test-prep.md`](.cursor/pipelines/test-prep.md) (`TEST-PREP:` optional `map_only=yes`), [`test-exec.md`](.cursor/pipelines/test-exec.md) (`TEST-EXEC:` optional `base_url=` / `skip_postgres` / `include_blocked` / `max_bundles`; optional pipeline), [`public-scrub.md`](.cursor/pipelines/public-scrub.md) (`PUBLIC-SCRUB:` optional `version=` / `source=` — **release branch only**; never commit scrub on `main`/`develop`), [`sync.md`](.cursor/pipelines/sync.md) (`SYNC:` optional `scope=` e.g. `full` / `pipelines` / `prompts` / `templates` / `tools` / `mcp` — **develop** / **`main`** only; not for **`release`**) |

### Epics

| Area | Path |
|------|------|
| Epic handoff JSON (one Epic at a time) | [epics/templates/epic-ref.json](epics/templates/epic-ref.json) · `epics/<KEY>/<KEY>-ref.json` · [epics/README.md](epics/README.md); **`client_shell_impact`** (Corner + Adaptive), **`snippet_status`** on requirements, optional **`implementation.hits`** + **`sources.bitbucket_repo`** (EPIC-PREP + Bitbucket MCP: split Stash **`PROJECT_KEY/repo_slug`** for tools; **`bitbucket_search_code`** may 404 — use browse fallback in [epic-prep.md](.cursor/pipelines/epic-prep.md) step **5b**); defaults in [docs/project.json](docs/project.json) `bitbucket` |
| Epic coverage (Smart Checklist draft + audit JSON) | [epics/templates/coverage-ref.json](epics/templates/coverage-ref.json) · `epics/<KEY>/<KEY>-coverage.json` · `epics/<KEY>/<KEY>-coverage.md` · trigger `COVERAGE:` |
| Epic requirement analysis | [epics/templates/analysis-ref.json](epics/templates/analysis-ref.json) · `epics/<KEY>/<KEY>-analysis.json` · `epics/<KEY>/<KEY>-analysis.md` · trigger `ANALYSE:` |
| Epic regression test drafts | [epics/templates/tests-ref.json](epics/templates/tests-ref.json) · `epics/<KEY>/<KEY>-tests.json` · `epics/<KEY>/<KEY>-tests.md` · trigger `TEST-PREP:` |
| Epic optional E2E materialization | [epics/templates/test-exec-ref.json](epics/templates/test-exec-ref.json) · `epics/<KEY>/<KEY>-test-exec.json` · `epics/<KEY>/tests/*.spec.ts` · trigger `TEST-EXEC:` (requires `-tests.json`; environment-dependent) |

### Automation tools

| Area | Path |
|------|------|
| Yogi URL resolve + lightweight snippets | [automation/docs/yogi-url-resolve.md](automation/docs/yogi-url-resolve.md) · [yogi-tool/](automation/tools/yogi-tool/) (`yogi_resolve.py`, `yogi_snippet.py`, `yogi_extract.py`) |
| CTQA Postgres SSH tunnel + probe + zip handoff | [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md) · `python automation/tools/tunnel/ctqa_pg.py USER@host` · `--probe-only` + env `CTQA_PG_PASSWORD` |
| Agent scratch / temp | [automation/temp/](automation/temp/) |

### Cursor

| Area | Path |
|------|------|
| Rules (harness) | [.cursor/rules/](.cursor/rules/) |
| Prompt scaffolds | [.cursor/prompts/](.cursor/prompts/) (e.g. [corner-adhoc-qa.md](.cursor/prompts/corner-adhoc-qa.md) for unstructured ticket/incident questions) |
| Humans: Cursor + MCP + tunnel how-to | [.cursor/HOW-TO.md](.cursor/HOW-TO.md) |
| CTQA Postgres MCP | [.cursor/HOW-TO.md](.cursor/HOW-TO.md) (*MCP — PostgreSQL*) — add **`postgres-ctqa`** to **gitignored** [`.cursor/mcp.json`](.cursor/mcp.json) and/or **global** `~/.cursor/mcp.json` (Windows: **`%USERPROFILE%\.cursor\mcp.json`**) using the JSON snippet there |

## Context escalation

1. Follow **[docs/harness-map.json](docs/harness-map.json)**: **T0** (`qa-handoff.md`, this file), then T1 `match_any_package` keywords; prefer the clearest single package, and follow that file’s **`rules`** (Jira-key MCP fetch, extra [docs/corner-platform-map.json](docs/corner-platform-map.json) when repro/env/repo scope applies)—do not open every doc by default.
2. **Corner QA on Confluence** is scoped to **QAPORTAL** page **497097273** (“Corner”) **and descendants** unless the user widens scope—see [docs/qa-project.json](docs/qa-project.json).
3. **Fork / platform** context: [docs/project.json](docs/project.json) → **CT** and **XT** Confluence spaces via MCP when needed.
4. **Hosts, repos, Jira projects** (which env, which Stash repo): [docs/corner-platform-map.json](docs/corner-platform-map.json) — credentials stay on Confluence only.

## How to start a session

1. Read **[qa-handoff.md](qa-handoff.md)** for current focus, blockers, and next steps.
2. Open only the **task-specific** docs or code paths you need—avoid loading the whole tree into context.
3. For substantive work, **update `qa-handoff.md`** before closing the session.

## MCP

### Jira and Confluence

All **discovery and retrieval** for Jira issues and Confluence pages (search, fetch, issue fields) must use **user-mcp-atlassian**. Read each tool’s schema before calling. Do not invent ticket or page content. **Do not** copy secrets from Atlassian into repo files.

### Figma (optional)

When tasks include **Figma file/frame/layer** URLs, use the **workspace-configured Figma MCP** if it is enabled in Cursor. Workflow: **[automation/docs/figma-mcp.md](automation/docs/figma-mcp.md)**. Do not store OAuth tokens or secrets in the repo.

### PostgreSQL / CTQA (optional)

1. **SSH tunnel** to forward a local port to Postgres (PuTTY `plink` default on Windows): see **[.cursor/HOW-TO.md](.cursor/HOW-TO.md)** and **[automation/tools/tunnel/README.md](automation/tools/tunnel/README.md)**.
2. **Cursor `mcp.json`** — add **`postgres-ctqa`** in **gitignored** `.cursor/mcp.json` and/or **global** `~/.cursor/mcp.json` (Windows: **`%USERPROFILE%\.cursor\mcp.json`**) per the snippet in [.cursor/HOW-TO.md](.cursor/HOW-TO.md). Cursor merges project and global; do not define the same server twice with conflicting URLs. Uses `@sarmadparvez/postgresql-mcp` with **`?mode=readonly`**; use **`sslmode=disable`** on `127.0.0.1` through SSH.
3. **Do not** commit real passwords; credentials live only in ignored `.cursor/mcp.json` and/or global MCP.

When the tunnel is up and MCP is enabled, the agent may use **`query`**, **`schema`**, and **`list_tables`** against database **ctqa**. Optional pipeline **`TEST-EXEC:`** may use the same server for **readonly** SQL checks when bundles require DB verification.

## Codebase exploration

Prefer **narrow** search and **bounded** file reads; summarize findings instead of pasting large files. See [.cursor/prompts/codebase-context.md](.cursor/prompts/codebase-context.md) for a reusable scaffold.

## Rules in this repo

Persistent agent behavior is under [.cursor/rules/](.cursor/rules/): `harness-context`, `mcp-atlassian-search`, `qa-artifacts`, `harness-maintenance`, `pipeline-router`. Keep **AGENTS.md** short; extend detail in linked JSON and Confluence via MCP.
