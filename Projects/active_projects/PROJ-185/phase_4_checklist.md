# Phase 4: Build Queue Single-Select Shim Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-185 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the single-selection backward compatibility shim from ViewModel and clean up test state exposure in Window

---

## Tasks

### Task 4.1: Remove test state exposure from Window [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Remove comment + lines 109-110:
  ```python
  # Expose state for backward compatibility with tests
  self.columns = self._filter_mgr.columns
  ```
- [ ] Check if `self.columns` is used elsewhere in Window class; if yes, keep as `self._columns` (private)
- [ ] Remove lines 131-135:
  ```python
  # Expose sidebar button dicts for test compatibility
  self.column_toggle_buttons = self._sidebar.column_toggle_buttons
  self.filter_toggle_buttons = self._sidebar.filter_toggle_buttons
  self.search_entry = self._sidebar.search_entry
  self.btn_apply_filters = self._sidebar.btn_apply_filters
  ```
- [ ] If tests reference these attributes, add proper read-only properties with docstrings
- [ ] Verify: tests may fail here - proceed to Task 4.5 for test updates

**Notes:**

---

### Task 4.2: Remove single-select shim from ViewModel [Medium]
**File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [ ] Remove `self._selected_index: int = -1` (line 81)
- [ ] Remove `self._selected_source: Optional[BuildQueueSource] = None` (line 82)
- [ ] Remove `selected_index` property (lines 114-117)
- [ ] Remove `selected_source` property (lines 119-122)
- [ ] Remove single-select sync block in `select_row()` (lines 215-222):
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
- [ ] Update event emission (line 224-227): remove `selected_source` from payload
- [ ] Remove single-select reset in `_refresh()` (lines 260-261)
- [ ] `get_selected_sources()` method stays (uses `selected_indices`)
- [ ] Clean up unused imports if any (`Optional` may still be needed elsewhere)

**Notes:**

---

### Task 4.3: Update Window facade properties [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Rewrite `selected_source` property (lines 210-212) as derived:
  ```python
  @property
  def selected_source(self) -> Optional[BuildQueueSource]:
      """Single selected source, or None if zero/multiple selected."""
      sources = self._viewmodel.get_selected_sources()
      return sources[0] if len(sources) == 1 else None
  ```
- [ ] Rewrite `selected_index` property (lines 214-217) as derived:
  ```python
  @property
  def selected_index(self) -> int:
      """Single selected index, or -1 if zero/multiple selected."""
      indices = self._viewmodel.selected_indices
      return next(iter(indices)) if len(indices) == 1 else -1
  ```
- [ ] These are now derived on Window, no longer delegating to ViewModel shim fields
- [ ] Update internal usage at line 433 if needed (`clicked_index == self.selected_index`)

**Notes:**

---

### Task 4.4: Update ViewModel test assertions [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [ ] Migrate all `vm.selected_index == N` assertions to `vm.selected_indices == {N}`
- [ ] Migrate all `vm.selected_index == -1` assertions to `vm.selected_indices == set()`
- [ ] Migrate all `vm.selected_source is X` assertions to `vm.get_selected_sources() == [X]`
- [ ] Migrate all `vm.selected_source is None` assertions to `vm.get_selected_sources() == []`
- [ ] Example migration:
  ```python
  # Before:
  assert vm.selected_index == 1
  assert vm.selected_source is sources[1]
  # After:
  assert vm.selected_indices == {1}
  assert vm.get_selected_sources() == [sources[1]]
  ```
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` passes

**Notes:**

---

### Task 4.5: Update Window test assertions [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Window keeps `selected_source` and `selected_index` as derived properties, so those assertions stay unchanged
- [ ] Update any tests referencing `win.column_toggle_buttons`, `win.filter_toggle_buttons`, `win.search_entry`, `win.btn_apply_filters` to use proper accessors (from Task 4.1)
- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
