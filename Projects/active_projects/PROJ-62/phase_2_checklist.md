# Phase 2: Extract Data Helpers & Column Manager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-62 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move data accessors to filters module; create `ColumnManager` in `planet_list_columns.py`

---

## Tasks

### Task 2.1: Move data accessors to `planet_list_filters.py` [Simple]
**File:** `game/ui/screens/planet_list_filters.py` (EXISTING)
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filters.py tests/integration/ui/test_planet_list_window.py`

- [x] Move `_compute_planet_ranges()` to `planet_list_filters.py` as `compute_planet_ranges(all_planets)` - replace `self.all_planets` with parameter
- [x] Move `_get_system_name()` as `get_system_name(planet)` - no self references
- [x] Move `_get_owner_name()` as `get_owner_name(planet, galaxy, empire)` - replace `self.galaxy`/`self.empire` with params
- [x] Move `_get_mass_earth()` as `get_mass_earth(planet)` - no self references
- [x] Move `_get_resource_str()` as `get_resource_str(planet, resource_name)` - no self references

### Task 2.2: Update `PlanetListWindow` to use extracted accessors [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/integration/ui/test_planet_list_window.py tests/repro_issues/`

- [x] Update import to include: `compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str`
- [x] Replace `self._compute_planet_ranges()` with `compute_planet_ranges(self.all_planets)`
- [x] Update column definitions to use module-level functions instead of `self._get_*` methods
- [x] Delete the 5 methods from `PlanetListWindow`

### Task 2.3: Create `planet_list_columns.py` with `ColumnManager` [Medium]
**File:** `game/ui/screens/planet_list_columns.py` (NEW)
**Tests:** `pytest tests/repro_issues/test_crash_planet_list_method.py tests/integration/ui/test_planet_list_window.py`

- [x] Create new file `game/ui/screens/planet_list_columns.py`
- [x] Define `ColumnManager` class:
  - `__init__(self, columns, manager, header_container, header_height)` - stores columns, sort state, header elements
  - `get_visible_columns(self)` - from `_get_visible_columns()`
  - `rebuild_headers(self)` - from `_rebuild_headers()`
  - `swap_columns(self, col_ref, direction)` - from `_swap_columns()`
  - `handle_header_clicks(self)` - returns `(sort_changed, columns_changed)` tuple
  - `toggle_visibility(self, col_id)` - toggle column visibility by ID
  - `kill(self)` - clean up header elements

### Task 2.4: Update `PlanetListWindow` to use `ColumnManager` [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [x] Add import: `from game.ui.screens.planet_list_columns import ColumnManager`
- [x] Create `self.column_mgr = ColumnManager(self.columns, manager, self.header_container, self.header_height)` in `__init__`
- [x] Replace all `self._rebuild_headers()` with `self.column_mgr.rebuild_headers()`
- [x] Replace `self._swap_columns(...)` with `self.column_mgr.swap_columns(...)`
- [x] Replace `self._get_visible_columns()` with `self.column_mgr.get_visible_columns()`
- [x] Access sort via `self.column_mgr.sort_column_id` / `self.column_mgr.sort_descending`
- [x] In `update()`, replace header click block with `self.column_mgr.handle_header_clicks()` call
- [x] In `update()`, replace column toggle block with `self.column_mgr.toggle_visibility()` calls
- [x] Delete `_rebuild_headers()`, `_swap_columns()`, `_get_visible_columns()` from main class
- [x] Update `kill()` to call `self.column_mgr.kill()`

### Task 2.5: Verify Phase 2 [Simple]
**Tests:** `pytest tests/`

- [x] Run full test suite - all 6246 tests pass
- [x] Verify `planet_list_window.py` line count: 757 lines (target: ~745-770 lines)

**Notes:**
- Updated `tests/repro_issues/test_crash_planet_list_method.py` to check `ColumnManager.get_visible_columns` instead of old method location
- Line counts after Phase 2:
  - `planet_list_window.py`: 944 → 757 lines (187 lines removed)
  - `planet_list_filters.py`: 173 → 310 lines (+137 lines from data accessors)
  - `planet_list_columns.py`: 200 lines (new)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
