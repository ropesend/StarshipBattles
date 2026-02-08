# Phase 2: Production Engine - Parallel Queue Processing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make the production engine process all queues independently each turn - planet base queue + each shipyard facility queue + fleet queues.

---

## Tasks

### Task 2.1: Update planet production to process facility queues [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/ && pytest tests/integration/strategy/production/`

- [ ] Modify `process_production()` (lines 47-84) to process multiple queues per colony:
  - Process base queue (`colony.construction_queue`): only handle items where `type == "complex"` (skip ship/fighter/satellite types - those belong in facility queues now)
  - Iterate `colony.facilities` to find operational shipyard facilities (reuse or import `_facility_is_shipyard()` from `build_queue_source.py`)
  - For each shipyard facility with non-empty `facility.construction_queue`:
    - Get first item: `facility.construction_queue[0]`
    - Apply same validation logic (shipyard check is implicit - it IS a shipyard)
    - Decrement `turns_remaining`
    - On completion: pop item, route to `_spawn_complex()` or `_spawn_ship()` as appropriate
  - Base queue still processes complexes without shipyard requirement (existing behavior)
- [ ] Update existing tests in `test_basics.py` to verify base queue still works for complexes
- [ ] Add test: planet with 1 shipyard facility - facility queue processes independently
- [ ] Add test: planet with 2 shipyard facilities - both queues process simultaneously (2 items per turn)
- [ ] Add test: base queue ignores ship-type items (they don't process)
- [ ] Add test: facility queue processes both ship and complex types
- [ ] Add test: facility queue obeys turns_remaining decrement and completion
- [ ] Update `test_completion.py` and `test_spawning.py` if they reference `colony.construction_queue` directly
- [ ] Verify: run `pytest tests/unit/strategy/production_engine/ -v` - all pass

**Notes:** The key change is: `process_production()` now has TWO loops per colony - one for the base queue (complexes only) and one for each shipyard facility queue (any type).

---

### Task 2.2: Verify fleet production unchanged [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_fleet_production.py`

- [ ] Verify `process_fleet_production()` (lines 177-232) still works unchanged - fleet has single queue, no facility concept
- [ ] Run `pytest tests/unit/strategy/production_engine/test_fleet_production.py -v` - all pass
- [ ] Run `pytest tests/integration/strategy/production/test_fleet_production_e2e.py -v` - all pass

**Notes:** Fleet production should be completely unaffected. Fleets don't have facilities.

---

### Task 2.3: Update integration tests [Medium]
**Files:** `tests/integration/strategy/production/test_queue.py`, `test_completion.py`
**Tests:** `pytest tests/integration/strategy/production/`

- [ ] Review integration tests for assumptions about single-queue processing
- [ ] Update any tests that directly modify `colony.construction_queue` to work with the new model
- [ ] Add integration test: E2E planet with 2 shipyards builds 2 ships in parallel over multiple turns
- [ ] Add integration test: save/load round-trip preserves facility construction queues
- [ ] Verify: run `pytest tests/integration/strategy/production/ -v` - all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
