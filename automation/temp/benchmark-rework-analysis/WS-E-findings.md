# WS-E — Test-bench / TEST-PREP shadow-tree gap closure

**Date:** 2026-05-08

## Current state

- [`.cursor/pipelines/test-prep.md`](../../../.cursor/pipelines/test-prep.md): **single** user trigger `TEST-PREP:` orchestrates planning + **phase 8a** shells + **phase 8b** **one subprocess per bundle** with strict MUST/MUST-NOT against one-shot drafts. All durable paths **`epics/<KEY>/...`** + **`epics/<KEY>/temp/`** draft merges.
- [`.cursor/benchmark/test-bench/pipeline/benchmark-test-prep.md`](../../../.cursor/benchmark/test-bench/pipeline/benchmark-test-prep.md): **`BENCHMARK-TEST-*`** tokens; completion checklist explicitly verifies **`epics/<KEY>/<KEY>-tests.*`** and bundle flags — **not** copies under `test-bench/runs/` in v1 ([`test-bench/HOW-TO.md`](../../../.cursor/benchmark/test-bench/HOW-TO.md)).
- Scaffold: **`compare_test_runs.py`** TBD, **`validator-test.md`** future.

## Shadow-only benchmark impact

Production norm “read `coverage` from `epics/<KEY>/`” must become “read **`workspace_root`/`<KEY>/...`** resolved by benchmark mode.” Same for **`temp`** under that root.

Hard constraints that **cannot** soften:

- Phase **8b** isolation (no multi-bundle full draft in one completion when `map_only` false).
- No invented Jira text; traceability to checklist ids.
- Durable JSON must not contain `/temp/` paths after merge.

## Gates: deterministic tooling vs agent judgment

| Gate | Deterministic (script / schema) | Agent judgment |
|------|----------------------------------|----------------|
| File exists: `-tests.json`, `-tests.md` | Yes | — |
| `sources.map_only` / `sources.coverage_loaded` consistency | Yes (JSON schema) | — |
| Every bundle: `authoring.subprocess_completed` | Yes | Whether draft *quality* is acceptable — human/LLM review |
| `covers_check_ids` ⊆ coverage `checks[].id` | Scriptable | Ambiguity resolution for matrix |
| JQL fetch completeness | Partial (non-empty vs empty) | Whether search was *correct* for taxonomy |
| Gold alignment for tests | TBD when test gold schema exists | Narrative |

## Benchmark hub interaction

For each **attempt** including `test_prep` in manifest `modes[]`:

1. Prompt pack runs **one** `TEST-PREP:`-equivalent in **benchmark mode** (shadow root) — may require new trigger alias `TEST-PREP-BENCHMARK:` or mode token on same line to avoid router ambiguity.
2. Subprocess-per-bundle can remain **Cursor Task** or equivalent isolated workers **inside** that attempt’s session (still satisfies TEST-PREP contract).
3. `DONE.json` lists each `bundle_id` with `subprocess_completed: true` after verify.

## Misinterpretation

- **Repasting `TEST-PREP` per attempt** does not violate “single user trigger” **per session** — each cold session is a new trigger instance. The norm prohibiting “human re-prompt per test” refers to **per-bundle** prose inside one run, not forbidding **multiple benchmark attempts**.

## Deliverable checklist

- [x] Mapped current test-bench ↔ production TEST-PREP coupling  
- [x] Classified gates tool vs agent  
- [x] Noted trigger / router extension need for shadow mode  
