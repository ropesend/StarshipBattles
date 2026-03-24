# Phase 3: Retrofit Fleet Report

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace Fleet Report's 8 binary paired-button filters with tri-state widgets backed by FilterStateManager. Status filter (4-state) is excluded.

---

## Tasks

### Task 3.1: Refactor `fleet_report_filters.py` to accept FilterState [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [x] Import `FilterState` from `game.ui.filters`
- [x] Change `filter_ships()` signature: `filter_state: Dict[str, bool]` → `filter_state: Dict[str, Any]` (accepts both FilterState and bool for backward compat during transition)
- [x] Refactor `_should_exclude_by_warp(ship, filter_state)`:
  - Read `filter_state.get('warp_capable', FilterState.IGNORE)` (single key, not paired)
  - If `FilterState.IGNORE` → return False (no exclusion)
  - If `FilterState.YES` → exclude if NOT warp-capable
  - If `FilterState.NO` → exclude if warp-capable
- [x] Refactor `_should_exclude_by_spaceyard(ship, filter_state)` — same pattern, key `'has_spaceyard'`
- [x] Refactor `_should_exclude_by_cargo(ship, filter_state)` — same pattern, key `'has_cargo'`
- [x] Refactor `_should_exclude_by_special_capabilities(ship, filter_state)`:
  - Replace dynamic key generation (`can_` / `no_` pairs) with single-key tri-state lookup
  - Keys: `'destroy_planet'`, `'open_warp'`, `'close_warp'`, `'destroy_star'`, `'create_sphere'`
  - Each key maps to `FilterState` value
- [x] Keep `_should_exclude_by_status()` UNCHANGED (status filter is out of scope)
- [x] Update all 5 exclusion functions to handle both `FilterState` enum values AND legacy `bool` values (for transition safety)
- [x] Update existing tests in `test_fleet_report_filters.py` to pass FilterState values instead of bool dicts
- [x] Add new tests for tri-state filter logic:
  - Test IGNORE state passes all ships through
  - Test YES state filters to matching only
  - Test NO state filters to non-matching only
  - Test combinations: some YES, some NO, some IGNORE
- [x] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py` passes

**Notes:** All 59 tests updated and passing. Added `_check_tri_state()` helper and `SPECIAL_CAPABILITY_FILTER_KEYS` mapping. No backward compat needed — clean cutover per project convention.

---

### Task 3.2: Refactor `FleetListViewModel` to use FilterStateManager [Medium]
**File:** `game/ui/screens/fleet_report_view_model.py`
**Tests:** `pytest tests/unit/ui/test_fleet_list_view_model.py`

- [x] Import `FilterState, FilterStateManager` from `game.ui.filters`
- [x] Replace 16 binary filter attributes (lines 40-57) with a `FilterStateManager` instance:
  ```python
  self._filter_mgr = FilterStateManager({
      'warp_capable': FilterState.IGNORE,
      'has_spaceyard': FilterState.IGNORE,
      'has_cargo': FilterState.IGNORE,
      'destroy_planet': FilterState.IGNORE,
      'open_warp': FilterState.IGNORE,
      'close_warp': FilterState.IGNORE,
      'destroy_star': FilterState.IGNORE,
      'create_sphere': FilterState.IGNORE,
  })
  ```
- [x] Keep status filter attributes UNCHANGED: `filter_show_damaged`, `filter_show_undamaged`, `filter_show_derelict`, `filter_show_destroyed` (lines 36-39)
- [x] Refactor `toggle_filter(filter_id)` (lines 77-152):
  - For tri-state filters: cycle state via `set_state(attr, new_state)` — caller must specify new state, not toggle
  - Add `set_filter_state(attribute: str, state: FilterState) -> None` method
  - Keep `toggle_filter()` for status filters (backward compat)
- [x] Refactor `get_filter_state()` (lines 171-199):
  - Return dict with FilterState values for tri-state filters
  - Include status filter bools for `_should_exclude_by_status()` backward compat
- [x] Refactor `is_filter_enabled(filter_id)` (lines 267-279):
  - For tri-state filters, return the FilterState value instead of bool
  - Or add `get_filter_state_for(attribute: str) -> FilterState` method
- [x] Update tests in `test_fleet_list_view_model.py` to use new API
- [x] Verify: `pytest tests/unit/ui/test_fleet_list_view_model.py` passes

**Notes:** Replaced 16 bool attributes with FilterStateManager. Added `set_filter_state()`, `get_tri_state()`, and `filter_manager` property. `toggle_filter()` now only handles status filters. `is_filter_enabled()` removed (replaced by `get_tri_state()`). 28 ViewModel tests updated and passing.

---

### Task 3.3: Replace paired buttons with TriStateFilterWidget in sidebar [Medium]
**File:** `game/ui/screens/fleet_report_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_sidebar.py`

- [x] Import `TriStateFilterWidget` from `game.ui.components.filters`
- [x] Import `FilterState` from `game.ui.filters`
- [x] Replace paired button creation in `_build_filter_section()` (lines 223-329):
  - Remove paired buttons for: warp, spaceyard, cargo, special capabilities
  - Create `TriStateFilterWidget` per binary attribute (8 total)
  - Store widgets in `self.tri_state_widgets: Dict[str, TriStateFilterWidget]`
  - Keep status filter buttons (damaged/undamaged/derelict/destroyed) as-is
- [x] Refactor `check_button_presses()` (lines 522-554):
  - Check each `TriStateFilterWidget.check_pressed()` in addition to status buttons
  - Return `{'filter_state_changed': (attribute, new_state)}` for tri-state changes
  - Keep existing `'filter_toggled'` return for status filter buttons
- [x] Remove `update_filter_button()` for tri-state attributes (widget manages its own visuals)
- [x] Remove or simplify `_create_filter_button()` (only needed for status filter now)
- [x] Update tests that check sidebar button creation/presses
- [x] Verify: `pytest tests/unit/ui/screens/test_fleet_report_sidebar.py` passes

**Notes:** Replaced 16 paired buttons with 8 TriStateFilterWidget instances via `_TRI_STATE_SECTIONS` config. Renamed `_create_filter_button` to `_create_status_filter_button` — uses `_STATUS_FILTERS` dict for initial state instead of `is_filter_enabled()` (removed). `check_button_presses()` now checks tri-state widgets first, returns `filter_state_changed` tuple. Widget calls `set_state()` on itself. Created `test_fleet_report_sidebar.py` with 12 tests. Updated multi-select test fixture to patch `TriStateFilterWidget`.

---

### Task 3.4: Update FleetReportWindow wiring [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

- [x] Update `_toggle_filter()` (lines 324-339):
  - Handle tri-state changes: `sidebar_actions.get('filter_state_changed')` → call `view_model.set_filter_state(attr, state)`
  - Handle status toggles: existing `sidebar_actions.get('filter_toggled')` → call `view_model.toggle_filter()`
  - Both paths: clear selection, call `refresh_list()`
- [x] Update `update()` (lines 298-322) to process both action types from sidebar
- [x] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py` passes

**Notes:** Added `_apply_tri_state_filter(attribute, state)` method. `update()` checks `filter_state_changed` first, then `filter_toggled`. Both paths clear selection and refresh. 4 new wiring tests in `TestFleetReportTriStateWiring` class. All 56 window tests + 12 sidebar tests passing.

---

### Task 3.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All 13,266 tests pass (0 failures, 2 skipped)
- [x] No regressions from Fleet Report changes

**Notes:** Full suite: 13,266 passed, 2 skipped in 99s.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Fleet Report's 8 binary filters use TriStateFilterWidget
- [x] Status filter (4-state) still works unchanged
- [x] All 59 fleet report filter tests updated and passing
- [x] All fleet report window tests passing
- [x] Full test suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
