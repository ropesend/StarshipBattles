# Phase 5: Planet List State Unification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate Planet List to use FilterStateManager infrastructure for state management. No tri-state UI conversion (no binary filters exist yet). Fix broken owner filter preset restore. Ensure future binary filters will use tri-state automatically.

---

## Tasks

### Task 5.1: Create PlanetListFilterManager using FilterStateManager [Medium]
**File:** `game/ui/screens/planet_list_filter_manager.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filter_manager.py`

- [x] Create `game/ui/screens/planet_list_filter_manager.py`:
  - `PlanetListFilterManager` class with filter_types, filter_owner, filter_ranges, search_text
  - `toggle_type()`, `toggle_owner()`, `set_all_types()`, `set_all_owners()`, `get_filter_state()`
  - Includes `FilterStateManager` for future binary/tri-state filters
  - No pygame imports. Pure Python.
- [x] Create `tests/unit/ui/screens/test_planet_list_filter_manager.py`:
  - 17 tests covering initialization, toggles, set_all, get_filter_state
- [x] Verify: `pytest tests/unit/ui/screens/test_planet_list_filter_manager.py` passes

**Notes:** Clean implementation following Build Queue pattern. 17 tests all passing.

---

### Task 5.2: Migrate PlanetListWindow to use PlanetListFilterManager [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filters.py`

- [x] Import `PlanetListFilterManager`
- [x] Replace direct state attributes with `self._filter_mgr = PlanetListFilterManager()`
- [x] Added property accessors for `filter_types`, `filter_owner`, `filter_ranges` delegating to filter manager
- [x] `_handle_filter_toggles()` works unchanged (mutates dict references from properties)
- [x] `refresh_list()` works unchanged (reads filter state through properties)
- [x] Verify: `pytest tests/unit/ui/screens/test_planet_list_filters.py` passes
- [x] Verify: `pytest tests/unit/ui/screens/test_planet_list_components.py` passes

**Notes:** Property-based delegation is transparent to all existing call sites. No behavioral changes. 35 existing tests pass unchanged.

---

### Task 5.3: Fix broken owner filter preset restore [Simple]
**File:** `game/ui/screens/planet_list_presets.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_components.py`

- [x] Fix `apply_planet_list_state()` signature — added `filter_owner` parameter
- [x] Add owner filter restoration logic:
  - Read `state['filters']['owner']` if present
  - Update `filter_owner` dict with saved values
  - Update owner toggle button appearances (select/unselect + text)
- [x] Update `PlanetListWindow._apply_state()` to pass `filter_owner`
- [x] Add migration safety: if preset lacks 'owner' key, filter_owner unchanged
- [x] Added 3 tests: owner filter apply, button updates, missing key safety
- [x] Verify: preset save → load round-trip preserves owner filter state

**Notes:** Fixed pre-existing bug (BUG-27 gap). Owner filter was captured but never restored. 3 new tests.

---

### Task 5.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All 13,300 tests pass (0 failures, 2 skipped)
- [x] No regressions from Planet List changes

**Notes:** Full suite: 13,300 passed, 2 skipped in 96s. Up from 13,280 (20 net new tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] PlanetListFilterManager exists and encapsulates filter state
- [x] PlanetListWindow delegates to filter manager
- [x] Owner filter preset restore is fixed
- [x] All planet list tests passing (55 tests)
- [x] Full test suite passes (13,300 passed, 2 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
