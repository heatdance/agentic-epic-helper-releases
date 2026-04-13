# CRT-639 — Smart Checklist (Jira paste)

Epic: [CRT-639](https://jira.in.devexperts.com/browse/CRT-639). Structured artifact: `CRT-639-coverage.json` (`explicitly_out_of_scope`, matrix, grounding).

## Primary focus

- This epic primarily verifies that FX Spot instruments use weighted-average costing for average position fill price, open P/L, % P/L gross, and realized P/L in cash settlement (replacing FIFO for that class), controlled by the associated-data FIFO vs WeightedAvg mapping in CRT-1741. Verification follows CRT-1740, CRT-1743, CRT-1742, and CRT-1738 for formulas, rounding behavior where specified, and the worked position-history ladder.

## Configuration and instrument scope

- [CRT-1741] Associated data exposes FIFO vs WeightedAvg mapping; FOREX (FX_SPOT subtype) is WeightedAvg in the reference configuration table; when not configured, FIFO is the default.
> Per CRT-1741, scenarios that change configuration for already existing instrument types can be skipped — do not treat production re-mapping as in-scope unless AC explicitly expands.

## WeightedAvg metrics — definitions and calculation ladders

- [CRT-1740] On a WeightedAvg-configured FX Spot position, average fill updates from opening trades since the last net-size zero crossing; after BUY +10 @ 99.00 then BUY +10 @ 98.00, average fill reflects the weighted combination before closes.
> Partial closes and increases: validate average fill only moves on opening-side activity consistent with “since last crossing 0” wording in CRT-1740 snippet.
> FIFO branch formulas for the same capability are out of epic primary scope — see CRT-639-coverage.json explicitly_out_of_scope.
- [CRT-1743] Open P/L for the WeightedAvg path matches position_qty × (mark price − average fill price) × multiplier for the same instrument and quote session; mark price source matches environment documentation (do not assume UI column label says “mark”).
- [CRT-1742] % P/L gross for the WeightedAvg path equals (Open P/L ÷ ABS(SUM(average price × qty × multiplier))) × 100 using the same signed average and position quantities as CRT-1743; result rounded to two decimals per requirement snippet.
- [CRT-1738] Execute the position-history ladder from flat: BUY +10 @ 99.00 → BUY +10 @ 98.00 → close/partial paths per requirement example (e.g. SELL −20 @ 99.50 to flat, or SELL −10 @ 99.50 to short 10); at each step, position average price and realized P/L match weighted-average cash-settlement rules (only opening trades contribute to average; closes realize against average).
> Include a cross-through-zero path (e.g. long to flat to short) and re-build of average on new opening legs after zero if spec implies.
- ! reason: CRT-1738 snippet references separate rounding rules for average price and realized P/L without resolvable nested requirement keys in epic-ref requirements[] — confirm rounding acceptance with BA or enrich Yogi snippet before sign-off.
> Known issue: [XT-7911](https://jira.in.devexperts.com/browse/XT-7911) Apply rounding rules to Avg Price and Realized PL (status Waiting for clarification); ticket links CRT-1921, CRT-1922, DXINV-326 — align numeric acceptance with those keys once clarified.

## Cross-surface consistency (Corner + Adaptive)

- [CRT-1740][CRT-1743][CRT-1742][CRT-1738] dxTrade5: average fill, open P/L, % P/L gross, and realized P/L (where exposed) match the API/account-statement truth source for the same WeightedAvg FX Spot test position.
- [CRT-1740][CRT-1743][CRT-1742][CRT-1738] WebBroker: same numeric parity as dxTrade5 for the surfaced metrics on the test account.
- [CRT-1740][CRT-1743][CRT-1742][CRT-1738] Adaptive: same numeric parity as dxTrade5/WebBroker for position metrics that the mobile shell exposes; if a metric is absent on Adaptive, capture N/A with product evidence rather than skipping silently.
