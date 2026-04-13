# Benchmark harness (Corner QA pipelines)

Self-contained under `.cursor/benchmark/`. **Not** linked from `AGENTS.md`, `README.md`, or `pipeline-router.mdc`—open this file when you want benchmark runs.

## Purpose

- Run **EPIC-PREP**-equivalent and **COVERAGE**-equivalent work **multiple times**, snapshotting outputs to measure **variance**.
- **Suite mode**: orchestrate many epics with **`BENCHMARK:`** / **`BENCHMARK-NEXT:`** — **one atomic pipeline per message** (see [`pipeline/benchmark-suite.md`](pipeline/benchmark-suite.md)).
- **Validate** against optional **gold** files; emit **crossref** + **digest**; suite finishes with **`runs/run-<suite_id>/SUMMARY.md`**.

## Layout

| Path | Role |
|------|------|
| [`HOW-TO.md`](HOW-TO.md) | This file |
| [`pipeline/benchmark-suite.md`](pipeline/benchmark-suite.md) | **`BENCHMARK:`** (plan queue only) + **`BENCHMARK-NEXT:`** (one step) |
| [`pipeline/benchmark-epic-prep.md`](pipeline/benchmark-epic-prep.md) | `BENCHMARK-EPIC-PREP:` |
| [`pipeline/benchmark-coverage.md`](pipeline/benchmark-coverage.md) | `BENCHMARK-COVERAGE:` |
| [`pipeline/validator.md`](pipeline/validator.md) | `PREP-VALIDATE:` / `COVERAGE-VALIDATE:` |
| [`scripts/compare_runs.py`](scripts/compare_runs.py) | Metrics → `crossref/` (legacy or `--suite-id`) |
| **`runs/run-<suite_id>/`** | **`support/`** (`queue.json`, `QUEUE.md`, `progress.json`, `suite-meta.json`), `attempts/<EPIC>/run-<seq>.json`, **`SUMMARY.md`** |
| **Legacy: `run-<n>/`** (under benchmark root, not under `runs/`) | Deprecated for new work; `meta.json` + snapshot sidecars |
| [`data/`](data/) | **You** add `<KEY>-gold.json` |
| [`crossref/`](crossref/) | Generated metrics JSON |
| [`digest/`](digest/) | Generated digest markdown |
| `temp/` | Local scratch only; do not commit secrets |

## Keywords (conventions)

Use in chat **after** instructing the agent to read the linked playbook (these are **not** registered in `pipeline-router.mdc`).

| Prefix | Playbook |
|--------|----------|
| **`BENCHMARK:`** | [`pipeline/benchmark-suite.md`](pipeline/benchmark-suite.md) |
| **`BENCHMARK-NEXT:`** | [`pipeline/benchmark-suite.md`](pipeline/benchmark-suite.md) |
| **`BENCHMARK-EPIC-PREP:`** | [`pipeline/benchmark-epic-prep.md`](pipeline/benchmark-epic-prep.md) |
| **`BENCHMARK-COVERAGE:`** | [`pipeline/benchmark-coverage.md`](pipeline/benchmark-coverage.md) |
| **`PREP-VALIDATE:`** | [`pipeline/validator.md`](pipeline/validator.md) |
| **`COVERAGE-VALIDATE:`** | [`pipeline/validator.md`](pipeline/validator.md) |

### Suite orchestration

- **`BENCHMARK: CRT-639, CRT-593`** — **plan only** in one turn: creates **`runs/run-<suite_id>/support/`** with `queue.json`, `QUEUE.md`, `progress.json`, `suite-meta.json`, plus empty **`attempts/<EPIC>/`** dirs. Default **`runs=3`** prep+coverage pairs per epic; optional **`repo=`**, **`focus=`**, **`suite_run=<id>`** (else auto id).
- **`BENCHMARK-NEXT: <suite_id>`** — execute **exactly one** queue step (prep, coverage, validate, or finalize). Repeat until done.
- Manual option: paste one line at a time from **`support/QUEUE.md`** instead of **`BENCHMARK-NEXT:`**.

### Single-epic benchmark (no suite)

- **`BENCHMARK-EPIC-PREP: CRT-639 runs=3`** — legacy **or** use **`suite_run=`** for structured paths under **`runs/run-<id>/attempts/...`**.
- **`PREP-VALIDATE: CRT-639`** — all legacy **`run-*`** for that epic, or **`PREP-VALIDATE: CRT-639 suite=<suite_id>`** for suite files only.

### Suite runner tokens (on prep/coverage lines)

- **`suite_run=<suite_id>`** — required for suite layout.
- **`attempt=<n>`**, **`seq=001`** — align with queue (seq zero-padded).
- **`runs=1`** per message when using **`BENCHMARK-NEXT:`**.

## Legacy vs suite snapshots

| | **Suite** | **Legacy** |
|--|-----------|------------|
| Prep | `runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json` with **`phase: prep`**, inline **`artifact`** | `run-<NNN>/epic-ref.snapshot.json` + `meta.json` |
| Coverage | same with **`phase: coverage`**, **`artifact`**, **`checklist_markdown`** | `run-<NNN>/coverage.snapshot.json` + `.md` |

**Deprecated**: new work should prefer **suite** or explicit **`suite_run=`**; legacy flat **`run-*`** remains supported for **`compare_runs.py`** and validators without **`suite=`**.

## Operator checklist

1. **Suite**: run **`BENCHMARK:`** once, then **`BENCHMARK-NEXT:`** (or paste from **`support/QUEUE.md`**) **once per step**; use a **fresh chat** per step if you need statistical isolation from prior context.
2. Confirm **`epics/<KEY>/temp/`** is deleted after each prep/coverage (production rule).
3. Confirm artifacts contain **no** `/temp/` paths.
4. Do **not** store secrets under `benchmark/`.
5. Add **`data/<KEY>-gold.json`** when you want gold alignment.

## Gold file schema (`data/<KEY>-gold.json`)

```json
{
  "epic_key": "CRT-639",
  "pipeline": "both",
  "scope_statement": "Oracle sentence for what this epic verifies.",
  "required_requirement_keys_in_snippets": ["CRT-1741", "CRT-1740"],
  "forbidden_checklist_regex": ["(?i)^## .*FIFO"],
  "required_smart_checklist_substrings": ["WeightedAvg", "FX_SPOT"]
}
```

- **`pipeline`**: `"prep"` | `"coverage"` | `"both"`.
- Omit keys you do not need.

## Automation

```bash
python .cursor/benchmark/scripts/compare_runs.py --help
python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic CRT-639 --kind prep
python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic CRT-639 --kind prep --suite-id <suite_id>
python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic CRT-639 --kind coverage --suite-id <suite_id>
```

With **`--suite-id`**, the script only reads **`run-*.json`** files whose wrapper **`phase`** matches **`--kind`** (`prep` vs `coverage`); malformed JSON files are still picked up so parse errors appear in metrics.

See [`pipeline/validator.md`](pipeline/validator.md) for digest sections and gold checks.
