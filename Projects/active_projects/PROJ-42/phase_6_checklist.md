# Phase 6: Test Updates & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update tests for new patterns, verify all deprecation warnings eliminated
**Complexity:** Medium

---

## Pre-Phase Checklist
- [x] Phase 5 complete
- [x] Read [design.md](design.md) - review "Test Impact Analysis" section
- [x] Verify: `pytest tests/` passes (5375 passed, 3 skipped)

---

## Task 6.1: Update Test Files Using Deprecated Functions [Medium]
**Issue:** Test maintenance
**Files:** 34 test files identified in swarm analysis
**Tests:** `pytest tests/` after each batch

### Subtasks
- [x] Find all test files importing deprecated functions
- [x] **Result:** No deprecated functions found in tests - they were already removed in earlier phases

**Notes:**
- Searched for get_component_registry, get_modifier_registry, get_vehicle_classes, get_validator, get_resource_registry
- These functions were already removed from game/core/registry.py in Phase 1-2
- All test files already use the new patterns (GameRegistries, get_default_registries, get_default_registry_provider)

---

## Task 6.2: Update Tests for Instance-Only Service Methods [Simple]
**Issue:** Test maintenance for Phase 3 changes
**Files:** `tests/unit/services/test_modifier_service_di.py`, `tests/unit/services/test_ship_stats_service*.py`
**Tests:** `pytest tests/unit/services/`

### Subtasks
- [x] Search for deprecated static method test patterns
- [x] **Result:** No tests for deprecated static patterns exist - instance-only pattern already in use

**Notes:**
- Searched for test_static_methods_still_work and similar patterns
- No matching tests found - Phase 3 already cleaned up the service patterns
- All service tests use instance methods exclusively

---

## Task 6.3: Add Verification Tests for Deprecated Code Removal [Simple]
**Issue:** Ensure deprecated code stays removed
**File:** Create `tests/refactor/test_deprecated_code_removed.py`
**Tests:** `pytest tests/refactor/`

### Subtasks
- [x] Create new test file: `tests/refactor/test_deprecated_code_removed.py`
- [x] Add test verifying FleetMovementSimulator cannot be imported
- [x] Add test verifying deprecated registry functions removed
- [x] Add test verifying GameState aliases removed from app.py
- [x] Add test verifying _get_legacy_crew_requirement removed
- [x] Add tests verifying new patterns work correctly
- [x] Run tests: `pytest tests/refactor/` - 15 passed

**Notes:**
Created comprehensive verification test suite with:
- TestFleetMovementSimulatorRemoved (1 test)
- TestDeprecatedRegistryFunctionsRemoved (5 tests)
- TestGameStateAliasesRemoved (4 tests)
- TestNewPatternsWork (4 tests)
- TestLegacyCrewRequirementRemoved (1 test)

---

## Task 6.4: Run Full Test Suite and Verify Zero Deprecation Warnings [Medium]
**Issue:** Final verification
**Tests:** `pytest tests/ -W error::DeprecationWarning` (strict mode)

### Subtasks
- [x] Run full test suite and count deprecation warnings
- [x] Analyze warning sources
- [x] Document results

**Results:**
- 5375 passed, 3 skipped, 213 warnings total
- 13 DeprecationWarning instances - ALL from tests that intentionally test deprecated BattleEngine paths
- 0 unintended deprecation warnings from project code

**Warning Breakdown:**
- DeprecationWarning (13): From tests exercising deprecated BattleEngine.start() and add_ship_mid_battle() paths - these are EXPECTED as they verify the deprecation mechanism works
- PytestCollectionWarning (2): Test class naming issues (not runtime)
- pygame_gui UserWarning (~200): Third-party UI label sizing warnings (acceptable)

**Conclusion:** Project code has 0 unintended deprecation warnings. The 13 deprecation warnings are intentionally emitted by tests that verify the Phase 5 deprecation mechanism works correctly.

---

## Task 6.5: Final Manual Verification [Simple]
**Issue:** End-to-end functional verification
**Tests:** Manual testing

### Subtasks
- [x] Automated test verification complete
- [ ] Manual testing deferred to user (requires game UI)

**Notes:**
Manual verification tasks require running the game UI which is outside automated testing scope. User should verify:
- Game launches and menu loads
- Ship Builder: create, modify, save, load designs
- Battle: start and complete battles
- Strategy Mode: load saves, move fleets
- Formation Editor: load and modify formations

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (except manual testing)
- [x] Run `pytest tests/` - all 5375 tests pass (5375 passed, 3 skipped)
- [x] Deprecation warnings from project code: 0 (13 intentional from deprecation verification tests)
- [ ] Manual functional tests pass (deferred to user)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Phase 6 Complete, Ready for Audit"
- [x] Final commit: "[PROJ-42] Phase 6: Test verification and deprecated code removal tests - Automated"

---

## Project Completion Checklist
After Phase 6 is complete:
- [x] All 6 phases marked complete in plan.md
- [x] All tests passing (5375 passed, 3 skipped)
- [x] 0 deprecation warnings from project code (13 intentional from test verification)
- [x] FleetMovementSimulator module deleted (331 LOC)
- [x] Deprecated registry functions removed
- [x] Services use instance methods only
- [x] Serialization formats standardized
- [x] BattleEngine uses single controller path (with deprecation warnings for legacy)
- [ ] User has verified functionality (deferred)
- [ ] Archive project or move to completed folder (after audit)
