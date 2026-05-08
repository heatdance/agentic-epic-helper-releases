# CRT-617 — PREP validate (suite `20260415-qa4e`)

## 1. Executive summary

Suite **20260415-qa4e** has **three** epic-prep snapshots for **CRT-617** (`run-001`, `run-003`, `run-005`). Deterministic comparison shows **no variance** in requirement key set, per-key Yogi/snippet SHA-256 hashes, or `client_shell_impact`. Gold file **`.cursor/benchmark/coverage-bench/data/CRT-617-gold.json`** has `required_requirement_keys_in_snippets: []` for prep, so **no additional snippet-key gold checks** apply. Prep quality for this suite is **stable and reproducible** at the measured signals.

## 2. Runs included

| Label | Path |
|--------|------|
| run-001 | `.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/attempts/CRT-617/run-001.json` |
| run-003 | `.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/attempts/CRT-617/run-003.json` |
| run-005 | `.cursor/benchmark/coverage-bench/runs/run-20260415-qa4e/attempts/CRT-617/run-005.json` |

Each record: `phase: prep`, non-null `artifact` (epic-ref snapshot).

## 3. Variance

| Signal | Result |
|--------|--------|
| `requirements[]` keys (intersection across all runs) | `CRT-1756`, `CRT-1757`, `CRT-1759`, `CRT-1760`, `CRT-1765`, `CRT-1877`, `CRT-1881` (7 keys, same on every run) |
| Snippet SHA-256 per key | **Identical** across all three runs for all seven keys |
| `unstable_keys` (hash mismatch across runs) | **None** |
| `client_shell_impact` | **No drift** — same structure and `qa_default_both` sourcing on every run |
| `meta.agent_summary` | Wording differs slightly (process narrative only); **artifact** content aligned |

Crossref: **`.cursor/benchmark/coverage-bench/crossref/CRT-617-prep-metrics.json`** (`suite_id: 20260415-qa4e`).

## 4. Strong matches

- **Requirement coverage**: Seven Jira-linked requirement keys consistently present with **non-null** snippets and **stable** normalized text hashes — indicates repeatable Yogi/MCP storage path (CT pages **529180233**, **345721535** per validation logs).
- **XT traversal**: Eight `xt_refs` retained across runs (per run `validation_log` / synthesis scope).
- **Implementation hits**: Empty in all runs for the **same** documented reason — `bitbucket_search_code` HTTP **404**; `skipped_reason` and `BRO/xt` default consistent — so **no Bitbucket-driven variance** (also no false-positive hit churn).

## 5. Divergences

- **Structured prep artifact**: **None** detected between runs at the metrics in `CRT-617-prep-metrics.json`.
- **Operational narrative only**: `meta.agent_summary` strings differ in phrasing across attempts; this does not affect epic-ref `artifact` equivalence for the compared fields.

## 6. Optimization plan

1. **Bitbucket MCP / code search (404)** — Epic-prep step **5b** cannot populate `implementation.hits` until the Stash code-search integration is fixed or an alternate capped search path is used; see **`.cursor/pipelines/epic-prep.md`** step 5b and benchmark playbook **`.cursor/benchmark/coverage-bench/pipeline/benchmark-epic-prep.md`**. COVERAGE phase 7 will still expect deduped hits when the tool works.
2. **`client_shell_impact`** — Still **`qa_default_both`** with `evidence: none_found`. If Jira or Confluence ever states Adaptive exclusion, tighten epic-prep rules so status is **tool-backed** rather than default-only (see **`epics/templates/epic-ref.json`** / **`docs/qa-project.json`**).
3. **Gold for prep** — `required_requirement_keys_in_snippets` is empty; if the team wants enforced snippet presence for specific keys, add them to **`.cursor/benchmark/coverage-bench/data/CRT-617-gold.json`** and re-run **PREP-VALIDATE** after future suite runs.
4. **Yogi UTF-8** — Later runs’ summaries mention UTF-8 handling for **CRT-1756** / **CRT-1757**; hashes are already stable; keep **automation/tools/yogi-tool/** subprocess encoding consistent to avoid future hash drift on similar tickets.

---

**Artifacts**: [crossref/CRT-617-prep-metrics.json](../crossref/CRT-617-prep-metrics.json) · [data/CRT-617-gold.json](../data/CRT-617-gold.json) (prep snippet list empty)

**Next queue step** (per `support/QUEUE.md`): **`COVERAGE-VALIDATE: CRT-617 suite=20260415-qa4e`**.
