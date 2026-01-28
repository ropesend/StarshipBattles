# PROJ-40: Comprehensive Code Quality Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-40` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-40 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist | Issues |
|-------|--------|-----------|--------|
| 1. Critical Architecture Fixes | **Complete** | [phase_1_checklist.md](phase_1_checklist.md) | 1 Critical |
| 2. Quick Wins - Dead Code & Duplicates | **Complete** | [phase_2_checklist.md](phase_2_checklist.md) | 9 Simple |
| 3. Core Infrastructure Improvements | **Complete** | [phase_3_checklist.md](phase_3_checklist.md) | 6 Issues |
| 4. Simulation Engine Cleanup | **Complete** | [phase_4_checklist.md](phase_4_checklist.md) | 9 Issues |
| 5. Strategy Layer Refinements | **Complete** | [phase_5_checklist.md](phase_5_checklist.md) | 5 Issues |
| 6. AI System Improvements | **Complete** | [phase_6_checklist.md](phase_6_checklist.md) | 4 Issues |
| 7. UI Layer Remediation | **SUPERSEDED** | [phase_7_checklist.md](phase_7_checklist.md) | Moved to Phase 12 |
| 8. Research System Polish | **Complete** | [phase_8_checklist.md](phase_8_checklist.md) | 7 Issues |
| 9. Data & Config Cleanup | **Complete** | [phase_9_checklist.md](phase_9_checklist.md) | 13 Issues |
| 10. Test Infrastructure | Not Started | [phase_10_checklist.md](phase_10_checklist.md) | 18 Issues |
| 11. Original Findings Completion | Not Started | [phase_11_checklist.md](phase_11_checklist.md) | 2 Issues |
| 12. UI Layer Remediation (Final) | Not Started | [phase_12_checklist.md](phase_12_checklist.md) | 37 Files |

**Total Issues:** ~74 (revised after Category 3 audit verification)
**Estimated Effort:** 40-51 hours (reduced from 46-63 hours)

## Current State
**Last Updated:** 2026-01-28
**Active Phase:** Phase 10 - Test Infrastructure (6/18 tasks complete)
**Last Action:** Completed Phase 10 Tasks 10.1, 10.2, 10.4, 10.6, 10.7, 10.12
**Next Action:** Continue Phase 10 - Tasks 10.3, 10.5, 10.8-10.11, 10.13-10.18
**Blockers:** None

### Recent Work (This Session)
- **Phase 10 In Progress:** Test infrastructure cleanup (6/18 tasks complete)
  - 10.1: Removed 5 duplicate scripts (profile_simulation, repro_shield, repro_energy_stats, reproduce_scaling, stress_test)
  - 10.2: Removed additional duplicates (generate_test_data, strategy_tournament, verify_determinism_current), renamed verify_builder_imports with _ prefix
  - 10.4: Consolidated make_mock_ship_instance() to tests/conftest.py, removed duplicates from 3 integration test files
  - 10.6: Renamed formation manual scripts (_test_formation_flight.py, _test_formation_attack.py) - they weren't pytest tests
  - 10.7: Reviewed underutilized directories - all serve valid purpose (no changes needed)
  - 10.12: Enhanced tests/README.md with Naming Conventions, Shared Test Helpers, Unit vs Integration Tests sections
  - Created/expanded `tests/unit/data/test_test_infrastructure.py` with 13 validation tests
  - All 5098 tests pass

### Files Modified This Session
- tests/conftest.py - Added make_mock_ship_instance() helper
- tests/README.md - Enhanced with naming conventions and guidelines
- tests/unit/data/test_test_infrastructure.py - Created with 13 tests
- tests/unit/refactor/test_modifier_loader_v2.py - Fixed reference to deleted modifiers_v2.json
- tests/integration/test_gameplay_loop.py - Uses shared make_mock_ship_instance
- tests/integration/test_colonization.py - Uses shared make_mock_ship_instance
- tests/integration/test_save_load.py - Uses shared make_mock_ship_instance

### Files Deleted This Session
- tests/unit/profile_simulation.py (kept performance/ version)
- tests/unit/repro_shield.py (kept performance/ version)
- tests/unit/repro_energy_stats.py (kept performance/ version)
- tests/unit/reproduce_scaling.py (kept performance/ version)
- tests/unit/stress_test.py (kept performance/ version)
- tests/unit/generate_test_data.py (kept performance/ version)
- tests/unit/strategy_tournament.py (kept performance/ version)
- tests/unit/verify_determinism_current.py (kept performance/ version)

### Files Renamed This Session
- tests/unit/verify_builder_imports.py → tests/unit/_verify_builder_imports.py
- tests/integration/test_formation_flight.py → tests/integration/_test_formation_flight.py
- tests/integration/test_formation_attack.py → tests/integration/_test_formation_attack.py

### Previous Work
- **Phase 9 Complete:** Data & config cleanup (13 tasks)

- **Phase 8 Complete:** Research system polish (7 tasks)
  - 8.1: Added type hints to _draw_node_text()
  - 8.2: Fixed font cache unbounded growth with size quantization
  - 8.3: Fixed state reference inconsistency (use _selected_node.id consistently)
  - 8.4: Added detect_cycles() call during validation
  - 8.6: Documented RP allocation validation with warning logs
  - 8.7: Added negated requirement visibility (red dashed lines)
  - 8.8: Documented fragile state assumption

- **Phase 6 Complete:** AI system improvements (4 tasks)
  - 6.1: Fixed CollisionSystem unsafe HP access with getattr defaults
  - 6.2: Added type hints to AIController (5 methods)
  - 6.3: Standardized collision scoring with fallback warning
  - 6.4: Added comprehensive behavior documentation (KiteBehavior, AttackRunBehavior, FormationBehavior)

- **Phase 5 Complete:** Strategy layer refinements
  - 5.1: Refactored calculate_intercept_point (176→90 lines, extracted helpers)
  - 5.3: Added type hints to pathfinding functions (find_path_*, get_system_at_hex)
  - 5.4: Added constructor injection to FleetMovementEngine
  - 5.5: Added serial validation with warning to ShipInstance.create()
  - 5.6: Reviewed helper methods - kept with improved documentation

- **Phase 4 Complete:** Simulation engine cleanup (7 tasks)

- **Phase 3 Complete:** Core infrastructure improvements (6 tasks)

- **Phase 2 Complete:** Dead code and duplicate removal (8 tasks)

- **Phase 1 Complete:** Fixed duplicate `total_defense_score` initialization

### Audit Results Summary
- **23 items REMOVED** from scope (not issues or already fixed)
- **PROJ comments (11.5) PRESERVED** - architectural documentation
- **UI items consolidated** into new Phase 12 (37 files, 12-16 hours)
- See [PROJ-40_Independent_Audit_Report.md](PROJ-40_Independent_Audit_Report.md) for details

## Overview
This project addresses all 108 issues discovered in the comprehensive code review (`2026-01-27_update_legacy-cleanup-verification`), plus 3 remaining issues from the original legacy cleanup review. Issues are organized into 11 phases by architectural layer and complexity.

### Source Review
- **Original Review:** `Reviews/results/2026-01-27_general_legacy-cleanup-verification`
- **Update Review:** `Reviews/results/2026-01-27_update_legacy-cleanup-verification`
- **Total New Issues:** 108 (3 Critical, 28 Major, 66 Minor, 11 Info)
- **Remaining Original:** 3 (LDF-03, LPA-04, DC-03)

### Issue Breakdown by Severity
| Severity | Count | Addressed in Phases |
|----------|-------|---------------------|
| Critical | 3 | Phase 1 |
| Major | 28 | Phases 2-7 |
| Minor | 66 | Phases 2-10 |
| Info | 11 | Phases 8-10 |
| Original (remaining) | 3 | Phase 11 |

### Phase Strategy

**Phase 1: Critical Architecture Fixes**
Address the 3 critical layer violations that break architectural principles:
- NEW-CORE-001: Core → Strategy layer violation (HexCoord import)
- NEW-SIM-001: Duplicate attribute initialization in Ship
- NEW-UI-001: 37 UI → Simulation/Strategy/AI import violations

**Phase 2: Quick Wins - Dead Code & Duplicates**
Low-effort, high-impact fixes:
- Duplicate code removals (NEW-SIM-002, NEW-SIM-003)
- Dead code patterns (NEW-SIM-004, NEW-UI-006, NEW-STRAT-004)
- Unused imports cleanup

**Phases 3-8: Layer-by-Layer Remediation**
Systematic cleanup of each architectural layer

**Phase 9: Data & Config Cleanup**
JSON schema standardization, placeholder cleanup

**Phase 10: Test Infrastructure**
Test organization, fixture consolidation, framework consistency

**Phase 11: Original Findings Completion**
Complete remaining items from original legacy cleanup

## Success Criteria
1. All 3 critical layer violations resolved
2. All 28 major issues addressed
3. Test suite passes after each phase
4. No regressions introduced

## Related Documents
- [design.md](design.md) - Findings summary and design notes
- [decisions.md](decisions.md) - Architecture decisions made during remediation
- Phase checklists linked in Quick Status table
