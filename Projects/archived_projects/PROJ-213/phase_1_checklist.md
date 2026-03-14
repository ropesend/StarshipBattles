# Phase 1: Fix Command Handler & Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-213 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix empty `total_cost` in AddToConstructionQueueCommandHandler and update tests

---

## Tasks

### Task 1.1: Add cost calculation to AddToConstructionQueueCommandHandler [Medium]
**File:** `game/strategy/engine/command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_repro.py tests/unit/strategy/test_command_handlers.py tests/integration/strategy/test_command_handlers.py -v`

- [x] Add import for `DesignCostCalculator` from `game.strategy.services.design_cost_calculator` (line 21)
- [x] Add import for `DesignLibrary` from `game.strategy.systems.design_library` (line 22)
- [x] Add `_load_design_cost()` helper method that loads design data via DesignLibrary and calculates cost via DesignCostCalculator (lines 817-841)
- [x] Update `execute()` to call `_load_design_cost()` and populate `total_cost` and `resources_consumed` (lines 791-800)
- [x] Verify: 90 handler tests pass

**Notes:** Handler gets `entity.owner_id` and `session.save_path` to create DesignLibrary instance. Graceful fallback to `{}` on failure.

### Task 1.2: Update test mock callback and assertions [Simple]
**File:** `tests/unit/strategy/engine/test_production_repro.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_repro.py -v`

- [x] Update `_make_add_callback()` to accept `design_data_registry` parameter for cost calculation
- [x] Add `_TEST_DESIGN_DATA` constant with test design data (cost: A=2500, B=6500, C=2000)
- [x] Add `design_data_registry` fixture mapping design IDs to design data
- [x] Rename tests to `test_queue_item_has_populated_cost` and `test_multiple_queue_additions_have_cost`
- [x] Update assertions to verify `total_cost == {"A": 2500, "B": 6500, "C": 2000}` and `resources_consumed == {"A": 0.0, "B": 0.0, "C": 0.0}`
- [x] Verify: 2 tests pass

### Task 1.3: Verify UI controller tests unaffected [Simple]
**File:** `tests/unit/ui/panels/test_build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/panels/test_build_queue_controller.py -v`

- [x] Confirmed controller tests only check `"total_cost" in item` (existence, not value)
- [x] Verify: 36 tests pass, no changes needed

### Task 1.4: Full test suite verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] 13005 passed, 1 skipped — matches baseline exactly

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
