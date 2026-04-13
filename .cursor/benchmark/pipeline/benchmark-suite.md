# Meta benchmark suite (multi-epic, one atomic step per message)

**Triggers** (not in `pipeline-router.mdc`):

- **`BENCHMARK:`** — **plan only**: create suite folders, **`support/`** with `queue.json`, `QUEUE.md`, `progress.json`, `suite-meta.json`. **Do not** run prep, coverage, or validators in the same turn.
- **`BENCHMARK-NEXT:`** + **`<suite_id>`** — execute **exactly one** queue step (see [`.cursor/benchmark/HOW-TO.md`](../HOW-TO.md)).

**Prerequisite**: Read [`.cursor/benchmark/HOW-TO.md`](../HOW-TO.md).

---

## Suite layout

All artifacts for one suite live under:

**`.cursor/benchmark/runs/run-<suite_id>/`**

- **`support/`** — orchestration sidecars (always this folder name):
  - `queue.json` — ordered steps
  - `QUEUE.md` — human copy-paste list (same steps)
  - `progress.json` — cursor for `BENCHMARK-NEXT`
  - `suite-meta.json` — defaults (`epics`, `runs`, `repo`, `focus`)
- `SUMMARY.md` — written on **suite_finalize** only
- `attempts/<EPIC_KEY>/` — per-epic atomic results: **`run-<seq>.json`** (`seq` zero-padded, e.g. `001`)

---

## 1. Parse `BENCHMARK:`

**Pattern**: message starts with **`BENCHMARK:`** then a comma-separated list of Jira epic keys (optional spaces), e.g. `BENCHMARK: CRT-639, CRT-593, CRT-100`.

**Optional tokens** on the same line:

| Token | Default | Notes |
|--------|---------|--------|
| **`runs=<N>`** | **3** | Prep+coverage pairs per epic |
| **`repo=WORKSPACE/REPO_SLUG`** | absent | Passed to every **coverage** step |
| **`focus=...`** | absent | Free text; passed to every coverage step (same rules as production `COVERAGE:`) |
| **`suite_run=<id>`** | auto | If omitted, generate **`<suite_id>`**: `YYYYMMDD-` + four alphanumeric chars (e.g. `20260413-a7f2`). Use only safe path chars: `[A-Za-z0-9._-]` |

**Normalize** epic keys to uppercase Jira style.

---

## 2. `BENCHMARK:` actions (single turn — **init only**)

1. Resolve **`<suite_id>`** from `suite_run=` or generate as above.
2. Create **`.cursor/benchmark/runs/run-<suite_id>/attempts/<EPIC>/`** for each epic (empty dirs).
3. Build **`<seq>`** per epic: for each epic, start at `001` and increment for **each** atomic file (prep then coverage per attempt).
4. Create **`support/`** under the suite root. Build **`support/queue.json`**:

```json
{
  "suite_id": "<suite_id>",
  "steps": [
    {
      "index": 0,
      "type": "prep",
      "epic": "CRT-639",
      "attempt": 1,
      "seq": "001",
      "exact_message": "BENCHMARK-EPIC-PREP: CRT-639 runs=1 suite_run=<suite_id> attempt=1 seq=001"
    }
  ]
}
```

**Default step order** (same as plan):

- Outer: epics in list order.
- Inner: for `attempt` = 1..`runs`: **prep** then **coverage**.
- After all prep/coverage: for each epic: **`prep_validate`**, then **`coverage_validate`**.
- Last step: **`suite_finalize`** (no `exact_message`; see §4).

**Validate steps** — include **`exact_message`** so they can be pasted manually:

- `PREP-VALIDATE: <EPIC> suite=<suite_id>`
- `COVERAGE-VALIDATE: <EPIC> suite=<suite_id>`

**`suite_finalize`** step object: `{ "index": <n>, "type": "suite_finalize" }` only (no `exact_message`).

**Coverage** steps: append to `exact_message` the same **`repo=`** / **`focus=`** as parsed (omit token if not provided).

Example coverage line:

`BENCHMARK-COVERAGE: CRT-639 runs=1 suite_run=<suite_id> attempt=1 seq=002 repo=my/ws`

5. Write **`support/QUEUE.md`**: numbered list; each line is the `exact_message` for that step (or a short heading for `suite_finalize`: “Run suite finalize (see benchmark-suite.md §4)”).
6. Write **`support/progress.json`**:

```json
{
  "suite_id": "<suite_id>",
  "next_step_index": 0,
  "steps_total": <N>,
  "completed_step_indices": [],
  "epics": ["CRT-639", "..."],
  "runs": 3,
  "repo": "<string or null>",
  "focus": "<string or null>"
}
```

7. Write **`support/suite-meta.json`**: copy of defaults for humans (`epics`, `runs`, `repo`, `focus`, `created_at` ISO). Optional **`note`** may mention `support/QUEUE.md` for paste workflow.

8. **Stop.** Reply with:
   - Path to **`runs/run-<suite_id>/support/QUEUE.md`**
   - Instruction: **one** step per message — paste the next line from **`support/QUEUE.md`** **or** send **`BENCHMARK-NEXT: <suite_id>`**
   - Recommend **new chat / fresh composer** per step when measuring model variance (operator choice).

**Do not** execute prep, coverage, or validation in this turn.

---

## 3. `BENCHMARK-NEXT:` + `<suite_id>`

1. Load **`.cursor/benchmark/runs/run-<suite_id>/support/queue.json`** and **`support/progress.json`**.
2. Let **`i` = `next_step_index`**. If **`i >= steps_total`**: report suite already complete; stop.
3. Read **`steps[i]`**.
4. **Execute exactly this one step** (no other queue steps in the same turn):
   - **`prep`**: follow [`benchmark-epic-prep.md`](benchmark-epic-prep.md) using **`steps[i].exact_message`** as if the user pasted it.
   - **`coverage`**: follow [`benchmark-coverage.md`](benchmark-coverage.md) the same way.
   - **`prep_validate`**: follow [`validator.md`](validator.md) — **`PREP-VALIDATE: <epic> suite=<suite_id>`** (epic from step; if step bundles per-epic validate, use that step’s epic).
   - **`coverage_validate`**: **`COVERAGE-VALIDATE: <epic> suite=<suite_id>`**
   - **`suite_finalize`**: execute §4 below only.

5. Append **`i`** to **`completed_step_indices`**, set **`next_step_index`** to **`i + 1`**, write **`support/progress.json`**.

6. Reply with: step done, next instruction (`BENCHMARK-NEXT: ...` or paste next line), and whether suite is complete.

---

## 4. Suite finalize (`suite_finalize` step)

When **`steps[i].type === "suite_finalize"`**:

1. Read **`support/suite-meta.json`** for epic list.
2. For each epic, if **`digest/<EPIC>-prep-digest.md`** / **`digest/<EPIC>-coverage-digest.md`** exist from validate steps, note paths.
3. Optionally run [`scripts/compare_runs.py`](../scripts/compare_runs.py) per epic:  
   `python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic <EPIC> --kind prep --suite-id <suite_id>`  
   (and `--kind coverage`). Discovery is **phase-filtered** (`phase` in each snapshot JSON must match `--kind`).
4. Write **`runs/run-<suite_id>/SUMMARY.md`** with:
   - **Suite id**, epics, `runs` count, timestamps
   - **Per-epic** links to `digest/*`, `crossref/*-prep-metrics.json`, `crossref/*-coverage-metrics.json` when present
   - **Rollup**: variance highlights (1–2 bullets per epic)
   - **Corrections / optimization list**: numbered hypotheses (playbooks, templates, yogi-tool) — **recommendations only**, no repo edits

5. Update **`support/progress.json`** as in §3.

---

## Hard rules

1. **`BENCHMARK:`** never runs child pipelines in the same turn.
2. **`BENCHMARK-NEXT:`** runs **at most one** queue step per turn.
3. **No secrets** in suite files.
4. **No** edits to global harness files (`AGENTS.md`, `pipeline-router.mdc`, etc.) from this playbook.
