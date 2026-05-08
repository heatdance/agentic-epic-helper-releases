<!-- Smart Checklist body mirrors CRT-639-coverage.json smart_checklist_markdown -->

# CRT-639 — Cash Settlement based on Average Price

## Primary focus

- This epic primarily verifies P/L and position metrics for FX Spot instruments when calculation uses weighted-average methodology instead of FIFO: functional configuration by instrument type (CRT-1741), average fill price (CRT-1740), open P/L (CRT-1743), % P/L Gross (CRT-1742), and the weighted-average cash-settlement ladder for average price, open PL, and realized PL (CRT-1738).

## Prerequisites and configuration

- [CRT-1741] For tests targeting FX Spot (FOREX / FX_SPOT subtype), associated data / functional configuration places the instrument under the Weighted Average branch per CRT-1741; when unset, FIFO default applies and WeightedAvg-specific expectations do not apply.
> CRT-1741 snippet: FIFO default instrument types vs Weighted Average for FOREX (FX_SPOT); “already existing instrument types” unchanged-configuration scenarios may be skipped per requirement text.

## Average fill price — WeightedAvg (position)

- [CRT-1740] With FX Spot on WeightedAvg, build an executable ladder (concrete BUY/SELL quantities and prices including partial closes and at least one net-size cross through zero); observed average fill / average position price matches weighted average by all opening trades since the last time net size crossed zero, not FIFO lot ordering.
> Ground implementation: `BRO/xt/dxcore/calculators/position-metrics` (`impl-003`).

## Open PL — WeightedAvg (position)

- [CRT-1743] For FX Spot under WeightedAvg, open PL matches `position_qty * (mark_price - average_fill_price) * multiplier` using the same mark and average fill definitions as the configuration branch (WeightedAvg snippet path).
> Do not assume UI column labels say “mark”; identify the platform truth source for mark and average fill (API/feed) from environment docs.

## Percent PL Gross — WeightedAvg (position)

- [CRT-1742] For FX Spot under WeightedAvg, % PL Gross matches `(Open PL / ABS(SUM(average price × qty × multiplier))) * 100` and rounds to two decimals per snippet.
> Use the same executed trade ladder and open PL inputs as the [CRT-1740]/[CRT-1743] checks so % PL Gross is computed on a consistent snapshot.

## Cash settlement ladder — CRT-1738

- [CRT-1738] For non-equity cash settlement on instrument types configured for weighted average, replay the requirement’s multi-step trade sequence from flat through long/short transitions; after each step, position average price and realized PL follow “closing P/L from average position price vs matched opens; only opening trades contribute to average price.”
> Rounding references in snippet point to other requirement keys not inlined in epic-ref — resolve nested keys or coordinate with XT-7911 before locking gold numbers (Jira comment).

## Cross-surface consistency — WebBroker and dxTrade5

- [CRT-1743] WebBroker: for a snapshot account/position under FX Spot WeightedAvg config, displayed open PL (where exposed) matches the backend/API value used as truth source for the formula check.
- [CRT-1743] dxTrade5 (desktop/web stack): same open PL as WebBroker for the same controlled snapshot when the metric is shown for FX Spot.

## Cross-surface consistency — Adaptive

- [CRT-1743] Adaptive: where FX Spot open PL or average fill is surfaced for the account, values match WebBroker/dxTrade5 for the same snapshot; if the metric is absent on Adaptive for FX Spot, record `! reason: metric not exposed on this surface` with product evidence rather than inferring pass.

## Dependencies and ambiguity

- ! reason: Jira comments reference XT-7911 and locking expected numeric outputs for the CRT-1738 ladder — treat definitive golden-vector sign-off as blocked until that dependency is cleared.
- ! reason: Jira asks which affected metrics appear in UI — enumerate observables per surface with BA/dev confirmation where labels differ from spec terms.
