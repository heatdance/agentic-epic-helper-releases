# Benchmark runner: COVERAGE variance

**Trigger**: user message starts with **`BENCHMARK-COVERAGE:`** and includes a Jira **Epic key** (e.g. `BENCHMARK-COVERAGE: CRT-639 repo=myworkspace/dxtrade-xt runs=3`).

**Not** in [`.cursor/rules/pipeline-router.mdc`](../../rules/pipeline-router.mdc). Execute when the operator asked you to follow this playbook (see [`../HOW-TO.md`](../HOW-TO.md)).

**Delegate**: Perform the **same steps** as [`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md) for each iteration—prerequisite **`{EpicDir}<KEY>-ref.json`**, outputs **`-coverage.json`** / **`-coverage.md`**, **`{EpicDir}temp/`** deleted, no **`/temp/`** in durable files. **`{EpicDir}`** resolves per [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md) when **`benchmark_suite` + benchmark_attempt`** are present.

**Scope**: **one Epic key** per invocation. Optional on the same line:

- **`runs=<N>`** — default **1**; cap at **20** unless the user explicitly overrides in the same message.
- **`repo=WORKSPACE/REPO_SLUG`** — pass through (production semantics).
- **`focus=...`** — free-text verification focus (production semantics).

---

## Preconditions

Same as [`coverage.md`](../../pipelines/coverage.md). If **`{EpicDir}<KEY>-ref.json`** is missing, **stop** and tell the user to run **`BENCHMARK-EPIC-PREP:`** (hub or legacy as appropriate) or **`EPIC-PREP:`** first.

**Production parity (delegated playbook)**: [`coverage.md`](../../pipelines/coverage.md) defines deterministic **`coverage_matrix[].id`**, a **`supporting` vs `out_of_epic`** decision ladder (phase **4**), verbatim **primary focus** in the first substantive Smart Checklist **`##`** block (phases **8** / **14**), optional-scenario discipline (phases **9** / **11**), phase **5** snippet enrichment rules tied to EPIC-PREP **3b**/**8**, and phase **7** Bitbucket **Stash MCP mapping** + **browse fallback** when code search **404**s (same as [`epic-prep.md`](../../pipelines/epic-prep.md) step **5b**). Benchmark runs must follow the same norms when executing COVERAGE work.

---

## Snapshot modes vs durable tree

| Mode | Detected when | Delegate line **must** include | Durable QA path | Machine snapshot |
|------|----------------|----------------------------------|-----------------|------------------|
| **Hub shadow** | **`benchmark_suite`** + **`benchmark_attempt`** on **`BENCHMARK-COVERAGE:`** | **`COVERAGE: <KEY> … benchmark_suite=… benchmark_attempt=…`** | **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/shadow/<KEY>/`** | **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/run-<seq>.json`** |
| **Legacy suite** | **`suite_run=`** without benchmark tokens | **`COVERAGE: <KEY> …`** only | **`epics/<KEY>/`** | **`coverage-bench/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`** |
| **Legacy flat** | neither | **`COVERAGE: <KEY> …`** | **`epics/<KEY>/`** | **`coverage-bench/run-<NNN>/`** sidecars |

---

## 1. Parse trigger

- Extract **Epic key**, **`runs`**, **`repo=`**, **`focus=`**.
- Extract optional **`benchmark_suite=<suite_id>`**, **`benchmark_attempt=<n>`** (hub shadow; **both** required together).
- Extract optional **`suite_run=<suite_id>`**, **`seq=<k>`** (legacy suite). If **`suite_run`** without **`seq`**, compute next seq under **`attempts/<KEY>/`** (legacy) or **`_machine/attempts/<KEY>/`** (hub), max **`run-*`** + 1, zero-pad to **3** digits.

---

## 2. Hub shadow mode

### Per iteration `i = 1 .. runs`

1. **Execute** full [`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md) as **`COVERAGE: <KEY> … benchmark_suite=<suite_id> benchmark_attempt=<n>`** (same **`repo=`** / **`focus=`** parsing as production).
2. **Self-check**: durable JSON/MD must **not** contain `/temp/`.
3. Read **`{EpicDir}<KEY>-coverage.json`** and **`{EpicDir}<KEY>-coverage.md`** (if present).
4. Write **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/run-<seq>.json`**:

```json
{
  "suite_id": "<suite_id>",
  "epic_key": "<KEY>",
  "phase": "coverage",
  "attempt": <attempt or i>,
  "seq": "<seq>",
  "iso_timestamp": "<ISO-8601>",
  "meta": {
    "source_playbook": ".cursor/benchmark/coverage-bench/pipeline/benchmark-coverage.md",
    "delegates": ".cursor/pipelines/coverage.md",
    "repo_token": "<workspace/repo or null>",
    "focus_token": "<focus or null>",
    "agent_summary": "<archetype, focus, ! lines, Bitbucket outcome>"
  },
  "artifact": <full object from {EpicDir}<KEY>-coverage.json>,
  "checklist_markdown": "<full text from -coverage.md for validator fallback>"
}
```

If **`-coverage.md`** is missing, set **`checklist_markdown`** from **`artifact.smart_checklist_markdown`** when present.

### Final message (hub shadow)

- Path to **`run-<seq>.json`**; **`COVERAGE-VALIDATE`** / **`compare_runs.py --suite-run-dir`** (see [validator.md](validator.md)).

---

## 3. Legacy suite mode (`suite_run=`)

### Per iteration `i = 1 .. runs`

1. **Execute** **`COVERAGE: <KEY>`** (**no** benchmark tokens); write under **`epics/<KEY>/`**.
2. **Self-check**, read **`epics/<KEY>/<KEY>-coverage.{json,md}`**.
3. Write **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`** (same wrapper shape).

### Final message (legacy suite)

- Path to **`run-<seq>.json`**; **`COVERAGE-VALIDATE: <KEY> suite=<suite_id>`**.

---

## 4. Legacy flat mode (no `suite_run=`)

Same as before: **`.cursor/benchmark/coverage-bench/run-<NNN>/`** with `coverage.snapshot.json`, `coverage.snapshot.md`, optional `epic-ref.snapshot.json`, **`meta.json`**, **`summary.md`**.

---

## Hard rules

1. **One epic key** per message unless the user widens scope.
2. **No secrets** in benchmark or epic files.
3. **`{EpicDir}temp/`** (or production **`epics/<KEY>/temp/`** in legacy-only) deleted after each iteration.
4. In **shadow** mode, do **not** write coverage artifacts under **`epics/<KEY>/`** for that trigger line.
5. Canonical outputs under **`{EpicDir}`** are overwritten on the next coverage run for that epic **within that attempt folder**.
