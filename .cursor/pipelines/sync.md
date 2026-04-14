# Pipeline: harness SYNC

**Trigger**: user message starts with **`SYNC:`**. Optional token on the same line:

- **`scope=full`** (default) — run all tiers **T0–T6** below.
- **`scope=pipelines`** — **T0**, **T1** only (router, harness-map, AGENTS, README, HOW-TO, qa-artifacts tables).
- **`scope=prompts`** — **T2** only ([`.cursor/prompts/`](../prompts/)).
- **`scope=templates`** — **T3** only ([`epics/templates/`](../../epics/templates/), [`epics/README.md`](../../epics/README.md)).
- **`scope=tools`** — **T4** only: [`automation/tools/`](../../automation/tools/), [`automation/docs/`](../../automation/docs/), harness **T2** hints if MCP/tunnel docs change.
- **`scope=mcp`** — **T4** **MCP sub-tier only** (postgres-ctqa snippet + global vs project `.cursor/mcp.json` story across HOW-TO / AGENTS / README / tunnel README).

**Scope**: Reconcile **harness pointers** after adding or changing a pipeline, template, tool, test surface, **MCP documentation** (e.g. postgres-ctqa snippet in HOW-TO), or **rule** file. Complements **`PUBLIC-SCRUB:`** ([`public-scrub.md`](public-scrub.md)) which runs only on **`release`**. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Hard invariant**: Run **`SYNC:`** only on **`develop`** or **`main`**. If the current branch is **`release`**, **stop** — use **`PUBLIC-SCRUB:`** there; do not use **`SYNC:`** as a release workflow.

**Policy anchor**: [`.cursor/rules/harness-maintenance.mdc`](../rules/harness-maintenance.mdc) — same-change updates to AGENTS, README, harness-map, rules/prompts.

**Outputs**: Edits across consumer files (typically **one** commit on **`develop`** or **`main`** with harness consistency fixes). No semver manifest; does not touch [`docs/public-export-manifest.json`](../../docs/public-export-manifest.json) or the **`PUBLIC-SCRUB:`** playbook’s release-only artifacts.

**Ephemeral**: [`automation/temp/sync/`](../../automation/temp/sync/) — optional notes or `rg` captures; **delete recursively** before finishing. Durable files must **not** reference `automation/temp/sync/`.

---

## Preflight (blocking)

1. **`git rev-parse --is-inside-work-tree`** — must succeed.
2. **`git branch --show-current`** — must be **`develop`** or **`main`**.
   - If the branch is **`release`**: **stop**. Instruct the operator to use **`PUBLIC-SCRUB:`** on `release` for public export, or checkout **`develop`**/**`main`** to run **`SYNC:`**.
   - Other branches: playbook does not forbid them, but **default** team policy is **`develop`**/**`main`** only; if on a feature branch, either merge via PR after SYNC commit or document skip.

---

## Normative pipeline registry (v1)

When you **add** a new file under `.cursor/pipelines/*.md`, **update this table** in the same change set, then apply **T0–T1** for all rows.

| Pipeline id | Trigger | Playbook | `harness-map` T1 package `id` | Temp / ephemeral | Must appear in: router, map, AGENTS, README, HOW-TO (bullets + keywords), qa-artifacts |
|-------------|---------|----------|-------------------------------|------------------|----------------------------------------------------------------------------------------|
| `epic-prep` | **`EPIC-PREP:`** | [`epic-prep.md`](epic-prep.md) | `epic_ref` | `epics/<KEY>/temp/` | Yes |
| `coverage` | **`COVERAGE:`** | [`coverage.md`](coverage.md) | `coverage_pipeline` | `epics/<KEY>/temp/` | Yes |
| `analysis` | **`ANALYSE:`** | [`analysis.md`](analysis.md) | `analysis_pipeline` | `epics/<KEY>/temp/` | Yes |
| `test-prep` | **`TEST-PREP:`** | [`test-prep.md`](test-prep.md) | `test_prep_pipeline` | `epics/<KEY>/temp/` | Yes |
| `test-exec` | **`TEST-EXEC:`** | [`test-exec.md`](test-exec.md) | `test_exec_pipeline` | `epics/<KEY>/temp/` | Yes |
| `public-scrub` | **`PUBLIC-SCRUB:`** | [`public-scrub.md`](public-scrub.md) | `public_scrub_pipeline` | `automation/temp/public-scrub/`; commits **only** on **`release`** | Yes (human docs describe **`release`** constraint) |
| `sync` | **`SYNC:`** | [`sync.md`](sync.md) (this file) | `sync_pipeline` | `automation/temp/sync/` | Yes |

**Exemptions**: None today. If a playbook is internal-only later, document **`harness-map` exemption** in this table and skip AGENTS/README/HOW-TO rows only with rationale.

---

## Tier T0 — Pipelines vs router vs harness-map

**Scope**: `full`, `pipelines`

1. List **`.cursor/pipelines/*.md`** (excluding non-playbook files if any appear later).
2. Each playbook has exactly one matching row in [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc) **Trigger → pipeline**.
3. Each **user-facing** pipeline in the [registry](#normative-pipeline-registry-v1) has a **`match_any_package`** entry in [`docs/harness-map.json`](../../docs/harness-map.json) with correct **`read`** paths and **`mcp_hint`** where applicable.
4. [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc) **Hard rules** — temp folders and **`PUBLIC-SCRUB:`** / **`SYNC:`** branch rules match the corresponding playbooks’ **Ephemeral** / preflight sections.

---

## Tier T1 — Entry-point tables

**Scope**: `full`, `pipelines`

Align:

- [`AGENTS.md`](../../AGENTS.md) — **Pipelines** table (all triggers + paths + branch notes for **`PUBLIC-SCRUB:`** / **`SYNC:`**).
- [`README.md`](../../README.md) — **Pipelines (chat triggers)** table.
- [`.cursor/HOW-TO.md`](../HOW-TO.md) — **Pipelines** bullets + **Keywords → pipelines** list.
- [`.cursor/rules/qa-artifacts.mdc`](../rules/qa-artifacts.mdc) — durable artifact bullets for epic pipelines, **`PUBLIC-SCRUB:`**, **`SYNC:`**.

---

## Tier T2 — Prompts

**Scope**: `full`, `prompts`

1. Scan [`.cursor/prompts/*.md`](../prompts/) for workflow steps that list pipeline triggers (e.g. [`combined-qa-task.md`](../prompts/combined-qa-task.md)).
2. Add or update lines for any new **Epic** pipelines; optionally mention **`PUBLIC-SCRUB:`** / **`SYNC:`** where humans paste starters for harness work.
3. Ensure relative links to playbooks still resolve.

---

## Tier T3 — Templates and epics README

**Scope**: `full`, `templates`

1. [`epics/templates/*`](../../epics/templates/) — `_comment` / schema text references the correct **`.cursor/pipelines/*.md`** and triggers.
2. [`epics/README.md`](../../epics/README.md) — workflow matches router + templates.

---

## Tier T4 — Tools, automation docs, and MCP documentation (postgres-ctqa)

**Scope**: `full`, `tools`, `mcp`

### T4a — Automation tools

**Scope**: `full`, `tools` (includes **`scope=mcp`**-only runs: skip)

1. New or renamed tools under [`automation/tools/`](../../automation/tools/) have docs under [`automation/docs/`](../../automation/docs/) and/or a **README** in the tool folder.
2. [`AGENTS.md`](../../AGENTS.md) and [`README.md`](../../README.md) **Automation** sections link discoverable tools when relevant.

### T4b — Postgres MCP snippet and `mcp.json` story

**Scope**: `full`, `tools`, `mcp`

1. There is **no** committed **`.cursor/mcp/`** folder; do **not** reintroduce template JSON files there. The **`postgres-ctqa`** copy-paste snippet lives in [`.cursor/HOW-TO.md`](../HOW-TO.md) (*MCP — PostgreSQL*).
2. [**`AGENTS.md`**](../../AGENTS.md), [**`README.md`**](../../README.md), [`.cursor/HOW-TO.md`](../HOW-TO.md), and [**`automation/tools/tunnel/README.md`**](../../automation/tools/tunnel/README.md) must stay aligned: engineers add MCP either to **global** `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`) **or** to **gitignored** project [`.cursor/mcp.json`](../../.cursor/mcp.json) — Cursor merges both; avoid duplicate **`postgres-ctqa`** definitions.
3. If MCP or tunnel **behavior** changes, update [`docs/harness-map.json`](../../docs/harness-map.json) **T2** / relevant **`mcp_hint`** and [`.cursor/HOW-TO.md`](../HOW-TO.md).

---

## Tier T5 — `.cursor/rules` inventory

**Scope**: `full` only (not `tools` / `mcp` / `pipelines` alone — run **`scope=full`** or add explicit passes)

1. Enumerate **`.cursor/rules/*.mdc`**.
2. Align with [**`AGENTS.md`**](../../AGENTS.md) *Rules in this repo* list and [`.cursor/HOW-TO.md`](../HOW-TO.md) **`.cursor/rules/`** bullets when a new rule file is added or renamed.

---

## Tier T6 — Harness maintenance and orphans

**Scope**: `full` only

1. Re-read [`.cursor/rules/harness-maintenance.mdc`](../rules/harness-maintenance.mdc).
2. Targeted **`rg`**: stale playbook filenames, removed triggers still mentioned, broken relative links to `.cursor/pipelines/` (fix or remove).
3. Optional: **`rg`** for obsolete paths (e.g. removed **`docs/tc-ref`** after migration to **`epics/templates/tests-ref.json`**, or removed **`.cursor/mcp/`** template folder).

---

## V1 — Verification

After edits:

1. Each **trigger** in the [registry](#normative-pipeline-registry-v1) appears in **`pipeline-router.mdc`** and in **HOW-TO** **Keywords → pipelines** (except if a future exemption is documented).
2. **`docs/harness-map.json`** parses as JSON; no duplicate **`id`** values inside **`match_any_package`**.
3. [`.cursor/HOW-TO.md`](../HOW-TO.md) (*MCP — PostgreSQL*) still contains the **`postgres-ctqa`** JSON snippet; AGENTS, README, and tunnel README still point to HOW-TO (no resurrected **`.cursor/mcp/*.json`** templates).

---

## V2 — Second pass

1. Re-read **AGENTS**, **README**, **HOW-TO** pipeline sections against the registry table row-by-row.
2. Record a short **`validation_log`** in the session summary (chat or **`qa-handoff.md`**): V1 checks done, V2 spot-check OK.

---

## Phases checklist

| # | Phase | Scope gates | Done when |
|---|--------|-------------|-----------|
| 0 | Preflight | all | On **`develop`** or **`main`**; not using **`SYNC:`** on **`release`** |
| 1 | T0 | full, pipelines | Router + harness-map + hard rules aligned |
| 2 | T1 | full, pipelines | AGENTS, README, HOW-TO, qa-artifacts aligned |
| 3 | T2 | full, prompts | Prompts list triggers / links |
| 4 | T3 | full, templates | Templates + epics README aligned |
| 5 | T4a | full, tools | Tool docs + AGENTS/README |
| 6 | T4b | full, tools, mcp | HOW-TO postgres snippet + global vs project `mcp.json` story + harness-map T2 if needed |
| 7 | T5 | full only | Rules inventory vs AGENTS / HOW-TO |
| 8 | T6 | full only | harness-maintenance + orphan `rg` clean |
| 9 | V1 | all applicable | Trigger + JSON + HOW-TO postgres snippet / MCP doc pointers pass |
| 10 | V2 | all applicable | Second pass + log |
| 11 | Cleanup | all | **`automation/temp/sync/`** deleted |

---

## Non-goals (v1)

- No **`docs/harness-registry.json`** (table above is canonical until extracted).
- No CI gate (optional follow-up).
- No interaction with **`PUBLIC-SCRUB:`** semver or **`release`** commits.

---

## Relation to PUBLIC-SCRUB

Run **`SYNC:`** on **`develop`** after harness structure changes; merge to **`main`** when stable. Then run **`PUBLIC-SCRUB:`** on **`release`** so the export inherits consistent pointers.
