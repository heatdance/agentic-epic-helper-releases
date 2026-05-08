# CRT-617 — COVERAGE validate (suite `20260415-qa4e`)

## 1. Executive summary

Suite **20260415-qa4e** has **three** coverage snapshots for **CRT-617** (`run-002`, `run-004`, `run-006`). Deterministic comparison shows **no variance** in checklist-derived bullets (pairwise Jaccard **1.0**), matrix row ids and `verification_role`, or bullet counts (**14** strong bullets per run, **weak_bullets** empty). **Gold alignment** against **`.cursor/benchmark/coverage-bench/data/CRT-617-gold.json`** `required_smart_checklist_substrings` **fails on all three runs** for the **same five** literals: the generated Smart Checklist uses requirement-key sections and phrasing (`FIX-router`, `MARKET`/`LIMIT`/`STOP` inline) that do **not** contain the gold strings copied from the legacy reference checklist (e.g. `et-fix-router`, `## Market Orders` style headings). **`forbidden_checklist_regex`** is empty — no regex violations.

## 2. Runs included

| Label | Path |
|--------|------|
| run-002 | `.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/attempts/CRT-617/run-002.json` |
| run-004 | `.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/attempts/CRT-617/run-004.json` |
| run-006 | `.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/attempts/CRT-617/run-006.json` |

Checklist source: `artifact.smart_checklist_markdown` (matches `checklist_markdown` on wrapper in sampled file).

## 3. Variance

| Signal | Result |
|--------|--------|
| Pairwise Jaccard (checklist bullets) | **1.0** for every pair (`run-002`↔`run-004`, `run-002`↔`run-006`, `run-004`↔`run-006`) |
| `bullet_count` | **14** each run |
| `matrix_rows` | Identical **m-001** … **m-006** with same `verification_role` (**m-003** = `out_of_epic`) |
| `matrix_intersection` | Matches each per-run matrix |
| `weak_bullets` | **[]** |

Crossref: **`.cursor/benchmark/coverage-bench/crossref/CRT-617-coverage-metrics.json`** (`suite_id: 20260415-qa4e`).

## 4. Strong matches

- **Cross-run stability**: All **14** normalized bullets appear in **`strong_bullets_all_runs`** with frequency **3** — zero wording drift across attempts.
- **Coverage structure**: Six-row **coverage_matrix** with explicit **out_of_epic** forward fork on **m-003** is stable; aligns with playbook intent for mixed archetype + scope boundaries.
- **Semantic coverage** (from stable bullets): FIXT.1.1 / logon / BE proxy, NewOrderMultileg vs NewOrderSingle, ExecutionReport, ET routing (CRT-1760), tag tables (CRT-1759), extensions (CRT-1765), persistence (CRT-1877/1881), WebBroker/dxTrade5/Adaptive surfaces, partial-fill non-goal, ops logging.

## 5. Divergences

- **Between runs**: **None** on metrics emitted by `compare_runs.py`.
- **Gold vs generated checklist** (substring match, all runs): **missing** from combined checklist body:
  - `et-fix-router` — artifact uses **“FIX-router”** / service naming in prose, not the literal **`et-fix-router`** token from gold `reference_checklist`.
  - `Market Orders`, `Limit Orders`, `Stop Orders` — gold reflects **## Market/Limit/Stop Orders** section titles; Smart Checklist groups by **requirement keys** and inline **MARKET** / **LIMIT/STOP** wording, not those exact heading strings.
  - `Common FIX Validation` — not present as a section title in the Smart Checklist spine.

**Forbidden regex**: `forbidden_checklist_regex` is **[]** — no matches to report.

## 6. Optimization plan

1. **Reconcile gold with COVERAGE output** — Either **relax or rewrite** `required_smart_checklist_substrings` in **`data/CRT-617-gold.json`** to match the **coverage.md** / Smart Checklist shape (requirement-tagged sections), **or** extend the coverage pipeline to inject an **operator preconditions** block that literally includes **`et-fix-router`** and order-type section labels if those strings must remain as contract tests.
2. **Keep using `reference_checklist` for human QA** — The gold file’s long `reference_checklist` remains a useful manual oracle even when substring gates do not match the condensed Smart Checklist.
3. **Bitbucket 404** — Same as prep validate: **`anti_pattern_findings`** note **`bitbucket_search_unavailable`**; restoring code search would allow **`implementation_hit_ids`** in later COVERAGE runs (see **`.cursor/pipelines/coverage.md`** phase 7).
4. **Suite finalize** — After digest review, run **`BENCHMARK-NEXT: 20260415-qa4e`** per **`.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/support/QUEUE.md`** step 9 and **`.cursor/benchmark/coverage-bench/pipeline/benchmark-suite.md`** §4.

---

**Artifacts**: [crossref/CRT-617-coverage-metrics.json](../crossref/CRT-617-coverage-metrics.json) · [data/CRT-617-gold.json](../data/CRT-617-gold.json)
