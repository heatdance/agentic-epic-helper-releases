# CI quality research — CRT-635 (Pipeline build 43)

Date: 2026-07-27.  
Artefacts: `Downloads/QA_Tooling_Corner_Epic_QA_Pipeline_43_artifacts/epic-work/`.  
Scope: research only (no harness patches in this note).

## BLUF

Green build published a stub Smart Checklist because:

1. **Root cause (auth):** TeamCity injects one `JIRA_API_TOKEN` into `JIRA_PERSONAL_TOKEN`, `CONFLUENCE_PERSONAL_TOKEN`, and `BITBUCKET_PERSONAL_TOKEN`. On Data Center that is wrong — Confluence and Stash returned **401**. Jira alone worked.
2. **Amplifier (waivers):** EPIC-PREP self-wrote `deferral_accepted`; verifiers and notify treated the run as success.
3. **Detection gap:** step-1 smoke checks only Jira REST; runner WARN only fires on *zero* MCP calls (here MCP ran and failed auth).

Local Cursor MCP (separate per-app PATs in `.cursor/mcp.json`) successfully reads Confluence page `469053356` and browses Stash `CAN/corner` — so content is reachable with the right tokens.

---

## Evidence from build 43 artefacts

### `dependencies/CRT-635-ref.json`

| Field | Value |
|-------|--------|
| `requirements[]` ×4 | `snippet_status=failed`, `snippet_failure_reason=mcp_export_failed`, empty `snippet_text`, page_ids `469053356` / `474722713` |
| `obligations_proposed` | 5 primary (setup + 4 “card is available”) + 4 `explicit_deferral` for field params |
| `implementation.hits` | `0` (Bitbucket skipped) |
| `validation_log` | see below |

Key `validation_log` entries (agent-authored):

- `3b_snippet_retry`: Confluence via MCP + REST — **all four keys failed (401 authentication)**
- `5b_bitbucket_prep`: **skipped bitbucket_auth_failed (Stash 401 on CAN/corner browse)**
- `6`: XT Confluence search skipped — **Confluence authentication 401**
- `8`: `{ "deferral_accepted": true, … "Confluence PAT invalid (401); …" }`

### `dependencies/CRT-635-coverage.json` / `CRT-635-coverage.md`

- 5 primary checks with stub wording (`card is available` / `details card is available`)
- 4 deferral checks `- ! reason: mcp_export_failed`
- All primary obligations marked `covered` — shape-complete, content-empty

### `dependencies/CRT-635-analysis.json`

- 4× `deferred_check` → `ignore_for_discover`
- 4× `snippet_missing` → `rerun_epic_prep`
- Build still posted Jira **success** (“coverage is ready”)

---

## Probe results

### 1. Auth nature (401 vs 403 vs SSL) — `probe-auth-split`

| Probe | Result |
|-------|--------|
| CI PAT re-hit from this workstation | **Blocked** — `JIRA_API_TOKEN` / Confluence/Bitbucket tokens absent in local shell |
| Build 43 log in ref | Explicit **HTTP 401 authentication** for Confluence (MCP + REST) and Stash browse — not SSL (auth challenge returned), not 403 (permission on valid session) |
| Local MCP `confluence_get_page` page `469053356` | **OK** (full widget DEFINITION content) |
| Local MCP `bitbucket_browse_directory` `CAN/corner` | **OK** (repo tree returned) |

**Conclusion:** Need **per-application PATs** (Confluence + Bitbucket/Stash), not reuse of Jira PAT. Docs currently claim the opposite ([automation/CI/secrets-and-params.md](../CI/secrets-and-params.md) “Single PAT”).

### 2. MCP package token independence — `probe-mcp-token-vars`

Package: `mcp-atlassian-with-bitbucket` 1.0.5 (uv cache).

| Service | Env var(s) | Shared with Jira? |
|---------|------------|-------------------|
| Confluence DC | `CONFLUENCE_PERSONAL_TOKEN` (also `CONFLUENCE_USERNAME`+`CONFLUENCE_API_TOKEN`) | **No** — `mcp_atlassian/confluence/config.py` |
| Jira DC | `JIRA_PERSONAL_TOKEN` | self |
| Bitbucket DC | `BITBUCKET_PERSONAL_TOKEN` | **No** — `mcp_atlassian/bitbucket/config.py` |

`mcp_atlassian/utils/environment.py` checks each service’s PAT env independently. Template [`.cursor/mcp.json.team.example`](../../.cursor/mcp.json.team.example) already uses **separate** `YOUR_*_PAT` placeholders.

CI wiring that collapses them:

- [automation/tools/teamcity/write-mcp-config.py](../tools/teamcity/write-mcp-config.py) — one `token = JIRA_API_TOKEN` → all three
- [automation/tools/teamcity/run_pipeline_agent.py](../tools/teamcity/run_pipeline_agent.py) `_mcp_env()` — same

**Conclusion:** Split tokens in TeamCity **will** work at the MCP layer if CI stops overwriting Confluence/Bitbucket with the Jira value.

### 3. Yogi / cookie path

- Live `yogi_snippet` needs `CONFLUENCE_SESSION_COOKIE` — **not** set in CI.
- Documented CI path: MCP `confluence_get_page` → temp storage export → `yogi_snippet.py --storage-file` ([automation/docs/yogi-url-resolve.md](../docs/yogi-url-resolve.md)).
- With a valid Confluence PAT, MCP alone is sufficient; cookie is optional second channel, not required for the fix.

### 4. Detection signal in runner — `probe-detection-signal`

[run_pipeline_agent.py](../tools/teamcity/run_pipeline_agent.py) `_consume_run_stream`:

- On `tool_call`: logs `name` + `status` (`running` / `completed` / `ERROR`) only
- Does **not** print tool result body / error text
- Counts `tool_error` and `mcp_tool_started`
- Soft WARN only if `mcp_tool_started == 0`
- Does **not** fail the step on `tool_error > 0`

Build 43 pattern: MCP tools **started** (agent retried Confluence), so zero-call WARN would **not** fire; auth failure lived only inside tool results and agent narrative → `validation_log`.

**Implication for future fix:** either

- (A) parse tool error/result text if SDK exposes it on completed/error messages, and fail on `401` / `Unauthorized`, or
- (B) prefer **pre-agent REST smoke** for Confluence + Stash (deterministic, no SDK dependency), and/or
- (C) post-agent gate on ref (`snippet_status` / forbid self-`deferral_accepted` in CI)

Recommend **B + C**; A is optional hardening.

---

## Waiver inventory — `inventory-waivers`

| # | Location | What it allows | OK for interactive? | OK for CI publish? |
|---|----------|----------------|---------------------|--------------------|
| W1 | Agent writes `validation_log[].deferral_accepted=true` | Completes EPIC-PREP when snippets failed | Only if **human** intentionally skips | **No** — self-issued |
| W2 | `epic_prep_verify` honors any `deferral_accepted` | Exit 0 with failed snippets | Yes (manual / calibrate) | **No** without human marker / env opt-in |
| W3 | Playbook epic-prep §8 “human-approved skip” | Same as W1 intent | Yes | CI must not treat agent-only entry as human |
| W4 | `coverage_verify` skips `tag_level_stub_patterns` when snippet ≠ ok | Stubs don’t fail verify when auth failed | Debatable | **No** for CI if goal is usable checklist |
| W5 | ANALYSE `deferred_check` → `ignore_for_discover` | Downstream discover skips deferrals | Yes (honest gap) | Yes — but must not imply success |
| W6 | ANALYSE `snippet_missing` → `rerun_epic_prep` | Correct signal | Yes | Yes — should **block** success notify |
| W7 | `jira_success.py` unconditional “coverage is ready” | Posts success if steps 1–10 green | N/A | **No** when W1–W4 fired |
| W8 | `mcp-smoke.sh` Jira-only | Green step 1 with Confluence dead | N/A | **No** — expand smoke |

Playbook text already says deferral is for “macro unsupported, page unresolved, or **human-approved** skip” — CI agent used it for recoverable **401**, which is a contract misuse.

---

## Recommended policy — `decide-degraded-policy`

**Decision (research recommendation): fail hard early + no self-waiver.**

Preferred package (**fail_after_prep**):

1. **Step 1 smoke:** Confluence REST (known page or `/rest/api/user/current`) + Stash REST with the tokens that MCP will use. Fail in seconds on 401/403.
2. **Split secrets:** `CONFLUENCE_API_TOKEN` / `BITBUCKET_API_TOKEN` (or `*_PERSONAL_TOKEN` params) with optional fallback to `JIRA_API_TOKEN` only for Jira comments; **do not** silently reuse Jira PAT for Confluence/Stash when dedicated params exist — and for DC, dedicated params should be **required** for Pipeline.
3. **CI prep gate:** `epic_prep_verify` (or wrapper) rejects `deferral_accepted` when `snippet_failure_reason` ∈ `{mcp_export_failed, no_cookie}` **or** when `CORNER_CI=1` / `--ci-strict` unless an explicit operator param `ALLOW_SNIPPET_DEFERRAL=yes` is set.
4. **Notify:** `jira_success` must not claim “ready” if any jira-linked requirement has `snippet_status != ok`, or if analysis has `snippet_missing` gaps — route to failure comment / DEGRADED body instead.

**Rejected for default CI:** “green with DEGRADED comment only” — still teaches operators that stub artefacts are acceptable delivery. DEGRADED notify is acceptable **only** as a secondary path behind an explicit opt-in after smoke was waived.

Rationale: user-visible failure of build 43 was not missing gaps in analysis (they existed) — it was **publishing stub coverage as success**. Auth fix alone is necessary but not sufficient without closing W1/W2/W7.

---

## Fix surface map (for next implementation PR — do not apply in this research)

| Layer | Files | Change |
|-------|-------|--------|
| Auth wiring | `write-mcp-config.py`, `run_pipeline_agent.py`, `secrets-and-params.md`, `teamcity-setup.md` | Separate Confluence/Bitbucket tokens |
| Early fail | `mcp-smoke.sh` (+ maybe small Python smoke) | Confluence + Stash probes |
| Honesty gate | `epic_prep_verify.py` and/or teamcity verify wrapper | `--ci-strict` / reject self-waiver on recoverable reasons |
| Optional | `coverage_verify.py` | CI mode: stub patterns fail even without ok snippet when linked keys failed |
| Notify | `jira_success.py` / `jira_failure.py` | Gate on snippet health / analysis gaps |
| Doctrine | `rollout-learnings.md`, ADR D17 | Record incident + decision |

**Out of scope for the auth fix:** regenerating CRT-635 artefacts in-repo; cookie-based Yogi; weakening stub patterns.

**Acceptance for follow-up PR:**

- Smoke fails if Confluence PAT invalid (demonstrable with wrong token).
- With valid three tokens, EPIC-PREP for CRT-635 produces `snippet_status=ok` for the four DXINV keys (or fails verify without self-waiver).
- Success Jira comment does not post when snippets failed.

---

## Hypotheses closed

| ID | Verdict |
|----|---------|
| H1 MCP not called | **Rejected** — MCP called; 401 |
| H2 Yogi/storage path broken in isolation | **Secondary** — never reached usable export due to 401 |
| H3 Agent self-defers + tag-level obligations | **Confirmed** |
| H4 Verifiers skip stubs when snippet failed | **Confirmed** (by design today) |
| H5 Local vs CI harness revision | **Not primary** — same failure mode explained by auth |
| H6 Notify ignores quality | **Confirmed** |

---

## Operator action needed before / with code PR

1. Create Confluence DC PAT + Stash HTTP access token (or confirm org SSO PAT policy).
2. Add TeamCity password params; wire `env.*` (do not commit secrets).
3. Confirm Pipeline “Stop build on failure” remains on so step-1 smoke abort is visible.
