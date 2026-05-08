# CRT-632 coverage digest — suite `20260413-qa9f`

## 1. Executive summary

Three **coverage** snapshots exist for **CRT-632** under suite **20260413-qa9f**. The **coverage matrix** is **identical** across runs (same 13 rows, including **m-010** as **out_of_epic**). **Checklist bullet sets** match between **run-004** and **run-006**; **run-002** adds **four** diagnostic lines for missing epic-ref snippets, lowering pairwise Jaccard vs the other two. **Gold coverage checks pass**: all **`required_smart_checklist_substrings`** appear in **every** run’s checklist body; **`forbidden_checklist_regex`** is empty.

Metrics: [`.cursor/benchmark/coverage-bench/crossref/CRT-632-coverage-metrics.json`](../crossref/CRT-632-coverage-metrics.json). Gold: [`data/CRT-632-gold.json`](../data/CRT-632-gold.json).

## 2. Runs included

Coverage phase only (`phase === "coverage"`, `artifact` present):

| Label | Path |
|-------|------|
| run-002 | `runs/run-20260413-qa9f/attempts/CRT-632/run-002.json` |
| run-004 | `runs/run-20260413-qa9f/attempts/CRT-632/run-004.json` |
| run-006 | `runs/run-20260413-qa9f/attempts/CRT-632/run-006.json` |

## 3. Variance

| Dimension | Finding |
|-----------|---------|
| **Bullet count** (markdown `- ` lines used by `compare_runs.py`) | **run-002**: 22; **run-004** / **run-006**: 18 each. |
| **Pairwise Jaccard** (normalized bullet text) | run-002 ↔ run-004 / run-006: **0.8182**; run-004 ↔ run-006: **1.0**. |
| **Matrix rows** `(id, verification_role)` | **Same** in all three runs; **intersection** = full set (13 rows). |
| **Weak bullets** (not in all runs) | Four `! reason: snippet_text missing for …` lines **only** in **run-002** (ties to prep variance on attempt 1). |

## 4. Strong matches

- **18** checklist bullets appear in **all three** coverage runs (see `strong_bullets_all_runs` in crossref), including epic-scoped Adaptive FX_SPOT threads for Search, Recently Viewed, Watchlist, and Instrument page.
- **Coverage matrix** and **verification_role** assignments are **stable** across runs.

## 5. Divergences

1. **run-002** extra bullets document **DXINV-285**, **DXINV-CB-4**, **DXINV-CB-91**, **DXINV-CB-309** snippet gaps from epic-ref; **run-004** and **run-006** omit those lines (prep had filled snippets by then).
2. **Bullet-count delta** is **noise for structural quality**—content overlap is still high (Jaccard **0.82** vs **1.0** between later attempts).

**Gold (coverage)** — `data/CRT-632-gold.json`: **`required_smart_checklist_substrings`** (**FX_SPOT**, **FX Spot**, **Search**, **Watchlist**, **Instrument**, **Adaptive**) **pass** in **run-002**, **run-004**, and **run-006** (`artifact.smart_checklist_markdown` / wrapper). **`forbidden_checklist_regex`** is empty (no checks).

## 6. Optimization plan

| Item | Evidence | Suggestion |
|------|----------|------------|
| Checklist variance from `! reason` lines | Weak bullets frequency **1** vs **3** | Optionally **normalize** coverage output: put snippet-gap notes in **`meta.agent_summary`** or a fixed appendix so **bullet Jaccard** reflects test intent only. |
| Prep ↔ coverage coupling | run-002 diagnostics match **PREP-VALIDATE** failures on attempt 1 | Keep **snippet completeness** in epic-ref before coverage, per [`.cursor/pipelines/coverage.md`](../../.cursor/pipelines/coverage.md) / [`.cursor/pipelines/epic-prep.md`](../../.cursor/pipelines/epic-prep.md). |
| Matrix stability | Intersection equals full matrix | **No change required** for matrix generation—good **determinism** across attempts. |

---

*Generated for **COVERAGE-VALIDATE: CRT-632 suite=20260413-qa9f**.*

