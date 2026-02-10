# Phase 3: Eliminate None-Means-Full Convention

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-95 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Always store actual resource values in `resource_levels`. Initialize at creation. Remove sparse-dict patterns. Simplify getters.

---

## Tasks

### Task 3.1: Initialize resource_levels at creation [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ --testmon`

- [ ] In `create()` factory method (lines 94-142): After design_data is set, populate resource_levels with max values:
  ```python
  # Initialize all resources to full
  stats = instance.get_calculated_stats()
  storage = stats.get('resource_storage', {})
  instance.resource_levels = {name: float(val) for name, val in storage.items()}
  ```
- [ ] In `from_ship()` bridge method: Store ALL resources, not just non-full (update the `_capture_resource_levels` helper or inline):
  ```python
  # OLD (only stores non-full):
  if current < max_val:
      levels[name] = current
  # NEW (always store):
  levels[name] = current
  ```
- [ ] In `update_from_ship()`: Same change -- store all resources
- [ ] Run: `pytest tests/unit/strategy/ship_instance/ --testmon`

**Notes:** The `_capture_resource_levels()` helper (extracted in PROJ-94) will need modification. Either update the helper to always store values, or rename it to `_capture_all_resource_levels()`.

---

### Task 3.2: Simplify ShipResourceManager getters [Simple]
**File:** `game/strategy/data/ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py --testmon`

- [ ] `get_current_resource()` (line ~165 after PROJ-94): Change `.get(resource_type, max_val)` to `.get(resource_type, 0.0)` (safe fallback for unexpected missing key)
- [ ] `consume_resource()` (line ~184 after PROJ-94): Same simplification
- [ ] `resupply()` (lines ~237-251 after PROJ-94): Remove sparse-dict pattern entirely:
  ```python
  # OLD:
  if resource_name not in self._ship.resource_levels:
      return 0  # Already at full
  ...
  if new_val >= max_val:
      del self._ship.resource_levels[resource_name]
      return max_val - old_val

  # NEW:
  def resupply(self, resource_name: str, amount: float) -> float:
      max_val = self.get_resource_capacity(resource_name)
      old_val = self._ship.resource_levels.get(resource_name, 0.0)
      new_val = min(max_val, old_val + amount)
      self._ship.resource_levels[resource_name] = new_val
      return new_val - old_val
  ```
- [ ] Run: `pytest tests/unit/strategy/test_ship_resource_manager.py --testmon`

**Notes:** Line numbers will have shifted after PROJ-94 Phase 2 deleted type-specific methods. Verify actual line numbers before editing.

---

### Task 3.3: Simplify ShipDisplayFormatter [Simple]
**File:** `game/strategy/data/ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/test_ship_display_formatter.py --testmon`

- [ ] `get_resource_display()` (lines ~90-93): Remove `if resource_name in self._ship.resource_levels:` check -- just read value directly:
  ```python
  current = int(self._ship.resource_levels.get(resource_name, 0))
  ```
- [ ] `get_resource_percentage()` (lines ~107-108): Remove `if resource_name not in self._ship.resource_levels: return 1.0` early return -- just compute from stored value
- [ ] Run: `pytest tests/unit/strategy/test_ship_display_formatter.py --testmon`

**Notes:**

---

### Task 3.4: Update fleet_report_filters.py [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_report_filters.py --testmon`

- [ ] Lines ~73-76 (fuel aggregation): Remove `if 'fuel' in ship.resource_levels:` check -- just read value directly (use ResourceType.FUEL constant from Phase 1)
- [ ] Lines ~81-84 (energy aggregation): Remove `if 'energy' in ship.resource_levels:` check -- just read value directly (use ResourceType.ENERGY constant)
- [ ] Run: `pytest tests/unit/strategy/test_fleet_report_filters.py --testmon`

**Notes:**

---

### Task 3.5: Update tests [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Update tests that verify "key absent = full" behavior -- now key should always be present with max value
- [ ] Update tests that verify `del` on resupply -- now key should remain with max value
- [ ] Update tests that check `resource_levels == {}` for full ships -- now should be `resource_levels == {ResourceType.FUEL: max_fuel, ResourceType.ENERGY: max_energy, ResourceType.AMMO: max_ammo}`
- [ ] Update `test_resupply_to_full` and `test_resupply_already_full` in `test_ship_resource_manager.py`
- [ ] Update `test_get_current_resource_returns_default_when_full` in `test_capacity_levels.py`
- [ ] Run: `pytest tests/ -n 12`

**Notes:** Search for tests referencing `resource_levels` being empty dict or checking key absence.

---

### Task 3.6: Verification [Simple]
- [ ] Grep: No `.get(resource_type, max` or `.get('fuel', max` patterns in strategy layer
- [ ] Grep: No `del self._ship.resource_levels` in strategy layer
- [ ] Grep: No `not in self._ship.resource_levels` patterns in strategy layer
- [ ] Grep: No `resource_name in self._ship.resource_levels` patterns (checking key presence for "is tracked")
- [ ] Full test suite: `pytest tests/ -n 12` -- all pass
- [ ] Record test count

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
