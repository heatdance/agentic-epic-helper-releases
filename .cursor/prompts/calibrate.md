# Prompt scaffold: calibrate subprocess

Use with **`/crtqa-calibrate`** after **`compare`** JSON is available.

## Inputs

- **Epic key:** <!-- -->
- **Compare report:** `.cursor/calibrate/reports/<KEY>-compare.json`
- **`outcome`:** <!-- NO_ACTIONABLE_DELTA | DELTA_REVIEW -->

## If `NO_ACTIONABLE_DELTA` or `GOLD_NOT_DISTINCT`

**Do not** run decision-map deep dive or emit harness lessons.

```markdown
## BLUF
Calibrate complete: **no harness changes recommended**. Gold and production align on all mechanical compare signals (or gold was not distinct — stop earlier).

## Compare summary
(paste `signals[]` where actionable is false)

## Epic debt (optional, not harness)
- (only if you observed temp/, CLOSE info, etc. — not lesson_record)

## Questions
- (optional)
```

## If `DELTA_REVIEW`

Load compare JSON; **`jq`** prod/gold slices per [automation/docs/jq.md](../../automation/docs/jq.md).

Each lesson **must** cite `diff_evidence.signal_id` from compare report.

```markdown
## BLUF

## Compare signals (actionable)
| signal_id | detail |
|-----------|--------|

## Prioritized suggestions (max 3)
1. [target: verifier|contract|playbook|coverage_norm] … **evidence:** signal_id, check_id/bundle_id

## Epic debt (not harness)
- …

## Lesson records
[ { "id": "...", "diff_evidence": { "signal_id": "check_ids", "path": "..." }, ... } ]

## Questions
```

**Forbidden:** suggestions without an actionable `compare.signals[]` entry.
