# Shadow session — TEST-PREP (cold context)

**Suite:** `<SUITE_ID>`  
**Run index `<r>` / folder:** `attempt-<nn>` (e.g. `r=1` → `attempt-01`)  
**Epic:** `<KEY>`

## Default (CONTROL_HUB parity — one line)

Paste **one** message line (matches **Execution order** table in **`CONTROL_HUB.md`**):

```text
TEST-PREP: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=<r>
```

The agent runs the full **`test-prep`** playbook under shadow **`{EpicDir}`**; per-bundle work occurs **inside** this session as required by [`.cursor/pipelines/test-prep.md`](../../pipelines/test-prep.md).

## Rules

1. Read [`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md), [`.cursor/pipelines/test-prep.md`](../../pipelines/test-prep.md), and **[`benchmark-test-prep.md`](../test-bench/pipeline/benchmark-test-prep.md)**.
2. **`benchmark_suite=`** + **`benchmark_attempt=`** on the **same line** as **`TEST-PREP:`**.
3. Benchmark tokens route outputs to **`attempt-<nn>/shadow/<KEY>/`** ([`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md)).

## Optional — `map_only` (same single-line shape)

```text
TEST-PREP: <KEY> map_only=yes benchmark_suite=<SUITE_ID> benchmark_attempt=<r>
```

Requires **`{EpicDir}<KEY>-coverage.json`** from a prior **`COVERAGE:`** step with the **same** benchmark tokens.

## Optional — atomic `BENCHMARK-TEST-*` queue

For variance micro-steps, use **one message per queue row** — see **`benchmark-test-prep.md`**. Not the default CONTROL_HUB pattern.

## Closing this run index

**Operator** pastes the matching block from **`DONE_HANDOFF_PROMPT.md`**. **Agent** authors **`DONE.json`** once **`<KEY>-tests.json`** / **`<KEY>-tests.md`** satisfy test-prep completion and durable paths are clean (no stray **`/temp/`**).
