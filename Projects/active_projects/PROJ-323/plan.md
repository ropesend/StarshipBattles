# PROJ-323: Test review P2 opportunistic polish 2026-05-02

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-323` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-323 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-9 Simplification (32 items) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-8 Needless Complexity (32 items) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-10 Parametrize (53 items) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-11 Fragile Assertion (15 items) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. CAT-12 Logic-Heavy (27 items) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-03
**Active Phase:** Phase 1 CAT-9 Simplification
**Last Action:** Project created from 2026-05-02_204633_test-review after independent verification (3rd skeptical pass)
**Next Action:** Begin Phase 1 tasks: simplify 32 verified CAT-9 cases
**Blockers:** None

## Overview
This project applies the P2 (opportunistic-polish) tier of the OpenCode test
review at `Reviews/results/2026-05-02_204633_test-review/`. After an
independent third-pass verification, 159 items survived (156 verified,
3 needs-rework) across categories CAT-8 through CAT-12, claiming
approximately 10,735 LOC of reclaimable test code.

## Goals
- Simplify the 32 verified CAT-9 cases identified by review `2026-05-02_204633_test-review` (smallest deltas first — repeated imports, micro-duplications).
- Reduce the 32 verified CAT-8 needless-complexity cases (flatten nested patches, reduce mock setup boilerplate).
- Parametrize the 53 verified CAT-10 identical-pattern test clusters.
- Replace fragile assertions in the 15 verified CAT-11 cases with semantic comparisons or documented boundary references.
- Replace reimplemented production logic in the 27 verified CAT-12 cases with reference values or direct production calls.

## Scope
**In:** CAT-8, CAT-9, CAT-10, CAT-11, CAT-12 — verified items only.
**Out:**
- CAT-1, CAT-2, CAT-3 — see PROJ-321 (P0 project).
- CAT-4..CAT-7 + APC/DUP/HLP — see PROJ-322 (P1 project).
- Anything OpenCode tagged DISPUTED or INCONCLUSIVE.
- Anything Claude's verification rejected or marked out-of-scope (see findings/verification_report.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| test_fleet_report_filters (4 items) | `tests/unit/ui/screens/test_fleet_report_filters.py` |
| test_fleet_data_source (3 items) | `tests/unit/ui/screens/test_fleet_data_source.py` |
| test_ai_controller_unit (2 items) | `tests/unit/ai/test_ai_controller_unit.py` |
| test_fleet_speed_calculator (2 items) | `tests/unit/strategy/test_fleet_speed_calculator.py` |
| test_callbacks (2 items) | `tests/unit/research/research_scene/test_callbacks.py` |
| test_initialization (2 items) | `tests/unit/research/research_scene/test_initialization.py` |
| test_engine_event_emission (2 items) | `tests/unit/strategy/test_engine_event_emission.py` |
| test_strategy_game_state_manager (2 items) | `tests/unit/ui/screens/test_strategy_game_state_manager.py` |
| test_superweapon_handler_validation (2 items) | `tests/unit/strategy/engine/test_superweapon_handler_validation.py` |
| test_battle_engine_end_conditions (2 items) | `tests/unit/simulation/systems/test_battle_engine_end_conditions.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification results
- [findings/source_review.md](findings/source_review.md) - Pointer to the source OpenCode test review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
