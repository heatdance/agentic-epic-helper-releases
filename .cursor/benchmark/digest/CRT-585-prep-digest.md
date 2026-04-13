# CRT-585 — prep validation digest

**Suite:** `20260413-qa9f`  
**Crossref:** [`.cursor/benchmark/crossref/CRT-585-prep-metrics.json`](../crossref/CRT-585-prep-metrics.json)  
**Gold:** [`.cursor/benchmark/data/CRT-585-gold.json`](../data/CRT-585-gold.json) (`pipeline: both` — prep checks applied here)

---

## 1. Executive summary

Three prep snapshots for **CRT-585** under suite **20260413-qa9f** are **bit-for-bit consistent** on requirement keys, per-key snippet hashes, and `client_shell_impact`: **zero cross-run variance**. Optional **gold** prep rules **do not pass**: seven requirement keys mandated by gold still have **null** `snippet_text` in every prep run (same gap on all attempts).

---

## 2. Runs included

| Label | Path |
|-------|------|
| run-001 | `.cursor/benchmark/runs/run-20260413-qa9f/attempts/CRT-585/run-001.json` |
| run-003 | `.cursor/benchmark/runs/run-20260413-qa9f/attempts/CRT-585/run-003.json` |
| run-005 | `.cursor/benchmark/runs/run-20260413-qa9f/attempts/CRT-585/run-005.json` |

*(Files `run-002`, `run-004`, `run-006` are coverage phase; excluded from prep metrics.)*

---

## 3. Variance

| Dimension | Result |
|-----------|--------|
| Requirement key set | **Identical** across all three prep runs (20 keys) |
| Snippet SHA-256 | **Stable** for every key that has a non-null snippet; **`unstable_keys`**: none |
| `client_shell_impact` | **No drift** (`client_shell_impact_drift`: false) |

---

## 4. Strong matches

- **Key intersection (all prep runs):** CRT-101, CRT-1473, CRT-1474, CRT-1480, CRT-1481, CRT-1522, CRT-1524, CRT-1526, CRT-1527, CRT-1528, CRT-1529, CRT-1530, CRT-1531, CRT-1533, CRT-1534, CRT-1598, CRT-1731, CRT-1732, CRT-1733, CRT-1734.
- **Snippet hashes** for populated snippets match across run-001 / run-003 / run-005 (see `snippet_hash_stable_across_all_runs` in crossref).

---

## 5. Divergences

- **Between prep attempts:** none detected (deterministic replay).
- **Gold vs snapshots:** see §7 — required keys with missing snippets are systematic, not run-specific.

---

## 6. Optimization plan

| Finding | Recommendation | Evidence |
|---------|----------------|----------|
| Null Yogi snippets for several requirements | Re-run **EPIC-PREP** / Yogi resolution for tags **CRT-101**, **CRT-1481**, **CRT-1522**, **CRT-1524**, **CRT-1531**, **CRT-1533**, **CRT-1732**; confirm anchors and macro output in Confluence | Gold `required_requirement_keys_in_snippets`; crossref `snippet_sha256` nulls |
| Low prep variance | Harness is stable for this epic; focus effort on **snippet completeness** rather than prompt temperature | `unstable_keys: []`, identical hashes |
| Coverage pass (next queue step) | Run **COVERAGE-VALIDATE: CRT-585 suite=20260413-qa9f** after validating checklist substrings against gold | [`.cursor/benchmark/pipeline/validator.md`](../pipeline/validator.md); gold `required_smart_checklist_substrings` |

Related playbooks: [`.cursor/benchmark/pipeline/benchmark-epic-prep.md`](../pipeline/benchmark-epic-prep.md), [`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md), [Yogi docs](../../../automation/docs/yogi-url-resolve.md).

---

## 7. Gold alignment (prep)

**Rule:** Each key in `required_requirement_keys_in_snippets` must have **non-null** `snippet_text` in **every** prep run.

**Failed keys** (null snippet in **all** of run-001, run-003, run-005):

- CRT-101  
- CRT-1481  
- CRT-1522  
- CRT-1524  
- CRT-1531  
- CRT-1533  
- CRT-1732  

**Passed:** All other keys in the gold list carry non-null snippets in every prep run (CRT-1473, CRT-1474, CRT-1480, CRT-1526, CRT-1527, CRT-1528, CRT-1529, CRT-1530, CRT-1534).

**Scope statement (gold):** *Incredibly difficult change to the system where a new instrument type is introduced…* — useful as a manual oracle; not auto-scored here.
