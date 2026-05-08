# Shadow session — COVERAGE only (cold context)

**Suite:** `20260508-ct01`
**Run index `2` / folder:** `attempt-02`
**Epic:** `CRT-639`

## Rules

1. Read [`docs/benchmark-contract.md`](../../../../../docs/benchmark-contract.md) and [`.cursor/benchmark/coverage-bench/pipeline/benchmark-coverage.md`](../../../coverage-bench/pipeline/benchmark-coverage.md) before executing.
2. **Shadow only:** **`benchmark_suite=`** + **`benchmark_attempt=`** on the **same line** as **`COVERAGE:`**; **`{EpicDir}`** is **`attempt-02/shadow/CRT-639/`** ([`docs/benchmark-contract.md`](../../../../../docs/benchmark-contract.md)).
3. Use the **same** **`benchmark_attempt=2`** as the prep step for this run index.

## Trigger (single message line)

```text
COVERAGE: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=2
```

## After completion

- Confirm **`attempt-02/shadow/CRT-639/`** includes **`CRT-639-coverage.json`** (and **`CRT-639-coverage.md`** if required by playbook).
- Optional: mirror **`run-*.json`** under **`attempt-02/_machine/attempts/CRT-639/`** with **`phase`:** **`coverage`** for **`compare_runs.py`**.
- **`DONE.json`:** after the **last** **`CONTROL_HUB`** row for this run index, operator pastes the matching block from **`DONE_HANDOFF_PROMPT.md`**.
