# CRT-639 — Coverage checklist (Smart Checklist paste)

## Primary focus

- This epic verifies that FX Spot P/L shifts from FIFO to average-price calculators: CRT-1741 maps instrument families to FIFO vs WeightedAvg; CRT-1740 Average Fill Price, CRT-1743 Open P/L, and CRT-1742 % PL Gross follow that mapping on positions; CRT-1738 binds the weighted-average ladder for Average Price, Open PL, and Realized PL during cash settlement, with parity on dxTrade5, Web Broker, and Adaptive.

## Functional configuration & instrument posture

- [CRT-1741] Build or reuse FX_SPOT **WeightedAvg** test instruments tied to CRT-1741 mapping; validate associated data places **FOREX (FX_SPOT subtype)** on the weighted-average lane instead of stale FIFO defaults before trading.
> Yogi CRT-1741: FIFO STOCKS/ETF/OPTION/CFD/… vs **Weighted Average: FOREX (FX_SPOT subtype)**.
> Record instrument id, **account group** id, and config screen evidence for rerun stability.

## Average fill price & weighted-average ladder

### CRT-1738 ladder

- [CRT-1738][CRT-1740] Execute a CRT-1738-aligned trade ladder on FX_SPOT WeightedAvg after last zero-cross: opening trades establishing average fill, partial closes altering realized P/L, and post-close average price — snapshot engine truth (position qty, avg price, realized, open exposure) **before** UI assertions.
> CRT-639 comment: waits for XT-7911 before locking immutable golden numeric table — cite interim tolerances.
> Map each ladder row to CRT-1738 illustrative BUY/SELL sequence inside the requirement snippet.

- [CRT-1740] For WeightedAvg instruments, weighted average fills come from opening trades since last net-size zero cross — verify observed average fill differs from FIFO-only netting when historic mixed-opening lots remain open.

## Open PL, % PL gross, parity

- [CRT-1743][CRT-1738][CRT-1742][CRT-1740][CRT-1741] With grounded mark feed, WeightedAvg **Open P/L** equals `position_qty × (mark − average_fill_price) × multiplier`; **% PL gross** denominator uses summed `average_price × qty × multiplier` weights (two-decimal rounding) — diff ≤ agreed tolerance versus risk engine/export.
> CRT-639 comment thread asks which metrics appear per UI — annotate `! reason` when metric absent on a shell.

### dxTrade5

- [CRT-1743][CRT-1742][CRT-1738][CRT-1741] **dxTrade5** exposes Average Fill Price, Open P/L, % PL gross for FX_SPOT WeightedAvg instrument matching ladder numbers within tolerance — structured `!` if column absent.

### Web Broker

- [CRT-1743][CRT-1742][CRT-1738][CRT-1741] **Web Broker** shows the same three metrics given identical quotes/session as the dxTrade5 capture for this ladder — attach screenshot + timestamp.

### Adaptive

- [CRT-1743][CRT-1742][CRT-1738][CRT-1741] **Adaptive** shows the surfaced subset per `qa_default_both`; if Adaptive omits metric, structured `! reason: Adaptive UI omits <metric>` with tracking key.

## Cash settlement stresses

- [CRT-1738] During **cash settlement** events for FX_SPOT weighted instruments, reconcile Average Fill, Open PL, Realized PL against CRT-1738 weighted-average wording (non-equity cash flow excerpt) plus rounding macros once keys are retrieved.
> Tie evidence to known cash-settlement window or BA-provided fixture once available.

## Dimensions

! reason: CRT-639 Jira text is silent on multi-account/multi-group quote permutations beyond configuration — skip extra dimension bullets unless BA extends scope.
