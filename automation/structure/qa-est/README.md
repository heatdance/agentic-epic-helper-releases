# QA Est Structure column

**QA Est** aggregates estimated effort for QA lane tickets on the Corner Roadmap board. Two formula versions differ only in whether **QA CR** (Test cases review) hours enter the **Epic rollup**.

## Versions

| Version | Path | Rollup lanes | Use |
|---------|------|--------------|-----|
| **v1** (recommended) | [`versions/v1/formula.expr`](versions/v1/formula.expr) | RA, TC, Validation — **excludes CR** | Default view |
| **v2** | [`versions/v2/formula.expr`](versions/v2/formula.expr) | RA, CR, TC, Validation — **includes CR** | Duplicate Structure view |

Paste the matching file into the **QA Est** column on each saved view.

## Ticket-level estimate (`ticket_est`)

| Condition | Value |
|-----------|--------|
| `timespent` > 0 (work logged) | `remainingEstimate` |
| Else `customfield_11250` (draft hours) > 0 | `DURATION(TEXT(draft_h) + "h")` |
| Else | `originalEstimate` |

CR **leaf rows** still show `display_est` in both versions (`in_qa_lane` unchanged); only **`SUM#leaves#strict`** uses `in_qa_lane_agg`.

## Epic scope (both versions)

Epic status must be one of: **Validation**, **Pending Fix**, **Under Implementation**.

Applied on:

- **Status layer:** `epic_in_scope`, `under_scope_epic` (parent), `scope_epics_in_subtree`
- **Label layer:** in-scope Epic branch (`qa-no-task`, slot/incomplete) — logic unchanged
- **PMOPROC layer:** `scope_epics_in_subtree > 0` rollup on folder/parent rows; `show_blank` exclusions unchanged

Leaves count toward sum when: `in_qa_lane_agg`, not Closed/Aborted, not excluded, and parent Epic is **qualified**.

Qualified Epic for layer rollup means:

- status is scoped (**Validation** / **Pending Fix** / **Under Implementation**)
- not labeled `qa-no-task`
- has at least one QA slot (`p_any_slot`)
- is **not** `not defined` or `incomplete` by slot/duplicate/missing-est checks (`NOT p_incomplete`)

This makes layer aggregation ignore Epics that would render `(?) not defined` or `(!) incomplete`.

## Epic row outcomes

| Condition | Display |
|-----------|---------|
| Archive / Fixed Cost / named folder rows | blank |
| `qa-no-task` Epic in scope | blank |
| No RA/CR/TC/Val slot in subtree | `(?) not defined` |
| Missing slot, duplicate TC, or open leaf without estimate | `(!) incomplete` |
| Else | `SUM#leaves#strict` of qualifying `ticket_est` |

Non–in-scope Epic with scoped epics in subtree: subtree `leaf_hours` sum only.

## Deploy

Details: [`metadata.json`](metadata.json). Registry: [`versions-manifest.json`](versions-manifest.json).
