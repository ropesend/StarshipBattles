# Phase 3: Method/Property Aliases [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove method and property aliases from strategy and simulation layers

---

## Tasks

### Task 3.1: Fleet Warp Aliases [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

- [x] Update `tests/unit/strategy/test_fleet.py`:
  - Find tests using `has_energy_for_warp()` and update to `has_resources_for_warp()`
  - Find tests using `consume_warp_energy()` and update to `consume_warp_resources()`
  - Lines to check: 871-929 (backward compat tests)
- [x] Delete `has_energy_for_warp()` method in `game/strategy/data/fleet.py` (lines 350-360):
  ```python
  def has_energy_for_warp(self, distance: int = 1) -> bool:
      """DEPRECATED: Use has_resources_for_warp() instead."""
      return self.has_resources_for_warp(distance)
  ```
- [x] Delete `consume_warp_energy()` method in `game/strategy/data/fleet.py` (lines 392-403):
  ```python
  def consume_warp_energy(self, distance: int = 1) -> bool:
      """DEPRECATED: Use consume_warp_resources() instead."""
      return self.consume_warp_resources(distance)
  ```
- [x] Verify: Run tests - should pass (76 passed)

**Notes:** Already complete - methods were removed in a previous cleanup. Tests already use canonical names.

---

### Task 3.2: PathSegment `.hex` Property [Simple]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_movement.py tests/unit/strategy/test_pathfinding.py -v`

- [x] Delete `.hex` property in `game/strategy/engine/fleet_movement.py` (lines 43-46):
  ```python
  @property
  def hex(self) -> HexCoord:
      """Alias for end, for backward compatibility."""
      return self.end
  ```
- [x] Update `to_dict()` method (around line 53):
  - Remove `'hex': self.end` from the returned dict (keep only `'end': self.end`)
- [x] Check `tests/unit/strategy/test_pathfinding.py` (lines ~483-485):
  - If tests expect `'hex'` key in dict output, update to expect only `'end'`
- [x] Verify: Run tests - should pass (51 passed)

**Notes:** Updated all test expectations from 'hex' to 'end' key.

**AUDIT FINDING (2026-01-25):** Missed `tests/strategy/test_path_projection.py` which also uses `'hex'` key. Fixed in Phase 7.

---

### Task 3.3: `project_path_as_dicts()` Wrapper [Medium]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/unit/strategy/test_pathfinding.py -v`

- [x] Read `game/strategy/data/pathfinding.py` (line 227) to understand usage:
  - Currently calls `simulator.project_path_as_dicts()`
- [x] Update `game/strategy/data/pathfinding.py` (line 227):
  - Change to call `project_path()` directly
  - Convert PathSegment objects to dicts if needed: `[seg.to_dict() for seg in path]`
- [x] Update test mocks in `tests/unit/strategy/test_pathfinding.py`:
  - Lines 455, 461, 469, 474, 488: Update mock references
- [x] Delete `project_path_as_dicts()` method in `fleet_movement.py` (lines 307-314)
- [x] Verify: Run tests - should pass (51 passed)

**Notes:** Wrapper was already removed from fleet_movement.py. Updated pathfinding.py to call project_path() directly and convert to dicts.

---

### Task 3.4: `to_hit_profile` Alias [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [x] Update `data/stats_layout.json` (line 276):
  - Change `"key": "to_hit_profile"` to `"key": "total_defense_score"`
- [x] Update `tests/unit/builder/test_builder_improvements.py` (line 89):
  - Change `mock_ship.to_hit_profile = 1.0` to `mock_ship.total_defense_score = 1.0`
- [x] Delete alias assignment in `game/simulation/entities/ship_stats.py` (line 390):
  - Remove `ship.to_hit_profile = ship.total_defense_score`
- [x] Keep `ship.py:130` declaration `self.to_hit_profile: float = 1.0` for now (may be referenced elsewhere)
- [x] Verify: Run tests - should pass (275 passed)

**Notes:** Updated stats_layout.json, test mock, and removed alias assignment.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/ tests/unit/entities/ -v` - all pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
