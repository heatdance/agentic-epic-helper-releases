# Legacy: one session — prep + coverage (all triggers)

**Status:** **Legacy / optional.** Prefer **[`CONTROL_HUB.example.md`](./CONTROL_HUB.example.md)** + **[`session_EPIC-PREP.example.md`](./session_EPIC-PREP.example.md)** + **[`session_COVERAGE.example.md`](./session_COVERAGE.example.md)** (**one cold chat per phase row**) unless your **`variance_methodology`** deliberately keeps prep and coverage in the **same** session.

---

# Benchmark attempt — paste into **one** agent session

**Suite:** `example-suite-20260508`  
**Attempt:** `1` of `3`  
**Epic:** `CRT-639`

## Rules

1. Read [docs/benchmark-contract.md](../../../docs/benchmark-contract.md) and the relevant pipeline playbooks **before** executing triggers.
2. Use **benchmark shadow** only: every pipeline line below must include **`benchmark_suite=example-suite-20260508 benchmark_attempt=1`** (adjust values per manifest); durable output under **`attempt-01/shadow/<KEY>/`** ([`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md)).
3. One **run index** per folder; legacy pattern runs **multiple** triggers in **one** chat — allowed only when methodology says so.

## Triggers (in order)

Replace `<KEY>` with the epic key from the manifest.

```text
EPIC-PREP: <KEY> benchmark_suite=example-suite-20260508 benchmark_attempt=1
COVERAGE: <KEY> benchmark_suite=example-suite-20260508 benchmark_attempt=1
```

(If `modes` in `_manifest.json` includes `test_prep`, add `TEST-PREP:` with the same benchmark tokens.)

## After completion

1. Confirm all files exist under `.cursor/benchmark/runs/example-suite-20260508/attempt-01/shadow/<KEY>/`.
2. **Preferred hub flow:** operator pastes **[`DONE_HANDOFF_PROMPT.example.md`](./DONE_HANDOFF_PROMPT.example.md)** (suite-filled **`DONE_HANDOFF_PROMPT.md`**) so an **agent** authors **`DONE.json`** (see [**`DONE.example.json`](./DONE.example.json)** / [**`DONE.example.coverage_test.json`](./DONE.example.coverage_test.json)**). Legacy all-in-one: agent may write **`DONE.json`** in-session.
3. Optionally mirror **`run-*.json`** under **`attempt-01/_machine/`** if using **`compare_runs --suite-run-dir`**.
