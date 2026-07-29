# CRT-663 — Regression test drafts

## Bundle map

| Bundle | Covers checks | Title |
|--------|---------------|-------|
| tb-001 | chk-001, chk-002 | CRT-663: FX Spot account and instrument configuration |
| tb-002 | chk-003, chk-004, chk-005, chk-006 | CRT-663: dxTrade5 Orders, Transactions, Positions widgets |
| tb-003 | chk-007, chk-008, chk-009 | CRT-663: WebBroker Client Area and dealer books |
| tb-004 | chk-010, chk-011, chk-012, chk-013 | CRT-663: Adaptive cross-surface parity |
| tb-005 | chk-016 | CRT-663: WebBroker dealer manual trade invariant |
| tb-006 | chk-017 | CRT-663: Margin liquidation closing order invariant |
| tb-007 | chk-018, chk-019, chk-020 | CRT-663: Market FX Spot flow (atomic) |
| tb-008 | chk-021, chk-022, chk-023 | CRT-663: Limit FX Spot flow (atomic) |
| tb-009 | chk-024, chk-025, chk-026 | CRT-663: Stop FX Spot flow (atomic) |

## tb-001: CRT-663: FX Spot account and instrument configuration

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Epic scope: FX_SPOT orders, transfers, positions visibility: use <account_code>; place or locate EURUSD.spot activity per precon step 7; record order key for UI verification.
2. Console FX Spot market, limit, and stop orders on EURUSD.spot: use <account_code>; buy <qty> <instrument_symbol> at <off_market_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now
3. Console FX Spot market, limit, and stop orders on EURUSD.spot — dxTrade5 shell: use <account_code>; buy <qty> <instrument_symbol> at <off_market_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now
4. Console FX Spot market, limit, and stop orders on EURUSD.spot — WebBroker shell: use <account_code>; buy <qty> <instrument_symbol> at <off_market_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now

### Results
1. Observable outcome matches coverage: Cross-surface display for one .spot instrument and order→transfer→position workflow. [CRT-663]
2. Observable outcome matches coverage: Prerequisite orders exist for widget parity (console-only creation path). [CRT-663]
3. Observable outcome matches coverage: Prerequisite orders exist for widget parity (console-only creation path) (dxTrade5 shell). [CRT-663]
4. Observable outcome matches coverage: Prerequisite orders exist for widget parity (console-only creation path) (WebBroker shell). [CRT-663]

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).

## tb-002: CRT-663: dxTrade5 Orders, Transactions, Positions widgets

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Orders widget FX Spot row: Log in to dxTrade5 as <account_code>; open Orders, Account Transactions, Positions, or Order History widget per case intent; filter or locate EURUSD.spot row.
2. Order History for .spot order: Log in to dxTrade5 as <account_code>; open Orders, Account Transactions, Positions, or Order History widget per case intent; filter or locate EURUSD.spot row.
3. Account Transactions TRADE for fill: Log in to dxTrade5 as <account_code>; open Orders, Account Transactions, Positions, or Order History widget per case intent; filter or locate EURUSD.spot row.
4. Positions widget net qty after fill: Log in to dxTrade5 as <account_code>; open Orders, Account Transactions, Positions, or Order History widget per case intent; filter or locate EURUSD.spot row.

### Results
1. Observable outcome matches coverage: Status, symbol, side, quantity, filled qty visible. [CRT-663]
2. Observable outcome matches coverage: All statuses in chart flyout history band. [CRT-663]
3. Observable outcome matches coverage: TRADE activity tied to test order. [CRT-663]
4. Observable outcome matches coverage: Non-zero position row when account has FX Spot exposure. [CRT-663]

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).

## tb-003: CRT-663: WebBroker Client Area and dealer books

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Client Area and dealer Order book parity: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.
2. Client Area Account Transactions TRADE: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.
3. Client Area Account Transactions TRADE — dxTrade5 shell: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.
4. Client Area Account Transactions TRADE — WebBroker shell: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.
5. Client Area and dealer Position book: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.

### Results
1. Observable outcome matches coverage: Same .spot order status/symbol/side/qty/filled qty. [CRT-663]
2. Observable outcome matches coverage: FX_SPOT TRADE matches dxTrade5 for same fill. [CRT-663]
3. Observable outcome matches coverage: FX_SPOT TRADE matches dxTrade5 for same fill (dxTrade5 shell). [CRT-663]
4. Observable outcome matches coverage: FX_SPOT TRADE matches dxTrade5 for same fill (WebBroker shell). [CRT-663]
5. Observable outcome matches coverage: Position row when qty ≠ 0. [CRT-663]

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).

## tb-004: CRT-663: Adaptive cross-surface parity

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Adaptive Working Orders WORKING row: Open Adaptive Portfolio for <account_code>; verify Working Orders, Trade History, or Positions section shows EURUSD.spot row per case intent.
2. Adaptive orders for other statuses: Open Adaptive Portfolio for <account_code>; verify Working Orders, Trade History, or Positions section shows EURUSD.spot row per case intent.
3. Adaptive Trade History fill: Open Adaptive Portfolio for <account_code>; verify Working Orders, Trade History, or Positions section shows EURUSD.spot row per case intent.
4. Adaptive Positions qty/side/symbol: Open Adaptive Portfolio for <account_code>; verify Working Orders, Trade History, or Positions section shows EURUSD.spot row per case intent.

### Results
1. Observable outcome matches coverage: Matches dxTrade5 Orders and WB Order book. [CRT-663]
2. Observable outcome matches coverage: Filled/cancelled/rejected parity across shells. [CRT-663]
3. Observable outcome matches coverage: Symbol, quantity, time match web Transactions. [CRT-663]
4. Observable outcome matches coverage: Matches dxTrade5 Positions and WB Position book. [CRT-663]

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).

## tb-005: CRT-663: WebBroker dealer manual trade invariant

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Dealer manual trade on routed FX Spot order: use <account_code>; place or locate EURUSD.spot activity per precon step 7; record order key for UI verification.
2. Dealer manual trade on routed FX Spot order — dxTrade5 shell: use <account_code>; place or locate EURUSD.spot activity per precon step 7; record order key for UI verification.

### Results
1. Observable outcome matches coverage: COMPLETED order plus TRADE and position rows consistent on all shells; ET path is auto fill/reject only. [CRT-663] Dealer manual trade path — ET FX Spot is auto fill/reject only.
2. Observable outcome matches coverage: COMPLETED order plus TRADE and position rows consistent on all shells; ET path is auto fill/reject only (dxTrade5 shell). [CRT-663] Dealer manual trade path — ET FX Spot is auto fill/reject only.

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).
- Manual fill is WebBroker/dxCore dealer action (Order Statuses transitions 17/23), not ET broker intervention.

## tb-006: CRT-663: Margin liquidation closing order invariant

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Margin liquidation FX Spot closing market order: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.
2. Margin liquidation FX Spot closing market order — dxTrade5 shell: Log in to WebBroker dealer UI; open Client Area or Trading Order Book / Position Book; locate EURUSD.spot row for <account_code>.

### Results
1. Observable outcome matches coverage: Closing order visible in Orders/Order book with liquidation origin marker. [CRT-663] Margin liquidation closing order shows liquidation origin marker when triggered.
2. Observable outcome matches coverage: Closing order visible in Orders/Order book with liquidation origin marker (dxTrade5 shell). [CRT-663] Margin liquidation closing order shows liquidation origin marker when triggered.

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).

## tb-007: CRT-663: Market FX Spot flow (atomic)

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Market order visibility (atomic): use <account_code>; buy <qty> <instrument_symbol> mkt fok; show order last
2. Market TRADE row (atomic): use <account_code>; buy <qty> <instrument_symbol> mkt fok; show order last
3. Market TRADE row (atomic) — dxTrade5 shell: use <account_code>; buy <qty> <instrument_symbol> mkt fok; show order last
4. Market TRADE row (atomic) — WebBroker shell: use <account_code>; buy <qty> <instrument_symbol> mkt fok; show order last
5. Market position update (atomic): use <account_code>; buy <qty> <instrument_symbol> mkt fok; show order last

### Results
1. Observable outcome matches coverage: Order status/symbol/side/qty/filled qty on all shells. [CRT-663] Market UI placement may be defect-sensitive; console-issued row still drives check.
2. Observable outcome matches coverage: TRADE in Account Transactions and Trade History. [CRT-663] Market UI placement may be defect-sensitive; console-issued row still drives check.
3. Observable outcome matches coverage: TRADE in Account Transactions and Trade History (dxTrade5 shell). [CRT-663] Market UI placement may be defect-sensitive; console-issued row still drives check.
4. Observable outcome matches coverage: TRADE in Account Transactions and Trade History (WebBroker shell). [CRT-663] Market UI placement may be defect-sensitive; console-issued row still drives check.
5. Observable outcome matches coverage: Net qty/side/symbol after Market fill. [CRT-663] Market UI placement may be defect-sensitive; console-issued row still drives check.

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).
- Limit/Stop console prices must be significantly off market; use help buy and help stp_order on CTQA.

## tb-008: CRT-663: Limit FX Spot flow (atomic)

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Limit order COMPLETED visibility (atomic): use <account_code>; buy <qty> <instrument_symbol> at <off_market_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now
2. Limit TRADE row (atomic): use <account_code>; buy <qty> <instrument_symbol> at <off_market_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now
3. Limit position update (atomic): use <account_code>; buy <qty> <instrument_symbol> at <off_market_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now

### Results
1. Observable outcome matches coverage: Order row on all shells after off-market fill. [CRT-663]
2. Observable outcome matches coverage: TRADE leg separate from order/position checks. [CRT-663]
3. Observable outcome matches coverage: Position net qty after Limit fill. [CRT-663]

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).
- Limit/Stop console prices must be significantly off market; use help buy and help stp_order on CTQA.

## tb-009: CRT-663: Stop FX Spot flow (atomic)

### Preconditions
- Complete environment setup per CRT-663-precon.md cluster *Account & FX Spot configuration* before executing this test.

### Actions
1. Stop order visibility (atomic): use <account_code>; stp_order buy <qty> <instrument_symbol> stop=<stop_price> limit=<limit_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now
2. Stop TRADE row (atomic): use <account_code>; stp_order buy <qty> <instrument_symbol> stop=<stop_price> limit=<limit_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now
3. Stop position update (atomic): use <account_code>; stp_order buy <qty> <instrument_symbol> stop=<stop_price> limit=<limit_price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now

### Results
1. Observable outcome matches coverage: Triggered Stop order on all shells. [CRT-663]
2. Observable outcome matches coverage: TRADE after Stop fill. [CRT-663]
3. Observable outcome matches coverage: Position after Stop fill. [CRT-663]

### Peculiarities
- Instrument symbology: EURUSD.spot per CT FX Spot docs; single instrument per pass.
- Column labels grounded from prep_verify_view exploration (Orders Status/Symbol/Side/Qty/Filled Qty).
- Limit/Stop console prices must be significantly off market; use help buy and help stp_order on CTQA.

