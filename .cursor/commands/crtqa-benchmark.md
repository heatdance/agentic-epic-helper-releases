---
description: Initialize and verify benchmark shadow suites (questionnaire, CONTROL_HUB, per-session prompts, DONE) for hub runs
---

# /crtqa-benchmark

Operator- or agent-driven workflow for **benchmark shadow** runs per [docs/benchmark-contract.md](../../docs/benchmark-contract.md) and [`.cursor/benchmark/README.md`](../benchmark/README.md).

## Purpose

- After a **mandatory questionnaire**, create a suite under `.cursor/benchmark/runs/<suite_id>/` with **`_manifest.json`**, **`CONTROL_HUB.md`** (**one paste line per row**, including **`TEST-PREP:`** for test profiles — same shape as prep/coverage), **`DONE_HANDOFF_PROMPT.md`** (per-run **`DONE.json`** instructions for **agents**), **`FINALIZE_PROMPT.md`** (control hub combine only), and per-run **`attempt-<nn>/`** phase stubs.
- **Verify** filesystem handoff: each **`attempt-<nn>/DONE.json`** + **`artifacts[]`** before **`compare_runs.py`** / validators.
- **Vendor-neutral:** same layout works outside Cursor.

## Terminology

- **`benchmark_attempt`** = **run index** (`1…N`). It selects folder **`attempt-<nn>/`** and **`EpicDir`** under **`shadow/<KEY>/`**.
- **One cold chat per orchestrated row** (prep, coverage, or test-prep phase—or each atomic **`BENCHMARK-TEST-*`** row). Multiple sequential **cold sessions** reuse the **same** `benchmark_attempt` when they belong to the same run; tokens on **every** line remain **`benchmark_suite=<suite_id> benchmark_attempt=<r>`**.
- **Control hub** — the Cursor chat **where `/crtqa-benchmark` ran** coordinates the suite (creates files, tracks progress, runs **finalize**). It does **not** substitute for cold shadow sessions.

## Before init (mandatory)

The answering agent **must** collect these from the operator **before** writing suite files (use **Ask** / explicit questions if values are missing):

| Input | Notes |
|-------|--------|
| **Benchmark profile** | **`coverage`** — `EPIC-PREP` + `COVERAGE` per run. **`test`** — hub **`TEST-PREP`** / atomic queue only (see [benchmark-test-prep.md](../benchmark/test-bench/pipeline/benchmark-test-prep.md)); no prep/coverage unless operator adds them. **`coverage_test`** — prep + coverage per run, then test-prep for each run (same tokens throughout). |
| **Number of runs `N`** | Maps to **`attempts`** in **`_manifest.json`** and to **`benchmark_attempt=1…N`**. |
| **Epic key(s)** | Jira epic(s), e.g. `CRT-639`. Primary key drives paths **`<KEY>`**; list all in manifest **`epics[]`**. |
| **Gold** | Default: **`.cursor/benchmark/data/<KEY>-gold.json`**. If elsewhere, set manifest **`gold.prep`** / **`gold.coverage`** and pass **`--gold-root`** to **`compare_runs.py`** when aggregating (see [`data/README.md`](../benchmark/data/README.md)). |
| **`variance_methodology`** | Must match how sessions are isolated — see [WS-B](../../automation/temp/benchmark-rework-analysis/WS-B-findings.md): **`fresh-session stochasticity`** vs **`deterministic replay`**. |
| **`suite_id`** (optional) | Path-safe id; if omitted, agent picks e.g. **`YYYYMMDD-abc`**. |

**Profile → `_manifest.json` `modes` (convention):**

| Profile | `modes` |
|---------|---------|
| `coverage` | `["epic_prep", "coverage"]` |
| `test` | `["test_prep"]` |
| `coverage_test` | `["epic_prep", "coverage", "test_prep"]` |

Echo answers back to the operator, then proceed to **Init**.

## Layout (normative)

```
.cursor/benchmark/runs/<suite_id>/
  CONTROL_HUB.md          # suite orchestration — ordered cold sessions (from templates/CONTROL_HUB.example.md)
  DONE_HANDOFF_PROMPT.md   # from templates/DONE_HANDOFF_PROMPT.example.md — copy blocks pasted in shadow for DONE.json
  FINALIZE_PROMPT.md       # from templates/FINALIZE_PROMPT.example.md (control hub only — verify, compare)
  _manifest.json           # templates/_manifest.example.json (+ optional report_run_key for report directory)
  attempt-01/
    PROMPT-prep.md         # when profile includes prep — from session_EPIC-PREP.example.md
    PROMPT-coverage.md     # when profile includes coverage — from session_COVERAGE.example.md
    PROMPT-test.md         # when profile includes test_prep — from session_TEST-PREP.example.md
    DONE.json               # completion marker (templates/DONE.example.json or DONE.example.coverage_test.json)
    shadow/<KEY>/           # pipeline durable outputs (EpicDir)
    _machine/attempts/<KEY>/run-*.json   # optional snapshots for compare_runs --suite-run-dir
  attempt-02/
    ...
  _aggregate/
    crossref/               # compare_runs output when using --suite-run-dir

# narratives + pipeline queue — separate from suite folder (finalize §4):

.cursor/benchmark/run-results/<run-key>/
  report.md                 # run-key = _manifest.report_run_key || suite_id
  pipeline-delta-queue.json # optional — templates/pipeline-delta-queue.example.json
```

## Init (agent steps)

1. Complete **Before init (mandatory)**; echo **`suite_id`**, profile, **`N`**, **`KEY`**, gold path, variance.
2. Create **`.cursor/benchmark/runs/<suite_id>/`**.
3. Copy [`.cursor/benchmark/templates/_manifest.example.json`](../benchmark/templates/_manifest.example.json) → **`_manifest.json`**; set **`suite_id`**, **`epics`**, **`modes`** (from profile table), **`attempts`** = **`N`**, **`gold`**, **`tokens`**, **`variance_methodology`**, **`created_at`**. Optional **`report_run_key`** if the report folder under **`run-results/`** should differ from **`suite_id`** ([`run-results/README.md`](../benchmark/run-results/README.md)).
4. Write **`CONTROL_HUB.md`** from [CONTROL_HUB.example.md](../benchmark/templates/CONTROL_HUB.example.md): fill variables; for **`coverage_test`** / **`test`**, include **`TEST-PREP: <KEY> benchmark_suite=<suite_id> benchmark_attempt=<r>`** as literal **Paste** rows (same three-column table as prep/coverage). Use [benchmark-test-prep.md](../benchmark/test-bench/pipeline/benchmark-test-prep.md) **only** when expanding an **optional** atomic multi-row sequence.
5. Write **`DONE_HANDOFF_PROMPT.md`** from [DONE_HANDOFF_PROMPT.example.md](../benchmark/templates/DONE_HANDOFF_PROMPT.example.md): one filled **copy block** per **`r`** in **`1…N`** (suite root paths; **`profile`**, **`KEY`**, **`suite_id`**).
6. Copy [FINALIZE_PROMPT.example.md](../benchmark/templates/FINALIZE_PROMPT.example.md) → **`FINALIZE_PROMPT.md`** with **`suite_id`**, **`KEY`**, and profile-dependent commands filled in.
7. For each **`r`** in **`1…N`**, create **`attempt-<nn>/`** (zero-pad **`r`**), add **`PROMPT-prep.md`** / **`PROMPT-coverage.md`** / **`PROMPT-test.md`** as required from [session_EPIC-PREP.example.md](../benchmark/templates/session_EPIC-PREP.example.md), [session_COVERAGE.example.md](../benchmark/templates/session_COVERAGE.example.md), [session_TEST-PREP.example.md](../benchmark/templates/session_TEST-PREP.example.md).
8. Ensure **`.cursor/benchmark/data/`** exists; operators place **`<KEY>-gold.json`** or use custom **`gold`** paths.
9. In the chat reply after suite creation, include **[`## What to do next (operator)`](#what-to-do-next-operator)** below (verbatim outline or summarized) so the operator has the three-step flow.

## What to do next (operator)

After init, answer the questionnaire only once; thereafter **paste prompts** into the right chat (**cold shadow** vs **this control hub**). Minimal input: triggers from **`CONTROL_HUB.md`**, handoff blocks from **`DONE_HANDOFF_PROMPT.md`**, then **finalize** here.

### 1. Execution order (`CONTROL_HUB.md`)

- Open **`CONTROL_HUB.md`** in the suite folder.
- **Each table row:** open a **new** cold agent chat; paste exactly **one** message line (**Paste** column) — prep, coverage, and **`TEST-PREP:`** all use this pattern.

### 2. Run-index handoffs (`DONE_HANDOFF_PROMPT.md`)

- After **all rows for run index `r`** are done (prep / coverage / test per profile), open a shadow chat (or continue the last one) and paste the **matching copy block** for **`r`** from **`DONE_HANDOFF_PROMPT.md`**.
- Shadow **agents** produce **`attempt-<nn>/DONE.json`** for **each run index** **`r = 1…N`** until every run index has a **`DONE`** file.

### 3. Combine (control hub — this chat)

- When **`DONE.json`** exists for **`N`** runs: in **this** control hub chat, use **Agent mode**, type **`finalize`** (hub agent reads **`FINALIZE_PROMPT.md`**, verifies, compares; writes **`.cursor/benchmark/run-results/<run-key>/report.md`** — avoid Plan mode for this step) **or** paste **`FINALIZE_PROMPT.md`** once.

## Verify (agent steps)

1. For each **`attempt-<nn>/`**, check **`DONE.json`** exists and **`artifacts[]`** paths exist (relative to that attempt folder or repo-root paths if used consistently).
2. **`_machine`/`run-*.json`** is **optional**. Without it, **`compare_runs.py --suite-run-dir`** reads **`attempt-<nn>/shadow/<KEY>/`** (`*-ref.json`, `*-coverage.json`, `*-tests.json`) per [**`docs/benchmark-contract.md`**](../../docs/benchmark-contract.md).
3. If using **`_machine`**, wrappers should include **`phase`** (**`prep`** \| **`coverage`** \| **`test`**) matching [compare_runs.py](../benchmark/coverage-bench/scripts/compare_runs.py) hub discovery when present.
4. Run [`automation/tools/benchmark_verify.py`](../../automation/tools/benchmark_verify.py) (repo root); fix failures before aggregate.

## Finalize / aggregate

After **Verify** passes (**Agent mode hub** preferred), execute **`FINALIZE_PROMPT.md`** (suite folder), or equivalently:

- **`python automation/tools/benchmark_verify.py --suite-dir .cursor/benchmark/runs/<suite_id> --strict-manifest`**
- **Aggregate / compare:** [`benchmark_aggregate.py`](../../automation/tools/benchmark_aggregate.py) runs **`compare_runs.py`** kinds implied by **`_manifest.json` `modes`** (prep / coverage / test). Optional **`--gold-root`** forwarded to **`compare_runs`**.
- **One-shot helper:** **`python automation/tools/benchmark_finalize_hub.py --suite-dir .cursor/benchmark/runs/<suite_id> [--gold-root <dir>]`** (runs verify strict + aggregate).
- **Test metrics:** **`compare_runs.py --kind test`** (same **`--suite-run-dir`** and gold flags) writes **`*-test-metrics.json`** under **`_aggregate/crossref/`**.
- Author **`report.md`** and optional **`pipeline-delta-queue.json`** under **`.cursor/benchmark/run-results/<run-key>/`** (`run-key` from **`FINALIZE_PROMPT.md`** / manifest) — section order [**`run-results/README.md`**](../benchmark/run-results/README.md); cite **`runs/<suite_id>/_aggregate/crossref/*.json`** paths, not pasted blobs.

Examples:

```bash
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic <KEY> --kind prep --suite-run-dir .cursor/benchmark/runs/<suite_id>
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic <KEY> --kind coverage --suite-run-dir .cursor/benchmark/runs/<suite_id>
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic <KEY> --kind test --suite-run-dir .cursor/benchmark/runs/<suite_id>
```

**`--suite-run-dir`** writes crossref under **`_aggregate/crossref/`**.

## References

- Templates: [`CONTROL_HUB.example.md`](../benchmark/templates/CONTROL_HUB.example.md), [`DONE_HANDOFF_PROMPT.example.md`](../benchmark/templates/DONE_HANDOFF_PROMPT.example.md), [`FINALIZE_PROMPT.example.md`](../benchmark/templates/FINALIZE_PROMPT.example.md), `session_*.example.md`
- [BENCHMARK_RUNBOOK.md](../benchmark/BENCHMARK_RUNBOOK.md) — **§1 hub (default)**; legacy **`BENCHMARK:`** appendix
- [HOW-TO.md](../../HOW-TO.md) — benchmark flow (operator-facing)
