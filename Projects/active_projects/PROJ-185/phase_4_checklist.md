# Phase 4: Build Queue Single-Select Shim Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-185 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove the single-selection backward compatibility shim from ViewModel and clean up test state exposure in Window

---

## Tasks

### Task 4.1: Remove test state exposure from Window [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Remove comment + lines 109-110:
  ```python
  # Expose state for backward compatibility with tests
  self.columns = self._filter_mgr.columns
  ```
- [x] Check if `self.columns` is used elsewhere in Window class; if yes, keep as `self._columns` (private)
- [x] Remove lines 131-135:
  ```python
  # Expose sidebar button dicts for test compatibility
  self.column_toggle_buttons = self._sidebar.column_toggle_buttons
  self.filter_toggle_buttons = self._sidebar.filter_toggle_buttons
  self.search_entry = self._sidebar.search_entry
  self.btn_apply_filters = self._sidebar.btn_apply_filters
  ```
- [x] If tests reference these attributes, add proper read-only properties with docstrings
- [x] Verify: tests may fail here - proceed to Task 4.5 for test updates

**Notes:** Added read-only properties that delegate to `_filter_mgr.columns` and `_sidebar.*`. Updated test helper to not set these as attributes.

---

### Task 4.2: Remove single-select shim from ViewModel [Medium]
**File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [x] Remove `self._selected_index: int = -1` (line 81)
- [x] Remove `self._selected_source: Optional[BuildQueueSource] = None` (line 82)
- [x] Remove `selected_index` property (lines 114-117)
- [x] Remove `selected_source` property (lines 119-122)
- [x] Remove single-select sync block in `select_row()` (lines 215-222):
  ```python
  # Update single-selection fields for backward compatibility
  if len(self._selected_indices) == 1:
      sole_idx = next(iter(self._selected_indices))
      self._selected_index = sole_idx
      self._selected_source = self.filtered_sources[sole_idx]
  else:
      self._selected_index = -1
      self._selected_source = None
  ```
- [x] Update event emission (line 224-227): remove `selected_source` from payload
- [x] Remove single-select reset in `_refresh()` (lines 260-261)
- [x] `get_selected_sources()` method stays (uses `selected_indices`)
- [x] Clean up unused imports if any (`Optional` may still be needed elsewhere)

**Notes:** Removed `Optional` import as it was no longer used.

---

### Task 4.3: Update Window facade properties [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Rewrite `selected_source` property (lines 210-212) as derived:
  ```python
  @property
  def selected_source(self) -> Optional[BuildQueueSource]:
      """Single selected source, or None if zero/multiple selected."""
      sources = self._viewmodel.get_selected_sources()
      return sources[0] if len(sources) == 1 else None
  ```
- [x] Rewrite `selected_index` property (lines 214-217) as derived:
  ```python
  @property
  def selected_index(self) -> int:
      """Single selected index, or -1 if zero/multiple selected."""
      indices = self._viewmodel.selected_indices
      return next(iter(indices)) if len(indices) == 1 else -1
  ```
- [x] These are now derived on Window, no longer delegating to ViewModel shim fields
- [x] Update internal usage at line 433 if needed (`clicked_index == self.selected_index`)

**Notes:** Also fixed `_select_source` method to use `self.selected_source` instead of `self._viewmodel.selected_source`.

---

### Task 4.4: Update ViewModel test assertions [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [x] Migrate all `vm.selected_index == N` assertions to `vm.selected_indices == {N}`
- [x] Migrate all `vm.selected_index == -1` assertions to `vm.selected_indices == set()`
- [x] Migrate all `vm.selected_source is X` assertions to `vm.get_selected_sources() == [X]`
- [x] Migrate all `vm.selected_source is None` assertions to `vm.get_selected_sources() == []`
- [x] Example migration:
  ```python
  # Before:
  assert vm.selected_index == 1
  assert vm.selected_source is sources[1]
  # After:
  assert vm.selected_indices == {1}
  assert vm.get_selected_sources() == [sources[1]]
  ```
- [x] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` passes

**Notes:** Updated 10 assertions across 7 test methods.

---

### Task 4.5: Update Window test assertions [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Window keeps `selected_source` and `selected_index` as derived properties, so those assertions stay unchanged
- [x] Update any tests referencing `win.column_toggle_buttons`, `win.filter_toggle_buttons`, `win.search_entry`, `win.btn_apply_filters` to use proper accessors (from Task 4.1)
- [x] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes

**Notes:** Test helper updated to not directly assign attribute values; properties delegate correctly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
