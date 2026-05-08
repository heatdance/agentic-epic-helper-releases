# CRT-639 Smart Checklist (coverage draft)

<!-- Shadow: benchmark_suite=20260508-ct01 attempt-02 -->

## Primary focus

- This epic primarily verifies that FOREX FX_SPOT (non-equity cash flow) position metrics use WeightedAvg accounting paths instead of FIFO while other instrument-type branches remain FIFO per configuration: CRT-1741 distinguishes FIFO vs WeightedAvg by instrument type (FX_SPOT subtype on WeightedAvg); CRT-1740 defines average position fill price separately for FIFO vs WeightedAvg (WeightedAvg ladder uses opening trades since the last zero-cross); CRT-1743 and CRT-1742 define Open P/L and % P/L Gross by configuration branch including two-decimal rounding on % P/L Gross for WeightedAvg; CRT-1738 binds cash-settlement average price, Open P/L, and Realized P/L to weighted-average rules with opening-trade-only contributions and the enumerated position-history ladder for expected relations.

## Prerequisites — configuration & truth source

- [CRT-1741] Functional configuration binds FOREX FX_SPOT (subtype) instruments to WeightedAvg while preserving FIFO defaults for STOCKS/ETF/OPTION/CFD/CFD_FOREX/FUTURE as listed (default FIFO when unset); after deploy, a fresh FX_SPOT test symbol shows platform metric calculators taking the WeightedAvg branch.
  > Map associated-data / account group configuration per environment; changing only out-of-epic instrument types is out of scope for primary ladders.
- [CRT-1741] After initial WeightedAvg history is established for an FX_SPOT position, changing account group or instrument accounting configuration for that symbol does not silently rewrite prior stored averages or historical cash effects for already-open history (regression against retroactive re-states).
  > If product explicitly allows replays on config flip, capture BA decision; epic text assumes skips when types already existed.

## [CRT-1740] Average position fill price — WeightedAvg path

- [CRT-1740] On FX_SPOT with WeightedAvg: execute sequence A) flat → BUY 10 @99 → BUY 10 @98 → SELL 20 @99.5 → verify position flat; record average fill after leg 2 from opening legs since last flat; reopen with SELL ladder per CRT-1738 excerpt and verify average incorporates only opening contributions since subsequent zero-crosses.
  > Contrast formulas stay in epic focus on WeightedAvg; FIFO branch peer scenarios are **out of epic** unless BA mandates regression parity (see backlog note).
  > Impl hint: BRO/xt `dxcore/calculators/` for server-side averages; reconcile with exported position metrics JSON if available.

## [CRT-1743] Open P/L — WeightedAvg path

- [CRT-1743] For the same staged FX_SPOT ladder, compute Open P/L from position_qty × (mark price − average fill price) × multiplier under WeightedAvg with mark price sourced per platform definition (explicit feed/mid observable used in CRT-1743 snippet); reconcile dxTrade5, WebBroker, and Adaptive surfaced Open P/L to the same numerical inputs within tolerance.
  > Do not infer UI label wording matches “mark price” verbatim in every column—bind to semantic mark from approved feed snapshot.

## [CRT-1742] % P/L Gross — WeightedAvg path

- [CRT-1742] With Open P/L and positions from the ladder, % P/L Gross matches (Open PL / ABS( SUM (average price × qty × multiplier))) × 100 for WeightedAvg and rounds to **two decimals**; compare UI/API outputs after explicit quantity and multiplier setup.
  > Nested rounding macro anchors in CRT-1738 excerpt are placeholders in snippets—coordinate exact basis with BA or follow-up requirement keys when XT-7911 settles numeric oracle.

## [CRT-1738] Cash settlement ladder — realized P/L & opening-trade-only averages

- [CRT-1738] Replay the CRT-1738 illustrative trade ladder (opening legs through multi-step buys/sells to long/short/zero states) under WeightedAvg and assert Realized PL per step matches CTR-1738 spreadsheet logic (opening trades only move average fill; closures realize against average, not against matched opening-price pairs).
  > Tie Ask/Bid reference inside scenario to observable quotes used by platform for that replay.
  > **Realized PL** assertions must survive partial closes without corrupting averages when configuration remains WeightedAvg.
- ! reason: CRT-1738 excerpt references unresolved rounding-rule requirement keys in exporter output; finalize expected cents once nested Yogi rows or XT-7911 guidance is approved (see Jira CRT-639 comments).

## Dimensions — position crosses zero / partial closures

- [CRT-1740][CRT-1738] After partial closes without returning to flat, weighted-average fill persists per opening-trade pool since prior zero-cross; after full zero-cross boundary, reopening resets opening-trade pool baseline for averages (repeat micro-ladder validating reset).

## Cross-surface parity — dxTrade5, WebBroker, Adaptive

- [CRT-1740][CRT-1743][CRT-1742][CRT-1738] **dxTrade5** — surfaced position columns (average fill, Open P/L, % P/L gross, realized / cash-equivalent columns if shown) numeric-align to API/export truth captured in ladder prerequisites for the staged FX_SPOT account.
  > Mention platform perspective / Explain-margin widgets only if they consume the affected metrics—otherwise omit.
- [CRT-1740][CRT-1743][CRT-1742][CRT-1738] **WebBroker** — same parity against truth source (`webbroker` stack in BRO/xt for UI wiring hints).
- [CRT-1740][CRT-1743][CRT-1742][CRT-1738] **Adaptive** — adaptive positions view repeats the reconciled averages and P/Ls for the seeded ladder; record `! reason: Adaptive column absent for metric X` if surface truly hides a field named in scope comments.

### Contrast / regression (non-epic path — minimal)

- [CRT-1741] Sanity-only: FIFO-configured CFD_FOREX/STOCK/etc. scenarios stay on FIFO calculators (baseline smoke, not exhaustive matrix) confirming FX_SPOT migration did not regress unrelated types.
