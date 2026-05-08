# Benchmark shadow — hand off run index `<r>` (paste into shadow session for the agent)

**Audience:** Agent in a shadow session (continuation after the last **`CONTROL_HUB`** line for this run index, or one follow-up cold chat).  
**Operator:** Paste the filled **copy block** for this **`r`** from **`DONE_HANDOFF_PROMPT.md`** at suite root.

*Link targets below assume suite root* **`.cursor/benchmark/runs/<SUITE_ID>/`**.

---

## Copy block per run index (init fills `<r>`, `<nn>`, `<KEY>`, `<SUITE_ID>`, `<profile>`)

You are closing **hub benchmark** run index **`<r>`** for suite **`<SUITE_ID>`**, epic **`<KEY>`**, working directory **`.cursor/benchmark/runs/<SUITE_ID>/attempt-<nn>/`** (e.g. `r=1` → `attempt-01`).

**Manifest profile:** `<profile>`

### Your tasks

1. Verify durable files under **`attempt-<nn>/shadow/<KEY>/`** match the profile:
   - **`coverage` / `coverage_test`:** **`<KEY>-ref.json`**, **`<KEY>-coverage.json`**, **`<KEY>-coverage.md`** as applicable.
   - **`test` / `coverage_test`:** **`<KEY>-tests.json`**, **`<KEY>-tests.md`** per [test-prep pipeline](../../../pipelines/test-prep.md) and [benchmark-test-prep](../../test-bench/pipeline/benchmark-test-prep.md).
2. **Write** **`attempt-<nn>/DONE.json`** with **`artifacts[]`** paths **relative to `attempt-<nn>/`**. Schemas:
   - [DONE.example.json](../../templates/DONE.example.json) — coverage-only;
   - [DONE.example.coverage_test.json](../../templates/DONE.example.coverage_test.json) — prep + coverage + test.
3. Set **`suite_id`**, **`attempt`**, **`completed_at`**, **`modes_completed`** consistently with files on disk. If expected artifacts are missing, finish the pipeline work in shadow first, then complete **`DONE.json`**.

---

**Init note:** Generate one **copy block** per run **`1…N`** in **`DONE_HANDOFF_PROMPT.md`** at suite root — convention: **one file**, multiple blocks.
