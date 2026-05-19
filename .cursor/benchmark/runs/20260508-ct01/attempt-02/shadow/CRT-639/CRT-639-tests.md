# CRT-639 regression test drafts (TEST-PREP)

**Epic:** CRT-639 — Cash Settlement based on Average Price

**Shadow:** benchmark_suite=`20260508-ct01` benchmark_attempt=`2`

## Mapping

| bundle_id | proposed_title | covers_check_ids | covers_sections |
|-----------|----------------|------------------|----------------|
| tb-001 | FX Spot WeightedAvg — configuration, ladders, Open P/L, % P/L gross, realized (dxCore-backed) | chk-001,chk-002,chk-003,chk-004,chk-005,chk-006,chk-007,chk-009 | ## Primary focus; ## Prerequisites — configuration & truth source; ## [CRT-1740] Average position fill price — Weight... |
| tb-002 | Cross-surface parity — dxTrade5, WebBroker, Adaptive (FX_SPOT WeightedAvg metrics) | chk-010,chk-011,chk-012 | ## Cross-surface parity — dxTrade5, WebBroker, Adaptive |
| tb-003 | FIFO sanity smoke — non-FX_SPOT instruments (regression guard) | chk-013 | ### Contrast / regression (non-epic path — minimal) |

## Excluded checklist items

- **chk-008** (ambiguity_flag): coverage.checks[chk-008].scenario_line Smart Checklist "! reason:" deferral for rounding-rule keys / XT-7911; default skip per test-prep.md.

## Existing CRTQA tests considered

- **CRTQA-10177** (Test): FX Spot - Calculate Average Price and Realized PL for the full ladder — adapt_steps (fetched_from_issue)
- **CRTQA-10183** (Test): FX Spot - Verify rounding for Average Price and Realized PL — reference_only (fetched_from_issue)
- **CRTQA-10184** (Test): FX Spot - Changing account group doesn't affect existing positions' Average Price — adapt_steps (fetched_from_issue)
- **CRTQA-10152** (Test): FX_SPOT - Check Open PL metric — adapt_steps (fetched_from_issue)
- **CRTQA-10176** (Pre-Condition): CRT-639: Account & System Configuration — none (not_fetched)

## Bundle tb-001 — FX Spot WeightedAvg — configuration, ladders, Open P/L, % P/L gross, realized (dxCore-backed)

**Automation:** feasibility=`blocked` blocked_reason=requires_console notes=CRTQA-10177 patterns require dxCore console; human execution / CLOSE documents blocked feasibility.

### Preconditions
1. CRTQA-10176 (Account & System Configuration) satisfied for the target environment, or an approved equivalent lab profile [TBD] (see Peculiarities 1–2).
2. dxCore console reachable; only command families illustrated in CRTQA-10177 / CRTQA-10183 / CRTQA-10184 may be reused (no ad-hoc invented console verbs).
3. Functional data associates FOREX FX_SPOT with WeightedAvg and leaves listed non-target types on FIFO defaults per CRT-1741; account/group mapping evidence [TBD] (chk-002).

### Actions
1. Confirm FX_SPOT → WeightedAvg binding and capture the effective account/instrument group mapping (chk-002).
2. Exercise the CRT-1740 micro-ladder (flat → layered buys/sells including zeroing) using CRTQA-10177 console patterns (buy / execution trade / show position_metrics_from_publisher) — prices/qty may mirror coverage checklist or CRTQA-10177 samples (chk-004, chk-009).
3. Extend the session through the fuller CRT-1738-style ladder with partial closes and Sell-first variant where required; assert Realized PL progression matches the issue’s worked math only where numerics are supplied in Jira (chk-007; supplement with [REQUIRES: BA numeric oracle] while XT-7911 open).
4. Recompute Open P/L per CRT-1743 from recorded mark vs weighted-average fill; compare publisher/console outputs (chk-005).
5. Validate % P/L Gross per CRT-1742 (two-decimal presentation) against the same staged position (chk-006).
6. Execute the CRTQA-10184 account-group transfer steps verbatim, then re-read position metrics to ensure prior Weighted Average for the open history is unchanged (chk-003).

### Results
1. Configuration evidence shows FX_SPOT on WeightedAvg with FIFO defaults elsewhere (chk-002 / CRT-1741).
2. Weighted-average fill updates follow opening-trade-only contribution rules through the micro-ladder (chk-004 / CRT-1740).
3. Extended ladder + partial-close legs keep Realized PL consistent with CRT-1738 narratives captured in CRTQA-10177 (chk-007, chk-009).
4. Open P/L matches CRT-1743 arithmetic for the truth-source mark used in the session (chk-005).
5. % P/L Gross matches CRT-1742 formula and rounds to two decimals (chk-006).
6. Account group change per CRTQA-10184 does not restate historical averages for already-open FX_SPOT exposure (chk-003).
7. Primary focus statement (chk-001) is satisfied by the end-to-end WA behavior demonstrated above — cross-check wording against CRT-639-coverage Primary focus block.

### Peculiarities
1. CRTQA-10177 — copy buy/execution/show position_metrics_from_publisher patterns from the Jira Test description; do not invent alternate console syntax.
2. CRTQA-10183 — reference explicit rounding ladders there when validating sub-cent behavior; skip rows not in scope for this bundle unless BA expands the session.
3. CRTQA-10184 — follow the group-add/remove narrative there for chk-003; instrument group names (OPPORTUNITY vs ENERGY etc.) remain as published in that issue.
4. CRT-639 Jira comments note dependency on XT-7911 for locking some CRT-1738 numeric ladders — document tolerances with BA when exact cents are still pending.

## Bundle tb-002 — Cross-surface parity — dxTrade5, WebBroker, Adaptive (FX_SPOT WeightedAvg metrics)

**Automation:** feasibility=`unknown` blocked_reason=None notes=Mixture of UI parity and CRTQA-10152 ssh/console prerequisites.

### Preconditions
1. Same FX_SPOT WeightedAvg-capable account/instrument state as bundle tb-001 truth source, or a fresh ladder session whose API/export snapshot is agreed as reference [TBD].
2. dxTrade5 session for [TBD operator account] (chk-010).
3. CRTQA-10152 preconditions (dxTrade5 login, ssh, dx run console, use <AccountPortfolio:AccountCode>) satisfied verbatim where that issue prescribes them — no extra ssh commands (chk-010, chk-011, chk-012).
4. Adaptive and WebBroker credentials or deep links per environment playbook [TBD] (chk-011, chk-012).

### Actions
1. Replicate CRTQA-10152 setup: open FX_SPOT exposure, compute Open P/L via position_qty × (mark − average fill) × multiplier using values from the issue, compare dxTrade5 Positions widget vs Adaptive vs console output (chk-010, chk-012).
2. Repeat the comparison after instrument/account grouping switch exactly as CRTQA-10152 instructs; capture any drift (chk-010, chk-012).
3. Validate average fill, % P/L gross, and realized / cash-equivalent columns on dxTrade5 vs the same reference snapshot when those fields are visible; mark ! reason if a column is absent (chk-010).
4. Navigate WebBroker positions UI (impl-003 BRO/xt wiring) and compare the same metrics; use ! reason when a column cannot be located (chk-011).
5. Confirm Adaptive shows the same metrics or document structured ! reasons per missing column (chk-012).

### Results
1. dxTrade5 values match the referenced formula / snapshot within agreed tolerance (chk-010).
2. Post-switch values remain explainable per CRTQA-10152 expectations (chk-010, chk-012).
3. WebBroker parity recorded or gaps flagged with ! (chk-011).
4. Adaptive parity recorded or gaps flagged with ! (chk-012).

### Peculiarities
1. CRTQA-10152 operational text is authoritative for ssh / dx run console / grouping switch — transcribe from Jira, not from memory.
2. Use [TBD] for account/portfolio codes, instruments, and rounding policy where the issue leaves them open.
3. impl-003 is a code-layout hint only — actual WebBroker navigation paths require the environment playbook.

## Bundle tb-003 — FIFO sanity smoke — non-FX_SPOT instruments (regression guard)

**Automation:** feasibility=`unknown` blocked_reason=None notes=UI smoke unless playbook adds FIFO diagnostics.

### Preconditions
1. Availability of at least one non-FX_SPOT instrument class still on FIFO configuration (e.g., CFD_FOREX or STOCK) per CRT-1741 matrix — exact symbol [REQUIRES: environment playbook].
2. Trader credentials with rights to place canned orders for that instrument [TBD].

### Actions
1. Open a minimal position on the FIFO-configured instrument using UI flows from the environment playbook (no invented console steps) (chk-013).
2. Perform a short open → reduce/close sequence that would surface FIFO consumption if exposed in UI diagnostics; if UI lacks explicit FIFO cues, capture position metrics only and mark [REQUIRES: diagnostics path] (chk-013).
3. Repeat a single comparable action on FX_SPOT WeightedAvg instrument in the same session only to ensure no cross-instrument error — keep scope smoke-level (chk-013).

### Results
1. FIFO-configured instrument completes the smoke path without errors attributable to CRT-639 regressions (chk-013).
2. Documented evidence notes any UI limitations for observing FIFO ordering explicitly (chk-013).

### Peculiarities
1. This bundle intentionally avoids the exhaustive FIFO matrix called out as out-of-epic in coverage; expand only when BA directs.

## Reverse validation

- **coverage_gaps:** none
- **draft_red_flags / notes:** see `CRT-639-tests.json`
