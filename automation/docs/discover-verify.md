# TEST-DISCOVER — linker verifier (draft_truth_v2)

Mechanical gate before emitting **`{EpicDir}dependencies/<KEY>-discover.json`**. **Linker mode** — no browser probes. Doctrine: [docs/harness-principles.md](../../docs/harness-principles.md) §8. Contract: [docs/discover-linker-contract.json](../../docs/discover-linker-contract.json).

## CLI (generation default)

```powershell
python automation/tools/discover_verify.py `
  --mode linker `
  --coverage epics/dependencies/CRT-594/CRT-594-coverage.json `
  --discover epics/dependencies/CRT-594/CRT-594-discover.json
```

Requires **`coverage.sources.coverage_frozen_at`**.

Optional **`--ref`**, **`--analysis`** for **`--strict-topology`** / **`--strict-principal`** (opt-in).

## Modes

| Mode | Use |
|------|-----|
| **`linker`** | Production emit (draft_truth_v2) |
| **`generation`** | Legacy fixtures only (benchmark CI) |
| **`benchmark`** | Alias for legacy probe fixtures |
| **`draft_truth`** | Coverage frozen lint only (no discover file) |
| **`principal`** | Principal-only lint |

## Linker failures (exit 1)

- `sources.discovery_mode` ≠ `linker_only`
- `fe_credentials`, `fe_ui_sessions`, or `operator_recovery` present
- `setup_depth: probe_executed` on fixture needs or affordances
- Primary check missing ledger disposition or UI/console affordance link

## Fixtures

```powershell
python automation/tools/discover_verify.py `
  --mode linker `
  --coverage automation/temp/coverage-594-frozen-shell.json `
  --discover automation/tools/fixtures/discover/discover-594-linker-pass.json
```

Bad fixture (`discover-594-linker-bad.json`) must exit **1**.

Legacy probe fixtures under `automation/tools/fixtures/discover/*-minimal.json` use **`--mode generation --allow-incomplete`** until removed.
