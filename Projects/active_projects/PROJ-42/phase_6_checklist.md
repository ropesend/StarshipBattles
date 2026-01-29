# Phase 6: Test Updates & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-42 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update tests for new patterns, verify all deprecation warnings eliminated
**Complexity:** Medium

---

## Pre-Phase Checklist
- [ ] Phase 5 complete
- [ ] Read [design.md](design.md) - review "Test Impact Analysis" section
- [ ] Verify: `pytest tests/` passes

---

## Task 6.1: Update Test Files Using Deprecated Functions [Medium]
**Issue:** Test maintenance
**Files:** 34 test files identified in swarm analysis
**Tests:** `pytest tests/` after each batch

### Subtasks
- [ ] Find all test files importing deprecated functions:
  ```bash
  grep -r "from game.core.registry import get_component_registry\|get_modifier_registry\|get_vehicle_classes\|get_validator\|get_resource_registry" tests/ --include="*.py" -l
  ```
- [ ] Update tests to use GameRegistries fixtures instead:
  - Replace `get_component_registry()` with `registries.components`
  - Replace `get_modifier_registry()` with `registries.modifiers`
  - Replace `get_vehicle_classes()` with `registries.vehicle_classes`
  - Replace `get_resource_registry()` with `registries.resources`
- [ ] Update tests in batches, running `pytest` after each batch:
  - Batch 1: `tests/unit/core/` files
  - Batch 2: `tests/unit/simulation/` files
  - Batch 3: `tests/unit/services/` files
  - Batch 4: `tests/unit/entities/` files
  - Batch 5: `tests/integration/` files
  - Batch 6: Remaining files
- [ ] Run full test suite: `pytest tests/`

**Notes:**

---

## Task 6.2: Update Tests for Instance-Only Service Methods [Simple]
**Issue:** Test maintenance for Phase 3 changes
**Files:** `tests/unit/services/test_modifier_service_di.py`, `tests/unit/services/test_ship_stats_service*.py`
**Tests:** `pytest tests/unit/services/`

### Subtasks
- [ ] Remove tests that specifically test static method calling pattern:
  - `test_static_methods_still_work`
  - `test_static_methods_with_registry_param_still_work`
- [ ] Update tests to use instance pattern exclusively
- [ ] Add tests verifying instance pattern works correctly
- [ ] Run tests: `pytest tests/unit/services/`

**Notes:**

---

## Task 6.3: Add Verification Tests for Deprecated Code Removal [Simple]
**Issue:** Ensure deprecated code stays removed
**File:** Create `tests/refactor/test_deprecated_code_removed.py`
**Tests:** `pytest tests/refactor/`

### Subtasks
- [ ] Create new test file: `tests/refactor/test_deprecated_code_removed.py`
- [ ] Add test verifying FleetMovementSimulator cannot be imported:
  ```python
  def test_fleet_movement_simulator_removed():
      with pytest.raises(ImportError):
          from game.strategy.engine.fleet_movement import FleetMovementSimulator
  ```
- [ ] Add test verifying deprecated registry functions removed:
  ```python
  def test_deprecated_registry_functions_removed():
      from game.core import registry
      assert not hasattr(registry, 'get_component_registry')
      assert not hasattr(registry, 'get_modifier_registry')
      # etc.
  ```
- [ ] Add test verifying GameState aliases removed from app.py:
  ```python
  def test_gamestate_aliases_removed():
      from game import app
      assert not hasattr(app, 'MENU')
      assert not hasattr(app, 'BUILDER')
      # etc.
  ```
- [ ] Run tests: `pytest tests/refactor/`

**Notes:**

---

## Task 6.4: Run Full Test Suite and Verify Zero Deprecation Warnings [Medium]
**Issue:** Final verification
**Tests:** `pytest tests/ -W error::DeprecationWarning` (strict mode)

### Subtasks
- [ ] Run full test suite with deprecation warnings as errors:
  ```bash
  pytest tests/ -W error::DeprecationWarning
  ```
- [ ] If any warnings remain, identify source and fix
- [ ] Run full test suite normally and count remaining warnings:
  ```bash
  pytest tests/ 2>&1 | grep -c "DeprecationWarning"
  ```
- [ ] Target: 0 deprecation warnings from project code
- [ ] Document any remaining warnings from third-party libraries (acceptable)

**Notes:**

---

## Task 6.5: Final Manual Verification [Simple]
**Issue:** End-to-end functional verification
**Tests:** Manual testing

### Subtasks
- [ ] Launch game and verify main menu loads
- [ ] Test Ship Builder:
  - Create new ship design
  - Add components
  - Add modifiers to components
  - Save design
  - Load design
- [ ] Test Battle:
  - Start a battle with saved design
  - Verify battle runs without errors
  - Complete battle
- [ ] Test Strategy Mode (if applicable):
  - Load save game
  - Verify fleets display correctly
  - Move a fleet
  - Save game
- [ ] Test Formation Editor:
  - Load formation
  - Modify formation
  - Save formation
- [ ] Document any issues found

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - all 5199+ tests pass
- [ ] Deprecation warnings from project code: 0
- [ ] Manual functional tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Final commit: "PROJ-42 Phase 6: Complete test updates and final verification"

---

## Project Completion Checklist
After Phase 6 is complete:
- [ ] All 6 phases marked complete in plan.md
- [ ] All tests passing (5199+)
- [ ] 0 deprecation warnings from project code
- [ ] FleetMovementSimulator module deleted (331 LOC)
- [ ] Deprecated registry functions removed
- [ ] Services use instance methods only
- [ ] Serialization formats standardized
- [ ] BattleEngine uses single controller path
- [ ] User has verified functionality
- [ ] Archive project or move to completed folder
