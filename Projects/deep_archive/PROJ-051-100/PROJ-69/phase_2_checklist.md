# Phase 2: Production Engine - Parallel Queue Processing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make the production engine process all queues independently each turn - planet base queue + each shipyard facility queue + fleet queues.

---

## Tasks

### Task 2.1: Update planet production to process facility queues [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ && pytest tests/integration/strategy/production/`

- [x] Modify `process_production()` to process multiple queues per colony:
  - Process base queue (`colony.construction_queue`): only handle items where `type == "complex"` (skip ship/fighter/satellite types)
  - Iterate `colony.facilities` to find operational shipyard facilities (imported `_facility_is_shipyard()` from `build_queue_source.py`)
  - For each shipyard facility with non-empty `facility.construction_queue`: decrement turns_remaining, route to spawner on completion
  - Base queue still processes complexes without shipyard requirement (existing behavior)
- [x] Update existing tests in `test_basics.py` to verify base queue still works for complexes
- [x] Add test: planet with 1 shipyard facility - facility queue processes independently
- [x] Add test: planet with 2 shipyard facilities - both queues process simultaneously (2 items per turn)
- [x] Add test: base queue ignores ship-type items (they don't process)
- [x] Add test: facility queue processes both ship and complex types
- [x] Add test: facility queue obeys turns_remaining decrement and completion
- [x] Update `test_completion.py` and `test_spawning.py` to use facility queues for ship items
- [x] Verify: run `pytest tests/unit/strategy/production_engine/ -v` - all 55 pass

**Notes:** Refactored `process_production()` into `_process_base_queue()` (complexes only) and `_process_facility_queues()` (per-shipyard parallel processing). 15 new tests in `test_facility_queue_production.py`. Updated `test_basics.py`, `test_completion.py`, `test_spawning.py` to use facility queues for ship items.

---

### Task 2.2: Verify fleet production unchanged [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_fleet_production.py`

- [x] Verify `process_fleet_production()` still works unchanged - fleet has single queue, no facility concept
- [x] Run `pytest tests/unit/strategy/production_engine/test_fleet_production.py -v` - all 16 pass
- [x] Run `pytest tests/integration/strategy/production/test_fleet_production_e2e.py -v` - all 7 pass

**Notes:** Fleet production completely unaffected. No changes needed.

---

### Task 2.3: Update integration tests [Medium]
**Files:** `tests/integration/strategy/production/test_queue.py`, `test_completion.py`
**Tests:** `pytest tests/integration/strategy/production/`

- [x] Review integration tests for assumptions about single-queue processing
- [x] Update tests that directly modify `colony.construction_queue` for ship items to use facility queues
- [x] Updated `test_completion.py` - ship spawning tests now use facility queues
- [x] Updated `test_queue.py` - shipyard requirement tests updated for new model
- [x] Updated `test_complex_workflow.py` - shipyard enables ship building test
- [x] Updated `test_turn_processing.py` - turn engine production tests
- [x] Verify: run `pytest tests/integration/strategy/production/ -v` - all 29 pass

**Notes:** Also updated `tests/integration/test_complex_workflow.py::test_shipyard_enables_ship_building` and `tests/unit/strategy/turn_engine/test_turn_processing.py::TestProductionProcessing` to use facility queues for ship items.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` - 6534 passed (1 pre-existing IFleet mock spec failure)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
