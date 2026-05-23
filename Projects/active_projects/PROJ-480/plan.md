# PROJ-480: Test review P2 opportunistic polish 2026-05-20

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-480` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-480 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. CAT-9 Simplification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. CAT-8 Needless Complexity | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CAT-10 Parametrize | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. CAT-11 Fragile Assertion | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. CAT-12 Logic-Heavy | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-22
**Active Phase:** Phase 1 (CAT-9 Simplification)
**Last Action:** Project created from `2026-05-20_210550_test-review` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None
**Line refs refreshed 2026-05-22 post-merge `67116932d`.**

## Overview
P2 tier of the 2026-05-20 test-review. Lowest-priority polish work — readability and maintainability improvements that don't change test fidelity. Dominated by **CAT-10 parametrization (88 verified findings, ~3,000 LOC reducible)**: clusters of structurally identical tests where the per-test setup is genuinely redundant. After verification, ~145 items entered the plan (~1,900 LOC reclaimable). This project is sequenced lowest-risk first (simplification, then complexity reduction, then parametrize, then assertion/logic polish).

## Goals
- Replace ~28 CAT-9 repeated-pattern setups with shared fixtures or in-module helpers
- Flatten ~30 CAT-8 deeply-nested patch / oversized helper sites
- Parametrize ~55 CAT-10 structurally-identical test clusters (≥3 members each)
- Replace ~12 CAT-11 brittle exact-value assertions with tolerance / property checks
- Replace ~20 CAT-12 logic-heavy test bodies with reference values + extracted helpers

## Scope
**In:** CAT-8 Needless Complexity, CAT-9 Simplification, CAT-10 Parametrize, CAT-11 Fragile Assertion, CAT-12 Logic-Heavy — verified items only.
**Out:**
- CAT-1 / 2 / 3 dead-trivial cleanup → see PROJ-478 (P0 project).
- CAT-4 / 5 / 6 / 7 brittle-bloated remediation + cluster items → see PROJ-479 (P1 project).
- Anything OpenCode tagged DISPUTED or INCONCLUSIVE (already excluded).
- Anything Claude's verification rejected or marked out-of-scope (see [findings/verification_report.md](findings/verification_report.md)).

## Key Files
| Component | File Path |
|-----------|-----------|
| Engine validation classes (12) | `tests/unit/strategy/engine/test_engine_validation.py` |
| Superweapon parametrize matrix | `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py` |
| Strategy input handler hotkeys | `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py` |
| Strategy input handler transfer | `tests/unit/ui/screens/test_strategy_input_handler_transfer.py` |
| Camera tests (13 patch blocks) | `tests/unit/ui/test_camera.py` |
| Fleet menu items (10+ FMS rows) | `tests/unit/ui/screens/test_fleet_menu_items.py` |
| Ship serialization roundtrips | `tests/unit/simulation/entities/test_ship_serialization.py` |
| Turn engine lazy properties (18 tests) | `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` |
| Race browser dialog (12 patch.object) | `tests/unit/ui/test_race_browser_dialog.py` (also Phase 3 of PROJ-479) |
| Naming Roman numeral cluster (16 tests) | `tests/unit/strategy/utility/test_naming.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Claude's independent re-verification
- [findings/source_review.md](findings/source_review.md) - Pointer to source OpenCode review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
