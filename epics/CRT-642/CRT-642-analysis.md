# CRT-642 — Requirement analysis

## Summary

CRT-642 validates that FX_SPOT trading actions during instrument non-trading windows (including the Mon–Thu 17:00–17:15 NY ET reload segment in the schedule) are confirmable but rejected with messaging aligned to CRT-1749 (code 358) and CRT-1750, while web greys bid/ask in Watchlist and webbroker Client Area and adaptive greys quotes on open-position details—explicitly not requiring adaptive Watchlist or OE quote grey-out. Practical focus is reproducible schedule evidence, cross-surface rejection semantics, and separating deferred chart scope (DxFeed) from order/quote acceptance.

## Gaps

- `gap-001` Nested requirement CRT-1481 is referenced from CRT-1750 snippet text but coverage `nested_requirement_refs` leaves `page_id` and `short_url` null—upstream schedule definition is not tool-resolved in-repo.
- `gap-002` Chart default trading-hours-only visibility remains `calculation_contract` `deferred_ambiguous` (DxFeed dependency); pass/fail criteria for that slice are environment-gated (`chk-015`).
- `gap-003` Stash code search returns HTTP 404; implementation evidence is browse/layout anchors only, not symbol-level validation code pointers (`anti_pattern_findings` + epic-ref bitbucket validation log).

## Questions

- `(G)` Should CRT-1481 be resolved to a Confluence `page_id` (or Yogi snippet) so schedule preconditions (`chk-002`, `chk-016`) cite authoritative non-trading definitions beyond CRT-1750 prose? — evidence: `nested_requirement_refs` CRT-1481 `page_id` null.
- `(G)` Once DxFeed provides FX_SPOT chart data, what observable UI/time-range rule counts as satisfying Jira item 2 versus deferring again? — evidence: `chk-015` `deferred_ambiguous`.
- `(H)` Does open XT-8043 (watchlist row exception) reproduce under FX_SPOT non-trading grey-quote flows on web, or is it a separate watchlist defect?
- `(H)` For XT-7451 (cancel completes during non-trading), which client shell and order state reproduce the bug—dxTrade5 web, webbroker paths, adaptive, or multiple?
- `(G)` Should closed upstream items (e.g. XT-7183 resolved localization for CRT-1749 token) be treated as regression anchors in TEST-PREP bundles even though ANALYSE does not mutate coverage for closed issues by default? — evidence: XT-7183 Resolved; default open-only coverage mutation.

## Known issues

### In scope (relevant)

- **XT-7451** — FX_SPOT - cancel order during non-trading hours is completed — `(OPEN)` — https://jira.in.devexperts.com/browse/XT-7451
- **XT-7184** — [DXTF] [RIA] Grey out FX_SPOT Quotes in UI in Non-Trading session — `(CLOSED)` — https://jira.in.devexperts.com/browse/XT-7184
- **XT-7183** — [DXTF] [RIA] Add localization for FX_SPOT_TRADING_DURING_NON_TRADING_HOURS_IS_PROHIBITED — `(CLOSED)` — https://jira.in.devexperts.com/browse/XT-7183
- **CAN-11914** — [FX_SPOT] Add a new OE validation error message — `(CLOSED)` — https://jira.in.devexperts.com/browse/CAN-11914

### Out of scope / questionable

- **CRTQA-10044** — [Corner][Requirement Analysis] CRT-642: Non-trading hours — `(CLOSED)` — out_of_epic (QA task) — https://jira.in.devexperts.com/browse/CRTQA-10044
- **XT-7182** — Introduce FxSpot Trading Hours Validation Rule — `(CLOSED)` — out_of_epic (implemented upstream feature CR) — https://jira.in.devexperts.com/browse/XT-7182
- **CAN-11918** — [FX_SPOT] Grey out quotes on Positions Details for non-trading hours — `(ABORTED_OR_OTHER)` — out_of_epic (aborted CAN item) — https://jira.in.devexperts.com/browse/CAN-11918
- **XT-8043** — Exception on watchlist row creation — `(OPEN)` — questionable (summary lacks FX_SPOT / non-trading linkage) — https://jira.in.devexperts.com/browse/XT-8043

### Unmapped (checklist candidates)

- **XT-7451** — ambiguous_mapping between web cancel scenario `chk-005` and adaptive cancel `chk-011`; no single best `checks[].check_id` per playbook—manual pick or split retest notes before appending a Known issue line.
