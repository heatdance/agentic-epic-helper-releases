# Cursor — how-to

## Pipelines (human-run playbooks)

All playbooks live under `.cursor/pipelines/`. Open the file and follow it, or start chat with the trigger phrase.

- **`.cursor/pipelines/epic-prep.md`** — Trigger: prefix **`EPIC-PREP:`** then the Jira Epic key (example: `EPIC-PREP: CRT-1234`; optional **`repo=`** for Bitbucket prep — Stash `PROJECT_KEY/repo_slug` e.g. **`BRO/xt`**, see [docs/project.json](../docs/project.json) `bitbucket`). Output: `epics/<KEY>/<KEY>-ref.json`; scratch only in `epics/<KEY>/temp/`, then delete that folder.
- **`.cursor/pipelines/coverage.md`** — Trigger: **`COVERAGE:`** + Epic key (example: `COVERAGE: CRT-639 repo=myworkspace/dxtrade-xt focus=FX_SPOT_WeightedAvg_metrics`). Optional **`focus=...`** narrows `epic_verification_focus` when Jira is ambiguous. Requires **`epics/<KEY>/<KEY>-ref.json`** from epic-prep first. Output: `epics/<KEY>/<KEY>-coverage.json` and `<KEY>-coverage.md` (Jira Smart Checklist paste). Same **`epics/<KEY>/temp/`** rule: delete when done.
- **`.cursor/pipelines/analysis.md`** — Trigger: **`ANALYSE:`** + Epic key (example: `ANALYSE: CRT-639 include_closed=yes`). Loads **`-ref.json`** and **`-coverage.json`** from disk when present. Output: **`epics/<KEY>/<KEY>-analysis.json`** and **`<KEY>-analysis.md`**; may append **Known issue** **`>`** lines to coverage when reconciliation is `in_scope_relevant`. Same **`epics/<KEY>/temp/`** rule: delete when done.

**Jira Smart Checklist markdown** (`-` / `>` / `!`, trace tags, scope rules) is defined in **coverage.md** under *Smart Checklist markdown (normative)*.

More pipelines: add a row here and a bullet in `.cursor/rules/pipeline-router.mdc`.

## Keywords → pipelines

These are the **chat triggers** for pipelines (not the harness-map T1 packages):

- `EPIC-PREP:` → **epic-prep** → `.cursor/pipelines/epic-prep.md`
- `COVERAGE:` → **coverage** → `.cursor/pipelines/coverage.md`
- `ANALYSE:` → **analysis** → `.cursor/pipelines/analysis.md`

## `automation/` folder

Manual **Python tests and tools** you write. Docs for tools (e.g. Yogi) live in `automation/docs/`; runnable helpers in `automation/tools/`. **Pipelines are not under `automation/`** — they are in `.cursor/pipelines/`.

## `.cursor/rules/` (always-on agent instructions)

- `harness-context.mdc` — Bounded reads, handoff, harness tiers.
- `mcp-atlassian-search.mdc` — Jira/Confluence via MCP only.
- `qa-artifacts.mdc` — QA refs, epics layout, automation docs path.
- `harness-maintenance.mdc` — Keep AGENTS, README, harness-map, rules/prompts in sync when docs change.
- `pipeline-router.mdc` — Maps triggers above to pipeline files; temp cleanup rules for **epic-prep**, **coverage**, and **analysis** under `epics/<KEY>/temp/`.

## MCP — PostgreSQL (CTQA, optional)

Copy **[mcp.json.example](mcp.json.example)** to **`mcp.json`** (gitignored) and edit the connection string. That file registers **`postgres-ctqa`** using **`@sarmadparvez/postgresql-mcp`** (maintained alternative to deprecated `@modelcontextprotocol/server-postgres`). The URL includes **`?mode=readonly`** so write tools (`execute`, `transaction`) are disabled at the MCP layer; still use a **database role** limited to `SELECT` when possible.

1. **SSH tunnel** — From repo root, **PuTTY `plink` is used by default on Windows** (avoids common OpenSSH “Corrupted MAC” issues against the same host).  
   `python automation/tools/tunnel/ctqa_pg.py YOUR_AD_USER@ctqa.prosp.devexperts.com`  
   Leave the terminal open; enter **AD** password when prompted. Second tab: set `CTQA_PG_PASSWORD` and run `python automation/tools/tunnel/ctqa_pg.py --probe-only` to verify DB over the tunnel. Full checklist and zip handoff: **[automation/tools/tunnel/README.md](../automation/tools/tunnel/README.md)**.  
   `-n` / `--dry-run` prints the exact command; `--backend ssh` forces OpenSSH. Default forward is **local `15432` → remote `127.0.0.1:5432`** (as on the SSH server); use `--remote-db-host` if your environment needs the DB hostname instead of loopback.
2. **Edit the connection string** in `mcp.json`: replace **`REPLACE_WITH_PASSWORD`** with the real DB password (URL-encode special characters). Adjust **port** if you change the local forward.
3. **SSL** — Use **`sslmode=disable`** for `127.0.0.1` through SSH (encrypted in the tunnel; avoids Node/pg self-signed cert errors with MCP). Do not disable SSL for direct internet DB connections.
4. **Reload MCP** — Restart Cursor or refresh MCP servers (**Cursor Settings → MCP**). Check **MCP Logs** if the server fails to start (`npx` must be on PATH for the Cursor process, same as Playwright MCP).

To keep secrets out of git, you can instead define **`postgres-ctqa`** only in your **user** `~/.cursor/mcp.json` and delete the entry from the project file.

## `.cursor/prompts/` (paste starters)

- `codebase-context.md` — Scoped codebase exploration.
- `combined-qa-task.md` — Full QA workflow + optional epic ref / EPIC-PREP / COVERAGE.
- `confluence-spec-work.md` — Confluence-first spec work.
- `jira-ticket-work.md` — Jira ticket work.
- `epic-prep.md` — Shortcut to EPIC-PREP + epic-prep playbook.

## Context map (for the agent, not pipeline triggers)

`AGENTS.md`, `qa-handoff.md`, and `docs/harness-map.json` tell the agent **which repo files to read** by topic (T0/T1/T2). That is separate from pipeline keywords.
