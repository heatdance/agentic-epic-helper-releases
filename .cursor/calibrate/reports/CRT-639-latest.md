# Calibrate report — CRT-639

**Run:** 2026-05-19 · **Epic:** CRT-639 (closed, archived under `context/`)

## BLUF

Gold and production **coverage** and **tests** JSON are **byte-identical** (copied from `epics/CRT-639/context/`). This run validates gates and layout only; **replace gold with operator-curated CRTQA/Jira oracle** before treating calibrate as a real harness feedback loop.

## Preflight

| Gate | Result |
|------|--------|
| `gold_gate` | OK |
| `prod_gate` | OK (root `.md` + `context/*.json`) |
| `coverage_verify` emit | OK |
| `test_prep_verify` tests (+ plan in `temp/`) | *(run at calibrate session)* |
| `close_verify` preflight | Expected fail — epic already archived |

## Cardinality (prod = gold)

| Artifact | Checks | Matrix | Obligations | Bundles | Excluded |
|----------|--------|--------|-------------|---------|----------|
| Coverage | 16 | 8 | 13 | — | — |
| Tests | — | — | — | 3 | 3 (chk-004, chk-012, chk-016) |

## Human oracle (`CRT-639-gold-meta.json`)

Thin meta defines scope (WeightedAvg FX Spot, cross-surface parity, rounding) and **structured_assertions** (snippet keys, checklist substrings, jaccard thresholds). **Not** applied mechanically in v1 calibrate playbook — use when populating real gold.

## Prod-only context (not in gold folder)

- **CLOSE:** `pass`; 3× **info** orphan checks **chk-013–015** (supporting parity, not bundled).
- **ANALYSE:** 5 gaps (2 deferred checks, 3 human_ba); **exploration_suppressed** aligns with excluded checks.
- **DISCOVER:** `complete`; scope_gap on chk-004, chk-012, chk-016.
- **Hygiene:** `epics/CRT-639/temp/` still present (scratch from prep); should be deleted per pipeline norms.

## Decision map (prod vs gold)

| Dimension | Delta |
|-----------|--------|
| traceability | None (identical JSON) |
| deferrals | None |
| expansion/cardinality | None |
| verification_class | None |
| topic_coverage | None |
| verifier_failures | N/A — identical; emit OK on prod coverage |
| human_oracle_gaps | **Gold = prod copy**; meta oracle unused |
