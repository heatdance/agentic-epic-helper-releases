# Finalize benchmark — **control hub only**

**Suite:** `20260508-ct01`
**Epics:** `CRT-639`
**Profile:** `coverage_test`

## Run key (`run-key`)

From **`.cursor/benchmark/runs/20260508-ct01/_manifest.json`**: **`run-key` = `report_run_key`** if that field is a non-null, non-empty string; otherwise **`run-key` = `suite_id`** (must match this folder name). Omit **`report_run_key`** or set **`null`** to use **`suite_id`**. All finalize outputs go under **`.cursor/benchmark/run-results/<run-key>/`** (see [`run-results/README.md`](../../run-results/README.md)).

## Mode

**Cursor Agent mode required** — not Plan, not Ask. Execute **numbered sections in order**.

**Keep context bounded:** **do not** paste full shadow JSON, MCP dumps, or entire `*-metrics.json` bodies into chat. After each shell step read **terminal stdout/stderr** and **`Wrote ...` paths** only. For **`report.md`**, summarize numeric claims from **`runs/20260508-ct01/_aggregate/crossref/`** filenames and **small KPI excerpts** — cite paths explicitly.

Optional one-shot toolchain (prints compare commands only; **does not** write **`report.md`**):

```bash
python automation/tools/benchmark_finalize_hub.py --suite-dir .cursor/benchmark/runs/20260508-ct01 [--gold-root <dir>]
```

(without **`--gold-root`** if **`.cursor/benchmark/data/CRT-639-gold.json`** is canonical).

**How to invoke:** In the **control hub** chat, paste this file’s body **or** send **`finalize`** (the agent reads **`.cursor/benchmark/runs/20260508-ct01/FINALIZE_PROMPT.md`** and executes every section below).

**This step runs in the hub:** verify → compare → author **`report.md`** + **`pipeline-delta-queue.json`** under **`run-results/<run-key>/`**.

---

## 1. Verify layout

From repo root — run **only** this; if it fails, stop and fix shadow / **`DONE.json`** before §2.

```bash
python automation/tools/benchmark_verify.py --suite-dir .cursor/benchmark/runs/20260508-ct01 --strict-manifest
```

If verification fails, use the relevant **`DONE_HANDOFF_PROMPT`** copy block again in shadow to align **`DONE.json`** / **`artifacts[]`**, or complete missing outputs under **`attempt-<nn>/shadow/CRT-639/`**, then retry.

## 2. Coverage metrics (prep + coverage)

For epic **`CRT-639`**, from repo root — add **`--gold-root <dir>`** when gold is **not** found under default search paths (see [`data/README.md`](../../data/README.md)):

```bash
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind prep --suite-run-dir .cursor/benchmark/runs/20260508-ct01 [--gold-root <dir>]
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind coverage --suite-run-dir .cursor/benchmark/runs/20260508-ct01 [--gold-root <dir>]
```

Shortcut — **modes-aware**:

```bash
python automation/tools/benchmark_aggregate.py --suite-dir .cursor/benchmark/runs/20260508-ct01 [--gold-root <dir>]
```

Outputs: **`.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/`**; append-only KPI history **`.cursor/benchmark/history/`** (**gitignored**).

## 3. Test benchmark metrics (`--kind test`)

For epic **`CRT-639`** (same **`--gold-root`** convention as §2):

```bash
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind test --suite-run-dir .cursor/benchmark/runs/20260508-ct01 [--gold-root <dir>]
```

Writes **`runs/20260508-ct01/_aggregate/crossref/CRT-639-test-metrics.json`**. Qualitative parity: [`test-bench/pipeline/validator-test.md`](../../test-bench/pipeline/validator-test.md).

## 4. Narrative + pipeline queue (`run-results/<run-key>/`)

**4a. Ensure output directory**

```powershell
New-Item -ItemType Directory -Force -Path ".cursor/benchmark/run-results/20260508-ct01"
```

(or `mkdir -p` on Unix). Use resolved **`run-key`** (`20260508-ct01` unless **`report_run_key`** overrides).

**4b. `report.md`**

Author or update **`.cursor/benchmark/run-results/20260508-ct01/report.md`** following **[`run-results/README.md`](../../run-results/README.md)** (full section order).

Base quantitative claims only on **`.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/`** (**`*-prep-metrics.json`**, **`*-coverage-metrics.json`**, **`*-test-metrics.json`**), cited by path — never paste full JSON bodies into chat.

**4c. `### Pipeline increments (structured)`** (inside `report.md`)

For **each** proposed playbook tweak, repeat this block template:

```markdown
#### <CR-ID e.g. CR-20260508-ct01-001>

- **Target:** `path/to/.cursor/pipelines/....md`
- **Trigger:** `.../runs/20260508-ct01/_aggregate/crossref/....json` — `<KPI or threshold gate>`
- **Hypothesis:** …
- **Proposed edit:** …
- **Generalization check:** Would this survive different epic keys? ≥2 epics?
- **Verify:** repro commands (e.g. `benchmark_aggregate.py --suite-dir ...`)
```

**4d. `pipeline-delta-queue.json`**

Mirror the same change requests into **`.cursor/benchmark/run-results/20260508-ct01/pipeline-delta-queue.json`** — start from **[`templates/pipeline-delta-queue.example.json`](../../templates/pipeline-delta-queue.example.json)**; set **`run_key`**, **`suite_id`**, **`suite_run_dir`**, **`crossref_dir`**, and **`change_requests`** to match this suite.
