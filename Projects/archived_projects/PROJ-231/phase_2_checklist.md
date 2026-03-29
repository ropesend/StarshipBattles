# Phase 2: Core Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the business logic files for star list filtering, sorting, and data provision.

---

## Tasks

### Task 2.1: Create Star List Filters [Medium]
**New file:** `game/ui/screens/star_list_filters.py`
**Template:** `game/ui/screens/planet_list_filters.py`
**Tests:** `python -m pytest tests/unit/ui/screens/test_star_list_filters.py -q`

- [x] `gather_stars(galaxy)`: Collect stars with cached values
- [x] `filter_stars(...)`: Apply all active filters
- [x] `sort_stars(...)`: Sort by column with special-case numeric columns
- [x] `compute_star_ranges(all_stars)`: Compute min/max ranges
- [x] Helper: `get_system_name(star)`
- [x] Helper: `get_star_type_display(star)`
- [x] Write unit tests (20 tests in test_star_list_filters.py)

**Notes:** Mirrors planet_list_filters.py closely. Uses _cached_type_category = star_type.name (raw enum name) for filter matching.

---

### Task 2.2: Create Star List Filter Manager [Simple]
**New file:** `game/ui/screens/star_list_filter_manager.py`
**Template:** `game/ui/screens/planet_list_filter_manager.py`

- [x] Define `STAR_TYPES` list (8 types)
- [x] Create `StarListFilterManager` class with filter_types, filter_ranges, search_text
- [x] Methods: `toggle_type()`, `set_all_types()`, `get_filter_state()`

**Notes:** No owner filter needed (stars have no owner). No tri-state manager needed.

---

### Task 2.3: Create Star Data Source [Simple]
**New file:** `game/ui/screens/star_data_source.py`
**Template:** `game/ui/screens/planet_data_source.py`

- [x] `StarDataSource(ITableDataSource)` with all required methods
- [x] Value extraction via func/attr/fmt patterns
- [x] `get_cell_image()` returns None (no star icons)

**Notes:** Simplified constructor — no galaxy/empire needed since stars have no owner or icon.

---

### Task 2.4: Create Star List Sidebar [Medium]
**New file:** `game/ui/screens/star_list_sidebar.py`
**Template:** `game/ui/screens/planet_list_sidebar.py`

- [x] `build_sidebar()` function returning widget dict
- [x] Filters: name search, star type grid (8 types), All/None buttons
- [x] Range sliders: mass, temperature, luminosity, age, radius_hexes
- [x] Column visibility toggles
- [x] Preset dropdown + Save button
- [x] UIScrollingContainer for sidebar content

**Notes:** No owner filter section. Star type buttons are wider (105px) to fit longer names like "Main Sequence".

---

### Task 2.5: Create Star List Presets [Simple]
**New file:** `game/ui/screens/star_list_presets.py`
**Template:** `game/ui/screens/planet_list_presets.py`

- [x] `StarPresetManager(PresetManager)` with `PRESET_FILENAME = 'star_ui_presets.json'`
- [x] `capture_star_list_state()` and `apply_star_list_state()` functions

**Notes:** Subclassed PresetManager to reuse disk I/O logic with separate filename.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All new files created and importable without errors
- [x] Unit tests pass: 20 passed in test_star_list_filters.py
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
