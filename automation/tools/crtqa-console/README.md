# crtqa-console — multiplex SSH + scripted `dx`

Windows-first tooling to reach **`dx run console`** on CRTQA hosts using **PuTTY `plink`** without committing secrets. Agent-facing workflow, truth hierarchy, and Confluence trust levels: **[docs/dxcore-console-harness.json](../../../docs/dxcore-console-harness.json)** (T1 **`dxcore_console`** in [docs/harness-map.json](../../../docs/harness-map.json)).

## Paths (recommended)

| Script | Audience | Purpose |
|--------|----------|---------|
| **`Start-CrtqaConsoleSession.ps1`** | Operator + agent (`/crtqa-console start`) | One desktop dialog (**username + password**), multiplex upstream (`plink -share -N`), stash **sudo** credential via Windows **DPAPI** under `temp/crtqa-console/`. |
| **`Get-CrtqaConsoleStatus.ps1`** | Agents | Read-only session + PID + multiplex echo; writes `temp/crtqa-console/gate-status.json`. |
| **`Invoke-CrtqaDxConsole.ps1`** | Agents | Run non-interactive `dx` batches over **`plink -share`**; **`-Probe`** for bounded `show console_guide`; append `invoke-*.log`. |
| **`Stop-CrtqaConsoleSession.ps1`** | Operators / teardown (`/crtqa-console stop`) | Kill upstream **`plink`** PID + delete state + credential blob. |
| **`Enter-CrtqaConsole.ps1`** | Operator only | Opens an interactive TTY/`dx`; no multiplex bookkeeping. Prefer **Start/Invoke** for cold sessions.

## Prerequisites

1. **PuTTY** `plink.exe` (default location in **`crtqa-console.config.json`**).  
2. Optional **`crtqa-console.local.json`** (copy from **`crtqa-console.local.json.example`**; gitignored overrides).  
3. Network/VPN for `sshHost`.

## Typical cold session

```powershell
# 1 operator modal (Environment qa|uat + username + password):
pwsh -NoProfile -File automation/tools/crtqa-console/Start-CrtqaConsoleSession.ps1
# optional pre-select UAT in the dialog:
pwsh -NoProfile -File automation/tools/crtqa-console/Start-CrtqaConsoleSession.ps1 -Environment uat

# 2 agent batches (SSH reuse via multiplex; sudo uses DPAPI per call).
# From repo root — either dot-source in the *current* pwsh (array syntax safe):
. ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @('help','exit')
# Or spawn a child pwsh without splatting `exit` into -ConfigRoot (nested -File quirk):
pwsh -NoProfile -Command "& { Set-Location '$PWD'; . ./automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Commands @('help','exit') }"
```

Hosts / sudo users come from **`environments.qa`** / **`environments.uat`** in **`crtqa-console.config.json`** (override fields in **`crtqa-console.local.json`**). Session state records `environment` + `sshHost` in `session.active.json`.
Status (agents, no password dialog):

```powershell
pwsh -NoProfile -File automation/tools/crtqa-console/Get-CrtqaConsoleStatus.ps1
```

Bounded console probe (TEST-DISCOVER Step E):

```powershell
pwsh -NoProfile -File automation/tools/crtqa-console/Invoke-CrtqaDxConsole.ps1 -Probe
```

Cleanup:

```powershell
pwsh -NoProfile -File automation/tools/crtqa-console/Stop-CrtqaConsoleSession.ps1
```

Slash commands: [`.cursor/commands/crtqa-console.md`](../../../.cursor/commands/crtqa-console.md) (`start` | `status` | `probe` | `stop`). Console gate: [`crtqa_console_probe.py`](../crtqa_console_probe.py) (epic-helper + GROUND).

**Linux CI (dxCity):** OpenSSH transport on build agents — [automation/CI/README.md](../../CI/README.md) (full pipeline) · [automation/docs/crtqa-console-ci.md](../../docs/crtqa-console-ci.md) (console gate only).

## Security / limitations

| Topic | Notes |
|------|-------|
| “Cursor modal” | Slash commands execute markdown + scripts; **`System.Windows.Forms`** is the safest built-in masking dialog unless you publish a Cursor extension exposing `showInputBox`. |
| Credential files | **`session.active.json`** (state) + **`session-credential.dpapi`** (encrypted password blob) stay under **`temp/crtqa-console/`** (ignored by Git); readable only under the signing-in Windows profile. |
| sudo cost | **`Invoke`** unwraps DPAPI once per invocation; infra can still add **`NOPASSWD`** for narrower automation. |
| Console limits | Scripted batches run **dumb TTY (`-batch`)** pipelines—some human-only interactions may refuse; transcripts capture stdout/stderr. |

## Older notes

Interactive-only guidance + OpenSSH quirks live in **`Enter-CrtqaConsole.ps1`** comments.

For long-term unattended automation favour **SSH keys** + audited `sudoers` instead of password reuse.
