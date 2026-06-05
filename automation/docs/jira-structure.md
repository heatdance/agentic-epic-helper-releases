# Jira Structure formulas

Deploy and version **ALM Works Structure** Expr columns for Corner QA on the **[Enterprise] Corner Roadmap** board. This is **not** part of epic pipelines (`EPIC-PREP`, `TEST-PREP`, etc.) — paste-only maintenance in Jira Structure UI.

## Discovery

| Artifact | Role |
|----------|------|
| [`docs/jira-structure-contract.json`](../../docs/jira-structure-contract.json) | Normative paths, recommended versions, column mapping |
| [`automation/structure/README.md`](../structure/README.md) | Bundle overview |
| [`automation/structure/roadmap-columns/metadata.json`](../structure/roadmap-columns/metadata.json) | Field ids, JQL, snippet semantics, known inconsistencies |
| [`docs/harness-map.json`](../../docs/harness-map.json) | T1 package `jira_structure` keywords |

## Roadmap QA columns (four formulas)

**Recommended:** `automation/structure/roadmap-columns/versions/v04-epic-aborted-skip-with-jql-counter/`

| Repo file | Structure column |
|-----------|------------------|
| `RA` | QA RA |
| `TC` | QA TC |
| `CR` | QA CR |
| `Validation` | Validation |

### Deploy steps

1. Open [Structure board 603](https://jira.in.devexperts.com/secure/StructureBoard.jspa?s=603#).
2. For each column: **Column settings → Formula** (Saved column: Custom).
3. Copy-paste the matching extensionless file from the version folder.
4. Confirm **Sum over sub-items** is off (observed on QA RA; verify others).
5. On **QA RA**, reconcile Structure variables: repo uses `qa_pid` and `qa_alias`; editor may show `qa_pld` / `qa_cties` — match live Jira before saving.

### Rollback

Use [`versions-manifest.json`](../structure/roadmap-columns/versions-manifest.json): paste from `v03-…` or earlier if v04 behavior is wrong. Do not edit historical version folders in place — add `v05-…` for the next change.

### Expr pitfalls (v04)

Documented under `metadata.json` → `epic_aborted_skip.structure_expr_notes` (top-level `with abortMatches`, `CONCAT` parentheses, `=` not `==`).

## QA End Date (one formula)

**Recommended:** `automation/structure/qa-end-date/versions/v1/formula.expr`

1. Create or edit column **QA End Date**.
2. Paste `formula.expr`.
3. Map variable **EndDate** → Jira **End Date**.
4. Column format: General or Text; sum over sub-items: **OFF**.
5. Remove old Epic MAX and Ticket ED columns.

See [`automation/structure/qa-end-date/README.md`](../structure/qa-end-date/README.md) for display rules.

## QA Est (two formula versions, two views)

| Version | File | Rollup |
|---------|------|--------|
| **v1** (default) | `automation/structure/qa-est/versions/v1/formula.expr` | RA + TC + Validation — **excludes QA CR** hours |
| **v2** | `automation/structure/qa-est/versions/v2/formula.expr` | All lanes including **QA CR** |

1. Duplicate the Structure view if you need both behaviors.
2. Paste the matching `formula.expr` into **QA Est** on each view.
3. Column format: **Duration** (or General if your board uses duration display).

**Epic scope (both):** **Validation**, **Pending Fix**, **Under Implementation** — on status (`epic_in_scope`, parent scope, subtree count), label branch, and PMOPROC subtree rollup. In-Epic slot/incomplete logic unchanged.

**Leaf estimate:** if `timespent` > 0 use `remainingEstimate`; else if draft `customfield_11250` > 0 use `DURATION(hours)`; else `originalEstimate`. Literals: `done`, `none`, `(?)`, `(?) not defined`, `(!) incomplete`.

Details: [`automation/structure/qa-est/README.md`](../structure/qa-est/README.md) and [`metadata.json`](../structure/qa-est/metadata.json).

## Confluence references (embedded in create URLs)

From `metadata.json` → `embedded_docs`:

- [Test Repository](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497097317/Test+Repository) (TC description)
- [Validation workflow](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497102460/Workflow)

## Bumping versions

1. Copy the current recommended version folder to a new `v05-…` (or new `qa-end-date/v2`) name.
2. Edit formulas; update `versions-manifest.json` and `recommended` id.
3. Bump `contract_version` in `docs/jira-structure-contract.json` when semantics or recommended version changes.
4. Update `metadata.json` paths and `last_reviewed` if field ids or behavior changed.

No `*_verify.py` in v1 — validate by paste test on a sample Epic in Structure preview.
