# Phase 2: Core Logic

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the business logic files for star list filtering, sorting, and data provision.

---

## Tasks

### Task 2.1: Create Star List Filters [Medium]
**New file:** `game/ui/screens/star_list_filters.py`
**Template:** `game/ui/screens/planet_list_filters.py`
**Tests:** `python -m pytest tests/unit/ui/screens/test_star_list_filters.py -q`

- [ ] `gather_stars(galaxy) -> list`: Iterate all systems, collect all stars. Attach cached computed values onto each Star object:
  - `_cached_name_lower` = `star.name.lower()`
  - `_cached_type_category` = `star.star_type.name` (e.g. "MAIN_SEQUENCE")
  - `_cached_system_name` = `system.name`
  - `_cached_system_global_location` = `system.global_location`
  - `_cached_planet_count` = `len(system.planets)`
  - `_cached_companion_count` = `len(system.stars) - 1`
- [ ] `filter_stars(stars, search_lower, filter_types, min_mass, max_mass, min_temp, max_temp, min_lum, max_lum, min_age, max_age, min_radius, max_radius) -> list`: Apply all active filters using cached values
- [ ] `sort_stars(stars, sort_column_id, sort_descending, columns) -> list`: Sort by column. Special-case numeric columns (mass, temperature, luminosity, age, radius_hexes) for direct attribute access; fallback to func/attr extraction for others.
- [ ] `compute_star_ranges(all_stars) -> dict`: Compute min/max for mass, temp, luminosity, age, radius from actual star data. Returns `{'mass': (min, max), 'temp': (min, max), ...}`
- [ ] Helper: `get_system_name(star) -> str`: Return `star._cached_system_name`
- [ ] Helper: `get_star_type_display(star) -> str`: Return `star.star_type.name.replace('_', ' ').title()`
- [ ] Write unit tests in `tests/unit/ui/screens/test_star_list_filters.py`

**Notes:**

---

### Task 2.2: Create Star List Filter Manager [Simple]
**New file:** `game/ui/screens/star_list_filter_manager.py`
**Template:** `game/ui/screens/planet_list_filter_manager.py`

- [ ] Define `STAR_TYPES` list: `['Main Sequence', 'Red Giant', 'Blue Giant', 'White Dwarf', 'Red Dwarf', 'Neutron Star', 'Black Hole', 'Brown Dwarf']`
- [ ] Create `StarListFilterManager` class:
  - `filter_types: Dict[str, bool]` — 8 star types, all True by default
  - `filter_ranges: Dict[str, List[float]]` — keys: 'mass', 'temperature', 'luminosity', 'age', 'radius_hexes'
  - `search_text: str = ""`
- [ ] Methods: `toggle_type(type_name)`, `set_all_types(enabled: bool)`, `get_filter_state() -> dict`

**Notes:**

---

### Task 2.3: Create Star Data Source [Simple]
**New file:** `game/ui/screens/star_data_source.py`
**Template:** `game/ui/screens/planet_data_source.py`

- [ ] `StarDataSource(ITableDataSource)` class:
  - `__init__(self, columns, galaxy)`
  - `get_row_count() -> int`
  - `get_cell_value(row_index, column_id) -> str` — extract value using func/attr/fmt from column def
  - `get_cell_image(row_index, column_id) -> Optional[Surface]` — return None (no star icons)
  - `get_columns() -> List[Dict]`
  - `get_star_at_index(row_index) -> Optional[Star]`
  - `update_data(stars: list) -> None`
- [ ] Value extraction via `_extract_value(star, col)`: check for `func`, then `attr` (with dot-path support), then `fmt`

**Notes:**

---

### Task 2.4: Create Star List Sidebar [Medium]
**New file:** `game/ui/screens/star_list_sidebar.py`
**Template:** `game/ui/screens/planet_list_sidebar.py`

- [ ] `build_sidebar(sidebar_panel, manager, filter_mgr, star_ranges, columns) -> dict` function returning widget references
- [ ] **Filters section:**
  - FILTERS label
  - Name search text entry
  - Star type multi-select grid (8 types) with All/None buttons
  - Range sliders for: Mass (solar masses), Temperature (K), Luminosity (solar luminosity), Age (years), Radius (hexes) — each with min/max text entries
  - Apply Filters button
- [ ] **Columns section:**
  - COLUMNS label
  - Toggle buttons for each column (visible/hidden)
- [ ] **Presets section:**
  - Preset dropdown + Save button
- [ ] Use `UIScrollingContainer` for sidebar content (same as planet sidebar)

**Notes:**

---

### Task 2.5: Create Star List Presets [Simple]
**New file:** `game/ui/screens/star_list_presets.py`
**Template:** `game/ui/screens/planet_list_presets.py`

- [ ] Subclass `PresetManager` with `PRESET_FILENAME = 'star_ui_presets.json'` (or create standalone class following same pattern)
- [ ] `capture_star_list_state(column_manager, filter_mgr) -> dict`: Serialize column order/visibility + filter state
- [ ] `apply_star_list_state(state, column_manager, filter_mgr)`: Restore from saved state

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new files created and importable without errors
- [ ] Unit tests pass: `python -m pytest tests/unit/ui/screens/test_star_list_filters.py -q`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
