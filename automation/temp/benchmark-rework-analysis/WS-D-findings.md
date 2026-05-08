# WS-D — Layout migration mapping

**Date:** 2026-05-08

## Current layout (conceptual — today)

| Bucket | Typical paths | Role |
|--------|----------------|------|
| Suite orchestration | `.cursor/benchmark/coverage-bench/runs/run-<suite_id>/support/` (`queue.json`, `QUEUE.md`, `progress.json`, `suite-meta.json`) | BENCHMARK-NEXT state machine |
| Attempt snapshots | `.../attempts/<KEY>/run-<seq>.json` | Prep/coverage payload copies |
| Cross metrics | `.cursor/benchmark/coverage-bench/crossref/*-metrics.json` | `compare_runs.py` |
| Digest / history | `coverage-bench/digest/`, `coverage-bench/history/` | Validator outputs |
| Gold | `.cursor/benchmark/coverage-bench/data/<KEY>-gold.json` | Oracle (moving per roadmap to shared `benchmark/data`; WS-F) |
| Human summaries | `.cursor/benchmark/run-results/*.md` | Derivative narratives |
| Test scaffold | `.cursor/benchmark/test-bench/` runs/support (planned); durable tests still **`epics/`** in v1 | PATH T |

## Target layout (from roadmap intent)

Single logical tree under `.cursor/benchmark/runs/<suite_label>/`:

| Root child | Contents |
|------------|----------|
| `report.md` | Human-primary; mirrors run-results templates (Evidence, Epic-scoped, Generalized recommendations, Epic-local follow-ups) |
| `_manifest.json` | WS-C manifest |
| `attempt-<nn>/` | `PROMPT.md`, `DONE.json`, `_machine/` (or similar) hiding JSON snapshots + shadow `epics/<KEY>/...` payloads |
| `_aggregate/` | Post-all-attempts: crossref-equivalent metrics, validator digests, compare logs |
| _(optional)_ `data/` symlink or pointer | Prefer **suite-agnostic** gold only under `.cursor/benchmark/data/` |

**Relocation map**

| Legacy | Target |
|--------|--------|
| `coverage-bench/runs/run-*` | `.cursor/benchmark/runs/<label>/attempt-*` snapshot structure merged with shadow durable tree |
| `coverage-bench/crossref/` | `.cursor/benchmark/runs/<label>/_aggregate/crossref/` **or** keep global crossref with `suite_id` in filenames (decision: global pollutes git; per-suite folder cleaner) |
| `coverage-bench/digest/` | `_aggregate/digest/` per suite |
| `coverage-bench/history/` | Either global (longitudinal) or per-suite first line; WS-F notes append-only behavior |
| `run-results/*.md` | Superseded by each suite’s `report.md` at run root |
| `test-bench/runs/` | Same `runs/<label>/` convention with `modes` including `test_prep` |

## Documentation / harness files to update when implementing

| Consumer | Likely edits |
|----------|----------------|
| [`.cursor/HOW-TO.md`](../../../.cursor/HOW-TO.md) benchmark table | New paths + hub flow |
| [`.cursor/benchmark/README.md`](../../../.cursor/benchmark/README.md), [`BENCHMARK_RUNBOOK.md`](../../../.cursor/benchmark/BENCHMARK_RUNBOOK.md) | Deprecate BENCHMARK-NEXT-centric flow gradually |
| [`.cursor/pipelines/public-scrub.md`](../../../.cursor/pipelines/public-scrub.md) | Scratch locations for benchmark crumbs |
| [`.cursor/rules/qa-artifacts.mdc`](../../../.cursor/rules/qa-artifacts.mdc) / [`AGENTS.md`](../../../AGENTS.md) | If benchmarks become first-class documented paths |

## Risks

- **Gitignore:** benchmark often excluded from VCS — migration docs must state what operators commit vs ignore (`report.md` only? manifest + `_aggregate/`?).
- **Deep links:** existing run folders and digests cite old paths — need one-time rewrite table in implementation PR.

## Deliverable checklist

- [x] Before/after path map  
- [x] Doc surface list  
- [x] Git/report policy note  
