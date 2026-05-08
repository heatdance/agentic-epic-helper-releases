# Benchmark suite — control hub

**Suite ID:** `<SUITE_ID>`  
**Epic `<KEY>`:** `<KEY>`  
**Profile:** `<coverage | test | coverage_test>`  
**Runs `N`:** `<N>`  
**Gold:** `<path or default .cursor/benchmark/data/<KEY>-gold.json>`  
**Variance methodology:** `<fresh-session stochasticity | deterministic replay>` — must match `_manifest.json`  

## This chat (control hub)

Use **this** conversation for:

- Checking off **Execution order** rows as cold sessions finish.
- **Combine step:** when **`N`** run indices all have **`DONE.json`**, stay in **this** chat and send **`finalize`** (the hub agent reads **`FINALIZE_PROMPT.md`**, verifies, compares, then writes **`.cursor/benchmark/run-results/<run-key>/report.md`** per that prompt) **or** paste **`FINALIZE_PROMPT.md`** here.

**Orchestration:** open a **new** cold chat per table row; paste the **single** line from the **Paste** column. Pipeline triggers run in those shadow chats under **`attempt-<nn>/`** — not as ad-hoc lines in the hub. **Each table row = one cold agent chat** unless **`variance_methodology`** is **deterministic replay**.

## Rules (all shadow sessions)

1. Read [`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md) and the relevant playbooks before triggers.
2. **Same line** carries tokens: `benchmark_suite=<SUITE_ID> benchmark_attempt=<r>` with `EPIC-PREP:`, `COVERAGE:`, or `TEST-PREP:` as applicable.
3. **Shadow EpicDir:** benchmark tokens route durable output to **`attempt-<nn>/shadow/<KEY>/`** per [`docs/benchmark-contract.md`](../../../docs/benchmark-contract.md).
4. **Run index `<r>`** matches folder **`attempt-<nn>/`** (e.g. `r=1` → `attempt-01`).

## Execution order (cold sessions)

Fill the table during init. **Global session counter S** increments for **each new chat**. Every **Paste** cell is a **single message line** — same shape for prep, coverage, and test-prep.

### Profile `coverage`

For **each** `r` from **1** to **`N`**:

| S | Purpose | Paste (single message line) |
|---|---------|----------------------------|
| … | Prep run **r** | `EPIC-PREP: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=r` |
| … | Coverage run **r** | `COVERAGE: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=r` |

(Replace **`r`** with the numeral **1**, **2**, … when generating the real suite.)

After **Prep run r**, expect **`shadow/<KEY>/<KEY>-ref.json`** under **`attempt-<nn>/`**. After **Coverage run r**, expect **`-coverage.json`** / **`-coverage.md`**.

### Profile `coverage_test`

For **each** `r` from **1** to **`N`** — **three** cold sessions per run (prep → coverage → test-prep):

| S | Purpose | Paste (single message line) |
|---|---------|----------------------------|
| … | Prep run **r** | `EPIC-PREP: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=r` |
| … | Coverage run **r** | `COVERAGE: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=r` |
| … | Test-prep run **r** | `TEST-PREP: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=r` |

The **`TEST-PREP:`** line runs the full test-prep playbook for that epic under shadow **`{EpicDir}`** (bundles may execute **inside** that session per [`.cursor/rules/pipeline-router.mdc`](../../rules/pipeline-router.mdc)).

### Profile `test` only

For **each** `r` **1…N**:

| S | Purpose | Paste (single message line) |
|---|---------|----------------------------|
| … | Test-prep run **r** | `TEST-PREP: <KEY> benchmark_suite=<SUITE_ID> benchmark_attempt=r` |

### Atomic queue (advanced, optional)

If you need **one cold session per map / bundle / finalize** instead of one **`TEST-PREP:`** row, expand **test** steps into **multiple** table rows; each **Paste** column is still exactly **one** line. Patterns: **[`benchmark-test-prep.md`](../test-bench/pipeline/benchmark-test-prep.md)** (`BENCHMARK-TEST-MAPONLY:`, `BENCHMARK-TEST-BUNDLE:`, …). Keep **`benchmark_suite`** / **`benchmark_attempt`** on every line.

## After each run index

When **prep** (if any) + **coverage** (if any) + **TEST-PREP** (if any) have finished for run **`r`**, paste the matching **copy block** from suite-root **`DONE_HANDOFF_PROMPT.md`** into a shadow chat (same session as the last pipeline step or a short follow-up cold chat). The shadow **agent** completes **`attempt-<nn>/DONE.json`** using [`DONE_HANDOFF_PROMPT.example.md`](./DONE_HANDOFF_PROMPT.example.md) as the template for those blocks.

## When all runs are done (control hub)

In **this** hub chat, type **`finalize`** — the agent loads **`FINALIZE_PROMPT.md`**, runs verify/compare, and authors **`.cursor/benchmark/run-results/<run-key>/report.md`** (see prompt for **`run-key`**) — **or** paste **`FINALIZE_PROMPT.md`** here. Source template: [`FINALIZE_PROMPT.example.md`](./FINALIZE_PROMPT.example.md).
