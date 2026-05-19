---
description: Prod vs operator gold — harness calibration questionnaire and analysis (no auto playbook edits)
---

# /crtqa-calibrate

Compare **`epics/<KEY>/`** (and **`context/`** when archived) to operator gold in **`.cursor/calibrate/<KEY>-gold/`**. Ends with **generalized harness suggestions** only when mechanical compare finds an actionable delta; otherwise **hard stop** with **no harness suggestions**.

**No CLI arguments** on the slash command.

## 1. Questionnaire (mandatory)

Use **Cursor Ask** (or equivalent) to collect:

- **Epic key** — options from:
  - `epics/*/` directory names
  - `.cursor/calibrate/*-gold/` folder names (strip `-gold` suffix)
  - recent epic mention in [qa-handoff.md](../../qa-handoff.md)
- Free-text fallback if none of the options fit.

## 2. Gold preflight

```bash
python automation/tools/calibrate_verify.py --mode gold_gate --epic <KEY>
```

Checks required gold JSON **and** `README.md` with **`gold_as_of: YYYY-MM-DD`**.

If exit **non-zero**:

- **STOP** (no analysis).
- Reply with BLUF + how-to: [`.cursor/calibrate/README.md`](../calibrate/README.md), [automation/docs/calibrate.md](../../automation/docs/calibrate.md).

## 3. Gold distinct (hard stop)

```bash
python automation/tools/calibrate_verify.py --mode gold_distinct --epic <KEY>
```

If exit **non-zero** (`GOLD_NOT_DISTINCT`):

- **STOP** — do **not** run compare or playbook.
- BLUF: gold must be **operator-curated**, not a copy of `epics/<KEY>/context/`. Re-ingest from CRTQA/Jira or edit gold JSON after review.

## 4. Optional ingest

If the operator pastes **links** (Jira, Confluence) or **paths** to files in chat:

- Normalize into gold folder filenames (same schemas as production templates).
- Re-run **`gold_distinct`** after ingest.
- **MUST NOT** persist secrets in repo files.

## 5. Production preflight

```bash
python automation/tools/calibrate_verify.py --mode prod_gate --epic <KEY>
```

On fail: **STOP** — production artefacts missing (`PROD_BROKEN`).

## 6. Compare (mechanical)

```bash
python automation/tools/calibrate_verify.py --mode compare --epic <KEY>
```

Parse stdout JSON. **`outcome=`** line is authoritative.

| `outcome` | Agent action |
|-----------|----------------|
| **`GOLD_NOT_DISTINCT`** | Should not occur if step 3 passed; **STOP** if it does |
| **`NO_ACTIONABLE_DELTA`** | BLUF: **no harness changes recommended**; optional one-paragraph report; **no prioritized suggestions**; **STOP** (do not run playbook 6.1–6.6 for lessons) |
| **`DELTA_REVIEW`** | Continue to step 7 |
| Parse/IO failure | **STOP** — fix paths/JSON |

Compare report path (default): `.cursor/calibrate/reports/<KEY>-compare.json`

## 7. Playbook (only when `DELTA_REVIEW`)

Follow [`.cursor/pipelines/calibrate.md`](../pipelines/calibrate.md) with [`.cursor/prompts/calibrate.md`](../prompts/calibrate.md).

- Load **`compare` JSON** first.
- Use **`jq`** per [automation/docs/jq.md](../../automation/docs/jq.md).
- Run read-only verifiers where applicable; fold into maps — **epic hygiene** (temp/, CLOSE info) → **`epic_debt[]`**, not harness lessons.
- Step **6.6**: max **3** lessons; each **must** cite `diff_evidence` (`signal_id`, path, check/bundle id).

## 8. Stop

After step **6.6** or after **`NO_ACTIONABLE_DELTA` / `GOLD_NOT_DISTINCT`**: **end**. Harness edits are a **separate** explicit request.

## Related

| Item | Path |
|------|------|
| Contract | [docs/calibrate-contract.json](../../docs/calibrate-contract.json) |
| Gold layout | [.cursor/calibrate/README.md](../calibrate/README.md) |
| Doctrine | [docs/harness-principles.md](../../docs/harness-principles.md) §7 |
