# CRT-639 — Weighted-average FX Spot cash settlement coverage

## Primary focus

- Corners verifies weighted-average cash settlement P/L mapping for FOREX FX_SPOT instruments when Functional Configuration selects WeightedAvg (CRT-1741), spanning CRT-1740 average fill ladders that reset net size at zero, CRT-1738 realized versus open interplay, CRT-1743 mark-minus-average open P/L, and CRT-1742 gross percent denominators—all observed consistently on dxTrade5, WebBroker, and Adaptive shells.


## Invariants under configuration change

- [CRT-1740] With an open WeightedAvg FX_SPOT position and recorded average fill price, move the account between CornerTraderFxConfiguration groups (e.g. OPPORTUNITY to ENERGY) without closing the position; average fill price and open P/L inputs for the open lots remain unchanged.
  > Preconditions: open position built per weighted-average ladder; group keys from account_group_hierarchy.

## Functional configuration and prerequisites

- [CRT-1741] Using Functional Configuration Live Platform documentation, arrange a FOREX `FX_SPOT` test instrument—or equivalent controlled mapping—assigned to WeightedAvg (not FIFO) for valuation; confirm STOCKS/CFD paths remain FIFO unless explicitly migrating them (explicitly outside this epic’s primary focus).
  > Yogi CRT-1741: Weighted Average bucket covers FOREX (FX_SPOT subtype); default when unset is FIFO.
- [CRT-1741] Record the configuration row and associated data used on the test account so COVERAGE can reproduce the same instrument classification across dxTrade5, WebBroker, and Adaptive sessions.
  > impl-001 / impl-002: BRO/xt monorepo (`dxcore/`, `webbroker/`) is the default implementation surface for metric plumbing.

## Weighted-average ladder — average fill, realized P/L, crossing zero (CRT-1738 & CRT-1740)

- [CRT-1738] Drive the published ladder pattern from Yogi (flat → layered buys → sells through zero → short rebuild) on the configured WeightedAvg FX_SPOT instrument; after each trade, compare position net size, average price, and realized P/L effect against the authoritative ladder output once XT-7911 supplies final numerics.
  > Jira comment (2026-05-07): epic “Waits for XT-7911” before locking expected outputs for the CRT-1738 ladder.
  > ! reason: absolute numeric expectations still pending upstream XT-7911 alignment per Jira; execute structural ladder and document observed engine values for later diff.
- [CRT-1740] After re-crossing net zero, confirm the next opening leg restarts the WeightedAvg opening-trade window (only opening trades contribute; WeightedAvg path uses all opening trades since last crossing 0 per snippet).
- [CRT-1738] Verify partial closes that do not flip net sign update average price per WeightedAvg opening-trade rules (no silent regression to FIFO opening-match prices for closing events).


## Rounding and display policy

- [CRT-1742] For a WeightedAvg FX_SPOT position, verify % P/L gross rounds to two decimals per requirement denominator rules after a controlled mark move.
  > Use executable ladder from CRT-1742 snippet; compare UI/API to expected rounded value.

## Open P/L and % P/L gross (WeightedAvg path)

- [CRT-1743] On an open WeightedAvg FX_SPOT position, assert Open P/L equals `position_qty * (mark_price - average_fill_price) * multiplier` using the same mark feed as production configuration; document which mark source (mid, bid, ask, last) the environment applies.
- [CRT-1742] Assert % P/L gross follows `(Open PL / ABS(SUM(average_price * qty * multiplier))) * 100` for the WeightedAvg branch and rounds to two decimals per Yogi CRT-1742.
  > Contrast regression for FIFO denominators is explicitly out of epic scope unless QA policy demands a single smoke (see `explicitly_out_of_scope` in coverage JSON).

## Cross-surface parity (Corner Trader)

- [CRT-1738] dxTrade5 — For the same account/instrument snapshot, capture Average Price, Open P/L, % P/L gross, and Realized P/L columns from the primary positions view and compare to the dxCore/API truth used in prior sections.
- [CRT-1743] WebBroker — Repeat the same snapshot read (positions / client area widgets that expose the metrics) and assert numerics match dxTrade5 within rounding tolerance.
- [CRT-1742] Adaptive — Repeat for every metric column exposed on mobile position details; if a column is absent, log `! reason: metric not exposed on Adaptive surface` instead of bundling with web results.
  > Anti-pattern guard: do not assume UI labels say “mark” vs “mid”; bind checks to column semantics confirmed with PM/BA.

## Dimensions and edge cases (evidence-gated)

- [CRT-1738] Stress position history that crosses zero multiple times in one session to ensure average reset windows match Yogi expectations.

## Ambiguity / blocked

- [CRT-1738] ! reason: nested rounding requirement keys referenced inside CRT-1738 storage export are not yet resolved to explicit CRT keys in this workspace—open separate Yogi fetch before hard-pass/fail on rounding tolerances.
