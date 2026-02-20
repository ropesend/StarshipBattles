# Phase 2: Delete Tests for Dead API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-158 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove all unit tests that exclusively tested the dead `process_production()` / `process_fleet_production()` API.

---

## Tasks

### Task 2.1: Delete dead unit test files [Simple]
**Tests:** `pytest tests/unit/strategy/production_engine/ -q` (remaining tests should pass)

- [x] Delete `tests/unit/strategy/production_engine/test_basics.py` (3 tests — turn decrement via dead API)
- [x] Delete `tests/unit/strategy/production_engine/test_completion.py` (4 tests — completion via dead API)
- [x] Delete `tests/unit/strategy/production_engine/test_facility_queue_production.py` (8 tests — facility queue via dead API)
- [x] Delete `tests/unit/strategy/production_engine/test_fleet_production.py` (15 tests — fleet production via dead API)
- [x] In `tests/unit/strategy/production_engine/test_spawning.py`: Delete `TestMultipleItemsProcessing` class (1 test — calls dead `process_production`)
- [x] In `tests/unit/strategy/production_engine/test_spawning.py`: Delete `TestMultipleColoniesProcessing` class (1 test — calls dead `process_production`)
- [x] In `tests/unit/strategy/production_engine/test_spawning.py`: Delete `TestMultipleEmpiresProcessing` class (1 test — calls dead `process_production`)
- [x] Verify: remaining `test_spawning.py` tests pass (TestShipSpawning, TestComplexSpawning classes test live `_spawn_*` methods)
- [x] Verify: `test_resource_costs.py` still passes
- [x] Verify: `test_tick_consumption.py` unchanged (failures expected — fixed in Phase 3)

**Notes:** Total deleted: ~33 tests across 4 full files + 3 classes from test_spawning.py.

### Task 2.2: Delete dead turn engine production tests [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_processing.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_processing.py -q`

- [x] Delete `TestProductionProcessing` class entirely (5 tests: `test_empty_queue_skipped`, `test_production_decrements_turns`, `test_production_completes_at_zero`, `test_no_shipyard_pauses_production`, `test_complex_production_no_shipyard_needed`)
- [x] Delete `TestFleetProductionProcessing` class (1 test - calls dead `process_fleet_production`)
- [x] Update `TestTurnProcessing` tests to not reference dead `process_production` method (removed patches)
- [x] Delete `test_process_turn_runs_production` test (asserted dead method call)
- [x] Verify remaining test classes in the file still pass (44 pass)

**Notes:**

### Task 2.3: Remove dead interface tests [Simple]
**File:** `tests/unit/strategy/interfaces/test_engine_interfaces.py`
**Tests:** `pytest tests/unit/strategy/interfaces/test_engine_interfaces.py -q`

- [x] Find and remove any tests asserting `process_production` or `process_fleet_production` exist on IProductionEngine (none found - Phase 1 already cleaned up)
- [x] Verify remaining interface tests pass (68 pass)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/production_engine/ -q` — 25 pass, 11 fail in tick_consumption (Phase 3 scope)
- [x] `pytest tests/unit/strategy/turn_engine/ -q` — 44 pass
- [x] `pytest tests/unit/strategy/interfaces/ -q` — 68 pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
