# Shadow session — COVERAGE only (cold context)

**Suite:** `<SUITE_ID>`  
**Run index `<r>` / folder:** `attempt-<nn>` (e.g. `r=1` → `attempt-01`)  
**Epic:** `<KEY>`

## Rules

1. Read [`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md) and [`.cursor/benchmark/coverage-bench/pipeline/benchmark-coverage.md`](../coverage-bench/pipeline/benchmark-coverage.md) before executing.
2. **Shadow only:** **`benchmark_suite=`** + **`benchmark_attempt=`** on the **same line** as **`COVERAGE:`**; **`{EpicDir}`** is **`attempt-<nn>/shadow/<KEY>/`** ([`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md)).
3. Use the **same** **`benchmark_attempt=<r>`** as the prep step for this run index.

## Trigger (single message line)

```text
COVERAGE: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=<r>
```

## After completion

- Confirm **`.cursor/benchmark/runs/<SUITE_ID>/attempt-<nn>/shadow/<KEY>/`** includes **`<KEY>-coverage.json`** (and **`<KEY>-coverage.md`** if required by playbook).
- Optional: mirror **`run-*.json`** under **`attempt-<nn>/_machine/attempts/<KEY>/`** with **`phase`:** **`coverage`** for **`compare_runs.py`**.
- **`DONE.json`:** after the **last** **`CONTROL_HUB`** row for this run index, operator pastes the matching block from **`DONE_HANDOFF_PROMPT.md`** (**agent** writes **`DONE`** — see [**`DONE_HANDOFF_PROMPT.example.md`](./DONE_HANDOFF_PROMPT.example.md)**).
