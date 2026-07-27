---
description: Start, status, probe, or stop the multiplexed CRTQA SSH console session.
---

# /crtqa-console

Goal: operator authenticates **once per workstation session** via a desktop dialog; the **agent** reuses multiplexed **PuTTY `plink`** for **status**, **probe**, and **Invoke** batches.

**Default:** `/crtqa-console` with no subcommand = **`start`** (backward compatible).

| User says | Agent runs | Human? |
|-----------|------------|--------|
| `/crtqa-console` or **`start`** | `Start-CrtqaConsoleSession.ps1` | **Yes** — password dialog |
| **`status`** | `Get-CrtqaConsoleStatus.ps1` | No |
| **`probe`** | `Invoke-CrtqaDxConsole.ps1 -Probe` | No |
| **`stop`** | `Stop-CrtqaConsoleSession.ps1` | No |

All commands from **repo root**:

```powershell
pwsh -NoProfile -File automation/tools/crtqa-console/Start-CrtqaConsoleSession.ps1
pwsh -NoProfile -File automation/tools/crtqa-console/Get-CrtqaConsoleStatus.ps1
pwsh -NoProfile -File automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Probe
pwsh -NoProfile -File automation/tools/crtqa-console/Stop-CrtqaConsoleSession.ps1
```

**Prefer dot-source for arbitrary `-Commands` batches** (avoids nested `pwsh -File` splatting `exit` into `-ConfigRoot`):

```powershell
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @('help','exit')
```

## A. Cold session handshake (`start`)

1. Windows **desktop dialog**: operator picks **Environment** (**qa** | **uat**), then enters **Linux / AD-style SSH username + password**.
2. Script resolves `sshHost` / `sudoUnixUser` from `environments.*` in config, starts **`plink … -pwfile TMP -share -batch -N user@host`**, then writes:
   - `temp/crtqa-console/session.active.json` (no secrets; includes `environment`, `sshHost`)
   - `temp/crtqa-console/session-credential.dpapi` (sudo batches)

Optional: `Start-CrtqaConsoleSession.ps1 -Environment uat` pre-selects UAT in the dialog.

| Env | SSH host (default) | sudo user (default) |
|-----|--------------------|---------------------|
| **qa** | `ctqa.prosp.devexperts.com` | `ctqa` |
| **uat** | `ctuat.prosp.devexperts.com` | `ctuat` |

After **`start`**, SSH layer is reusable via **`plink -share`**. **sudo** still uses DPAPI per **Invoke** unless infra grants **NOPASSWD**.
## B. Status and probe (agents)

- **`status`** — read-only; writes `temp/crtqa-console/gate-status.json`; exit 0/1.
- **`probe`** — non-destructive `show console_guide` + `exit` (TEST-DISCOVER Step E depth).

## C. Scripted batches (`Invoke` without subcommand)

Agents may run **`-Commands @('…','exit')`** via dot-source or child `pwsh -Command` wrapper (see README).

Transcripts: **`temp/crtqa-console/invoke-*.log`**.

## D. Tear down (`stop`)

Kills tracked **plink** PID; removes **session.active.json** + **DPAPI credential**.

## Prerequisites

| Requirement | Detail |
|-------------|--------|
| PuTTY **`plink`** | **`crtqa-console.config.json`** / **`crtqa-console.local.json`** |
| Network | VPN/routes to `sshHost` |
| Windows | Desktop session for **`start`** modal |

## Epic-helper preflight

1. **`/crtqa-console start`** (human SSH password)
2. **`python automation/tools/crtqa_console_probe.py`** or **`/epic-helper resume`** after cold-start gate

## Security

- No Cursor IDE secret APIs for SSH password — **`System.Windows.Forms`** when PowerShell launches **`start`**.
- **`temp/crtqa-console/`** is gitignored.

## Docs

[`automation/tools/crtqa-console/README.md`](../../automation/tools/crtqa-console/README.md)
