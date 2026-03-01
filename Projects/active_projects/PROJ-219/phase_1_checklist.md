# Phase 1: Core Empire Changes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `_galaxy` infrastructure to Empire class for automatic fleet registration/unregistration

---

## Tasks

### Task 1.1: Add `_galaxy` parameter and storage [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [ ] Add `galaxy: 'Galaxy' = None` parameter to `__init__` signature (line 16-17, after `race_config`)
- [ ] Add `self._galaxy = galaxy` in `__init__` body (after line 44)
- [ ] Add TYPE_CHECKING import for Galaxy if not present:
  ```python
  if TYPE_CHECKING:
      from game.strategy.data.galaxy import Galaxy
  ```
- [ ] Verify: Empire can be constructed with and without galaxy parameter

**Notes:** [Filled during implementation]

---

### Task 1.2: Add `set_galaxy()` method [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [ ] Add `set_galaxy()` method after `get_next_serial()` (around line 86):
  ```python
  def set_galaxy(self, galaxy: 'Galaxy') -> None:
      """Set galaxy reference for auto-registration.

      Call after construction when galaxy is available later
      (e.g., during deserialization).
      """
      self._galaxy = galaxy
  ```
- [ ] Verify: Method sets `_galaxy` correctly

**Notes:**

---

### Task 1.3: Modify `add_fleet()` to auto-register [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [ ] Modify `add_fleet()` (lines 56-58) to call register:
  ```python
  def add_fleet(self, fleet):
      """Add fleet to empire and register with galaxy for O(1) lookup."""
      self.fleets.append(fleet)
      fleet.owner_id = self.id
      if self._galaxy:
          self._galaxy.register_fleet(fleet)
  ```
- [ ] Verify: Fleet added to empire AND registered with galaxy when galaxy is set
- [ ] Verify: Fleet added to empire ONLY when galaxy is None (no crash)

**Notes:**

---

### Task 1.4: Modify `remove_fleet()` to auto-unregister [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

- [ ] Modify `remove_fleet()` (lines 60-62) to call unregister:
  ```python
  def remove_fleet(self, fleet):
      """Remove fleet from empire and unregister from galaxy."""
      if fleet in self.fleets:
          self.fleets.remove(fleet)
          if self._galaxy:
              self._galaxy.unregister_fleet(fleet)
  ```
- [ ] Verify: Fleet removed from empire AND unregistered from galaxy when galaxy is set
- [ ] Verify: Fleet removed from empire ONLY when galaxy is None (no crash)

**Notes:**

---

### Task 1.5: Create unit tests [Medium]
**File:** `tests/unit/strategy/data/test_empire_fleet_registration.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_empire_fleet_registration.py`

Create new test file with:
- [ ] `test_add_fleet_without_galaxy_does_not_crash`
- [ ] `test_add_fleet_with_galaxy_auto_registers`
- [ ] `test_remove_fleet_with_galaxy_auto_unregisters`
- [ ] `test_remove_fleet_without_galaxy_does_not_crash`
- [ ] `test_set_galaxy_enables_registration`
- [ ] `test_remove_fleet_not_in_list_does_not_crash`

**Test template:**
```python
"""Tests for Empire fleet auto-registration (PROJ-219)."""
import pytest
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.core.hex_math import HexCoord


class TestEmpireFleetAutoRegistration:
    """Tests for automatic fleet registration/unregistration."""

    def test_add_fleet_without_galaxy_does_not_crash(self):
        """Empire without galaxy can still add fleets."""
        empire = Empire(0, "Test", (255, 0, 0))
        fleet = Fleet(1, 0, HexCoord(0, 0))
        empire.add_fleet(fleet)
        assert fleet in empire.fleets
        assert fleet.owner_id == 0

    # ... more tests ...
```

- [ ] All 6 tests pass

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/data/test_empire_fleet_registration.py` - all pass
- [ ] Run `pytest tests/ --testmon` - no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
