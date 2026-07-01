# CRT-639 — fixture formula_first spine

## Primary focus

- Verify weighted-average cash settlement P/L for FOREX FX_SPOT when Functional Configuration selects WeightedAvg (CRT-1741): CRT-1740 average fill with zero-crossing reset, CRT-1738 realized versus open interplay, CRT-1743 mark-minus-average open P/L, and CRT-1742 gross percent denominators—observed on dxTrade5, WebBroker, and Adaptive.

## Functional configuration and prerequisites

- [CRT-1741] Arrange a FOREX FX_SPOT test instrument mapped to WeightedAvg via Functional Configuration.

## Weighted-average ladder

- [CRT-1738] Drive the weighted-average ladder on the configured FX_SPOT instrument; compare net size, average price, and realized P/L after each trade.
  > ! reason: authoritative cent-level ladder numerics pending XT-7911.

## Invariants under configuration change

- [CRT-1738] Realized P/L for each closing trade derives from average position price, not matched opening-trade prices.

## Rounding and display policy

- [CRT-1742] % P/L gross display rounds to two decimal places on surfaces that expose the field.

## Cross-surface parity

- [CRT-1738] dxTrade5 — Capture Average Price and Open P/L from positions view; compare to dxCore/API truth.
