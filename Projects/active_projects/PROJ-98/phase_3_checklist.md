# Phase 3: Column Sorting & Reordering [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-98 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace static UILabel headers with ColumnManager-powered interactive headers supporting click-to-sort and arrow-to-reorder.

**Pattern source:** `game/ui/screens/planet_list_columns.py` (ColumnManager) uses `check_pressed()` polling in `update()`. Same pattern as `planet_list_window.py` lines 293-299.

---

## Tasks

### Task 3.1: Add sort_sources() to filter manager [Medium]
**File:** `game/ui/screens/empire_build_queue_filter_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_filter_manager.py -k "sort"`

- [ ] Add `NUMERIC_COLUMNS` set at module level containing column IDs that sort numerically:
  `{'queue_count', 'turns_left', 'build_rate', 'res_metals_rate', 'res_organics_rate', 'res_vapors_rate', 'res_radioactives_rate', 'res_exotics_rate', 'res_metals_total', 'res_organics_total', 'res_vapors_total', 'res_radioactives_total', 'res_exotics_total'}`
- [ ] Add `sort_sources(self, sources, sort_column_id, sort_descending, get_column_value_fn)` method:
  - Return unchanged if `sort_column_id` is None or not found in columns
  - Extract sort keys via `get_column_value_fn(source, sort_column_id)` for each source
  - For numeric columns: parse to float, use `float('inf')` for "-" or unparseable values
  - For string columns: lowercase comparison, "-" sorts after all other values
  - Sort in-place with `list.sort(key=..., reverse=sort_descending)`
  - Return same list reference
  - Follow `sort_planets()` pattern from `game/ui/screens/planet_list_filters.py:97-144`

**Notes:**

### Task 3.2: Write sort tests [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py`

- [ ] Add `TestSortSources` class with these tests:
  - `test_sort_by_location_ascending` - alphabetical sort A->Z
  - `test_sort_by_location_descending` - alphabetical sort Z->A
  - `test_sort_by_queue_count_numeric` - numeric sort, "-" sorts to bottom
  - `test_sort_by_turns_left_numeric` - numeric values sorted correctly
  - `test_sort_by_resource_rate_numeric` - resource rate column sorted numerically
  - `test_sort_no_column_id_unchanged` - None sort_column_id returns unchanged
  - `test_sort_unknown_column_unchanged` - unknown col ID returns unchanged
  - `test_sort_dash_values_last` - "-" values sort after real values in both ascending and descending

**Setup:** Use `_make_source()` helper to create mock sources. Pass a `get_column_value_fn` lambda that returns predetermined values for each source/column combination.

**Notes:**

### Task 3.3: Integrate ColumnManager into the window [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`

- [ ] Add import: `from game.ui.screens.planet_list_columns import ColumnManager` (top of file)
- [ ] In `__init__()` (around line 145): replace `self._build_header_labels(manager, main_w)` with:
  ```python
  self.column_mgr = ColumnManager(
      self._filter_mgr.columns, manager,
      self.header_container, self.header_height
  )
  self.column_mgr.rebuild_headers()
  ```
- [ ] Remove `_build_header_labels()` method entirely (lines 177-193)
- [ ] Remove `_header_labels` attribute references (check `kill()` and `_handle_column_toggle_click()`)
- [ ] Add `_apply_sort_and_refresh()` helper method:
  ```python
  def _apply_sort_and_refresh(self) -> None:
      self._filter_mgr.sort_sources(
          self.filtered_sources,
          self.column_mgr.sort_column_id,
          self.column_mgr.sort_descending,
          self._get_column_value,
      )
      self._refresh_list()
  ```

**Notes:**

### Task 3.4: Add sort polling to update() [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (lines 485-491)

- [ ] In `update()`, after `super().update(time_delta)`, add:
  ```python
  sort_changed, columns_changed = self.column_mgr.handle_header_clicks()
  if columns_changed or sort_changed:
      self._apply_sort_and_refresh()
  ```
- [ ] Keep existing scrollbar check below

**Notes:**

### Task 3.5: Update column toggle to use ColumnManager [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (line 650)

- [ ] In `_handle_column_toggle_click()`: replace `self._build_header_labels(self.ui_manager, 0)` with `self.column_mgr.rebuild_headers()`

**Notes:**

### Task 3.6: Add sort step to apply_filters() [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (lines 589-599)

- [ ] After `self.filtered_sources = self._filter_sources(self.all_sources)` and before `self._refresh_list()`, insert:
  ```python
  self._filter_mgr.sort_sources(
      self.filtered_sources,
      self.column_mgr.sort_column_id,
      self.column_mgr.sort_descending,
      self._get_column_value,
  )
  ```

**Notes:**

### Task 3.7: Clean up kill() [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (line 823)

- [ ] Add `self.column_mgr.kill()` before `super().kill()`
- [ ] Remove any `_header_labels` cleanup if still present

**Notes:**

### Task 3.8: Write integration tests [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Update `_make_window()` helper to create `column_mgr` mock (or real ColumnManager with mocked UI)
- [ ] Add `TestColumnSortingAndReorder` class:
  - `test_column_mgr_attribute_exists` - window has column_mgr after init
  - `test_apply_sort_and_refresh_calls_sort` - verify sort_sources is called then _refresh_list
  - `test_apply_filters_includes_sort` - verify apply_filters calls sort before refresh
  - `test_column_toggle_rebuilds_headers` - toggling column calls column_mgr.rebuild_headers()

**Notes:**

### Task 3.9: Full test run [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All 7595+ tests pass
- [ ] No regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
