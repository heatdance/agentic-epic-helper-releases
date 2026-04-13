# CRT-639 — Requirement analysis

Structured artifact: [CRT-639-analysis.json](CRT-639-analysis.json). Epic: [CRT-639](https://jira.in.devexperts.com/browse/CRT-639).

## Summary

CRT-639 validates FX Spot moving from FIFO to weighted-average costing for average fill, open P/L, % P/L gross, and realized P/L in cash settlement, driven by associated-data FIFO vs WeightedAvg mapping (CRT-1741) and the formula ladder in CRT-1740/1743/1742/1738. QA proves configuration read, metric ladders (including cross-through-zero paths), and numeric parity across dxTrade5, WebBroker, Adaptive, and API/statement truth sources. Open rounding clarification on XT-7911 remains the main acceptance risk before hard numeric sign-off.

## Gaps

- `gap-001` — No code-level implementation hits: Bitbucket/Stash code search returned HTTP 404; epic-ref `implementation.hits` empty (`CRT-639-ref.json`, `CRT-639-coverage.json` anti_pattern).
- `gap-002` — Rounding rules for average price vs realized P/L reference nested requirements not present in epic-ref `requirements[]`; acceptance deferred on `chk-007` (`CRT-639-coverage.json`).
- `gap-003` — `client_shell_impact` marks both shells affected under `qa_default_both` with `evidence: none_found` — confirm product signal if Jira later excludes a shell (`CRT-639-ref.json`).
- `gap-004` — Epic-linked XT-7651 (prospective accounts settlement) is adjacent to cash-settlement scope; test slice not explicit in coverage matrix (Jira epic children).

## Questions

- `(G)` Which feed or service is the authoritative mark price for Open P/L on each target environment (dxTrade5/WebBroker/API), given the checklist warns not to infer from UI column labels? (`chk-004`)
- `(G)` Before locking expected numeric outputs for the CRT-1738 ladder, will XT-7911 and linked CRT-1921, CRT-1922, DXINV-326 supply final rounding contracts? (`chk-007`, nested refs)
- `(H)` Does XT-7651 require an explicit prospective-account or account-type slice in Corner validation, or is standard FX Spot WeightedAvg coverage sufficient?
- `(G)` For Adaptive, which of average fill, open P/L, % P/L gross, and realized P/L are actually exposed for FX Spot WeightedAvg positions in the bank build under test? (`chk-010`)
- `(H)` Should resolved upstream CRs XT-7312, XT-7325–XT-7328, XT-7552 be cited as regression anchors in execution notes even though they are closed and not duplicated as new checklist `>` lines?

## Known issues

### In scope (relevant)

- XT-7911 — Apply rounding rules to Avg Price and Realized PL calculations (OPEN — Waiting for clarification) — [browse](https://jira.in.devexperts.com/browse/XT-7911)
- XT-7649 — Remain using position when it needs to calculate average price (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7649)
- XT-7328 — Update Settlement for WEIGHTED_AVERAGE instruments (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7328)
- XT-7326 — Update OpenPL calculation for weighted-average-instruments (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7326)
- XT-7325 — Update calculation of AveragePrice for Position (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7325)
- XT-7327 — Update Percent PL Gross calculation for WEIGHTED_AVERAGE instruments (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7327)
- XT-7552 — Override PLRelatedPositionData to support weighted average calculations (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7552)
- XT-7312 — Introduce global associated data PlCalculationMode (CLOSED — Resolved/Done) — [browse](https://jira.in.devexperts.com/browse/XT-7312)

### Out of scope / questionable

- CRTQA-10132 — [Corner][Test Case Development] CRT-639 (OPEN — In Progress) — QA workflow — [browse](https://jira.in.devexperts.com/browse/CRTQA-10132)
- CRTQA-10042 — [Corner][Requirement Analysis] CRT-639 (CLOSED) — QA task — [browse](https://jira.in.devexperts.com/browse/CRTQA-10042)
- CRTQA-10133 — [Corner][Test Case Review] CRT-639 (OPEN) — QA workflow — [browse](https://jira.in.devexperts.com/browse/CRTQA-10133)
- CRTQA-10134 — [Corner][Epic Validation] CRT-639 (OPEN) — QA workflow — [browse](https://jira.in.devexperts.com/browse/CRTQA-10134)
- XT-7651 — Support Settlement Calculations For Prospective accounts (CLOSED — questionable mapping to epic matrix) — [browse](https://jira.in.devexperts.com/browse/XT-7651)

### Unmapped (checklist candidates)

- None — open in-scope issue XT-7911 maps to `chk-007`; dedupe skipped a second `>` line because `XT-7911` is already cited under that check.
