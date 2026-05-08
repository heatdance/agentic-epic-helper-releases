# CRT-639 — Regression test drafts (TEST-PREP)

| bundle | proposed title | covers |
|--------|----------------|-------|
| tb-001 | FX Spot — WeightedAvg prep + CRT-1738 ladder (engine) | chk-001, chk-002, chk-003 |
| tb-002 | FX Spot — Engine vs dxTrade5 metrics reconciliation | chk-004, chk-005 |
| tb-003 | FX Spot — Web Broker & Adaptive parity | chk-006, chk-007 |
| tb-004 | FX Spot — CRT-1738 cash settlement observe | chk-008 |

## excluded checks
- chk-009 — optional multi-account stress deferred (see coverage Smart Checklist).

## tb-001 — FX Spot — WeightedAvg prep + CRT-1738 ladder (engine)

### Preconditions

1. Epic CRT-639 in scope: FX Spot weighted-average migration per CRT-639 coverage.
2. Functional config capability to map FOREX (FX_SPOT subtype) instruments to WEIGHTED_AVERAGE lane (CRT-1741).
3. FX_SPOT test instrument + trader account identifiers available or flagged [TBD].
4. CRT-1738 ladder can be exercised after last net-size zero cross (engine observability reachable).
5. Session can intentionally retain historic mixed-opening lots before comparison (CRT-1740 stress).
6. Golden numerics flagged [TBD] until XT-7911 rounding decisions land on CRT-639 thread.

### Actions

1. Provision environment using CRTQA-10176 playbook segments (console or Web Broker path) preserving FX_SPOT tradeability.
2. Prove PlCalculationMode (or successor global assoc-data) binds FOREX to WEIGHTED_AVERAGE for exercised instrument.
3. Walk CRT-1738 illustrative BUY / SELL sequence after rebuild from flat; halt after each transaction to snapshot engine qty, weighted average fill, realized PL, open PL.
4. Compare snapshots against CRT-639 coverage ladder tolerances ([TBD] until XT-7911).
5. With mixed-opening lots unchanged, inspect average fill derivation vs FIFO-style expectation from coverage notes.

### Results

1. Functional mapping evidence stored (screens/console transcript without secrets).
2. Engine ladder tables complete for chk-002 with gaps explicitly noted when tolerances unreachable.
3. CRT-1740 distinguishing observation documented for chk-003 (pass / fail / deferred).

### Peculiarities

1. Source: CRTQA-10176 — console macros for broker_client creation, FX_SPOT allow list, Opportunity group onboarding, ExternalExecution routing, pub_to_realtime sample.
2. ASCII-only substitutions used when copying commands; replace placeholders before execution.
3. Reference CRT-639-coverage.chk-002 detail lines for CRT-639 epic comment about XT-7911 dependency.

## tb-002 — FX Spot — Engine vs dxTrade5 metrics reconciliation

### Preconditions

1. ladder + quoting session produced in tb-001 remains authoritative for qty, multiplier, weighted average inputs.
2. Authorized engine/export pathway for reconciliation identified ([REQUIRES: BA-approved dump] acceptable).

### Actions

1. Export engine truth for WeightedAvg Open PL and Percent PL Gross for snapshot timestamp T0.
2. Capture dxTrade5 metrics (Average Fill, Open PL, Percent PL Gross) at T0.
3. Compare Open PL to CRT-1743 weighted expression via engine-fed parameters (no handheld rounding).
4. Compare Percent PL Gross to CRT-1742 denominator policy using exported components.
5. Raise structured ambiguity if column missing referencing CRT-639 Smart Checklist instruction.

### Results

1. dxTrade5 metrics match export within tolerance or documented delta cause.
2. Outstanding rounding tracked under XT-7911 / CRT linkage without silent pass.

### Peculiarities

1. Keep evidence attachments outside harness ephemeral directories per QA policy.
2. DO NOT mint golden numerics absent BA sign-off.

## tb-003 — FX Spot — Web Broker & Adaptive parity

### Preconditions

1. Baseline trio from tb-002 capture recorded alongside UTC timestamp.
2. Web Broker + Adaptive clients reachable using same entitlement as dxTrade session.
3. qa_default_both layout enabled on Adaptive builds under test.

### Actions

1. Reload Web Broker position widget; capture trio metrics for identical instrument/account.
2. Reload Adaptive Positions workspace; locate mapped fields for Average Fill, Open PL, Percent PL Gross where shipped.
3. Diff both clients vs dxTrade5 baseline within agreed tolerance spreadsheet or [TBD].
4. Document structured ambiguity per chk-007 if Adaptive omits a named metric.

### Results

1. Web Broker parity recorded pass/fail per metric.
2. Adaptive parity or gap list referencing issue keys only.

### Peculiarities

1. Resync feeds if Adaptive lags dxTrade due to websocket batching.

## tb-004 — FX Spot — CRT-1738 cash settlement observe

### Preconditions

1. [REQUIRES: BA fixture] Controlled cash-settlement window for weighted FX_SPOT instrument booked.
2. Settlement authority (engine/report) agrees post-event reconciliation path.

### Actions

1. Snapshot CRT-1738 quartet (qty, weighted avg fill, open PL, realized PL) immediately before settlement event.
2. Trigger or observe settlement per BA playbook.
3. Snapshot same quartet after settlement; reconcile vs CRT-1738 non-equity cash flow prose.

### Results

1. Settlement PASS only when deltas within rounding policy documented with evidence.
2. If fixture unavailable: mark feasibility blocked referencing CRTQA tracker without fabricating PASS.

### Peculiarities

1. Optional context only: XT-7328 historically tracked settlement divergence work — cite as historical pointer, not procedural proof.
2. Maintain consistent rounding authority with tb-002.
