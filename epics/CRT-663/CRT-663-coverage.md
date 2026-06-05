# CRT-663 — Smart Checklist (coverage)

## Primary focus

- Verify FX_SPOT orders, transfers, and positions that exist on the account are visible and consistent in dxTrade5 client-area widgets, WebBroker client-area books, and Adaptive client views—using console-issued orders on a single FX Spot instrument and the order→transfer→position workflow.

## Prerequisites and test data

- Console — place or locate FX Spot market and limit orders on one `.spot` instrument for a CTQA account (console-only creation path per Epic).
> Single instrument per validation pass; symbology per CT FX Spot docs.

## dxTrade5 — Orders, Transactions, Positions

- Orders widget lists `.spot` order with status, symbol, side, quantity, and filled quantity visible.
> Map GUI labels to dxCore DB states per Orders table (Sending/Working/Filled/Cancelled).

- Order History widget lists `.spot` order with status, symbol, side, quantity, and filled quantity per all order statuses.
> From Orders widget click on the `.spot` order to invoke Order History; verify against dxCore DB using Activities table.

- Transactions widget shows TRADE activity for `.spot` fills tied to the test order.
> Map GUI labels to dxCore DB states per Activities table (TRADE).

- Positions widget shows the `.spot` position row when account net quantity is non-zero after fill.
> Compare qty/side/symbol to console `show positions` or account statement.

## WebBroker (Trading Area) — Order book, Transactions, Position book

- Order book lists the same `.spot` order with fields consistent with dxTrade5 Orders widget.

- Transactions widget lists FX_SPOT transfers for the test account matching dxTrade5 Transactions for the same fill.

- Position book shows `.spot` position when qty ≠ 0 and dealer has view permission.

## Cross-surface parity — Adaptive (orders, transfers, positions)

- From Portfolio tab Working Orders show `.spot` WORKING order id/status/filled qty as dxTrade5 Orders and WebBroker Order book.

- Orders show `.spot` order id/status/filled qty as dxTrade5 Orders and WebBroker Order book for other statuses.

- Transactions widget shows the same `.spot` fill type, symbol, quantity, and time as Web and WB Transactions.

- Positions view shows the same `.spot` qty, side, and symbol as dxTrade5 Positions and WebBroker Position book.

## E2E workflow — order, transfer, position

- `.spot` Market order fill: order reaches COMPLETED in Orders/Order book, TRADE appears in both Transactions widgets, Positions/Position book updates net qty.
> Workflow: order (ACCEPTED→WORKING) → execution transfer → order (WORKING→COMPLETED) → position update.

- `.spot` Limit order fill: order reaches COMPLETED in Orders/Order book, TRADE appears in both Transactions widgets, Positions/Position book updates net qty.
> Workflow: order (ACCEPTED→WORKING) → execution transfer → order (WORKING→COMPLETED) → position update.

## Invariants under configuration change

- Dealer manual fill yields COMPLETED order and consistent transfer/position display on all in-scope surfaces.

- When account triggers Liquidation affecting FX Spot, order appears in Order book/Orders with liquidation origin marker.

## Out of epic scope (reference)

- FX Spot order placement from dxTrade5 or WebBroker UI — out of epic until product enables non-console entry.
- Multi-instrument FX Spot regression matrix — out of epic; use one `.spot` instrument per pass.
- Full FX Forward widget family — out of epic.
