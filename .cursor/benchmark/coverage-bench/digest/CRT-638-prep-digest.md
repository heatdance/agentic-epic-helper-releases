# CRT-638 prep digest — suite `20260413-qa9f`

## 1. Executive summary

Three **prep** snapshots (`run-001`, `run-003`, `run-005`) are **stable** on requirement keys **CRT-1744** and **CRT-1745**: same keys and identical normalized snippet SHA-256 hashes across runs. **`client_shell_impact`** is structurally consistent (Corner **affected**, Adaptive **not_applicable**) but the script flags **wording drift** in `note` / `evidence` strings between runs.

**Gold alignment (`data/CRT-638-gold.json`, prep checks): FAIL** — `required_requirement_keys_in_snippets` includes **CRT-1875**, which does **not** appear in **`artifact.requirements[]`** in any prep run (no row for that key, so no non-null `snippet_text`).

Metrics file: [crossref/CRT-638-prep-metrics.json](../crossref/CRT-638-prep-metrics.json).

## 2. Runs included

| Label | Path |
|--------|------|
| Prep 1 | `runs/run-20260413-qa9f/attempts/CRT-638/run-001.json` |
| Prep 2 | `runs/run-20260413-qa9f/attempts/CRT-638/run-003.json` |
| Prep 3 | `runs/run-20260413-qa9f/attempts/CRT-638/run-005.json` |

*(Excluded: `run-002`, `run-004`, `run-006` — `phase === "coverage"`.)*

## 3. Variance

- **Requirement keys**: none across prep runs — intersection is `{ CRT-1744, CRT-1745 }`.
- **Snippet hashes**: stable for both keys (see `snippet_hash_stable_across_all_runs` in crossref).
- **`client_shell_impact`**: `compare_runs.py` sets `client_shell_impact_drift: true` because free-text `note` / `evidence` differ while statuses match.

## 4. Strong matches

- Repeated capture of **CRT-1744** and **CRT-1745** with **ok** `snippet_status` and long `snippet_text` from CT page `342174235`.
- **Adaptive** consistently **not_applicable** with evidence pointing at **CRT-632** (matches epic scope in Jira).

## 5. Divergences

- **Gold vs prep**: **CRT-1875** required in gold but **absent** from all three prep `artifact.requirements[]` — either gold is ahead of prep scope, or epic-prep runs should add that requirement (Yogi/MCP) and re-snapshot.
- **`client_shell_impact` prose**: cosmetic variance only; no status flip between runs.

## 6. Optimization plan

1. **CRT-1875**: Decide whether it belongs in **CRT-638** epic-ref. If yes, extend **epic-prep** / Yogi pass to resolve **CRT-1875** with non-null `snippet_text` and re-run suite prep; if no, drop or adjust **`required_requirement_keys_in_snippets`** in `CRT-638-gold.json`.
2. **Stabilize `client_shell_impact`**: If drift is noise, tighten epic-prep instructions to copy a canonical phrasing from Jira fields; if intentional paraphrase is acceptable, treat `client_shell_impact_drift` as low priority.
3. Re-run **`PREP-VALIDATE: CRT-638 suite=20260413-qa9f`** (or a new suite) after changes; confirm [crossref/CRT-638-prep-metrics.json](../crossref/CRT-638-prep-metrics.json) shows `unstable_keys: []` and gold prep checks pass.
