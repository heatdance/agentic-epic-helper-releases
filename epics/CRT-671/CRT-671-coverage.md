# CRT-671

## Primary focus

- Verify that when dxCore order status is ACCEPTED, client shells show UI label 'Sending' (not 'Working') on dxTrade5 web, WebBroker, and Adaptive, and that Adaptive lists Sending orders in Working orders on Portfolio and Account pages.

## Order placement and ACCEPTED state reachability

- [CRT-671] Issue a market or limit order on CTQA and observe dxCore status ACCEPTED before external execution confirmation.
> Verified on CTQA: show order last [n] [open] after use <account> — inspect dxCore status for ACCEPTED before UI Sending check.
> Harness: CTQA retail account with order-entry entitlement; issue order via dxTrade5 OE or API path per env profile.

- [CRT-1902] ACCEPTED means validation-to-execution passed and brokerage backend accepted; external party confirmation not yet received — UI must show Sending during this window.
> Note: Timing-sensitive — capture UI while dxCore remains ACCEPTED and before WORKING transition.

## Cross-shell Sending label when dxCore is ACCEPTED

- [CRT-1902] [CRT-1726] When dxCore order status is ACCEPTED, all in-scope client shells map the GUI label to Sending per updated order statuses table.
> Contrast: legacy XT manuals mapped ACCEPTED to Working; Corner delta requires Sending label.

## Adaptive Working orders list membership for Sending

- [CRT-671] Adaptive orders with UI status Sending appear in Working orders on Portfolio tab and Account page (not only in a terminal/history view).
> Harness: Adaptive Portfolio tab → Working orders; repeat on Account page.
> Note: Harness maps do not yet sample Sending label — live CTQA probe required.

## dxTrade5 — Orders

- [CRT-1902] [FAILED] dxTrade5 Orders widget Status column shows Sending (not Working) when dxCore order status is ACCEPTED.
> Harness: Chart title-bar icon switcher → Orders widget; Status column beside Instrument/Side.
> Verified on CTQA: Orders grid exposes Status column; in-flight Sending label not in harness samples — probe with ACCEPTED order.

- [CRT-1902] [FAILED] Modify and Cancel actions remain available for orders in Sending status.
> Note: Epic validation XT-8616 actions unavailable for Sending orders.

## WebBroker (dealer) — Order Book

- [CRT-1902] [FAILED] WebBroker Order Book displays order with Status Sending when dxCore is ACCEPTED and order is visible in the book.
> Harness: Workspace 1 → Order Book tile; Status column with Filter by Status.
> Note: Epic validation XT-8494 — Sending orders not displayed in Order Book.

- [CRT-1902] [FAILED] Order Book does not show duplicated OrderStatus and CtOrderStatus columns for Corner.
> Note: Epic validation XT-8216 duplicated status columns.

## Adaptive — Orders status display

- [CRT-1902] Adaptive order status label shows Sending when dxCore order status is ACCEPTED.
> Harness: Adaptive order detail / status field during ACCEPTED window.

## Adaptive — Working orders (Portfolio tab)

- [CRT-671] Sending order appears in Working orders list on Adaptive Portfolio tab.
> Harness: Adaptive Portfolio → Working orders section.

## Adaptive — Working orders (Account page)

- [CRT-671] Sending order appears in Working orders list on Adaptive Account page.
> Harness: Adaptive Account page → Working orders section.

## dxTrade5 — Order History

- [CRT-1902] [FAILED] Order History status filter and row labels include Sending (not Working-only filter set).
> Harness: Orders widget lower pane Order History; status filter list.
> Note: Epic validation XT-8615 incorrect status filter list.

## Adaptive — Order History

- [CRT-1902] [FAILED] Adaptive Order History shows Sending label consistently for ACCEPTED-phase orders.
> Note: Epic validation CAN-14623 incorrect Sending display in Order History.

## Cross-shell order status mapping

- [CRT-1726] Platform order-status mapping regression: ACCEPTED → Sending label family consistent with CT order statuses table (not upstream Working-only label).
> Note: XT upstream manuals reference Sending for NEW and Working for ACCEPTED; Corner table maps ACCEPTED→Sending.
