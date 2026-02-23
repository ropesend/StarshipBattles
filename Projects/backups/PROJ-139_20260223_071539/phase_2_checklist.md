# Phase 2: Galaxy Zone Registry

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-139 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add zone tracking to Galaxy. Register/unregister zones. Update lookups.

---

## Tasks

### Task 2.1: Add zone registry to Galaxy.__init__ [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] Add `self._global_hex_zones = {}` after `self._global_hex_planets = {}` (after line 107)
- [x] Verify: existing tests still pass

**Notes:** Added comment indicating PROJ-139 Phase 2.

### Task 2.2: Add `register_zone()`, `unregister_zone()`, `get_zones_at_global_hex()` [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] Add `register_zone(self, system, obj)` method after `register_planet` (~line 183)
- [x] Add `unregister_zone(self, system, obj)` method
- [x] Add `get_zones_at_global_hex(self, global_hex)` query method
- [x] Write tests:
  - `test_register_zone_adds_to_all_hexes`
  - `test_unregister_zone_removes_from_all_hexes`
  - `test_get_zones_at_global_hex_returns_object`
  - `test_get_zones_at_global_hex_empty_returns_empty_list`
  - `test_register_zone_no_duplicates`
- [x] Verify: `pytest tests/unit/strategy/data/test_galaxy.py` passes

**Notes:** All 5 new tests pass.

### Task 2.3: Register star zones during system setup [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] In `add_system()` (line 119): register zones for all stars after adding system
- [x] In `from_dict()` (after line 824): register star zones during deserialization
- [x] Write tests:
  - `test_add_system_registers_star_zones`
  - `test_from_dict_rebuilds_star_zones`
- [x] Verify: `pytest tests/unit/strategy/data/test_galaxy.py` passes

**Notes:** Both tests pass.

### Task 2.4: Update register_planet/unregister_planet for zone-aware planets [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] In `register_planet()` (after line 182): register zone for multi-hex planets (diameter_hexes > 0)
- [x] In `unregister_planet()` (before line 249): unregister zone for multi-hex planets
- [x] In `from_dict()` (after planet index rebuild): register planet zones
- [x] Write tests:
  - `test_register_dyson_sphere_planet_creates_zones`
  - `test_unregister_dyson_sphere_planet_removes_zones`
- [x] Verify: `pytest tests/unit/strategy/data/test_galaxy.py` passes

**Notes:** Both tests pass.

### Task 2.5: Update `get_system_at_location()` to check zones [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] After existing slow-path checks (line 311): add zone registry check before returning None
- [x] Write tests:
  - `test_get_system_at_location_finds_system_via_star_zone`
  - `test_get_system_at_location_finds_system_via_dyson_zone`
- [x] Verify: `pytest tests/unit/strategy/data/test_galaxy.py` passes

**Notes:** Both tests pass.

### Task 2.6: Update `get_all_fleets_in_system()` to include zones [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [x] After building system_hexes from stars (line 338): add star and planet zone hexes
- [x] Write test: `test_get_all_fleets_in_system_includes_zone_hexes`
- [x] Verify: `pytest tests/unit/strategy/data/test_galaxy.py` passes

**Notes:** Used getattr with isinstance check to handle MagicMock in existing tests.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (11925 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
