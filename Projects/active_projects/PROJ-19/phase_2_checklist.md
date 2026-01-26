# Phase 2: Replace Strategy Screen Duck Typing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the largest duck typing cluster to Protocol-based checks

---

## Tasks

### Task 2.1: Update strategy_screen.py show_detailed_report [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ui/test_strategy_screen.py -v` + manual testing

- [ ] Add import: `from game.core.protocols import (is_star_system, is_star, is_planet, is_fleet, is_warp_point, is_sector_environment)`
- [ ] Replace `hasattr(obj, 'stars')` with `is_star_system(obj)` (around line 446)
- [ ] Replace `hasattr(obj, 'color') and hasattr(obj, 'mass')` with `is_star(obj)` (around line 467)
- [ ] Replace `hasattr(obj, 'planet_type')` with `is_planet(obj)` (around line 481)
- [ ] Replace `hasattr(obj, 'calculate_radiation')` with `is_sector_environment(obj)` (around line 491)
- [ ] Replace `hasattr(obj, 'ships')` with `is_fleet(obj)` (around line 511)
- [ ] Replace `hasattr(obj, 'destination_id')` with `is_warp_point(obj)` (around line 544)
- [ ] Search for other hasattr patterns in file and evaluate for replacement
- [ ] Verify: Run game, navigate strategy map, select each entity type - info displays correctly

**Notes:**

---

### Task 2.2: Update strategy_detail_fmt.py [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ui/ -k "detail" -v` + manual testing

- [ ] Add Protocol imports at top of file
- [ ] Replace duck typing in `get_label_for_object()` function (around lines 222-244)
- [ ] Verify: Labels display correctly for all entity types in game

**Notes:**

---

### Task 2.3: Update strategy_scene.py [Simple]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/ui/test_strategy_scene.py -v` + manual testing

- [ ] Add Protocol imports at top of file
- [ ] Identify hasattr patterns (search file for "hasattr")
- [ ] Replace hasattr patterns with TypeGuard calls where appropriate
- [ ] Verify: Entity rendering works correctly in game

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run: `pytest tests/ui/ -v` - strategy tests pass
- [ ] Run: `pytest tests/ --testmon -q` - no regressions
- [ ] Manual test: Strategy map entity selection works for all types
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
