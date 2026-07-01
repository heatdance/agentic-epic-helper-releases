# Legacy CTQA env probe (archived)

**Not used** by draft_truth_v3, `/epic-helper`, or GROUND after console-only gate migration.

Retained for historical reference only.

## Contents

| Path | Was |
|------|-----|
| `crtqa_env_probe.py` | `/crtqa-env` + Postgres tunnel TCP + console multiplex |
| `crtqa_env_common.py` | Shared probe logic |
| `crtqa-env-doc.md` | Former `automation/docs/crtqa-env.md` |
| `tunnel/` | SSH Postgres tunnel + MCP setup docs |

## Active replacement

- Console gate: [`automation/tools/crtqa_console_probe.py`](../../tools/crtqa_console_probe.py)
- Operator command: [`/crtqa-console`](../../../.cursor/commands/crtqa-console.md)
