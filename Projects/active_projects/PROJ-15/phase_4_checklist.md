# Phase 4: PathSegment & to_hit_profile Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove .hex property alias and to_hit_profile attribute alias

---

## Tasks

### Task 4.1: Remove PathSegment.hex Property [Simple]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/unit/strategy/test_pathfinding.py tests/unit/strategy/test_fleet_movement_engine.py -v`

- [ ] Delete lines 43-46: `hex` property definition
  ```python
  # DELETE THIS:
  @property
  def hex(self) -> HexCoord:
      """Alias for end, for backward compatibility."""
      return self.end
  ```
- [ ] Line 53: Remove `'hex': self.end` from `to_dict()` return dict (duplicate key)
- [ ] Verify: `grep -r "\.hex" game/strategy/ --include="*.py"` returns no PathSegment usages

**Notes:**

---

### Task 4.2: Remove to_hit_profile Alias [Simple]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_stats.py`, `data/stats_layout.json`
**Tests:** `pytest tests/unit/entities/ tests/unit/builder/test_builder_improvements.py -v`

- [ ] `game/simulation/entities/ship.py:130` - Delete line: `self.to_hit_profile: float = 1.0`
- [ ] `game/simulation/entities/ship_stats.py:389-390` - Delete alias assignment and comment:
  ```python
  # DELETE THESE LINES:
  # Legacy/Alias for UI until fully refactored
  ship.to_hit_profile = ship.total_defense_score
  ```
- [ ] `data/stats_layout.json:276` - Change `"key": "to_hit_profile"` to `"key": "total_defense_score"`
- [ ] `tests/unit/builder/test_builder_improvements.py:89` - Change `mock_ship.to_hit_profile = 1.0` to `mock_ship.total_defense_score = 1.0`
- [ ] Verify: `grep -r "to_hit_profile" game/ data/ --include="*.py" --include="*.json"` returns no results

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No remaining PathSegment.hex usages
- [ ] No remaining to_hit_profile references
- [ ] Run: `pytest tests/unit/strategy/test_pathfinding.py tests/unit/strategy/test_fleet_movement_engine.py tests/unit/entities/ tests/unit/builder/test_builder_improvements.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
