# TEST-PRECON fixtures

Verifier: [`automation/tools/precon_verify.py`](../../precon_verify.py). Doc: [`automation/docs/precon-verify.md`](../../../docs/precon-verify.md).

## Round 1 (topology)

| Fixture | Pairing | Flags |
|---------|---------|-------|
| `precon-594-shell-minimal.json` | `coverage-594-shell-reinforce-minimal`, `discover-594-shell-minimal`, `ref-594-topology-full` | `--strict-topology --md` |
| `precon-639-formula-minimal.json` | `coverage-639-formula-reinforce-minimal`, `discover-639-formula-minimal`, `ref-639-topology-minimal` | `--strict-topology --md` |

## Round 2 (principal)

| Fixture | Pairing | Flags |
|---------|---------|-------|
| `precon-594-shell-principal-minimal.json` | `coverage-594-shell-reinforce-principal-minimal`, `discover-594-shell-principal-minimal`, `ref-594-topology-full` | `--strict-topology --strict-principal --md` |
| `precon-639-formula-principal-minimal.json` | `coverage-639-formula-reinforce-principal-minimal`, `discover-639-formula-principal-minimal`, `ref-639-topology-minimal` | `--strict-principal --md` |
| `precon-principal-bad-missing-provision.json` | same as 594 principal | `--mode principal` → exit **1** |

Contract: [`docs/precon-principal-contract.json`](../../../../docs/precon-principal-contract.json).
