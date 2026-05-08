# CRT-669 coverage digest — suite `20260413-qa9f`

## 1. Executive summary

Three **coverage** snapshots (**run-002**, **run-004**, **run-006**) share the same **matrix backbone** (intersection includes **m-001**–**m-009** plus **m-010** `out_of_epic`). **Attempts 2 and 3** produced **identical** checklist bodies (length **4707**, Jaccard **1.0**); **attempt 1** is slightly shorter (**14** bullets vs **15**) and pairwise Jaccard **0.93** vs the others. One bullet—the **XT-7765 / CFD_STOCK retest** line—appears in **two of three** runs (**weak** in `bullet_frequency`). **Gold coverage checks pass:** every run’s `smart_checklist_markdown` contains all **`required_smart_checklist_substrings`**; **`forbidden_checklist_regex`** is empty.

## 2. Runs included

| Label | Path |
|-------|------|
| run-002 | `runs/run-20260413-qa9f/attempts/CRT-669/run-002.json` |
| run-004 | `runs/run-20260413-qa9f/attempts/CRT-669/run-004.json` |
| run-006 | `runs/run-20260413-qa9f/attempts/CRT-669/run-006.json` |

*(Excluded: `run-001`, `run-003`, `run-005` — `phase: prep`.)*

## 3. Variance

| Dimension | Observation |
|-----------|---------------|
| Bullet count | **14** (run-002) vs **15** (run-004, run-006). |
| Pairwise Jaccard | run-004 ↔ run-006 **1.0**; run-002 ↔ run-004 / run-002 ↔ run-006 **0.9333**. |
| Matrix rows | run-002: **9** primary + **m-010** out_of_epic. run-004/006: **10** primary (adds **m-011**) + **m-010** out_of_epic. |
| Bullet frequency | **14** bullets at frequency **3**; **1** bullet at frequency **2** (retest / XT-7765 note — missing from run-002). |

## 4. Strong matches

- **Core scenario bullets** (IPF field, defaults **CFD_FOREX_OTC** / **CFD_FOREX_DMA**, no default for plain CFD/CFD_STOCK, chunking rules, simultaneous orders, trading hours, completion, IN REVIEW, large position allowed, dxMC, WebBroker) appear in **all three** runs—see **`strong_bullets_all_runs`** in crossref.
- **Gold substrings** (**Liquidation**, **MAX_LIQUIDATION**, **CFD_FOREX_OTC**, **CFD_FOREX_DMA**, **CFD_FOREX**) are present in **every** coverage checklist.

## 5. Divergences

- **Optional retest bullet** (`[crt-1891] retest margin liquidation chunking… xt-7765…`) present in **run-004** and **run-006** only → only **weak** signal for that scenario across the suite.
- **Extra matrix row m-011** in run-004/run-006 aligns with the added bullet; run-002 omits both.
- **FX_SPOT** `out_of_epic` row (**m-010**) is **stable** across all runs.

## 6. Optimization plan

1. **[`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md)** / **Smart Checklist norms**: if **Jira validation comments** (e.g. XT-7765 retest) should always surface as checks, add an explicit step to **merge validation-field bullets** so they are not dropped in some attempts.
2. **Epic coverage template** ([`epics/templates/coverage-ref.json`](../../../epics/templates/coverage-ref.json)): encourage **requirement-tagged** scenario titles (gold **`checklist_notes`** already flags repeating epic title vs Yogi keys).
3. **Gold file** ([`data/CRT-669-gold.json`](../data/CRT-669-gold.json)): optional stricter check could require the **retest** substring if that scenario is mandatory for this epic; current gold only enforces **topic** substrings—**pass** as written.

---

**Crossref:** [`.cursor/benchmark/coverage-bench/crossref/CRT-669-coverage-metrics.json`](../crossref/CRT-669-coverage-metrics.json) (`suite_id`: `20260413-qa9f`).

**Gold (coverage):** [`.cursor/benchmark/coverage-bench/data/CRT-669-gold.json`](../data/CRT-669-gold.json) — **`required_smart_checklist_substrings`**: **pass** all runs; **`forbidden_checklist_regex`**: **n/a** (empty).
