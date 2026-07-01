# CLOSE verifier (`close_verify.py`)

Normative contract: [docs/close-contract.json](../../docs/close-contract.json). Playbook: [`.cursor/pipelines/close.md`](../../.cursor/pipelines/close.md). Topology lint: [docs/close-topology-contract.json](../../docs/close-topology-contract.json). Principal lint: [docs/close-principal-contract.json](../../docs/close-principal-contract.json).

## Modes

| Mode | Purpose |
|------|---------|
| `preflight` | Required JSON at epic root; no `temp/`; not already archived |
| `ladder_l0` … `ladder_l4` | Structural checks per level; optional `--bundle-id` |
| `findings` | `-close.json` findings shape |
| `finalize` | Corrections ⊆ whitelist |
| `md_regen` | Three root `.md` exist and non-empty (coverage, analysis, tests; precon optional legacy) |
| `archive` | Post-close layout: JSON under `context/`, three md at root (+ optional legacy precon.md) |
| `topology` | Cross-artifact oracle/session lint; requires `--strict-topology` |
| `principal` | Cross-artifact principal lint; requires `--strict-principal` (implied when `--mode principal`) |
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

python automation/tools/close_verify.py --mode topology --strict-topology \
  --epic-dir automation/tools/fixtures/close/topology-594-pass

python automation/tools/close_verify.py --mode principal --strict-principal \
  --epic-dir automation/tools/fixtures/close/principal-594-pass

python automation/tools/close_verify.py --mode principal --strict-principal \
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json \
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json \
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json \
  --precon automation/tools/fixtures/precon/precon-594-shell-principal-minimal.json \
  --tests automation/tools/fixtures/test_prep/tests-principal-bad-missing-setup.json \
  --epic-dir automation/tools/fixtures/close/principal-594-pass
```

## Principal checks (`--strict-principal`)

Requires all five JSON artefacts. Skips when no principal handoff (`sources.principal_loaded` / ref provision personas).

| Check | Failure when |
|-------|----------------|
| `principal_loaded` alignment | discover / precon / tests flags disagree (warning) |
| Provision chain | discover `ref_principal_provision` fixture not satisfied by precon `pc-setup` |
| Setup skeleton parity | precon `tb-setup` `covers_check_ids` != tests `tb-setup` bundle |
| Deferral parity | coverage deferral-only IDs != precon/tests excluded + tests `coverage_gaps` |
| Placeholder chain | precon `session_placeholders` keys not copied to tests `sources.session_placeholders` |
| Tests leg | Delegates to `test_prep_verify.verify_strict_test_prep_principal` |

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
