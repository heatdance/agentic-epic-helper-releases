# Benchmark runner: EPIC-PREP variance

**Trigger**: user message starts with **`BENCHMARK-EPIC-PREP:`** and includes a Jira **Epic key** (e.g. `BENCHMARK-EPIC-PREP: CRT-639 runs=3`).

**Not** in [`.cursor/rules/pipeline-router.mdc`](../../rules/pipeline-router.mdc). Execute only when the operator asked you to follow this playbook (see [`../HOW-TO.md`](../HOW-TO.md)).

**Delegate**: Perform the **same steps** as [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md) for each iteration—Jira, Yogi, **`<KEY>-ref.json`** and **`temp/`** under the resolved **`{EpicDir}`**, no `/temp/` in durable JSON. When **benchmark shadow** applies, **`{EpicDir}`** is under `.cursor/benchmark/runs/.../shadow/` (see [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md)).

**Scope**: **one Epic key** per invocation. Optional **`runs=<N>`** on the same line (default **1**). Parse `runs` as a positive integer; cap at **20** unless the user explicitly overrides with a higher number in the same message.

---

## Preconditions

Same as [`epic-prep.md`](../../pipelines/epic-prep.md): MCP Atlassian, Yogi docs, no fabricated snippets, no secrets in files.

**Production parity (delegated playbook)**: [`epic-prep.md`](../../pipelines/epic-prep.md) defines **step 3b** (one retry round for recoverable snippet failures), **step 8** finalize gate for **jira-linked** requirement rows unless **`deferral_accepted`** in `validation_log`, **step 2b** stable **`client_shell_impact`** (**`note`** vs **`evidence`**, verbatim **`qa_default_both`** sentence), **step 3** treating **MCP storage + `yogi_snippet.py --storage-file`** as a first-class success path, and **step 5b** Bitbucket **Stash `project_key`/`repo_slug` mapping** plus **browse fallback** when `bitbucket_search_code` returns **404**. Benchmark runs must follow the same steps when executing EPIC-PREP work.

---

## Snapshot modes vs durable tree

| Mode | Detected when | Delegate line **must** include | Durable QA path (`{EpicDir}`) | Machine snapshot (`run-*.json`) |
|------|----------------|---------------------------------|--------------------------------|----------------------------------|
| **Hub shadow** (preferred) | **`benchmark_suite=<suite_id>`** and **`benchmark_attempt=<n>`** on **`BENCHMARK-EPIC-PREP:`** | **`EPIC-PREP: <KEY> benchmark_suite=… benchmark_attempt=…`** (same values) | **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/shadow/<KEY>/`** | **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/run-<seq>.json`** |
| **Legacy suite** | **`suite_run=<suite_id>`** without both benchmark tokens | **`EPIC-PREP: <KEY>`** only | **`epics/<KEY>/`** (production) | **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`** |
| **Legacy flat** | neither suite nor benchmark tokens | **`EPIC-PREP: <KEY>`** | **`epics/<KEY>/`** | **`.cursor/benchmark/coverage-bench/run-<NNN>/`** (see §3) |

**`<nn>`** on disk is **`benchmark_attempt`** zero-padded to **two** digits (matches [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md)).

New suite work should use **Hub shadow** so production **`epics/<KEY>/`** is not overwritten and [`compare_runs.py`](../scripts/compare_runs.py) can use **`--suite-run-dir`**.

---

## 1. Parse trigger

- Extract **Epic key** (e.g. `CRT-639`).
- Extract **`runs`** (default 1).
- Extract optional **`benchmark_suite=<suite_id>`** / **`benchmark_attempt=<n>`** — enable shadow **`{EpicDir}`**; **both required together** for hub mode (same semantics as **`EPIC-PREP:`** in the production playbook).
- Extract optional **`suite_run=<suite_id>`** — path-safe id for **legacy** suite layout (**`coverage-bench/runs/run-<suite_id>/`**); do **not** mix with benchmark shadow unless the operator explicitly requests legacy behavior.
- Extract optional **`seq=<k>`** — sequence within the epic snapshot folder (`001`, `002`, …). If snapshots are written but **`seq`** is missing, compute **next** seq: list existing **`run-*.json`** under the snapshot directory for this mode (hub → `_machine/attempts/<KEY>/`; legacy suite → **`attempts/<KEY>/`**), parse numeric suffix, max+1, zero-pad to **3** digits.

---

## 2. Hub shadow mode (`benchmark_suite=` + `benchmark_attempt=`)

### Per iteration `i = 1 .. runs` (normally **`runs=1`** in suite queue)

1. **Execute** full [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md) with **`EPIC-PREP: <KEY> benchmark_suite=<suite_id> benchmark_attempt=<n>`** (reuse **same** `benchmark_attempt` unless the queue advances attempts).
2. **Self-check**: ref JSON must **not** contain `/temp/`.
3. Read **`{EpicDir}<KEY>-ref.json`** (shadow path above).
4. Determine **`seq`** for this iteration (from message or auto); pad to 3 digits (`run-001.json`).
5. Write **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/run-<seq>.json`**:

```json
{
  "suite_id": "<suite_id>",
  "epic_key": "<KEY>",
  "phase": "prep",
  "attempt": <attempt or i>,
  "seq": "<seq>",
  "iso_timestamp": "<ISO-8601>",
  "meta": {
    "source_playbook": ".cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md",
    "delegates": ".cursor/pipelines/epic-prep.md",
    "agent_summary": "<short notes: snippets, Yogi, gaps>"
  },
  "artifact": <full object copied from {EpicDir}<KEY>-ref.json>
}
```

6. **Do not** copy `temp/` into `_machine/` paths.

### Final message (hub shadow)

- Path to **`run-<seq>.json`**; durable path under **`…/shadow/<KEY>/`**.
- Next: **`BENCHMARK-NEXT:`** or queue row; **`PREP-VALIDATE: <KEY>`** referencing hub layout or run [`compare_runs.py`](../scripts/compare_runs.py) with **`--suite-run-dir`** (see [validator.md](validator.md)).

---

## 3. Legacy suite mode (`suite_run=` without benchmark tokens)

### Per iteration `i = 1 .. runs`

1. **Execute** [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md) for **`EPIC-PREP: <KEY>`** (**no** benchmark tokens).
2. **Self-check**: ref JSON must **not** contain `/temp/`.
3. Read **`epics/<KEY>/<KEY>-ref.json`**.
4. Write **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`** (same JSON shape as hub, with **`phase": "prep"`**).

### Final message (legacy suite)

- Path to **`run-<seq>.json`**; next queue step or **`PREP-VALIDATE: <KEY> suite=<suite_id>`**.

---

## 4. Legacy flat mode (no `suite_run=`, no benchmark tokens)

### Choose run folder sequence

- Under **`.cursor/benchmark/coverage-bench/`**, use consecutive folders: `run-001`, `run-002`, … at the **coverage-bench root** (not under `runs/`).
- If folders exist, continue from next free index or use an explicit pattern documented in the first `summary.md`.

### For each iteration `i = 1 .. runs`

1. **Execute** epic-prep playbook for **`EPIC-PREP: <KEY>`**; delete **`epics/<KEY>/temp/`**.
2. **Self-check**: no `/temp/` in ref JSON.
3. Copy **`epics/<KEY>/<KEY>-ref.json`** → **`.cursor/benchmark/coverage-bench/run-<NNN>/epic-ref.snapshot.json`**
4. Write **`.cursor/benchmark/coverage-bench/run-<NNN>/meta.json`**:

```json
{
  "epic_key": "<KEY>",
  "pipeline": "benchmark_epic_prep",
  "run_index": <i>,
  "iso_timestamp": "<ISO-8601>",
  "source_playbook": ".cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md",
  "delegates": ".cursor/pipelines/epic-prep.md"
}
```

5. Write **`.cursor/benchmark/coverage-bench/run-<NNN>/summary.md`** (short human notes).

### Final message (legacy flat)

- Snapshot paths; **`PREP-VALIDATE: <KEY>`**; [HOW-TO](../HOW-TO.md).

---

## Hard rules

1. **One epic key** per message unless the user widens scope.
2. **No secrets** in benchmark or epic files.
3. **`{EpicDir}temp/`** (or **`epics/<KEY>/temp/`** in legacy-only runs) deleted after each iteration.
4. In **shadow** mode, canonical prep output lives under **`attempt-<nn>/shadow/<KEY>/`**; **`epics/<KEY>/`** must **not** receive writes for that run line.
5. Snapshots under **`_machine/`** are **copies** for tooling; regenerate on the next hub attempt as needed.
