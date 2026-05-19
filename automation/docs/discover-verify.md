# TEST-DISCOVER — obligation closure verifier

Mechanical gate before emitting **`{EpicDir}<KEY>-discover.json`**. Agents **MUST** run this after the closure loop and **before** deleting **`{EpicDir}temp/`** (or against the emitted file immediately after write).

Playbook: [`.cursor/pipelines/test-discover.md`](../../.cursor/pipelines/test-discover.md). Doctrine: [docs/harness-principles.md](../../docs/harness-principles.md) §8.

## CLI

```powershell
python automation/tools/discover_verify.py `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --ledger epics/CRT-639/temp/discover-ledger.json
```

Post-emit check:

```powershell
python automation/tools/discover_verify.py `
  --coverage epics/CRT-639/CRT-639-coverage.json `
  --discover epics/CRT-639/CRT-639-discover.json
```

Optional **`--mode generation|benchmark`** overrides **`sources.crtqa_index_enabled`** inference.

Optional **`--ref epics/<KEY>/<KEY>-ref.json`** when **`environment.client_shell_impact`** is missing on the ledger/discover (Adaptive complete bar).

Exit code **0** = closure contract satisfied for the target **`discovery_status`**. Non-zero = run another closure iteration or emit **`incomplete`** with logged gaps.

## What it checks

1. Every **primary** `checks[].id` in **`-coverage.json`** has an **`obligation_ledger`** row with **`disposition`** not **`pending`** (accepts **`fixture_need_mapped`**).
2. If **`discovery_status`** is **`complete`**, **`obligation_closure.verifier_passed`** is true and no pending rows remain.
3. **CRTQA-off (schema v3 generation):** when **`sources.crtqa_index_enabled`** is false — **`reference_index`**, **`precondition_signals`**, **`prerequisite_edges`** empty; no **`prerequisite_keys`** citing **`CRTQA-*`**; no **`prerequisite_mapped`** dispositions.
4. **Generation + `discovery_status: complete`:** setup depth bar (fixture needs not shallow unless **`setup_depth_gaps`**); registry kinds in [`docs/discover-fixture-probes.json`](../../docs/discover-fixture-probes.json) linked to primary chks must meet **`complete_requires`** (typically **`probe_executed`**).
4b. **FE UI sessions (v3):** **`webbroker_dealer_client_metrics`** / **`dxtrade5_retail_positions`** at **`probe_executed`** require matching **`fe_ui_sessions.*: authenticated`** (or **`waived`** with linked chks **`scope_gap`**). **`complete`** with FE fixture kinds requires **`authenticated`** or **`waived`** per surface — see [`docs/fe-ui-probe-contract.json`](../../docs/fe-ui-probe-contract.json).
5. **Generation + `complete` + Adaptive affected:** when **`environment.client_shell_impact.adaptive.status`** (or **`--ref`**) is **`affected`** / **`likely_affected`** — no **`closure_gaps`** with adaptive-not-probed reasons; at least one Adaptive-linked affordance at **`probe_executed`** with runtime evidence; **`fe_credentials.adaptive`** must be **`not_required`**, not **`missing`**.
6. **Generation warnings:** **`verification_affordances`** with **`setup_role: fixture`**, **`evidence_grade: doc_only`**, linked fixture still shallow while chk has **`console`** in **`evidence_need`**.
7. **Phase 0 emit forbidden (`--discover` only):** if **`cold_gate_skip_token_used`** is false and **`session_gates`** show postgres **`probe_required_operator`** or crtqa handshake **`failed`** / **`pending_operator_session`** while intent required — artefact must not exist.
8. **Tooling consistency:** crtqa **`intent: required`** + **`session_started: false`** → **`availability`** must not be **`available`**; failed handshake must not pair with **`available`**.
9. **`operator_recovery[]` on emitted discover:** must be **`[]`** when Phase 0 passed; if non-empty, each item must have **`gate_id`**, **`actions[]`**, **`documentation_refs[]`** (no legacy **`tool`** / **`action`** only).
10. **`validation_log`:** if **`sources.discover_run_started_at`** set, no entry **`at`** earlier; at most one **`phase0`** unless **`phase0_proceed`** appears before a second **`phase0`**.
11. **`tooling.*.intent: required`** implies **`availability: available`**, **`cold_gate_skip`**, or non-empty **`operator_recovery`** (ledger staging only before Phase 0 pass).
12. No **`/temp/`** path segments or obvious secrets in durable JSON strings.

**v2 artefacts:** verifier warns; re-verify may fail CRTQA-off or Phase 0 rules — re-run **`TEST-DISCOVER`** after infra ready.

## Self-heal loop

On verifier failure: do **not** emit **`complete`**. Re-run closure for pending obligations / shallow fixture depth only (max **5** iterations, **no-progress** stop per playbook). Use **`--allow-incomplete`** when validating an intentional **`incomplete`** artefact.
