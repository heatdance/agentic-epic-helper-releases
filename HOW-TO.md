# Corner QA — how to run the main processes

This workspace is a **Corner Trader QA harness** for humans and AI agents: prepare epics, draft coverage and tests, and archive artefacts under `epics/<KEY>/`. **Workspace rules load automatically** in Cursor.

**Organization-wide Cursor MCP**: [AI with Cursor](https://confluence.in.devexperts.com/spaces/QAPORTAL/pages/497112528/AI+with+Cursor) on QAPORTAL.

### Operator prerequisites

- **jq** on system **PATH** (`winget install --id jqlang.jq -e` on Windows). [automation/docs/jq.md](automation/docs/jq.md).
- **MCP:** configure `user-mcp-atlassian` per [AGENTS.md](AGENTS.md).

**Detail:** [AGENTS.md](AGENTS.md) · [docs/draft-truth-contract.json](docs/draft-truth-contract.json) · [docs/harness-principles.md](docs/harness-principles.md)

---

## Epic workflow (start here)

**Recommended:** `/epic-helper CRT-1234` then `/epic-helper resume` — one stage per turn. Spec: [`.cursor/commands/epic-helper.md`](.cursor/commands/epic-helper.md).

**Chain:** EPIC-PREP → COVERAGE → GROUND (needs console) → ANALYSE → **you review coverage + scenario groups** → TEST-DISCOVER (linker, no browser) → TEST-PREP (scenario intent drafts, no console) → CLOSE.

**Console** (`/crtqa-console start`): epic-helper cold start, GROUND, and manual test runs — not TEST-PREP generation.

Individual triggers: see pipeline table in [epics/README.md](epics/README.md).

### Legacy (not in default chain)

`TEST-PRECON:`, `COVERAGE-REINFORCE:` — calibrate/benchmark only.

---

## Calibrate (prod vs operator gold)

After **`CLOSE:`** and gold under **`.cursor/calibrate/<KEY>-gold/`** (local, not in repo):

1. **`/epic-calibrate`** in Cursor.
2. Answer questionnaire (epic key).
3. **`NO_ACTIONABLE_DELTA`** = success; **`DELTA_REVIEW`** = discuss harness in separate chat.

**Docs:** [automation/docs/calibrate.md](automation/docs/calibrate.md)
