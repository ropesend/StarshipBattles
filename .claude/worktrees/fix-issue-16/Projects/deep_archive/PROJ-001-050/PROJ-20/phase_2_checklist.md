# Phase 2: Fleet Ship Format Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove legacy string ship support. Ships must be `ShipInstance` objects only.

**Risk:** Medium - 12 files call `get_ship_instances()`, need methodical replacement

---

## Tasks

### Task 2.1: Update fleet.py type annotations [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Changes needed:**

- [x] Line 60: Change `ships: List[Union[str, 'ShipInstance']]` to `ships: List['ShipInstance']`
- [x] Lines 45-54: Update class docstring to remove mention of string format
- [x] Remove import of `Union` if no longer needed
- [x] Verify: `grep -n "Union\[str" game/strategy/data/fleet.py` returns nothing

**Notes:** Also updated add_ship() and remove_ship() signatures to ShipInstance only. All 70 fleet tests pass.

---

### Task 2.2: Remove get_ship_instances() method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] Delete `get_ship_instances()` method entirely
- [x] Verify: Method is removed from fleet.py

**Notes:** Removed method and updated internal caller in create_simulation_ships().

---

### Task 2.3: Remove has_ship_instances() method and speed guard [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] Delete `has_ship_instances()` method
- [x] Remove guard in `_trigger_speed_recalculation()` that checks for string-only fleets
- [x] The method should always proceed to calculate speed
- [x] Verify: No `has_ship_instances` references in fleet.py

**Notes:** Also updated turn_engine.py _resolve_combat() to use fleet.ships instead.

---

### Task 2.4: Update callers of get_ship_instances() [Medium]
**Files:** Multiple files
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -v`

- [x] `fleet_mobility_service.py`: Replace `fleet.get_ship_instances()` with `fleet.ships`
- [x] `fleet_report_window.py`: Replace all occurrences
- [x] `turn_engine.py`: Replace all occurrences
- [x] Verify: `grep -rn "get_ship_instances" game/` returns nothing

**Notes:** Updated fleet_mobility_service.py, fleet_report_window.py, turn_engine.py, and internal caller in fleet.py create_simulation_ships().

---

### Task 2.5: Simplify serialization [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] Update `to_dict()` to only serialize ShipInstance objects
- [x] Update `from_dict()` to only deserialize ShipInstance format
- [x] Remove legacy string preservation logic
- [x] Verify: Serialization roundtrip works for ShipInstance only

**Notes:** Simplified to_dict() to just call s.to_dict() for each ship, from_dict() to just call ShipInstance.from_dict().

---

### Task 2.6: Update get_ship_names() and related methods [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] Simplify `get_ship_names()` to assume all ships are ShipInstance: `return [s.name for s in self.ships]`
- [x] Simplify `get_combat_capable_ships()` to remove isinstance check
- [x] Verify: Methods work correctly with ShipInstance only

**Notes:** Simplified both methods to direct attribute access.

---

### Task 2.7: Remove legacy_string_fleet fixture [Simple]
**File:** `tests/unit/strategy/conftest.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Delete `legacy_string_fleet` fixture entirely
- [x] Verify: No tests reference this fixture

**Notes:** Fixture was unused, removed.

---

### Task 2.8: Remove/update legacy string ship tests [Medium]
**Files:** Multiple test files
**Tests:** Run full test suite after removal

- [x] `tests/unit/strategy/test_fleet.py`: Removed `test_add_ship_string()`, updated to `test_add_ship()`
- [x] `tests/unit/strategy/test_fleet.py`: Removed `test_get_ship_names_with_strings()`, updated to `test_get_ship_names()`
- [x] `tests/unit/strategy/test_fleet.py`: Removed legacy string-only tests (movement/warp costs legacy tests)
- [x] `tests/integration/test_resource_system.py`: Removed `TestFleetMixedLegacyAndNewShipInstances` class
- [x] Update any remaining tests that use string ships to use ShipInstance
- [x] Verify: All fleet tests pass

**Notes:** Updated tests in test_fleet.py, test_fleet_mobility_service.py, test_turn_engine.py, test_production_engine.py, test_colonization.py, test_gameplay_loop.py, test_save_load.py, test_advanced_fleet_orders.py to use ShipInstance mocks.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/test_fleet.py tests/unit/strategy/test_fleet_mobility_service.py -v` passes
- [x] `grep -rn "Union\[str.*ShipInstance" game/` returns nothing
- [x] `grep -rn "get_ship_instances\|has_ship_instances" game/` returns nothing
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
