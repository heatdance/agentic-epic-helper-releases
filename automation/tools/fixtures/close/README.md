# CLOSE verifier fixtures

Minimal epic-root layouts for `close_verify.py`. Not production epic data.

## Pass layouts (topology — Round 1)

| Directory | Chain |
|-----------|-------|
| `topology-639-pass/` | metrics/formula fixture chain (639 ref; no oracle rules on ref) |
| `topology-594-pass/` | shell/widget fixture chain with full oracle topology |

## Pass layouts (principal — Round 2 step 8)

| Directory | Chain |
|-----------|-------|
| `principal-594-pass/` | Full principal chain: provision + pc-setup + persona-split tests |
| `principal-639-pass/` | Metrics principal chain; deferral parity; no pc-setup |

## Bad oracle (topology)

| File | Role |
|------|------|
| `topology-594-oracle-bad-coverage.json` | Same as reinforce minimal but `chk-001.oracle_rule_id=por-999` (not in ref) |

## Commands (from repo root)

```powershell
$fix = "automation/tools/fixtures/close"

# 639 topology pass — expect exit 0
python automation/tools/close_verify.py --mode topology --strict-topology `
  --epic-dir "$fix/topology-639-pass"

# 594 topology pass — expect exit 0
python automation/tools/close_verify.py --mode topology --strict-topology `
  --epic-dir "$fix/topology-594-pass"

# 594 principal pass — expect exit 0
python automation/tools/close_verify.py --mode principal --strict-principal `
  --epic-dir "$fix/principal-594-pass"

# 639 principal pass — expect exit 0
python automation/tools/close_verify.py --mode principal --strict-principal `
  --epic-dir "$fix/principal-639-pass"

# 594 principal bad (missing tb-setup) — expect exit 1
python automation/tools/close_verify.py --mode principal --strict-principal `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json `
  --coverage automation/tools/fixtures/coverage/coverage-594-shell-reinforce-principal-minimal.json `
  --discover automation/tools/fixtures/discover/discover-594-shell-principal-minimal.json `
  --precon automation/tools/fixtures/precon/precon-594-shell-principal-minimal.json `
  --tests automation/tools/fixtures/test_prep/tests-principal-bad-missing-setup.json `
  --epic-dir "$fix/principal-594-pass"

# 594 bad oracle — expect exit 1
python automation/tools/close_verify.py --mode topology --strict-topology `
  --ref epics/CRT-594/CRT-594-ref.json `
  --coverage "$fix/topology-594-oracle-bad-coverage.json" `
  --discover automation/tools/fixtures/discover/discover-594-shell-minimal.json `
  --precon automation/tools/fixtures/precon/precon-594-shell-minimal.json `
  --tests automation/tools/fixtures/test_prep/tests-594-shell-minimal.json `
  --epic-dir "$fix/topology-594-pass"

# Archived CRT-639 legacy — strict topology no-op (no topology_loaded on context artefacts)
python automation/tools/close_verify.py --mode topology --strict-topology `
  --ref epics/CRT-639/context/CRT-639-ref.json `
  --coverage epics/CRT-639/context/CRT-639-coverage.json `
  --discover epics/CRT-639/context/CRT-639-discover.json `
  --precon epics/CRT-639/context/CRT-639-precon.json `
  --tests epics/CRT-639/context/CRT-639-tests.json `
  --epic-dir epics/CRT-639
```

## Related

- Topology contract: [docs/close-topology-contract.json](../../../../docs/close-topology-contract.json)
- Principal contract: [docs/close-principal-contract.json](../../../../docs/close-principal-contract.json)
- Upstream chains: [fixtures/precon/](../precon/), [fixtures/test_prep/](../test_prep/), [fixtures/discover/](../discover/)
