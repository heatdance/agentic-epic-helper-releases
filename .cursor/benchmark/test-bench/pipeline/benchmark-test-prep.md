# Benchmark test-prep (hub default + optional atomic queue)

These tokens are **benchmark-only**. They are **not** registered in `AGENTS.md` or **`.cursor/rules/pipeline-router.mdc`**. Operators and agents use them when driving **`test-bench/runs/run-<suite_id>/support/QUEUE.md`** (one message per row), or when expanding **hub** **`CONTROL_HUB.md`** (suite under **`.cursor/benchmark/runs/<suite_id>/`**) with **optional** multi-row atomic steps ([§ Optional atomic queue](#optional-atomic-benchmark-test--queue)).

Prerequisite: **[`.cursor/pipelines/test-prep.md`](../../../pipelines/test-prep.md)** and **[`epics/templates/tests-ref.json`](../../../../epics/templates/tests-ref.json)**.

Hub suite init: **[`/crtqa-benchmark`](../../../commands/crtqa-benchmark.md)** — default **one `TEST-PREP:` line per run index** in **`CONTROL_HUB.md`**; agents close each run with **`DONE_HANDOFF_PROMPT.md`** ( **`DONE.json`** written by the agent, not by hand).

---

## Hub shadow default (CONTROL_HUB)

For **`.cursor/benchmark/runs/<suite_id>/`** shadow suites, the default orchestration matches **prep** and **coverage** rows:

- **One cold session per run index** for test-prep = **one** pasted line:  
  **`TEST-PREP: <EPIC> benchmark_suite=<suite_id> benchmark_attempt=<n>`**  
  (same-line **`benchmark_*`** tokens per [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md).)

- The **router** dispatches to the full **`test-prep`** playbook; **per-bundle subprocesses** may run **inside** that session (same as production **`TEST-PREP:`** behavior).

- Optional **single-line** variant: **`map_only=yes`** when you only need the map step under hub **`{EpicDir}`** (requires prior **`COVERAGE:`** with matching tokens).

This default does **not** require **`BENCHMARK-TEST-*`** queue rows.

---

## Relationship to production `TEST-PREP:`

Production **`TEST-PREP: CRT-639`** is **one** chat trigger that plans once and may run **many** bundle subprocesses internally.

## Optional: Atomic `BENCHMARK-TEST-*` queue

Use this when you want **one cold session per** map-only step, **per bundle**, or finalize — e.g. legacy **`test-bench/runs/.../QUEUE.md`** or an **expanded** **`CONTROL_HUB.md`** (each row still **one** paste line). Each **`BENCHMARK-TEST-BUNDLE`** line is a **separate message**; the agent MUST still obey test-prep **MUST / MUST NOT** (no invented Jira steps; one bundle’s full draft prose per completion for that bundle).

---

## Durable paths (`{EpicDir}`)

When **`benchmark_suite=<suite_id>`** **and** **`benchmark_attempt=<n>`** appear on the **same line** as **`TEST-PREP:`** — **matching [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md)**:

```
{EpicDir} = .cursor/benchmark/runs/<suite_id>/attempt-<nn>/shadow/<EPIC>/
```

Completion checks (**`-tests.json`**, **`-tests.md`**, **`temp/`**) apply under **`{EpicDir}`** only; **do not** require matching files under **`epics/<EPIC>/`** for that trigger line.

If **either** benchmark token is omitted, **`{EpicDir}`** is **`epics/<EPIC>/`** (production).

---

## Tokens (atomic / queue expansion)

| Token pattern | Queue `type` | Agent obeys |

|---------------|--------------|-------------|

| **`BENCHMARK-TEST-MAPONLY: <EPIC> suite_run=<suite_id>`** *(legacy orchestration)* | `test_map_only` | **`TEST-PREP: <EPIC>`** — production **`epics/<EPIC>/`** unless the line adds **`benchmark_suite=`** / **`benchmark_attempt=`** |

| **`BENCHMARK-TEST-MAPONLY: <EPIC> benchmark_suite=<id> benchmark_attempt=<n>`** *(hub)* | `test_map_only` | **`TEST-PREP: <EPIC> map_only=yes benchmark_suite=<id> benchmark_attempt=<n>`**. Output **`{EpicDir}<EPIC>-tests.json`** with **`sources.map_only`** true and **`sources.coverage_loaded`** true (requires **`{EpicDir}<EPIC>-coverage.json`** from a prior **`COVERAGE:`** line with the **same** benchmark tokens). |

| **`BENCHMARK-TEST-BUNDLE: <EPIC> suite_run=<suite_id> bundle=<tb-XXX>`** | `test_bundle` | **`TEST-PREP:`** scoped to **`bundle=`** — add hub benchmark tokens **whenever** the suite uses **`…/runs/<suite_id>/attempt-<nn>/shadow/`**. |

| **`BENCHMARK-TEST-FINALIZE: suite_run=<suite_id>`** or **`benchmark_suite=<suite_id> benchmark_attempt=<n>`** per queue convention | `test_finalize` | Ensure **`-tests.md`** exists and aligns with **`-tests.json`** for **every epic** under the benchmark run (**`{EpicDir}`** each); housekeeping per test-prep (e.g. no **`/temp/`** in durable paths). |

Use **`benchmark_suite`** / **`benchmark_attempt`** consistently **across PREP → COVERAGE → TEST-PREP** for a hub attempt.

---

## Completion checklist (agent or SDK)

Resolve **`{EpicDir}`** from the **`TEST-PREP:`** line (benchmark tokens vs production).

Before advancing **`support/progress.json`** (or **`DONE.json`** in hub layout), confirm **durable artifacts under `{EpicDir}`**:

- **`test_map_only`**: **`-tests.json`** exists; **`sources.map_only`** is **true**; **`sources.coverage_loaded`** is **true**.

- **`test_bundle`**: **`test_bundles[]`** contains the step’s **`bundle_id`** with **`authoring.subprocess_completed`** **true**.

- **`test_finalize`**: **`-tests.json`** and **`-tests.md`** exist for every epic in the suite metadata / queue.

For the **default** single-line hub **`TEST-PREP:`**, apply the **full** test-prep completion expectations from [`.cursor/pipelines/test-prep.md`](../../../pipelines/test-prep.md) under **`{EpicDir}`** before the operator pastes **`DONE_HANDOFF_PROMPT.md`** for that run index.

Skip checks only when deliberately accepting an incomplete run (e.g. debugging).

---

## See also

- [`BENCHMARK_RUNBOOK.md`](../../BENCHMARK_RUNBOOK.md) — defaults + copy-paste flow

- **[`.cursor/benchmark/README.md`](../../README.md)** — hub layout + git hygiene

- **[`docs/benchmark-contract.md`](../../../../docs/benchmark-contract.md)**
