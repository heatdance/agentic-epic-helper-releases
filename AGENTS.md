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
| **dxCore console** agent map (truth tiers + forks + Confluence trust; T1 **`dxcore_console`**) | [docs/dxcore-console-harness.json](docs/dxcore-console-harness.json) |
| **dxTrade5 web UI** agent map (concept → IA → locations; T1 **`dxtrade5_harness`**) | [docs/dxtrade5-harness/](docs/dxtrade5-harness/) — [README](docs/dxtrade5-harness/README.md), [dxtrade5-harness.json](docs/dxtrade5-harness/dxtrade5-harness.json), [concept-map.json](docs/dxtrade5-harness/concept-map.json) |
| **WebBroker dealer web UI** agent map (concept → IA → locations; T1 **`webbroker_harness`**) | [docs/webbroker-harness/](docs/webbroker-harness/) — [README](docs/webbroker-harness/README.md), [webbroker-harness.json](docs/webbroker-harness/webbroker-harness.json), [concept-map.json](docs/webbroker-harness/concept-map.json) |
| **Harness doctrine** (generation vs benchmark, coverage vs E2E, reference ownership) | [docs/harness-principles.md](docs/harness-principles.md) |
| Public export manifest (example; live file on `public-*` only) | [docs/public-export-manifest.example.json](docs/public-export-manifest.example.json) |

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
| All pipelines + triggers | [`.cursor/pipelines/`](.cursor/pipelines/) — [`epic-prep.md`](.cursor/pipelines/epic-prep.md) (`EPIC-PREP:`), [`coverage.md`](.cursor/pipelines/coverage.md) (`COVERAGE:`), [`analysis.md`](.cursor/pipelines/analysis.md) (`ANALYSE:`), [`test-discover.md`](.cursor/pipelines/test-discover.md) (`TEST-DISCOVER:`), [`test-precon.md`](.cursor/pipelines/test-precon.md) (`TEST-PRECON:`), [`test-prep.md`](.cursor/pipelines/test-prep.md) (`TEST-PREP:`), [`close.md`](.cursor/pipelines/close.md) (`CLOSE:`), [`clean.md`](.cursor/pipelines/clean.md) (`CLEAN:` — **`personal` only**; align + publish team/public; [clean_verify.py](automation/tools/clean_verify.py)) |

### Epics

| Area | Path |
|------|------|
| Epic handoff JSON (schema v4) | [epics/templates/epic-ref.json](epics/templates/epic-ref.json) · **`obligations_proposed[]`** · [docs/epic-obligation-kinds.json](docs/epic-obligation-kinds.json) · [epic-prep-verify.md](automation/docs/epic-prep-verify.md) |
| Epic coverage (schema v2) | [epics/templates/coverage-ref.json](epics/templates/coverage-ref.json) · **`obligations_coverage`** · [coverage-obligation-contract.json](docs/coverage-obligation-contract.json) · [coverage-verify.md](automation/docs/coverage-verify.md) |
| Epic requirement analysis (v2) | [analysis-ref.json](epics/templates/analysis-ref.json) · [analysis-gap-contract.json](docs/analysis-gap-contract.json) · [analysis-verify.md](automation/docs/analysis-verify.md) · `exploration_suppressed[]` |
| Epic optional discovery (obligation closure map) | [epics/templates/discover-ref.json](epics/templates/discover-ref.json) v3 · `epics/<KEY>/<KEY>-discover.json` · `TEST-DISCOVER:` · **`fixture_needs`** (CRTQA index opt-in) · verifier [automation/tools/discover_verify.py](automation/tools/discover_verify.py) |
| Epic optional precondition authoring (v4) | [precon-ref.json](epics/templates/precon-ref.json) · [exploration-depth-ladder.json](docs/exploration-depth-ladder.json) · [precon_verify.py](automation/tools/precon_verify.py) (`--discover`, `--md`) |
| Epic regression test drafts (v3) | [epics/templates/tests-ref.json](epics/templates/tests-ref.json) schema v4 · [test-prep-draft-profiles.json](docs/test-prep-draft-profiles.json) · [test-prep-tbd-contract.json](docs/test-prep-tbd-contract.json) · `-tests.json` / `-tests.md` · `TEST-PREP:` |
| Epic close (integrity + archive) | [epics/templates/close-ref.json](epics/templates/close-ref.json) · `epics/<KEY>/context/<KEY>-close.json` · four root `.md` · trigger `CLOSE:` (documentation-only; after full artifact set) |

### Automation tools

| Area | Path |
|------|------|
| Yogi URL resolve + lightweight snippets | [automation/docs/yogi-url-resolve.md](automation/docs/yogi-url-resolve.md) · [yogi-tool/](automation/tools/yogi-tool/) (`yogi_resolve.py`, `yogi_snippet.py`, `yogi_extract.py`) |
| CTQA Postgres SSH tunnel + probe + zip handoff | [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md) · `python automation/tools/tunnel/ctqa_pg.py USER@host` · `--probe-only` + env `CTQA_PG_PASSWORD` |
| CTQA environment probe · slash **`/crtqa-env`** | [automation/docs/crtqa-env.md](automation/docs/crtqa-env.md) · `python automation/tools/crtqa_env_probe.py` (optional `--coverage epics/<KEY>/<KEY>-coverage.json`) |
| CTQA **`dx run console`** (SSH/plink) · slash **`/crtqa-console`** (`start` \| `status` \| `probe` \| `stop`) | [automation/tools/crtqa-console/README.md](automation/tools/crtqa-console/README.md) · `Start-` / `Get-CrtqaConsoleStatus` / `Invoke -Probe` / `Stop-`; interactive: `Enter-CrtqaConsole.ps1` |
| **jq** JSON projection (system PATH; agent inspect) | [automation/docs/jq.md](automation/docs/jq.md) · `winget install --id jqlang.jq -e` (Windows); rule [`.cursor/rules/jq-json.mdc`](.cursor/rules/jq-json.mdc) |
| Agent scratch / temp | [automation/temp/](automation/temp/) |
| **CRTQA TCD stats (v4)** | [stats/crtqa-stats/README.md](stats/crtqa-stats/README.md) · `/crtqa-stats` [crtqa-stats.md](.cursor/commands/crtqa-stats.md) · rollup [crtqa_stats_rollup.py](automation/tools/crtqa_stats_rollup.py) · [crtqa-stats.md (tool)](automation/docs/crtqa-stats.md) — corpus vs comparison; draft `customfield_11250`; `latest.md` + gitignored `state/` |

### Cursor

| Area | Path |
|------|------|
| Rules (harness) | [.cursor/rules/](.cursor/rules/) |
| Prompt scaffolds | [.cursor/prompts/](.cursor/prompts/) (e.g. [corner-adhoc-qa.md](.cursor/prompts/corner-adhoc-qa.md) for unstructured ticket/incident questions) |
| Custom commands (**`/crtqa-env`**, **`/crtqa-console`**, **`/crtqa-stats`**, **`/crtqa-benchmark`**, **`/clean`**) | [.cursor/commands/](.cursor/commands/) — env [crtqa-env.md](.cursor/commands/crtqa-env.md); console [crtqa-console.md](.cursor/commands/crtqa-console.md); stats [crtqa-stats.md](.cursor/commands/crtqa-stats.md); benchmark [crtqa-benchmark.md](.cursor/commands/crtqa-benchmark.md); publish [clean.md](.cursor/commands/clean.md) |
| EPIC-PREP verifier | [epic_prep_verify.py](automation/tools/epic_prep_verify.py) · [automation/docs/epic-prep-verify.md](automation/docs/epic-prep-verify.md) |
| COVERAGE verifier | [coverage_verify.py](automation/tools/coverage_verify.py) · [automation/docs/coverage-verify.md](automation/docs/coverage-verify.md) |
| ANALYSE verifier | [analysis_verify.py](automation/tools/analysis_verify.py) · [automation/docs/analysis-verify.md](automation/docs/analysis-verify.md) |
| TEST-DISCOVER verifier | [discover_verify.py](automation/tools/discover_verify.py) · [automation/docs/discover-verify.md](automation/docs/discover-verify.md) |
| TEST-PREP verifier | [test_prep_verify.py](automation/tools/test_prep_verify.py) · [automation/docs/test-prep-verify.md](automation/docs/test-prep-verify.md) |
| CLOSE verifier | [close_verify.py](automation/tools/close_verify.py) · [automation/docs/close-verify.md](automation/docs/close-verify.md) · [close_archive.py](automation/tools/close_archive.py) |
| CLEAN verifier | [clean_verify.py](automation/tools/clean_verify.py) · [clean-verify.md](automation/docs/clean-verify.md) · helpers `clean_file_map.py`, `clean_apply_team.py`, `clean_apply_public.py` |
| Humans: Cursor + main processes | [HOW-TO.md](HOW-TO.md) |
| CTQA Postgres MCP | [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md) (*MCP — PostgreSQL*) — add **`postgres-ctqa`** to **gitignored** [`.cursor/mcp.json`](.cursor/mcp.json) and/or **global** `~/.cursor/mcp.json` (Windows: **`%USERPROFILE%\.cursor\mcp.json`**) using the JSON snippet there |
| Chrome DevTools MCP (**`chrome-devtools`**, ad-hoc UI) | [automation/docs/chrome-devtools-mcp.md](automation/docs/chrome-devtools-mcp.md); merge into `.cursor/mcp.json` — see [`.cursor/mcp.json.example`](.cursor/mcp.json.example) |

## Context escalation

1. Follow **[docs/harness-map.json](docs/harness-map.json)**: **T0** (`qa-handoff.md`, this file), then T1 `match_any_package` keywords; prefer the clearest single package, and follow that file’s **`rules`** (Jira-key MCP fetch, extra [docs/corner-platform-map.json](docs/corner-platform-map.json) when repro/env/repo scope applies)—do not open every doc by default.
2. **Corner QA on Confluence** is scoped to **QAPORTAL** page **497097273** (“Corner”) **and descendants** unless the user widens scope—see [docs/qa-project.json](docs/qa-project.json).
3. **Fork / platform** context: [docs/project.json](docs/project.json) → **CT** and **XT** Confluence spaces via MCP when needed.
4. **Hosts, repos, Jira projects** (which env, which Stash repo): [docs/corner-platform-map.json](docs/corner-platform-map.json) — credentials stay on Confluence only.

## How to start a session

1. Read **[qa-handoff.md](qa-handoff.md)** for current focus, blockers, and next steps.
2. For any substantive **pipeline**, **benchmark**, or **epic deliverable** work, read **[docs/harness-principles.md](docs/harness-principles.md)** once per session (or follow the matching **`harness-map.json`** package that includes it)—**stable doctrine**, not duplicated in `qa-handoff.md`.
3. Open only the **task-specific** docs or code paths you need—avoid loading the whole tree into context.
4. For substantive work, **update `qa-handoff.md`** before closing the session.

## MCP

### Jira and Confluence

All **discovery and retrieval** for Jira issues and Confluence pages (search, fetch, issue fields) must use **user-mcp-atlassian**. Read each tool’s schema before calling. Do not invent ticket or page content. **Do not** copy secrets from Atlassian into repo files.

### Figma (optional)

When tasks include **Figma file/frame/layer** URLs, use the **workspace-configured Figma MCP** if it is enabled in Cursor. Workflow: **[automation/docs/figma-mcp.md](automation/docs/figma-mcp.md)**. Do not store OAuth tokens or secrets in the repo.

### Chrome DevTools (optional, ad-hoc)

**Chrome DevTools MCP** (register as **`chrome-devtools`**) supports ad-hoc UI exploration (discover/precon/prep phases, harness maps)—not a **`CLOSE:`** dependency. **Setup:** [automation/docs/chrome-devtools-mcp.md](automation/docs/chrome-devtools-mcp.md) and **[`.cursor/mcp.json.example`](.cursor/mcp.json.example)**.

### PostgreSQL / CTQA (optional)

1. **SSH tunnel** to forward a local port to Postgres (PuTTY `plink` default on Windows): see **[automation/tools/tunnel/README.md](automation/tools/tunnel/README.md)**.
2. **Cursor `mcp.json`** — add **`postgres-ctqa`** in **gitignored** `.cursor/mcp.json` and/or **global** `~/.cursor/mcp.json` (Windows: **`%USERPROFILE%\.cursor\mcp.json`**) per the snippet in [automation/tools/tunnel/README.md](automation/tools/tunnel/README.md). Cursor merges project and global; do not define the same server twice with conflicting URLs. Uses `@sarmadparvez/postgresql-mcp` with **`?mode=readonly`**; use **`sslmode=disable`** on `127.0.0.1` through SSH.
3. **Do not** commit real passwords; credentials live only in ignored `.cursor/mcp.json` and/or global MCP.

When the tunnel is up and MCP is enabled, the agent may use **`query`**, **`schema`**, and **`list_tables`** against database **ctqa** for ad-hoc readonly checks during exploration pipelines—not **`CLOSE:`**.

## Codebase exploration

Prefer **narrow** search and **bounded** file reads; summarize findings instead of pasting large files. See [.cursor/prompts/codebase-context.md](.cursor/prompts/codebase-context.md) for a reusable scaffold.

## Rules in this repo

Persistent agent behavior is under [.cursor/rules/](.cursor/rules/): `harness-context`, **`jq-json`**, **`pipeline-router`** (trigger → playbook), `mcp-atlassian-search`, **`dxcore-console-harness`** (optional), **`dxtrade5-harness`** (optional), **`webbroker_harness`** (optional), `qa-artifacts`, `harness-maintenance`. **Stable doctrine:** [docs/harness-principles.md](docs/harness-principles.md). Keep **AGENTS.md** short; extend detail in linked JSON and Confluence via MCP.
