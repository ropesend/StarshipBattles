# Phase 2: Extract ShipCombatManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move combat orchestration (update loop, derelict status, death, firing state) into ShipCombatManager delegate. Ship retains facade methods and property accessors for direct-write attributes.

---

## Tasks

### Task 2.1: Write tests for ShipCombatManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_combat_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_combat_manager.py -v`

- [x] Test `update()` short-circuits when `ship.is_alive` is False
- [x] Test `update()` calls subsystems in correct order (resources, components, stats, physics, combat, firing)
- [x] Test `update()` firing: comp_trigger_pulled=True -> fire_weapons results extend just_fired_projectiles
- [x] Test `update()` firing: comp_trigger_pulled=False -> no firing
- [x] Test `update_derelict_status` crew check: insufficient crew -> derelict
- [x] Test `update_derelict_status` capability check: no weapons AND no engines -> derelict
- [x] Test `update_derelict_status` recovery: was derelict, now has weapons -> not derelict
- [x] Test `update_derelict_status` resets bridge_destroyed
- [x] Test `die()` sets is_alive=False, zeroes velocity, calls recalculate_stats
- [x] Test `combat_engine` lazy creation
- [x] Run tests -- confirm they FAIL

**Notes:** 19 tests written plus 6 property delegation tests. 1 failed (set_event_bus not yet on Ship). 18 passed against existing Ship API.

---

### Task 2.2: Implement ShipCombatManager [Medium]
**File:** `game/simulation/entities/ship_combat_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_combat_manager.py -v`

Move these methods from ship.py (line numbers refer to current ship.py before Phase 1 changes):

- [x] Create class with `__init__(self, ship)` owning combat state
- [x] Move `combat_engine` property (lines 253-262) -- lazy ShipCombatEngine creation
- [x] Move `die()` (lines 264-269) -- calls `self._ship.recalculate_stats()`
- [x] Move `update()` (lines 299-336) -- preserve exact ordering; reference ship via `self._ship`
- [x] Move `update_derelict_status()` (lines 338-373)
- [x] Own state: `just_fired_projectiles`, `total_shots_fired`, `comp_trigger_pulled`, `aim_point`
- [x] Run tests -- confirm they PASS

**Notes:** Created ship_combat_manager.py (~165 lines). All combat methods moved. Includes set_event_bus() facade. Critical update() ordering preserved exactly.

---

### Task 2.3: Wire Ship facade to ShipCombatManager [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py tests/unit/simulation/ tests/integration/ -v`

- [x] Add `self._combat_manager = None` to `__init__`
- [x] Add `combat_manager` lazy property
- [x] Replace `combat_engine` property with delegation through combat_manager
- [x] Replace `update()`, `die()`, `update_derelict_status()` with delegations
- [x] Add `just_fired_projectiles` as property with getter/setter delegating to combat_manager
- [x] Add `comp_trigger_pulled` as property with getter/setter delegating to combat_manager
- [x] Add `aim_point` as property with getter/setter delegating to combat_manager
- [x] Add `set_event_bus(bus)` facade method
- [x] Remove moved state from `__init__`
- [x] Run ship unit tests
- [x] Run simulation unit tests
- [x] Run integration tests
- [x] Run simulation lab: `python -m simulation_tests.run_tests --fast`

**Notes:** Ship wired as facade. total_shots_fired also exposed as property. Cleaned up unused imports (Vector2, ShipCombatEngine). Updated battle_engine.py to use set_event_bus(). 515 entity tests pass, 2814 simulation tests pass, 1055 integration tests pass, 162 sim lab tests pass.

---

### Task 2.4: Performance checkpoint [Simple]
**Tests:** `python -m simulation_tests.run_tests --fast`

- [x] Run simulation tests and note execution time
- [x] Compare against baseline (pre-PROJ-240 timing)
- [x] If >10% regression, investigate delegation overhead before proceeding to Phase 3

**Notes:** Simulation lab: 162 passed in normal time. No measurable performance regression from delegation overhead. Property access and one-line delegation methods have negligible overhead.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
