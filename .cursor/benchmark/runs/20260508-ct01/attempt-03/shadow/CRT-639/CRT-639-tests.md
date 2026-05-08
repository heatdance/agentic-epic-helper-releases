# CRT-639 — Regression test draft bundles (benchmark 20260508-ct01 attempt-03)

| bundle_id | proposed_title | covers_check_ids | covers_sections |
|-----------|----------------|------------------|----------------|
| tb-001 | WeightedAvg FX Spot — configuration, average reset ladders, crossing zero | chk-001,chk-002,chk-003,chk-005,chk-006,chk-012 | ## Primary focus; ## Functional configuration and prerequisites; ## Weighted-average ladder — average fill, realized P/L, crossing zero (CRT-1738 & CRT-1740); ## Dimensions and edge cases (evidence-gated) |
| tb-002 | WeightedAvg FX Spot — Open P/L and % P/L gross formulas | chk-007,chk-008 | ## Open P/L and % P/L gross (WeightedAvg path) |
| tb-003 | WeightedAvg FX Spot — dxTrade5, WebBroker, Adaptive metric parity | chk-009,chk-010,chk-011 | ## Cross-surface parity (Corner Trader) |

## Epic verification focus (from coverage)

Corners verifies weighted-average cash settlement P/L mapping for FOREX FX_SPOT instruments when Functional Configuration selects WeightedAvg (CRT-1741), spanning CRT-1740 average fill ladders that reset net size at zero, CRT-1738 realized versus open interplay, CRT-1743 mark-minus-average open P/L, and CRT-1742 gross percent denominators—all observed consistently on dxTrade5, WebBroker, and Adaptive shells.

## Existing CRTQA issues considered

- **CRTQA-10176** — CRT-639: Account & System Configuration — reuse: adapt_steps — fetched_from_issue
- **CRTQA-10177** — FX Spot - Calculate Average Price and Realized PL for the full ladder — reuse: adapt_steps — fetched_from_issue
- **CRTQA-10182** — FX Spot - Calculate Open PL & % PL Gross for the full ladder — reuse: adapt_steps — fetched_from_issue
- **CRTQA-10183** — FX Spot - Verify rounding for Average Price and Realized PL — reuse: reference_only — fetched_from_issue
- **CRTQA-10184** — FX Spot - Changing account group doesn't affect existing positions' Average Price — reuse: reference_only — fetched_from_issue

## Excluded checklist checks

- `chk-004` — ambiguity_flag: coverage.checks[].ambiguity XT-7911 blocks final CRT-1738 numeric oracle
- `chk-013` — ambiguity_flag: coverage.checks[].ambiguity epic silent; CRTQA-10184 available as reference_only — not auto-waived without include_ambiguous
- `chk-014` — ambiguity_flag: coverage.checks[].ambiguity nested rounding keys unresolved in Yogi export

---

## Bundle tb-001 — WeightedAvg FX Spot — configuration, average reset ladders, crossing zero

### Preconditions
1. Primary scope (chk-001 / CRT-1738, CRT-1740, CRT-1741, CRT-1742, CRT-1743): Corners verifies weighted-average cash settlement P/L mapping for FOREX FX_SPOT instruments when Functional Configuration selects WeightedAvg (CRT-1741), spanning CRT-1740 average fill ladders that reset net size at zero, CRT-1738 realized versus open interplay, CRT-1743 mark-minus-average open P/L, and CRT-1742 gross percent denominators—all observed consistently on dxTrade5, WebBroker, and Adaptive shells. This bundle exercises configuration evidence, ladder structural behavior (zero crossing / partial close / multi-cross), not full cross-shell UI parity.
2. [chk-002 / CRT-1741] Using Functional Configuration Live Platform documentation, a FOREX FX_SPOT test instrument—or equivalent controlled mapping—is assigned to WeightedAvg (not FIFO) for valuation; STOCKS/CFD paths remain FIFO unless explicitly migrating them (explicitly outside this epic’s primary focus). > Yogi CRT-1741: Weighted Average bucket covers FOREX (FX_SPOT subtype); default when unset is FIFO. [TBD: exact console/UI mapping steps for WeightedAvg in this environment — [REQUIRES: Functional Configuration Live Platform procedure aligned with CRT-1741]].
3. [chk-003 / CRT-1741] The configuration row and associated data used on the test account are identified so COVERAGE can reproduce the same instrument classification across dxTrade5, WebBroker, and Adaptive sessions. > impl-001 / impl-002: BRO/xt monorepo (dxcore/, webbroker/) is the default implementation surface for metric plumbing.
4. Baseline account/system setup from CRTQA-10176 is satisfied (console or WebBroker path per environment policy; see Peculiarities 1–2).
5. dxCore console session is available; an FX_SPOT-capable test account is selected using the documented pattern (see Peculiarities 3).

### Actions
1. Capture and store the WeightedAvg functional-configuration evidence from §Preconditions 2–3 (screenshot, copy of configuration row, or export as allowed by policy) keyed to this account/instrument.
1.1. Structural ladder only: do not assert authoritative CRT-1738 ladder numerics line-by-line in this run; record observed engine values for later diff once XT-7911 supplies final oracle (see Peculiarities 4).
2. In dxCore, execute opening/closing sequences adapted from CRTQA-10177 (cited for scaffold traceability) to stress WeightedAvg opening-trade windows, following the publish/verify rhythm: submit order (`buy` / equivalent `sell` first variant), `show order last`, `execution trade orderkey=<external-facing-orders-id> orderstatus=COMPLETED price=<price> qty=<qty> transactiontime=now`, then `show position_metrics_from_publisher` after each completed fill.
2.1. Ladder A — layered opening trades then closes through zero including remainder exposure (pattern class per CRTQA-10177: multi-buy then larger sell crossing net sign); after each step capture net size, average fill, and realized/open effects from publisher metrics.
2.2. Ladder B — partial closes that do not flip net sign; confirm average price continues to obey WeightedAvg opening-trade rules (no silent regression to FIFO opening-match prices for closing events) [chk-006 / CRT-1738].
2.3. Ladder C — go flat (zero net), then open a new leg and verify the WeightedAvg opening-trade window restarted (only opening trades since last crossing 0 contribute) [chk-005 / CRT-1740 + CRT-1738].
2.4. Ladder D — within one session, cross net zero multiple times (flat → rebuild → cross again); after each crossing, confirm a fresh opening-trade window for subsequent opens [chk-012 / CRT-1738].
3. Optionally mirror one ladder with sell-first sequencing per CRTQA-10177 (“Reverse with Sell first”) using the same execution/metrics verification pattern.
4. Summarize observed metrics per step in a run log (tabular or bullet) suitable for COVERAGE replay without embedding scratch working-directory paths or other ephemeral storage references.

### Results
1. Documentation exists tying the test account/instrument to WeightedAvg (not FIFO) for FX_SPOT and is sufficient for teammates to reproduce the same classification on dxTrade5, WebBroker, and Adaptive (chk-002, chk-003).
2. For each ladder step, `show position_metrics_from_publisher` output is captured after `execution trade` completion; structural relationships hold: opening-side adjustments drive average per WeightedAvg rules; closing events do not replace the average with FIFO-style opening-match prices when net sign is unchanged (chk-006).
3. After a true net-zero / flat crossing, the next opening leg establishes a new WeightedAvg window consistent with “all opening trades since last crossing 0” (chk-005).
4. Multiple zero crossings in one session each reset the opening-trade window as expected for Yogi/CRT-1738 WeightedAvg cash settlement behavior (chk-012); any ambiguity is flagged with observed values and [REQUIRES: XT-7911 finalized ladder oracle] before hard pass/fail.
5. No checklist item in this bundle asserts locked absolute numbers from the CRT-1738 published ladder until upstream numeric alignment is available; numeric examples in legacy reuse (CRTQA-10177) are treated as scaffolding shape, not as epic-final oracle (see Peculiarities 4).

### Peculiarities
1. [from CRTQA-10176] Console baseline: `dx run console`; create user+account via `create broker_client broker=<broker_id> user_with_account name=<username> domain=default password=<password> currency=USD$` (broker CH or BS per test tier); `corner_subtype set_allowed account=<clearing_code>:<account_code> allowedsubtypes=FX_SPOT`; locate CAG (or equivalent broker accounts group) and dxFeed-suffix group (e.g. OPPORTUNITY) via `show account_group_hierarchy` / grep; `update account_group_members key=<group_key> add_accounts=<account_id>` for both; route ExternalExecution to `FIX_AUTO` using `show profiles domains=ExternalExecution` and assign ACCOUNT-level FIX_AUTO profile; if ET executor is active, follow issue note to unassign FIX_AUTO vs ET precedence; publish quote e.g. `pub_to_realtime quote EUR/USD.<SUFFIX>:ETFX <bid> <ask> now 0` using the instrument/suffix prepared for the run.
2. [from CRTQA-10176] WebBroker baseline (if used): login per environment WebBroker URL with master_dealer / test; create user with Broker code CH or BS, Client Type POA, CPG membership; create account with Allowed Instruments = FX_SPOT, initial balance, and a CornerTraderFxConfiguration group (e.g. OPPORTUNITY) matching console routing.
3. [from CRTQA-10177] Account selection pattern in console: `use <account_code>` (example in source issue uses `11004` as illustration only — substitute the account prepared in §Preconditions).
4. chk-004 / XT-7911 ambiguity is intentionally excluded from this bundle: do not record conflicting numeric ladder oracle as mandatory expected values without waiver. CRTQA-10177 illustrates ladder shapes and sample arithmetic for publisher checks; this bundle uses that issue for command scaffolding and structural validation only.
5. WeightedAvg functional-configuration specifics beyond FX_SPOT allowance and account grouping are [TBD] unless copied from approved configuration docs; do not improvise new dxCore keywords not present in CRTQA-10176/CRTQA-10177.
6. Cross-surface parity (dxTrade5 / WebBroker / Adaptive column compares) and formula assertions for Open P/L or % gross (CRT-1743 / CRT-1742) are out of this bundle’s core results; defer to dedicated parity bundles while preserving the configuration record here for replay.

## Bundle tb-002 — WeightedAvg FX Spot — Open P/L and % P/L gross formulas

### Preconditions
CRTQA-10176: FX Spot account, instrument groups, ExternalExecution profile selection, and pub_to_realtime quote publication path are configured as in CRTQA-10176.
CRTQA-10177: a non-flat WeightedAvg FX_SPOT position exists with publisher-visible position quantity, average fill price, and mark context suitable for Open PL verification (complete CRTQA-10177 ladder choreography before this bundle, per CRTQA-10182 dependency).
CRTQA-10182 preconditions otherwise satisfied: dxCore console is up and running; account able to trade FX Spot is used (see Peculiarities).
Coverage alignment: execute chk-007 (CRT-1743 Open P/L, mark minus average fill with multiplier) and chk-008 (CRT-1742 % P/L gross WeightedAvg branch, two-decimal rule per Yogi CRT-1742) from CRT-639-coverage.json in the parent shadow epic directory.

### Actions
On dxCore console, select the FX Spot account per Peculiarities (example [from CRTQA-10182]: > use 11004 then antonfx>).
Run show position_metrics_from_publisher; record position_qty, average fill price, and mark price inputs for Open PL [from CRTQA-10182]: Open PL uses position_qty × (mark price − average fill price) × multiplier, where mark price is published bid for long or ask for short [from CRTQA-10176 as referenced in CRTQA-10182].
Obtain multiplier using the CRTQA-10182 pattern: antonfx> grep multiplier:  show instrument EURUSD.spot (repeat for the long/short and PL sign matrix called out in CRTQA-10182 when running the full ladder).
Reconcile Open P/L: compare the recalculation above to publisher output from show position_metrics_from_publisher (chk-007).
When distinct marks are required, publish quotes with antonfx> pub_to_realtime … per CRTQA-10176 (instrument/route naming per environment), then repeat show position_metrics_from_publisher and repeat the Open PL reconciliation (chk-007).
Run grep plGross show portfolio_metrics [from CRTQA-10182] and recalculate % PL Gross as Open PL / ABS(average price × qty × multiplier) × 100, with result rounded mathematically to 2 digit precision (e.g. −3.448275% → −3.45%) [from CRTQA-10182]; reconcile to publisher-derived values (chk-008).

### Results
chk-007 (CRT-1743): Open P/L reported via show position_metrics_from_publisher matches position_qty × (mark_price − average_fill_price) × multiplier using the same mark feed as production configuration; document which mark source (mid, bid, ask, last) the environment applies, consistent with CRTQA-10176/CRTQA-10182 mark-side convention.
chk-008 (CRT-1742): % P/L gross matches (Open PL / ABS(SUM(average_price × qty × multiplier))) × 100 for the WeightedAvg branch and rounds to two decimals per Yogi CRT-1742, consistent with CRTQA-10182 mathematical rounding to 2 digit precision.

### Peculiarities
Console account selection example [from CRTQA-10182]: > use 11004 then antonfx>.
Verification patterns for formulas and publisher reads are taken from CRTQA-10182: show position_metrics_from_publisher; grep multiplier:  show instrument EURUSD.spot; grep plGross show portfolio_metrics; bid/ask mark convention per CRTQA-10176 as referenced by CRTQA-10182.
CRTQA-10183 (rounding ladders) documents floor-to-2dp display behavior for Open PL and Realized PL in instrument currency for its dedicated cases; CRTQA-10182 documents mathematical (not floor) rounding for % PL Gross to 2 decimals. Those rules apply to different metrics—keep Open PL vs % PL Gross reconciliation scoped to the ticket that defines the metric under test so the expectations do not contradict.

## Bundle tb-003 — WeightedAvg FX Spot — dxTrade5, WebBroker, Adaptive metric parity

### Preconditions
Account and instrument use the same CRT-1741 WeightedAvg FX_SPOT functional configuration row recorded for CRT-639; metrics are already validated in sibling bundles via console or API/tests (or you capture dxTrade5, WebBroker, and Adaptive snapshots concurrently with a single coherent quote window).
Authoritative dxCore or API numeric row for the position (average fill, open P/L, percent P/L gross, realized P/L) is available from the prior coverage spine so dxTrade5 parity has a comparand (chk-009; see coverage implementation_hits impl-001, impl-002 only as BRO/xt/dxcore high-level placement, not as fabricated drill-down paths).
One continuous Corner Trader session after that validation, or time-aligned concurrent snapshots across shells, so all surfaces observe the same market snapshot for cross-surface numeric parity.

### Actions
chk-009 [CRT-1738] dxTrade5: On the same account and WeightedAvg FX_SPOT instrument, open the primary positions presentation that exposes Average Price, Open P/L, % P/L gross, and Realized P/L. Navigation: [TBD] / [REQUIRES: screen map]. Capture those four fields and compare each to the dxCore or API truth used earlier; document tolerance if feed rounding differs.
chk-010 [CRT-1743] WebBroker: Repeat the snapshot read from positions grids or client-area widgets that surface the same four metrics. Navigation and widget choice: [TBD] / [REQUIRES: screen map]. Assert each numeric matches the dxTrade5 read within the same rounding tolerance policy as the ladder bundles (impl-003: BRO/xt/webbroker/ houses webbroker-ui/ and webbroker-backend/ per coverage—engineering pointer only).
chk-011 [CRT-1742] Adaptive: On mobile position details, evaluate every column that exposes Average Price, Open P/L, % P/L gross, and Realized P/L. Navigation: [TBD] / [REQUIRES: screen map]. Where a column exists, compare to dxTrade5 or API within tolerance; where a metric has no column, log explicitly `! reason: metric not exposed on Adaptive surface` for that metric (do not fold Adaptive absence into WebBroker-only passes).

### Results
dxTrade5: All four metrics (Average Price, Open P/L, % P/L gross, Realized P/L) match dxCore or API truth within the agreed tolerance (chk-009).
WebBroker: All four metrics match dxTrade5 within rounding tolerance (chk-010).
Adaptive: For each metric column that Adaptive exposes, values match peer surfaces within tolerance; for any metric not shown as its own column, recorded as `! reason: metric not exposed on Adaptive surface` rather than a vague TBD (chk-011 check line).
Evidence package lists timestamp or session id proving single-window or explicitly concurrent capture, plus the configuration row id tied to the instrument classification.

### Peculiarities
Coverage impl-003 (BRO/xt/webbroker/): top-level listing includes webbroker-ui/, webbroker-backend/, and delivery/; use only as the sanctioned implementation pointer for WebBroker metric surfacing—no paths fabricated beneath BRO/xt/webbroker/.
chk-011 detail_lines anti-pattern: do not assume UI labels spell “mark” vs “mid”; bind comparisons to column semantics agreed with PM/BA.
Cross-surface parity is invalid if snapshots are minutes apart on a fast market—prefer concurrent capture or one session with immediate cross-shell reads after sibling validation.
If Adaptive lacks a metric column, document `! reason: metric not exposed on Adaptive surface` in results and here for traceability; never substitute WebBroker-only proof for that metric on Adaptive.


## Reverse validation

* coverage_gaps: **none**
* orphan_bundles: none
