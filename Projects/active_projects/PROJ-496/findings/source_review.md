# PROJ-496: Source Review

## Origin

This project carries over the **risky** + **non-UI integration** subsets of PROJ-480's deferred backlog.

- Source review: `Reviews/results/2026-05-20_210550_test-review/`
- Source project: `Projects/active_projects/PROJ-480/` (stalled at ~36/138 tasks)
- Structure consult (locality-first split): `AgentCoordination/Scratchpad/Consult/20260523T125719Z_plan-PROJ-480-followthrough/response.md`
- PROJ-480 mid-project audit that re-pended Task 5.14: `Projects/active_projects/PROJ-480/findings/audit_verification.md` F1

## How the backlog was partitioned

See `Projects/active_projects/PROJ-494/findings/source_review.md` for the full Codex recommendation. PROJ-496 owns Codex's third bucket:

> risky core + non-UI integration ownership. `tests/integration/**` outside UI, plus the guard/assertion/logic-heavy unit files that are easy to mis-handle

Additionally, `tests/regression/test_generator_crew_requirement_design.py` (PROJ-480 T5.8 — defensive branch removal) routed here because it's a high-judgment task.

## PROJ-480 Phase-by-phase contribution

| PROJ-480 phase | PROJ-480 task IDs landing in PROJ-496 |
|---|---|
| Phase 2 (CAT-8) | 2.2 (resource_pipeline monolithic split) |
| Phase 3 (CAT-10) | 3.29 (turn_engine 18 isinstance), 3.31 (deterministic_generation 4 tests) |
| Phase 4 (CAT-11) | 4.1 (persistence_adapter 50-line dict), 4.11 (bug_regressions opaque formula) |
| Phase 5 (CAT-12) | 5.4 + 5.5 (battle_engine_tick), 5.8 (generator_crew defensive), 5.9 (atmosphere stochastic), 5.11 (research workflow RNG), 5.12 (commands_colonization retry), 5.13 (complex_workflow retry), 5.14 (turn_engine guards re-pended), 5.17 (colony_output derivation) |

Total: ~13 actionable tasks across 2 execution phases.

## Source-review categories covered

- CAT-8 Needless Complexity (1 task)
- CAT-10 Parametrize (2 tasks — both single-file)
- CAT-11 Fragile Assertion (2 tasks)
- CAT-12 Logic-Heavy (8 tasks — the bulk)

## Special handling notes

1. **T5.14 re-pending**: PROJ-480 originally expected PROJ-479 Task 3.21 to absorb T5.14 by splitting the guards into `tests/static_guards/`. Codex's 2026-05-23 audit (PROJ-480/findings/audit_verification.md F1) found both `inspect.getsource(...)` and AST-parsing guards still present in `test_turn_engine_lazy_properties.py:219-288`, and PROJ-479's Task 3.21 is itself NEEDS_REWORK. T5.14 is therefore re-pended into this project.

2. **T5.5 assertion adjustment**: PROJ-480 Phase 5 documented that the review suggested a weaker first-element-only check; verification adjusted it to `all(i < j for i in ai_indices for j in ship_indices)`. Honor that.

3. **T5.9 RNG handling**: Use the canonical seeded-RNG pattern in the project. Do not introduce ad-hoc determinism.

4. **T5.17 derivation removal**: External value, not re-derived logic. Reference the formula doc rather than re-computing.

## Verification protocol

Phase 0 must re-grep every task's target pattern before TDD work begins. Every file path here was re-verified against the live tree on 2026-05-23, but **line numbers were not** — they are still advisory.
