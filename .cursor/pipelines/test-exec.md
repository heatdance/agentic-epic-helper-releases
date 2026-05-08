# Pipeline: test-exec (optional E2E materialization + run manifest)

**Trigger**: user message starts with `TEST-EXEC:` and includes a Jira **Epic key** (e.g. `TEST-EXEC: CRT-639`). Optional tokens on the same line (parse flexibly: `key=value`, `key=yes` / `true` / `1`):

| Token | Meaning | Default |
|--------|---------|---------|
| **`base_url=...`** | Application under test (HTTPS). | **Required** for UI materialization; if missing: set manifest `skip_reason: environment_not_ready` and **skip** UI-dependent bundles (still may emit manifest + blocked rows). |
| **`skip_postgres=yes`** | Do not use **postgres-ctqa** MCP or DB assertions. | `no` — attempt DB when bundle needs it and MCP is available. |
| **`include_blocked=yes`** | Allow materialization for bundles with `automation.feasibility == blocked` or exec-detected block. | `no` — **skip** those bundles (status `blocked` / `skipped_feasibility`). |
| **`max_bundles=N`** | Process at most **N** bundles in this run (order: `test_bundles[]` array order). | No cap. |
| **`benchmark_suite=`** / **`benchmark_attempt=`** | Optional; shadow **`{EpicDir}`** ([`docs/benchmark-contract.md`](../../docs/benchmark-contract.md)) — match prior **`TEST-PREP`** tokens for this attempt. | — |

**Scope**: **one Epic** per run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

## Epic workspace (`{EpicDir}`)

Resolve **`{EpicDir}`** like [`epic-prep.md`](epic-prep.md).

**Nature**: **Optional** and **non-gating**. It depends on a reachable app URL, **user-mcp-playwright**, and optionally **postgres-ctqa** (SSH tunnel + global MCP). It does **not** replace human regression execution or `TEST-PREP` drafts. Failures here do not invalidate `-tests.json` / `-tests.md`.

**Prerequisite**: `{EpicDir}<KEY>-tests.json` **must** exist (from [`TEST-PREP:`](test-prep.md)). If missing: **stop** and instruct `TEST-PREP: <KEY>` first (with matching benchmark tokens when in benchmark mode).

**Inputs**: `{EpicDir}<KEY>-tests.json` (schema_version ≥ 1; **`automation`** hints from schema_version **2** when present). Optionally load `{EpicDir}<KEY>-coverage.json` for extra context — do not fabricate checks.

**Outputs**:

- `{EpicDir}tests/` — Playwright spec files, one per successfully materialized bundle, named **`{bundle_id}.spec.ts`** (e.g. `tb-001.spec.ts`). **No secrets** in files; use environment variables or documented placeholders only.
- `{EpicDir}<KEY>-test-exec.json` — manifest per [epics/templates/test-exec-ref.json](../../epics/templates/test-exec-ref.json).

**Explicitly out of scope**: **dxCore console**, **SSH** to hosts, **webbroker-only** environment setup, or any verification path not expressible as **Playwright (UI)** + **readonly Postgres MCP** (`postgres-ctqa`). Do not invent operational commands.

**Ephemeral**: `{EpicDir}temp/` — use only for `test-exec-*` scratch (draft spec fragments, heal diffs, transcript notes). **Must be deleted** before the run is considered complete (success or abort after temp was created). Durable files must **not** contain the substring `/temp/`.

---

## Normative rules (MUST / MUST NOT)

### Feasibility and blocking

- **MUST** mark a bundle **`blocked`** (and **not** emit a runnable spec that pretends setup exists) when the draft or peculiarity text **requires** any of: **console-only** actions, **webbroker-only** configuration, or setup **not** reachable via UI + optional readonly SQL checks.
- **MUST** respect `test_bundles[].automation.feasibility` when present: if **`blocked`**, skip materialization unless **`include_blocked=yes`** in the trigger (use only when a human explicitly accepts risk).
- **MUST** treat **`[TBD]`** / **`[REQUIRES: …]`** / empty **draft** arrays as **not executable** — status `skipped_empty_draft` or `blocked` with `blocked_reason: missing_operational_detail`; do not guess SQL or console steps.
- **MUST NOT** weaken assertions or expected outcomes to obtain green without an explicit **`oracle_change_recorded: true`** on the bundle row **and** a human-auditable reason in **`notes`** (pipeline violation if done silently).

### Environment and optional skip

- **MUST** distinguish **`skip_reason: environment_not_ready`** (no base URL, Playwright MCP unavailable, or user chose skip) from **`failed_clear`** / **`failed_ambiguous`** (run attempted).
- **SHOULD** set `environment.playwright_mcp_ok` / `postgres_mcp_ok` / `tunnel_probe_ok` from **observed** ability to call tools (after reading schemas), not assumed.
- **MUST NOT** copy **passwords**, **tokens**, or **session cookies** into repo files or durable JSON.

### MCP

- **MUST** read **tool schemas** before **user-mcp-playwright** and **postgres-ctqa** calls (same discipline as [`.cursor/rules/mcp-atlassian-search.mdc`](../rules/mcp-atlassian-search.mdc) for Atlassian).
- **MUST** use **postgres-ctqa** only in **readonly** intent; do not bypass MCP readonly mode.

### Orchestration (no one-shot materialization)

- **MUST** use a **single user trigger** `TEST-EXEC:` — the human does **not** re-prompt per bundle.
- **MUST NOT** generate **full** Playwright specs for **more than one** `bundle_id` in a **single** model completion / turn. Use **one subprocess per bundle** (e.g. Cursor **Task** `generalPurpose`) for codegen and heal attempts — same severity as test-prep one-shot violation.
- **MUST** run bundles **sequentially** in array order (subject to **`max_bundles`**). If a bundle ends **`failed_ambiguous`** (cannot separate environment flake vs product defect vs test bug), **stop that bundle**, record status, **continue** to the next.

### Self-healing (strict)

- **MUST** cap **heal_attempts** per bundle (recommended default: **3**). Each attempt **MUST** append a short note describing the **diff** (selector, wait strategy, assertion text — what changed).
- **MUST NOT** increase heal count by “fixing” the **oracle** without **`oracle_change_recorded: true`** and rationale in **`notes`**.

### Traceability

- **MUST** copy **`covers_check_ids`** from `-tests.json` into each **`bundles[]`** row in `-test-exec.json`.
- **SHOULD** copy **`proposed_title`** for human orientation.

---

## Subprocess prompt contract (normative)

**Mechanism**: One **dedicated subprocess** per `test_bundles[].bundle_id` selected for materialization or heal loop.

**Orchestrator → subprocess — include explicitly**:

1. `epic_key`, `bundle_id`, `proposed_title`, `covers_check_ids`, `base_url` (if any).
2. **Draft slice**: `draft.preconditions`, `actions`, `results`, `peculiarities` for this bundle only.
3. **`automation`** object from `-tests.json` when present.
4. **Environment flags**: `skip_postgres`, whether Postgres MCP is usable.
5. Pointers: [`.cursor/pipelines/test-exec.md`](test-exec.md) **Feasibility**, **Self-healing**, **MUST NOT** list; [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json) **format_norms** for human-step intent only — codegen is Playwright.
6. Output: updated spec file content **or** explicit **blocked** / **skipped** JSON for orchestrator merge.

**Subprocess → orchestrator — output**:

- Preferred: write **`{EpicDir}temp/test-exec-spec-<bundle_id>.json`** with `{ "bundle_id", "status", "spec_ts_content" | null, "blocked_reason", "notes"[] }` for orchestrator to merge into `{EpicDir}tests/<bundle_id>.spec.ts` and **`bundles[]`**.
- Alternative: return the same object in the Task transcript if parsing is reliable.

**Caps**: Subprocess **MUST NOT** fetch unrelated Jira issues solely to invent steps; operational text must come from the **draft** or tool-backed sources already in `-tests.json`.

---

## Folder lifecycle

1. Ensure `{EpicDir}` exists.
2. Create **`{EpicDir}temp/`** when writing any `test-exec-*` scratch.
3. Create **`{EpicDir}tests/`** when emitting first spec (if absent).
4. Merge durable content into **`{EpicDir}<KEY>-test-exec.json`** and spec files under **`tests/`**.
5. **Delete** `{EpicDir}temp/` recursively before finishing.
6. **Self-check**: `-test-exec.json` and **`tests/*.spec.ts`** must **not** contain `/temp/`.

---

## Phases (complete all unless N/A — document in `validation_log`)

### 1. Resolve trigger and paths

- Parse `<KEY>` and optional tokens; set `trigger_options` on manifest.
- Append `validation_log` step `1`.

### 2. Load `-tests.json`

- If missing: **stop**; instruct `TEST-PREP: <KEY>`.
- If `sources.map_only: true`: still emit manifest; mark all targeted bundles `skipped_map_only` unless user override token is added later — default **skip** materialization.
- Set `sources.tests_loaded: true`.
- Append `validation_log`: step `2`.

### 3. Environment probe (observational)

- Set `environment.base_url` / `build_id` from trigger if provided.
- Set `playwright_mcp_ok` / `postgres_mcp_ok` / `tunnel_probe_ok` from **attempted** or **reasoned** checks (no secrets in log).
- If **`base_url`** missing: set `skip_reason: environment_not_ready` for the run; UI materialization phases **skip** with bundle status `skipped_env`.
- Append `validation_log`: step `3`.

### 4. Select bundles

- Iterate `test_bundles[]` in order; apply **`max_bundles`**.
- Skip with **`skipped_empty_draft`** if draft arrays are empty or only placeholders without executable content.
- Skip with **`blocked`** / **`skipped_feasibility`** per **Feasibility** rules and **`include_blocked`** default.
- Append `validation_log`: step `4`.

### 5. Per-bundle subprocess (materialize + optional heal)

- For each selected bundle, invoke **one subprocess** per [Subprocess prompt contract](#subprocess-prompt-contract-normative).
- Orchestrator merges spec into `{EpicDir}tests/<bundle_id>.spec.ts` when `spec_ts_content` is non-null.
- Update **`bundles[]`**: `status`, `heal_attempts`, `oracle_change_recorded`, `last_run_at`, `notes`.
- On **`failed_ambiguous`**: do not retry indefinitely; **continue** to next bundle.
- Append `validation_log`: step `5-<bundle_id>` per bundle.

### 6. Emit manifest

- Write **`{EpicDir}<KEY>-test-exec.json`** from [epics/templates/test-exec-ref.json](../../epics/templates/test-exec-ref.json).
- Set `run_completed_at` (ISO-8601).

### 7. Cleanup

- **Delete** `{EpicDir}temp/`.
- Append `validation_log`: step `7` (complete).

---

## Pitfalls

- **One-shot all-bundle specs** — Violates [Orchestration](#orchestration-no-one-shot-materialization); use **one subprocess per bundle**.
- **Pretending console/webbroker setup** — Use **`blocked`**; no fake UI flow.
- **Secrets in specs** — Use env vars; never commit credentials.
- **Temp leakage** — Mandatory delete + substring self-check.
- **Conflating skip vs fail** — Use `skip_reason` vs `failed_*` statuses consistently.

---

## Related

- Input template: [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json)
- Manifest template: [epics/templates/test-exec-ref.json](../../epics/templates/test-exec-ref.json)
- Test drafting: [`test-prep.md`](test-prep.md)
- Human how-to (tunnel, Postgres MCP): [`automation/tools/tunnel/README.md`](../../automation/tools/tunnel/README.md)
- Router: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc)
