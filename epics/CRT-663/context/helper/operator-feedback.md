# Operator feedback — CRT-663 helper

## 2026-06-08T10:00:00Z

**Coverage reinforcement — E2E atomicity and FX Spot order types**

- FX Spot supports Limit, Market, Stop order types. Market currently blocked by defect; Limit/Stop need manual price adjustment by a significant fraction — UI scenarios remain driving for tests.
- **Atomicity:** Do not bundle order+transfer+position in one check (e.g. "FX Spot Full Chain"). Split per order-type flow into atomic checks: (a) Order visibility, (b) Trade/transfer visibility, (c) Position visibility — so failures localize (e.g. Market flow: order OK, trade fails).
- Each order type (Market, Limit, Stop) must be a **separate scenario group** with atomic sub-checks.
- Explore automatic order-chain triggers beyond liquidation: margin liquidation spawns closing market orders; also consider rollover (FX Spot Rollover Process) as transfer-only chain — scope TBD for visibility epic.
- **Manual fill (chk-016):** Verify ET provider path — ET FIX integration is auto ExecutionReport fill/reject only for FX Spot; manual trade is dxCore/WebBroker dealer action (Order Statuses transitions 17/23), not ET broker intervention. Reframe or defer chk-016 if mislabeled.
- **Adaptive user switch:** cookie `application-dxlg-token` = `username:password` (e.g. antonfx:test) — discover/precon only; not persisted here.

## 2026-06-08T11:45:00Z

Resume cred tokens received on chat line (not stored). Discover Phase 0c: dxTrade5 + WebBroker + Adaptive authenticated; parity account **antonfx**, instrument **EURUSD.spot** visible in all three shells.
