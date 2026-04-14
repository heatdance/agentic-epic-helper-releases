# Cursor — how-to

## Cursor MCP (org-wide)

For **general** Cursor MCP setup—**tokens**, **global MCP layout**, and org-wide configuration—use Confluence: **[AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor)** (QAPORTAL). This HOW-TO only documents **Corner-specific** steps (pipelines, CTQA tunnel, **postgres-ctqa** connection string).

## Before Corner QA agent chats (checklist)

1. **user-mcp-atlassian** enabled in Cursor (Jira, Confluence, Bitbucket/Stash tools)—see **AI with Cursor** above if tokens need refresh.
2. Optional per task: **user-mcp-playwright** (TEST-EXEC), **postgres-ctqa** + SSH tunnel (DB checks)—see sections below.
3. Skim [docs/corner-platform-map.json](../docs/corner-platform-map.json) when the task involves **which environment**, **which repo**, or **which Jira project**; agents use it as the structured map (secrets stay on Confluence).

## Prompt Template

Auto mode works better when the **first message** is structured. Copy and fill in:

```
**Issue / keys:** <!-- e.g. CRTQA-1234, CRT-639, XT-5678 — or "none" -->
**Environment:** <!-- e.g. CT QA, CT UAT, CT DEV — or "unknown" -->
**Goal:** <!-- one sentence: what you want decided, verified, or drafted -->
**Constraints:** <!-- optional: timebox, surfaces dxTrade5/WebBroker/Adaptive, no DB, etc. -->
```

**Also:**

- Turn on **user-mcp-atlassian** (Jira / Confluence / Stash) — see [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) if tools fail.
- For **unstructured** Q&A (incidents, metrics, “why does this ticket…”), paste [corner-adhoc-qa.md](prompts/corner-adhoc-qa.md) or keep the four lines above in every follow-up so the agent does not lose the thread.

Epic-sized work: use chat triggers (`EPIC-PREP:`, `COVERAGE:`, …) per **Keywords → pipelines** below instead of a vague question.

## Pipelines (human-run playbooks)

All playbooks live under `.cursor/pipelines/`. Open the file and follow it, or start chat with the trigger phrase.

- **`.cursor/pipelines/epic-prep.md`** — Trigger: prefix **`EPIC-PREP:`** then the Jira Epic key (example: `EPIC-PREP: CRT-1234`; optional **`repo=`** for Bitbucket prep — Stash `PROJECT_KEY/repo_slug` e.g. **`BRO/xt`**, see [docs/project.json](../docs/project.json) `bitbucket`). Output: `epics/<KEY>/<KEY>-ref.json`; scratch only in `epics/<KEY>/temp/`, then delete that folder.
- **`.cursor/pipelines/coverage.md`** — Trigger: **`COVERAGE:`** + Epic key (example: `COVERAGE: CRT-639 repo=myworkspace/dxtrade-xt focus=FX_SPOT_WeightedAvg_metrics`). Optional **`focus=...`** narrows `epic_verification_focus` when Jira is ambiguous. Requires **`epics/<KEY>/<KEY>-ref.json`** from epic-prep first. Output: `epics/<KEY>/<KEY>-coverage.json` and `<KEY>-coverage.md` (Jira Smart Checklist paste). Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/analysis.md`** — Trigger: **`ANALYSE:`** + Epic key (example: `ANALYSE: CRT-639 include_closed=yes`). Loads **`-ref.json`** and **`-coverage.json`** from disk when present. Output: **`epics/<KEY>/<KEY>-analysis.json`** and **`<KEY>-analysis.md`**; may append **Known issue** **`>`** lines to coverage when reconciliation is `in_scope_relevant`. Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/test-prep.md`** — Trigger: **`TEST-PREP:`** + Epic key (optional **`map_only=yes`**). Requires **`epics/<KEY>/<KEY>-coverage.json`**. Output: **`epics/<KEY>/<KEY>-tests.json`** and **`<KEY>-tests.md`**. Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/test-exec.md`** — Trigger: **`TEST-EXEC:`** + Epic key (optional **`base_url=…`**, **`skip_postgres=yes`**, **`include_blocked=yes`**, **`max_bundles=N`**). **Optional**, environment-dependent; requires **`epics/<KEY>/<KEY>-tests.json`**. May emit **`epics/<KEY>/tests/*.spec.ts`** and **`<KEY>-test-exec.json`**. Scratch only in **`epics/<KEY>/temp/`** (`test-exec-*`), then delete that folder.
- **`.cursor/pipelines/public-scrub.md`** — Trigger: **`PUBLIC-SCRUB:`** (optional **`version=X.Y.Z`**, optional **`source=develop`** default or **`source=main`**). **Public export / sanitize**: run only while **`git checkout release`** — merges upstream into **`release`**, applies tiers A–D, writes **`docs/public-export-manifest.json`**, optional **`.agents/`** layer, V1/V2 checks; **do not** scrub or commit on **`main`** or **`develop`**. Example manifest on internal branches: [docs/public-export-manifest.example.json](../docs/public-export-manifest.example.json). Scratch only in **`automation/temp/public-scrub/`**, then delete before commit. See [README.md](../README.md) **`release`** branch row.
- **`.cursor/pipelines/sync.md`** — Trigger: **`SYNC:`** (optional **`scope=full`**, or **`pipelines`** / **`prompts`** / **`templates`** / **`tools`** / **`mcp`**). **Harness reconciliation** on **`develop`** or **`main`** only — keeps router, [docs/harness-map.json](../docs/harness-map.json), **`.cursor/rules/`** inventory, [AGENTS.md](../AGENTS.md), [README.md](../README.md), HOW-TO, [qa-artifacts.mdc](rules/qa-artifacts.mdc), prompts, templates, and tool pointers aligned per [harness-maintenance.mdc](rules/harness-maintenance.mdc). **Do not** run on **`release`** (use **`PUBLIC-SCRUB:`** there). Scratch only in **`automation/temp/sync/`**, then delete when done.

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

Org-wide MCP and tokens: **[AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor)**. Keep **DB credentials out of git**.

**Where to put `postgres-ctqa`**

Add the server **once** — either in **global** Cursor MCP or in **gitignored** [`.cursor/mcp.json`](mcp.json) (same folder as this HOW-TO). Cursor **merges** project and global configs; if both define **`postgres-ctqa`**, the project entry wins. Do not duplicate with conflicting URLs.

**Global file path**

- **Windows:** `%USERPROFILE%\.cursor\mcp.json`
- **macOS / Linux:** `~/.cursor/mcp.json`

**Snippet** (merge the `postgres-ctqa` block under `mcpServers` in whichever file you use; placeholders only):

```json
{
  "mcpServers": {
    "postgres-ctqa": {
      "command": "npx",
      "args": [
        "-y",
        "@sarmadparvez/postgresql-mcp",
        "postgresql://USER:PASSWORD@127.0.0.1:15432/ctqa?mode=readonly&sslmode=disable"
      ]
    }
  }
}
```

Uses **`@sarmadparvez/postgresql-mcp`** (maintained alternative to deprecated `@modelcontextprotocol/server-postgres`). **`?mode=readonly`** disables write tools at the MCP layer; prefer a DB role limited to **`SELECT`**. Replace **`USER:PASSWORD`** (**URL-encode** special characters). **Port** must match the tunnel (default **15432**).

**Terminal checklist (order matters)**

1. **Open a terminal at the repo root** and start the **SSH tunnel** (leave this window open). **PuTTY `plink` is the default on Windows** (avoids common OpenSSH “Corrupted MAC” issues against the same host):  
   `python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com`  
   Enter **AD** password when prompted. `-n` / `--dry-run` prints the exact command; `--backend ssh` forces OpenSSH. Default forward is **local `15432` → remote `127.0.0.1:5432`**; use `--remote-db-host` if your environment needs the DB hostname instead of loopback. Full detail: **[automation/tools/tunnel/README.md](../automation/tools/tunnel/README.md)**.
2. **Open a second terminal** (tunnel still running). Set **`CTQA_PG_PASSWORD`**, then verify DB connectivity:  
   `python automation/tools/tunnel/ctqa_pg.py --probe-only`
3. **Configure MCP** using the snippet above in **global** `mcp.json` and/or **`.cursor/mcp.json`** as you prefer.
4. **SSL** — Use **`sslmode=disable`** for `127.0.0.1` through SSH (encrypted in the tunnel; avoids Node/pg self-signed cert errors with MCP). Do not disable SSL for direct internet DB connections.
5. **Reload MCP** — Restart Cursor or refresh MCP servers (**Cursor Settings → MCP**), after any org-wide MCP steps from Confluence. Check **MCP Logs** if the server fails to start (`npx` must be on PATH for the Cursor process, same as Playwright MCP).

**`.cursor/mcp.json`** is listed in **`.gitignore`** so it is never committed. There is **no** committed `.cursor/mcp/` template folder — copy the snippet from this section when adding the server.

## `.cursor/prompts/` (paste starters)

- `codebase-context.md` — Scoped codebase exploration.
- `combined-qa-task.md` — Full QA workflow + optional epic ref / EPIC-PREP / COVERAGE.
- `corner-adhoc-qa.md` — Ad-hoc Corner Q&A (tickets, incidents, metrics; MCP-first; restate goal on clarifications).
- `confluence-spec-work.md` — Confluence-first spec work.
- `jira-ticket-work.md` — Jira ticket work.
- `epic-prep.md` — Shortcut to EPIC-PREP + epic-prep playbook.

## Context map (for the agent, not pipeline triggers)

`AGENTS.md`, `qa-handoff.md`, and `docs/harness-map.json` tell the agent **which repo files to read** by topic (T0/T1/T2). That is separate from pipeline keywords.
