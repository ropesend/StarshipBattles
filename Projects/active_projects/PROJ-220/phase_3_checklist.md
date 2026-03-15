# Phase 3: Retrofit Fleet Report

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace Fleet Report's 8 binary paired-button filters with tri-state widgets backed by FilterStateManager. Status filter (4-state) is excluded.

---

## Tasks

### Task 3.1: Refactor `fleet_report_filters.py` to accept FilterState [Medium]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [ ] Import `FilterState` from `game.ui.filters`
- [ ] Change `filter_ships()` signature: `filter_state: Dict[str, bool]` → `filter_state: Dict[str, Any]` (accepts both FilterState and bool for backward compat during transition)
- [ ] Refactor `_should_exclude_by_warp(ship, filter_state)`:
  - Read `filter_state.get('warp_capable', FilterState.IGNORE)` (single key, not paired)
  - If `FilterState.IGNORE` → return False (no exclusion)
  - If `FilterState.YES` → exclude if NOT warp-capable
  - If `FilterState.NO` → exclude if warp-capable
- [ ] Refactor `_should_exclude_by_spaceyard(ship, filter_state)` — same pattern, key `'has_spaceyard'`
- [ ] Refactor `_should_exclude_by_cargo(ship, filter_state)` — same pattern, key `'has_cargo'`
- [ ] Refactor `_should_exclude_by_special_capabilities(ship, filter_state)`:
  - Replace dynamic key generation (`can_` / `no_` pairs) with single-key tri-state lookup
  - Keys: `'destroy_planet'`, `'open_warp'`, `'close_warp'`, `'destroy_star'`, `'create_sphere'`
  - Each key maps to `FilterState` value
- [ ] Keep `_should_exclude_by_status()` UNCHANGED (status filter is out of scope)
- [ ] Update all 5 exclusion functions to handle both `FilterState` enum values AND legacy `bool` values (for transition safety)
- [ ] Update existing tests in `test_fleet_report_filters.py` to pass FilterState values instead of bool dicts
- [ ] Add new tests for tri-state filter logic:
  - Test IGNORE state passes all ships through
  - Test YES state filters to matching only
  - Test NO state filters to non-matching only
  - Test combinations: some YES, some NO, some IGNORE
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py` passes

**Notes:** This is the highest-risk task (59 existing tests). Take care with the filter_state dict key changes.

---

### Task 3.2: Refactor `FleetListViewModel` to use FilterStateManager [Medium]
**File:** `game/ui/screens/fleet_report_view_model.py`
**Tests:** `pytest tests/unit/ui/test_fleet_list_view_model.py`

- [ ] Import `FilterState, FilterStateManager` from `game.ui.filters`
- [ ] Replace 16 binary filter attributes (lines 40-57) with a `FilterStateManager` instance:
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
- [ ] Keep status filter attributes UNCHANGED: `filter_show_damaged`, `filter_show_undamaged`, `filter_show_derelict`, `filter_show_destroyed` (lines 36-39)
- [ ] Refactor `toggle_filter(filter_id)` (lines 77-152):
  - For tri-state filters: cycle state via `set_state(attr, new_state)` — caller must specify new state, not toggle
  - Add `set_filter_state(attribute: str, state: FilterState) -> None` method
  - Keep `toggle_filter()` for status filters (backward compat)
- [ ] Refactor `get_filter_state()` (lines 171-199):
  - Return dict with FilterState values for tri-state filters
  - Include status filter bools for `_should_exclude_by_status()` backward compat
- [ ] Refactor `is_filter_enabled(filter_id)` (lines 267-279):
  - For tri-state filters, return the FilterState value instead of bool
  - Or add `get_filter_state_for(attribute: str) -> FilterState` method
- [ ] Update tests in `test_fleet_list_view_model.py` to use new API
- [ ] Verify: `pytest tests/unit/ui/test_fleet_list_view_model.py` passes

**Notes:**

---

### Task 3.3: Replace paired buttons with TriStateFilterWidget in sidebar [Medium]
**File:** `game/ui/screens/fleet_report_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py`

- [ ] Import `TriStateFilterWidget` from `game.ui.components.filters`
- [ ] Import `FilterState` from `game.ui.filters`
- [ ] Replace paired button creation in `_build_filter_section()` (lines 223-329):
  - Remove paired buttons for: warp, spaceyard, cargo, special capabilities
  - Create `TriStateFilterWidget` per binary attribute (8 total)
  - Store widgets in `self.tri_state_widgets: Dict[str, TriStateFilterWidget]`
  - Keep status filter buttons (damaged/undamaged/derelict/destroyed) as-is
- [ ] Refactor `check_button_presses()` (lines 522-554):
  - Check each `TriStateFilterWidget.check_pressed()` in addition to status buttons
  - Return `{'filter_state_changed': (attribute, new_state)}` for tri-state changes
  - Keep existing `'filter_toggled'` return for status filter buttons
- [ ] Remove `update_filter_button()` for tri-state attributes (widget manages its own visuals)
- [ ] Remove or simplify `_create_filter_button()` (only needed for status filter now)
- [ ] Update tests that check sidebar button creation/presses
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py` passes

**Notes:**

---

### Task 3.4: Update FleetReportWindow wiring [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

- [ ] Update `_toggle_filter()` (lines 324-339):
  - Handle tri-state changes: `sidebar_actions.get('filter_state_changed')` → call `view_model.set_filter_state(attr, state)`
  - Handle status toggles: existing `sidebar_actions.get('filter_toggled')` → call `view_model.toggle_filter()`
  - Both paths: clear selection, call `refresh_list()`
- [ ] Update `update()` (lines 298-322) to process both action types from sidebar
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py tests/unit/ui/screens/test_fleet_report_window_multi_select.py` passes

**Notes:**

---

### Task 3.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All 13,178+ tests pass
- [ ] No regressions from Fleet Report changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Fleet Report's 8 binary filters use TriStateFilterWidget
- [ ] Status filter (4-state) still works unchanged
- [ ] All 59 fleet report filter tests updated and passing
- [ ] All fleet report window tests passing
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
