# `temp/` — Jira Structure QA column formulas

Shared documentation for **[Enterprise] Corner Roadmap** formula columns (**QA RA**, **QA TC**, **QA CR**, **Validation**) lives in **[`dependencies.json`](dependencies.json)** only (one file for all versions).

Formula **source text** is versioned under **`structure-columns/`** — copy the right folder’s `CR`, `RA`, `TC`, `Validation` files into Jira Structure; do not maintain duplicate snippet files in `temp/` root.

## Version folders (`structure-columns/`)

| Folder | Behavior |
|--------|-----------|
| **v01-baseline-before-validation-te-rule** | Baseline CR / RA / TC before Validation-TE–closed rules. |
| **v02-validation-te-closed-always-skips-three-columns** | Closed Validation TE forced **Skipped** on RA/TC/CR unconditionally (superseded). |
| **v03-validation-te-closed-only-with-no-matching-child** | Closed Validation TE → **Skipped** only when that column has **no** matching child (create branch). |
| **v04-epic-aborted-skip-with-jql-counter** | Recommended: Epic **Aborted** branch, JQL link on count, Validation-TE-closed gating, no `<PROJECT>` summary prefix. |

## Structure Expr gotchas (v04)

See **`dependencies.json` → `epic_aborted_skip.structure_expr_notes`**: top-level `with abortMatches`, correct `CONCAT` closing parens, use `=` not `==` for compares.

## Deploy

1. Open **[`dependencies.json`](dependencies.json)** for field ids, JQL tails, and column mapping.  
2. Paste formulas from **`structure-columns/v04-epic-aborted-skip-with-jql-counter/`** (or an older `v0*` if rolling back).  
3. Board URL and structure id are under **`dependencies.json` → `deployment`**.
