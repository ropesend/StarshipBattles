# PROJ-157: Test Suite Cleanup - Validated Findings v4

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-157` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-157 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Safe Deletions | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Merge-Then-Delete | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Partial Cleanups | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Old Directory Tree Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-16 17:45
**Active Phase:** Plan Approved - Ready for Implementation
**Last Action:** Baseline test suite run, plan fully documented
**Next Action:** Begin Phase 1 Task 1.1 (delete diagnostic scripts)
**Blockers:** None
**Baseline:** 4405 passed, 2 skipped, 2 pre-existing failures (see below)
**Context for Next Agent:** Four validation reviews are in `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_*.md`. These contain the evidence for every deletion/merge decision. Consult them if unsure about any item.

### Pre-Existing Test Failures (NOT caused by this project)
1. `tests/unit/quickstart/test_quickstart_designs.py::test_design_stats_match_expected[qs_general_purpose-unknown]` - Formula-based ability definitions (`'=ship_class_mass'`) not being evaluated
2. `tests/integration/gameplay_loop/test_turn_execution.py::test_production_completes_across_turns` - Same root cause (ability creation failures)

## Overview
Remove confirmed dead test code identified by 4 independent validation reviews: diagnostic scripts, empty scaffolds, over-mocked tests exercising zero production code, and duplicate test files. Where duplicates contain unique tests, merge those into canonical files first. Finally, clean up 4 old directory trees (services/, combat/, entities/, components/) file-by-file.

## Goals
- Remove ~5,000+ lines of confirmed-dead test code (scripts, scaffolds, zero-value tests)
- Consolidate ~14 duplicate files by merging ~70 unique tests into canonical counterparts
- Partially clean up ~11 files by removing dead classes/methods within them
- Remove ~12,700 lines from 4 old directory trees (file-by-file verified)
- Zero test coverage loss for production code

## Scope
**In:**
- DELETE files confirmed safe by validation reviews (scripts, scaffolds, dead tests)
- MERGE unique tests from duplicate files into canonical counterparts, then delete duplicates
- PARTIAL CLEANUP of specific classes/methods within otherwise-good files
- DELETE 8 empty/dead conftest.py files
- FILE-BY-FILE deletion of old directory trees (services/, combat/, entities/, components/)

**Out:**
- Touching any DISPUTED files (repro tests, fixture meta-tests, physics formula tests, etc.)
- MockComponent extraction (intentionally different per context)
- MockPlanetType extraction (valid candidate but separate project)
- Renaming directories (refactor/ → modifiers/)
- Old directory tree wholesale deletion - must be file-by-file verified

## Key Files
| Component | File Path |
|-----------|-----------|
| Validation Review 1 (UI/Strategy) | `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_1_ui_strategy.md` |
| Validation Review 2 (Simulation/Core) | `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_2_simulation_core.md` |
| Validation Review 3 (AI/Refactor) | `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_3_ai_refactor.md` |
| Validation Review 4 (Remaining/Crosscut) | `Reviews/results/2026-02-16_105410_general_test-suite-cleanup-v3/findings/validation_4_remaining_crosscut.md` |

## Already Cleaned Up (confirmed missing during planning)
- mock_battle_ui_service.py, test_conflict_core.py, test_build_queue_source_errors.py
- test_engines_contracts.py, test_configs/, output/logs/, test_ship_stats_phase_ordering.py
- test_ability_aggregator_scope.py, test_spatial_extended.py, test_collision_system.py
- test_strategy_detail_formatter.py, test_production_refactor.py, test_beam_ramming.py
- test_fleet_report_filters.py, test_fleet_resource_aggregator.py, test_fleet_battle_adapter.py

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
### After Each Phase
- [ ] `pytest tests/ -x -q --tb=short` - all tests pass
- [ ] Verify test count decreased only by expected number of removed tests

### Final Verification
- [ ] `pytest tests/ -n 12` - full parallel run passes
- [ ] No files from DISPUTED list were touched
- [ ] Document final test count delta

## Completion Checklist
- [ ] Phase 1 checklist complete
- [ ] Phase 2 checklist complete
- [ ] Phase 3 checklist complete
- [ ] Phase 4 checklist complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
