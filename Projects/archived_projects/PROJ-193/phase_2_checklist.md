# Phase 2: Type Discrimination Replacements [12 instances]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-193 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace `hasattr(obj, 'planet_type')` / `hasattr(obj, 'ships')` patterns with existing TypeGuard functions from `game.core.protocols`.

---

## Tasks

### Task 2.1: strategy_camera_nav.py [Simple]
**File:** `game/ui/screens/strategy_camera_nav.py` (lines 60-82)
**Tests:** `pytest tests/unit/ui/`

- [x] Add import: `from game.core.protocols import is_planet, is_fleet, is_star_system`
- [x] Replace `_resolve_global_hex()` method (lines 60-82):
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
- [x] Line 138: Replace `isinstance(self.scene.selected_object, StarSystem)` with `is_star_system(self.scene.selected_object)`
- [x] Remove `from game.strategy.data.galaxy import StarSystem` if no longer needed
- [x] Verify: Run tests

**Notes:** Removed StarSystem import completely - all uses now via protocols

### Task 2.2: strategy_colonization.py [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add import: `from game.core.protocols import is_planet`
- [x] Lines 81-87: Replace `hasattr(zone_obj, 'planet_type')` with `is_planet(zone_obj)`
- [x] Lines 195-202: Same pattern in second method
- [x] Verify: Run tests

**Notes:** Also replaced getattr(zone_obj, 'owner_id', None) with direct access since is_planet() guarantees owner_id property

### Task 2.3: fleet_orders_window.py [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Line 167: Replace `hasattr(t, 'q') and hasattr(t, 'r')` with `isinstance(t, HexCoord)` (import HexCoord if not already imported)
- [x] Lines 172-178: Replace `hasattr(order.target, 'name')`, `hasattr(order.target, 'id')` with appropriate TypeGuard or isinstance checks
- [x] Verify: Run tests

**Notes:** Used is_planet and is_fleet for COLONIZE and INTERCEPT/JOIN order targets

### Task 2.4: planet_report_panel.py type checks [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [x] Line 203: Remove `hasattr(self.planet, 'planet_type')` guard — `planet_type` is always present on Planet (it's in the Protocol)
- [x] Line 263: Remove `hasattr(self.planet, 'facilities')` guard — `facilities` is always present on Planet (now in extended Protocol)
- [x] Verify: Run tests

**Notes:** Simplified conditionals since IPlanet guarantees these properties

### Task 2.5: strategy_widgets.py [Simple]
**File:** `game/ui/panels/strategy_widgets.py`
**Tests:** `pytest tests/unit/ui/panels/`

- [x] Line 33: Replace `hasattr(star, 'spectrum')` with `is_star(star)` (import from protocols)
- [x] Line 114: Remove `hasattr(planet, 'atmosphere')` guard — `atmosphere` is always present on Planet (now in extended Protocol)
- [x] Verify: Run tests

**Notes:** Added is_star import. Deleted obsolete test_render_handles_no_atmosphere test (atmosphere is always present per Protocol)

### Task 2.6: Run tests [Simple]
**Tests:** Full suite

- [x] Run: `pytest tests/unit/ui/ -n 4` — all pass
- [x] Run: `pytest tests/ -n 12` (full suite checkpoint) — all pass

**Notes:** 12711 passed, 1 skipped. Deleted 1 obsolete test.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
