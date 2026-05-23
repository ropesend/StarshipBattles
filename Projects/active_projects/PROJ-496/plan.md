# PROJ-496: Test polish risky + non-UI integration (PROJ-480 follow-through)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-496` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-496 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Retarget / prune | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Risky unit files | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Non-UI integration | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Planning complete; ready for Phase 0
**Last Action:** Project scaffolded from PROJ-480 deferred backlog (Codex consult 2026-05-23 — locality-first split). All listed file paths re-verified against current tree.
**Next Action:** Run Phase 0 (retarget/prune) — re-grep every task's target pattern before TDD.
**Blockers:** None.

## Overview
P2 test-review polish carried over from PROJ-480 for the **explicitly risky** files Codex identified plus **non-UI integration** tests. These tasks have higher failure risk than mechanical polish: they touch guard/introspection code (`test_turn_engine_lazy_properties.py` AST guard re-pended after PROJ-479's subsume claim never landed), exact-literal regression bodies, stochastic test bodies (atmosphere generation), or formula re-derivations (colony output). Integration tests in this scope have retry loops or RNG-driven branches that need deterministic rewrites.

This project is sequenced LAST because failure cost is highest. PROJ-494/495 should land first to free up overlapping conftest helpers.

## Goals
- Apply CAT-11/12 polish to the risky unit files (Codex 6 + regression-defensive) with extra care for assertion semantics
- Apply CAT-12 polish to non-UI integration tests (deterministic-setup rewrites for retry loops)
- Inherit PROJ-480 Task 5.14 re-pending (AST-parsing + inspect.getsource guards still present in turn_engine lazy_properties)

## Scope
**In:** Pending PROJ-480 tasks where the target file is:
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (PROJ-480 T3.29 + T5.14 — explicitly risky)
- `tests/unit/strategy/engine/session/test_persistence_adapter.py` (PROJ-480 T4.1 — 50-line literal dict)
- `tests/unit/regressions/test_bug_regressions_2026_01.py` (PROJ-480 T4.11 — opaque formula `assert ab.amount == 25`)
- `tests/unit/simulation/systems/test_battle_engine_tick.py` (PROJ-480 T5.4 + T5.5 — strict AI-ordering invariant + loop tests)
- `tests/unit/strategy/planet_atmosphere/test_generation.py` (PROJ-480 T5.9 — stochastic RNG branching)
- `tests/unit/strategy/formulas/test_colony_output.py` (PROJ-480 T5.17 — happiness rate re-derivation)
- `tests/regression/test_generator_crew_requirement_design.py` (PROJ-480 T5.8 — defensive branches + debug print)
- `tests/integration/strategy/test_deterministic_generation.py` (PROJ-480 T3.31)
- `tests/integration/resource_system/test_resource_pipeline.py` (PROJ-480 T2.2 — 73-line monolithic test split)
- `tests/integration/research_workflow/test_workflow.py` (PROJ-480 T5.11 — seeded RNG)
- `tests/integration/gameplay_loop/test_commands_colonization.py` (PROJ-480 T5.12 — retry-loop → deterministic)
- `tests/integration/test_complex_workflow.py` (PROJ-480 T5.13 — retry guards → deterministic)

**Out:**
- UI-family → PROJ-494
- Mechanical core polish → PROJ-495
- Integration tests under `tests/integration/ui/**` → PROJ-494
- Anything PROJ-480 marked NO-ACTION / verified-acceptable
- Anything PROJ-480 deliberately skipped

## Key Files
See [manifest.md](manifest.md) for the full file list.

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/source_review.md](findings/source_review.md)
- `Projects/active_projects/PROJ-480/findings/audit_verification.md` (F1: Task 5.14 re-pending rationale)
- Source: `Projects/active_projects/PROJ-480/plan.md` (deferred backlog)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
