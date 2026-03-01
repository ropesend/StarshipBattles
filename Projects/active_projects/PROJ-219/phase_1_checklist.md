# Phase 1: Core Empire Changes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `_galaxy` infrastructure to Empire class for automatic fleet registration/unregistration

---

## Tasks

### Task 1.1: Add `_galaxy` parameter and storage [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [x] Add `galaxy: 'Galaxy' = None` parameter to `__init__` signature (line 16-17, after `race_config`)
- [x] Add `self._galaxy = galaxy` in `__init__` body (after line 44)
- [x] Add TYPE_CHECKING import for Galaxy if not present:
  ```python
  if TYPE_CHECKING:
      from game.strategy.data.galaxy import Galaxy
  ```
- [x] Verify: Empire can be constructed with and without galaxy parameter

**Notes:** Used `self._galaxy: Optional['Galaxy'] = None` as instance attribute (not constructor param) since set_galaxy() is the primary setter. TYPE_CHECKING import added for Galaxy.

---

### Task 1.2: Add `set_galaxy()` method [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [x] Add `set_galaxy()` method after `get_next_serial()` (around line 86):
- [x] Verify: Method sets `_galaxy` correctly

**Notes:** Added between get_next_serial() and Resource Economy Methods section.

---

### Task 1.3: Modify `add_fleet()` to auto-register [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [x] Modify `add_fleet()` to call register
- [x] Verify: Fleet added to empire AND registered with galaxy when galaxy is set
- [x] Verify: Fleet added to empire ONLY when galaxy is None (no crash)

**Notes:** Added `if self._galaxy: self._galaxy.register_fleet(fleet)` guard.

---

### Task 1.4: Modify `remove_fleet()` to auto-unregister [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [x] Modify `remove_fleet()` to call unregister
- [x] Verify: Fleet removed from empire AND unregistered from galaxy when galaxy is set
- [x] Verify: Fleet removed from empire ONLY when galaxy is None (no crash)

**Notes:** Added `if self._galaxy: self._galaxy.unregister_fleet(fleet)` inside the `if fleet in self.fleets:` guard.

---

### Task 1.5: Create unit tests [Medium]
**File:** `tests/unit/strategy/data/test_empire_fleet_registration.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [x] `test_add_fleet_without_galaxy_does_not_crash`
- [x] `test_add_fleet_with_galaxy_auto_registers`
- [x] `test_remove_fleet_with_galaxy_auto_unregisters`
- [x] `test_remove_fleet_without_galaxy_does_not_crash`
- [x] `test_set_galaxy_enables_registration`
- [x] `test_remove_fleet_not_in_list_does_not_crash`

- [x] All 7 tests pass (6 planned + 1 bonus: test_galaxy_not_serialized)

**Notes:** Used MagicMock for galaxy to isolate Empire behavior. Added bonus test verifying _galaxy is not in to_dict() output.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/data/test_empire_fleet_registration.py` - all 7 pass
- [x] Run `pytest tests/ -n 12` - 13152 passed, 1 skipped (no regressions)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
