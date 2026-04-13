# Benchmark suite summary — `20260413-qa9f`

## Suite metadata

| Field | Value |
|--------|--------|
| **Suite id** | `20260413-qa9f` |
| **Epics** | CRT-585, CRT-632, CRT-638, CRT-669 |
| **Prep + coverage attempts per epic** | 3 |
| **`repo` / `focus`** | not set (`null`) |
| **Suite created (suite-meta)** | 2026-04-13T00:00:00Z |
| **Finalized** | 2026-04-13 (suite_finalize) |

Atomic run artifacts: `attempts/<EPIC>/run-001.json` … `run-006.json` (prep on odd seq, coverage on even seq).

---

## Per-epic artifacts

Paths are relative to this file (`runs/run-20260413-qa9f/`).

### CRT-585

| Kind | Digest | Crossref metrics |
|------|--------|------------------|
| Prep | [`../../digest/CRT-585-prep-digest.md`](../../digest/CRT-585-prep-digest.md) | [`../../crossref/CRT-585-prep-metrics.json`](../../crossref/CRT-585-prep-metrics.json) |
| Coverage | [`../../digest/CRT-585-coverage-digest.md`](../../digest/CRT-585-coverage-digest.md) | [`../../crossref/CRT-585-coverage-metrics.json`](../../crossref/CRT-585-coverage-metrics.json) |

### CRT-632

| Kind | Digest | Crossref metrics |
|------|--------|------------------|
| Prep | [`../../digest/CRT-632-prep-digest.md`](../../digest/CRT-632-prep-digest.md) | [`../../crossref/CRT-632-prep-metrics.json`](../../crossref/CRT-632-prep-metrics.json) |
| Coverage | [`../../digest/CRT-632-coverage-digest.md`](../../digest/CRT-632-coverage-digest.md) | [`../../crossref/CRT-632-coverage-metrics.json`](../../crossref/CRT-632-coverage-metrics.json) |

### CRT-638

| Kind | Digest | Crossref metrics |
|------|--------|------------------|
| Prep | [`../../digest/CRT-638-prep-digest.md`](../../digest/CRT-638-prep-digest.md) | [`../../crossref/CRT-638-prep-metrics.json`](../../crossref/CRT-638-prep-metrics.json) |
| Coverage | [`../../digest/CRT-638-coverage-digest.md`](../../digest/CRT-638-coverage-digest.md) | [`../../crossref/CRT-638-coverage-metrics.json`](../../crossref/CRT-638-coverage-metrics.json) |

### CRT-669

| Kind | Digest | Crossref metrics |
|------|--------|------------------|
| Prep | [`../../digest/CRT-669-prep-digest.md`](../../digest/CRT-669-prep-digest.md) | [`../../crossref/CRT-669-prep-metrics.json`](../../crossref/CRT-669-prep-metrics.json) |
| Coverage | [`../../digest/CRT-669-coverage-digest.md`](../../digest/CRT-669-coverage-digest.md) | [`../../crossref/CRT-669-coverage-metrics.json`](../../crossref/CRT-669-coverage-metrics.json) |

> **Note:** `compare_runs.py` was executed for each epic with `--suite-id 20260413-qa9f` at finalize time, refreshing the `crossref/*-metrics.json` files above.

---

## Rollup — variance highlights

- **CRT-585:** Requirement keys and non-null snippet hashes are stable across the three prep runs. Coverage checklist similarity is high (pairwise Jaccard about 0.94–0.97 across coverage attempts). Residual variance is mostly **matrix shape**: extra rows (`m-006b`, `m-017`) and different `verification_role` on edge rows between runs; two **weak** checklist bullets (XT roadmap / brokerage sync disclaimers) appear in only one attempt each.
- **CRT-632:** Prep **attempt 1** left several Yogi keys without `snippet_sha256` while attempts 2–3 agree on filled hashes for those keys — export or timing variance on first pass. Coverage **bullet_count** differs (22 vs 18) between first and later attempts; Jaccard between first and others is about **0.82**, while attempts 2–3 are identical (1.0). Weak bullets align with **MCP / snippet export failures** called out in the digest.
- **CRT-638:** Only two requirement keys; snippet hashes are stable. **`client_shell_impact_drift`** is true — `corner_trader` notes use different wording per run while status stays consistent. Coverage Jaccard about **0.92** pairwise; three alternate **“primary focus”** preamble bullets show up as weak / non-universal.
- **CRT-669:** Snippet hashes stable; **`client_shell_impact_drift`** true (evidence phrasing for WebBroker vs `qa_default_both` Adaptive). Coverage Jaccard about **0.93** (first vs others) and **1.0** between the last two runs; one bullet (**XT-7765 / cfd_stock retest**) appears in two of three coverage runs only.

---

## Corrections / optimization (hypotheses — recommendations only)

1. **`compare_runs` / suite files:** When scanning `run-*.json`, filter by `phase` (`prep` vs `coverage`) so metrics do not list half the files as errors; makes dashboards easier to read without changing captured artifacts.
2. **`benchmark-epic-prep` playbook:** Add an explicit step to **re-fetch or flag** requirements that return `mcp_export_failed` on first pass, so attempt 1 matches later attempts for snippet hashes (CRT-632 pattern).
3. **`benchmark-coverage` playbook:** Tighten guidance on **stable matrix row ids** and when to use `supporting` vs `out_of_epic`, to reduce CRT-585-style row churn that does not change checklist bullets much.
4. **`epic-ref` template / prep:** For `client_shell_impact`, offer a **short canonical sentence** plus optional free-text evidence to limit cosmetic drift while preserving Jira-backed status (CRT-638, CRT-669).
5. **Yogi tooling:** Add retry or batch export for keys that frequently fail MCP export in benchmark runs, shrinking “reason: snippet_text missing” weak bullets in coverage outputs.

---

## Suite status

All queue steps through **`suite_finalize`** are complete for this run folder. Use **`support/progress.json`** `next_step_index` ≥ `steps_total` to detect a finished suite programmatically.
