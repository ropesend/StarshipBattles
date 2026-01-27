# Phase 2: Fleet Ship Format Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove legacy string ship support. Ships must be `ShipInstance` objects only.

**Risk:** Medium - 12 files call `get_ship_instances()`, need methodical replacement

---

## Tasks

### Task 2.1: Update fleet.py type annotations [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Changes needed:**

- [ ] Line 60: Change `ships: List[Union[str, 'ShipInstance']]` to `ships: List['ShipInstance']`
- [ ] Lines 45-54: Update class docstring to remove mention of string format
- [ ] Remove import of `Union` if no longer needed
- [ ] Verify: `grep -n "Union\[str" game/strategy/data/fleet.py` returns nothing

**Notes:**

---

### Task 2.2: Remove get_ship_instances() method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Current State (Lines 101-104):**
```python
def get_ship_instances(self) -> List['ShipInstance']:
    """Return only ShipInstance objects, filtering out legacy strings."""
    return [s for s in self.ships if isinstance(s, ShipInstance)]
```

- [ ] Delete `get_ship_instances()` method entirely
- [ ] Verify: Method is removed from fleet.py

**Notes:** Callers will be updated in Task 2.4

---

### Task 2.3: Remove has_ship_instances() method and speed guard [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Current State:**
- Lines 124-127: `has_ship_instances()` method
- Lines 85-99: Speed recalculation guard for string-only fleets

- [ ] Delete `has_ship_instances()` method (lines 124-127)
- [ ] Remove guard in `_trigger_speed_recalculation()` that checks for string-only fleets
- [ ] The method should always proceed to calculate speed
- [ ] Verify: No `has_ship_instances` references in fleet.py

**Notes:**

---

### Task 2.4: Update callers of get_ship_instances() [Medium]
**Files:** Multiple files
**Tests:** `pytest tests/unit/strategy/ tests/integration/ -v`

**Files to update (replace `fleet.get_ship_instances()` with `fleet.ships`):**

| File | Line(s) | Context |
|------|---------|---------|
| `game/strategy/services/fleet_mobility_service.py` | ~106 | Speed calculation |
| `game/ui/screens/fleet_report_window.py` | ~752, 790 | Ship listing |
| `game/strategy/engine/turn_engine.py` | ~277, 464, 468 | Turn processing |

- [ ] `fleet_mobility_service.py`: Replace `fleet.get_ship_instances()` with `fleet.ships`
- [ ] `fleet_report_window.py`: Replace all occurrences
- [ ] `turn_engine.py`: Replace all occurrences
- [ ] Verify: `grep -rn "get_ship_instances" game/` returns nothing

**Notes:**

---

### Task 2.5: Simplify serialization [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Current State (Lines 589-666):**
- `to_dict()` preserves both string and ShipInstance formats
- `from_dict()` handles both formats

- [ ] Update `to_dict()` to only serialize ShipInstance objects
- [ ] Update `from_dict()` to only deserialize ShipInstance format
- [ ] Remove legacy string preservation logic
- [ ] Verify: Serialization roundtrip works for ShipInstance only

**Notes:**

---

### Task 2.6: Update get_ship_names() and related methods [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Current State:**
- `get_ship_names()` handles both strings and ShipInstance
- `get_combat_capable_ships()` filters for ShipInstance

- [ ] Simplify `get_ship_names()` to assume all ships are ShipInstance: `return [s.name for s in self.ships]`
- [ ] Simplify `get_combat_capable_ships()` to remove isinstance check
- [ ] Verify: Methods work correctly with ShipInstance only

**Notes:**

---

### Task 2.7: Remove legacy_string_fleet fixture [Simple]
**File:** `tests/unit/strategy/conftest.py`
**Tests:** `pytest tests/unit/strategy/ -v`

**Current State (Lines 256-270):**
```python
@pytest.fixture
def legacy_string_fleet():
    """Fleet with only legacy string ships."""
    ...
```

- [ ] Delete `legacy_string_fleet` fixture entirely
- [ ] Verify: No tests reference this fixture

**Notes:**

---

### Task 2.8: Remove/update legacy string ship tests [Medium]
**Files:** Multiple test files
**Tests:** Run full test suite after removal

Tests to remove/update:
- [ ] `tests/unit/strategy/test_fleet.py`: Remove `test_add_ship_string()` (if exists)
- [ ] `tests/unit/strategy/test_fleet.py`: Remove `test_get_ship_names_with_strings()` (if exists)
- [ ] `tests/unit/strategy/test_fleet.py`: Remove any tests for string-only fleets
- [ ] `tests/integration/test_resource_system.py`: Remove `TestFleetMixedLegacyAndNewShipInstances` class (if exists)
- [ ] Update any remaining tests that use string ships to use ShipInstance
- [ ] Verify: All fleet tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/test_fleet.py tests/unit/strategy/test_fleet_mobility_service.py -v` passes
- [ ] `grep -rn "Union\[str.*ShipInstance" game/` returns nothing
- [ ] `grep -rn "get_ship_instances\|has_ship_instances" game/` returns nothing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
