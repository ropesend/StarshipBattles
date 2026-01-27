# Phase 2: Replace Strategy Screen Duck Typing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-19 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the largest duck typing cluster to Protocol-based checks

---

## Tasks

### Task 2.1: Update strategy_screen.py show_detailed_report [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ui/test_strategy_screen.py -v` + manual testing

- [x] Add import: `from game.core.protocols import (is_star_system, is_star, is_planet, is_fleet, is_warp_point, is_sector_environment)`
- [x] Replace `hasattr(obj, 'stars')` with `is_star_system(obj)` (around line 446)
- [x] Replace `hasattr(obj, 'color') and hasattr(obj, 'mass')` with `is_star(obj)` (around line 467)
- [x] Replace `hasattr(obj, 'planet_type')` with `is_planet(obj)` (around line 481)
- [x] Replace `hasattr(obj, 'calculate_radiation')` with `is_sector_environment(obj)` (around line 491)
- [x] Replace `hasattr(obj, 'ships')` with `is_fleet(obj)` (around line 511)
- [x] Replace `hasattr(obj, 'destination_id')` with `is_warp_point(obj)` (around line 544)
- [x] Search for other hasattr patterns in file and evaluate for replacement
- [x] Verify: Run game, navigate strategy map, select each entity type - info displays correctly

**Notes:** Replaced 9 duck typing patterns total. Also replaced 3 additional `hasattr(obj, 'ships')` for fleet checks in button handlers. Kept scene/self attribute checks (hasattr(self, ...)) as those are appropriate.

---

### Task 2.2: Update strategy_detail_fmt.py [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ui/ -k "detail" -v` + manual testing

- [x] Add Protocol imports at top of file
- [x] Replace duck typing in `get_label_for_object()` function (around lines 222-244)
- [x] Verify: Labels display correctly for all entity types in game

**Notes:** Replaced 6 hasattr type checks with TypeGuard functions. Kept defensive hasattr in format_planet_info for resources/owner_id (within-type checks).

---

### Task 2.3: Update strategy_scene.py [Simple]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/ui/test_strategy_scene.py -v` + manual testing

- [x] Add Protocol imports at top of file
- [x] Identify hasattr patterns (search file for "hasattr")
- [x] Replace hasattr patterns with TypeGuard calls where appropriate
- [x] Verify: Entity rendering works correctly in game

**Notes:** Replaced 4 duck typing patterns in _get_object_asset(). Kept hasattr for self.session and self.build_queue_screen (attribute existence checks, not type checks).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run: `pytest tests/ui/ -v` - strategy tests pass (87 passed)
- [x] Run: `pytest tests/ --testmon -q` - no regressions
- [x] Manual test: Strategy map entity selection works for all types
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
