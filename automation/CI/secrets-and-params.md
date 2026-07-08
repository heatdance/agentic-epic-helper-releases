# Secrets and TeamCity parameters

Never commit tokens, PATs, SSH private keys, or sudo passwords to git. Store as TeamCity **password** parameters (masked in logs).

## Dispatch parameters

| Name | Type | Purpose |
|------|------|---------|
| `JIRA_API_TOKEN` | password | Jira REST Bearer PAT |
| `PIPELINE_BUILD_TYPE_ID` | text | Target Pipeline build type id |
| `DISPATCH_LOOKBACK_MINUTES` | text | Jira search window (minutes) |
| `TRIGGER_PHRASE` | text | Substring match in comment body |
| `TC_REST_TOKEN` | password | dxCity REST token (queue build) |
| `TC_SERVER_URL` | text | Optional; default `https://dxcity.in.devexperts.com` |

## Pipeline parameters

| Name | Type | Purpose |
|------|------|---------|
| `EPIC_KEY` | text | e.g. `CRT-671` — from Dispatch or manual Run |
| `QA_TASK_KEY` | text | e.g. `CRTQA-10241` |
| `COMMENT_ID` | text | Jira comment id (empty OK on manual Run) |
| `CURSOR_API_KEY` | password | Cursor SDK / agent API |
| `JIRA_API_TOKEN` | password | **Single PAT** — Jira comments **and** Atlassian MCP (`JIRA` / `CONFLUENCE` / `BITBUCKET` tokens) |
| `AGENT_MAX_WAIT_MINUTES` | text | Per agent step wait timeout; default **`45`** |
| `CRTQA_CONSOLE_TRANSPORT` | text | `openssh` |
| `CRTQA_SSH_USER` | text | SSH login on CRTQA host |
| `CRTQA_SSH_PRIVATE_KEY_B64` | password | Base64-encoded PEM (single line) |
| `CRTQA_SUDO_PASSWORD` | password | Sudo password for `su - ctqa` |

Optional overrides: `CRTQA_SSH_HOST`, `CRTQA_SUDO_UNIX_USER`, `JIRA_BASE_URL`, `ATLASSIAN_MCP_JIRA_URL`, `ATLASSIAN_MCP_CONFLUENCE_URL`, `ATLASSIAN_MCP_BITBUCKET_URL`.

### Build settings (operator)

| Setting | Recommended |
|---------|-------------|
| **Build timeout** | **180 min** (four agent steps + verifiers; EPIC-PREP often exceeds 90 min) |
| Dispatch `DISPATCH_LOOKBACK_MINUTES` | **`120`** (hourly cron can miss comments with small lookback) |

### Agent host prerequisites (dxAgent pool)

| Tool | Purpose | Bootstrap |
|------|---------|-----------|
| `python3` 3.10+ | Verifiers + `cursor-sdk` | required on image |
| `jq` | Harness playbooks / JSON inspection | required on image (no self-install) |
| `curl` or `wget` | Install `uv` on first build | required on image |
| `uv` / `uvx` | `mcp-atlassian-with-bitbucket` | **auto-installed** by step 1 [`bootstrap-agent-env.sh`](../tools/teamcity/bootstrap-agent-env.sh) to `$HOME/.local/bin` |
| Network | Jira, Confluence, Stash, Cursor API, astral.sh | required |

Step 1 also installs **`cursor-sdk`** via pip and warms the MCP wheel cache. Later steps source the same bootstrap marker (`.teamcity-ci/bootstrap.env`) so each fresh TeamCity shell gets the correct `PATH` and `UVX_BIN`.

## Encode SSH key (Windows PowerShell)

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.ssh\crtqa-ci")) | Set-Clipboard
```

Paste into **`CRTQA_SSH_PRIVATE_KEY_B64`** only.

## Jira authentication

Use **Bearer** PAT in `Authorization: Bearer {token}` — Basic auth with username/password returned 401 in v1 testing.

## Anti-patterns (TeamCity)

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `%CRTQA_SSH_PRIVATE_KEY%` in script comments | Spurious required parameter | Use **B64 param only**; remove stray `%tokens%` |
| Multiline PEM in password field | SSH «invalid key» | Use B64 single line |
| `%Y-%m-%d` in Python inside build step | Phantom parameters / broken script | Use `fromisoformat` — see [dispatch.md](dispatch.md) |
| Wrong `PIPELINE_BUILD_TYPE_ID` | Dispatch logs QUEUE but no Pipeline | Copy id from Pipeline → General settings |

## CRTQA env sourcing

Steps 6 and 7 source [`crtqa-openssh-env.sh`](../tools/teamcity/crtqa-openssh-env.sh):

- Decodes B64 to temp key file (deleted on EXIT)
- Sets `CRTQA_SSH_KEY_PATH`, `CRTQA_SUDO_PASSWORD`, `CRTQA_CONSOLE_TRANSPORT`

GROUND agent step **must** source this before Cursor agent — otherwise `runtime_probes` fail (console checks need OpenSSH env).

## Rotation

- Rotate Jira PAT and TeamCity token on schedule or leak.
- Rotate CRTQA service SSH key: generate new keypair, update `authorized_keys`, re-encode B64, update TeamCity param.
