# Benchmark run report — `20260508-ct01`

## Evidence and scope

- **Fork:** `combined` (epic prep + coverage + test-prep per hub attempt).
- **Epic keys:** CRT-639.
- **Metrics:** `.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/` — `CRT-639-prep-metrics.json`, `CRT-639-coverage-metrics.json`, `CRT-639-test-metrics.json`.
- **Shadow snapshots:** `.cursor/benchmark/runs/20260508-ct01/attempt-<nn>/shadow/CRT-639/`.
- **This report:** `.cursor/benchmark/run-results/20260508-ct01/report.md`.
- **Gold:** `.cursor/benchmark/data/CRT-639-gold.json` (prep/coverage gate checks applied where noted in crossref).

## Epic-scoped observations

### Variance methodology

**`fresh-session stochasticity`** — each `CONTROL_HUB.md` row ran as its own cold session; `benchmark_suite=20260508-ct01` and `benchmark_attempt=1…3` held constant per run index. Interpret spread in coverage bullets and client-shell prose as **session noise + LLM stochasticity**, not replay.

### Gold vs runs

| Phase | Source | Outcome (summary) |
|--------|--------|-------------------|
| Prep | `CRT-639-prep-metrics.json` `gold_checks` | Structured snippet keys and `min_snippet_completion_rate` **pass** (1.0 across runs). Legacy and sanitization pass. Threshold **`require_client_shell_impact_stable`** **fails** (`client_shell_impact_drift`: true; per-run `client_shell_impact` **note** / **evidence** strings differ). |
| Coverage | `CRT-639-coverage-metrics.json` | `min_core_bullet_jaccard_avg` **0.0** (threshold ≥ 0.9 **fail**). **`max_matrix_role_flip_count`** **3** (threshold ≤ 1 **fail**). Gold legacy: **`required_smart_checklist_substrings`**: missing **`account group`** on `attempt-01` and `attempt-03`. Gold structured: **`required_out_of_scope_substrings`** missing **`out of epic`** on `attempt-01`. **`primary_focus_verbatim_pass_rate`** **1.0** (**pass**). |
| Test | `CRT-639-test-metrics.json` | Gold `pipeline_not_applicable`; thresholds **not_configured**. **`test_bundle_count_by_run`**: 5 / 3 / 3. **`temp_path_fragment_violation_run_count`**: **1** (`attempt-01__shadow-test`: `temp_path_fragment_in_json` true). All runs **`subprocess_completed_rate`** **1.0**; **`tests_md_missing_run_count`** **0**. |

### Variance interpretation

Coverage **pairwise Jaccard** is **0.0** across all shadow attempts — checklists are **semantically non-overlapping at the string level** even when **primary-focus verbatim** passes. Combined with **matrix role flips** (m-003 / m-004 / m-006 roles change **primary** vs **out_of_epic** / **supporting** between runs), the numeric **“stability”** gates are **strict for this stochasticity mode**. Treat **jaccard** as “verbatim bullet churn” and consider **normalized** or **semantic** overlap for future gold if the intent is stability of *meaning* rather than *exact line text*.

## Pipeline increments (structured)

#### CR-20260508-ct01-001

- **Target:** `.cursor/pipelines/coverage.md` (and/or gold `CRT-639-gold.json` coverage thresholds)
- **Trigger:** `.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/CRT-639-coverage-metrics.json` — `thresholds.checks`: **`min_core_bullet_jaccard_avg`** actual **0.0** (expected ≥ **0.9**); **`max_matrix_role_flip_count`** actual **3** (expected ≤ **1**). Gold: `required_smart_checklist_substrings` missing **`account group`**; `required_out_of_scope_substrings` missing **`out of epic`** on **attempt-01**.
- **Hypothesis:** One cold **COVERAGE** session per row produces **large bullet wording drift** and **matrix classification drift**; strict verbatim Jaccard and role-flip caps are miscalibrated for **fresh-session** benchmarks unless the playbook constrains *structure* (matrix IDs, OOS labeling) more tightly.
- **Proposed edit:** Add explicit guidance: preserve **stable matrix row IDs** and **verification_role** semantics per spec; require a **single canonical** phrase for **out-of-epic** rows if gold substring checks depend on it; separate **“exploratory diagnostic bullets”** from **core** bullets so core Jaccard is comparable across runs.
- **Generalization check:** Applies to any epic with a **requirement×shell** matrix; validate on a **second epic key** before tightening gold thresholds globally.
- **Verify:** `python automation/tools/benchmark_aggregate.py --suite-dir .cursor/benchmark/runs/20260508-ct01`

#### CR-20260508-ct01-002

- **Target:** `.cursor/pipelines/epic-prep.md` (client shell / digest normalization)
- **Trigger:** `.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/CRT-639-prep-metrics.json` — **`require_client_shell_impact_stable`** **fail**; `kpis.client_shell_impact_drift` **true** despite **`snippet_sha256`** stable across runs.
- **Hypothesis:** **Narrative fields** in **`client_shell_impact`** (note/evidence) are **free-form**; models paraphrase **qa_default_both** explanations, tripping **stability** even when **affected** status is consistent.
- **Proposed edit:** Define **templated** note text for **`qa_default_both`** (or gate stability on **status + source** only, not prose), and document that **evidence** should prefer **`none_found`** or **enumerated** tokens over long prose when drift-sensitive gates are on.
- **Generalization check:** Any epic using default-both client rules; confirm on **≥2** keys if used as a CI gate.
- **Verify:** Same as CR-001 prep: `benchmark_aggregate.py`; optional gold tweak **`require_client_shell_impact_stable`** semantics in `CRT-639-gold.json` if product owners accept **semantic** stability only.

#### CR-20260508-ct01-003

- **Target:** `.cursor/pipelines/test-prep.md` (durable JSON hygiene)
- **Trigger:** `.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/CRT-639-test-metrics.json` — `kpis.temp_path_fragment_violation_run_count` **1**; `per_run.attempt-01__shadow-test.temp_path_fragment_in_json` **true**.
- **Hypothesis:** **`CRT-639-tests.json`** for **attempt-01** still **embeds or references** a **`temp/`** path fragment; downstream compares treat that as a **hygiene violation**.
- **Proposed edit:** Reinforce **finalize step**: rewrite or relocate paths so **durable** JSON contains only **EpicDir-resident** paths (no `temp/` segments in published fields).
- **Generalization check:** All epics with multi-bundle test-prep; same rule as `qa-artifacts` temp discipline.
- **Verify:** Re-run `python .cursor/benchmark/coverage-bench/scripts/compare_runs.py --epic CRT-639 --kind test --suite-run-dir .cursor/benchmark/runs/20260508-ct01` and confirm **`temp_path_fragment_violation_run_count`** **0**.

## Metrics snapshot

Authoritative JSON: `.cursor/benchmark/runs/20260508-ct01/_aggregate/crossref/CRT-639-{prep,coverage,test}-metrics.json` (see **Gold vs runs** table above for headline KPIs).

## Generalized pipeline recommendations

1. **Coverage stability:** For hub **fresh-session** runs, treat **core bullet Jaccard** as a **diagnostic** unless the playbook **forces** normalized bullets (IDs, stable headings). Consider gold thresholds that use **matrix_intersection** + **primary_focus_verbatim** before **raw Jaccard**, or document that **0.0 Jaccard** is **expected** under verbatim tokenization.

2. **Prep client-shell:** Split **machine-stable** fields (**status**, **source**) from **human-readable** notes for drift-sensitive benchmarks, or disable **`require_client_shell_impact_stable`** in gold when only narrative drift occurs.

3. **Test-prep:** Add an explicit **path scrub** before **`DONE.json`**: no **`temp/`** path fragments in **`CRT-639-tests.json`** (attempt-01 violation in this suite).

**Generalization checklist:** Recommendations 1–3 are epic-agnostic; **CRT-639-only** gold substring lists (e.g. **`account group`**) belong under **Epic-local follow-ups** until repro’d on another key.

## Epic-local follow-ups

- **Gold substrings:** **`account group`** missed in **two** coverage runs — confirm whether the checklist **must** literally contain that phrase or relax gold to **structured** matrix checks only.
- **Out-of-scope labeling:** **`out of epic`** substring missing on **attempt-01** — align **`COVERAGE:`** output template with gold or adjust gold to match documented **matrix** exports instead of free-text substrings.
- **Test bundle count:** **5** vs **3** bundles between attempt-01 and attempts 02–03 — expected if coverage inputs differed; if not, trace **bundle split** rules in shadow **`CRT-639-tests.json`** for attempt-01 only.
