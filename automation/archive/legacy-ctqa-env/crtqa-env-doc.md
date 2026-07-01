# CTQA environment probe (`crtqa_env_probe.py`)

Epic-agnostic **read-only** checks for CTQA Postgres + dxCore console.

## When to use

| Use case | Env required? |
|----------|---------------|
| **`GROUND:`** console probes | Yes |
| **`/epic-helper`** cold start (env gate) | Yes |
| Manual test execution | Yes |
| **`TEST-PREP:`** scenario_intent generation | **No** |
| **`TEST-DISCOVER:`** linker | **No** |

## Gates (always probed)

| Gate ID | Check | Pass |
|---------|-------|------|
| `postgres_ctqa_tunnel` | TCP `127.0.0.1:15432` (or `CTQA_LOCAL_PG_PORT`) | Port accepts connection |
| `crtqa_dx_console_session` | [`Get-CrtqaConsoleStatus.ps1`](../tools/crtqa-console/Get-CrtqaConsoleStatus.ps1) | `session.active.json`, master PID, `crtqa_multiplex_ok` echo |

**Postgres MCP** is not probed here — use tunnel README + Cursor MCP reload.

## Usage

From repo root:

```powershell
python automation/tools/crtqa_env_probe.py
python automation/tools/crtqa_env_probe.py --coverage epics/CRT-639/CRT-639-coverage.json
python automation/tools/crtqa_env_probe.py --format text
```

- Exit **0** — all gates pass.
- Exit **1** — one or more gates failed.
- JSON on stdout; human checklist on stderr when `--format both` (default).

## Operator flow (GROUND / manual runs)

1. Tab 1: Postgres tunnel — [tunnel/README.md](../tools/tunnel/README.md)
2. **`/crtqa-console start`** — desktop SSH password (human only)
3. **`/crtqa-env`** — agent runs this probe; follow checklist if fail
4. **`GROUND: CRT-639`** or manual test execution

## Cursor

- Slash command: [`.cursor/commands/crtqa-env.md`](../../.cursor/commands/crtqa-env.md)
- Console splits: [`.cursor/commands/crtqa-console.md`](../../.cursor/commands/crtqa-console.md)
- Production chain: [docs/draft-truth-contract.json](../../docs/draft-truth-contract.json)

## Security

No passwords or connection strings in probe output. Recovery text points to slash commands and doc paths only.
