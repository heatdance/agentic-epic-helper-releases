# QA End Date Structure column

One **Formula** column **QA End Date** (replaces Epic MAX column + **Ticket ED** field column).

| Setting | Value |
|---------|--------|
| Structure variable | **EndDate** → Jira **End Date** |
| Column format | **General** or **Text** (dates or literals `done` / `aborted`) |
| Sum over sub-items | **OFF** |

## QA Task / Test Execution row

| Status | Display |
|--------|---------|
| Closed | `done` |
| Aborted | `aborted` |
| Other | End Date |

## Epic row (direct children only)

Uses `COUNT#children` / `MAX#children` over QA Task and Test Execution children.

| Condition | Display |
|-----------|---------|
| No QA Task or Test Execution child | blank |
| At least one child not Closed and not Aborted | **Latest** End Date among open children only |
| All children Aborted | `aborted` |
| All children Closed | `done` |
| Mix of Closed + Aborted only (no open children) | `done` |

Other rows: blank.

## Deploy

1. Paste [`versions/v1/formula.expr`](versions/v1/formula.expr) into the column formula.
2. Map Structure variable **EndDate** to Jira **End Date**.
3. Remove superseded Epic MAX and Ticket ED columns.

If QA tickets are not direct Epic children, switch `#children` to `#subtree` in the formula (document any board-specific change in a new version folder).

Version registry: [`versions-manifest.json`](versions-manifest.json).
