# WS-F — Gold and metrics continuity

**Date:** 2026-05-08

## Current behavior

[`.cursor/benchmark/coverage-bench/scripts/compare_runs.py`](../../../.cursor/benchmark/coverage-bench/scripts/compare_runs.py):

- Loads gold via **`benchmark_root / "data" / f"{epic_key}-gold.json"`** (`_load_gold`).
- `_attach_gold_checks`, `_evaluate_thresholds`, `_evaluate_sanitization`, `_append_history_entry` — all keyed by `epic_key` and **`--kind` (`prep`|`coverage`)**.
- Writes **`crossref/<KEY>-{prep|coverage}-metrics.json`** under same `benchmark-root`.
- **Appends** `.cursor/benchmark/coverage-bench/history/<KEY>-{prep|coverage}-history.jsonl` (`_append_history_entry`) — longitudinal side effect on every successful run.

[`.cursor/benchmark/coverage-bench/pipeline/validator.md`](../../../.cursor/benchmark/coverage-bench/pipeline/validator.md): documents optional gold path **`.cursor/benchmark/coverage-bench/data/<KEY>-gold.json`** and same crossref/digest outputs.

## Roadmap relocation: `.cursor/benchmark/data/`

| Concern | Note |
|---------|------|
| Path change | Add `benchmark_root / ".." / "data"` or unify `--benchmark-root` to `.cursor/benchmark` and place `coverage-bench/scripts` lookups relative to new root — **needs single resolution rule** |
| Existing gold files | One-time move `coverage-bench/data/*.json` → `benchmark/data/` + update validator docs |
| Validator narrative | Inline paths in HOW-TO, run-results README gold schema pointers |
| `compare_runs` default `--benchmark-root` | Today defaults `.cursor/benchmark/coverage-bench`; changing breaks muscle memory unless CLI wrapper sets new default |

## History append coupling (edge)

If `--benchmark-root` moves to suite-scoped dirs (WS-D), **global** longitudinal history probably belongs under `.cursor/benchmark/history/` (gitignored) or explicit `CORNER_BENCHMARK_HISTORY=1` flag — otherwise each suite writes duplicate or fragmented trend lines.

**Analytical recommendation:** separate **suite-local metrics** (`_aggregate/crossref/`) from **optional global regression history** (`benchmark/history/`) keyed by `{epic,key,kind}` only.

## Test-bench gold

Not implemented (`test-bench/data/` TBD per HOW-TO). When added, reuse **structured_assertions** pattern from coverage gold schema in [`.cursor/benchmark/coverage-bench/HOW-TO.md`](../../../.cursor/benchmark/coverage-bench/HOW-TO.md).

## Deliverable checklist

- [x] Mapped compare_runs gold + historytouchpoints  
- [x] Stated relocation to `benchmark/data/` consequences  
- [x] Flagged longitudinal history placement conflict with per-suite folders  
