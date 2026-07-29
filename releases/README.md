# Corner release notes (`releases/`)

**Branch policy:** **`releases/**`** is **personal-branch only** (not on `team/team` or `public-*` via `CLEAN:`). Run **`/release-notes`** on branch **`personal`**.

## Output layout

```text
releases/<batch-token>/
  <batch-token>-rns.md      # Master (general) RNs
  <batch-token>-rns-fx.md   # FX Spot RNs
  <batch-token>-rns-rb.md   # Retail Banking RNs
```

- One folder per comma-separated batch argument (`436-441` is one folder).
- Inside each file: **`h3. v436`**, **`h3. v437`**, … — never a combined range heading.
- Skip a file when that lane has no issues for any version in the batch.

## JQL (schema v4)

SoT: [docs/release-notes-contract.json](../docs/release-notes-contract.json) → `corner_scope` + `jql.templates`.

| Lane | Base query id | Adaptive query id (no `project=`) |
|------|---------------|-------------------------------------|
| Master (general) | `master_base` | `master_adaptive` |
| FX Spot | `fx_spot_base` | `fx_spot_adaptive` |
| Retail Banking | `retail_banking_base` | `retail_banking_adaptive` |

**FX Spot** (`PMOPROC-1398`): Epic Link **not in** `CRT-650`, `CRT-644`. Base XT query also excludes status `aborted`, `resolved`, `won't fix`.

**Retail Banking** (`PMOPROC-1399`): base XT query excludes status `aborted`, `resolved`, `won't fix`. **Not** in the Master PMOPROC list.

**Master:** listed PMOPROCs **or** Epic Link **in** `CRT-650`, `CRT-644`. Base and adaptive: status **not in** `aborted` only.

**Adaptive:** detect `update adaptive` on master base scan; pull token after `to` → `corner-adaptive-{token}`; run all three adaptive JQLs (no `project=`); nest CAN children under the trigger in the correct file.

## Slash command

[.cursor/commands/release-notes.md](../.cursor/commands/release-notes.md)

Helper: [automation/tools/release_notes.py](../automation/tools/release_notes.py)

**Scratch:** `automation/temp/release-notes/` (delete when done).

## Issue line format

Jira wiki links for Confluence paste:

```text
[XT-7884|https://jira.in.devexperts.com/browse/XT-7884] full summary
- CR: [CAN-13953|https://jira.in.devexperts.com/browse/CAN-13953] child summary
```

Host: `jira_host` in the contract.
