# Shadow session — EPIC-PREP only (cold context)

**Suite:** `<SUITE_ID>`  
**Run index `<r>` / folder:** `attempt-<nn>` (e.g. `r=1` → `attempt-01`)  
**Epic:** `<KEY>`

## Rules

1. Read [`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md) and [`.cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md`](../coverage-bench/pipeline/benchmark-epic-prep.md) before executing.
2. **Shadow only:** include **`benchmark_suite=`** and **`benchmark_attempt=`** on the **same line** as the trigger; output under **`attempt-<nn>/shadow/<KEY>/`** ([`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md)).
3. **One run index per folder** — use the **`r`** assigned to this session (matches **`attempt-<nn>/`**).

## Trigger (single message line)

```text
EPIC-PREP: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=<r>
```

## After completion

- Confirm **`.cursor/benchmark/runs/<SUITE_ID>/attempt-<nn>/shadow/<KEY>/`** has progressing prep artifacts (e.g. **`<KEY>-ref.json`** per playbook).
- **Operator:** after all phases for this run index finish, paste the suite’s **`DONE_HANDOFF_PROMPT.md`** block so the **agent** writes **`DONE.json`** — see [**`DONE_HANDOFF_PROMPT.example.md`](./DONE_HANDOFF_PROMPT.example.md)**.
