# Benchmark validator: PREP + COVERAGE

**Triggers** (conventions; not in `pipeline-router.mdc`):

- **`PREP-VALIDATE:`** + Epic key — analyze **prep** snapshots.
- **`COVERAGE-VALIDATE:`** + Epic key — analyze **coverage** snapshots.

**Optional**: **`suite=<suite_id>`** on the same line — scope to **`.cursor/benchmark/runs/run-<suite_id>/attempts/<KEY>/run-*.json`** only (suite benchmark). If omitted, use **legacy** layout: **`.cursor/benchmark/run-*/`** with `meta.json` + sidecar snapshots.

**Prerequisite**: Read [`.cursor/benchmark/HOW-TO.md`](../HOW-TO.md). Optional gold: **`.cursor/benchmark/data/<KEY>-gold.json`**.

**Scope**: **one Epic key** per run unless the user lists multiple keys explicitly.

---

## 1. Discover inputs

Parse **Epic key** from the trigger (normalize to uppercase for folder lookup under **`attempts/`**).

Parse optional **`suite=<suite_id>`** (token may be unquoted; stop at next space-delimited token or end of line).

### A. Suite mode (`suite=<suite_id>`)

1. Base path: **`.cursor/benchmark/runs/run-<suite_id>/attempts/<KEY>/`** where **`<KEY>`** matches the epic (same spelling as Jira key in folder names, typically uppercase).
2. Enumerate **`run-*.json`** files; sort by filename.
3. **PREP-VALIDATE**: keep only records where JSON **`phase === "prep"`** and **`artifact`** is an object. Treat **`artifact`** as the epic-ref snapshot for all metrics below.
4. **COVERAGE-VALIDATE**: keep only **`phase === "coverage"`**; use **`artifact`** as coverage JSON; for checklist text prefer **`artifact.smart_checklist_markdown`**, else **`checklist_markdown`** on the wrapper.
5. **Run labels** for tables: relative path e.g. **`runs/run-<suite_id>/attempts/<KEY>/run-001.json`**.

If no matching files: **stop** and tell the user to run suite prep/coverage steps first.

### B. Legacy mode (no `suite=`)

1. Enumerate **`.cursor/benchmark/run-*/`** (top-level only — not under **`runs/`**).
2. Skip directories that are clearly suite roots (suite orchestration lives under **`runs/run-*/support/`** with **`support/queue.json`**; legacy **`run-*`** dirs at the benchmark root won’t overlap).
3. For each **`run-*`**, read **`meta.json`**. Include only if **`epic_key`** matches trigger key (case-insensitive compare).
4. **PREP-VALIDATE**: require **`epic-ref.snapshot.json`** per directory.
5. **COVERAGE-VALIDATE**: require **`coverage.snapshot.json`** (use **`coverage.snapshot.md`** when helpful).

If no matching runs: **stop** and tell the user to run **`BENCHMARK-EPIC-PREP:`** / **`BENCHMARK-COVERAGE:`** first.

---

## 2. Deterministic metrics (no LLM required)

Same definitions as before; **per run** means each suite JSON file or each legacy directory.

### PREP — per run

- From epic-ref **`artifact`**: count **`requirements[]`**; snippet null vs non-null; SHA256 of normalized snippet text; **`client_shell_impact`**.

### PREP — cross-run

- Key intersection, stable snippet hashes, unstable keys, `client_shell_impact` drift.

### COVERAGE — per run

- Matrix rows; bullets from **`smart_checklist_markdown`** / MD fallback.

### COVERAGE — cross-run

- Matrix intersection, pairwise Jaccard, bullet frequency (strong / weak).

---

## 3. Optional script

From repo root:

```bash
python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic CRT-639 --kind prep
python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic CRT-639 --kind prep --suite-id <suite_id>
python .cursor/benchmark/scripts/compare_runs.py --benchmark-root .cursor/benchmark --epic CRT-639 --kind coverage --suite-id <suite_id>
```

- Writes **`crossref/<KEY>-prep-metrics.json`** or **`<KEY>-coverage-metrics.json`** (payload includes **`suite_id`** when `--suite-id` is set).
- If the script fails, compute manually in the digest.

---

## 4. Gold alignment (when `data/<KEY>-gold.json` exists)

Load gold. Respect **`pipeline`**: `"prep"` | `"coverage"` | `"both"`.

### Prep checks

- **`required_requirement_keys_in_snippets`**: each key must appear in **every** prep run’s **`artifact`** with non-null **`snippet_text`** (or list failures per run label).

### Coverage checks

- **`required_smart_checklist_substrings`**: default **each** coverage run’s combined checklist text contains all substrings.
- **`forbidden_checklist_regex`**: Python **`re.search`** against normalized full checklist body per run.

---

## 5. Outputs (write files)

### Crossref

Same paths: **`crossref/<KEY>-prep-metrics.json`**, **`crossref/<KEY>-coverage-metrics.json`** (optionally note **`suite_id`** in digest when suite-scoped).

### Digest

- **`digest/<KEY>-prep-digest.md`**
- **`digest/<KEY>-coverage-digest.md`**

Each digest **must** include:

1. **Executive summary**
2. **Runs included** — suite: path to each `run-*.json`; legacy: folder name + timestamp from **`meta.json`**
3. **Variance**
4. **Strong matches**
5. **Divergences**
6. **Optimization plan** — link evidence to epic-prep, coverage, templates, yogi-tool (recommendations only)

---

## 6. Final user message

- Recap + links to **`crossref/*`** and **`digest/*`**.
- If gold missing: note **`data/<KEY>-gold.json`**.
