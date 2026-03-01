# Phase 2: Fix Command Handler and All Callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-218 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all callers of `DesignCostCalculator` to pass registries, ensuring every code path produces correct costs.

---

## Tasks

### Task 2.1: Fix `AddToConstructionQueueCommandHandler._load_design_cost()` [Simple]
**File:** `game/strategy/engine/command_handlers.py` (lines 817-841)
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestAddToConstructionQueueCommandHandler -v`

- [ ] Update `_load_design_cost()` to pass `session.registries` to `DesignCostCalculator.calculate_total_cost()`
- [ ] Verify the handler test `test_queue_item_has_required_fields()` now gets populated costs
- [ ] Add test assertion that `total_cost` is non-empty when design exists

**Notes:**

### Task 2.2: Fix `ProductionEngine._calculate_design_cost()` [Simple]
**File:** `game/strategy/engine/production_engine.py` (lines 89-107)
**Tests:** `pytest tests/unit/strategy/production_engine/ -v`

- [ ] Update to pass `self._registries` to `DesignCostCalculator.calculate_total_cost()`
- [ ] Verify existing production engine tests pass

**Notes:** This method is a fallback path called during tick processing. Should be correct even if rarely hit.

### Task 2.3: Fix Maintenance Engine Callers [Simple]
**File:** `game/strategy/engine/maintenance_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_maintenance_engine.py -v`

- [ ] Find all calls to `DesignCostCalculator.calculate_total_cost()` or `calculate_maintenance_cost()`
- [ ] Update to pass registries
- [ ] Verify maintenance engine tests pass

**Notes:**

### Task 2.4: Fix Empire Economy Calculator [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/engine/test_empire_economy.py -v`

- [ ] Find all calls to cost calculator
- [ ] Update to pass registries
- [ ] Verify economy tests pass

**Notes:**

### Task 2.5: Update Command Handler Tests [Medium]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestAddToConstructionQueueCommandHandler -v`

- [ ] Update test fixtures to provide registries with component definitions that have `resource_cost`
- [ ] Add test: add design to queue → verify `total_cost` matches expected component costs
- [ ] Add test: add design with modifiers → verify cost reflects modifier multipliers
- [ ] Verify all existing handler tests still pass

**Notes:**

### Task 2.6: Update Production Repro Tests [Simple]
**File:** `tests/unit/strategy/engine/test_production_repro.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_repro.py -v`

- [ ] Update `_make_add_callback()` to pass registries to cost calculator
- [ ] Verify `test_queue_item_has_populated_cost()` passes with the fix

**Notes:** This test was written for PROJ-213 to verify costs are populated — should pass after fix.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/test_command_handlers.py -v` passes
- [ ] `pytest tests/unit/strategy/engine/ -v` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
