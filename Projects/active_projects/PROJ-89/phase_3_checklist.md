# Phase 3: EmpireBuildQueueWindow Filter Manager [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-89 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract filter state management, filter predicates, column configuration, and sort logic from EmpireBuildQueueWindow into a standalone `empire_build_queue_filter_manager.py` module. This follows the same pattern as the existing `fleet_report_filters.py`.

**File:** `game/ui/screens/empire_build_queue_window.py`
**New File:** `game/ui/screens/empire_build_queue_filter_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_empire_build_queue_filter_manager.py`

---

## Tasks
### Task 3.1: Create empire_build_queue_filter_manager.py [Medium]
**File:** `game/ui/screens/empire_build_queue_filter_manager.py`
- [ ] Create new module with docstring explaining it manages filter state and column visibility for the empire build queue
- [ ] Add imports: `from typing import Any, Dict, List, TYPE_CHECKING`
- [ ] Add TYPE_CHECKING import for `BuildQueueSource`
- [ ] Create `BuildQueueFilterManager` class with `__init__`:
  - `self.filter_location_type: Dict[str, bool] = {'Planet': True, 'Fleet': True}`
  - `self.filter_status: Dict[str, bool] = {'Active': True, 'Empty': True}`
  - `self.filter_capabilities: Dict[str, bool] = {'Ships': True, 'Complexes': True}`
  - `self.search_text: str = ""`
  - `self.columns: List[Dict[str, Any]]` - accept as constructor parameter with default column definitions
- [ ] Extract `get_visible_columns(self)` method:
  - Signature: `def get_visible_columns(self) -> List[Dict[str, Any]]`
  - Returns `[c for c in self.columns if c.get('visible', True)]`
- [ ] Extract `toggle_column_visibility(self, col_id)` method:
  - Signature: `def toggle_column_visibility(self, col_id: str) -> bool`
  - Copy implementation from lines 585-598
- [ ] Extract `filter_sources(self, sources)` method:
  - Signature: `def filter_sources(self, sources: List[BuildQueueSource]) -> List[BuildQueueSource]`
  - Copy implementation from lines 604-652 (the `_filter_sources` method)
  - Uses `self.filter_location_type`, `self.filter_status`, `self.filter_capabilities`, `self.search_text`
- [ ] Add `reset_selection_state(self)` convenience method that returns default values:
  - Returns a dict: `{'selected_source': None, 'selected_index': -1, 'selected_indices': set()}`
  - The window will use this to reset its state after applying filters

**Notes:**

---

### Task 3.2: Write unit tests for empire_build_queue_filter_manager.py [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py`
- [ ] Create helper `_make_source()` function (same pattern as existing test file)
- [ ] Create `TestFilterManagerInit` class:
  - Test: default filter state has all types enabled
  - Test: default search_text is empty
  - Test: columns list is populated with expected IDs
- [ ] Create `TestGetVisibleColumns` class:
  - Test: returns only visible columns
  - Test: hidden columns excluded
  - Test: build_rate hidden by default
- [ ] Create `TestToggleColumnVisibility` class:
  - Test: toggle visible column makes it invisible
  - Test: toggle hidden column makes it visible
  - Test: toggle unknown column returns False
- [ ] Create `TestFilterSources` class:
  - Test: all filters enabled shows all sources
  - Test: hide fleet sources filters correctly
  - Test: hide planet sources filters correctly
  - Test: hide empty queues filters correctly
  - Test: hide active queues filters correctly
  - Test: capabilities filter - ships only
  - Test: capabilities filter - complexes only
  - Test: text search filters by display_name
  - Test: text search is case-insensitive
  - Test: combined filters (AND logic)
- [ ] No pygame initialization needed - these are pure data tests

**Notes:**

---

### Task 3.3: Update EmpireBuildQueueWindow to delegate to filter manager [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
- [ ] Add import: `from game.ui.screens.empire_build_queue_filter_manager import BuildQueueFilterManager`
- [ ] In `__init__`, create filter manager instance:
  ```python
  self._filter_mgr = BuildQueueFilterManager()
  ```
- [ ] Replace `self.columns` with `self._filter_mgr.columns` (or keep as a property that delegates)
- [ ] Replace `self.filter_location_type` with property delegating to `self._filter_mgr.filter_location_type`
  - Alternative: keep direct attributes and sync them, but delegation is cleaner
  - Simplest approach: set `self.filter_location_type = self._filter_mgr.filter_location_type` (same dict object)
- [ ] Similarly for `self.filter_status`, `self.filter_capabilities`, `self.search_text`
  - For search_text (a string, immutable): keep it on both and sync in `_handle_apply_filters_click`
- [ ] Replace `_get_visible_columns` body with delegation:
  ```python
  def _get_visible_columns(self):
      return self._filter_mgr.get_visible_columns()
  ```
- [ ] Replace `toggle_column_visibility` body with delegation:
  ```python
  def toggle_column_visibility(self, col_id):
      return self._filter_mgr.toggle_column_visibility(col_id)
  ```
- [ ] Replace `_filter_sources` body with delegation:
  ```python
  def _filter_sources(self, sources):
      self._filter_mgr.search_text = self.search_text
      return self._filter_mgr.filter_sources(sources)
  ```
- [ ] Verify `apply_filters` still works: it calls `_filter_sources` and resets selection
- [ ] Verify sidebar builders still work: they reference `self.filter_location_type` etc. (same dict objects)
- [ ] Run existing tests: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` - all must pass unchanged

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes (existing tests)
- [ ] `pytest tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` passes (new tests)
- [ ] `pytest tests/ -n 12` full suite passes with no regressions
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
