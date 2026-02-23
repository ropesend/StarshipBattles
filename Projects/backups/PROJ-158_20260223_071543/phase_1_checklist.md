# Phase 1: Delete Dead Production API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the dead `process_production()` and `process_fleet_production()` methods from production code, turn engine, interface, and mocks.

---

## Tasks

### Task 1.1: Remove dead methods from ProductionEngine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -k "test_empty_queue or test_partial_resource or test_item_completes or test_next_item or test_fleet_complex_paused or test_items_without_cost"`

- [x] Delete `process_production()` method (lines 443-450)
- [x] Delete comment "Legacy methods _process_base_queue..." (line 452)
- [x] Delete `process_fleet_production()` method (lines 563-572)
- [x] Verify: passing tick tests still pass

**Notes:** Deleted both methods and the legacy comment.

### Task 1.2: Remove dead calls from TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -k "not TestProductionProcessing"`

- [x] Delete `self.process_production(empires, galaxy, save_path)` call (line 275)
- [x] Delete comment "# 3. Production Phase (Colonies)" (line 274)
- [x] Delete `self.production_engine.process_fleet_production(empires, galaxy, save_path)` call (line 278)
- [x] Delete comment "# 4. Fleet Production Phase (PROJ-67)" (line 277)
- [x] Delete `TurnEngine.process_production()` method entirely (lines 303-313)
- [x] Verify: non-production turn tests still pass

**Notes:** Removed all dead calls and the delegate method. Renumbered phase comments.

### Task 1.3: Remove dead methods from IProductionEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/interfaces/`

- [x] Delete `process_production()` abstract method (lines 154-169)
- [x] Delete `process_fleet_production()` abstract method (lines 171-188)
- [x] Update example usage in class docstring (lines 128-131) — remove references to these methods

**Notes:** Rewrote interface docstring to reflect tick-based only production.

### Task 1.4: Update MockProductionEngine [Simple]
**File:** `tests/unit/strategy/mocks/mock_engines.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_dependency_injection.py`

- [x] Remove `process_production_calls` tracking list from `__init__`
- [x] Remove `process_fleet_production_calls` tracking list from `__init__`
- [x] Remove `process_production()` method
- [x] Remove `process_fleet_production()` method
- [x] Verify: DI tests still pass

**Notes:** Updated mock to only track process_construction_tick.

### Task 1.5: Update documentation [Simple]
**File:** `docs/systems/planetary_complex.md`
**Tests:** N/A (documentation)

- [x] Search for references to `process_production` and update to describe tick-based system
- [x] Search for references to `process_fleet_production` and update similarly

**Notes:** Updated Turn Processing section, Key Methods, and Critical Files table.

### Additional Task: Update tests that referenced deleted methods
**Files:**
- `tests/unit/strategy/interfaces/test_engine_interfaces.py`
- `tests/unit/strategy/turn_engine/test_dependency_injection.py`

- [x] Delete tests that verified dead methods exist on interface
- [x] Update concrete implementation test to only implement process_construction_tick
- [x] Fix DI tests that called deleted process_production method

**Notes:** This was necessary cleanup discovered during Phase 1 execution.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/interfaces/ tests/unit/strategy/turn_engine/test_dependency_injection.py` — 76 passed
- [x] Passing tick tests unchanged: 7 passed
- [x] No new failures introduced
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
