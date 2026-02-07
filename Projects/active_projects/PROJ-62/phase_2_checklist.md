# Phase 2: Extract Data Helpers & Column Manager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-62 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move data accessors to filters module; create `ColumnManager` in `planet_list_columns.py`

---

## Tasks

### Task 2.1: Move data accessors to `planet_list_filters.py` [Simple]
**File:** `game/ui/screens/planet_list_filters.py` (EXISTING)
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filters.py tests/integration/ui/test_planet_list_window.py`

- [ ] Move `_compute_planet_ranges()` to `planet_list_filters.py` as `compute_planet_ranges(all_planets)` - replace `self.all_planets` with parameter
- [ ] Move `_get_system_name()` as `get_system_name(planet)` - no self references
- [ ] Move `_get_owner_name()` as `get_owner_name(planet, galaxy, empire)` - replace `self.galaxy`/`self.empire` with params
- [ ] Move `_get_mass_earth()` as `get_mass_earth(planet)` - no self references
- [ ] Move `_get_resource_str()` as `get_resource_str(planet, resource_name)` - no self references

### Task 2.2: Update `PlanetListWindow` to use extracted accessors [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/integration/ui/test_planet_list_window.py tests/repro_issues/`

- [ ] Update import to include: `compute_planet_ranges, get_system_name, get_owner_name, get_mass_earth, get_resource_str`
- [ ] Replace `self._compute_planet_ranges()` with `compute_planet_ranges(self.all_planets)`
- [ ] Update column definitions to use module-level functions instead of `self._get_*` methods
- [ ] Delete the 5 methods from `PlanetListWindow`

### Task 2.3: Create `planet_list_columns.py` with `ColumnManager` [Medium]
**File:** `game/ui/screens/planet_list_columns.py` (NEW)
**Tests:** `pytest tests/repro_issues/test_crash_planet_list_method.py tests/integration/ui/test_planet_list_window.py`

- [ ] Create new file `game/ui/screens/planet_list_columns.py`
- [ ] Define `ColumnManager` class:
  - `__init__(self, columns, manager, header_container)` - stores columns, sort state, header elements
  - `get_visible_columns(self)` - from `_get_visible_columns()` (line 1047-1049)
  - `rebuild_headers(self)` - from `_rebuild_headers()` (lines 464-526)
  - `swap_columns(self, col_ref, direction)` - from `_swap_columns()` (lines 528-551)
  - `handle_header_clicks(self)` - extract from `update()` lines 980-997, returns `(sort_changed, columns_changed)` tuple
  - `toggle_visibility(self, col_id)` - extract from `update()` lines 966-978
  - `kill(self)` - clean up header elements

### Task 2.4: Update `PlanetListWindow` to use `ColumnManager` [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/`

- [ ] Add import: `from game.ui.screens.planet_list_columns import ColumnManager`
- [ ] Create `self.column_mgr = ColumnManager(self.columns, manager, self.header_container)` in `__init__`
- [ ] Replace all `self._rebuild_headers()` with `self.column_mgr.rebuild_headers()`
- [ ] Replace `self._swap_columns(...)` with `self.column_mgr.swap_columns(...)`
- [ ] Replace `self._get_visible_columns()` with `self.column_mgr.get_visible_columns()`
- [ ] Access sort via `self.column_mgr.sort_column_id` / `self.column_mgr.sort_descending`
- [ ] In `update()`, replace header click block with `self.column_mgr.handle_header_clicks()` call
- [ ] In `update()`, replace column toggle block with `self.column_mgr.toggle_visibility()` calls
- [ ] Delete `_rebuild_headers()`, `_swap_columns()`, `_get_visible_columns()` from main class
- [ ] Update `kill()` to call `self.column_mgr.kill()`

### Task 2.5: Verify Phase 2 [Simple]
**Tests:** `pytest tests/`

- [ ] Run full test suite - all 6248 tests pass
- [ ] Verify `planet_list_window.py` line count (target: ~745-770 lines)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
