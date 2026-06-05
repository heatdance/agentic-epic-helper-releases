# Pipeline: coverage-reinforce

**Trigger**: user message starts with `COVERAGE-REINFORCE:` and includes a Jira **Epic key** (e.g. `COVERAGE-REINFORCE: CRT-639`).

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Purpose:** Second coverage pass after **TEST-DISCOVER** — merge **verification affordances**, **obligation ledger** closure hints, and **operator feedback** into the existing Smart Checklist without re-running full greenfield COVERAGE from ref-only inputs.

**Schema:** Same as production COVERAGE — **`schema_version: 2`**, **`obligations_coverage`**. Set **`coverage_pass: 2`** and **`reinforced_at`** (ISO-8601 UTC) on emit.

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** = `epics/<KEY>/`.

**Prerequisites (all required):**

- `{EpicDir}<KEY>-ref.json` (schema v4)
- `{EpicDir}<KEY>-coverage.json` + `.md` (pass 1)
- `{EpicDir}<KEY>-discover.json` (schema v3, `discover_verify.py` OK)
- `{EpicDir}helper/affordances-slice.json` (from `crtqa_helper_affordances.py` after discover)
- `{EpicDir}helper/operator-feedback.md` (may be empty; ingest from `/crtqa-helper resume` comments)

If **discover** or **helper slice** missing: **STOP** — run `TEST-DISCOVER:` and helper affordances export first.

## Allowed inputs (exception to production COVERAGE forbidden list)

| Input | Use |
|-------|-----|
| `-discover.json` | **jq slices only** — `verification_affordances`, `obligation_ledger`, `fixture_needs`, `client_shell_impact` |
| `helper/affordances-slice.json` | Primary machine slice for reinforce |
| `helper/operator-feedback.md` | Human gaps (Order History, UI↔DB, surface parity, instrument tokens) |
| Existing `-coverage.json` / `.md` | **Merge base** — extend checks; do not drop row-complete obligations |

Contract: [`docs/coverage-obligation-contract.json`](../../docs/coverage-obligation-contract.json) `reinforce_allowed_inputs`.

## Forbidden inputs

- **CRTQA** Jira issues, **`.cursor/calibrate/`** gold
- **`-tests.json`**, **`-precon.json`**
- Full discover JSON loaded unfiltered into context (use **`jq`**)

## Preconditions

- **user-mcp-atlassian** when Jira refresh needed for ambiguity only — reinforce is **coverage-grounded**, not a second EPIC-PREP.
- **Harness maps:** read [`docs/dxtrade5-harness/`](../../docs/dxtrade5-harness/) and [`docs/webbroker-harness/`](../../docs/webbroker-harness/) for widget/screen affordances cited in discover.
- **Smart Checklist norms:** same as [`coverage.md`](coverage.md) — **no meta prose** in executable `-` lines; use `>` for variants.

**Ephemeral:** `{EpicDir}temp/` — delete before finish.

---

## Phases

### 1. Load merge base + slices

- **`jq`** project `-coverage.json` obligations + checks; `-discover.json` affordances; `affordances-slice.json`; read `operator-feedback.md`.
- Record `sources.reinforce_inputs[]` in coverage JSON: paths + loaded_at.
- Append `validation_log` step `reinforce-1`.

### 2. Map affordances → checks

For each **primary** obligation still thin per discover `obligation_ledger` or operator feedback:

- Add or deepen **`-`** lines: concrete UI surfaces, DB oracles (Orders/Activities), Order History, cross-shell parity where `client_shell_impact` applies.
- Tie new checks to **`obligation_ids[]`**; preserve existing covered rows.
- Convert operator feedback bullets into **executable** scenarios — not checklist meta (“verify widget works”).

**Anti-patterns to fix on reinforce:**

- Generic widget-only lines without history/DB when discover cites fixtures
- Instrument litter (e.g. EURUSD) when epic/ref says FX Spot class — use `.spot` or ref instrument tokens
- Symmetric peer sections when `epic_verification_focus` is one-way

### 3. Obligation row-complete (unchanged bar)

- Every **`primary_candidate`** in ref must remain **covered**, **deferred_in_check**, or **excluded_with_reason** in `obligations_coverage`.
- Run `coverage_verify.py --mode obligations` with `--ref`.

### 4. Emit

- Bump **`coverage_pass: 2`**, set **`reinforced_at`**.
- Regenerate `-coverage.md` via `coverage_verify.py --mode emit`.
- Delete `{EpicDir}temp/`.
- Self-check: no `/temp/` paths in durable JSON.

### 5. Helper handoff

When invoked from **`/crtqa-helper`**: append `stage-log.jsonl`; next stage **`precon`** on resume.

---

## Verifier

```text
python automation/tools/coverage_verify.py --mode obligations \
  --coverage epics/<KEY>/<KEY>-coverage.json \
  --ref epics/<KEY>/<KEY>-ref.json

python automation/tools/coverage_verify.py --mode emit \
  --coverage epics/<KEY>/<KEY>-coverage.json \
  --md epics/<KEY>/<KEY>-coverage.md
```
