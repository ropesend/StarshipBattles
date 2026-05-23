# PROJ-495: Test polish core mechanical (PROJ-480 follow-through)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-495` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-495 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Retarget / prune | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. CAT-9 simplification (core) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-8 needless complexity (core) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-10 parametrize (core) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-11/12 fragile + logic (core) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Planning complete; ready for Phase 0
**Last Action:** Project scaffolded from PROJ-480 deferred backlog (Codex consult 2026-05-23 — locality-first split). All listed file paths re-verified against current tree.
**Next Action:** Run Phase 0 (retarget/prune) — re-grep every task's target pattern before TDD.
**Blockers:** None.

## Overview
P2 test-review polish carried over from PROJ-480 for **core mechanical** (non-UI, non-risky) tests. Covers `tests/unit/strategy/**`, `tests/unit/simulation/**`, `tests/unit/ai/**`, `tests/unit/modifiers/**`, `tests/unit/builder/**`, `tests/regression/**` (excluding the explicit risky files routed to PROJ-496). PROJ-494 owns UI-family; PROJ-496 owns risky guard/introspection + non-UI integration.

## Goals
- Apply CAT-8/9/10/11/12 polish to every core-mechanical test file pending after PROJ-480 stalled
- Lift in-method imports, parametrize structurally-identical clusters, extract shared mock factories
- Avoid the risky guard/introspection files (those live in PROJ-496)

## Scope
**In:** Pending PROJ-480 tasks where the target file is under:
- `tests/unit/strategy/**` (excluding `test_turn_engine_lazy_properties.py`, `test_persistence_adapter.py`, `test_colony_output.py`, `test_generation.py` atmosphere — all routed to PROJ-496)
- `tests/unit/simulation/**` (excluding `test_battle_engine_tick.py` — routed to PROJ-496)
- `tests/unit/ai/**`
- `tests/unit/modifiers/**`
- `tests/unit/builder/**`
- `tests/regression/**` (excluding `test_generator_crew_requirement_design.py` — routed to PROJ-496 with other defensive-branch logic)

**Out:**
- UI-family tests → PROJ-494
- Risky guard/introspection/atmosphere/derivation files + non-UI integration → PROJ-496
- Anything PROJ-480 marked NO-ACTION / verified-acceptable / coordination-only
- Anything PROJ-480 deliberately skipped

## Key Files
See [manifest.md](manifest.md) for the full file list.

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/source_review.md](findings/source_review.md) — origin (PROJ-480 + Codex consult)
- Source: `Projects/active_projects/PROJ-480/plan.md` (deferred backlog)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
