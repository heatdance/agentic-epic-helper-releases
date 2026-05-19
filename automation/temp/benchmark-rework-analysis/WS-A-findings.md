# WS-A — Artifact and path coupling audit

> **Historical context (superseded for git / grep expectations):** As of benchmark harness finishing work (2026), **`.cursor/benchmark/`** harness sources are **tracked** in the repo except machine paths listed in **`.gitignore`** (see **`.cursor/benchmark/README.md`** § Git hygiene). Findings below about “may be gitignored” / “not fully greppable” applied to the **earlier** state when the tree was wholly ignored — keep the coupling table as design rationale.

**Date:** 2026-05-08  
**Method:** `epics/<` / `epics/` pattern search under `.cursor/pipelines`, `.cursor/rules`, `.cursor/prompts`, `epics/templates`, `automation`. Manual read of benchmark delegates (historically, files under `.cursor/benchmark` could be omitted from tooling when gitignored wholesale).

## Executive summary

Production pipelines hard-code **`epics/<KEY>/`** for durable outputs, **`epics/<KEY>/temp/`** for scratch, and sibling reads (`-ref.json` → `-coverage.json` chain). Benchmark delegates today **re-run the same playbooks**, so they **mutate `epics/<KEY>/`** and only **mirror** into `coverage-bench/runs/.../attempts/...`. A shadow-only benchmark mode requires **every** reader/writer on that path surface to accept a **workspace root** (production vs benchmark).

## Durable artifacts × production path × benchmark target (conceptual) × consumers

| Artifact | Production path | Intended benchmark shadow (from roadmap) | Primary consumers |
|----------|-----------------|------------------------------------------|-------------------|
| Epic ref | `epics/<KEY>/<KEY>-ref.json` | e.g. `.cursor/benchmark/runs/<run>/<attempt>/shadow/<KEY>/<KEY>-ref.json` | `coverage.md` (read), `test-prep.md` (optional read), `analysis.md` (optional read), templates `epic_ref_path` in `coverage-ref.json` |
| Coverage JSON/MD | `epics/<KEY>/<KEY>-coverage.{json,md}` | same under shadow attempt root | `test-prep.md` (required), `analysis.md`, `close.md` (optional), templates `sources.coverage_path` in `tests-ref.json` |
| Analysis JSON/MD | `epics/<KEY>/<KEY>-analysis.{json,md}` | shadow (if ANALYSE in stack) | `test-prep.md` (optional read); may mutate coverage when `known_issues=yes` |
| Discover / Precon | `epics/<KEY>/<KEY>-discover.json`, `-precon.{json,md}` | shadow | `test-precon.md`, `test-prep.md`, `close.md` (preflight) |
| Tests JSON/MD | `epics/<KEY>/<KEY>-tests.{json,md}` | shadow | Human Jira paste; `close.md` L0 |
| CLOSE manifest | `epics/<KEY>/context/<KEY>-close.json` after archive | shadow `context/` same layout | `close_verify.py`; documentation-only |
| Temp | `epics/<KEY>/temp/` (+ test-prep / close scratch) | benchmark-scoped temp only (never `epics/`) | Pipeline self-check: no `/temp/` in durable JSON |

## Files with strong `epics/<KEY>/` coupling (grep-backed)

### `.cursor/pipelines/`

| File | Role |
|------|------|
| [`.cursor/pipelines/epic-prep.md`](../../../.cursor/pipelines/epic-prep.md) | Creates folder, `-ref.json`, temp lifecycle |
| [`.cursor/pipelines/coverage.md`](../../../.cursor/pipelines/coverage.md) | Prerequisite `-ref.json`; writes `-coverage.*`; reads ref |
| [`.cursor/pipelines/analysis.md`](../../../.cursor/pipelines/analysis.md) | Reads ref/coverage; writes `-analysis.*`; may edit `-coverage.*` |
| [`.cursor/pipelines/test-prep.md`](../../../.cursor/pipelines/test-prep.md) | Reads coverage (+ optional analysis/ref); temp draft merge; writes `-tests.*` |
| [`.cursor/pipelines/close.md`](../../../.cursor/pipelines/close.md) | Integrity ladder; archive to `context/` |
| [`.cursor/pipelines/test-discover.md`](../../../.cursor/pipelines/test-discover.md) | `-discover.json` |
| [`.cursor/pipelines/test-precon.md`](../../../.cursor/pipelines/test-precon.md) | `-precon.*` |
| [`.cursor/pipelines/sync.md`](../../../.cursor/pipelines/sync.md) | Harness table referencing temp under `epics/<KEY>/temp/` |
| [`.cursor/pipelines/public-scrub.md`](../../../.cursor/pipelines/public-scrub.md) | Deletes real `epics/<REAL_EPIC_KEY>/`; mentions `.cursor/benchmark/` scratch |

### `.cursor/rules` / prompts

| File | Role |
|------|------|
| [`.cursor/rules/pipeline-router.mdc`](../../../.cursor/rules/pipeline-router.mdc) | Normative durable + temp paths for all epic pipelines |
| [`.cursor/rules/qa-artifacts.mdc`](../../../.cursor/rules/qa-artifacts.mdc) | Template → `epics/<KEY>/...` mapping |
| [`.cursor/prompts/combined-qa-task.md`](../../../.cursor/prompts/combined-qa-task.md), [`epic-prep.md`](../../../.cursor/prompts/epic-prep.md), [`confluence-spec-work.md`](../../../.cursor/prompts/confluence-spec-work.md) | Operator instructions embedding `epics/` paths |

### `epics/templates/`

Embedded path strings in JSON `_comment` and `*_path` fields: [`epic-ref.json`](../../../epics/templates/epic-ref.json), [`coverage-ref.json`](../../../epics/templates/coverage-ref.json), [`analysis-ref.json`](../../../epics/templates/analysis-ref.json), [`tests-ref.json`](../../../epics/templates/tests-ref.json), [`close-ref.json`](../../../epics/templates/close-ref.json), [`discover-ref.json`](../../../epics/templates/discover-ref.json), [`precon-ref.json`](../../../epics/templates/precon-ref.json). Pre-**CLOSE** paths use `epics/<KEY>/`; post-close JSON under `epics/<KEY>/context/` (see [close-contract.json](../../../docs/close-contract.json)). Runtime paths use `{EpicDir}` when benchmark tokens are set.

### `automation`

| File | Role |
|------|------|
| [`automation/docs/yogi-url-resolve.md`](../../docs/yogi-url-resolve.md) | Example storing snippets in `epics/<EPIC>/...` |

### Benchmark layer (manual / prior read; greppability caveat superseded — see banner)

| File | Coupling |
|------|----------|
| [`.cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md`](../../../.cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md) | Explicitly delegates to `epic-prep.md`; durable `epics/<KEY>/<KEY>-ref.json` |
| [`.cursor/benchmark/coverage-bench/pipeline/benchmark-coverage.md`](../../../.cursor/benchmark/coverage-bench/pipeline/benchmark-coverage.md) | Same for coverage |
| [`.cursor/benchmark/coverage-bench/HOW-TO.md`](../../../.cursor/benchmark/coverage-bench/HOW-TO.md) | States delegates write under `epics/<KEY>/` |

### Repo docs / handoff

| File | Role |
|------|------|
| [`qa-handoff.md`](../../../qa-handoff.md) | Points humans at concrete `epics/<KEY>/` paths; CRT-639 note on benchmark housekeeping |

### `compare_runs.py`

[`.cursor/benchmark/coverage-bench/scripts/compare_runs.py`](../../../.cursor/benchmark/coverage-bench/scripts/compare_runs.py) — **does not reference `epics/`**; consumes suite `attempts/*.json` + optional `data/<KEY>-gold.json` under `--benchmark-root`. Benchmark shadow move affects it only via **attempt snapshot layout** and **gold path** relocation (WS-F).

## Collision / concurrency edge cases (for WS-B linkage)

Same production `<KEY>` while benchmark runs: **shared** `epics/<KEY>/temp/` and **same filenames** (`-ref.json`, etc.) make parallel production + benchmark or two benchmark attempts writing to production **unsafe**. Shadow-only mode removes prod collision; parallel **attempt** folders still need distinct paths per attempt (already partially modeled by suite `attempts/<KEY>/run-*.json` snapshots).

## Deliverable checklist

- [x] Epic pipeline inventory  
- [x] Template + router + prompts consumers  
- [x] Benchmark delegate coupling  
- [x] compare_runs independence from epics  

**Next implementation dependency:** introduce a single **path context** concept (names TBD) referenced by all of the above, or accept duplicated path rules in every playbook (not recommended).
