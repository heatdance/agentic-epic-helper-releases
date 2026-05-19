# CLOSE verifier (`close_verify.py`)

Normative contract: [docs/close-contract.json](../../docs/close-contract.json). Playbook: [`.cursor/pipelines/close.md`](../../.cursor/pipelines/close.md).

## Modes

| Mode | Purpose |
|------|---------|
| `preflight` | Required JSON at epic root; no `temp/`; not already archived |
| `ladder_l0` … `ladder_l4` | Structural checks per level; optional `--bundle-id` |
| `findings` | `-close.json` findings shape |
| `finalize` | Corrections ⊆ whitelist |
| `md_regen` | Four root `.md` exist and non-empty |
| `archive` | Post-close layout: JSON under `context/`, four md at root |
| `emit` | Full gate on **archived** tree |

## Examples

```bash
python automation/tools/close_verify.py --mode preflight --epic-dir epics/CRT-639

python automation/tools/close_verify.py --mode ladder_l0 --epic-dir epics/CRT-639 --bundle-id tb-001

python automation/tools/close_verify.py --mode findings \
  --epic-dir epics/CRT-639 --close epics/CRT-639/CRT-639-close.json

python automation/tools/close_verify.py --mode emit \
  --epic-dir epics/CRT-639 \
  --close epics/CRT-639/context/CRT-639-close.json
```

## Archive helper

```bash
python automation/tools/close_archive.py --epic-dir epics/CRT-639 \
  --close epics/CRT-639/CRT-639-close.json
```

## jq slices (per bundle, L0)

```bash
jq '.test_bundles[] | select(.bundle_id=="tb-001")' epics/CRT-639/CRT-639-tests.json
jq '.checks[].id' epics/CRT-639/CRT-639-coverage.json
```

See [automation/docs/jq.md](jq.md) for canonical filters.
