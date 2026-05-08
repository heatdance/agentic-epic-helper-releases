# Benchmark validator: PREP + COVERAGE

**Triggers** (conventions; not in `pipeline-router.mdc`):

- **`PREP-VALIDATE:`** + Epic key — analyze **prep** snapshots.
- **`COVERAGE-VALIDATE:`** + Epic key — analyze **coverage** snapshots.

**Optional**: **`suite=<suite_id>`** on the same line — scope to **legacy** suite layout: **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/attempts/<KEY>/run-*.json`**. Prefer **hub** discovery (§1C) for new work under **`.cursor/benchmark/runs/<suite_id>/`**.

**Optional**: **`suite_run_dir=…`** or operator phrasing “hub suite …” — treat inputs as **§1C** (`attempt-*/_machine/attempts/<KEY>/`).

**Prerequisite**: Read [`../HOW-TO.md`](../HOW-TO.md). Optional gold (canonical): **`.cursor/benchmark/data/<KEY>-gold.json`**; legacy: **`coverage-bench/data/<KEY>-gold.json`**.

**Scope**: **one Epic key** per run unless the user lists multiple keys explicitly.

---

## 1. Discover inputs

Parse **Epic key** from the trigger (normalize to uppercase for folder lookup under **`attempts/`**).

Parse optional **`suite=<suite_id>`** (token may be unquoted; stop at next space-delimited token or end of line).

### A. Suite mode (`suite=<suite_id>`)

1. Base path: **`.cursor/benchmark/coverage-bench/runs/run-<suite_id>/attempts/<KEY>/`** where **`<KEY>`** matches the epic (same spelling as Jira key in folder names, typically uppercase).
2. Enumerate **`run-*.json`** files; sort by filename.
3. **PREP-VALIDATE**: keep only records where JSON **`phase === "prep"`** and **`artifact`** is an object. Treat **`artifact`** as the epic-ref snapshot for all metrics below.
4. **COVERAGE-VALIDATE**: keep only **`phase === "coverage"`**; use **`artifact`** as coverage JSON; for checklist text prefer **`artifact.smart_checklist_markdown`**, else **`checklist_markdown`** on the wrapper.
5. **Run labels** for tables: relative path e.g. **`runs/run-<suite_id>/attempts/<KEY>/run-001.json`**.

If no matching files: **stop** and tell the user to run suite prep/coverage steps first.

### B. Legacy mode (no `suite=`)

1. Enumerate **`.cursor/benchmark/coverage-bench/run-*/`** (top-level only — not under **`runs/`**).
2. Skip directories that are clearly suite roots (suite orchestration lives under **`runs/run-*/support/`** with **`support/queue.json`**; legacy **`run-*`** dirs at the coverage-bench root won’t overlap).
3. For each **`run-*`**, read **`meta.json`**. Include only if **`epic_key`** matches trigger key (case-insensitive compare).
4. **PREP-VALIDATE**: require **`epic-ref.snapshot.json`** per directory.
5. **COVERAGE-VALIDATE**: require **`coverage.snapshot.json`** (use **`coverage.snapshot.md`** when helpful).

If no matching runs: **stop** and tell the user to run **`BENCHMARK-EPIC-PREP:`** / **`BENCHMARK-COVERAGE:`** first.

### C. Hub suite mode (`.cursor/benchmark/runs/<suite_id>/`)

1. Base path: **`.cursor/benchmark/runs/<suite_id>/attempt-<nn>/_machine/attempts/<KEY>/`** (normative wrapper tree for [`compare_runs.py`](../scripts/compare_runs.py) **`--suite-run-dir`**).
2. Enumerate **all** matching **`run-*.json`** across **`attempt-*`** folders; sort for display (e.g. by **`attempt-*`** then filename).
3. **PREP-VALIDATE** / **COVERAGE-VALIDATE**: same phase / **`artifact`** rules as §1A.
4. **Run labels** for tables: e.g. **`attempt-01__run-001`** (matches compare_runs labels) or full relative path from repo root.
5. **Metrics output** (script): **`_aggregate/crossref/<KEY>-*-metrics.json`** inside the suite folder; **global** append-only history: **`.cursor/benchmark/history/<KEY>-*-history.jsonl`** (not duplicated per suite).

If no matching files: **stop** — run hub **`BENCHMARK-EPIC-PREP:`** / **`BENCHMARK-COVERAGE:`** with **`benchmark_suite` + benchmark_attempt** first (see [docs/benchmark-contract.md](../../../../docs/benchmark-contract.md)).

---

## 2. Deterministic metrics (no LLM required)

Same definitions as before; **per run** means each suite JSON file or each legacy directory.

### PREP — per run

- From epic-ref **`artifact`**: count **`requirements[]`**; snippet null vs non-null; SHA256 of normalized snippet text; **`client_shell_impact`**.
- KPIs from crossref **`kpis`**: `snippet_completion_rate_by_run`, `snippet_completion_rate_avg`, `snippet_missing_keys_by_run`, `client_shell_impact_drift`.

### PREP — cross-run

- Key intersection, stable snippet hashes, unstable keys, `client_shell_impact` drift.

### COVERAGE — per run

- Matrix rows; bullets from **`smart_checklist_markdown`** / MD fallback.
- Split bullets into:
  - **core** (semantic test intent),
  - **diagnostic** (tooling/data-noise lines such as snippet-missing reasons).
- KPI fields: `core_bullet_jaccard_avg`, `diagnostic_bullet_count_by_run`, `matrix_role_flip_count`, `primary_focus_verbatim_pass_rate`.

### COVERAGE — cross-run

- Matrix intersection, pairwise Jaccard, bullet frequency (strong / weak).
- Prefer **core** metrics for stability decisions; use diagnostic counts for root-cause context.

---

## 3. Optional script

From repo root:

```bash
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --benchmark-root .cursor/benchmark/coverage-bench --epic CRT-639 --kind prep
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --benchmark-root .cursor/benchmark/coverage-bench --epic CRT-639 --kind prep --suite-id <suite_id>
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --benchmark-root .cursor/benchmark/coverage-bench --epic CRT-639 --kind coverage --suite-id <suite_id>
# Hub suite (shadow + _machine wrappers):
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind prep --suite-run-dir .cursor/benchmark/runs/<suite_id>
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind coverage --suite-run-dir .cursor/benchmark/runs/<suite_id>
# Optional explicit gold directory:
python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind prep --suite-run-dir .cursor/benchmark/runs/<suite_id> --gold-root .cursor/benchmark/data
```

- **Legacy / coverage-bench suite**: writes **`coverage-bench/crossref/<KEY>-*-metrics.json`** (payload includes **`suite_id`** when `--suite-id` is set).
- **Hub**: writes **`.cursor/benchmark/runs/<suite_id>/_aggregate/crossref/<KEY>-*-metrics.json`**; gold defaults to **`.cursor/benchmark/data/`** (see **`--gold-root`**).
- If the script fails, compute manually in the digest.

---

## 4. Gold alignment (when `data/<KEY>-gold.json` exists)

Load gold. Respect **`pipeline`**: `"prep"` | `"coverage"` | `"both"`.

### Prep checks

- **`required_requirement_keys_in_snippets`**: each key must appear in **every** prep run’s **`artifact`** with non-null **`snippet_text`** (or list failures per run label).
- **`structured_assertions.prep`** (preferred when present):
  - `required_snippet_keys`
  - `min_snippet_completion_rate`
  - `client_shell_source_in`
- **`structured_assertions.thresholds.prep`** (policy):
  - `min_snippet_completion_rate`
  - `max_missing_snippet_keys`
  - `require_client_shell_impact_stable`

### Coverage checks

- **`required_smart_checklist_substrings`**: default **each** coverage run’s combined checklist text contains all substrings.
- **`forbidden_checklist_regex`**: Python **`re.search`** against normalized full checklist body per run.
- **`structured_assertions.coverage`** (preferred when present):
  - `required_matrix_roles`
  - `min_core_bullet_count`
  - `required_out_of_scope_substrings`
  - `primary_focus_verbatim_required`
- **`structured_assertions.thresholds.coverage`** (policy):
  - `min_core_bullet_jaccard_avg`
  - `max_matrix_role_flip_count`
  - `min_primary_focus_verbatim_pass_rate`
  - `max_diagnostic_bullets_per_run`

Compatibility note: legacy substring/regex checks remain supported. For reduced false negatives, keep critical gates in structured assertions and treat string literals as supplemental.

### Sanitization checks (soft-fail policy)

- **`structured_assertions.sanitization`** may define:
  - `forbidden_regex`
  - `forbidden_substrings`
  - `allowed_exceptions`
  - `scan_targets`
- Crossref emits `sanitization` block with:
  - `evaluated`
  - `checks`
  - `violations` (redacted excerpts only)
  - `summary` (`status`, `violation_count`)
- **Soft-fail behavior**: sanitization violations do **not** stop metrics file generation, but should downgrade overall status (`thresholds.summary.status`) and be called out in digest.

---

## 5. Outputs (write files)

### Crossref

- **Coverage-bench root**: **`crossref/<KEY>-prep-metrics.json`**, **`crossref/<KEY>-coverage-metrics.json`** (optionally note **`suite_id`** in digest when suite-scoped).
- **Hub suite**: **`.cursor/benchmark/runs/<suite_id>/_aggregate/crossref/`** (same filenames).

Crossref now includes:

- `thresholds.summary` (pass/fail rollup)
- `sanitization.summary` (soft-fail content hygiene result)
- `trend` snapshot (latest history, deltas, regression flags)

History artifacts:

- **Hub / shared longitudinal**: **`.cursor/benchmark/history/<KEY>-prep-history.jsonl`** and **`<KEY>-coverage-history.jsonl`** (written when using **`--suite-run-dir`**).
- **Legacy-only** (benchmark-root under coverage-bench, no hub): **`.cursor/benchmark/coverage-bench/history/<KEY>-*-history.jsonl`**.

### Digest

- **Coverage-bench root:** **`digest/<KEY>-prep-digest.md`**, **`digest/<KEY>-coverage-digest.md`**
- **Hub (convention):** **`.cursor/benchmark/runs/<suite_id>/_aggregate/digest/`** — same basenames if authors split per-suite digests from global **`coverage-bench/digest/`**

Each digest **must** include:

1. **Executive summary**
2. **Runs included** — suite: path to each `run-*.json`; legacy: folder name + timestamp from **`meta.json`**
3. **Variance**
4. **Strong matches**
5. **Threshold status** (configured checks, failures, pass/fail summary)
6. **Sanitization status** (violations and soft-fail impact)
7. **Trend changes vs previous run** (delta and regression flags)
8. **Divergences**
9. **Optimization plan** — link evidence to epic-prep, coverage, templates, yogi-tool (**recommendations only**). Prefer **invariant- or role-shaped** suggestions for harness files (“when matrix role is ambiguous, coverage playbook should…”) over copy-pasting ticket-specific checklist lines. **Epic-only** deltas that are not yet portable → call out for **epic follow-up** ([`run-results/README.md`](../../run-results/README.md)) rather than implying a mandatory `coverage.md` edit.

---

## 6. Final user message

- Recap + links to **`crossref/*`** and **`digest/*`**.
- If gold missing: note **`.cursor/benchmark/data/<KEY>-gold.json`** (or legacy **`coverage-bench/data/`**).
