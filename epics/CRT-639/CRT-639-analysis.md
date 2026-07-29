## Gaps

- `gap-001` [high] **deferred_check** — chk-004 / CRT-1738 — CRT-1738 ladder check defers cent-level numeric oracle until XT-7911 (calculation_contract deferred_ambiguous). — action: **ignore_for_discover** (confirmed_gap)
- `gap-002` [high] **deferred_check** — chk-016 / CRT-1738 — Ambiguity section reiterates XT-7911 block on locking CRT-1738 worked-table numerics. — action: **ignore_for_discover** (confirmed_gap)
- `gap-003` [high] **human_ba** — chk-012 / CRT-1738 — CRT-1738 Yogi snippet cites rounding rules for average price, realized PL, and open PL but nested requirement keys are not resolved in coverage nested_requirement_refs. — action: **human_ba** (open)
- `gap-004` [medium] **human_ba** — chk-008 / CRT-1743 — Open P/L check requires documenting mark price source (mid/bid/ask/last) but environment-specific mark path is not specified in coverage or Jira. — action: **human_ba** (open)
- `gap-005` [medium] **human_ba** — chk-002 / CRT-1741 — Functional Configuration procedure to assign WeightedAvg for FX_SPOT is not spelled as executable console/UI steps in coverage (TBD mapping). — action: **human_ba** (open)

## Actions

- rerun_coverage: **False**
- rerun_epic_prep: **False**
- focus_hint: **Structural CRT-1738 ladder + WeightedAvg FX_SPOT metrics; defer locked numerics until XT-7911; resolve rounding nested Yogi keys before hard rounding pass/fail.**
- human_notes: **[]**
