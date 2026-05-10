# Phase 5: TurnEngine Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-74 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Wire ResupplyEngine into turn processing

---

## Tasks

### Task 5.1: Write integration tests [Medium]
**File:** `tests/integration/strategy/turn_engine/test_resupply.py` (NEW)
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resupply.py`

- [x] Create test file with fixtures for empire, colony, fleet, facility

- [x] Write `test_turn_processes_fuel_generation`:
  - Create colony with fuel synthesizer facility
  - Process one turn
  - Verify fuel accumulated in facility

- [x] Write `test_turn_processes_fleet_resupply`:
  - Create colony with fuel in facility
  - Create fleet at colony location with partial fuel
  - Process one turn
  - Verify fleet refueled

- [x] Write `test_resupply_before_movement_gives_fuel`:
  - Verify resupply phases run before movement in tick processing
  - Uses mock engines to track call order

- [x] Write `test_full_turn_resupply_and_movement`:
  - Create complete scenario: empire, colony, facility, fleet
  - Process full turn
  - Verify fuel generation and resupply both work together

- [x] Verify: All tests fail initially (no integration yet)

**Notes:** 5 tests written. Used call-order verification for movement ordering test to avoid complex mock ship setup for movement engine.

---

### Task 5.2: Add resupply_engine property to TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/`

- [x] Add import for IResupplyEngine in TYPE_CHECKING block

- [x] Add parameter to `__init__`: `resupply_engine: Optional['IResupplyEngine'] = None`

- [x] Add instance variable: `self._resupply_engine`

- [x] Add property with lazy initialization (follows existing pattern)

- [x] Verify: Property works correctly

**Notes:** Follows exact same pattern as other engine properties (population_engine, resource_engine, etc.)

---

### Task 5.3: Integrate into _process_tick [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/integration/strategy/turn_engine/test_resupply.py`

- [x] Find `_process_tick()` method
- [x] Add Phase 0a (fuel generation) after Phase 0 resource consumption
- [x] Add Phase 0b (fleet resupply) after Phase 0a
- [x] Updated module docstring and _process_tick docstring to reflect new phases

- [x] Verify: All integration tests pass

**Notes:** Resupply runs after resource consumption but before movement, so fleets get refueled before they attempt to move.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - all tests pass
- [x] Run `pytest tests/ -n 12` - full suite passes (6853 passed, 2 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
