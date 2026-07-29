# CRT-639 — Weighted-average FX Spot cash settlement coverage

## Primary focus

- Verify weighted-average cash settlement P/L for FOREX FX_SPOT when Functional Configuration selects WeightedAvg (CRT-1741): CRT-1740 average fill with zero-crossing reset, CRT-1738 realized versus open interplay, CRT-1743 mark-minus-average open P/L, and CRT-1742 gross percent denominators—observed on dxTrade5, WebBroker, and Adaptive.

## Functional configuration and prerequisites

- [CRT-1741] Arrange a FOREX FX_SPOT test instrument mapped to WeightedAvg (not FIFO) via Functional Configuration; confirm non-target instrument families (STOCKS, CFD, etc.) remain on FIFO defaults unless explicitly in scope.
  > Yogi CRT-1741: Weighted Average covers FOREX (FX_SPOT subtype); default when unset is FIFO.
- [CRT-1741] Record the configuration row and associated data on the test account so the same instrument classification is reproducible across dxTrade5, WebBroker, and Adaptive.
  > impl-001 / impl-002: BRO/xt (`dxcore/`, `webbroker/`, `dxcore/calculators/`) grounds metric implementation.

## Weighted-average ladder — average fill, realized P/L, crossing zero (CRT-1738 & CRT-1740)

- [CRT-1738] Drive the Yogi ladder pattern (flat → layered buys → sells through zero → short rebuild) on the configured WeightedAvg FX_SPOT instrument; after each trade compare net size, average price, and realized P/L progression.
  > Jira comment (2026-05-07): epic waits for XT-7911 before locking CRT-1738 numeric ladder outputs.
  > ! reason: authoritative cent-level ladder numerics pending XT-7911; capture observed engine values for later diff.
- [CRT-1740] After net size re-crosses zero, confirm the next opening leg restarts the WeightedAvg window (weighted average of opening trades since last crossing 0 only).
- [CRT-1738] Partial closes that do not flip net sign must update average price per WeightedAvg opening-trade rules (no silent FIFO opening-match prices on closes).
- [CRT-1738] Stress multiple zero crossings in one session; each flat point must reset the opening-trade contribution window per CRT-1738.

## Open P/L and % P/L gross (WeightedAvg path)

- [CRT-1743] On an open WeightedAvg FX_SPOT position, assert Open P/L equals `position_qty * (mark_price - average_fill_price) * multiplier` using the environment mark feed; document mark source (mid/bid/ask/last).
- [CRT-1742] Assert % P/L gross follows `(Open PL / ABS(SUM(average_price * qty * multiplier))) * 100` for the WeightedAvg branch.

## Invariants under configuration change

- [CRT-1738] For WeightedAvg cash settlement, each closing trade realized P/L must derive from average position price, not matched opening-trade prices.
- [CRT-1738] Only opening trades contribute to position average price for WeightedAvg-configured instruments.

## Rounding and display policy

- [CRT-1742] % P/L gross display rounds to the nearest value with two decimal places on surfaces that expose the field.
  > ! reason: nested rounding requirement keys cited inside CRT-1738 prose are not resolved to separate Yogi keys in this workspace—fetch before hard-pass/fail on ladder rounding tolerances.

## Cross-surface parity (Corner Trader)

- [CRT-1738] dxTrade5 — Capture Average Price, Open P/L, % P/L gross, and Realized P/L from the primary positions view; compare to dxCore/API truth from ladder sections.
- [CRT-1743] WebBroker — Repeat snapshot read on positions/client widgets that expose the same metrics; assert parity with dxTrade5 within rounding tolerance.
- [CRT-1742] Adaptive — Repeat for each metric column on mobile position details; if absent, log `! reason: metric not exposed on Adaptive surface`.
  > Bind checks to semantic definitions from Yogi, not assumed UI label names (e.g. mark vs midpoint).

## Ambiguity / blocked

- [CRT-1738] ! reason: XT-7911 blocks locking final CRT-1738 worked-table numerics; structural ladder execution proceeds with documented observed values.
