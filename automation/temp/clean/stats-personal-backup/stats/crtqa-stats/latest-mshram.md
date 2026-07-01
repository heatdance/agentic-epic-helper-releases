# CRTQA stats

- **Generated:** 2026-06-12T10:45:59Z
- **User:** `mshram`
- **Counts:** 5 epics in corpus · 9 corpus rows · 0 comparison rows · 0 AI-assisted epics · 34 tests scanned
- **Display tier:** `collapsed`

**Display tiers:** **full** — both Small and Big subcategories have ≥4 epics; show category×subcategory detail. **partial** — some subcategories are sparse; prefer category rollup. **collapsed** — two or more categories are not full; lead with collapsed rollup, then category×subcategory. **Collapsed rollup** splits into Small/Big TCD rows when **both** bands have ≥4 corpus epics; otherwise one all-corpus row.

**AI-assisted epics** — operator-attested at initial assessment (`attestation_by_epic`) and/or epics with **comparison** Done TCD rows after incremental update. **AI logged avg** and **Saved %** use comparison rows only (Done TCD with user worklogs); attested-only epics count toward **AI epics** but not avg/Saved until logged.

## Collapsed rollup

| Epics | Median draft (h) | Median logged (h) | AI epics | AI logged avg (h) | Saved % |
|------:|-----------------:|------------------:|---------:|------------------:|--------:|
| 5 | 16.00 | 18.85 | 0 | — | — |

## Category rollup

| Category | Subcategory | Epics | Median draft (h) | Median logged (h) | AI epics | AI logged avg (h) | Saved % |
|----------|-------------|------:|-----------------:|------------------:|---------:|------------------:|--------:|
| FE Epic | Small TCD (≤16h) | 3 | 12.00 | 18.79 | 0 | — | — |
| FE Epic | Big TCD (>16h) | 0 | — | — | 0 | — | — |
| BE Epic | Small TCD (≤16h) | 2 | 10.50 | 24.01 | 0 | — | — |
| BE Epic | Big TCD (>16h) | 1 | 24.00 | 53.67 | 0 | — | — |
| API / Integration | Small TCD (≤16h) | 0 | — | — | 0 | — | — |
| API / Integration | Big TCD (>16h) | 0 | — | — | 0 | — | — |
| Other | Small TCD (≤16h) | 0 | — | — | 0 | — | — |
| Other | Big TCD (>16h) | 0 | — | — | 0 | — | — |
## Epic breakdown

| Epic | Category | Draft (h) | Logged (h) | Note |
|------|----------|----------:|-----------:|------|
| [CRT-572](https://jira.in.devexperts.com/browse/CRT-572) | FE+S | 24.00 | 58.30 | Port Chart Trading Panel (HORN-1196)<br>Port Chart Trading panel from upstream (HORN-1196 / DXBROBL-1227); client trading UI. |
| [CRT-601](https://jira.in.devexperts.com/browse/CRT-601) | FE+S | 24.00 | 34.13 | AF Effect Display in OE for FX_SPOT<br>Est. AF Effect on FX_SPOT order-entry form; UI fields with BE-sourced values (DXINV-028). |
| [CRT-609](https://jira.in.devexperts.com/browse/CRT-609) | FE+S | 24.00 | 38.12 | FX_SPOT chart<br>FX_SPOT charts on midpoint in web and WebBroker client area (CRT-1737). |
| [CRT-525](https://jira.in.devexperts.com/browse/CRT-525) | BE+S | 5.00 | 33.62 | Fix automatic DAY orders expiration in non-trading day<br>DAY order auto-expiration rules and allowedJobs (CRT-1211/1248); core trading engine logic. |
| [CRT-593](https://jira.in.devexperts.com/browse/CRT-593) | BE+B | 40.00 | 68.07 | FX_SPOT Metrics<br>FX_SPOT instrument/account/portfolio metrics and margin formulas (CRT-856, CRT-004, CRT-574). |

## AI Epic breakdown

No AI-assisted epics.

