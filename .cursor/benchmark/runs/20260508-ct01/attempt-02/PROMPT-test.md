# Shadow session — TEST-PREP (cold context)

**Suite:** `20260508-ct01`
**Run index `2` / folder:** `attempt-02`
**Epic:** `CRT-639`

## Default (CONTROL_HUB parity — one line)

```text
TEST-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=2
```

The agent runs the full **`test-prep`** playbook under shadow **`{EpicDir}`**; per-bundle work occurs **inside** this session as required by [`.cursor/pipelines/test-prep.md`](../../../../pipelines/test-prep.md).

## Rules

1. Read [`docs/benchmark-contract.md`](../../../../../docs/benchmark-contract.md), [`.cursor/pipelines/test-prep.md`](../../../../pipelines/test-prep.md), and **[`benchmark-test-prep.md`](../../../test-bench/pipeline/benchmark-test-prep.md)**.
2. **`benchmark_suite=`** + **`benchmark_attempt=`** on the **same line** as **`TEST-PREP:`**.
3. Benchmark tokens route outputs to **`attempt-02/shadow/CRT-639/`** ([`docs/benchmark-contract.md`](../../../../../docs/benchmark-contract.md)).

## Optional — `map_only` (same single-line shape)

```text
TEST-PREP: CRT-639 map_only=yes benchmark_suite=20260508-ct01 benchmark_attempt=2
```

Requires **`CRT-639-coverage.json`** from a prior **`COVERAGE:`** step with the **same** benchmark tokens.

## Optional — atomic `BENCHMARK-TEST-*` queue

For variance micro-steps, use **one message per queue row** — see **`benchmark-test-prep.md`**. Not the default CONTROL_HUB pattern.

## Closing this run index

**Operator** pastes the matching block from **`DONE_HANDOFF_PROMPT.md`**. **Agent** authors **`DONE.json`** once **`CRT-639-tests.json`** / **`CRT-639-tests.md`** satisfy test-prep completion.
