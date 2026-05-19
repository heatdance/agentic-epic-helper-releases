# TEST-PREP subprocess scaffold (v3 — CRTQA outlines)

**Playbook:** [`.cursor/pipelines/test-prep.md`](../pipelines/test-prep.md)

**Profiles:** [`docs/test-prep-draft-profiles.json`](../../docs/test-prep-draft-profiles.json) · **TBD:** [`docs/test-prep-tbd-contract.json`](../../docs/test-prep-tbd-contract.json)

**Verifier:** [`automation/tools/test_prep_verify.py`](../../automation/tools/test_prep_verify.py) — `plan`, `explore`, `draft`, `merge`, `tests`

## Orchestrator checklist

1. **MUST** `jq` project **`-coverage.json`** (required), **`-precon.json`** (SHOULD — `case_outline`, `session_placeholders`, `command_patterns`), optional **`-discover.json`**, **`-ref.json`** per [automation/docs/jq.md](../../automation/docs/jq.md) before Read; summarize stdout, then load only slices needed for edit/emit.
2. Parse **`draft_profile`** (default `crtqa_outline` = executable outline), optional **`shape_ref=benchmark`** (**only** if both **`benchmark_suite=`** + **`benchmark_attempt=`** on trigger), **`draft_split=`**.
3. Phase **6**: CRTQA Jira search skip.
4. Phase **8a** shells from **`test_skeleton[]`**.
5. **Phase 0** (after 8a): machine + FE creds + **0c smoke only**.
6. Phase **8a½**: plan + **`case_outline[]`** per bundle → `--mode plan` (max 3).
7. Phase **8a¾**: verification exploration per bundle → `--mode explore` (max 2 per bundle).
8. Phase **8b**: draft per bundle **or** per **`check_id`** (split rule); **no** parent-chat one-shot.
9. Phase **8c**: merge per-check drafts → `--mode merge` (**`--plan` required**).
10. **8b-verify** per bundle (`--mode draft` + **`--plan`**); emit → `--mode tests` + **`--plan`** → delete `temp/`.

## Subprocess 8a½ (plan)

- Merge PRECON **`case_outline[]`**; add rows until **`min_case_count`**.
- **`shape_ref=benchmark`**: benchmark mode only — case titles only — **no CRTQA keys** in plan JSON.
- If **`obligations_coverage`** has uncovered **`primary_candidate`**: **`map_only=yes`** or STOP.

## Subprocess 8b (draft)

**Input:** `case_outline[]` slice, `session_placeholders`, `command_patterns`, 8a¾ labels, `results_only_context`.

**crtqa_outline:** one numbered Action/Result **per `case_outline` row**; `command_patterns.ladder_step` lines are **sub-bullets inside** that action (not separate numbered pairs). See **`expansion_policy`** in TBD contract. Ladder templates use `<placeholders>`; forbidden whole-scenario TBD.

**teaching:** legacy illustration_budget cap.

## Subprocess 8c (orchestrator)

Merge `test-prep-draft-<bundle>-<chk>.json` → bundle `draft` ordered by `case_id`.

## Trigger tokens

`draft_profile=teaching`, `shape_ref=benchmark`, `draft_split=per_check|per_bundle`, `dxtrade5_creds=`, `webbroker_creds=`, `fe_exploration_waived=yes`, `proceed`, `skip_cold_gate=yes`, `map_only=yes`, `discover_override=yes`, `benchmark_suite=`, `benchmark_attempt=`
