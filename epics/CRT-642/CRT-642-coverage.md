# CRT-642 — Coverage checklist (Smart Checklist paste)

## Primary focus
- This epic verifies FX_SPOT behavior during instrument non-trading hours (including the Mon-Thu 17:00-17:15 NY ET reload window captured in the instrument schedule): on web and on adaptive, order flows for new/modify/cancel/close still run through confirmation but are rejected with the appropriate reason; rejections and pre-trade validation in Order Entry align with CRT-1750 and CRT-1749 (code 358); web greys bid/ask quotes in Watchlist and in webbroker Client Area as stated; adaptive greys quotes on position details when a position is open, while adaptive Watchlist presentation and Order Entry quote greying are explicitly out of scope per the epic because rejection is considered sufficient there.

## Preconditions and schedule evidence
- [CRT-1750] For the target FX_SPOT symbol, the configured instrument schedule includes the non-trading segment used in the scenario (including Mon-Thu 17:00-17:15 NY when exercising the ET reload freeze window from the epic context) so that "non-trading hours" is reproducible, not guessed from wall clock alone.
> Evidence: instrument schedule / console or approved environment notes; align with Jira Context freeze description.

## Web — FX_SPOT order flows (dxTrade5 / webbroker Order Entry)
- [CRT-1749] [CRT-1750] Web: user can confirm and send a **new** FX_SPOT order during non-trading hours when other preconditions pass, but the platform **rejects** the order and surfaces a reason consistent with **FX_SPOT trading during non-trading hours is prohibited** (CRT-1749 / code **358**), including **pre-trade validation in Order Entry** before or at send per epic Requirements 1.1.
> Jira: Acceptance Criteria for web — new order.
> Bitbucket anchors (layout only): `impl-001` repo root; `impl-002` `webbroker/` (webbroker-ui, webbroker-backend); `impl-003` `dxcore/` (server-side validation stack).
- [CRT-1749] [CRT-1750] Web: user can confirm a **modify** of an FX_SPOT order during non-trading hours, but the modify is **rejected** with the same prohibition family / messaging expectation as new orders (CRT-1749 / 358 path).
- [CRT-1749] [CRT-1750] Web: user can confirm **cancellation** of an FX_SPOT order during non-trading hours, but the cancel action is **rejected** with the same prohibition family / messaging expectation (replace/cancel treated per Requirements 1.1).
- [CRT-1749] [CRT-1750] Web: user can confirm **close FX_SPOT position** during non-trading hours, but the closing order is **rejected** with the same prohibition family / messaging expectation.

## Web — quote presentation (Watchlist and Client Area)
- [CRT-1750] Web **Watchlist**: while viewing FX_SPOT quotes during non-trading hours, bid/ask remain visible but are **greyed out** (disabled presentation) per Jira Acceptance Criteria for web.
- [CRT-1750] Web **webbroker Client Area**: while viewing FX_SPOT quotes during non-trading hours, bid/ask are shown and **greyed out** per Jira Requirements 1.2.

## Adaptive — FX_SPOT order flows
- [CRT-1749] [CRT-1750] Adaptive: **new** FX_SPOT order during non-trading hours — confirm flow allowed, order **rejected** with appropriate reason aligned to CRT-1749 / 358 including Order Entry **pre-validations** per Requirements 1.1.
- [CRT-1749] [CRT-1750] Adaptive: **modify** FX_SPOT order during non-trading hours — confirm then **reject** with same expectation family.
- [CRT-1749] [CRT-1750] Adaptive: **cancel** FX_SPOT order during non-trading hours — confirm cancellation then **reject** with same expectation family.
- [CRT-1749] [CRT-1750] Adaptive: **close FX_SPOT position** during non-trading hours — confirm then **reject** with same expectation family.

## Adaptive — quote presentation (position details)
- [CRT-1750] Adaptive: with at least one **open** FX_SPOT position, **position details** quotes during FX_SPOT non-trading hours are **greyed out** per Jira Acceptance Criteria for adaptive.

## Cross-surface — error semantics
- [CRT-1749] Rejection surfaces expose the **CRT-1749** client message / code **358** semantics for FX_SPOT non-trading prohibition on **web** and **adaptive** (wording may follow localization rules; verify mapping to `FX_SPOT_TRADING_DURING_NON_TRADING_HOURS_IS_PROHIBITED` per requirement snippet, not a generic unexpected error).
> Snippet: CRT-1749 EXECUTE row documents code 358 and English text.

## Chart QA follow-up (DxFeed dependency)
- ! reason: deferred_ambiguous — Jira item 2 is a **QA note**: default FX_SPOT chart shows **trading hours only** on web and adaptive once **Chart Data for FX_SPOT is provided by DxFeed**; until feeds support that slice, record environment readiness rather than failing the epic on chart alone.

## Dimensions (evidence-gated)
- [CRT-1750] **ET reload window**: exercise at least one scenario in the **Mon-Thu 17:00-17:15 NY** non-trading segment described in Jira Context (instrument schedule includes that freeze) and observe the same rejection + grey-quote rules as other non-trading segments for FX_SPOT.
> Do not add unrelated multi-account / multi-group dimensions unless a future story ties them to this epic.

## Explicitly out of scope (consolidated)
- Adaptive **Watchlist** bid/ask grey-out and **Order Entry** live quote grey-out: epic explicitly states **no change** there for adaptive; **order rejection** is the sufficient control — do not file defects for missing adaptive watchlist grey when AC says none.
- Full **non-FX_SPOT** instrument-type matrix for non-trading (equities, futures, etc.): epic scope is **FX_SPOT** behavior unless Jira is amended.
- Deep **CRT-1481** schedule-definition content beyond what is needed to pick a reproducible non-trading window: nested reference from CRT-1750 snippet; treat as upstream context, not a standalone test matrix for this epic.
- **XT BRO** configuration narratives (global vs ipfBased vs custom trading hours) as exhaustive Corner QA: use token-light summaries under `xt_confluence_hits` for orientation only unless Corner AC explicitly adopts a BRO-only knob.
