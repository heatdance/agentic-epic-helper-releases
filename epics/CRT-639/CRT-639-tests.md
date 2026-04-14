# CRT-639 — Regression test drafts (TEST-PREP)

**Epic:** [CRT-639](https://jira.in.devexperts.com/browse/CRT-639) — Cash Settlement based on Average Price (FX Spot WeightedAvg).

**Focus (from coverage):** Weighted-average costing for average fill, open P/L, % P/L gross, and realized P/L in cash settlement; CRT-1741 configuration mapping; ladders CRT-1740 / CRT-1743 / CRT-1742 / CRT-1738; cross-surface parity (dxTrade5, WebBroker, Adaptive) vs API/account-statement truth source.

**Structured artifact:** `CRT-639-tests.json` (schema_version 2).

---

## Mapping table

| bundle_id | proposed_title | covers_check_ids | covers_sections (short) |
|-----------|----------------|------------------|-------------------------|
| tb-001 | FX Spot WeightedAvg — dxTrade5 ladder, CRT-1741 config read, API/statement parity | chk-001, chk-002, chk-003, chk-004, chk-005, chk-006, chk-008 | Primary focus; Configuration; WeightedAvg ladders; Cross-surface (dxTrade5/API) |
| tb-002 | WebBroker — FX Spot WeightedAvg metric parity vs dxTrade5 | chk-009 | Cross-surface (WebBroker) |
| tb-003 | Adaptive — FX Spot WeightedAvg metrics exposure and parity | chk-010 | Cross-surface (Adaptive) |

---

## Excluded checks

| check_id | reason | note |
|----------|--------|------|
| chk-007 | ambiguity_flag (!) | Rounding rules for average price vs realized P/L — confirm with BA / XT-7911 (CRT-1921, CRT-1922, DXINV-326) before hard numeric sign-off. |

---

## Existing tests considered (Jira)

- **CRTQA-10132** — Test Execution (workflow: create tests for CRT-639). **Reuse:** none (no executable steps).
- **CRTQA-9968** — Test Execution (CRT-593 workflow template). **Reuse:** none.
- **CRTQA-2545 / CRTQA-2547** — Test (Non-Equity average fill; dxCore + FIFO-weighted expected text). **Reuse:** reference_only — methodology and surface differ from CRT-639 WeightedAvg FX Spot UI/API path; do not copy console commands.
- **CRTQA-276** — Adaptive order-level Avg Price. **Reuse:** reference_only for tb-003 label/format awareness; position-metric parity is the scope of chk-010.

---

## tb-001 — Preconditions

1. CRT-1741 associated-data mapping for costing method (FIFO vs WeightedAvg) is visible or documented for this environment; FOREX / FX_SPOT subtype is WeightedAvg in the reference configuration table, or the default FIFO behavior is observable when the type is not mapped — follow CRT-1741 guidance and do not perform unsafe reconfiguration of existing instrument types (see Peculiarities 1).
2. A test account and FX Spot instrument are available under WeightedAvg costing for cash settlement (this epic is weighted-average FX Spot, not FIFO console methodology from legacy CRTQA-2545 / CRTQA-2547) (see Peculiarities 2).
3. Position is flat (or baseline is explicitly recorded) at the start of the CRT-1738 ladder so opening legs and zero-crossing semantics are unambiguous.
4. dxTrade5 access shows position metrics: average fill, open P/L, % P/L gross, and realized P/L where the client exposes them.
5. A truth source for the same account, instrument, and session is available for parity checks: [REQUIRES: specific API doc or account-statement export runbook naming endpoints, fields, and retrieval steps] (see Peculiarities 3).
6. Mark price (or equivalent valuation input) used for Open P/L is identified per environment documentation — not inferred from UI labels alone; numeric mark and rounding rules remain [TBD] until BA clarifies XT-7911 / rounding (see Peculiarities 4).

### tb-001 — Actions

1. Configuration mapping (chk-002 / CRT-1741): Record how FIFO vs WeightedAvg is determined for the test instrument (table, key, or admin path per project docs). Confirm FX_SPOT maps to WeightedAvg in reference config, or document observed default FIFO when unmapped.
2. Ladder — open long (chk-003, chk-006 / CRT-1738, CRT-1740): From flat, execute BUY +10 @ 99, then BUY +10 @ 98 (use platform order entry equivalent; sizes and prices are scenario labels — adjust only if environment constraints require). After each leg, note average fill in dxTrade5; expected relationship follows weighted average of opening quantity since last zero crossing — exact ladder numbers [TBD] pending XT-7911 / rounding.
3. Partial close on long (chk-003 / CRT-1740): Execute SELL -10 @ 99.50 (or permitted platform equivalent). Verify per CRT-1740 that partial closes do not change average fill from opening-side-only activity; capture displayed avg fill and quantities.
4. Path A — flat (chk-006): Close remaining long to flat at a recorded price (e.g. SELL -10 @ 99.50 or environment equivalent). Capture realized P/L and flat position; cash-settlement weighted-average behavior — numeric expectations [TBD]; parity vs API/statement [REQUIRES: truth source].
5. Path B — short rebuild (chk-006): If Path A was used, re-flatten and repeat ladder from flat, or on a separate controlled session: from the state after the second BUY leg, execute SELL -10 @ 99.50 so net position is short 10; verify average fill for the short reflects opening-side activity since last zero crossing per CRT-1738 / CRT-1740; values [TBD].
6. Cross-through-zero (chk-006): Execute trades that take the position through zero and reopen on the opposite side (e.g. continue closes until flat then open opposite, per approved scenario). Verify average fill resets from opening activity after the crossing per CRT-1738 — use recorded fills only; no invented dxCore steps.
7. Open P/L (chk-004 / CRT-1743): For a non-flat snapshot, compute Open P/L = position_qty × (mark − average fill) × multiplier using documented multiplier and [TBD] mark from [REQUIRES: environment valuation runbook]. Compare to dxTrade5 open P/L.
8. % P/L gross (chk-005 / CRT-1742): Using the same snapshot, compute % P/L gross = (Open P/L ÷ ABS(SUM(avg × qty × multiplier))) × 100 with 2 decimal rounding per requirement; compare to dxTrade5 — tie-break vs BA on XT-7911 if UI/API differ.
9. API / statement parity (chk-008): For each ladder checkpoint (after material legs and at flat/short/cross states), pull the same metrics from the truth source in precondition 5 and compare to dxTrade5: average fill, open P/L, % P/L gross, realized P/L where exposed. Log match/mismatch with timestamps and instrument/account identifiers.

### tb-001 — Results

1. CRT-1741 configuration intent is evidenced: WeightedAvg for FX_SPOT in reference mapping, or default FIFO when unmapped, without violating skip/reconfig rules from the requirement text.
2. After BUY +10 @ 99 then BUY +10 @ 98, dxTrade5 average fill behavior matches weighted-average opening ladder intent (CRT-1740 / CRT-1738); numeric equality vs spec table [TBD].
3. After partial SELL -10 @ 99.50 from the long 20 position, average fill in dxTrade5 is unchanged vs pre-partial-close expectation per CRT-1740 opening-side rule, within [TBD] rounding.
4. Flat path: position is flat; realized P/L and cash settlement figures align with weighted-average methodology — exact numbers [TBD]; parity vs API/statement [REQUIRES: truth source].
5. Short-rebuild path: net short 10; average fill and open metrics match CRT-1738 ladder intent; parity vs API/statement [REQUIRES: truth source].
6. Cross-through-zero path: post-crossing averages and P/L reflect opening activity since the crossing per CRT-1738; parity vs API/statement [REQUIRES: truth source].
7. Open P/L matches CRT-1743 formula when mark and multiplier are taken from approved docs; dxTrade5 matches formula and truth source within [TBD] tolerance.
8. % P/L gross matches CRT-1742 (2 d.p. where specified); dxTrade5 matches formula and truth source within [TBD] tolerance.
9. chk-008 satisfied: dxTrade5 avg fill, open P/L, % P/L gross, and realized P/L (where shown) match API or account-statement truth for the same WeightedAvg FX Spot position, account, instrument, and session — or defects filed with evidence.

### tb-001 — Peculiarities

1. CRT-1741: Prefer read-only verification of mapping; do not paste or execute legacy FIFO dxCore/console steps from CRTQA-2545/2547 — this epic is FX Spot weighted-average cash settlement.
2. Instrument must be FX Spot under WeightedAvg; if the environment labels differ, map to FOREX / FX_SPOT subtype per CRT-1741 reference table language.
3. Truth source is mandatory for chk-008; without [REQUIRES: API or statement runbook], parity cannot be closed — block or defer with explicit gap.
4. Mark source: Use [TBD] or [REQUIRES: environment runbook] for mark and for API endpoints — do not invent sample marks or REST paths.
5. Cross-through-zero scenarios are sensitive to session boundaries and corporate actions; scope to the CRT-1738 ladder unless BA extends.
6. Any mismatch between dxTrade5, formula, and API/statement must capture screenshots/exports and reference XT-7911 for rounding disposition.

---

## tb-002 — Preconditions

1. Bundle tb-001 (dxTrade5 baseline) has been executed or is advanced enough that a written log exists for the same test account, WeightedAvg FX Spot instrument, and ladder session: at minimum average fill, open P/L, % P/L gross, and realized P/L (where dxTrade5 exposes it) per checkpoint you will revisit in WebBroker — identifiers and timestamps recorded in the tb-001 session notes (see Peculiarities 1).
2. WebBroker is reachable for that same test account in this environment: base URL and login path are [TBD] or [REQUIRES: QA WebBroker URL + auth runbook]; credentials match the tb-001 session (see Peculiarities 2).
3. No intentional change to account mapping, instrument subtype (FX Spot / FOREX WeightedAvg), or open position between the tb-001 snapshot and the WebBroker comparison for a given checkpoint; if a delay is unavoidable, record time and note mark-movement risk (see Peculiarities 6).
4. You can locate the open FX Spot position and its position-level metrics in WebBroker using product navigation documented under [REQUIRES: WebBroker IA / help] — not guessed deep links (see Peculiarities 4).

### tb-002 — Actions

1. chk-009 / Cross-surface consistency: Open WebBroker using the approved entry URL from precondition 2; log in with the same test account as tb-001.
2. Navigate to the portfolio or positions area and open the same FX Spot position row as in tb-001 (match account, symbol/instrument id, and side/qty from the tb-001 log) (see Peculiarities 3).
3. For each logical checkpoint that tb-001 recorded (e.g. after material ladder legs, after partial close, non-flat snapshot for P/L formulas, flat, short-rebuild, cross-through-zero as applicable): pause trading, refresh or reopen the position detail if the product requires it, then transcribe WebBroker’s displayed average fill (or equivalent label), open P/L, % P/L gross, and realized P/L where the WebBroker UI shows it.
4. Beside each WebBroker reading, copy the corresponding dxTrade5 values from the tb-001 session log for the same checkpoint; if labels differ, map columns using the glossary or field list in [REQUIRES: cross-client metric mapping] or annotate the mapping in the evidence (see Peculiarities 4).
5. Where tb-001 used formula checks (open P/L, % P/L gross), treat dxTrade5 as the session reference for WebBroker parity — do not introduce new computed marks or multipliers beyond what tb-001 already documented; unresolved mark source or tolerance remains [TBD] / XT-7911 per tb-001 (see Peculiarities 5).
6. Capture evidence (screenshots or allowed exports) for WebBroker and reference the tb-001 evidence pointers so chk-009 can be reviewed without invented SQL or dxCore steps (see Peculiarities 5).

### tb-002 — Results

1. At every compared checkpoint, WebBroker average fill matches the tb-001 dxTrade5 average fill within the same rounding/tolerance stance as tb-001 ([TBD] / XT-7911), or a defect is filed with paired evidence.
2. Open P/L and % P/L gross on WebBroker match tb-001 dxTrade5 for the same non-flat snapshots, within the same tolerance; mismatches reference CRT-1743 / CRT-1742 and XT-7911 as in tb-001.
3. Realized P/L: where WebBroker surfaces it for the position or account slice, it matches tb-001 dxTrade5 at flat or realized checkpoints; if WebBroker does not show the field, record N/A with UI/product evidence rather than skipping silently (see Peculiarities 4).
4. chk-009 is satisfied: WebBroker shows the same numeric parity as dxTrade5 for the surfaced metrics on the test account for this WeightedAvg FX Spot session — or gaps are explicitly blocked/deferred with [REQUIRES: …] / [TBD] and defect keys.

### tb-002 — Peculiarities

1. This bundle is a consumer of tb-001 data; without a checkpointed dxTrade5 log (account, instrument, times, values), chk-009 cannot be closed — do not fabricate baseline numbers.
2. Environment-specific WebBroker URL, MFA, and session stability are out of scope to invent; use [TBD] / [REQUIRES: environment QA runbook].
3. Same test account and instrument as tb-001 is mandatory; mixing sessions or instruments invalidates the cross-surface comparison.
4. UI label differences between dxTrade5 and WebBroker are expected; document the mapping in evidence instead of assuming column names match verbatim.
5. No invented SQL, dxCore, or undisclosed REST paths — parity is dxTrade5 (tb-001) vs WebBroker UI readings unless [REQUIRES: approved WebBroker/API truth source] is added as a formal extension.
6. Compare at the same logical ladder checkpoint; wide time gaps may change mark-driven open P/L — align with tb-001 timing or document why readings may diverge.

---

## tb-003 — Preconditions

1. The same WeightedAvg FX Spot test account, instrument, and valuation session used for dxTrade5 and WebBroker parity (chk-008 / chk-009) is available for observation on Adaptive — coordinate timing with those bundles via [REQUIRES: shared test runbook or session id] (see Peculiarities 1).
2. Adaptive mobile shell build under test is installed and the test user can authenticate and open Positions (or the bank’s equivalent position detail) for that account (see Peculiarities 2).
3. Reference numeric values for average fill, open P/L, % P/L gross, and realized P/L are recorded from dxTrade5 and/or WebBroker for each checkpoint you will compare — from the same coordinated run as precondition 1 or concurrent observation; do not fabricate reference figures (see Peculiarities 3).
4. Mark price / valuation inputs and rounding disposition follow environment documentation and any open BA clarification (e.g. XT-7911); treat exact tolerances as [TBD] until signed — same constraint as desktop parity bundles (see Peculiarities 4).
5. Where available, a short list of which of the four metrics Adaptive is designed to expose for FX Spot positions is agreed — [REQUIRES: shell spec, Figma, or BA pointer]; if absent, exposure is discovered during execution and still recorded per chk-010 (see Peculiarities 5).

### tb-003 — Actions

1. On Adaptive, navigate to the Positions (or equivalent) experience for the test account and open the WeightedAvg FX Spot position aligned with the coordinated scenario (identifiers per precondition 1) (see Peculiarities 1).
2. For each of average fill, open P/L, % P/L gross, and realized P/L that the mobile shell displays for that position: capture the on-screen value at the same logical checkpoint as the desktop references (or closest simultaneous observation) and compare numerically to dxTrade5/WebBroker; log match/mismatch with timestamp and screen identifiers — tolerance [TBD] (see Peculiarities 3).
3. For each of the four metrics the mobile shell does not display: do not omit the metric — record N/A (not exposed on Adaptive) and collect product evidence per checklist: UI capture showing the field is absent or not applicable on this screen, plus a dated pointer to an official artifact (help, Confluence shell page, requirement AC, or release note) that supports non-exposure (see Peculiarities 6).
4. If only a subset of the four metrics is shown (e.g. average fill and open P/L only): perform parity for each shown metric against desktop references; for each missing metric, apply action 3 (N/A + evidence), not silent skip (see Peculiarities 6).
5. At a second material position state when the coordinated plan provides one (e.g. after an additional open leg or a close): repeat actions 2–4 so parity/N/A is not validated on a single snapshot only — if only one state is scheduled, mark scope [TBD] with reason in the evidence table (see Peculiarities 1).
6. Produce a chk-010 evidence table: rows = the four metrics; columns = Adaptive value or N/A, dxTrade5/WebBroker reference, parity outcome, and links/screenshots for every N/A — no empty cells without explanation (see Peculiarities 6).

### tb-003 — Results

1. The WeightedAvg FX Spot position is visible on Adaptive and identifiable as the coordinated test instrument (account/symbol alignment per precondition 1).
2. Each exposed metric among the four matches dxTrade5/WebBroker within the agreed tolerance once [TBD] rounding/tolerance is set, or a defect is raised with side-by-side evidence and session metadata.
3. Each non-exposed metric is explicitly recorded as N/A with product evidence satisfying chk-010 (no silent omission from the test record).
4. In partial-exposure cases, shown metrics meet result 2; absent metrics meet result 3.
5. If a second checkpoint was in scope: results 2–4 hold there too; if deferred, the evidence table states [TBD] and why.
6. chk-010 is satisfied: Adaptive shows numeric parity with dxTrade5/WebBroker for every surfaced position metric, and every absent metric has documented N/A with product evidence rather than being skipped silently.

### tb-003 — Peculiarities

1. Session alignment: Parity is only meaningful when Adaptive and desktop views reflect the same logical position state and comparable mark context — note any refresh lag in the evidence table.
2. Navigation / labels: Adaptive field labels may differ from dxTrade5/WebBroker; map by semantics (average fill, open P/L, % P/L gross, realized P/L) per CRT-1740 / CRT-1743 / CRT-1742 / CRT-1738, not by identical column titles.
3. Reference provenance: Desktop reference numbers must come from authorized parity runs or live concurrent observation — do not invent gold values or backend queries ([REQUIRES: truth-source runbook] where API/statement is used upstream).
4. Mark and rounding: Do not invent SQL, dxCore commands, or sample API payloads; use [TBD] / [REQUIRES: BA or environment doc] for mark source and numeric tolerance, consistent with XT-7911 disposition when applicable.
5. Expected exposure: Without a pre-approved shell list, document observed exposure first, then apply parity vs N/A rules — still covers chk-010.
6. Product evidence for N/A (chk-010): Minimum acceptable bundle = (a) screenshot or short recording of the Adaptive position UI showing that the metric is not presented for this instrument/state, and (b) dated citation to a product artifact stating omission is by design or out of mobile scope — [REQUIRES: project evidence template] if the bank defines one.

---

## Reverse validation summary

- **coverage_gaps:** none (included checks are mapped; chk-007 excluded with documented reason).
- **orphan_bundles:** none.
- **draft_red_flags:** none recorded.

---

## Jira test search (audit)

| purpose | result_count | notes |
|---------|--------------|--------|
| epic_link (`"Epic Link" = CRT-639` in CRTQA) | 4 | Workflow / execution containers, not executable Test-type CRT-639 cases |
| epic_key_text (CRTQA Test + text CRT-639) | 0 | No Test issues with epic key in text |
| epic_key_text (CRTQA + text CRT-639) | 4 | Same epic-linked set |
| summary_keyword (CRTQA Test + Average Fill / average price) | 7 | Includes CRTQA-2545, CRTQA-2547, CRTQA-276, etc. |

Full JQL and timestamps: see `CRT-639-tests.json` → `jira_test_search`.
