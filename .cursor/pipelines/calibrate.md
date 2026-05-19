# Playbook: calibrate (prod vs operator gold)

**Invocation:** **`/crtqa-calibrate`** only ([`.cursor/commands/crtqa-calibrate.md`](../commands/crtqa-calibrate.md)). **Not** a `CALIBRATE:` router trigger in v1.

**Contract:** [`docs/calibrate-contract.json`](../../docs/calibrate-contract.json) (schema v2). **Gold how-to:** [`.cursor/calibrate/README.md`](../calibrate/README.md).

**MUST NOT:** re-run production pipelines; fetch CRTQA for generation; auto-edit playbooks, verifiers, or contracts after step **6.6**.

---

## Prerequisites (command steps 2–6)

Run in order per command doc:

1. `gold_gate` → `gold_distinct` → `prod_gate` → `compare`
2. Load **`.cursor/calibrate/reports/<KEY>-compare.json`** (or stdout from `compare`).

| `compare.outcome` | Playbook |
|-------------------|----------|
| **`NO_ACTIONABLE_DELTA`** | **Do not run** steps 6.1–6.6 for harness lessons. Optional one-paragraph report: “no harness changes.” |
| **`DELTA_REVIEW`** | Run 6.1–6.6 |
| **`GOLD_NOT_DISTINCT`** | Command stops before this playbook |

Preflight: [`calibrate_verify.py`](../../automation/tools/calibrate_verify.py) — `gold_gate`, `gold_distinct`, `prod_gate`, `compare`.

---

## Paths

| Role | Path |
|------|------|
| Production root | `epics/<KEY>/` |
| Production context (post-CLOSE) | `epics/<KEY>/context/*.json` |
| Compare report | `.cursor/calibrate/reports/<KEY>-compare.json` |
| Gold | `.cursor/calibrate/<KEY>-gold/` |
| Optional narrative report | `.cursor/calibrate/reports/<KEY>-latest.md` |

---

## Step 6.1 — Production decision map

**Skip** if `compare.outcome` is `NO_ACTIONABLE_DELTA` (emit one-line “maps empty — mechanical compare found no delta”).

1. **`jq`** project production (`context/` first for JSON).
2. Build **`prod_decision_map`** from [`decision_map_dimensions`](../../docs/calibrate-contract.json).
3. Seed from **`compare.signals[]`** where `actionable: true`.

---

## Step 6.2 — Gold decision map

Same as 6.1 for gold paths. Align with **compare** signal `detail` fields.

---

## Step 6.3 — Cross-reference

1. Read `context/` discover, analysis, close when present.
2. Map each **actionable** `compare.signals[].id` to decision-map dimensions.
3. **`epic_debt[]`** (report only): `temp/` present, CLOSE info orphans, analysis gaps **without** gold/prod diff — per contract `epic_debt_examples`.

---

## Step 6.4 — Epic report

Write chat and/or **`.cursor/calibrate/reports/<KEY>-latest.md`**:

- BLUF from `compare.outcome` and signal summary.
- **`epic_debt[]`** separate from harness lessons.

---

## Step 6.5 — Generalize lessons

**Only when `compare.actionable_delta_count` > 0.**

1. Each **`lesson_record`** **must** include **`diff_evidence`**: `signal_id`, `path`, optional `check_id` / `bundle_id`.
2. **Reject** lessons without a matching actionable compare signal.
3. **Reject** epic-only items (orphan checks, temp/) — those belong in **`epic_debt[]`** only.
4. Max **3** lessons in 6.6 (`lesson_policy.max_prioritized_lessons`).
5. Optional read-only verifiers; verifier-only failures without gold/prod diff → **`epic_debt`** or footnote, not harness lesson unless gold encodes the bar.

---

## Step 6.6 — Operator gate

| Condition | Output |
|-----------|--------|
| `actionable_delta_count == 0` | **Forbidden:** prioritized harness suggestions. Allowed: confirm success, questions, pointer to update gold when prod changes. |
| `actionable_delta_count > 0` | Up to **3** prioritized suggestions; `confidence: low` → appendix only |

**STOP** — no auto-apply of playbook/verifier edits.

---

## Related

| Item | Path |
|------|------|
| Prompt scaffold | [`.cursor/prompts/calibrate.md`](../prompts/calibrate.md) |
| Operator doc | [automation/docs/calibrate.md](../../automation/docs/calibrate.md) |
| Harness doctrine | [docs/harness-principles.md](../../docs/harness-principles.md) §7 |
