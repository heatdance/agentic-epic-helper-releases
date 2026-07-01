# jq — JSON projection for agents

[jq](https://jqlang.org/) is a command-line JSON processor. In this workspace, agents **project** large repo JSON into small slices **before** loading full files into chat. jq is **not** a Cursor plugin or MCP — it runs in the shell like `python` or `git`.

**Norms:** [`.cursor/rules/jq-json.mdc`](../../.cursor/rules/jq-json.mdc), [docs/harness-principles.md](../../docs/harness-principles.md) (JSON inspection).

## Install (system-wide)

Install once per machine so **any** Cursor workspace terminal can run `jq`.

| OS | Command |
|----|---------|
| **Windows** | `winget install --id jqlang.jq -e` |
| **macOS** | `brew install jq` (or [download](https://jqlang.org/download/)) |
| **Linux** | distro package or [download](https://jqlang.org/download/) |

Verify: `jq --version` (expect **1.7+**; repo tested with **1.8.x**).

**Troubleshooting (Windows):** After winget, restart Cursor or open a **new** terminal tab. If still missing, refresh PATH in PowerShell:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
jq --version
```

There is **no** vendored `jq.exe` in this repo — use system PATH.

**Org doc (manual):** Consider adding **jq** to [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) alongside MCP/tunnel prerequisites.

## Agent norms

| Situation | Use jq? |
|-----------|---------|
| **Inspect** epic/harness JSON (~60+ lines or need a subset) | **Yes** — run filter, summarize output in chat |
| **Edit / emit** durable `*-*.json` | **No** requirement — Read/write the file; jq optional for spot-check |
| **Schema / pipeline gate** | **No** — use `discover_verify.py`, `calibrate_verify.py`, `crtqa_console_probe.py`, etc. |
| **Small JSON** (&lt; ~60 lines) | Optional |
| **Invalid JSON** | Fix file or use Python; jq will error |
| **Repo-wide file find** | `grep` / Glob — not jq |
| **MCP-returned JSON** | jq optional |

**MUST NOT** use `grep` / `Select-String` as the primary way to query **structured** in-repo JSON.

## PowerShell examples

From repo root; quote the filter with single quotes; path last:

```powershell
jq '.test_prep_gates' epics/CRT-639/CRT-639-discover.json
jq '.checks[] | select(.id=="chk-003")' epics/CRT-639/CRT-639-coverage.json
jq -r '.bundles[].id' epics/CRT-639/CRT-639-tests.json
```

Calibrate gold: `.cursor/calibrate/<KEY>-gold/<KEY>-coverage.json` (and tests).

## Canonical filters

Replace `<KEY>`, `chk-NNN`, `mNNN`, and package id as needed. Production `{EpicDir}` = `epics/<KEY>/`.

### Discover (`<KEY>-discover.json`)

```powershell
jq '{discovery_status, test_prep_gates, obligation_closure}' epics/<KEY>/<KEY>-discover.json
jq '.obligation_ledger[] | select(.check_id=="chk-NNN")' epics/<KEY>/<KEY>-discover.json
jq '.fixture_needs[]' epics/<KEY>/<KEY>-discover.json
jq '.validation_log[-5:]' epics/<KEY>/<KEY>-discover.json
```

### Coverage (`<KEY>-coverage.json`)

```powershell
jq '.epic_verification_focus' epics/<KEY>/<KEY>-coverage.json
jq '.checks[] | select(.verification_role=="primary") | {id, summary}' epics/<KEY>/<KEY>-coverage.json
jq '.coverage_matrix[] | select(.id=="mNNN")' epics/<KEY>/<KEY>-coverage.json
```

### Epic ref (`<KEY>-ref.json`)

```powershell
jq '.client_shell_impact' epics/<KEY>/<KEY>-ref.json
jq '.requirements[] | {key, snippet_status}' epics/<KEY>/<KEY>-ref.json
jq '.implementation.hits' epics/<KEY>/<KEY>-ref.json
```

### Precon (`<KEY>-precon.json`)

```powershell
jq '.test_skeleton[] | {bundle_id, covers_check_ids, case_outline}' epics/<KEY>/<KEY>-precon.json
jq '.session_placeholders, .command_patterns' epics/<KEY>/<KEY>-precon.json
jq '.precon_steps[] | {id, cluster_id, surfaces}' epics/<KEY>/<KEY>-precon.json
```

### Tests (`<KEY>-tests.json`)

```powershell
jq '.test_bundles[] | {bundle_id, covers_check_ids, proposed_title}' epics/<KEY>/<KEY>-tests.json
jq '.test_bundles[] | select(.bundle_id=="tb-001")' epics/<KEY>/<KEY>-tests.json
jq '.test_bundles[] | select(.covers_check_ids[]? == "chk-NNN") | {bundle_id}' epics/<KEY>/<KEY>-tests.json
```

### CLOSE (`<KEY>-close.json` — pre-archive at root; post-archive under `context/`)

```powershell
jq '{epic_verdict, findings: (.findings|length), corrections: (.corrections|length)}' epics/<KEY>/context/<KEY>-close.json
jq '.findings[] | select(.severity=="error") | {id, level, bundle_id, summary}' epics/<KEY>/context/<KEY>-close.json
jq '.test_bundles[] | select(.bundle_id=="tb-001") | {covers_check_ids, draft: .draft | {actions: (.actions|length), results: (.results|length)}}' epics/<KEY>/<KEY>-tests.json
```

### TEST-PREP temp / plan (ephemeral under `{EpicDir}temp/`)

```powershell
jq '.bundles[] | {bundle_id, plan_status}' epics/<KEY>/temp/test-prep-plan.json
jq '.verification_plan[] | {check_id, min_case_count}' epics/<KEY>/temp/test-prep-plan-<bundle_id>.json
```

### Harness / config JSON

```powershell
jq '.tiers[] | select(.id=="T1") | .match_any_package[] | select(.id=="jq_json")' docs/harness-map.json
jq '.tiers[] | select(.id=="T0") | .read' docs/harness-map.json
```

## Optional global Cursor User Rule

Repo rules apply only in **cursor.corner**. For the same jq norms in **all** workspaces, save the block below as `%USERPROFILE%\.cursor\rules\jq-json-global.mdc` (Windows) or `~/.cursor/rules/jq-json-global.mdc`:

```markdown
---
description: Use jq to inspect JSON before loading large files into agent context
alwaysApply: true
---

# JSON inspection (jq)

- **MUST** use shell `jq` to **inspect** JSON before pasting large blobs into chat or multi-field reasoning on nested data.
- **Threshold:** ~**60 lines** or whenever you need a **subset** of keys/arrays.
- **MUST NOT** use grep/Select-String as the primary query for structured JSON files.
- **Exceptions:** writing/editing JSON; small files; invalid JSON; normative Python verifiers; MCP blobs (jq optional).
- Install: Windows `winget install --id jqlang.jq -e`; see https://jqlang.org/download/
```

## Related

- T1 package **`jq_json`** in [docs/harness-map.json](../../docs/harness-map.json)
- Pipelines (**MUST** project before full Read): [epic-prep](../../.cursor/pipelines/epic-prep.md), [coverage](../../.cursor/pipelines/coverage.md), [analysis](../../.cursor/pipelines/analysis.md), [test-discover](../../.cursor/pipelines/test-discover.md), [test-precon](../../.cursor/pipelines/test-precon.md), [test-prep](../../.cursor/pipelines/test-prep.md), [close](../../.cursor/pipelines/close.md)
- Prompt scaffolds: [`.cursor/prompts/`](../../.cursor/prompts/) (orchestrators reference this doc for epic JSON inspect)
