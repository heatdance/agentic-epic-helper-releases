# TEST-DISCOVER orchestrator scaffold

Copy into chat when running **`TEST-DISCOVER: <KEY>`**. Doctrine: [docs/harness-principles.md](../../docs/harness-principles.md) §8. Playbook: [`.cursor/pipelines/test-discover.md`](../pipelines/test-discover.md).

## Mode

- [ ] **Generation** (default): **`sources.crtqa_index_enabled: false`** — **skip Step C-index**
- [ ] **`crtqa_index=yes`** on trigger — run C-index in generation
- [ ] **Benchmark** (`benchmark_suite=` + `benchmark_attempt=`): **`crtqa_index_enabled: true`**

## Preconditions

- [ ] **MUST** `jq` project `{EpicDir}<KEY>-ref.json` and `{EpicDir}<KEY>-coverage.json` per [automation/docs/jq.md](../../automation/docs/jq.md) before loading full files for the closure loop
- [ ] `{EpicDir}<KEY>-ref.json` and `{EpicDir}<KEY>-coverage.json` exist
- [ ] Optional: `-analysis.json` (degraded OK)

## Step 0 — Cold gates (hard stop)

- [ ] Operator prep (recommended): tunnel tab → **`/crtqa-console start`** → **`/crtqa-env`**
- [ ] Run `python automation/tools/crtqa_env_probe.py --coverage {EpicDir}<KEY>-coverage.json` (both gates always)
- [ ] Apply tooling intent rubric from coverage; set **`sources.discovery_mode`** and **`sources.crtqa_index_enabled`**
- [ ] If postgres **required** and tunnel gate pass: MCP **`list_tables`** on **`postgres-ctqa`**
- [ ] If console **required**: `Get-CrtqaConsoleStatus.ps1` exit **0** (agent-run; no UI confirmation)
- [ ] **0b** — For each required dxTrade5/webbroker surface: cred token on line **or** **STOP** (offer **`fe_exploration_waived=yes`** after ack)
- [ ] **0c** — When creds supplied: **`chrome-devtools`** post-login smoke per [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json); set **`fe_ui_sessions`**
- [ ] Unless `skip_cold_gate=yes`: on any **required** gate fail → **STOP** — **no** `-discover.json`
- [ ] Chat: BLUF + **`operator_recovery`** (`fe_dxtrade5_creds_missing`, tunnel, console, auth failed)
- [ ] Operator fixes infra or creds, then **`TEST-DISCOVER: <KEY> proceed`** (or waiver token) → fresh Phase 0 → Step A

## Step A — Ledger (only after Phase 0 pass)

- [ ] Set **`sources.discover_run_started_at`** (ISO-8601, once)
- [ ] Initialize **`validation_log: []`**; append **`phaseA`**
- [ ] One `obligation_ledger[]` row per **primary** `checks[].id`; all `disposition: pending`
- [ ] Snapshot **`environment.client_shell_impact`**; persist **`fe_credentials`** + **`fe_ui_sessions`** from Phase **0b/0c** (not trigger alone)
- [ ] Write `{EpicDir}temp/discover-ledger.json`

## Closure loop (max 5 iterations)

Per iteration, subprocesses as needed:

- [ ] **B** — Affordance mapping for pending rows
- [ ] **C-fixture** — **`fixture_needs[]`** from coverage/ref (always)
- [ ] **C-index** — Jira CRTQA reference index (**only** if `crtqa_index_enabled`)
- [ ] **D** — Delivery + PR map (per competency)
- [ ] **E** — Per [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) **kind** batches + FE; if ref **Adaptive affected** → Chrome smoke on CTQA `/adaptive/` (shared principal, no cred token)
- [ ] Re-iterate shallow registry kinds (`phaseE_fixture_<kind>`) before repeating `console_guide` only
- [ ] Merge ledger; append **`closure_iteration_N`** only (no second **`phase0`**)
- [ ] Update dispositions (`fixture_need_mapped`, not `prerequisite_mapped` in generation)

Then:

```powershell
python automation/tools/discover_verify.py `
  --coverage {EpicDir}<KEY>-coverage.json `
  --ledger {EpicDir}temp/discover-ledger.json
```

- [ ] Verifier exit **0** + setup depth bar → **`complete`** (generation)
- [ ] Verifier fail or shallow depth → **`incomplete`** with **`setup_depth_gaps`**

## Final emit

- [ ] Project to `{EpicDir}<KEY>-discover.json` schema **v3** — **do not** merge prior discover `validation_log`
- [ ] **`reference_index`** / **`precondition_signals`** empty when index off
- [ ] Tooling/session_gates consistent (`session_started: true` iff crtqa `available`)
- [ ] **`operator_recovery: []`** on emitted discover (Phase 0 recovery was chat-only)
- [ ] `obligation_closure.verifier_passed` matches target status
- [ ] Scrub secrets and `/temp/` paths
- [ ] Delete `{EpicDir}temp/` entirely

## Hard stops

- Do **not** emit discover when Phase 0 required probes fail (without `skip_cold_gate=yes`)
- Do **not** one-shot Steps A–G + emit in a single completion
- Do **not** set `discovery_status: complete` without verifier pass and generation setup-depth rules
- Do **not** invent PR URLs or operational commands
- Do **not** run C-index or populate CRTQA keys in generation without **`crtqa_index=yes`**
