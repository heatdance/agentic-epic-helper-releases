---
description: Assemble release-note markdown from six PMOPROC JQL queries per fixVersion batch (Master, FX Spot, Retail Banking).
---

# /release-notes

Build **Confluence-style** release note markdown from Jira using **[docs/release-notes-contract.json](../../docs/release-notes-contract.json)** (schema v4). **No** `corner-map.json` — scope is fixed PMOPROC / Epic Link JQL.

**Recommended:** branch **`personal`** — **`releases/**`** is personal-only (CLEAN).

## Required input

Release batch string, e.g. `270.29` or `270.29, 436-441`.

- Comma separates **batch folders** (`releases/<batch-token>/`).
- Hyphen inside a token expands versions: `436-441` → 436, 437, …, 441 (one folder, **one** file per lane with multiple `h3. v{version}` sections — never `h3. v436-441`).

## Output lanes

| Lane | File suffix | Base query id | Adaptive query id |
|------|-------------|---------------|-------------------|
| Master (general) | `-rns.md` | `master_base` | `master_adaptive` |
| FX Spot | `-rns-fx.md` | `fx_spot_base` | `fx_spot_adaptive` |
| Retail Banking | `-rns-rb.md` | `retail_banking_base` | `retail_banking_adaptive` |

## Tools

- **`user-mcp-atlassian`**: `jira_search` (paginate `limit=50`, `start_at` until exhausted).
- **`python automation/tools/release_notes.py`**: `parse-batches`, `build-jql`, `assemble-from-raw`, `write-batch`.

## Scratch

**`automation/temp/release-notes/`** — Jira JSON per version/query; delete when done.

## Six JQL queries (per fixVersion)

Render with `build-jql --query <id> --version <V>` or `--adaptive-token <token>` for adaptive ids.

| Query id | Output lane | Notes |
|----------|-------------|--------|
| `master_base` | `-rns.md` | Master PMOPROCs **or** Epic Link **in** CRT-650, CRT-644; status **not** aborted |
| `fx_spot_base` | `-rns-fx.md` | PMOPROC-1398; Epic Link **not** CRT-650, CRT-644; status **not** aborted, resolved, won't fix |
| `retail_banking_base` | `-rns-rb.md` | PMOPROC-1399; status **not** aborted, resolved, won't fix |
| `master_adaptive` | nested in `-rns.md` | **No** `project=`; same Epic include as master base; status **not** aborted |
| `fx_spot_adaptive` | nested in `-rns-fx.md` | **No** `project=`; same Epic exclude as fx base; status **not** aborted |
| `retail_banking_adaptive` | nested in `-rns-rb.md` | **No** `project=`; PMOPROC-1399; status **not** aborted |

**CRT-644** is on the **Master** branch (with CRT-650), excluded from **FX Spot**.

**PMOPROC-1399** is **Retail Banking only** — not in the Master PMOPROC list (avoids duplicate lines in `-rns.md`).

Constants: `corner_scope` in [docs/release-notes-contract.json](../../docs/release-notes-contract.json).

## Workflow (per comma-separated batch)

### 1. Parse

```bash
python automation/tools/release_notes.py parse-batches "436-441"
```

### 2. Collect (per `version` in batch)

For each version `V`:

```bash
python automation/tools/release_notes.py build-jql --query master_base --version V
python automation/tools/release_notes.py build-jql --query fx_spot_base --version V
python automation/tools/release_notes.py build-jql --query retail_banking_base --version V
```

Run all three via MCP `jira_search`; save issues under `automation/temp/release-notes/`.

**Adaptive (only if master_base has a trigger):** summary contains `update adaptive` (or Task + `adaptive`).

1. Read trigger summary; pull token after **`to`** (e.g. `dev.5` → `corner-adaptive-dev.5`).
2. Run adaptive JQL (**do not** add `project = XT`):

```bash
python automation/tools/release_notes.py build-jql --query master_adaptive --adaptive-token dev.5
python automation/tools/release_notes.py build-jql --query fx_spot_adaptive --adaptive-token dev.5
python automation/tools/release_notes.py build-jql --query retail_banking_adaptive --adaptive-token dev.5
```

3. MCP search all three; attach CAN children to the matching lane for that version.

### 3. Assemble and emit

Build `version_payloads[]` JSON:

```json
{
  "batch": {"batch_token": "436-441", "versions": ["436", "437", "438", "439", "440", "441"]},
  "version_payloads": [
    {
      "version": "436",
      "master_base": [],
      "fx_base": [],
      "rb_base": [],
      "master_adaptive": [],
      "fx_adaptive": [],
      "rb_adaptive": []
    }
  ]
}
```

```bash
python automation/tools/release_notes.py assemble-from-raw --input automation/temp/release-notes/assembled-input.json
```

Write files (skip empty lane):

```bash
python automation/tools/release_notes.py write-batch --batch-token 436-441 --lane non_fx --content ...
python automation/tools/release_notes.py write-batch --batch-token 436-441 --lane fx --content ...
python automation/tools/release_notes.py write-batch --batch-token 436-441 --lane rb --content ...
```

### 4. Report (BLUF)

- Batch token(s) and expanded versions
- Files written vs skipped (empty lane)
- Per version: master / fx / retail-banking counts; adaptive trigger key + token + child counts per lane
- Blockers (e.g. adaptive trigger but no token in summary)

Delete **`automation/temp/release-notes/`** when done.

## Markdown format

- **Wiki links:** `[XT-7884|https://jira.in.devexperts.com/browse/XT-7884] summary` (host from contract `jira_host`).
- **Adaptive:** trigger line ends with `:`; children `- CR: [CAN-13953|…] summary` with **`key` required**.

## Helper reference

| Subcommand | Purpose |
|------------|---------|
| `parse-batches` | Expand version tokens |
| `list-queries` | Six query ids |
| `build-jql` | Render JQL for MCP |
| `assemble-from-raw` | `version_payloads` → master / fx / rb markdown |
| `format-markdown` | Low-level formatter |
| `write-batch` | `releases/<token>/` (`--lane non_fx` \| `fx` \| `rb`) |
