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
| 3. Test File Splitting | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Weak Assertion Fixes | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Naming Convention Standardization | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Directory Structure Reorganization | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Mock Pattern Standardization | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Test Quality Improvements | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** Phase 4 COMPLETE - Weak Assertion Fixes
**Last Action:** Phase 4 Complete - Fixed all weak assertions, added assertion helpers
**Next Action:** Start Phase 5 - Naming Convention Standardization
**Blockers:** None

**Phase 4 Summary:**
- Task 4.1 Complete: Fixed 18 `assert success` patterns across 6 files
- Task 4.2 Complete: Reviewed length assertions, no changes needed
- Task 4.3 Complete: Fixed 48+ `assert x == True/False` patterns to use `is`
- Task 4.4 Complete: Added assertion helpers to tests/conftest.py
- Task 4.5 Complete: Verified no remaining weak assertions

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
