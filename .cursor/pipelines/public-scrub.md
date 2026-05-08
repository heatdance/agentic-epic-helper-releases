# Pipeline: public scrub / export

**Trigger**: user message starts with **`PUBLIC-SCRUB:`**. Optional tokens on the same line:

- **`version=X.Y.Z`** — set this run’s **export** semver to exactly `X.Y.Z` (must be valid semver: non-negative integers). Next run without `version=` **patch-bumps** from this value (e.g. after `1.2.0` → default next is `1.2.1`).
- **`source=develop`** (default) or **`source=main`** — after checkout of **`release`**, merge **`origin/develop`** or **`origin/main`** into `release` before scrubbing.

**Scope**: **one** public-export commit on **`release`** per completed run. **Router rule**: [`.cursor/rules/pipeline-router.mdc`](../rules/pipeline-router.mdc).

**Hard invariant**: **Do not** apply scrub edits, stage scrub changes, or **commit** scrub results on **`main`** or **`develop`**. Only the branch named **`release`** may receive scrub commits. If the current branch is not `release`, **stop** immediately (see [Preflight](#preflight-blocking)).

**Prerequisite**: Git repo with remotes configured; local `release` branch (create on first use — see [First-time `release` branch](#first-time-release-branch)).

**Outputs** (on `release` only, committed in the same run):

- Sanitized tree per tiers **A–D** below.
- [`docs/public-export-manifest.json`](../../docs/public-export-manifest.json) — version + provenance (see [Manifest](#manifest-docspublic-export-manifestjson)).
- Optional **`.agents/`** tree (vendor-neutral agent config; see [.agents Protocol](https://dotagentsprotocol.com/)).

**Ephemeral**: [`automation/temp/public-scrub/`](../../automation/temp/public-scrub/) — create if needed; **delete recursively** before the final `release` commit. Durable files must **not** reference `automation/temp/public-scrub/` or paths under it.

**Reference on internal branches**: [`docs/public-export-manifest.example.json`](../../docs/public-export-manifest.example.json) documents manifest fields; do not treat it as the live manifest on `release`.

---

## Preflight (blocking)

1. **`git rev-parse --is-inside-work-tree`** — must succeed.
2. **`git branch --show-current`** — must be exactly **`release`**.  
   - If the branch is **`main`** or **`develop`**: **stop**. Tell the operator: checkout or create `release`, merge upstream, then re-run. **Do not** scrub on `main`/`develop` even “just to preview.”
3. **Working tree**: resolve or stash unrelated changes before merging upstream; the final commit should be intentional (scrub + manifest only, plus allowed files).

---

## First-time `release` branch

If **`release`** does not exist locally:

```text
git fetch origin
git checkout -b release origin/develop
```

(Or `origin/main` if policy is to track stable only.) Push when ready:

```text
git push -u origin release
```

Subsequent runs: `git checkout release` then follow [Sync upstream](#sync-upstream).

---

## Sync upstream

After **`git checkout release`**:

```text
git fetch origin
```

Then merge the source branch chosen from the trigger (default **`develop`**):

```text
git merge origin/develop
```

or

```text
git merge origin/main
```

**Merge vs reset**: Prefer **`git merge`** so `release` keeps its own history (including `docs/public-export-manifest.json`). **`git reset --hard origin/develop`** (or `main`) discards `release`-only commits until force-pushed — only use if the team explicitly wants a linear mirror; warn that **`public-export-manifest.json` must be restored** after a hard reset.

Resolve merge conflicts **without** re-introducing internal-only content forbidden by tier C/D.

---

## Semver rules

- **Valid semver** for this pipeline: `MAJOR.MINOR.PATCH` with non-negative integer parts (e.g. `1.0.0`, `0.1.2`).
- If the trigger includes **`version=X.Y.Z`**: `export_version` for this run **is** `X.Y.Z`.
- Else: read **`docs/public-export-manifest.json`** on `release`.  
  - If missing: `export_version` **starts at `1.0.0`**.  
  - If present: **patch increment only** — increment `PATCH` by 1, keep `MAJOR` and `MINOR` unchanged (e.g. `1.2.0` → `1.2.1`).
- After a manual **`version=1.2.0`**, the **next** run without `version=` yields **`1.2.1`**.

Record the chosen version in the manifest **before** the final commit message (see [Manifest](#manifest-docspublic-export-manifestjson)).

---

## Manifest (`docs/public-export-manifest.json`)

On **`release`**, write or update JSON with at least:

| Field | Type | Description |
|--------|------|-------------|
| `schema_version` | integer | Start at **1**; bump only if fields change incompatibly. |
| `export_version` | string | Semver string for this export (see [Semver rules](#semver-rules)). |
| `last_source_branch` | string | `develop` or `main` (from trigger). |
| `last_source_sha` | string | SHA of merged upstream tip (e.g. `git rev-parse origin/develop` after fetch). |
| `last_run_utc` | string | ISO-8601 UTC timestamp when the run finished. |
| `notes` | string (optional) | Short free text; append **V2** command summary (see [V2](#v2-verification-of-verification)). |
| `validation_log` | string (optional) | One-line or short multiline summary: V1/V2 exit codes and blocklist passes. |

**Do not** commit this file to **`main`** or **`develop`** as a live manifest — only the **example** [`docs/public-export-manifest.example.json`](../../docs/public-export-manifest.example.json) lives on internal branches.

---

## Tier A — Keep generic harness

Preserve structure and templates that are product-agnostic:

- [`epics/templates/`](../../epics/templates/) (schemas / `_comment` guidance).
- Playbook **shapes** under [`.cursor/pipelines/`](.) (may later be generalized in tier B text).
- [`epics/templates/tests-ref.json`](../../epics/templates/tests-ref.json) (or neutral replacement), [`docs/dr-ref`](../../docs/dr-ref) (or neutral replacements).
- [`docs/harness-map.json`](../../docs/harness-map.json) only if scrubbed in tier B/C to remove org-specific keyword payloads — otherwise transform, don’t blindly delete.

**Self-check**: templates remain valid JSON where applicable; no broken links introduced in top-level README for retained paths.

---

## Tier B — Replace org-wired configs with examples + generic guides

| Path / topic | Action |
|--------------|--------|
| MCP Postgres / DB in workflows | Replace Corner-only **server id** and **database name** in **committed** examples with **placeholders**. Add or keep a **tool-agnostic** note: SSH tunnel → local port → **readonly** DB role; **MCP** is one integration option; credentials only in user/global config — see internal [`automation/tools/tunnel/README.md`](../../automation/tools/tunnel/README.md) pattern generalized in public README scrub. |
| [`automation/tools/remote-cli/secrets.properties`](../../automation/tools/remote-cli/secrets.properties) | **Remove** from export if present; keep only [`secrets.properties.example`](../../automation/tools/remote-cli/secrets.properties.example) (or equivalent). |
| [`docs/project.json`](../../docs/project.json), [`docs/qa-project.json`](../../docs/qa-project.json) | **Transform** to placeholders: generic Confluence/Jira **shape** without real space IDs, page IDs, or internal hostnames — or replace with `*.example` + minimal stub JSON. |
| Bitbucket / internal remotes in docs | Strip or anonymize; document “set your `default_repo` here” in prose. |

**Self-check**: no real passwords; no `USER:PASSWORD` in URIs; `.example` files clearly labeled.

---

## Tier C — Remove internal artifacts and identifiers

Apply **delete** or **rewrite** per team policy. Minimal default manifest (extend in each run as needed):

| Path / pattern | Action |
|----------------|--------|
| `epics/<REAL_EPIC_KEY>/` (e.g. `CRT-*`, org-specific keys) | **Delete** directories for real epics; keep [`epics/README.md`](../../epics/README.md) + [`epics/templates/`](../../epics/templates/) only unless templates contain secrets. |
| `qa-handoff.md` | **Delete** or replace with neutral `qa-handoff.example.md` (no session history, no internal ticket lists). |
| Internal URLs | Remove `https://jira...internal...`, internal Confluence hosts, etc. |
| Benchmark outputs under [`.cursor/benchmark/`](../../.cursor/benchmark/) — **`coverage-bench/temp/`**, **`test-bench/temp/`**, legacy **`coverage-bench/runs/`**, **`crossref/`** / **`history/`**, hub **`runs/<suite_id>/attempt-*/`**, **`runs/<suite_id>/_aggregate/`**, **`benchmark/history/`**, **`run-results/<run-key>/`** (finalize narratives + **`pipeline-delta-queue.json`**; subtree **gitignored** except template **`README`**) | **Delete** or strip if they embed real ticket keys/secrets. Hub suite root **`runs/<suite_id>/`** prompts + **`_manifest.json`** *may* be committed—scrub if inappropriate for **`release`**. Do **not** expect **`report.md`** under the suite folder; it lives under **`run-results/`**. **Tracked harness** (root **`HOW-TO.md`**, **`pipeline/`**, **`scripts/`**, **`templates/`**, **`data/README.md`**) stays unless contaminated. |
| `.cursor/prompts/` or rules mentioning internal-only scopes | Trim or generalize text while keeping harness behavior describable. |

**Self-check**: `rg` for known internal domains and project keys returns **no** matches in tracked files (see [V1](#v1-verification)).

---

## Tier D — Secrets and credentials

- Ensure **no** committed `secrets.properties`, `.env` with real values, cookies, API tokens, or private keys.
- Block obvious **credential-shaped** strings in scrubbed tree (password assignments, `Bearer ` literals in docs).
- **Git**: confirm no secret files were only gitignored locally but required to be absent on `release` for public clone.

---

## `.agents/` layer (vendor-neutral)

On **`release`**, ensure a portable layout compatible with [.agents Protocol](https://dotagentsprotocol.com/):

```text
.agents/
├── agents.md           # AGENTS.md-compatible project guidelines (neutral product name / placeholders)
├── mcp.json            # example only: generic mcpServers entries with placeholders (no secrets)
├── skills/             # optional: minimal skill stubs or pointers
├── agents/             # optional sub-agent profiles
├── tasks/              # optional
└── memories/           # optional; omit or empty for public-safe default
```

- **`agents.md`**: summarize build/test conventions and “configure MCP externally”; point readers at `~/.agents/` and workspace `.agents/` merge order.
- **`mcp.json`**: JSON with **placeholder** commands/URLs; document that real config merges from global `~/.agents/mcp.json`.

Do **not** duplicate secrets into `.agents/mcp.json`.

---

## V1 — Verification

Run from repo root on **`release`** working tree **before** commit (adjust patterns to match your org’s blocklist):

1. **Forbidden paths** — must not exist if policy says delete:

   ```text
   rg --files -g 'secrets.properties' .
   ```

   (Expect **no** matches, or only under `*.example` if allowed.)

2. **Internal host / URL patterns** (examples — extend):

   ```text
   rg -n "jira\\.in\\.devexperts|confluence\\.in\\.devexperts" . --glob '!*.example' --glob '!public-scrub.md'
   ```

3. **Real epic dirs** (example pattern):

   ```text
   rg --files -g 'epics/CRT-*/*' .
   ```

4. **Allowlist sanity**: [`README.md`](../../README.md), [`AGENTS.md`](../../AGENTS.md) or [`.agents/agents.md`](../../.agents/agents.md), templates under `epics/templates/` still present if tier A requires.

**Failure**: fix tree; do not commit until V1 passes.

---

## V2 — Verification of verification

1. Record V1 commands and **exit codes** (all zero) in `validation_log` or `notes` in the manifest.
2. **Clean-room**: add a **temporary git worktree** at a sibling path, checkout **`release`** at the **commit you are about to push** (or re-run V1 after `git commit` on `release` in a fresh clone):

   ```text
   git worktree add ../cursor-corner-public-verify release
   cd ../cursor-corner-public-verify
   ```

3. Re-run the **same** V1 `rg` / checks from the worktree root.
4. Remove worktree when done:

   ```text
   cd -
   git worktree remove ../cursor-corner-public-verify
   ```

5. Append V2 confirmation to **`validation_log`** / **`notes`** in `docs/public-export-manifest.json`.

---

## Commit and push (release only)

1. Delete **`automation/temp/public-scrub/`** if it exists.
2. Stage scrubbed changes + **`docs/public-export-manifest.json`** + **`.agents/**`*.
3. Commit message convention: **`public-export: X.Y.Z`** (use `export_version`).
4. **`git push origin release`**.

**Optional**: tag **`vX.Y.Z`** on the same commit (`git tag v1.2.3 && git push origin v1.2.3`) if the team uses tags for exports.

---

## Abort criteria

- Current branch ≠ `release`.
- Merge upstream cannot be completed without violating tier C/D.
- V1 or V2 fails and cannot be remediated in the same run.

Document reason in operator chat; do not half-commit scrub to `release`.

---

## Phases checklist (complete in order)

| # | Phase | Done when |
|---|--------|-----------|
| 0 | Preflight | On `release`; clean enough to merge |
| 1 | Sync upstream | Merged `origin/develop` or `origin/main` |
| 2 | Tier A | Generic harness preserved |
| 3 | Tier B | Examples + generic DB/MCP story |
| 4 | Tier C | Internal trees/URLs/keys removed per manifest |
| 5 | Tier D | No secrets |
| 6 | `.agents/` | Neutral `agents.md` + example `mcp.json` |
| 7 | Semver + manifest | `export_version` and provenance written |
| 8 | V1 | Blocklist/allowlist checks pass |
| 9 | Commit | Single commit on `release` |
| 10 | V2 | Worktree re-run passes; manifest updated |
| 11 | Push | `origin release` (+ optional tag) |

---

## Downstream

Consumers clone **`release`** (or a tag). They copy **`.agents/mcp.json`** patterns to `~/.agents/mcp.json`, fill **`docs/project.json`** (or local equivalents), and use any editor that reads **AGENTS.md** / **`.agents/agents.md`**.

Internal feature work stays on **`develop`** / **`main`**; re-run **`PUBLIC-SCRUB:`** on **`release`** after merges.
