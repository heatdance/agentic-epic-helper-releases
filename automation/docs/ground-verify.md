# GROUND verifier (`ground_verify.py`)

Contract: [docs/ground-contract.json](../../docs/ground-contract.json). Playbook: [`.cursor/pipelines/ground.md`](../../.cursor/pipelines/ground.md).

## Emit

```powershell
python automation/tools/ground_verify.py --mode emit `
  --coverage automation/tools/fixtures/ground/ground-594-pass-coverage-slice.json `
  --ref automation/tools/fixtures/epic-prep/ref-594-topology-full.json
```

**Exit 0** when every console-tagged primary check has **`runtime_probes[]`** or **`probe_waived`** + **`waiver_reason`**; no **`temp/`** paths in durable JSON.
