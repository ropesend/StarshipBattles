# Phase 1: Fix UI Encapsulation Violations & Extract Bridge Helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix live private access violations in 2 UI files and DRY up duplicate bridge code. Low risk, no API changes.

---

## Tasks

### Task 1.1: Fix stats_config.py private access [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [x] Replace `ship.resources._resources.keys()` with `ship.resources.get_resource_names()` (line 433)
- [x] Verify: stats_config still discovers all resource names (run builder tests)

**Notes:** Changed `set(ship.resources._resources.keys())` to `set(ship.resources.get_resource_names())`

---

### Task 1.2: Add get_all_resources() to ResourceRegistry [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [x] Add method after `get_resource_names()` (after line 199):
  ```python
  def get_all_resources(self) -> List['ResourceState']:
      """Return list of all registered ResourceState objects."""
      return list(self._resources.values())
  ```
- [x] Verify: `python -c "from game.simulation.systems.resource_manager import ResourceRegistry"`

**Notes:** Added get_all_resources() method to return list of ResourceState objects

---

### Task 1.3: Fix ship_stats_renderer.py private access [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ --testmon`

- [x] Replace lines 116-117:
  ```python
  # OLD (lines 116-117):
  if hasattr(ship.resources, '_resources'):
      all_res = list(ship.resources._resources.values())
  # NEW:
  all_res = ship.resources.get_all_resources()
  ```
- [x] Also remove the `if hasattr(ship.resources, '_resources'):` guard (line 116) since `get_all_resources()` is a proper public method
- [x] Verify: ship stats panel still renders resource bars correctly

**Notes:** Simplified to single line using public API, added `or not ship.resources` guard to hasattr check

---

### Task 1.4: Extract _capture_resource_levels() helper [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

- [x] Add static helper method to ShipInstance (before `from_ship` or in a logical location):
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
- [x] Update `from_ship()` (lines 180-186) to use helper:
  ```python
  # Replace lines 180-186 with:
  instance.resource_levels = cls._capture_resource_levels(ship)
  ```
- [x] Update `update_from_ship()` (lines 558-565) to use helper:
  ```python
  # Replace lines 558-565 with:
  self.resource_levels = self._capture_resource_levels(ship)
  ```
- [x] Run tests: `pytest tests/unit/strategy/ship_instance/ tests/integration/strategy/ --testmon`

**Notes:** Also removed defensive `getattr(ship, 'is_derelict', False)` calls and replaced with direct `ship.is_derelict` since IPostBattleShip declares it as required property

---

### Task 1.5: Run full test suite [Simple]
- [x] `pytest tests/ -n 12` -- all tests pass
- [x] Record test count: 7616 passed

**Notes:** Also fixed MockResourceContainer in test_build_queue_design_report.py to add get_resource_names() method

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
