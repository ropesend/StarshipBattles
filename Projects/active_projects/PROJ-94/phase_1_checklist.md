# Phase 1: Fix UI Encapsulation Violations & Extract Bridge Helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix live private access violations in 2 UI files and DRY up duplicate bridge code. Low risk, no API changes.

---

## Tasks

### Task 1.1: Fix stats_config.py private access [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] Replace `ship.resources._resources.keys()` with `ship.resources.get_resource_names()` (line 433)
- [ ] Verify: stats_config still discovers all resource names (run builder tests)

**Notes:**

---

### Task 1.2: Add get_all_resources() to ResourceRegistry [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [ ] Add method after `get_resource_names()` (after line 199):
  ```python
  def get_all_resources(self) -> List['ResourceState']:
      """Return list of all registered ResourceState objects."""
      return list(self._resources.values())
  ```
- [ ] Verify: `python -c "from game.simulation.systems.resource_manager import ResourceRegistry"`

**Notes:** This is needed because `ship_stats_renderer.py` uses `._resources.values()` to get ResourceState objects (for `.name`, `.current_value`, `.max_value`).

---

### Task 1.3: Fix ship_stats_renderer.py private access [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] Replace lines 116-117:
  ```python
  # OLD (lines 116-117):
  if hasattr(ship.resources, '_resources'):
      all_res = list(ship.resources._resources.values())
  # NEW:
  all_res = ship.resources.get_all_resources()
  ```
- [ ] Also remove the `if hasattr(ship.resources, '_resources'):` guard (line 116) since `get_all_resources()` is a proper public method
- [ ] Verify: ship stats panel still renders resource bars correctly

**Notes:**

---

### Task 1.4: Extract _capture_resource_levels() helper [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

- [ ] Add static helper method to ShipInstance (before `from_ship` or in a logical location):
  ```python
  @staticmethod
  def _capture_resource_levels(ship) -> Dict[str, float]:
      """Extract non-full resource levels from a post-battle Ship."""
      levels = {}
      if ship.resources:
          for name in ship.resources.get_resource_names():
              current = ship.resources.get_value(name)
              max_val = ship.resources.get_max_value(name)
              if current < max_val:
                  levels[name] = current
      return levels
  ```
- [ ] Update `from_ship()` (lines 180-186) to use helper:
  ```python
  # Replace lines 180-186 with:
  instance.resource_levels = cls._capture_resource_levels(ship)
  ```
- [ ] Update `update_from_ship()` (lines 558-565) to use helper:
  ```python
  # Replace lines 558-565 with:
  self.resource_levels = self._capture_resource_levels(ship)
  ```
- [ ] Run tests: `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

**Notes:**

---

### Task 1.5: Run full test suite [Simple]
- [ ] `pytest tests/ -n 12` -- all tests pass
- [ ] Record test count

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
