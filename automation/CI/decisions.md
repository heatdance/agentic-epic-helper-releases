# Decisions — Corner Epic QA CI v1

ADR-style record of v1 scope. Change via operator entrust + doc update.

## D1 — Trigger on CRTQA comment, not CRT epic

**Decision:** Dispatch watches **CRTQA** tasks for comment **`Agent: Coverage`**. Epic key parsed from QA task **summary** (`CRT-\d+`).

**Rationale:** Corner QA workflow assigns CRTQA tasks per epic; Epic Link field not reliably populated.

**Status:** Accepted, verified in production Dispatch logs.

---

## D2 — Chain stops at ANALYSE

**Decision:** CI runs **EPIC-PREP → COVERAGE → Console gate → GROUND → ANALYSE** only.

**Out of scope v1:** TEST-DISCOVER, TEST-PREP, CLOSE, `COVERAGE fix_breadth=yes`, human `coverage_frozen_at` / `scenario_groups[]`.

**Rationale:** Unattended first pass delivers coverage + analysis drafts; human review and test prep stay in IDE `/epic-helper` or manual pipelines.

**Status:** Accepted.

---

## D3 — Jira comment only, no REST attachment

**Decision:** Success/fail feedback via **Jira comment** pointing to TeamCity **`epic-work`** artifacts. No Jira REST file attach.

**Rationale:** Operator PAT received HTTP 403 on attach API; manual UI attach works but is not automatable with current token scope.

**Status:** Accepted v1; revisit if Jira admin grants attachment scope.

---

## D4 — TeamCity REST queue, not runBuild service message

**Decision:** Dispatch uses `POST /app/rest/buildQueue` with Bearer `TC_REST_TOKEN`.

**Rationale:** `##teamcity[runBuild ...]` logged QUEUE but did not enqueue Pipeline in dxCity 2026.1 testing.

**Status:** Accepted.

---

## D5 — OpenSSH console transport on Linux agents

**Decision:** Pipeline console gate and GROUND use **`CRTQA_CONSOLE_TRANSPORT=openssh`** and B64 SSH key — not Windows PuTTY multiplex.

**Rationale:** dxCity agents are Linux; desktop `/crtqa-console` flow is Windows-only.

**Status:** Accepted; see [crtqa-console-ci.md](../docs/crtqa-console-ci.md).

---

## D6 — Dedup at Dispatch by comment id

**Decision:** `CRTQA-xxxx#commentId` in `processed_comment_ids.txt`; Pipeline does not dedup.

**Rationale:** One Pipeline per triggering comment; manual Pipeline bypasses Dispatch.

**Status:** Accepted.

---

## D7 — Documentation tier personal + team only

**Decision:** `automation/CI/**`, `automation/tools/teamcity/**`, and `automation/docs/crtqa-console-ci.md` **deleted on public** export.

**Rationale:** Internal dxCity/Stash/CRTQA operational detail not needed in public guide export.

**Status:** Accepted — encoded in [clean-publish-tier-matrix.json](../../docs/clean-publish-tier-matrix.json).

---

## D8 — Stash `AI/agentic-feature-helper` branch `team` as CI checkout

**Decision:** TeamCity VCS checks out Stash **`team`**, not GitHub team mirror.

**Rationale:** dxCity integrated with internal Stash; harness pushes via `git push stash`.

**Status:** Accepted.

---

## D9 — MCP + project rules mandatory for CI agents

**Decision:** Pipeline agent steps use [`run_pipeline_agent.py`](../tools/teamcity/run_pipeline_agent.py) with **inline** `user-mcp-atlassian` stdio MCP and `setting_sources=["project"]`. Step 1 bootstraps gitignored `.cursor/mcp.json` and Jira smoke. Single **`JIRA_API_TOKEN`** PAT feeds MCP and Jira comment scripts.

**Rationale:** Bare `Agent.prompt` + `LocalAgentOptions(cwd=…)` only did not load `.cursor/rules/` (pipeline-router) or Atlassian MCP; playbooks require MCP for Jira/Confluence/Bitbucket. `status: finished` without `epics/<KEY>/*` was a false green before `--require` post-checks.

**Status:** Accepted (MCP patch).

---

## Deferred / revisit

| Item | Notes |
|------|-------|
| Jira attachment API | Needs PAT scope or app user |
| Stash repo visibility | Infra / AI project admins |
| `fix_breadth` CI loop | Optional Round 2 — not v1 |
| Full `/epic-helper` parity | Requires human gates automation |
