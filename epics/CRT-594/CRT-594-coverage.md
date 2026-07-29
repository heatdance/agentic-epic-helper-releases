# CRT-594 — FX_SPOT Pricing (groups and mapping to dxFeed)

## Primary focus

- Verify FX_SPOT group-specific bid/ask on named client surfaces (Watchlist, Position Book, Instrument page, Derivatives, Client Area), tier/oracle rules per widget, midpoint invariant across groups, and backup/EOD midpoint capture.

## Data setup — account groups and quote publication

- [CRT-1761] CornerTraderFxConfiguration groups exist with FxSpotSuffix and domain profiles for RAG-CH and RAG-BS brokers (ENRG vs OPPT contrast).
> Provision two account groups on CTQA before UI quote observation.
> Prerequisite (console): Confirm CornerTraderFxConfiguration account groups for RAG-CH-broker and RAG-BS-broker; profiles include FxSpotSuffix, minTolerance, maxTradableQty; FxSpotSuffix per CRT-1766 (CH) / CRT-1767 (BS).
> Contrast: use two accounts in ENRG vs OPPT groups before any UI quote check.

- [CRT-1761] ET publish tier streams and instrument allow-list configured before quote checks on client surfaces.
> Prerequisite (console): Confirm CornerTraderFxConfiguration account groups for RAG-CH-broker and RAG-BS-broker; profiles include FxSpotSuffix, minTolerance, maxTradableQty; FxSpotSuffix per CRT-1766 (CH) / CRT-1767 (BS).
> Contrast: use two accounts in ENRG vs OPPT groups before any UI quote check.

## dxTrade5 — Watchlist

- [CRT-1714] Watchlist bid/ask reflects account group suffix and TextConfiguration tier closest to order quantity.
> Oracle: tier-by-qty oracle for default order qty.
> Harness: dxtrade5.workspace.watchlist — Market palette → Watchlist grid.

## dxTrade5 — Position Book

- [CRT-1713] Position Book bid/ask uses Quote stream first tier for the instrument.
> Oracle: tier-by-qty oracle — first TextConfiguration tier only.
> Harness: Chart flyout → Positions; verify bid/ask/mark columns.

## Adaptive — Instrument page

- [CRT-1717] Instrument page shows group-specific bid/ask for the logged-in account.
> Harness: Adaptive Instrument page — bid/ask reflects logged-in account group.

## dxTrade5 — Derivatives

- [CRT-1713] Derivatives widget bid/ask uses first tier Quote stream for FX_SPOT.
> Oracle: tier-by-qty oracle — first TextConfiguration tier.
> Harness: dxTrade5 widget switcher → Derivatives; live column verify on CTQA.

## WebBroker (client) — Client Area

- [CRT-1761] Client Area quote matches account group mapping for FX_SPOT.
> Harness: WebBroker Client Area palette → Watchlist; header account selects group suffix.

## WebBroker (dealer) — Backup Prices

- [CRT-1621] Backup Prices widget includes FX_SPOT in asset type filter; EOD midpoint captured.
> Harness: System Management → Backup Prices; verify FX_SPOT asset type filter post-drop.

## Cross-surface invariants

- [CRT-1717] Midpoint invariant: same midpoint across account groups while spreads may differ.
> Contrast: same FX_SPOT instrument — different account groups may show different bid/ask; midpoint must match across groups.

- [CRT-1714] Mark price equals midpoint for FX_SPOT on mark column surfaces.
> Note: Mark column on Positions/Watchlist FX_SPOT rows must equal midpoint (not bid/ask).

- [CRT-1761] dxCore show prices bid/ask from first TextConfiguration tier.
> Verified on CTQA: show prices EURUSD.spot (after use) — bid/ask from Quote stream.
> Prerequisite (console): show prices for target FX_SPOT symbol; bid/ask from first TextConfiguration tier (min volume).

## Out of scope

- Chart candles for fx-spot excluded (x) per operator final coverage.

## Backup and EOD

- [CRT-1621] EOD backup trading day captures midpoint for FX_SPOT.
> Verified: backup_price show symbol=EURUSD.spot; daily_data_recorder_config show (FOREX EOD schedules).
