# CRT-617 — Coverage checklist (Smart Checklist paste)

## Primary focus
- This epic primarily verifies a new FIX-router path for FOREX FX_SPOT with ET Trader: ET general FIX spec (CRT-1756), ET-prepared FIX message examples for DX (CRT-1757), additional fields sent to ET and saved on fill (CRT-1765), key outbound FIX tags per table (CRT-1759), saved ET execution tags including transaction id ET_REFERENCE_ID (CRT-1877, CRT-1881), and routing of all Forex FX_SPOT orders to ET (CRT-1760).

## [CRT-1760] FX_SPOT routing to ET
- [CRT-1760] For a configured FOREX FX_SPOT symbol, placing any supported client order type that should use ET shows the order routed to the ET FIX session (not a legacy domestic venue) — observable via execution destination / route diagnostics or approved gateway capture.
> Evidence: venue configuration + order audit or FIX capture per environment playbook; confirm instrument subtype FX_SPOT.

## [CRT-1756] FIX session and supported messages
- [CRT-1756] FIXT.1.1 session establishes with required DefaultApplVerID and successful logon, then proxy user BE (35=BE) succeeds per ET connection table — session stable for subsequent trade messages.
> Reference: ET FIX integration page admin tag table and logon examples in CRT-1756 snippet.
> Partial fills: confirm integration does not implement partial-fill handling on ET path (explicit non-goal per spec snippet).
- [CRT-1756] For FX spot trading, DX sends NewOrderMultileg (35=AB) for MARKET orders and NewOrderSingle (35=D) for LIMIT/STOP; cancels use F/G as specified; ET responds with ExecutionReport (35=8) for fills/rejects.
> Cross-check message list against CRT-1757 examples where tags are ambiguous.

## [CRT-1765] Market order extensions to ET
- [CRT-1765] MARKET FX_SPOT order to ET carries tolerance, current price for selected quantity, quoteId, and settlDate via the new New Order extension — fields visible in outbound capture and persisted on accepted orders per model.
> Linked tolerances reference nested CRT-1844 / price ladder CRT-1775 per requirement page; pull snippets if extending tests.
> Value date linkage per nested CRT-1929 when in scope for environment.

## [CRT-1759] Outbound tag mapping
- [CRT-1759] Outbound NewOrderSingle / NewOrderMultileg / cancel messages populate FIX tags per CRT-1759 table (PartyIDs, Account, Symbol/SecurityType, OrdType variants, Memo composition, market-only leg tags) matching a golden capture for a reference account group.
> Use CRT-1757 narrative where CRT-1759 says description is basis; document any tag-level ambiguity as structured ! in runbooks.

## [CRT-1877] [CRT-1881] Execution persistence
- [CRT-1877] [CRT-1881] On fill, dxCore execution stores ET transaction id mapped to ET_REFERENCE_ID (tag 37 semantics per CRT-1881) and related additional fields per CRT-1877 table — values match inbound ExecutionReport and downstream reporting expectations.
> CRT-1879 linkage for transactions report consistency appears in requirement page; verify only if reporting scope is in test charter.
> Confirm 6127 / value-date extension persistence when ET sends FillSettlDate per nested CRT-1929.

## Cross-surface order flow
- [CRT-1760] dxTrade5: user can place a routed FX_SPOT market/limit path that hits ET per configuration; order state and errors surface consistently with backend.
- [CRT-1760] WebBroker: same ET-routed FX_SPOT scenario as dxTrade5 baseline — order lifecycle and rejection reasons align (no silent divergence).
- [CRT-1760] Adaptive: if FX_SPOT order entry is in scope for the bank build, ET-routed orders show consistent states vs web stack — ! reason: adaptive_surface_scope_bank_config

## Observability and ops
- [CRT-1756] Support can collect FIX line logs for ET session (sender/target/compids per published test tables) and correlate with dxCore order keys for incidents.
> ET FIX integration page lists example session IDs — use only sanitized lab credentials in artifacts.

## Explicitly out of scope (consolidated)
- FX Forward-only FIX scenarios in CRT-1757 catalog: Epic Jira centers FX_SPOT with ET; forward flows are adjacent in linked doc, not named as primary epic verification.
- Partial-fill handling on ET integration: Requirement text states partial fills are not expected and must not be implemented/tested for this ET path.
- DxFeed pricing subscription mechanics as standalone epic: Snippet notes pricing done on DxFeed side; coverage here assumes feeds as prerequisite, not re-validating full dxFeed ET subscription matrix unless explicitly in CRT-617 scope.
