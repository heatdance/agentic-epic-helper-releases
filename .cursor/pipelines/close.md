# Pipeline: close (epic integrity ladder + archive)

**Trigger**: user message starts with `CLOSE:` and includes a Jira **Epic key** (e.g. `CLOSE: CRT-639`). Optional tokens on the **same line**:

| Token | Meaning | Default |
|--------|---------|---------|
| **`heal=no`** | Skip mechanical corrections in finalize | **heal on** (apply whitelist fixes) |
| **`strict_topology=yes`** | Run Phase E½ cross-artifact oracle/session topology lint | **off** (legacy epics unchanged) |
| **`strict_principal=yes`** | Run Phase E¾ cross-artifact principal lint | **off** (legacy epics unchanged) |

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Nature**: **Cold-session**, **documentation-only**. Backward integrity ladder from `-tests.json` through ref. **No** MCP, creds, Chrome, postgres, console, SSH, or live app. **Does not** re-run **ANALYSE**.

**Contract**: [`docs/close-contract.json`](../../docs/close-contract.json). **Topology lint**: [`docs/close-topology-contract.json`](../../docs/close-topology-contract.json). **Principal lint**: [`docs/close-principal-contract.json`](../../docs/close-principal-contract.json). **Verifier**: [`automation/docs/close-verify.md`](../../automation/docs/close-verify.md). **Template**: [`epics/templates/close-ref.json`](../../epics/templates/close-ref.json).

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

**Pre-CLOSE** (upstream pipelines): all durable JSON and md at **`{EpicDir}`** root.

**Post-CLOSE** (archive **always**, any verdict):

- **Root:** `{EpicDir}<KEY>-coverage.md`, `<KEY>-analysis.md`, `<KEY>-tests.md` only (human surface; v3 — no precon.md).
- **`{EpicDir}context/`:** all `*.json` including `<KEY>-close.json`; legacy `tests/*.spec.ts` under `context/tests/` if present.
- **No** `<KEY>-close.md`.

**Prerequisites** (preflight — **STOP** if missing):

- `{EpicDir}dependencies/<KEY>-ref.json`, `-coverage.json`, `-discover.json`, `-tests.json` from upstream pipelines (`-precon.json` optional legacy).
- **Optional:** `-analysis.json` (if absent, regenerate **analysis.md** stub per contract).
- **`{EpicDir}temp/`** must **not** exist.

**Ephemeral**: `{EpicDir}temp/` — close scratch only (`close-ladder-*.json`, regen notes). **Delete** before finish.

---

## Normative rules (MUST / MUST NOT)

### Orchestration

- **MUST** use **one subprocess per `test_bundles[].bundle_id` per ladder level** (L0–L4). **MUST NOT** load full `-tests.json` / `-coverage.json` into one completion — **jq** slice per bundle per [automation/docs/jq.md](../../automation/docs/jq.md).
- **MUST** accumulate **findings only** in L0–L4 (no JSON edits except append to temp findings merge).
- **MUST** apply **corrections** only in **finalize** (single phase), using whitelist in contract.
- **MUST NOT** add/remove bundles, rewrite oracles or test steps, or remove coverage checks.
- **MUST NOT** store secrets in durable JSON or md.

### Verdicts

- **`pass`** — no error-severity findings remain.
- **`pass_with_warnings`** — warnings only (no errors).
- **`fail`** — one or more error-severity findings remain, or preflight/archive/verifier failed.

### Archive

- **MUST** run archive after finalize **even on `fail`** ([`docs/close-contract.json`](../../docs/close-contract.json) `archive_always`).
- **MUST** regenerate **three** root `.md` from JSON **after** finalize corrections, **before** archive move.

---

## Subprocess prompt contract (L0–L4)

**Mechanism**: One **dedicated subprocess** per `(level, bundle_id)`.

**Orchestrator → subprocess — include**:

1. `epic_key`, `level`, `bundle_id`, `covers_check_ids`.
2. **jq slice** for that bundle from `-tests.json` and level-appropriate source JSON.
3. Check families for that level from contract **`ladder_checks`**.
4. Output path: `{EpicDir}temp/close-ladder-<level>-<bundle_id>.json` with `{ "findings": [...] }` only.

**Subprocess → orchestrator**: findings array; **no** file edits.

**Epic-wide pass** (optional single subprocess): orphan checks, cross-file id audit — append to same findings list.

---

## Phases

### 0. Preflight

- Parse `<KEY>`, `heal=no`, `strict_topology=yes`, `strict_principal=yes`.
- Run `python automation/tools/close_verify.py --mode preflight --epic-dir {EpicDir}`.
- If epic already has `context/<KEY>-ref.json` → **STOP** (closed epic; see [HOW-TO.md](../../HOW-TO.md)).
- Initialize `{EpicDir}temp/` and in-progress `{EpicDir}dependencies/<KEY>-close.json` from template.
- Append `validation_log` step `0`.

### L0–L4. Ladder (per bundle, per level)

For each level in order **L0 → L4**, for each `bundle_id` in `test_bundles[]` (respect `max_bundles_per_run` in contract):

1. Spawn subprocess per [Subprocess prompt contract](#subprocess-prompt-contract-l0l4).
2. Merge findings into `<KEY>-close.json` with unique `find-###` ids.
3. Run `close_verify.py --mode ladder_<ln> --epic-dir {EpicDir} [--bundle-id …]` as a sanity check (warnings OK).
4. Update `ladder_summary[]` for the level.

**L0 families**: `covers_check_ids` ⊆ coverage; draft 1:1; no CRTQA in generation mode; unique `bundle_id`. **Draft+truth:** linker discover has no probe fields; `test_prep_gates.blocked` should be false.

**L1 families**: tests **`shared_preconditions`** when scenario_intent; **`scenario_groups`** 1:1 with bundles when frozen coverage.

**L2 families**: discover gates vs tests `sources.discover_blocked_acknowledged`.

**L3 families**: coverage checks / obligations_coverage for bundle checks.

**L4 families**: ref snippets / obligations vs bundle (epic-wide ref slice allowed per bundle check set).

### E. Epic-wide pass

- Orphan coverage checks not referenced by any bundle; orphan bundles; id namespace consistency.
- Append findings; append `validation_log` step `epic`.

### E½. Topology lint (optional — `strict_topology=yes`)

When the trigger includes **`strict_topology=yes`**:

1. **jq** slices per [`docs/close-topology-contract.json`](../../docs/close-topology-contract.json) — ref `pricing_oracle_rules`, coverage `oracle_rule_id`, discover `oracle_binding`, precon `pattern_ref` / `session_placeholders`, tests `coverage_gaps` / `precon_cluster_refs`. **MUST NOT** load full epic JSON into one completion.
2. Run `python automation/tools/close_verify.py --mode topology --strict-topology --epic-dir {EpicDir}`.
3. Merge findings into `<KEY>-close.json` with kinds `oracle_mismatch`, `topology_drift`, or `session_mismatch` per contract; update `topology_lint` summary on `-close.json`.
4. Append `validation_log` step `topology`.

**Legacy no-op:** when none of discover / precon / tests have `sources.topology_loaded: true`, verifier skips strict checks (ref-only topology does not force lint).

**Program note:** Round 1 topology lint (E½) and Round 2 principal lint (E¾) complete the correction program; no downstream pipeline.

### E¾. Principal lint (optional — `strict_principal=yes`)

When the trigger includes **`strict_principal=yes`**:

1. **jq** slices per [`docs/close-principal-contract.json`](../../docs/close-principal-contract.json) — ref `downstream_hints`, discover `fixture_needs`, precon `pc-setup` / `tb-setup` / `session_placeholders`, tests setup bundle / `persona_tags`. **MUST NOT** load full epic JSON into one completion.
2. Run `python automation/tools/close_verify.py --mode principal --strict-principal --epic-dir {EpicDir}`.
3. Merge findings into `<KEY>-close.json` with kinds `provision_mismatch`, `persona_drift`, `deferral_drift`, or `principal_drift` per contract; update `principal_lint` summary on `-close.json`.
4. Append `validation_log` step `principal`.

**Legacy no-op:** when none of discover / precon / tests have `sources.principal_loaded: true` and ref has no provision personas, verifier skips strict checks.

### F. Finalize (single phase)

1. Compute `epic_verdict` from findings severities (contract **`verdict_rules`**).
2. If heal enabled (default): apply **whitelist** corrections to JSON files at **root** paths; record each in `corrections[]`.
3. Run `close_verify.py --mode finalize --close {EpicDir}dependencies/<KEY>-close.json`.
4. **Regenerate** three md from JSON (playbooks in contract **`md_regen_sources`**):
   - coverage.md ← coverage.json
   - analysis.md ← analysis.json or stub when absent
   - tests.md ← tests.json (`format_norms`)
5. Run `close_verify.py --mode md_regen --epic-dir {EpicDir}`.
6. Append `validation_log` step `finalize`.

### G. Archive

1. Write final `<KEY>-close.json` at root (if not already).
2. Run `python automation/tools/close_archive.py --epic-dir {EpicDir} --close {EpicDir}dependencies/<KEY>-close.json` (moves JSON to `context/`; if present, gitignored `{EpicDir}helper/` → `{EpicDir}context/helper/` per [`epic-helper-contract.json`](../../docs/epic-helper-contract.json)).
3. Run `close_verify.py --mode archive` then `--mode emit --close {EpicDir}context/<KEY>-close.json`.
4. **Delete** `{EpicDir}temp/`.
5. Append `validation_log` step `archive` (complete).

---

## Pitfalls

- **One-shot full epic JSON** — Use jq + per-bundle subprocesses.
- **Editing during L0–L4** — Findings only until finalize.
- **Skipping archive on fail** — Archive **always**.
- **Leaving close.json at root** — Must end under `context/`.
- **Rerunning EPIC-PREP on closed epic** — JSON under `context/` breaks upstream paths; restore layout or use new epic folder.
- **Strict topology on pre-archive tree** — Phase E½ requires all five JSON at epic **root** (not under `context/`).
- **Strict principal on pre-archive tree** — Phase E¾ requires all five JSON at epic **root** (not under `context/`).

---

## Explicitly out of scope

- MCP / environment / Playwright / chrome-devtools
- Re-running **ANALYSE**
- Mandatory-chain doc reconciliation (discover always required in all playbooks — separate pass)
- Benchmark CLOSE KPI metrics
- Automated un-archive

---

## Related

- Archive helper: [`automation/tools/close_archive.py`](../../automation/tools/close_archive.py)
- Topology lint contract: [`docs/close-topology-contract.json`](../../docs/close-topology-contract.json)
- Principal lint contract: [`docs/close-principal-contract.json`](../../docs/close-principal-contract.json)
- Test drafting input: [`test-prep.md`](test-prep.md)
- Router: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc)
- Epic layout: [`epics/README.md`](../../epics/README.md)
