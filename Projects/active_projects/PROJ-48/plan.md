# PROJ-48: Testing Infrastructure Overhaul

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-48` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-48 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Infrastructure Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Conftest Consolidation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Test File Splitting | In Progress | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Weak Assertion Fixes | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Naming Convention Standardization | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Directory Structure Reorganization | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Mock Pattern Standardization | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Test Quality Improvements | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** Phase 3 In Progress - Test File Splitting
**Last Action:** Split 2 more severe monoliths (turn_engine_strategy, modifier_ability_snapshots)
**Next Action:** Continue Phase 3 - Split remaining 14 severe monoliths (Task 3.2)
**Blockers:** None

**Phase 3 Progress:**
- Split test_ship_stats_calculator.py (1775 LOC) -> 5 files in tests/unit/strategy/ship_stats/ (70 tests)
- Split test_ship_instance_proj08.py (1458 LOC) -> 3 files in tests/unit/strategy/ship_instance/ (71 tests)
- Split test_battle_controller.py (1425 LOC) -> 4 files in tests/unit/simulation/battle_controller/ (110 tests)
- Split test_fleet.py (1103 LOC) -> 3 files in tests/unit/strategy/fleet/ (70 tests)
- Split test_pathfinding.py (996 LOC) -> 3 files in tests/unit/strategy/pathfinding/ (55 tests)
- Split test_registry.py (973 LOC) -> 3 files in tests/unit/core/registry/ (69 tests)
- Split test_research_scene.py (954 LOC) -> 3 files in tests/unit/research/research_scene/ (30 tests)
- Split test_collision_edge_cases.py (949 LOC) -> 3 files in tests/unit/engine/collision_edge_cases/ (32 tests)
- Split test_turn_engine_strategy.py (932 LOC) -> 3 files in tests/strategy/turn_engine/ (27 tests)
- Split test_modifier_ability_snapshots.py (907 LOC) -> 2 files in tests/regression/modifier_ability_snapshots/ (70 tests)
- Remaining: 14 severe monoliths (700-1000 LOC), 26 moderate monoliths (500-700 LOC)
- Tests pass: 5734 passed (283 tests moved to new files)

## Overview
This project addresses 36 identified issues in the testing infrastructure, covering critical fixes, conftest consolidation, aggressive splitting of 50 test files over 500 LOC, weak assertion fixes, naming standardization, directory reorganization, mock pattern standardization, and test quality improvements. The goal is to create a maintainable, well-organized test suite with consistent patterns.

## Goals
- Fix critical issues preventing tests from running (2 disabled integration tests)
- Standardize fixture patterns across 13 conftest.py files
- Split 50 monolith test files (>500 LOC) into smaller focused files
- Replace 875 weak assertions with specific value checks
- Standardize naming conventions across test files, classes, and methods
- Mirror source directory structure in tests
- Establish consistent mock patterns across 3011 mock usages
- Clean up print statements, stub classes, and skipped tests

## Scope
**In:**
- All 36 issues from `findings_07_testing_infrastructure.md`
- TSR-001 to TSR-015 (Critical and Major structure issues)
- TNC-001 to TNC-011 (Naming convention issues)
- TC-06 (Test isolation)
- Aggressive splitting of all 50 files >500 LOC

**Out:**
- Writing new tests for coverage gaps (TC-01 to TC-09) - separate project
- Fixing 5 pre-existing test failures in `test_builder_io_integration.py`
- Production code changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Root conftest | `conftest.py` |
| Tests conftest | `tests/conftest.py` |
| Session cache | `tests/infrastructure/session_cache.py` |
| Fixtures module | `tests/fixtures/*.py` |
| Formation tests | `tests/integration/test_formation_*.py` |
| Largest monolith | `tests/unit/strategy/test_ship_stats_service.py` (1756 LOC) |
| Findings source | `findings_07_testing_infrastructure.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## Baseline
**Test Suite Status (2026-01-28):**
- 5244 passed
- 5 failed (pre-existing, excluded from this project)
- 3 skipped
- 28,166 warnings
- ~40 seconds runtime

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline maintained)
- [ ] No test file exceeds 500 LOC
- [ ] All test files follow `test_*.py` naming
- [ ] Parallel execution works (`pytest -n 4`)
- [ ] Audit passed
- [ ] User verified
