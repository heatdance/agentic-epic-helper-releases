## Gaps

- `gap-001` [high] **anti_pattern** — chk-014 / obl-010 — Bundled order+TRADE+position in chk-014/chk-015 single lines; split into atomic order / trade / position checks per order-type flow. — action: **rerun_coverage**
- `gap-002` [high] **anti_pattern** — obl-010 — Stop order E2E missing (only Market chk-014, Limit chk-015); CT supports Limit/Market/Stop per Pre-Trade Validations + ET FIX. — action: **rerun_coverage**
- `gap-003` [high] **human_ba** — chk-016 / obl-011 — "Dealer manual fill" misaligned with ET path: ET FX Spot is FIX auto fill/reject only; manual trade is dxCore dealer action (Order Statuses t17/t23), not ET intervention. Reframe chk-016. — action: **rerun_coverage** (confirmed_gap)
- `gap-004` [medium] **human_ba** — chk-014 — Market order path env-blocked by known defect; keep UI-driving atomic scenarios. — action: **ignore_for_discover**
- `gap-005` [medium] **human_ba** — chk-017 / obl-012 — Margin liquidation auto-spawns FX_SPOT market closing orders (valid chk-017); option/futures liquidation types out of FX Spot scope. — action: **ignore_for_discover** (confirmed_gap)
- `gap-006` [medium] **human_ba** — obl-003 — FX Spot rollover creates transfers without client orders; optional transfer-visibility scenario, not in pass-1 E2E. — action: **human_ba**

## Actions

- rerun_coverage: **yes** (via COVERAGE-REINFORCE after discover)
- rerun_epic_prep: **no**
- focus_hint: **Atomic E2E per order type (Market/Limit/Stop): separate order, trade, position checks; reframe manual trade vs ET; liquidation marker retained; market defect noted on Market path.**
