# CRT-669 prep digest — suite `20260413-qa9f`

## 1. Executive summary

All three prep snapshots agree on **three** linked requirements (**CRT-1126**, **CRT-1785**, **CRT-1891**) with **identical normalized snippet hashes** per key—structural prep output is **stable** across runs. **`client_shell_impact`** is flagged as **drifting** by metrics because **run-001** uses slightly different prose for Corner/Adaptive notes than **run-003** and **run-005**, while **status** values stay **`affected`** / **`qa_default_both`**. Gold file **`.cursor/benchmark/data/CRT-669-gold.json`** has an empty **`required_requirement_keys_in_snippets`** list, so **prep gold alignment passes** (no per-key snippet assertions).

## 2. Runs included

| Label | Path |
|-------|------|
| run-001 | `runs/run-20260413-qa9f/attempts/CRT-669/run-001.json` |
| run-003 | `runs/run-20260413-qa9f/attempts/CRT-669/run-003.json` |
| run-005 | `runs/run-20260413-qa9f/attempts/CRT-669/run-005.json` |

*(Excluded: `run-002`, `run-004`, `run-006` — `phase: coverage`.)*

## 3. Variance

| Dimension | Observation |
|-----------|-------------|
| Requirement keys | Intersection across prep runs: **CRT-1126**, **CRT-1785**, **CRT-1891** (3 keys each run). |
| Snippet text | **Stable**: same SHA-256 per key on all three prep runs (`unstable_keys`: **none**). |
| `client_shell_impact` | **Wording variance** between attempt 1 vs 2/3 notes; **no** status flip between runs. |

## 4. Strong matches

- **Requirement set** and **snippet hashes** are **fully aligned** across all prep attempts—good for reproducible epic-ref content.
- **Synthesis keywords** and problem framing (MAX_LIQUIDATION_QTY, CFD subtypes, dxMC, WebBroker) are consistent with the epic scope.

## 5. Divergences

- **`client_shell_impact` drift** (metric `client_shell_impact_drift: true`): run-001’s `corner_trader.note` / `adaptive.note` differ in phrasing from run-003/run-005; evidence strings also differ slightly (e.g. explicit Jira quote vs “Epic text and validation comment…”).
- This is **narrative variance**, not contradictory client classification—all runs keep both shells **`affected`** with **`source: qa_default_both`**.

## 6. Optimization plan

1. **Epic-prep playbook** ([`.cursor/pipelines/epic-prep.md`](../../pipelines/epic-prep.md)): add or tighten guidance so **`client_shell_impact` notes** use a **single template** when evidence is the same (e.g. always cite the same Jira field phrasing or always the same “silent on Adaptive → qa_default_both” line) to reduce cosmetic drift in benchmarks.
2. **Yogi / snippets** ([`automation/docs/yogi-url-resolve.md`](../../../automation/docs/yogi-url-resolve.md), [`yogi-tool/`](../../../automation/tools/yogi-tool/)): run-001 meta notes **yogi_snippet** failure for CRT-1891 (`macro_end_not_found`) with **Confluence MCP fallback**—if macro extraction is flaky, document the fallback path in epic-prep so agents don’t treat it as an error state across runs.
3. **Gold**: optional future **`required_requirement_keys_in_snippets`** entries would enforce non-null snippets for chosen Yogi keys; current gold intentionally leaves this empty for Confluence-only links.

---

**Crossref:** [`.cursor/benchmark/crossref/CRT-669-prep-metrics.json`](../crossref/CRT-669-prep-metrics.json) (`suite_id`: `20260413-qa9f`).

**Gold:** [`.cursor/benchmark/data/CRT-669-gold.json`](../data/CRT-669-gold.json) — prep checks **pass** (empty required snippet keys).
