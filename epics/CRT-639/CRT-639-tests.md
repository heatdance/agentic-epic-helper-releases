# CRT-639 — Regression test drafts

## Bundle map

| Bundle | Covers checks | Title |
|--------|---------------|-------|
| tb-001 | chk-001, chk-002, chk-003 | CRT-639: FX_SPOT WeightedAvg configuration and instrument posture |
| tb-002 | chk-005, chk-006, chk-007, chk-010, chk-011 | CRT-639: Weighted-average ladder and invariants |
| tb-003 | chk-008, chk-009 | CRT-639: Open P/L and percent PL gross formulas |

## tb-001: CRT-639: FX_SPOT WeightedAvg configuration and instrument posture

### Preconditions
- Complete environment setup per CRT-639-precon.md cluster *Account & system configuration* before executing this test.

### Actions
1. Epic scope: WeightedAvg FX_SPOT cash settlement: Confirm WeightedAvg FX_SPOT posture for <account_code> (Functional Configuration row, instrument subtype, group membership per precon).
2. Flat position before ladder: Confirm WeightedAvg FX_SPOT posture for <account_code> (Functional Configuration row, instrument subtype, group membership per precon).
3. FX_SPOT subtype WeightedAvg on instrument: Confirm WeightedAvg FX_SPOT posture for <account_code> (Functional Configuration row, instrument subtype, group membership per precon).
4. Flat position before ladder: Confirm WeightedAvg FX_SPOT posture for <account_code> (Functional Configuration row, instrument subtype, group membership per precon).
5. Reproducible configuration across shells: Confirm WeightedAvg FX_SPOT posture for <account_code> (Functional Configuration row, instrument subtype, group membership per precon).
6. Flat position before ladder: Confirm WeightedAvg FX_SPOT posture for <account_code> (Functional Configuration row, instrument subtype, group membership per precon).

### Results
1. Configuration matches CRT-1741 intent: End-to-end scope for CRT-1741 posture and metric families. [CRT-1741, CRT-1738]
2. Configuration matches CRT-1741 intent: Ladder vignette 1 for chk-001. [CRT-1741, CRT-1738]
3. Configuration matches CRT-1741 intent: Instrument posture matches CRT-1741. [CRT-1741]
4. Configuration matches CRT-1741 intent: Ladder vignette 1 for chk-002. [CRT-1741]
5. Configuration matches CRT-1741 intent: Same classification on dxTrade5, WebBroker, and Adaptive. [CRT-1741]
6. Configuration matches CRT-1741 intent: Ladder vignette 1 for chk-003. [CRT-1741]

### Peculiarities
- Resolve <cag_group_key> and <fx_config_group_key> from live show account_group_hierarchy on CTQA.

## tb-002: CRT-639: Weighted-average ladder and invariants

### Preconditions
- Complete environment setup per CRT-639-precon.md cluster *Account & system configuration* before executing this test.

### Actions
1. WeightedAvg window resets after zero cross: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
2. Flat position before ladder: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
3. First opening buy at <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
4. Second opening buy at different <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
5. Partial close without sign flip: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
6. Sell through zero to flat: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
7. Partial close without sign flip: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
8. Flat position before ladder: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
9. First opening buy at <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
10. Second opening buy at different <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
11. Partial close without sign flip: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
12. Sell through zero to flat: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
13. Multiple zero crossings in one session: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
14. Flat position before ladder: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
15. First opening buy at <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
16. Second opening buy at different <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
17. Partial close without sign flip: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
18. Sell through zero to flat: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
19. Realized P/L from average position price: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
20. Flat position before ladder: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
21. First opening buy at <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
22. Second opening buy at different <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
23. Partial close without sign flip: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
24. Sell through zero to flat: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
25. Opening trades only in average: Establish open FX_SPOT position on <account_code>, then read average fill via show position_metrics_from_publisher; record values before any config change.
26. Flat position before ladder: Establish open FX_SPOT position on <account_code>, then read average fill via show position_metrics_from_publisher; record values before any config change.

### Results
1. Position metrics and net size match WeightedAvg rules for WeightedAvg window resets after zero cross. [CRT-1740, CRT-1738] [oracle:TBD]
2. Position metrics and net size match WeightedAvg rules for Flat position before ladder. [CRT-1740, CRT-1738] [oracle:TBD]
3. Position metrics and net size match WeightedAvg rules for First opening buy at <price>. [CRT-1740, CRT-1738] [oracle:TBD]
4. Position metrics and net size match WeightedAvg rules for Second opening buy at different <price>. [CRT-1740, CRT-1738] [oracle:TBD]
5. Position metrics and net size match WeightedAvg rules for Partial close without sign flip. [CRT-1740, CRT-1738] [oracle:TBD]
6. Position metrics and net size match WeightedAvg rules for Sell through zero to flat. [CRT-1740, CRT-1738] [oracle:TBD]
7. Position metrics and net size match WeightedAvg rules for Partial close without sign flip. [CRT-1738] [oracle:TBD]
8. Position metrics and net size match WeightedAvg rules for Flat position before ladder. [CRT-1738] [oracle:TBD]
9. Position metrics and net size match WeightedAvg rules for First opening buy at <price>. [CRT-1738] [oracle:TBD]
10. Position metrics and net size match WeightedAvg rules for Second opening buy at different <price>. [CRT-1738] [oracle:TBD]
11. Position metrics and net size match WeightedAvg rules for Partial close without sign flip. [CRT-1738] [oracle:TBD]
12. Position metrics and net size match WeightedAvg rules for Sell through zero to flat. [CRT-1738] [oracle:TBD]
13. Position metrics and net size match WeightedAvg rules for Multiple zero crossings in one session. [CRT-1738] [oracle:TBD]
14. Position metrics and net size match WeightedAvg rules for Flat position before ladder. [CRT-1738] [oracle:TBD]
15. Position metrics and net size match WeightedAvg rules for First opening buy at <price>. [CRT-1738] [oracle:TBD]
16. Position metrics and net size match WeightedAvg rules for Second opening buy at different <price>. [CRT-1738] [oracle:TBD]
17. Position metrics and net size match WeightedAvg rules for Partial close without sign flip. [CRT-1738] [oracle:TBD]
18. Position metrics and net size match WeightedAvg rules for Sell through zero to flat. [CRT-1738] [oracle:TBD]
19. Position metrics and net size match WeightedAvg rules for Realized P/L from average position price. [CRT-1738] [oracle:TBD]
20. Position metrics and net size match WeightedAvg rules for Flat position before ladder. [CRT-1738] [oracle:TBD]
21. Position metrics and net size match WeightedAvg rules for First opening buy at <price>. [CRT-1738] [oracle:TBD]
22. Position metrics and net size match WeightedAvg rules for Second opening buy at different <price>. [CRT-1738] [oracle:TBD]
23. Position metrics and net size match WeightedAvg rules for Partial close without sign flip. [CRT-1738] [oracle:TBD]
24. Position metrics and net size match WeightedAvg rules for Sell through zero to flat. [CRT-1738] [oracle:TBD]
25. Average fill and realized P/L behavior match invariant: WeightedAvg-configured instruments. [CRT-1738]
26. Average fill and realized P/L behavior match invariant: Ladder vignette 1 for chk-011. [CRT-1738]

### Peculiarities
- Use command_patterns.ladder_step from precon; literary execution trade only during PREP.
- WeightedAvg opening-side average; realized on closes from average position price.
- [oracle:TBD] for cent-level ladder numerics pending XT-7911.
- Resolve <cag_group_key> and <fx_config_group_key> from live show account_group_hierarchy on CTQA.

## tb-003: CRT-639: Open P/L and percent PL gross formulas

### Preconditions
- Complete environment setup per CRT-639-precon.md cluster *Account & system configuration* before executing this test.

### Actions
1. Open P/L from mark minus average fill: After ladder on <account_code>, read Avg Fill Price, Open P/L, % PL Gross on dxTrade5 Positions and WebBroker Position Book; note mark source.
2. Flat position before ladder: After ladder on <account_code>, read Avg Fill Price, Open P/L, % PL Gross on dxTrade5 Positions and WebBroker Position Book; note mark source.
3. First opening buy at <price>: After ladder on <account_code>, read Avg Fill Price, Open P/L, % PL Gross on dxTrade5 Positions and WebBroker Position Book; note mark source.
4. Percent PL gross denominator: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
5. Flat position before ladder: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
6. First opening buy at <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
7. Second opening buy at different <price>: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
8. Partial close without sign flip: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher
9. Sell through zero to flat: use <account_code>; buy <qty> <instrument_symbol> at <price> gtc; show order last; execution trade orderkey=<orderkey> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now; show position_metrics_from_publisher

### Results
1. Open P/L and % PL gross match formulas in Peculiarities within [tolerance:TBD]. [CRT-1743]
2. Open P/L and % PL gross match formulas in Peculiarities within [tolerance:TBD]. [CRT-1743]
3. Open P/L and % PL gross match formulas in Peculiarities within [tolerance:TBD]. [CRT-1743]
4. Position metrics and net size match WeightedAvg rules for Percent PL gross denominator. [CRT-1742] [oracle:TBD]
5. Position metrics and net size match WeightedAvg rules for Flat position before ladder. [CRT-1742] [oracle:TBD]
6. Position metrics and net size match WeightedAvg rules for First opening buy at <price>. [CRT-1742] [oracle:TBD]
7. Position metrics and net size match WeightedAvg rules for Second opening buy at different <price>. [CRT-1742] [oracle:TBD]
8. Position metrics and net size match WeightedAvg rules for Partial close without sign flip. [CRT-1742] [oracle:TBD]
9. Position metrics and net size match WeightedAvg rules for Sell through zero to flat. [CRT-1742] [oracle:TBD]

### Peculiarities
- Open P/L = position_qty * (mark_price - average_fill_price) * multiplier (CRT-1743).
- Percent PL gross = (Open PL / ABS(SUM(average_price * qty * multiplier))) * 100 (CRT-1742).
- UI labels: dxTrade5 Avg Fill Price, Open P/L, % PL Gross; WebBroker Avg Price.
- Use command_patterns.ladder_step from precon; literary execution trade only during PREP.
- WeightedAvg opening-side average; realized on closes from average position price.
- [oracle:TBD] for cent-level ladder numerics pending XT-7911.
