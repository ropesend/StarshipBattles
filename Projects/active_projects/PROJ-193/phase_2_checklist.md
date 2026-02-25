# Phase 2: Type Discrimination Replacements [12 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace `hasattr(obj, 'planet_type')` / `hasattr(obj, 'ships')` patterns with existing TypeGuard functions from `game.core.protocols`.

---

## Tasks

### Task 2.1: strategy_camera_nav.py [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py` (lines 60-82)
**Tests:** `pytest tests/unit/ui/`

- [ ] Add import: `from game.core.protocols import is_planet, is_fleet, is_star_system`
- [ ] Replace `_resolve_global_hex()` method (lines 60-82):
  ```python
  # OLD:
  if hasattr(obj, 'location'):
      if hasattr(obj, 'planet_type'):  # Planet
      elif hasattr(obj, 'ships'):  # Fleet
      elif hasattr(obj, 'global_location'):  # System

  # NEW:
  if is_planet(obj):
      sys = next((s for s in self.systems if obj in s.planets), None)
      if sys:
          return sys.global_location + obj.location
  elif is_fleet(obj):
      return obj.location
  elif is_star_system(obj):
      return obj.global_location
  ```
- [ ] Line 138: Replace `isinstance(self.scene.selected_object, StarSystem)` with `is_star_system(self.scene.selected_object)`
- [ ] Remove `from game.strategy.data.galaxy import StarSystem` if no longer needed
- [ ] Verify: Run tests

**Notes:**

### Task 2.2: strategy_colonization.py [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add import: `from game.core.protocols import is_planet`
- [ ] Lines 81-87: Replace `hasattr(zone_obj, 'planet_type')` with `is_planet(zone_obj)`
- [ ] Lines 195-202: Same pattern in second method
- [ ] Verify: Run tests

**Notes:**

### Task 2.3: fleet_orders_window.py [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Line 167: Replace `hasattr(t, 'q') and hasattr(t, 'r')` with `isinstance(t, HexCoord)` (import HexCoord if not already imported)
- [ ] Lines 172-178: Replace `hasattr(order.target, 'name')`, `hasattr(order.target, 'id')` with appropriate TypeGuard or isinstance checks
- [ ] Verify: Run tests

**Notes:**

### Task 2.4: planet_report_panel.py type checks [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [ ] Line 203: Remove `hasattr(self.planet, 'planet_type')` guard — `planet_type` is always present on Planet (it's in the Protocol)
- [ ] Line 263: Remove `hasattr(self.planet, 'facilities')` guard — `facilities` is always present on Planet (now in extended Protocol)
- [ ] Verify: Run tests

**Notes:**

### Task 2.5: strategy_widgets.py [Simple]
**File:** `game/ui/panels/strategy_widgets.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [ ] Line 33: Replace `hasattr(star, 'spectrum')` with `is_star(star)` (import from protocols)
- [ ] Line 114: Remove `hasattr(planet, 'atmosphere')` guard — `atmosphere` is always present on Planet (now in extended Protocol)
- [ ] Verify: Run tests

**Notes:**

### Task 2.6: Run tests [Simple]
**Tests:** Full suite

- [ ] Run: `pytest tests/unit/ui/ -n 4` — all pass
- [ ] Run: `pytest tests/ -n 12` (full suite checkpoint) — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
