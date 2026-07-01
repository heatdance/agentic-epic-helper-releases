# CRT-663 — Smart Checklist (coverage)

## Primary focus

- Verify FX_SPOT orders, transfers, and positions that exist on the account are visible and consistent in dxTrade5 client-area widgets, WebBroker client-area books, and Adaptive client views—using console-issued orders on a single FX Spot instrument and the order→transfer→position workflow.

## Prerequisites and test data

- Console — place or locate FX Spot market, limit, and stop orders on one `.spot` instrument (EURUSD.spot) for parity account (console-only creation path per Epic).
> Single instrument per validation pass; symbology per CT FX Spot docs.
> Limit/Stop may require price significantly off market; market path may be defect-sensitive in UI.

## dxTrade5 — Orders, Transactions, Positions

- Orders widget lists .spot order with status, symbol, side, quantity, and filled quantity visible.
> Map GUI labels to dxCore DB states per Orders table (Sending/Working/Filled/Cancelled).

- Order History widget lists .spot order with status, symbol, side, quantity, and filled quantity per all order statuses.
> Chart widget icon- flyout → Orders; select `.spot` order → lower band Order History.
> Verify against dxCore DB Activities table.

- Transactions widget shows TRADE activity for .spot fills tied to the test order.
> Map GUI labels to dxCore DB states per Activities table (TRADE).

- Positions widget shows the .spot position row when account net quantity is non-zero after fill.
> Compare qty/side/symbol to console show positions or account statement.

## WebBroker — Client Area and dealer books

- Client Area Orders widget (and dealer Order book) list the same `.spot` order with status, symbol, side, quantity, filled qty.
> Client Area via header flyout; dealer Order book via Trading workspace.

- Client Area Account Transactions lists FX_SPOT TRADE for the test account matching dxTrade5 Account Transactions for the same fill.

- Client Area Positions (and dealer Position book) show `.spot` position when qty ≠ 0 and dealer has view permission.

## Cross-surface parity — Adaptive (orders, transfers, positions)

- From Portfolio tab Working Orders show .spot WORKING order id/status/filled qty as dxTrade5 Orders and WebBroker Order book.

- Orders show .spot order id/status/filled qty as dxTrade5 Orders and WebBroker Order book for other statuses.

- Transactions widget shows the same .spot fill type, symbol, quantity, and time as Web and WB Transactions.

- Positions view shows the same .spot qty, side, and symbol as dxTrade5 Positions and WebBroker Position book.

## Invariants under configuration change

- WebBroker dealer manual trade on routed FX Spot order yields COMPLETED internal order; TRADE and position rows consistent on dxTrade5, WebBroker Client Area, and Adaptive.
> ET FIX FX Spot path is auto ExecutionReport fill/reject only — not dealer manual fill.
> Manual trade = dxCore dealer action per CT Order Statuses transitions 17/23.

- When margin liquidation affects FX Spot, closing market order appears in Orders/Order book with liquidation origin marker.
> Margin liquidation spawns FX_SPOT market closing orders (CT Margin Call and Liquidations).
> WB Order book marks Margin Utilization; option/futures liquidation types out of scope.

## E2E — Market FX Spot flow (atomic)

- After console-issued `.spot` Market order (or existing filled Market row), order status/symbol/side/qty/filled qty visible in dxTrade5 Orders, WB Client Area Orders, Adaptive Working Orders.
> Market UI placement may be blocked by known defect — console fill still drives visibility checks.
> Workflow leg: order ACCEPTED→WORKING→COMPLETED per Order Statuses.

- TRADE row for Market fill appears in dxTrade5 Account Transactions, WB Client Area Account Transactions, Adaptive Trade History with matching symbol/qty/order id.
> Map to Activities TRADE; atomic trade leg separate from order/position checks.

- Positions net qty/side/symbol for Market fill updates in dxTrade5 Positions, WB Client Area Positions, Adaptive Positions.
> Compare to console `show positions`; atomic position leg.

## E2E — Limit FX Spot flow (atomic)

- After console-issued `.spot` Limit order fill, order reaches COMPLETED with status/symbol/side/qty/filled qty in dxTrade5 Orders, WB Client Area Orders, Adaptive orders views.
> Limit price must be adjusted significantly off market to route; UI-driving scenario.
> Workflow leg: order only — not bundled with trade/position.

- TRADE row for Limit fill appears in dxTrade5 Account Transactions, WB Client Area Account Transactions, Adaptive Trade History.
> Atomic trade leg for Limit flow.

- Positions net qty/side/symbol updates for Limit fill in dxTrade5 Positions, WB Client Area Positions, Adaptive Positions.
> Atomic position leg for Limit flow.

## E2E — Stop FX Spot flow (atomic)

- After console-issued `.spot` Stop order (triggered to fill), order status/symbol/side/qty/filled qty visible in dxTrade5 Orders, WB Client Area Orders, Adaptive Working Orders.
> Stop hosted until trigger; stop price off market; ET NewOrderSingle OrdType Stop.
> Atomic order leg for Stop flow.

- TRADE row for Stop fill appears in dxTrade5 Account Transactions, WB Client Area Account Transactions, Adaptive Trade History.
> Atomic trade leg for Stop flow.

- Positions net qty/side/symbol updates for Stop fill in dxTrade5 Positions, WB Client Area Positions, Adaptive Positions.
> Atomic position leg for Stop flow.

## Out of epic scope (reference)

- FX Spot order entry from dxTrade5 or WebBroker UI (non-console) — out of epic — Jira states console is the only way to create FX Spot orders today (obl-014).
- Multi-instrument FX Spot regression matrix — out of epic — single instrument EURUSD.spot per obl-013.
- FX Forward instrument widgets and RFQ flows — out of epic — CRT-663 is FX_SPOT visibility only.
- Deep rollover statement/export-only scenarios — out of epic — rollover may appear in Transactions but not Epic AC.
