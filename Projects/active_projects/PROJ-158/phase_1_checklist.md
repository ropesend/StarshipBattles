# Phase 1: Delete Dead Production API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the dead `process_production()` and `process_fleet_production()` methods from production code, turn engine, interface, and mocks.

---

## Tasks

### Task 1.1: Remove dead methods from ProductionEngine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -k "test_empty_queue or test_partial_resource or test_item_completes or test_next_item or test_fleet_complex_paused or test_items_without_cost"`

- [ ] Delete `process_production()` method (lines 443-450)
- [ ] Delete comment "Legacy methods _process_base_queue..." (line 452)
- [ ] Delete `process_fleet_production()` method (lines 563-572)
- [ ] Verify: passing tick tests still pass

**Notes:**

### Task 1.2: Remove dead calls from TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -k "not TestProductionProcessing"`

- [ ] Delete `self.process_production(empires, galaxy, save_path)` call (line 275)
- [ ] Delete comment "# 3. Production Phase (Colonies)" (line 274)
- [ ] Delete `self.production_engine.process_fleet_production(empires, galaxy, save_path)` call (line 278)
- [ ] Delete comment "# 4. Fleet Production Phase (PROJ-67)" (line 277)
- [ ] Delete `TurnEngine.process_production()` method entirely (lines 303-313)
- [ ] Verify: non-production turn tests still pass

**Notes:**

### Task 1.3: Remove dead methods from IProductionEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/interfaces/`

- [ ] Delete `process_production()` abstract method (lines 154-169)
- [ ] Delete `process_fleet_production()` abstract method (lines 171-188)
- [ ] Update example usage in class docstring (lines 128-131) — remove references to these methods

**Notes:**

### Task 1.4: Update MockProductionEngine [Simple]
**File:** `tests/unit/strategy/mocks/mock_engines.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_dependency_injection.py`

- [ ] Remove `process_production_calls` tracking list from `__init__`
- [ ] Remove `process_fleet_production_calls` tracking list from `__init__`
- [ ] Remove `process_production()` method
- [ ] Remove `process_fleet_production()` method
- [ ] Verify: DI tests still pass

**Notes:**

### Task 1.5: Update documentation [Simple]
**File:** `docs/systems/planetary_complex.md`
**Tests:** N/A (documentation)

- [ ] Search for references to `process_production` and update to describe tick-based system
- [ ] Search for references to `process_fleet_production` and update similarly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/production_engine/test_tick_consumption.py tests/unit/strategy/production_engine/test_resource_costs.py -q` — passing tests unchanged
- [ ] No new failures introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
