# Benchmark runner: EPIC-PREP variance

**Trigger**: user message starts with **`BENCHMARK-EPIC-PREP:`** and includes a Jira **Epic key** (e.g. `BENCHMARK-EPIC-PREP: CRT-639 runs=3`).

**Not** in [`.cursor/rules/pipeline-router.mdc`](../../rules/pipeline-router.mdc). Execute only when the operator asked you to follow this playbook (see [`.cursor/benchmark/HOW-TO.md`](../HOW-TO.md)).

**Delegate**: Perform the **same work** as [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md) for each iteration—Jira, Yogi, `epics/<KEY>/<KEY>-ref.json`, `epics/<KEY>/temp/` lifecycle, no `/temp/` in durable JSON.

**Scope**: **one Epic key** per invocation. Optional **`runs=<N>`** on the same line (default **1**). Parse `runs` as a positive integer; cap at **20** unless the user explicitly overrides with a higher number in the same message.

---

## Preconditions

Same as [`epic-prep.md`](../../pipelines/epic-prep.md): MCP Atlassian, Yogi docs, no fabricated snippets, no secrets in files.

**Production parity (delegated playbook)**: [`epic-prep.md`](../../pipelines/epic-prep.md) defines **step 3b** (one retry round for recoverable snippet failures), **step 8** finalize gate for **jira-linked** requirement rows unless **`deferral_accepted`** in `validation_log`, **step 2b** stable **`client_shell_impact`** (**`note`** vs **`evidence`**, verbatim **`qa_default_both`** sentence), and **step 3** treating **MCP storage + `yogi_snippet.py --storage-file`** as a first-class success path. Benchmark runs must follow the same steps when executing EPIC-PREP work.

---

## Suite mode vs legacy mode

| Mode | Detected when | Output |
|------|----------------|--------|
| **Suite** | **`suite_run=<suite_id>`** present | **`.cursor/benchmark/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`** |
| **Legacy** | `suite_run` absent | **`.cursor/benchmark/run-<NNN>/`** with `epic-ref.snapshot.json` + `meta.json` + `summary.md` |

---

## 1. Parse trigger

- Extract **Epic key** (e.g. `CRT-639`).
- Extract **`runs`** (default 1).
- Extract optional **`suite_run=<suite_id>`** — path-safe id matching the suite folder (**`runs/run-<suite_id>/`**).
- Extract optional **`attempt=<n>`** (1-based; for suite queue alignment).
- Extract optional **`seq=<k>`** — sequence within the epic folder (`001`, `002`, …). If **`suite_run`** is set but **`seq`** is missing, compute **next** seq: list `attempts/<KEY>/run-*.json`, parse numeric suffix, max+1, zero-pad to **3** digits.

---

## 2. Suite mode (`suite_run=`)

### Per iteration `i = 1 .. runs` (normally **`runs=1`** in suite queue)

1. **Execute** full [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md) for `<KEY>` until `epics/<KEY>/<KEY>-ref.json` is complete and `epics/<KEY>/temp/` is **deleted**.
2. **Self-check**: ref JSON must **not** contain `/temp/`.
3. Read the completed **`epics/<KEY>/<KEY>-ref.json`** into memory.
4. Determine **`seq`** for this iteration (from message or auto as above); pad to 3 digits (`run-001.json`).
5. Write **`.cursor/benchmark/runs/run-<suite_id>/attempts/<KEY>/run-<seq>.json`**:

```json
{
  "suite_id": "<suite_id>",
  "epic_key": "<KEY>",
  "phase": "prep",
  "attempt": <attempt or i>,
  "seq": "<seq>",
  "iso_timestamp": "<ISO-8601>",
  "meta": {
    "source_playbook": ".cursor/benchmark/pipeline/benchmark-epic-prep.md",
    "delegates": ".cursor/pipelines/epic-prep.md",
    "agent_summary": "<short notes: snippets, Yogi, gaps>"
  },
  "artifact": <full object copied from epics/<KEY>/<KEY>-ref.json>
}
```

6. **Do not** copy `temp/` into benchmark paths.

### Final message (suite mode)

- Path to written **`run-<seq>.json`**.
- Next: **`BENCHMARK-NEXT:`** or coverage line from queue; **`PREP-VALIDATE: <KEY> suite=<suite_id>`** when prep block for that epic is done.

---

## 3. Legacy mode (no `suite_run=`)

### Choose run folder sequence

- Under **`.cursor/benchmark/`**, use consecutive folders: `run-001`, `run-002`, … at the **benchmark root** (not under `runs/`).
- If folders exist, continue from next free index or use an explicit pattern documented in the first `summary.md`.

### For each iteration `i = 1 .. runs`

1. **Execute** epic-prep playbook for `<KEY>`; delete `temp/`.
2. **Self-check**: no `/temp/` in ref JSON.
3. Copy **`epics/<KEY>/<KEY>-ref.json`** → **`.cursor/benchmark/run-<NNN>/epic-ref.snapshot.json`**
4. Write **`.cursor/benchmark/run-<NNN>/meta.json`**:

```json
{
  "epic_key": "<KEY>",
  "pipeline": "benchmark_epic_prep",
  "run_index": <i>,
  "iso_timestamp": "<ISO-8601>",
  "source_playbook": ".cursor/benchmark/pipeline/benchmark-epic-prep.md",
  "delegates": ".cursor/pipelines/epic-prep.md"
}
```

5. Write **`.cursor/benchmark/run-<NNN>/summary.md`** (short human notes).

### Final message (legacy)

- Snapshot paths; **`PREP-VALIDATE: <KEY>`**; [HOW-TO](../HOW-TO.md).

---

## Hard rules

1. **One epic key** per message unless the user widens scope.
2. **No secrets** in benchmark or epic files.
3. **`epics/<KEY>/temp/`** deleted after each iteration.
4. Snapshots are **copies**; canonical **`epics/<KEY>/<KEY>-ref.json`** is overwritten on the next prep for that epic.
