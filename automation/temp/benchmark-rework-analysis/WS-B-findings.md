# WS-B — Isolation semantics (“variance honesty”)

**Date:** 2026-05-08

## Conflict in current documentation

Three ideas coexist:

1. **Suite mechanics** ([`.cursor/benchmark/coverage-bench/pipeline/benchmark-suite.md`](../../../.cursor/benchmark/coverage-bench/pipeline/benchmark-suite.md)): one queue step **per chat message** (`BENCHMARK-NEXT` runs at most one of prep, coverage, validate, finalize). This splits work for **progress tracking** and operator clarity; it does **not** imply a cold LLM context between steps unless the operator uses a fresh chat **per step**.

2. **Variance guidance** ([`.cursor/benchmark/coverage-bench/HOW-TO.md`](../../../.cursor/benchmark/coverage-bench/HOW-TO.md) operator checklist): use a **fresh chat per step** when measuring model variance. Same file + runbook recommend **fresh Composer** per step as an **operator choice** for stochastic isolation.

3. **Realistic workflow coupling**: For a single **attempt**, **EPIC-PREP → COVERAGE** (and optionally **TEST-PREP**) is a **chain** where later phases **should** read outputs of earlier phases in the same attempt. Full cold reset between prep and coverage **within** the same attempt would force re-fetching Jira/Yogi and could measure “tool repeatability” more than “drafting variance.”

## Recommended semantics (for hub + report labels)

| Layer | Isolation target | Rationale |
|-------|------------------|-----------|
| **Cross-attempt** (prep₁/cov₁ vs prep₂/cov₂) | **Cold session** (new agent thread) per `attempt` index | Estimates model/tool variance without prior attempt transcript |
| **Within-attempt** (prep → coverage → tests) | **Same session allowed** (single paste pack) | Matches production handoff; coverage legitimately depends on ref |
| **Within TEST-PREP** | **Subprocess per bundle** (existing norm in [`.cursor/pipelines/test-prep.md`](../../../.cursor/pipelines/test-prep.md)) | Prevents one-shot multi-bundle collapse; orthogonal to cross-attempt sessions |

## Metric / report labeling (align with [`.cursor/benchmark/run-results/README.md`](../../../.cursor/benchmark/run-results/README.md))

When reporting cross-attempt spread, always state **mode**:

- **Fresh-session stochasticity**: N attempts each in its **own** chat/session (hub design target).
- **Deterministic replay / same-thread**: all attempts in **one** session or rapid follow-on messages without cold start — high Jaccard / low spread may reflect **context reuse**, not robust pipeline stability.
- **Hybrid** (discouraged for publishing): e.g. prep in cold session A, coverage pasted in session B without shared ref file discipline — hard to interpret; avoid unless explicitly documented.

## Edge: “one session per run” vs “one session per micro-step”

**Stakeholder default from chat:** one **cold session per benchmark run (attempt)** containing prep + coverage + (optional) tests for that attempt.

**Heavier alternative:** separate sessions for prep₁ vs coverage₁ — only needed if the research question is independence of **coverage drafting** from **prep transcript**; operationally expensive and diverges from normal pipeline use.

## Deliverable checklist

- [x] Reconcile suite one-step-per-message vs statistical isolation  
- [x] Define within-attempt vs cross-attempt context policy  
- [x] Map labels to run-results variance section expectations  

**Implementation note:** hub-generated `report.md` should **require** an explicit **Variance methodology** line (which of the three modes above) so `compare_runs` KPIs are not over-interpreted.
