# Cursor — how-to

## Cursor MCP (org-wide)

For **general** Cursor MCP setup—**tokens**, **global MCP layout**, and org-wide configuration—use Confluence: **[AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor)** (QAPORTAL). This HOW-TO only documents **Corner-specific** steps (pipelines, CTQA tunnel, **postgres-ctqa** connection string).

## Pipelines (human-run playbooks)

All playbooks live under `.cursor/pipelines/`. Open the file and follow it, or start chat with the trigger phrase.

- **`.cursor/pipelines/epic-prep.md`** — Trigger: prefix **`EPIC-PREP:`** then the Jira Epic key (example: `EPIC-PREP: CRT-1234`; optional **`repo=`** for Bitbucket prep — Stash `PROJECT_KEY/repo_slug` e.g. **`BRO/xt`**, see [docs/project.json](../docs/project.json) `bitbucket`). Output: `epics/<KEY>/<KEY>-ref.json`; scratch only in `epics/<KEY>/temp/`, then delete that folder.
- **`.cursor/pipelines/coverage.md`** — Trigger: **`COVERAGE:`** + Epic key (example: `COVERAGE: CRT-639 repo=myworkspace/dxtrade-xt focus=FX_SPOT_WeightedAvg_metrics`). Optional **`focus=...`** narrows `epic_verification_focus` when Jira is ambiguous. Requires **`epics/<KEY>/<KEY>-ref.json`** from epic-prep first. Output: `epics/<KEY>/<KEY>-coverage.json` and `<KEY>-coverage.md` (Jira Smart Checklist paste). Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/analysis.md`** — Trigger: **`ANALYSE:`** + Epic key (example: `ANALYSE: CRT-639 include_closed=yes`). Loads **`-ref.json`** and **`-coverage.json`** from disk when present. Output: **`epics/<KEY>/<KEY>-analysis.json`** and **`<KEY>-analysis.md`**; may append **Known issue** **`>`** lines to coverage when reconciliation is `in_scope_relevant`. Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/test-prep.md`** — Trigger: **`TEST-PREP:`** + Epic key (optional **`map_only=yes`**). Requires **`epics/<KEY>/<KEY>-coverage.json`**. Output: **`epics/<KEY>/<KEY>-tests.json`** and **`<KEY>-tests.md`**. Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/test-exec.md`** — Trigger: **`TEST-EXEC:`** + Epic key (optional **`base_url=…`**, **`skip_postgres=yes`**, **`include_blocked=yes`**, **`max_bundles=N`**). **Optional**, environment-dependent; requires **`epics/<KEY>/<KEY>-tests.json`**. May emit **`epics/<KEY>/tests/*.spec.ts`** and **`<KEY>-test-exec.json`**. Scratch only in **`epics/<KEY>/temp/`** (`test-exec-*`), then delete that folder.
- **`.cursor/pipelines/public-scrub.md`** — Trigger: **`PUBLIC-SCRUB:`** (optional **`version=X.Y.Z`**, optional **`source=develop`** default or **`source=main`**). **Public export / sanitize**: run only while **`git checkout release`** — merges upstream into **`release`**, applies tiers A–D, writes **`docs/public-export-manifest.json`**, optional **`.agents/`** layer, V1/V2 checks; **do not** scrub or commit on **`main`** or **`develop`**. Example manifest on internal branches: [docs/public-export-manifest.example.json](../docs/public-export-manifest.example.json). Scratch only in **`automation/temp/public-scrub/`**, then delete before commit. See [README.md](../README.md) **`release`** branch row.
- **`.cursor/pipelines/sync.md`** — Trigger: **`SYNC:`** (optional **`scope=full`**, or **`pipelines`** / **`prompts`** / **`templates`** / **`tools`** / **`mcp`**). **Harness reconciliation** on **`develop`** or **`main`** only — keeps router, [docs/harness-map.json](../docs/harness-map.json), **`.cursor/mcp/`** templates, **`.cursor/rules/`** inventory, [AGENTS.md](../AGENTS.md), [README.md](../README.md), HOW-TO, [qa-artifacts.mdc](rules/qa-artifacts.mdc), prompts, templates, and tool pointers aligned per [harness-maintenance.mdc](rules/harness-maintenance.mdc). **Do not** run on **`release`** (use **`PUBLIC-SCRUB:`** there). Scratch only in **`automation/temp/sync/`**, then delete when done.

**Jira Smart Checklist markdown** (`-` / `>` / `!`, trace tags, scope rules) is defined in **coverage.md** under *Smart Checklist markdown (normative)*.

Full trigger list and temp rules: [`.cursor/rules/pipeline-router.mdc`](rules/pipeline-router.mdc).

## Keywords → pipelines

These are the **chat triggers** for pipelines (not the harness-map T1 packages):

- `EPIC-PREP:` → **epic-prep** → `.cursor/pipelines/epic-prep.md`
- `COVERAGE:` → **coverage** → `.cursor/pipelines/coverage.md`
- `ANALYSE:` → **analysis** → `.cursor/pipelines/analysis.md`
- `TEST-PREP:` → **test-prep** → `.cursor/pipelines/test-prep.md`
- `TEST-EXEC:` → **test-exec** → `.cursor/pipelines/test-exec.md`
- `PUBLIC-SCRUB:` → **public-scrub** → `.cursor/pipelines/public-scrub.md` (**`release`** branch only)
- `SYNC:` → **sync** → `.cursor/pipelines/sync.md` (**`develop`** / **`main`** only)

## `automation/` folder

Manual **Python tests and tools** you write. Docs for tools (e.g. Yogi) live in `automation/docs/`; runnable helpers in `automation/tools/`. **Pipelines are not under `automation/`** — they are in `.cursor/pipelines/`.

## `.cursor/rules/` (always-on agent instructions)

- `harness-context.mdc` — Bounded reads, handoff, harness tiers.
- `mcp-atlassian-search.mdc` — Jira/Confluence via MCP only.
- `qa-artifacts.mdc` — QA refs, epics layout, automation docs path.
- `harness-maintenance.mdc` — Keep AGENTS, README, harness-map, rules/prompts in sync when docs change.
- `pipeline-router.mdc` — Maps triggers to pipeline files; temp cleanup for **epic-prep**, **coverage**, **analysis**, **test-prep**, and **test-exec** under `epics/<KEY>/temp/`; **public-scrub** uses **`automation/temp/public-scrub/`** then delete (commits only on **`release`**); **sync** uses **`automation/temp/sync/`** then delete (**develop** / **`main`** only).

## MCP — PostgreSQL (CTQA, optional)

Org-wide MCP and tokens: **[AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor)**. Configure **`postgres-ctqa`** in **Cursor’s global** MCP file so the repo stays free of DB credentials.

**Global file paths**

- **Windows:** `%USERPROFILE%\.cursor\mcp.json`
- **macOS / Linux:** `~/.cursor/mcp.json`

**Terminal checklist (order matters)**

1. **Open a terminal at the repo root** and start the **SSH tunnel** (leave this window open). **PuTTY `plink` is the default on Windows** (avoids common OpenSSH “Corrupted MAC” issues against the same host):  
   `python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com`  
   Enter **AD** password when prompted. `-n` / `--dry-run` prints the exact command; `--backend ssh` forces OpenSSH. Default forward is **local `15432` → remote `127.0.0.1:5432`**; use `--remote-db-host` if your environment needs the DB hostname instead of loopback. Full detail: **[automation/tools/tunnel/README.md](../automation/tools/tunnel/README.md)**.
2. **Open a second terminal** (tunnel still running). Set **`CTQA_PG_PASSWORD`**, then verify DB connectivity:  
   `python automation/tools/tunnel/ctqa_pg.py --probe-only`
3. **Merge the server entry into global `mcp.json`**: use the repo template **[mcp/postgres-ctqa.mcp.json](mcp/postgres-ctqa.mcp.json)** (placeholders only)—copy the **`postgres-ctqa`** object under **`mcpServers`**. It uses **`@sarmadparvez/postgresql-mcp`** (maintained alternative to deprecated `@modelcontextprotocol/server-postgres`). The URL includes **`?mode=readonly`** so write tools (`execute`, `transaction`) are disabled at the MCP layer; still use a **database role** limited to `SELECT` when possible. Replace **`USER:PASSWORD`** with real credentials (**URL-encode** special characters). **Port** in the URL must match your local forward (default **15432**).
4. **SSL** — Use **`sslmode=disable`** for `127.0.0.1` through SSH (encrypted in the tunnel; avoids Node/pg self-signed cert errors with MCP). Do not disable SSL for direct internet DB connections.
5. **Reload MCP** — Restart Cursor or refresh MCP servers (**Cursor Settings → MCP**), after any org-wide MCP steps from Confluence. Check **MCP Logs** if the server fails to start (`npx` must be on PATH for the Cursor process, same as Playwright MCP).

**Project `.cursor/mcp.json`** is gitignored and is **not** part of the repo (avoid duplicating **`postgres-ctqa`** here if it is already in **global** `mcp.json`). Committed snippets live only under **`.cursor/mcp/*.mcp.json`** — merge those into **global** `mcp.json` unless you deliberately use a project-only server list.

## `.cursor/prompts/` (paste starters)

- `codebase-context.md` — Scoped codebase exploration.
- `combined-qa-task.md` — Full QA workflow + optional epic ref / EPIC-PREP / COVERAGE.
- `confluence-spec-work.md` — Confluence-first spec work.
- `jira-ticket-work.md` — Jira ticket work.
- `epic-prep.md` — Shortcut to EPIC-PREP + epic-prep playbook.

## Context map (for the agent, not pipeline triggers)

`AGENTS.md`, `qa-handoff.md`, and `docs/harness-map.json` tell the agent **which repo files to read** by topic (T0/T1/T2). That is separate from pipeline keywords.
