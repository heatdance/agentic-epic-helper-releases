# EPIC-PREP — mechanical verifier

Gate **`-ref.json`** schema v4 **`obligations_proposed[]`**. Playbook: [`.cursor/pipelines/epic-prep.md`](../../.cursor/pipelines/epic-prep.md). Kinds: [`docs/epic-obligation-kinds.json`](../../docs/epic-obligation-kinds.json).

## CLI

**Before finalize (step 8):**

```powershell
python automation/tools/epic_prep_verify.py --mode ref `
  --ref epics/CRT-639/CRT-639-ref.json
```

**After reconcile subprocess (step 6b):**

```powershell
python automation/tools/epic_prep_verify.py --mode reconcile `
  --ref epics/CRT-639/CRT-639-ref.json
```

Exit **0** = pass. Max **2** reconcile iterations on failure per playbook.

## Modes

| Mode | Checks |
|------|--------|
| **ref** | `schema_version` ≥ 4; obligations shape; snippet finalize gate; no `/temp/`; no CRTQA keys |
| **reconcile** | **ref** checks + `obligations_reconcile.epic_summary_aligned`; primary obligations reviewed |
