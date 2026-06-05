# Jira Structure formulas (Corner QA)

Versioned **ALM Works Structure** Expr sources for the **[Enterprise] Corner Roadmap** board (id **603**). Live Jira Structure remains source of truth after paste deploy.

| Bundle | Recommended | Purpose |
|--------|-------------|---------|
| [`roadmap-columns/`](roadmap-columns/) | **v04-epic-aborted-skip-with-jql-counter** | QA RA, QA TC, QA CR, Validation — workflow buttons and status links on Epic rows |
| [`qa-end-date/`](qa-end-date/) | **v1** | QA End Date — Epic rollup over QA Task / Test Execution children |
| [`qa-est/`](qa-est/) | **v1** / **v2** | QA Est — v1 excludes CR from rollup; v2 includes CR; both scope Under Implementation epics |

**Start here for agents:** [`docs/jira-structure-contract.json`](../docs/jira-structure-contract.json) → this file → [`automation/docs/jira-structure.md`](../docs/jira-structure.md).

**Engine:** Structure column type **Formula** (Expr). Roadmap columns apply to **Epic** rows only; other issue types render blank.

**Deploy (summary):** Structure → board 603 → column settings → Formula → paste snippet files from the recommended version folder; map Structure variables (e.g. `EndDate`, `qa_pid` / `qa_alias` on QA RA — see metadata discrepancy note).
