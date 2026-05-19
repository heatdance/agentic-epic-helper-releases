# WS-C — Control hub specification (vendor-neutral core)

**Date:** 2026-05-08

## Design principle

The **filesystem + manifest** is the contract any vendor’s agent runner can obey. Cursor slash commands (`/crtqa-benchmark`), Python CLIs, or CI jobs are thin **emitters/verifiers** of that contract — see precedent: [`.cursor/commands/crtqa-stats.md`](../../../.cursor/commands/crtqa-stats.md) drives behavior by **Markdown playbook**, not by a bundled `crtqa` binary under [`automation/tools/`](../../../automation/tools). For benchmark, recommend **parity first** (slash command README + prompts) with **optional** `automation/tools/crtqa-benchmark/` later for `verify`/`status`/`report` deterministic steps.

## 1. Manifest (suggested schema — analytical, not implemented)

Place at suite root next to orchestration state, e.g. `.cursor/benchmark/runs/<suite_label>/manifest.json`:

| Field | Purpose |
|-------|---------|
| `schema_version` | Evolve compatibility |
| `suite_id` / `suite_label` | Human + machine id |
| `epics[]` | Jira keys |
| `modes` | Ordered stack: e.g. `["epic_prep","coverage"]` or add `analysis`, `test_discover`, `test_precon`, `test_prep`, `close` |
| `attempts` | Integer N — **must match** required cold sessions for cross-run variance |
| `gold` | Map: `prep`, `coverage`, `tests` → paths under [`.cursor/benchmark/data/`](../../../.cursor/benchmark/data) (see WS-F) |
| `tokens` | Optional `repo`, `focus`, `map_only`, etc. |
| `benchmark_mode` literal | Forces playbooks into shadow tree (implementation TBD) |
| `created_at` | ISO |

## 2. Per-attempt prompt pack (`attempt-<nn>/PROMPT.md` or sibling)

Machine-generated blob the operator pastes **once** into a **new** session (WS-B):

- Absolute paths for shadow outputs (once pipeline supports them).
- Explicit **benchmark_mode** sentence + playbook file list to read first.
- Ordered triggers for the selected `modes[]` stack for **this attempt only**.
- Forbidden: chaining multiple attempts in one paste.

## 3. Completion handshake — `DONE.json`

Suggested path: `.cursor/benchmark/runs/<suite>/attempt-<nn>/DONE.json`:

| Field | Purpose |
|-------|---------|
| `attempt`, `suite_id`, `schema_version` | Join to manifest |
| `completed_at` | ISO |
| `modes_completed[]` | Each pipeline gate run in this attempt |
| `artifacts[]` | List of required relative paths present (or glob checksums) |
| `tooling_fingerprint` | Optional: MCP/agent product name + version — not required v1 |
| `integrity` | Optional: SHA256 map for key JSON files |

**Automation boundary:** Hub **`verify`** only checks **presence + optional schema validity** — not subjective quality (validators remain separate phase).

## 4. Conceptual subcommands (language-agnostic)

| Subcommand | Responsibility |
|------------|------------------|
| `init` | Create `suite` folder tree, manifest from template / CLI args, emit `attempt-01/PROMPT.md` … `attempt-N/PROMPT.md` |
| `status` | For each attempt: MISSING / IN_PROGRESS / DONE per `DONE.json` + required artifact list |
| `verify` | Exit non-zero if any required artifact missing or JSON invalid |
| `aggregate` | After all `DONE.json`: invoke `compare_runs.py` (or successors) paths, validators, assemble **draft** `report.md` sections |
| `report` | Finalize root `report.md` (deterministic templating preferred; optional LLM polish flagged in metadata)

## 5. Misinterpretation guardrails

- **Automatic gates:** No requirement that the hub **runs** MCP or pipelines — only that it **documents** gate order and verifies **artifacts**. LLM execution stays in child sessions unless you adopt Cursor SDK programmatic agents later.
- **BENCHMARK-NEXT replacement:** Removing chat-based `BENCHMARK-NEXT` implies **either** playbook-internal step machines (risky without code) **or** manifest-driven prompt packs only (recommended intermediate).

## Deliverable checklist

- [x] Manifest field sketch  
- [x] DONE.json sketch  
- [x] Subcommand responsibilities  
- [x] Vendor-neutral vs crtqa-stats precedent  
