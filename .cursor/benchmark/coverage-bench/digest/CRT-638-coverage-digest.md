# CRT-638 coverage digest — suite `20260413-qa9f`

## 1. Executive summary

Three **coverage** snapshots (`run-002`, `run-004`, `run-006`) share the same **verification matrix** shape (five rows: three **primary**, one **supporting**, one **out_of_epic**) and **24** bullets each after normalization. **Pairwise Jaccard** between any two runs is **0.92** — almost all checklist bullets repeat across runs; **three** distinct **primary-focus** lines appear once each across the trio (see `weak_bullets` in crossref).

**Gold alignment (`data/CRT-638-gold.json`, coverage checks): PARTIAL FAIL** — `required_smart_checklist_substrings` includes the exact substring **`Instrument Suggestion`** (capital **S**). None of the three runs’ `smart_checklist_markdown` / `checklist_markdown` bodies contain that exact string; they use **`instrument suggestion`** (lowercase **s**) and headings like **`## Instrument suggestion —`**. All other required substrings (**`FX_SPOT`**, **`FX Spot`**, **`dxTrade5`**, **`WebBroker`**) are present in every run. **`forbidden_checklist_regex`** is empty — no forbidden-pattern checks.

Metrics: [crossref/CRT-638-coverage-metrics.json](../crossref/CRT-638-coverage-metrics.json).

## 2. Runs included

| Label | Path |
|--------|------|
| Coverage 1 | `runs/run-20260413-qa9f/attempts/CRT-638/run-002.json` |
| Coverage 2 | `runs/run-20260413-qa9f/attempts/CRT-638/run-004.json` |
| Coverage 3 | `runs/run-20260413-qa9f/attempts/CRT-638/run-006.json` |

Checklist source per playbook: `artifact.smart_checklist_markdown` (present on these snapshots).

## 3. Variance

- **Matrix**: identical **id** / **verification_role** intersection across all three runs (`m-001` … `m-005`).
- **Bullets**: **22** bullets appear in **all** three runs (`strong_bullets_all_runs`); **2** runs share one primary-focus variant and one run differs — net **three** weak / low-frequency primary-focus strings (Jaccard **0.92**).
- **CRT-1875** appears in coverage bullets in all runs (prep gold gap remains a prep-only issue).

## 4. Strong matches

- Stable widget split (**dxTrade5** vs **WebBroker**), **All** / **FX Spot** tab scenarios, column filters, **IPF** consistency, permissions, **XT-7667/7668/7530** epic-validation line.
- Shared structure: section title pattern `dxTrade5 / WebBroker`, design link, widget callouts.

## 5. Divergences

- **Wording-only** variance in the opening **primary focus** bullet (three phrasings across runs); no structural loss of coverage.
- **Gold substring casing**: failing strict **`Instrument Suggestion`** vs actual **`instrument suggestion`** / **`Instrument suggestion`** — fix either gold (relax to case-insensitive or match actual heading) or standardize coverage template output to Title Case **Suggestion**.

## 6. Optimization plan

1. **Gold vs markdown**: Update **`required_smart_checklist_substrings`** in `CRT-638-gold.json` to match exported checklist casing (e.g. **`instrument suggestion`**) or add an explicit **Title Case** rule in [`.cursor/pipelines/coverage.md`](../../../pipelines/coverage.md) / benchmark coverage playbook so drafts always include **`Instrument Suggestion`** if that string is required.
2. **Reduce weak primary-focus drift**: Pin **`epic_verification_focus`** or a single canonical opening line in **`CRT-638-ref.json`** (or coverage instructions) so repeated runs converge to **Jaccard 1.0** on bullets.
3. Re-run **`COVERAGE-VALIDATE: CRT-638 suite=…`** after changes; confirm **`strong_bullets_all_runs`** includes any new mandatory lines and gold passes.
