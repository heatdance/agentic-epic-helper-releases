# Benchmark suite — control hub

**Suite ID:** `20260508-ct01`
**Epic `<KEY>`:** `CRT-639`
**Profile:** `coverage_test`
**Runs `N`:** `3`
**Gold:** `.cursor/benchmark/data/CRT-639-gold.json` (canonical; pass `--gold-root` to tooling if you relocate gold)
**Variance methodology:** `fresh-session stochasticity` — must match `_manifest.json`

## This chat (control hub)

Use **this** conversation for:

- Checking off **Execution order** rows as cold sessions finish.
- **Combine step:** when **`N`** run indices all have **`DONE.json`**, stay in **this** chat and send **`finalize`** (the hub agent reads **`FINALIZE_PROMPT.md`**, verifies, compares, then writes **`.cursor/benchmark/run-results/<run-key>/report.md`** per that prompt) **or** paste **`FINALIZE_PROMPT.md`** here.

**Orchestration:** open a **new** cold chat per table row; paste the **single** line from the **Paste** column. Pipeline triggers run in those shadow chats under **`attempt-<nn>/`** — not as ad-hoc lines in the hub. **Each table row = one cold agent chat** (this suite uses fresh-session stochasticity).

## Rules (all shadow sessions)

1. Read [`docs/benchmark-contract.md`](../../../../docs/benchmark-contract.md) and the relevant playbooks before triggers.
2. **Same line** carries tokens: `benchmark_suite=20260508-ct01 benchmark_attempt=<r>` with `EPIC-PREP:`, `COVERAGE:`, or `TEST-PREP:` as applicable.
3. **Shadow EpicDir:** benchmark tokens route durable output to **`attempt-<nn>/shadow/CRT-639/`** per [`docs/benchmark-contract.md`](../../../../docs/benchmark-contract.md).
4. **Run index `<r>`** matches folder **`attempt-<nn>/`** (e.g. `r=1` → `attempt-01`).

## Execution order (cold sessions)

**Global session counter S** increments for **each new chat**. Every **Paste** cell is a **single message line** — same shape for prep, coverage, and test-prep.

For **each** `r` from **1** to **3** — **three** cold sessions per run (prep → coverage → test-prep):

| S | Purpose | Paste (single message line) |
|---|---------|----------------------------|
| 1 | Prep run **1** | `EPIC-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=1` |
| 2 | Coverage run **1** | `COVERAGE: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=1` |
| 3 | Test-prep run **1** | `TEST-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=1` |
| 4 | Prep run **2** | `EPIC-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=2` |
| 5 | Coverage run **2** | `COVERAGE: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=2` |
| 6 | Test-prep run **2** | `TEST-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=2` |
| 7 | Prep run **3** | `EPIC-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=3` |
| 8 | Coverage run **3** | `COVERAGE: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=3` |
| 9 | Test-prep run **3** | `TEST-PREP: CRT-639 benchmark_suite=20260508-ct01 benchmark_attempt=3` |

After **Prep run r**, expect **`shadow/CRT-639/CRT-639-ref.json`** under **`attempt-<nn>/`**. After **Coverage run r**, expect **`-coverage.json`** / **`-coverage.md`**. After **Test-prep run r**, expect **`-tests.json`** / **`-tests.md`**.

The **`TEST-PREP:`** line runs the full test-prep playbook for that epic under shadow **`{EpicDir}`** (bundles may execute **inside** that session per [`.cursor/rules/pipeline-router.mdc`](../../../rules/pipeline-router.mdc)).

## After each run index

When **prep** + **coverage** + **TEST-PREP** have finished for run **`r`**, paste the matching **copy block** from suite-root **`DONE_HANDOFF_PROMPT.md`** into a shadow chat (same session as the last pipeline step or a short follow-up cold chat). The shadow **agent** completes **`attempt-<nn>/DONE.json`**.

## When all runs are done (control hub)

In **this** hub chat, type **`finalize`** — the agent loads **`FINALIZE_PROMPT.md`**, runs verify/compare, and authors **`.cursor/benchmark/run-results/<run-key>/report.md`** — **or** paste **`FINALIZE_PROMPT.md`** here.
