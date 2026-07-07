# CRTQA console gate — Linux CI (dxCity / OpenSSH)

**Full pipeline context:** [automation/CI/README.md](../CI/README.md) (Dispatch, Pipeline steps, Jira, artifacts).

Headless **console gate** (Pipeline step 6) and **GROUND preflight** on **Linux build agents** (`dxAgent*`). Windows desktop flow (`/crtqa-console start` + PuTTY multiplex) stays unchanged for local IDE work.

## Problem

`crtqa_console_probe.py` on Linux called `pwsh` + `Get-CrtqaConsoleStatus.ps1`, which expects a **Windows multiplex session** on the same host. dxCity agents are Linux → gate always failed.

## Solution

**Transport `openssh`**: one-shot SSH from the agent to `ctqa.prosp.devexperts.com`, `sudo su - ctqa`, pipe commands into `dx run console` (same remote bash as `Invoke-CrtqaDxConsole.ps1`).

| Component | Path |
|-----------|------|
| OpenSSH probe | `automation/tools/crtqa_console_openssh.py` |
| Router | `automation/tools/crtqa_console_common.py` (`CRTQA_CONSOLE_TRANSPORT` / auto on Linux) |
| CLI gate | `automation/tools/crtqa_console_probe.py` |
| TeamCity wrapper | `automation/tools/teamcity/console-gate-wrapper.sh` |
| CRTQA env helper | `automation/tools/teamcity/crtqa-openssh-env.sh` |
| Standalone step script | `automation/tools/crtqa-console/ci-gate-step.sh` |

Pipeline wiring (step numbers, GROUND env): [automation/CI/pipeline-steps.md](../CI/pipeline-steps.md).

## One-time setup

### 1. Service SSH key

On a secure machine (not committed to git):

```bash
ssh-keygen -t ed25519 -f crtqa-ci -C "dxcity-corner-qa-console" -N ""
```

Add **`crtqa-ci.pub`** to `~/.ssh/authorized_keys` on CRTQA for the Linux login used for automation (e.g. shared service user). Confirm VPN/network from **dxAgent** to `ctqa.prosp.devexperts.com:22`.

### 2. Sudo password (TeamCity secret)

The remote bootstrap uses `sudo -S su - ctqa` (same as desktop tooling). Store the **SSH user's sudo password** as TeamCity password parameter **`CRTQA_SUDO_PASSWORD`**.

If infra provides **passwordless** `sudo su - ctqa` for the service user, leave `CRTQA_SUDO_PASSWORD` empty and ask for a small harness patch (not in v1).

### 3. TeamCity parameters

Create on **Console Gate** test build and on **Corner Epic QA Pipeline** (steps 6 and 7):

| Parameter | Type | Notes |
|-----------|------|--------|
| `CRTQA_CONSOLE_TRANSPORT` | text | `openssh` |
| `CRTQA_SSH_USER` | text | Linux login on CRTQA (overrides config `sshUser`) |
| `CRTQA_SSH_PRIVATE_KEY_B64` | password | Base64 of PEM file (one line) — **only** key param in CI script |
| `CRTQA_SUDO_PASSWORD` | password | Sudo password for SSH user |

**Encode key on Windows (PowerShell):**

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.ssh\crtqa-ci")) | Set-Clipboard
```

Paste into **`CRTQA_SSH_PRIVATE_KEY_B64`** (password parameter). Do **not** add `%CRTQA_SSH_PRIVATE_KEY%` to the build script — TeamCity auto-creates required parameters from every `%…%` token in the step text.

Optional: `CRTQA_SSH_HOST`, `CRTQA_SUDO_UNIX_USER` (default `ctqa`), `CRTQA_REMOTE_DX_COMMAND` (default `dx run console`).

**VPN / MTU workaround (Windows laptop):** if manual `ssh` needs cipher options, either rely on the built-in Windows defaults in `crtqa_console_openssh.py`, or set:

```bash
export CRTQA_SSH_EXTRA_OPTS="-o MACs=hmac-sha2-256 -o Ciphers=aes256-ctr"
```

Linux dxCity agents usually need no extra opts; set the same env var only if the agent log shows `Corrupted MAC on input`.

Defaults otherwise come from `automation/tools/crtqa-console/crtqa-console.config.json`.

## Standalone test build (recommended before full Pipeline)

Create **`Corner Epic QA Console Gate`** under QA Tooling:

1. **No VCS required** if you paste the script; or attach same Stash VCS root (`team`) after pushing harness changes.
2. **One build step** — Command Line — run [`console-gate-wrapper.sh`](../tools/teamcity/console-gate-wrapper.sh) from harness checkout, or paste [`ci-gate-step.sh`](../tools/crtqa-console/ci-gate-step.sh).
3. Fill parameters above.
4. **Run** — expect exit **0** and log line `Console gate OK` / `openssh + dx show console_guide OK`.

Green gate → same env is used in Pipeline step 6 and sourced again for GROUND step 7.

## Local smoke (Linux or WSL with VPN)

```bash
export CRTQA_CONSOLE_TRANSPORT=openssh
export CRTQA_SSH_KEY_PATH="$HOME/.ssh/crtqa-ci"
export CRTQA_SSH_USER="your-user"
export CRTQA_SUDO_PASSWORD="..."
python3 automation/tools/crtqa_console_probe.py --format both
```

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| `CRTQA_SUDO_PASSWORD not set` | Add TeamCity password parameter |
| `CRTQA_SSH_PRIVATE_KEY_B64` / invalid PEM | Re-encode key; one line, no spaces |
| Spurious `name` parameter in TeamCity | Remove old build step; never put example `%tokens%` in script comments |
| `SSH echo failed` | VPN, firewall, wrong user, key not in authorized_keys |
| `dx probe exit N` | Wrong sudo password, `ctqa` user missing, `dx` not on PATH |
| `too little stdout` | Console hung or auth failed silently — check stderr in `temp/crtqa-console/gate-status.json` on agent |
| GROUND fails after green gate | GROUND step did not source `crtqa-openssh-env.sh` — see [pipeline-steps.md](../CI/pipeline-steps.md) |

## Security

- Never commit keys or passwords to Stash.
- TeamCity password parameters are masked in logs; script deletes temp key file after run.
- Rotate service key if leaked.
