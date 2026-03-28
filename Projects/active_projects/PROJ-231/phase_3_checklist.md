# Phase 3: Star List Window

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the main StarListWindow class tying all Phase 2 components together.

---

## Tasks

### Task 3.1: StarListWindow - Layout & Init [Medium]
**New file:** `game/ui/screens/star_list_window.py`
**Template:** `game/ui/screens/planet_list_window.py`

- [ ] Class `StarListWindow(UIWindow)` with constructor:
  ```python
  def __init__(self, rect, manager, galaxy, on_close_callback=None, on_navigate_callback=None):
  ```
- [ ] Column definitions for all 19 star attributes (10 visible + 9 hidden spectrum):
  - Visible: name, type, system, mass, radius, temp, luminosity, age, planets, companions
  - Hidden: spec_gamma, spec_xray, spec_uv, spec_blue, spec_green, spec_red, spec_ir, spec_micro, spec_radio
- [ ] Two-panel layout: left sidebar (260px) + main table area (full remaining width, no right detail panel)
- [ ] Initialize `TableColumnManager` with column definitions
- [ ] Initialize `StarDataSource` with columns and galaxy
- [ ] Initialize `VirtualTable` with panel, manager, data source, column manager, `SingleSelect`
- [ ] Build sidebar via `build_sidebar()` from `star_list_sidebar.py`
- [ ] Initialize `StarListFilterManager` with ranges from `compute_star_ranges()`
- [ ] Initialize `StarPresetManager` (or `PresetManager` subclass)
- [ ] Store `on_close_callback` and `on_navigate_callback`
- [ ] Call `refresh_list()` on init

**Notes:**

---

### Task 3.2: StarListWindow - Refresh/Filter/Sort Logic [Medium]

- [ ] `refresh_list()` method:
  1. `gather_stars(galaxy)` — collect all stars with cached values
  2. `filter_stars(...)` — apply current filter state from filter manager
  3. `sort_stars(...)` — sort by current sort column from column manager
  4. `data_source.update_data(sorted_stars)`
  5. `virtual_table.force_update()`
- [ ] Wire Apply Filters button press to `refresh_list()`
- [ ] Wire column header sort/swap events to refresh

**Notes:**

---

### Task 3.3: StarListWindow - Event Handling [Medium]

- [ ] `process_event(event)` method handling:
  - `UI_BUTTON_PRESSED` — filter toggles, All/None buttons, Apply, column toggles, preset save, Navigate
  - `UI_TEXT_ENTRY_FINISHED` — name search, range slider text entries
  - `UI_DROP_DOWN_MENU_CHANGED` — preset selection
  - `MOUSEWHEEL` — delegate to virtual table
  - Screenshot hotkey
- [ ] `update(time_delta)` method handling:
  - Column header button presses (sort/swap) via `virtual_table.check_header_presses()`
  - Row selection changes
  - Slider value synchronization with text entries
- [ ] `_handle_filter_toggles(event)` — star type toggle buttons
- [ ] `_handle_slider_sync()` — sync slider positions with text entry values
- [ ] `_handle_column_toggles(event)` — column visibility toggle buttons
- [ ] `_handle_preset_changes(event)` — preset dropdown and save button

**Notes:**

---

### Task 3.4: StarListWindow - Navigation & Selection [Simple]

- [ ] On row selection (from VirtualTable), store `self.selected_star`
- [ ] Add "Navigate to Star" button below the table or in a small area
- [ ] When Navigate clicked and a star is selected:
  - Call `self.on_navigate_callback(star._cached_system_global_location)` to center camera
- [ ] `kill()` method: call `on_close_callback()` if set, then `super().kill()`
- [ ] `set_dimensions()` override for resize support (recalculate layout)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `star_list_window.py` imports cleanly
- [ ] No circular import issues
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
