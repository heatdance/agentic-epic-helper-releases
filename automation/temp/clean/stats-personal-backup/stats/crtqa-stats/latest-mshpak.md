# CRTQA stats

- **Generated:** 2026-05-29T10:32:09Z
- **User:** `mshpak`
- **Counts:** 33 epics in corpus · 37 corpus rows · 0 comparison rows · 1 AI-assisted epics · 1059 tests scanned
- **Display tier:** `collapsed`

**Display tiers:** **full** — both Small and Big subcategories have ≥4 epics; show category×subcategory detail. **partial** — some subcategories are sparse; prefer category rollup. **collapsed** — two or more categories are not full; lead with collapsed rollup, then category×subcategory. **Collapsed rollup** splits into Small/Big TCD rows when **both** bands have ≥4 corpus epics; otherwise one all-corpus row.

**AI-assisted epics** — operator-attested at initial assessment (`attestation_by_epic`) and/or epics with **comparison** Done TCD rows after incremental update. **AI logged avg** and **Saved %** use comparison rows only (Done TCD with user worklogs); attested-only epics count toward **AI epics** but not avg/Saved until logged.

## Collapsed rollup


| Subcategory      | Epics | Median draft (h) | Median logged (h) | AI epics | AI logged avg (h) | Saved % |
| ---------------- | ----- | ---------------- | ----------------- | -------- | ----------------- | ------- |
| Small TCD (≤16h) | 20    | 8.00             | 7.10              | 1        | —                 | —       |
| Big TCD (>16h)   | 14    | 22.50            | 21.15             | 0        | —                 | —       |


## Category rollup


| Category          | Subcategory      | Epics | Median draft (h) | Median logged (h) | AI epics | AI logged avg (h) | Saved % |
| ----------------- | ---------------- | ----- | ---------------- | ----------------- | -------- | ----------------- | ------- |
| FE Epic           | Small TCD (≤16h) | 7     | 8.00             | 5.99              | 1        | —                 | —       |
| FE Epic           | Big TCD (>16h)   | 5     | 19.00            | 20.10             | 0        | —                 | —       |
| BE Epic           | Small TCD (≤16h) | 11    | 8.00             | 8.48              | 0        | —                 | —       |
| BE Epic           | Big TCD (>16h)   | 8     | 27.00            | 22.73             | 0        | —                 | —       |
| API / Integration | Small TCD (≤16h) | 2     | 8.00             | 10.28             | 0        | —                 | —       |
| API / Integration | Big TCD (>16h)   | 1     | 20.00            | 22.80             | 0        | —                 | —       |
| Other             | Small TCD (≤16h) | 0     | —                | —                 | 0        | —                 | —       |
| Other             | Big TCD (>16h)   | 0     | —                | —                 | 0        | —                 | —       |


## Epic breakdown


| Epic                                                     | Category | Draft (h) | Logged (h) | Note                                                                                                                                                                                                                                              |
| -------------------------------------------------------- | -------- | --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [CRT-171](https://jira.in.devexperts.com/browse/CRT-171) | FE+S     | 4.00      | 6.55       | [PenTest] Sensitive Information Sent via HTTTP GET Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): [PenTest] Sensitive Information Sent via HTTTP GET.                                                                             |
| [CRT-290](https://jira.in.devexperts.com/browse/CRT-290) | FE+S     | 8.00      | 4.47       | Mapping algorithm update for Hong-Kong CFD_STOCK DXTF charting update using Candle.bid when instrument flagged (CRT-983); client chart UI.                                                                                                        |
| [CRT-308](https://jira.in.devexperts.com/browse/CRT-308) | FE+S     | 7.00      | 7.10       | Add Slide-In Coefficient to Position Book in dxTrade Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Add Slide-In Coefficient to Position Book in dxTrade.                                                                         |
| [CRT-320](https://jira.in.devexperts.com/browse/CRT-320) | FE+S     | 24.00     | 7.00       | Fix price for spreads in all transaction and trade widgets Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Fix price for spreads in all transaction and trade widgets.                                                             |
| [CRT-340](https://jira.in.devexperts.com/browse/CRT-340) | FE+S     | 16.00     | 5.43       | Value Position CCY / %change (HORN-511) Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Value Position CCY / %change (HORN-511).                                                                                                   |
| [CRT-563](https://jira.in.devexperts.com/browse/CRT-563) | FE+S     | 4.00      | 0.97       | Add filters by Instrument fields in Order Book widget in Web Broker (HORN-1092) Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Add filters by Instrument fields in Order Book widget in Web Broker (HORN-1092).                   |
| [CRT-76](https://jira.in.devexperts.com/browse/CRT-76)   | FE+S     | 15.00     | 7.98       | Taxes support in UI Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Taxes support in UI.                                                                                                                                           |
| [CRT-131](https://jira.in.devexperts.com/browse/CRT-131) | FE+B     | 18.00     | 5.95       | Fix Liquidation order statuses Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Fix Liquidation order statuses.                                                                                                                     |
| [CRT-147](https://jira.in.devexperts.com/browse/CRT-147) | FE+B     | 18.00     | 18.73      | Process raw parameter files from IG - Swap Rates Update Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Process raw parameter files from IG - Swap Rates Update.                                                                   |
| [CRT-19](https://jira.in.devexperts.com/browse/CRT-19)   | FE+B     | 24.00     | 20.10      | Financing Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Financing.                                                                                                                                                               |
| [CRT-530](https://jira.in.devexperts.com/browse/CRT-530) | FE+B     | 40.00     | 82.85      | CA management between AF and DX with quantity impact (HORN-372) - Simplified version Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): CA management between AF and DX with quantity impact (HORN-372) - Simplified ver.             |
| [CRT-79](https://jira.in.devexperts.com/browse/CRT-79)   | FE+B     | 19.00     | 20.35      | Align financing with IG rules Major work is client-facing UI (dxTrade5/WebBroker/charts/OE): Align financing with IG rules.                                                                                                                       |
| [CRT-110](https://jira.in.devexperts.com/browse/CRT-110) | BE+S     | 14.00     | 8.80       | [CRT] Undefined margin rates Major work is server-side logic, metrics, jobs, or risk/settlement: [CRT] Undefined margin rates.                                                                                                                    |
| [CRT-129](https://jira.in.devexperts.com/browse/CRT-129) | BE+S     | 16.00     | 9.38       | Risk management EOD report Major work is server-side logic, metrics, jobs, or risk/settlement: Risk management EOD report.                                                                                                                        |
| [CRT-286](https://jira.in.devexperts.com/browse/CRT-286) | BE+S     | 16.00     | 14.82      | CPS commission per underlying (FUTURE and OPTION commissions) CPS commission rules per underlying for FUTURE/OPTION.                                                                                                                              |
| [CRT-287](https://jira.in.devexperts.com/browse/CRT-287) | BE+S     | 16.00     | 13.97      | Collateral Profile Major work is server-side logic, metrics, jobs, or risk/settlement: Collateral Profile.                                                                                                                                        |
| [CRT-30](https://jira.in.devexperts.com/browse/CRT-30)   | BE+S     | 13.00     | 19.44      | Exposure limits by instrument Major work is server-side logic, metrics, jobs, or risk/settlement: Exposure limits by instrument.                                                                                                                  |
| [CRT-306](https://jira.in.devexperts.com/browse/CRT-306) | BE+S     | 8.00      | 9.13       | Fix metrics when there is a short equity position Major work is server-side logic, metrics, jobs, or risk/settlement: Fix metrics when there is a short equity position.                                                                          |
| [CRT-341](https://jira.in.devexperts.com/browse/CRT-341) | BE+S     | 4.17      | 21.87      | Liquidation proposal (HORN-502) - Mark Price update based on trading hours Major work is server-side logic, metrics, jobs, or risk/settlement: Liquidation proposal (HORN-502) - Mark Price update based on trading hours.                        |
| [CRT-41](https://jira.in.devexperts.com/browse/CRT-41)   | BE+S     | 5.17      | 3.23       | Available Balance For Withdrawal Withdrawal balance metric and liquidation-domain limit calculation (CRT-069, CRT-091).                                                                                                                           |
| [CRT-49](https://jira.in.devexperts.com/browse/CRT-49)   | BE+S     | 1.25      | 2.80       | Add IG instrument ID field to instruments Instrument master field for IG instrument ID.                                                                                                                                                           |
| [CRT-544](https://jira.in.devexperts.com/browse/CRT-544) | BE+S     | 5.00      | 3.47       | Console command to move positions to new instrument symbols (HORN-747) Major work is server-side logic, metrics, jobs, or risk/settlement: Console command to move positions to new instrument symbols (HORN-747).                                |
| [CRT-1](https://jira.in.devexperts.com/browse/CRT-1)     | BE+B     | 21.00     | 20.55      | CFD Margining Major work is server-side logic, metrics, jobs, or risk/settlement: CFD Margining.                                                                                                                                                  |
| [CRT-18](https://jira.in.devexperts.com/browse/CRT-18)   | BE+B     | 24.00     | 28.15      | Margin calls and liquidation Major work is server-side logic, metrics, jobs, or risk/settlement: Margin calls and liquidation.                                                                                                                    |
| [CRT-183](https://jira.in.devexperts.com/browse/CRT-183) | BE+B     | 30.00     | 16.93      | [CT ETD] Portfolio metrics Major work is server-side logic, metrics, jobs, or risk/settlement: [CT ETD] Portfolio metrics.                                                                                                                        |
| [CRT-236](https://jira.in.devexperts.com/browse/CRT-236) | BE+B     | 30.00     | 30.25      | CFDs Shares - updating parameters (Horn-365 High) Major work is server-side logic, metrics, jobs, or risk/settlement: CFDs Shares - updating parameters (Horn-365 High).                                                                          |
| [CRT-350](https://jira.in.devexperts.com/browse/CRT-350) | BE+B     | 40.00     | 41.02      | Liquidation proposal - Liquidation improvements Major work is server-side logic, metrics, jobs, or risk/settlement: Liquidation proposal - Liquidation improvements.                                                                              |
| [CRT-373](https://jira.in.devexperts.com/browse/CRT-373) | BE+B     | 18.00     | 9.93       | Price snapshot and backup price update schedules should depend on instrument type Major work is server-side logic, metrics, jobs, or risk/settlement: Price snapshot and backup price update schedules should depend on instrument typ.           |
| [CRT-380](https://jira.in.devexperts.com/browse/CRT-380) | BE+B     | 40.00     | 23.70      | Liquidation proposal - Fix remaining issues (instruments without close price + summary gap) Major work is server-side logic, metrics, jobs, or risk/settlement: Liquidation proposal - Fix remaining issues (instruments without close price + s. |
| [CRT-91](https://jira.in.devexperts.com/browse/CRT-91)   | BE+B     | 18.00     | 21.75      | Portfolio statement Major work is server-side logic, metrics, jobs, or risk/settlement: Portfolio statement.                                                                                                                                      |
| [CRT-46](https://jira.in.devexperts.com/browse/CRT-46)   | API+S    | 8.00      | 9.25       | FIX trading integration with IG (OTC) FIX trading integration with IG OTC (CRT-096).                                                                                                                                                              |
| [CRT-672](https://jira.in.devexperts.com/browse/CRT-672) | API+S    | 24.00     | 20.91      | Add Taxes, Commissions and External Fees to CA API Extend Apply CA Transactions API with tax, commission, and fee fields (CRT-1918–1920).                                                                                                         |
| [CRT-264](https://jira.in.devexperts.com/browse/CRT-264) | API+B    | 20.00     | 22.80      | Consider Last Trade Time on Last Trade Date of options dxFeed LAST_TRADE_TIME in IPF and platform trading-end logic (external market data).                                                                                                       |


## AI Epic breakdown


| Epic                                                     | Category | Draft (h) | Logged (h) | Note                                                                                                                                                                                               |
| -------------------------------------------------------- | -------- | --------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [CRT-594](https://jira.in.devexperts.com/browse/CRT-594) | FE+S     | —         | —          | FX_SPOT Pricing (groups and mapping to dxFeed) AI-assisted; excluded from corpus at initial assessment. FX_SPOT pricing groups and mapping UI/configuration for client pricing (AI-assisted epic). |


