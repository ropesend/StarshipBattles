# Phase 2: Extract ShipCombatManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move combat orchestration (update loop, derelict status, death, firing state) into ShipCombatManager delegate. Ship retains facade methods and property accessors for direct-write attributes.

---

## Tasks

### Task 2.1: Write tests for ShipCombatManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_combat_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_combat_manager.py -v`

- [ ] Test `update()` short-circuits when `ship.is_alive` is False
- [ ] Test `update()` calls subsystems in correct order (resources, components, stats, physics, combat, firing)
- [ ] Test `update()` firing: comp_trigger_pulled=True -> fire_weapons results extend just_fired_projectiles
- [ ] Test `update()` firing: comp_trigger_pulled=False -> no firing
- [ ] Test `update_derelict_status` crew check: insufficient crew -> derelict
- [ ] Test `update_derelict_status` capability check: no weapons AND no engines -> derelict
- [ ] Test `update_derelict_status` recovery: was derelict, now has weapons -> not derelict
- [ ] Test `update_derelict_status` resets bridge_destroyed
- [ ] Test `die()` sets is_alive=False, zeroes velocity, calls recalculate_stats
- [ ] Test `combat_engine` lazy creation
- [ ] Run tests -- confirm they FAIL

**Notes:**

---

### Task 2.2: Implement ShipCombatManager [Medium]
**File:** `game/simulation/entities/ship_combat_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_combat_manager.py -v`

Move these methods from ship.py (line numbers refer to current ship.py before Phase 1 changes):

- [ ] Create class with `__init__(self, ship)` owning combat state
- [ ] Move `combat_engine` property (lines 253-262) -- lazy ShipCombatEngine creation
- [ ] Move `die()` (lines 264-269) -- calls `self._ship.recalculate_stats()`
- [ ] Move `update()` (lines 299-336) -- preserve exact ordering; reference ship via `self._ship`
- [ ] Move `update_derelict_status()` (lines 338-373)
- [ ] Own state: `just_fired_projectiles`, `total_shots_fired`, `comp_trigger_pulled`, `aim_point`
- [ ] Run tests -- confirm they PASS

**Notes:**

---

### Task 2.3: Wire Ship facade to ShipCombatManager [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py tests/unit/simulation/ tests/integration/ -v`

- [ ] Add `self._combat_manager = None` to `__init__`
- [ ] Add `combat_manager` lazy property
- [ ] Replace `combat_engine` property with delegation through combat_manager
- [ ] Replace `update()`, `die()`, `update_derelict_status()` with delegations
- [ ] Add `just_fired_projectiles` as property with getter/setter delegating to combat_manager
- [ ] Add `comp_trigger_pulled` as property with getter/setter delegating to combat_manager
- [ ] Add `aim_point` as property with getter/setter delegating to combat_manager
- [ ] Remove moved state from `__init__`
- [ ] Run ship unit tests
- [ ] Run simulation unit tests
- [ ] Run integration tests
- [ ] Run simulation lab: `python -m simulation_tests.run_tests --fast`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
