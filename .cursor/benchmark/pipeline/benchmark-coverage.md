# Benchmark runner: COVERAGE variance

**Trigger**: user message starts with **`BENCHMARK-COVERAGE:`** and includes a Jira **Epic key** (e.g. `BENCHMARK-COVERAGE: CRT-639 repo=myworkspace/dxtrade-xt runs=3`).

**Not** in [`.cursor/rules/pipeline-router.mdc`](../../rules/pipeline-router.mdc). Execute when the operator asked you to follow this playbook (see [`.cursor/benchmark/HOW-TO.md`](../HOW-TO.md)).

**Delegate**: Perform the **same work** as [`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md) for each iteration—prerequisite `epics/<KEY>/<KEY>-ref.json`, outputs `-coverage.json` / `-coverage.md`, `epics/<KEY>/temp/` deleted, no `/temp/` in durable files.

**Scope**: **one Epic key** per invocation. Optional on the same line:

- **`runs=<N>`** — default **1**; cap at **20** unless the user explicitly overrides in the same message.
- **`repo=WORKSPACE/REPO_SLUG`** — pass through (production semantics).
- **`focus=...`** — free-text verification focus (production semantics).

---

## Preconditions

Same as [`coverage.md`](../../pipelines/coverage.md). If `epics/<KEY>/<KEY>-ref.json` is missing, **stop** and tell the user to run **`BENCHMARK-EPIC-PREP:`** or **`EPIC-PREP:`** first.

**Production parity (delegated playbook)**: [`coverage.md`](../../pipelines/coverage.md) defines deterministic **`coverage_matrix[].id`**, a **`supporting` vs `out_of_epic`** decision ladder (phase **4**), verbatim **primary focus** in the first substantive Smart Checklist **`##`** block (phases **8** / **14**), optional-scenario discipline (phases **9** / **11**), and phase **5** snippet enrichment rules tied to EPIC-PREP **3b**/**8**. Benchmark runs must follow the same norms when executing COVERAGE work.

---

## Suite mode vs legacy mode

| Mode | Detected when | Output |
|------|----------------|--------|
| **Suite** | **`suite_run=<suite_id>`** present | **`runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`** |
| **Legacy** | `suite_run` absent | **`run-<NNN>/`** under benchmark root with `coverage.snapshot.json` / `.md` + `meta.json` |

---

## 1. Parse trigger

- Extract **Epic key**, **`runs`**, **`repo=`**, **`focus=`**.
- Extract optional **`suite_run=<suite_id>`**, **`attempt=<n>`**, **`seq=<k>`**. If **`suite_run`** without **`seq`**, compute next seq under **`attempts/<KEY>/`** (max `run-*.json` + 1, zero-pad to 3 digits).

---

## 2. Suite mode (`suite_run=`)

### Per iteration `i = 1 .. runs`

1. **Execute** full [`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md) for `<KEY>` with parsed **`repo=`** / **`focus=`**.
2. **Self-check**: durable JSON/MD must **not** contain `/temp/`.
3. Read **`epics/<KEY>/<KEY>-coverage.json`** and **`epics/<KEY>/<KEY>-coverage.md`** (if present).
4. Write **`.cursor/benchmark/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`**:

```json
{
  "suite_id": "<suite_id>",
  "epic_key": "<KEY>",
  "phase": "coverage",
  "attempt": <attempt or i>,
  "seq": "<seq>",
  "iso_timestamp": "<ISO-8601>",
  "meta": {
    "source_playbook": ".cursor/benchmark/pipeline/benchmark-coverage.md",
    "delegates": ".cursor/pipelines/coverage.md",
    "repo_token": "<workspace/repo or null>",
    "focus_token": "<focus or null>",
    "agent_summary": "<archetype, focus, ! lines, Bitbucket outcome>"
  },
  "artifact": <full object from -coverage.json>,
  "checklist_markdown": "<full text from -coverage.md for validator fallback>"
}
```

If **`-coverage.md`** is missing, set **`checklist_markdown`** from **`artifact.smart_checklist_markdown`** when present.

### Final message (suite mode)

- Path to **`run-<seq>.json`**; next queue step or **`COVERAGE-VALIDATE: <KEY> suite=<suite_id>`**.

---

## 3. Legacy mode (no `suite_run=`)

Same as before: **`.cursor/benchmark/run-<NNN>/`** with `coverage.snapshot.json`, `coverage.snapshot.md`, optional `epic-ref.snapshot.json`, **`meta.json`**, **`summary.md`**.

---

## Hard rules

1. **One epic key** per message unless the user widens scope.
2. **No secrets** in benchmark or epic files.
3. **`epics/<KEY>/temp/`** deleted after each iteration.
4. Canonical outputs under **`epics/<KEY>/`** are overwritten on the next coverage run for that epic.
