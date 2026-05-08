# Shadow session — EPIC-PREP only (cold context)

**Suite:** `20260508-ct01`
**Run index `1` / folder:** `attempt-01`
**Epic:** `CRT-639`

## Rules

1. Read [`docs/benchmark-contract.md`](../../../../../docs/benchmark-contract.md) and [`.cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md`](../../../coverage-bench/pipeline/benchmark-epic-prep.md) before executing.
2. **Shadow only:** include **`benchmark_suite=`** and **`benchmark_attempt=`** on the **same line** as the trigger; output under **`attempt-01/shadow/CRT-639/`** ([`docs/benchmark-contract.md`](../../../../../docs/benchmark-contract.md)).
3. **One run index per folder** — use **`1`** assigned to this session (matches **`attempt-01/`**).

## Trigger (single message line)

```text
EPIC-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=1
```

## After completion

- Confirm **`.cursor/benchmark/runs/20260508-ct01/attempt-01/shadow/CRT-639/`** has progressing prep artifacts (e.g. **`CRT-639-ref.json`** per playbook).
- **Operator:** after all phases for this run index finish, paste the suite’s **`DONE_HANDOFF_PROMPT.md`** block so the **agent** writes **`DONE.json`** — see [**`DONE_HANDOFF_PROMPT.example.md`**](../../../templates/DONE_HANDOFF_PROMPT.example.md).
