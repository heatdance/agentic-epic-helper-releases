# Benchmark shadow — hand off per run index (paste into shadow session for the agent)

**Audience:** Agent in a shadow session (continuation after the last **`CONTROL_HUB`** line for this run index, or one follow-up cold chat).
**Operator:** Paste the filled **copy block** for run index **`r`** below.

*Link targets assume suite root* **`.cursor/benchmark/runs/20260508-ct01/`**.

---

## Run index `r = 1` (`attempt-01`)

You are closing **hub benchmark** run index **1** for suite **`20260508-ct01`**, epic **`CRT-639`**, working directory **`.cursor/benchmark/runs/20260508-ct01/attempt-01/`**.

**Manifest profile:** `coverage_test`

### Your tasks

1. Verify durable files under **`attempt-01/shadow/CRT-639/`** match the profile:
   - **`CRT-639-ref.json`**, **`CRT-639-coverage.json`**, **`CRT-639-coverage.md`**
   - **`CRT-639-tests.json`**, **`CRT-639-tests.md`** per [test-prep pipeline](../../../pipelines/test-prep.md) and [benchmark-test-prep](../../test-bench/pipeline/benchmark-test-prep.md).
2. **Write** **`attempt-01/DONE.json`** with **`artifacts[]`** paths **relative to `attempt-01/`**. Schema: [DONE.example.coverage_test.json](../../templates/DONE.example.coverage_test.json).
3. Set **`suite_id`**, **`attempt`**, **`completed_at`**, **`modes_completed`** consistently with files on disk. If expected artifacts are missing, finish the pipeline work in shadow first, then complete **`DONE.json`**.

---

## Run index `r = 2` (`attempt-02`)

You are closing **hub benchmark** run index **2** for suite **`20260508-ct01`**, epic **`CRT-639`**, working directory **`.cursor/benchmark/runs/20260508-ct01/attempt-02/`**.

**Manifest profile:** `coverage_test`

### Your tasks

1. Verify durable files under **`attempt-02/shadow/CRT-639/`** match the profile:
   - **`CRT-639-ref.json`**, **`CRT-639-coverage.json`**, **`CRT-639-coverage.md`**
   - **`CRT-639-tests.json`**, **`CRT-639-tests.md`** per [test-prep pipeline](../../../pipelines/test-prep.md) and [benchmark-test-prep](../../test-bench/pipeline/benchmark-test-prep.md).
2. **Write** **`attempt-02/DONE.json`** with **`artifacts[]`** paths **relative to `attempt-02/`**. Schema: [DONE.example.coverage_test.json](../../templates/DONE.example.coverage_test.json).
3. Set **`suite_id`**, **`attempt`**, **`completed_at`**, **`modes_completed`** consistently with files on disk. If expected artifacts are missing, finish the pipeline work in shadow first, then complete **`DONE.json`**.

---

## Run index `r = 3` (`attempt-03`)

You are closing **hub benchmark** run index **3** for suite **`20260508-ct01`**, epic **`CRT-639`**, working directory **`.cursor/benchmark/runs/20260508-ct01/attempt-03/`**.

**Manifest profile:** `coverage_test`

### Your tasks

1. Verify durable files under **`attempt-03/shadow/CRT-639/`** match the profile:
   - **`CRT-639-ref.json`**, **`CRT-639-coverage.json`**, **`CRT-639-coverage.md`**
   - **`CRT-639-tests.json`**, **`CRT-639-tests.md`** per [test-prep pipeline](../../../pipelines/test-prep.md) and [benchmark-test-prep](../../test-bench/pipeline/benchmark-test-prep.md).
2. **Write** **`attempt-03/DONE.json`** with **`artifacts[]`** paths **relative to `attempt-03/`**. Schema: [DONE.example.coverage_test.json](../../templates/DONE.example.coverage_test.json).
3. Set **`suite_id`**, **`attempt`**, **`completed_at`**, **`modes_completed`** consistently with files on disk. If expected artifacts are missing, finish the pipeline work in shadow first, then complete **`DONE.json`**.
