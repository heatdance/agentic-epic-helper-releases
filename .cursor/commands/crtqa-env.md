---
description: Probe CTQA Postgres tunnel + crtqa console multiplex (checklist for TEST-DISCOVER and TEST-PRECON Phase 0)
---

# /crtqa-env

**BLUF:** Run the shared environment probe; print pass/fail checklist. Does **not** start the tunnel or console — operators handle passwords separately.

## Agent action

From repo root:

```powershell
python automation/tools/crtqa_env_probe.py
```

When the user names an epic (or you are in **TEST-DISCOVER** or **TEST-PRECON** Phase 0), add coverage for `required_for_epic` labels:

```powershell
python automation/tools/crtqa_env_probe.py --coverage epics/<KEY>/<KEY>-coverage.json
```

- **Exit 0** — all gates pass → tell the user they are ready for **`TEST-DISCOVER: <KEY>`** or **`TEST-PRECON: <KEY>`** (after `-coverage.json` exists; discover/ref recommended for precon).
- **Exit 1** — one or more gates failed → print **`checklist_markdown`** from stderr (or re-run with `--format text`) and numbered recovery actions from the JSON **`gates[].recovery`** blocks.

## Human gates (agent MUST NOT automate)

| Gate | Human step |
|------|------------|
| Postgres | Start tunnel tab: `python automation/tools/tunnel/ctqa_pg.py USER@host`; configure **`postgres-ctqa`** MCP per [tunnel README](../../automation/tools/tunnel/README.md). |
| Console | **`/crtqa-console start`** — desktop SSH password dialog (~30s). |

On console-only failure, point to **`/crtqa-console start`** — do **not** invoke Start from this command.

## Related

- [automation/docs/crtqa-env.md](../../automation/docs/crtqa-env.md)
- Console splits: [crtqa-console.md](crtqa-console.md)
- Playbook Phase 0: [test-discover.md](../pipelines/test-discover.md), [test-precon.md](../pipelines/test-precon.md)
