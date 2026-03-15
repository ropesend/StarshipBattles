# Phase 4: Retrofit Build Queue

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace Build Queue's 3 binary filter groups with tri-state widgets backed by FilterStateManager.

---

## Tasks

### Task 4.1: Refactor BuildQueueFilterManager to use FilterStateManager [Medium]
**File:** `game/ui/screens/empire_build_queue_filter_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_filter_manager.py`

- [ ] Import `FilterState, FilterStateManager` from `game.ui.filters`
- [ ] Replace 3 filter dicts with a single FilterStateManager:
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
- [ ] Refactor `filter_sources()` to use tri-state logic:
  - Location: if `loc_Planet` is YES, include only planets; if NO, exclude planets; if IGNORE, include all
  - Status: same pattern for Active/Empty
  - Capabilities: same pattern for Ships/Complexes
  - Text search: unchanged (not a tri-state filter)
- [ ] Add property accessors for backward compat with ViewModel:
  - `get_filter_state(key: str) -> FilterState`
  - `set_filter_state(key: str, state: FilterState) -> None`
- [ ] Remove old `filter_location_type`, `filter_status`, `filter_capabilities` dict attributes
- [ ] Update tests in `test_empire_build_queue_filter_manager.py`:
  - Replace bool-based filter assertions with FilterState-based
  - Add tests for tri-state filter logic (IGNORE passes all, YES filters, NO inverts)
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` passes

**Notes:** Build Queue has the cleanest architecture — this should be straightforward.

---

### Task 4.2: Refactor EmpireBuildQueueViewModel for tri-state [Medium]
**File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [ ] Import `FilterState` from `game.ui.filters`
- [ ] Refactor `toggle_filter()` (lines 253-284):
  - Instead of flipping a bool, accept a new FilterState value
  - Add `set_filter_state(key: str, state: FilterState) -> None` method
  - Keep `toggle_filter()` as convenience that delegates to new method
- [ ] Update filter state property accessors (lines 126-159):
  - Properties should expose FilterState values, not bools
  - Or remove individual properties and expose `get_filter_state(key)` method
- [ ] Update `apply_filters()` (lines 286-292) — minimal changes, just ensure it delegates correctly
- [ ] Update tests in `test_empire_build_queue_viewmodel.py`:
  - Replace bool-based filter assertions with FilterState-based
  - Test tri-state cycling
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` passes

**Notes:**

---

### Task 4.3: Replace Build Queue sidebar buttons with TriStateFilterWidget [Medium]
**File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Import `TriStateFilterWidget` from `game.ui.components.filters`
- [ ] Import `FilterState` from `game.ui.filters`
- [ ] Replace filter toggle button creation (lines 95-185):
  - Remove `[x]`/`[ ]` checkbox-style buttons
  - Create `TriStateFilterWidget` per filter attribute (6 total: loc_Planet, loc_Fleet, status_Active, status_Empty, cap_Ships, cap_Complexes)
  - Store in `self.tri_state_widgets: Dict[str, TriStateFilterWidget]`
- [ ] Refactor `_handle_filter_toggle()` (lines 237-253):
  - Read new state from widget's `check_pressed()` return
  - Call `self.viewmodel.set_filter_state(key, new_state)` instead of `toggle_filter()`
  - Call `self.viewmodel.apply_filters()`
- [ ] Update `handle_button_click()` to check tri-state widgets
- [ ] Remove old `filter_toggle_buttons` dict (replaced by `tri_state_widgets`)
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes

**Notes:**

---

### Task 4.4: Update EmpireBuildQueueWindow wiring [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Update filter state property accessors that delegate to ViewModel (lines 215-242):
  - Remove or update `filter_location_type`, `filter_status`, `filter_capabilities` properties
  - Expose `get_filter_state(key)` if needed by tests
- [ ] Update any direct filter state access in `apply_filters()` (lines 537-544):
  - Remove direct assignment to `_filter_mgr.filter_location_type` etc.
  - Use new FilterStateManager API
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes

**Notes:**

---

### Task 4.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass
- [ ] No regressions from Build Queue changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Build Queue's 6 filter attributes use TriStateFilterWidget
- [ ] Filter logic correctly handles IGNORE/YES/NO semantics
- [ ] All 32 filter manager tests updated and passing
- [ ] All 51 viewmodel tests updated and passing
- [ ] All 119 window tests passing
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
