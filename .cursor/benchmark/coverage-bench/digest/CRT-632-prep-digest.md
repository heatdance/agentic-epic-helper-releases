# CRT-632 prep digest — suite `20260413-qa9f`

## 1. Executive summary

Three **prep** snapshots exist for **CRT-632** under suite **20260413-qa9f**. **Yogi snippets are complete and consistent on attempts 2 and 3**, but **attempt 1** left **four** gold-required requirement keys with **null** `snippet_text`. **`client_shell_impact`** is **unchanged** across all three prep runs. **Gold prep alignment fails** for **`runs/run-20260413-qa9f/attempts/CRT-632/run-001.json`** only.

Metrics: [`.cursor/benchmark/coverage-bench/crossref/CRT-632-prep-metrics.json`](../crossref/CRT-632-prep-metrics.json). Gold: [`data/CRT-632-gold.json`](../data/CRT-632-gold.json).

## 2. Runs included

Prep phase only (per validator: `phase === "prep"` and `artifact` object):

| Label | Path |
|-------|------|
| run-001 | `runs/run-20260413-qa9f/attempts/CRT-632/run-001.json` |
| run-003 | `runs/run-20260413-qa9f/attempts/CRT-632/run-003.json` |
| run-005 | `runs/run-20260413-qa9f/attempts/CRT-632/run-005.json` |

Other files in the same folder (`run-002`, `run-004`, `run-006`) are **coverage** steps and are out of scope for **PREP-VALIDATE**.

## 3. Variance

| Dimension | Finding |
|-----------|---------|
| Requirement key set | **12** keys per prep run; **11** match gold `required_requirement_keys_in_snippets` plus extra **DXINV-CB-34** (not listed in gold). |
| Snippet presence | **run-001**: null snippets for **DXINV-285**, **DXINV-CB-4**, **DXINV-CB-91**, **DXINV-CB-309**. **run-003** and **run-005**: all gold keys have non-null snippets. |
| Snippet content (SHA256, normalized) | For keys present with text in **all three** runs, hashes **match** (see `snippet_hash_stable_across_all_runs` in crossref). |
| `client_shell_impact` | **No drift** (`client_shell_impact_drift`: false). |

## 4. Strong matches

- **Stable snippet hashes** (when non-null in every prep run): DXINV-174, DXINV-CB-206, DXINV-CB-25, DXINV-CB-27, DXINV-CB-29, DXINV-CB-308, DXINV-CB-315, DXINV-CB-34.
- **Identical `client_shell_impact`** narrative: Corner Trader **not_applicable**, Adaptive **affected**, sourced from Jira.

## 5. Divergences

1. **Gold failure (prep)** — `required_requirement_keys_in_snippets`: **run-001** missing non-null snippets for **DXINV-285**, **DXINV-CB-4**, **DXINV-CB-91**, **DXINV-CB-309**. **run-003** and **run-005** pass.
2. **Extra requirement** **DXINV-CB-34** appears in all three prep artifacts but is **not** in the gold required-key list (informational; not a gold violation).

## 6. Optimization plan

| Item | Evidence | Suggestion |
|------|----------|------------|
| First-run snippet gaps | run-001 nulls vs run-003/run-005 filled | In **EPIC-PREP** / **BENCHMARK-EPIC-PREP**, add an explicit **snippet completeness gate** before writing the snapshot (re-run Yogi for any `snippet_text` still null). |
| Root cause | Same keys eventually resolve | Treat as **agent/tool variance** or **ordering** (late Yogi calls); compare timestamps or step logs in the original chat if retained. |
| Tooling | Yogi resolution | Prefer [`automation/docs/yogi-url-resolve.md`](../../automation/docs/yogi-url-resolve.md) + [`automation/tools/yogi-tool/`](../../automation/tools/yogi-tool/) for deterministic small snippets. |
| Template | epic-ref shape | Align with [`epics/templates/epic-ref.json`](../../epics/templates/epic-ref.json) and [`.cursor/pipelines/epic-prep.md`](../../.cursor/pipelines/epic-prep.md) so `requirements[].snippet_text` is mandatory before “done”. |

---

*Generated for **PREP-VALIDATE: CRT-632 suite=20260413-qa9f**.*
