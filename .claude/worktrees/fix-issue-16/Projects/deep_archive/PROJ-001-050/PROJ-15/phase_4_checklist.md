# Phase 4: PathSegment & to_hit_profile Aliases [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove .hex property alias and to_hit_profile attribute alias

---

## Tasks

### Task 4.1: Remove PathSegment.hex Property [Simple]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `pytest tests/unit/strategy/test_pathfinding.py tests/unit/strategy/test_fleet_movement_engine.py -v`

- [x] Delete lines 43-46: `hex` property definition
- [x] Remove `'hex': self.end` from `to_dict()` return dict (duplicate key)
- [x] Verify: `grep -r "\.hex" game/strategy/ --include="*.py"` returns no PathSegment usages (only uuid.hex)

**Notes:** Also updated docstring for to_dict() from "backward compatibility" to "serialization"

---

### Task 4.2: Remove to_hit_profile Alias [Simple]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_stats.py`, `data/stats_layout.json`
**Tests:** `pytest tests/unit/entities/ tests/unit/builder/test_builder_improvements.py -v`

- [x] `game/simulation/entities/ship.py:130` - Changed to use `total_defense_score` directly (not just deleted)
- [x] `game/simulation/entities/ship_stats.py:389-390` - Delete alias assignment and comment
- [x] `data/stats_layout.json:276` - Change `"key": "to_hit_profile"` to `"key": "total_defense_score"`
- [x] `tests/unit/builder/test_builder_improvements.py:89` - Change `mock_ship.to_hit_profile` to `mock_ship.total_defense_score`
- [x] Verify: `grep -r "to_hit_profile" game/ data/ --include="*.py" --include="*.json"` returns no results

**Notes:** One comment in tests/unit/entities/test_stacking_rules.py still mentions the old name for historical context - left as is.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No remaining PathSegment.hex usages
- [x] No remaining to_hit_profile references (except one historical comment in test)
- [x] Run: `pytest tests/unit/strategy/test_pathfinding.py tests/unit/strategy/test_fleet_movement_engine.py tests/unit/entities/ tests/unit/builder/test_builder_improvements.py -v` - 355 tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
