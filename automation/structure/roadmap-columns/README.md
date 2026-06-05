# Roadmap QA Structure columns

Four **ALM Works Structure** formula columns on **[Enterprise] Corner Roadmap** (structure id **603**): **QA RA**, **QA TC**, **QA CR**, **Validation**.

Agent-oriented field ids, JQL tails, and per-snippet behavior: [`metadata.json`](metadata.json). Version registry: [`versions-manifest.json`](versions-manifest.json). Normative paths: [`docs/jira-structure-contract.json`](../../docs/jira-structure-contract.json).

## Version folders (`versions/`)

| Folder | Behavior |
|--------|----------|
| **v01-baseline-before-validation-te-rule** | Baseline CR / RA / TC before Validation-TE–closed rules. |
| **v02-validation-te-closed-always-skips-three-columns** | Closed Validation TE forced **Skipped** on RA/TC/CR unconditionally (superseded). |
| **v03-validation-te-closed-only-with-no-matching-child** | Closed Validation TE → **Skipped** only when that column has **no** matching child. |
| **v04-epic-aborted-skip-with-jql-counter** | **Recommended:** Epic **Aborted** branch, JQL link on count, Validation-TE-closed gating. |

Paste the extensionless `CR`, `RA`, `TC`, `Validation` files from the chosen version folder into Structure column settings.

## Structure Expr gotchas (v04)

See **`metadata.json` → `epic_aborted_skip.structure_expr_notes`**: top-level `with abortMatches`, correct `CONCAT` closing parens, use `=` not `==` for compares.

## Deploy

1. Open [`metadata.json`](metadata.json) for field ids, JQL tails, and column mapping.
2. Paste from **`versions/v04-epic-aborted-skip-with-jql-counter/`** (or an older `v0*` to roll back).
3. Board URL: **`metadata.json` → `deployment`**.
