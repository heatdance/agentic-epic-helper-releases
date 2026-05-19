# CRT-642 — Requirement analysis (v2)

## Gaps

- `gap-001` [high] nested_req_unresolved — — — Nested requirement CRT-1481 is referenced from CRT-1750 snippet text but coverage nested_requirement_refs leaves page_id… — action: confluence_resolve
- `gap-002` [high] deferred_check — chk-015 — Chart default trading-hours-only visibility remains calculation_contract deferred_ambiguous (DxFeed dependency); pass/fa… — action: ignore_for_discover
- `gap-003` [high] nested_req_unresolved — — — Stash code search returns HTTP 404; implementation evidence is browse/layout anchors only, not symbol-level validation c… — action: rerun_coverage

## Actions

- rerun_coverage: no
- rerun_epic_prep: no
- focus_hint: null
- human: Resolve CRT-1481 via Confluence for schedule preconditions (chk-002, chk-016)
