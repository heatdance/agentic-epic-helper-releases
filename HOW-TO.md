# Corner QA — how to

This repo is a **QA harness** for Corner Trader epics: draft coverage and test plans under `epics/<KEY>/`, then archive when done. Cursor rules load automatically.

**Detail:** [AGENTS.md](AGENTS.md) · [docs/draft-truth-contract.json](docs/draft-truth-contract.json) · [docs/harness-principles.md](docs/harness-principles.md)

**Prerequisites:** **jq** on PATH (`winget install --id jqlang.jq -e` on Windows). Atlassian MCP per [AGENTS.md](AGENTS.md).

---

## Epic workflow (start here)

**Recommended:** run the full chain with the orchestrator:

```text
/epic-helper CRT-1234
/epic-helper resume
```

One pipeline stage runs per agent turn. Full command spec: [`.cursor/commands/epic-helper.md`](.cursor/commands/epic-helper.md).

**What happens (plain English):**

1. **Prepare the epic** — map requirements (`EPIC-PREP`).
2. **Draft the checklist** — Smart Checklist (`COVERAGE`).
3. **Ground console syntax** — live CTQA console probes on coverage (`GROUND`) — **needs console** (`/crtqa-console start`).
4. **Audit gaps** — what's missing or blocked (`ANALYSE`); optional second coverage pass.
5. **You review coverage** — merge toward gold, edit **scenario groups**, freeze coverage (human gate).
6. **Link checks to surfaces** — deterministic map, no browser (`TEST-DISCOVER`).
7. **Draft test plans** — scenario intent, not final CRTQA steps (`TEST-PREP`) — **no env gate**.
8. **Archive** — integrity check + move JSON to `context/` (`CLOSE`).

**When you need the console** (`/crtqa-console start`): **epic-helper** cold start, **GROUND**, and when **you** run tests manually. Not required to **generate** TEST-PREP drafts.

You can run individual triggers (below) without `/epic-helper`.

---

## Pipeline quick reference

One epic per chat. Paste trigger + key on the first line.

| Trigger | Purpose | You need |
|---------|---------|----------|
| `EPIC-PREP:` | Requirement map | Jira key |
| `COVERAGE:` | Smart Checklist | `-ref.json` |
| `GROUND:` | Console probes on coverage | `/crtqa-console start` |
| `ANALYSE:` | Gap audit | `-coverage.json` after GROUND |
| `TEST-DISCOVER:` | Linker map (no browser) | Frozen coverage + `scenario_groups[]` |
| `TEST-PREP:` | Scenario intent test drafts | Frozen coverage; outputs **drafts for humans** |
| `CLOSE:` | Archive + integrity | ref, coverage, discover, tests at epic root |

Playbooks: [.cursor/pipelines/](.cursor/pipelines/) · Layout: [epics/README.md](epics/README.md)

### Legacy (not in default chain)

| Trigger | Note |
|---------|------|
| `TEST-PRECON:` | Calibrate/benchmark only — **not** in `/epic-helper` v4 |
| `COVERAGE-REINFORCE:` | Opt-in pass-2 coverage — conflicts with frozen coverage |

---

## Other slash commands

| Command | Use |
|---------|-----|
| `/crtqa-console start` | Start multiplexed dxCore console (epic-helper + GROUND) |
| `/epic-calibrate` | After CLOSE — compare prod vs gold (optional) |
| `/epic-stats` | Personal TCD stats — [stats/epic-stats/README.md](stats/epic-stats/README.md) |
| `/release-notes` | Release notes from Jira (personal branch) |
| `/clean` | Publish harness (personal → Stash team → public) — **`personal` branch only** |

---

## Maintainer only

**`/clean`** on branch **`personal`** only — publish personal / Stash team / public tiers. [`.cursor/commands/clean.md`](.cursor/commands/clean.md) · [`.cursor/pipelines/clean.md`](.cursor/pipelines/clean.md)

### Stash push (agent / Cursor)

Remote **`team`** → Stash `AI/agentic-feature-helper` (branch `team`). Git needs your SSH key unlocked in **`ssh-agent`**.

1. Once (admin PowerShell): `Set-Service ssh-agent -StartupType Automatic` → `Start-Service ssh-agent`
2. After each reboot / login: `ssh-add $env:USERPROFILE\.ssh\id_ed25519` (passphrase once)
3. Check: `git fetch team` — then you can ask the agent to push to team

Passphrase is **not** remembered across reboot unless you use a separate key without passphrase (optional trade-off). This section is **personal-only** (team HOW-TO is rewritten from templates on `/clean`).
