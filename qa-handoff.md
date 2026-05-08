# QA session handoff — Corner Trader

Read at the start of substantive QA work; **update before ending** (date, focus, next steps). Detail lives in **`epics/<KEY>/`** and **[AGENTS.md](AGENTS.md)** — do not duplicate long pipeline logs here.

## Last updated

- **Date**: 2026-05-08 — **CRT-639 hub benchmark** (multiple cold sessions, `benchmark_suite` + `benchmark_attempt`) produced shadow artifacts under **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/shadow/CRT-639/`** (`-ref.json`, `-coverage.json`/`.md`, `-tests.json`/`.md`) per **`docs/benchmark-contract.md`**. That example suite folder was removed locally; re-run **`/crtqa-benchmark`** / **`FINALIZE_PROMPT.md`** for a new **`suite_id`** and store the narrative under **`.cursor/benchmark/run-results/<run-key>/report.md`** (see **`.cursor/benchmark/run-results/README.md`**).
- **Date**: 2026-04-28 — Confluence/Yogi trace for **Est. AF Effect** / **CRT-030**, **CRT-707**, **CRT-1730** (FX_SPOT reference price) and BE parity checklist: [automation/temp/af-effect-plan-delivery.md](automation/temp/af-effect-plan-delivery.md) (+ storage export `automation/temp/confluence-portfolio-metrics-345703196.json`).
- **Date**: 2026-04-17 — Added [corner-map/](corner-map/) seed (Phase 5 change-map plan + [corner-map/docs/architecture.md](corner-map/docs/architecture.md)); [README.md](README.md) Satellite link. Prior: 2026-04-16 trimmed handoff noise.

## Current focus

- **CRT-642** (*Non-trading hours*): [CRT-642-ref.json](epics/CRT-642/CRT-642-ref.json), [CRT-642-coverage.md](epics/CRT-642/CRT-642-coverage.md), [CRT-642-analysis.md](epics/CRT-642/CRT-642-analysis.md). **Next**: `TEST-PREP: CRT-642` (optional `TEST-EXEC:` when env is ready). Open gaps called out in analysis: CRT-1481 pointer; chk-015 DxFeed deferral; Stash `bitbucket_search_code` **404** (use browse fallback per playbooks).
- **CRT-639** (cash settlement / weighted average): production **`epics/CRT-639/`** files are **not** present in-repo (cleared during benchmark housekeeping, or authored only under **benchmark shadow**: **`.cursor/benchmark/runs/<suite>/attempt-*/shadow/CRT-639/`** — see **`docs/benchmark-contract.md`**). Restore production tree via **`EPIC-PREP:`** → **`COVERAGE:`** → optional **`TEST-PREP:`** / **`TEST-EXEC:`** when that epic is active again (see **[HOW-TO.md](HOW-TO.md)** triggers). **Benchmark-mode** pipelines must pass **`benchmark_suite=`** / **`benchmark_attempt=`** consistently if using shadow **`{EpicDir}`**.

Tiered context and MCP scope: **[AGENTS.md](AGENTS.md)** → **[docs/harness-map.json](docs/harness-map.json)**. Hosts and dashboards (no secrets in git): **[docs/corner-platform-map.json](docs/corner-platform-map.json)**.

## Blockers

- **user-mcp-atlassian** must be healthy for live Jira/Confluence; retry or check MCP in Cursor settings.
- **Figma MCP**: re-auth OAuth if design tools fail.

## Next steps

1. **`TEST-PREP: CRT-642`** when regression drafts are the priority.
2. Before **`PUBLIC-SCRUB:`**: ensure branch **`release`** exists from **`main`** per [README.md](README.md) (operator workflow if `release` was removed).
3. If Corner env URLs or Jira links change materially on Confluence, bump **`last_reviewed`** in [docs/corner-platform-map.json](docs/corner-platform-map.json).

## Notes

- **AF / FX_SPOT pricing:** CRT-1730 still has “link TBD”; align with **CRT-1910** (market FX Spot extra params) and cash-settlement / average-price elaboration on [FX Rolling Spot Estimations](https://confluence.in.devexperts.com/pages/viewpage.action?pageId=490569747) when filing defects vs spec.
- Ordered workflow scaffold: [.cursor/prompts/combined-qa-task.md](.cursor/prompts/combined-qa-task.md). Credentials stay on Confluence, not in repo files.
- **corner-map** (planned): portable spec under [corner-map/README.md](corner-map/README.md); next owner step is extract to dedicated repo and add validator / runner harness (see README checklist).
