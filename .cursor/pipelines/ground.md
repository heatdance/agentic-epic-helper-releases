# Pipeline: ground (GROUND)

**Trigger**: user message starts with `GROUND:` and includes a Jira **Epic key** (e.g. `GROUND: CRT-594`). Optional tokens:

- **`probe_waive=yes`** — when console unavailable after console probe (run **`/crtqa-console start`** before GROUND); set **`probe_waived`** + **`waiver_reason`** on console checks — **must not** invent **`verified_syntax`**.
- **`proceed`** — after Phase **0** env hard stop (same bar as TEST-DISCOVER).

**Contract**: [`docs/ground-contract.json`](../../docs/ground-contract.json). **Master**: [`docs/draft-truth-contract.json`](../../docs/draft-truth-contract.json).

**Scope**: **one Epic** per run. **Router**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Outputs**: Updates **`{EpicDir}<KEY>-coverage.json`** in place (probes + `>` lines only). **No** new `-ground.json` in v1.

**Ephemeral**: `{EpicDir}temp/ground-probe-*.log` — **delete** before finish; persist sanitized probe rows on coverage only.

---

## Preconditions

- **`{EpicDir}<KEY>-coverage.json`** with **`coverage_pass`** **1** or **2**.
- **`{EpicDir}<KEY>-ref.json`**.
- **PREPARE**: `python automation/tools/crtqa_console_probe.py` — exit **0** unless operator **`probe_waive=yes`**.
- **Console**: [`/crtqa-console start`](../../.cursor/commands/crtqa-console.md) before probes unless waived.

**Forbidden**: adding new **`checks[]`** ids; shrinking **`scenario_coverage_map`**; CRTQA keys in durable JSON.

---

## Phases

### 0. Console gate

- Run **`crtqa_console_probe.py`** when console checks exist.
- On failure: **STOP** unless **`probe_waive=yes`** (log in **`validation_log`**).

### 1. Identify console-tagged checks

- jq slice checks where section/detail cite console, **`show prices`**, **`backup_price`**, **`daily_data`**, or **`topology_surface_id`** / ref oracle surface **`console_show_prices`**.

### 2. Probe loop

- For each console-tagged **primary** check: run minimal command via [`Invoke-CrtqaDxConsole.ps1`](../../automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1).
- Transcript → `temp/ground-probe-<chk-id>.log` (delete in phase **4**).
- Append **`runtime_probes[]`** on the check: **`command_attempted`**, **`outcome`**, **`verified_syntax`** (success only), **`evidence_note`**, **`probed_at`**.

### 3. Update detail lines

- On **success**: replace harness oracle enum tokens in **`detail_lines`** with **`verified_syntax`** or **`human_oracle_label`** text.
- On **failed/blocked**: set **`ambiguity`** or structured **`! reason:`**; **`grounding_audit`** **`probe_failed`**.
- **Forbidden**: append **`> Discover:`** or **`> Discovery:`** to **`detail_lines`** or **`smart_checklist_markdown`** — machine trace stays in **`linker_trace_lines`** only.

### 4. Finalize

- Run **`python automation/tools/ground_verify.py --mode emit --coverage {EpicDir}<KEY>-coverage.json --ref {EpicDir}<KEY>-ref.json`** — exit **0** required.
- **Delete** `{EpicDir}temp/` entirely.

---

## Related

- dxCore harness: [`docs/dxcore-console-harness.json`](../../docs/dxcore-console-harness.json)
- Next: **`ANALYSE:`** (draft+truth gaps)
