# CRT-585 — coverage validation digest

**Suite:** `20260413-qa9f`  
**Crossref:** [`.cursor/benchmark/crossref/CRT-585-coverage-metrics.json`](../crossref/CRT-585-coverage-metrics.json)  
**Gold:** [`.cursor/benchmark/data/CRT-585-gold.json`](../data/CRT-585-gold.json) (`pipeline: both` — coverage checks applied here)

---

## 1. Executive summary

Three coverage snapshots agree on **most** Smart Checklist bullets (**32** appear in **all** runs; pairwise **Jaccard** ≈ **0.94–0.97**). **Structural drift** shows up in the **coverage matrix**: run-002 has **16** rows (one `out_of_epic`); run-004 and run-006 add extra rows (`m-016` / `m-017`, and run-006 adds **`m-006b`**). **Bullet counts** differ slightly (**34** vs **35**). **Gold** substring and forbidden-regex checks **pass** for every coverage run.

---

## 2. Runs included

| Label | Path |
|-------|------|
| run-002 | `.cursor/benchmark/runs/run-20260413-qa9f/attempts/CRT-585/run-002.json` |
| run-004 | `.cursor/benchmark/runs/run-20260413-qa9f/attempts/CRT-585/run-004.json` |
| run-006 | `.cursor/benchmark/runs/run-20260413-qa9f/attempts/CRT-585/run-006.json` |

---

## 3. Variance

| Metric | run-002 | run-004 | run-006 |
|--------|---------|---------|---------|
| Checklist bullets (parsed) | 34 | 35 | 35 |
| Matrix rows | 16 | 17 | 18 |
| `out_of_epic` row id | m-016 | m-017 | m-017 |

**Pairwise Jaccard** (bullet sets): run-002↔run-004 **0.9714**; run-002↔run-006 **0.9714**; run-004↔run-006 **0.9444**.

**Matrix intersection (all runs):** `m-001` … `m-015` with `verification_role: primary` — **15** rows stable; runs diverge on **splitting** / **supporting** / **out_of_epic** rows beyond that core.

**Weak bullets** (present in **one** run only, per crossref): two **XT** epic-ref disclaimers (**brokerage requirements sync** `402589756`, **roadmap breakdown** `402589824`).

---

## 4. Strong matches

- **32 bullets** in `strong_bullets_all_runs` (crossref) — consistent narrative across IPF, console, WebBroker, jobs, EOD, Adaptive, and CRT-585-tagged surfaces.
- **Stable matrix spine:** `m-001`–`m-015` **primary** rows align on capabilities (IPF subtype/fields, static list, console config, WebBroker admin/client, gating, EOD, CFD Parameters job, Adaptive).

---

## 5. Divergences

- **Extra matrix rows** in later attempts: `m-016` as **supporting** (run-004) vs **out_of_epic** only in run-002; run-006 introduces **`m-006b`** (**supporting**) alongside **`m-006`** (**primary**).
- **Optional XT caveat bullets** appear in **one** run each — low frequency, flagged as weak ties in checklist wording.

---

## 6. Optimization plan

| Finding | Recommendation | Evidence |
|---------|----------------|----------|
| Matrix row count / role drift | Tighten **coverage.md** guidance on when to emit **supporting** vs **out_of_epic** for traversal-only XT pages; pin matrix **id** scheme so optional rows do not reorder core **m-00x** | Per-run `matrix_rows` in crossref |
| Bullet count 34 vs 35 | Diff checklist bodies between run-002 and run-004/006 to find the **extra** bullet; decide if it should be **deterministic** (always on) or **conditional** | `bullet_count` + `bullet_frequency` |
| High Jaccard, low structural variance | Prompt / template is **stable** for narrative; invest in **matrix schema** consistency if automation consumes JSON | Jaccard ≥ 0.94 |

Playbooks: [`.cursor/benchmark/pipeline/benchmark-coverage.md`](../pipeline/benchmark-coverage.md), [`.cursor/pipelines/coverage.md`](../../pipelines/coverage.md).

---

## 7. Gold alignment (coverage)

| Check | Result |
|--------|--------|
| `required_smart_checklist_substrings` (**FX_SPOT**, **FOREX**, **Console**, **WebBroker**, **IPF**, **CRT-585**) | **Pass** — all six substrings present in combined checklist text for **run-002**, **run-004**, **run-006** (case-sensitive match on raw markdown). |
| `forbidden_checklist_regex` | **N/A** (empty list) — no violations. |

**Manual context (not auto-scored):** Gold `checklist_notes` and `reference_checklist` describe desired checklist shape (components, examples, requirement references); use for human review alongside [`CRT-585-prep-digest.md`](CRT-585-prep-digest.md).
