# Teach lessons — auto-tests smoke

Operator builds the framework; the agent coaches and reviews. **Do not ask the agent to scaffold `tests/` unless you explicitly want a full solution.**

| Lesson | Phase | Topic | Status |
|--------|-------|-------|--------|
| [01 — Roles](lesson-01-roles.md) | Layer 1 | Credentials overlay | Done (`dxtf_bot`) |
| [02 — Spec](lesson-02-phase-0-spec.md) | Phase 0 | Manifest scope + oracle | Done (CRTQA-1692 row) |
| [03 — Fixtures](lesson-03-phase-1-fixtures.md) | Phase 1 | pytest skeleton + wiring | **You build this** |
| 04 — Oracle | Phase 2 | CRTQA-1692 smoke test | Blocked until lesson 03 exit |

Exit criteria per phase: [../specs/schema.json](../specs/schema.json) → `teach_track.phases[]`.
