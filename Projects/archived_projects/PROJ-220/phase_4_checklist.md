# Phase 4: Retrofit Build Queue

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace Build Queue's 3 binary filter groups with tri-state widgets backed by FilterStateManager.

---

## Tasks

### Task 4.1: Refactor BuildQueueFilterManager to use FilterStateManager [Medium]
**File:** `game/ui/screens/empire_build_queue_filter_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_filter_manager.py`

- [x] Import `FilterState, FilterStateManager` from `game.ui.filters`
- [x] Replace 3 filter dicts with a single FilterStateManager:
  ```python
  self._filter_mgr = FilterStateManager({
      'loc_Planet': FilterState.IGNORE,
      'loc_Fleet': FilterState.IGNORE,
      'status_Active': FilterState.IGNORE,
      'status_Empty': FilterState.IGNORE,
      'cap_Ships': FilterState.IGNORE,
      'cap_Complexes': FilterState.IGNORE,
  })
  ```
  Note: Build Queue's existing keys are category-prefixed (`loc_`, `status_`, `cap_`). Keep this convention for backward compat with ViewModel's `toggle_filter()` key parsing.
- [x] Refactor `filter_sources()` to use tri-state logic:
  - Location: if `loc_Planet` is YES, include only planets; if NO, exclude planets; if IGNORE, include all
  - Status: same pattern for Active/Empty
  - Capabilities: same pattern for Ships/Complexes
  - Text search: unchanged (not a tri-state filter)
- [x] Add property accessors for backward compat with ViewModel:
  - `get_filter_state(key: str) -> FilterState`
  - `set_filter_state(key: str, state: FilterState) -> None`
- [x] Remove old `filter_location_type`, `filter_status`, `filter_capabilities` dict attributes
- [x] Update tests in `test_empire_build_queue_filter_manager.py`:
  - Replace bool-based filter assertions with FilterState-based
  - Add tests for tri-state filter logic (IGNORE passes all, YES filters, NO inverts)
- [x] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` passes

**Notes:** Build Queue has the cleanest architecture — this should be straightforward.

---

### Task 4.2: Refactor EmpireBuildQueueViewModel for tri-state [Medium]
**File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [x] Import `FilterState` from `game.ui.filters`
- [x] Refactor `toggle_filter()` (lines 253-284):
  - Removed `toggle_filter()` entirely (no backward compat needed)
  - Added `set_filter_state(key: str, state: FilterState) -> None` method
  - Added `get_filter_state(key: str) -> FilterState` method
- [x] Update filter state property accessors (lines 126-159):
  - Removed `filter_location_type`, `filter_status`, `filter_capabilities` properties and setters
  - Replaced with `get_filter_state(key)` and `set_filter_state(key, state)` delegating to FilterManager
- [x] Update `apply_filters()` — no changes needed, delegates correctly
- [x] Update tests in `test_empire_build_queue_viewmodel.py`:
  - Replaced bool-based assertions with FilterState-based
  - Removed `TestToggleFilter` class, added `TestSetFilterState` class
  - Updated `TestFilterApplication` and `TestLazyRefresh` to use new API
- [x] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` passes

**Notes:** Removed old properties and toggle_filter entirely. Clean cutover — 50 tests passing.

---

### Task 4.3: Replace Build Queue sidebar buttons with TriStateFilterWidget [Medium]
**File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Import `TriStateFilterWidget` from `game.ui.components.filters`
- [x] Import `FilterState` from `game.ui.filters`
- [x] Replace filter toggle button creation with TriStateFilterWidget via `_TRI_STATE_SECTIONS` config
- [x] Added `check_tri_state_presses()` method for polling tri-state widgets
- [x] Removed `_handle_filter_toggle()` and `filter_toggle_buttons` dict
- [x] `handle_button_click()` now only handles column toggles and apply button
- [x] Created `test_empire_build_queue_sidebar.py` with 13 tests
- [x] Verify: all sidebar tests pass

**Notes:** Replaced 6 checkbox buttons with 6 TriStateFilterWidget instances. Sidebar uses poll-based `check_tri_state_presses()` called from window's `update()` loop.

---

### Task 4.4: Update EmpireBuildQueueWindow wiring [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Removed `filter_location_type`, `filter_status`, `filter_capabilities` properties and setters
- [x] Removed `filter_toggle_buttons` property
- [x] Removed `_filter_sources()` method (was syncing old dict state)
- [x] Simplified `apply_filters()` to just delegate to ViewModel
- [x] Added `check_tri_state_presses()` call in `update()` loop
- [x] Updated 117 window tests to use new tri-state API
- [x] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes

**Notes:** Removed old filter dict properties and `_filter_sources()`. Window tests now use `_viewmodel.set_filter_state()` + `apply_filters()`. Net test count reduced from 122 to 117 (removed redundant filter tests already covered by filter_manager tests).

---

### Task 4.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All 13,280 tests pass (0 failures, 2 skipped)
- [x] No regressions from Build Queue changes

**Notes:** Full suite: 13,280 passed, 2 skipped in 99s. Up from 13,266 (14 net new tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Build Queue's 6 filter attributes use TriStateFilterWidget
- [x] Filter logic correctly handles IGNORE/YES/NO semantics
- [x] All 39 filter manager tests updated and passing
- [x] All 50 viewmodel tests updated and passing
- [x] All 117 window tests passing (+ 13 sidebar tests)
- [x] Full test suite passes (13,280 passed, 2 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
