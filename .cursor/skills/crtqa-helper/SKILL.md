---
name: crtqa-helper
description: Epic pipeline orchestrator — one stage per turn, session/resume, three gates, COVERAGE-REINFORCE after discover
---

# crtqa-helper

Orchestrate the full epic chain for **one** Jira key per session. **Coach + automation:** probes, verifiers, normative playbooks; **never** weaken gates or skip verifiers.

**Contract:** [`docs/crtqa-helper-contract.json`](../../docs/crtqa-helper-contract.json) (`crtqaHelper.version`). **Command:** [`.cursor/commands/crtqa-helper.md`](../../commands/crtqa-helper.md).

## When to use

- Operator runs **`/crtqa-helper CRT-…`** to start a greenfield epic through **CLOSE** without one-shotting multiple pipelines.
- Operator runs **`/crtqa-helper resume`** after env, coverage review, or discover cred gates.

**Not for:** editing CRT-663 or other closed pilots unless operator explicitly reopens; **not** a substitute for manual `EPIC-PREP:` when helper is off.

## Stage machine

| Stage ID | Pipeline | Gate after? |
|----------|----------|-------------|
| `env` | `crtqa_env_probe.py` | Yes if fail |
| `epic_prep` | `EPIC-PREP:` | No |
| `coverage_v1` | `COVERAGE:` | **coverage_review** |
| `analyse` | `ANALYSE:` | No |
| `discover` | `TEST-DISCOVER:` | **discover_creds** on Phase 0 |
| `coverage_reinforce` | `COVERAGE-REINFORCE:` | No |
| `precon` | `TEST-PRECON:` | No |
| `test_prep` | `TEST-PREP:` | No |
| `close` | `CLOSE:` | Done (`active: false`) |

Default chain: EPIC-PREP → COVERAGE → ANALYSE → TEST-DISCOVER → **COVERAGE-REINFORCE** → TEST-PRECON → TEST-PREP → CLOSE.

## Session files (`epics/<KEY>/helper/`)

| File | Purpose |
|------|---------|
| `session.json` | Stage state — **no creds** |
| `operator-feedback.md` | Ingested on resume after coverage review |
| `stage-log.jsonl` | Append-only audit |
| `affordances-slice.json` | jq export after discover (reinforce input) |

Template: [`epics/templates/helper-session-ref.json`](../../epics/templates/helper-session-ref.json). Gitignored; archives to `context/helper/` on CLOSE.

## Execution limits (non-negotiable)

1. **One pipeline per agent turn** — stop after verifier or gate.
2. **No playbook concatenation** — forbidden to run EPIC-PREP through COVERAGE in one turn.
3. **`jq`** per [`automation/docs/jq.md`](../../automation/docs/jq.md) before reasoning on large JSON.
4. **No summarization substitute** — artefact paths + verifier exit codes = progress.
5. **Explore subagent** (read-only, max 2 parallel) before `coverage_v1` and `coverage_reinforce` for dxtrade5 + webbroker harness affordances.

## Gate copy

### env

Probe failed. Operator: tunnel, `/crtqa-console start`, `/crtqa-env`. Agent **must not** start console from helper. Then `/crtqa-helper resume`.

### coverage_review

`-coverage.md` draft ready. Edit file and/or comment on resume (→ `operator-feedback.md`). Reinforce stage **will** consume both. Then `/crtqa-helper resume`.

### discover_creds

Phase 0 stop. Resume with cred tokens on the **chat line only** (e.g. `dxtrade5_creds=… webbroker_creds=…`) or `fe_exploration_waived=yes` after ack. Never write tokens to `session.json`.

## Per-stage duties

### env

Run probe; on pass chain into `epic_prep` **same turn** only for cold start (contract allows env+epic_prep on first message when env passes).

### coverage_v1 / coverage_reinforce

- Subagent explore harness maps first.
- Run full playbook for trigger.
- `coverage_verify.py --mode obligations` then `--mode emit`.
- Reinforce: read `operator-feedback.md`, `affordances-slice.json`, discover jq slices; merge into existing coverage; set `coverage_pass: 2` or `reinforced_at` in JSON.

### discover

- Honor Phase 0/0b/0c gates.
- On success: `crtqa_helper_affordances.py` → `affordances-slice.json`.
- `discover_verify.py` required.

### close

- `close_verify.py`; `close_archive.py` moves `helper/` → `context/helper/`.
- Set `session.json` `active: false`.

## Increment 2 pilot mode (historical)

Early increments printed next trigger without auto-run. **Current:** helper **executes** one stage per resume with verifiers unless `awaiting_gate` blocks.

## Do / do not

| Do | Do not |
|----|--------|
| Read contract + command each cold session | Run two pipelines in one turn |
| Append `stage-log.jsonl` | Store passwords in helper scratch |
| Ingest resume comments to feedback file | Replace emits with chat summaries |
| Delegate harness explore before coverage passes | Edit shipped_core without entrust |

## Maintainer

Behavior change → bump `crtqaHelper.version`, update [`automation/tools/fixtures/operator-assist/crtqa-helper-golden.json`](../../automation/tools/fixtures/operator-assist/crtqa-helper-golden.json), run `corner-harness-verify.ps1`.
