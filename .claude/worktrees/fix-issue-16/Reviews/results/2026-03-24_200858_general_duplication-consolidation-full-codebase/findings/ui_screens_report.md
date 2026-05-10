# UI Screens Duplication Report

**Scope:** `game/ui/screens/` and all subdirectories
**Total files reviewed:** 120+ Python files (~41,400 LOC)
**Date:** 2026-03-24

## Summary

The `game/ui/screens/` directory contains significant structural duplication across its list windows (FleetReport, PlanetList, EmpireBuildQueue, EventLog), selection dialogs (Planet, Fleet, System), sidebar components, and data source implementations. The code was clearly built incrementally with copy-paste-modify patterns. While some of the MVVM refactoring (PROJ-172, PROJ-188) has reduced internal duplication within individual windows, the cross-window patterns remain highly duplicated.

**Key themes:**
1. **Column toggle sidebar logic** duplicated across 4 sidebar classes
2. **VirtualTable lifecycle boilerplate** (update_scroll_bar + force_update + update_visible_rows) repeated 5+ times
3. **Mouse wheel scroll handling** copied nearly identically in 4 windows
4. **Selection window pattern** (Label + SelectionList + Confirm/Cancel buttons) repeated in 3 classes
5. **Star/planet formatting** duplicated between strategy detail, galaxy test, and strategy_detail_formatter
6. **Command dispatch pattern** (facade-or-session routing) duplicated in 3 files
7. **Data source classes** share identical interface boilerplate with no shared base

---

## Findings

#### MAJOR: Column Toggle Sidebar Pattern Duplicated Across 4 Components
**ID:** DUP-SCR-001
**Location:**
- `fleet_report_sidebar.py:313-341` (`_build_column_section`)
- `event_log_sidebar.py:57-92` (`_build_column_section`)
- `empire_build_queue_sidebar.py:92-112` (`_build_column_toggles`)
- `planet_list_sidebar.py:195-209` (column toggle section in `build_sidebar`)

**Issue:** All four sidebars build column visibility toggle buttons with the exact same pattern: iterate columns from a column manager, create `[x] Title` / `[ ] Title` buttons, store references in a dict keyed by `col_id`, and attach `col_ref` to the button. The `FleetReportSidebar._build_column_section` and `EventLogSidebar._build_column_section` are nearly character-for-character identical (same UILabel "COLUMNS", same button creation loop, same `btn.col_ref = col` pattern). The `update_column_button` / `refresh_button_labels` methods are also duplicated.

**Impact:** Bug fixes or style changes to column toggles must be applied in 4 places. Divergence risk is high.
**Recommendation:** Extract a `ColumnToggleSection` widget class that takes a `column_manager` and builds the toggle buttons. All sidebars would embed this widget.
**Effort:** Simple

---

#### MAJOR: VirtualTable Refresh Boilerplate Duplicated Across 5+ Windows
**ID:** DUP-SCR-002
**Location:**
- `fleet_report_window.py:166-168` (refresh_list)
- `planet_list_window.py:221-223` (refresh_list)
- `event_log_window.py:252-256` (_rebuild_list)
- `empire_build_queue_window.py:266-268` (_refresh_list)
- `build_queue_renderer.py:142-144` (refresh_queue_display)

**Issue:** Every window using VirtualTable has the same 3-line refresh sequence:
```python
self.virtual_table.update_scroll_bar()
self.virtual_table.force_update()
self.virtual_table.update_visible_rows()
```
This also appears after column toggle operations (rebuild_headers + rebuild_row_pool + refresh), which is a 5-line sequence appearing in all 4 list windows. The header swap/sort handling is also nearly identical across all windows.

**Impact:** If VirtualTable's refresh API changes, 5+ call sites must be updated. The pattern is error-prone (easy to forget one of the three calls).
**Recommendation:** Add a `VirtualTable.full_refresh()` convenience method that calls all three internally. Similarly, add `VirtualTable.rebuild_and_refresh()` for the column-change case.
**Effort:** Simple

---

#### MAJOR: Mouse Wheel Scroll Handling Duplicated in 3 Windows
**ID:** DUP-SCR-003
**Location:**
- `planet_list_window.py:280-299`
- `empire_build_queue_window.py:430-443`
- `builder/weapons_panel.py:206-215`

**Issue:** The mouse wheel scroll handling follows the same pattern in all three:
1. Check `event.type == pygame.MOUSEWHEEL`
2. Get mouse position
3. Check if within table/list area via `collidepoint`
4. Calculate `row_percent = self.row_height / total_h`
5. Get `current_pct = scroll_bar.start_percentage`
6. Calculate `new_pct = current_pct - (event.y * row_percent)`
7. Clamp to `[0.0, 1.0 - visible_percentage]`
8. Call `scroll_bar.set_scroll_from_start_percentage(new_pct)`

This is ~15 lines of identical logic in each location.

**Impact:** Bug fixes (e.g., scroll speed adjustment) must be applied in multiple places.
**Recommendation:** Add a `handle_mousewheel(event, total_items, row_height)` method to VirtualTable, or create a shared `scroll_wheel_handler()` utility function.
**Effort:** Simple

---

#### MAJOR: Selection Window Pattern Duplicated Across 3 Dialog Classes
**ID:** DUP-SCR-004
**Location:**
- `planet_selection_window.py` (183 lines)
- `fleet_selection_window.py` (113 lines)
- `system_selection_window.py` (111 lines)

**Issue:** All three selection windows follow the exact same structural pattern:
1. Extend `UIWindow`
2. Create `UILabel` header (y=10)
3. Create `UISelectionList` (y=45, height=rect.height-120)
4. Create Confirm `UIButton` (bottom-left, y=rect.height-60)
5. Create Cancel/Any `UIButton` (bottom-right)
6. In `update()`, check `btn_confirm.check_pressed()`, get `selection_list.get_single_selection()`, look up actual object, call callback, kill self
7. Cancel button: kill self

The layout geometry, button positioning, and selection flow are nearly identical. `FleetSelectionWindow` and `SystemSelectionWindow` are particularly close (differ only in the data type and display label formatting).

**Impact:** Adding new selection dialogs requires copy-pasting the same boilerplate. Changes to dialog styling must be applied 3 times.
**Recommendation:** Create a generic `SelectionDialog(UIWindow)` base class that handles the common layout (label, selection list, confirm/cancel buttons) and `update()` loop. Subclasses override only `_format_item(item) -> str` and `_get_selected_item(name) -> T`.
**Effort:** Medium

---

#### MAJOR: Star/Planet Info Formatting Duplicated in 3 Locations
**ID:** DUP-SCR-005
**Location:**
- `strategy_detail_fmt.py:182-197` (`format_star_info`) and `strategy_detail_fmt.py:66-156` (`format_planet_info`)
- `strategy_detail_formatter.py:265-279` (`_format_star`) and `strategy_detail_formatter.py:243-263` (`_format_star_system`)
- `galaxy_test/system_mode.py:383-402` (`_format_star_info`) and `galaxy_test/system_mode.py:404-449` (`_format_planet_info`)

**Issue:** Star formatting is done three ways:
1. `strategy_detail_fmt.format_star_info()` returns HTML with `<b>Star:</b> name<br>...`
2. `strategy_detail_formatter._format_star()` rebuilds the same HTML inline (same fields, same order) instead of calling `format_star_info()`
3. `galaxy_test/system_mode._format_star_info()` returns plain text list with the same fields

The `_format_star_system` method in `strategy_detail_formatter.py:243-263` also duplicates `strategy_detail_fmt.format_star_system_info()` instead of calling it. Both produce the same HTML string with System name, Primary, Type, Mass, Temp, Stars count.

Planet info formatting has 3 independent implementations with overlapping fields (name, type, mass, radius, gravity, temp).

**Impact:** If display format changes (e.g., adding luminosity), 3 locations must be updated. The formatter class was supposed to delegate to `strategy_detail_fmt` (it imports the module) but reimplements the formatting inline.
**Recommendation:** `StrategyDetailFormatter._format_star()` and `._format_star_system()` should call the existing `format_star_info()` and `format_star_system_info()` from `strategy_detail_fmt.py`. The galaxy_test version is a debug display with different format (plain text vs HTML), so partial duplication is acceptable there.
**Effort:** Simple

---

#### MAJOR: Facade-or-Session Command Dispatch Pattern Duplicated
**ID:** DUP-SCR-006
**Location:**
- `build_queue_screen.py:262-266` (`_dispatch_add_to_queue_command`)
- `build_queue_screen.py:298-302` (`_dispatch_remove_from_queue_command`)
- `empire_build_queue_window.py:372-377` (`_add_item_to_source`)

**Issue:** The exact same dispatch pattern is duplicated:
```python
if self.facade:
    self.facade.handle_command(cmd)
else:
    self.session.handle_command(cmd)
```
This 4-line facade-or-session fallback pattern appears 3 times across 2 files, and will spread to any new screen that dispatches commands.

**Impact:** If the dispatch priority changes (e.g., adding a third option), all locations must be updated.
**Recommendation:** Extract a `dispatch_command(cmd, facade, session)` helper function, or use a unified dispatch target (always pass a single command handler rather than facade + session).
**Effort:** Simple

---

#### MAJOR: Data Source Classes Share Identical Boilerplate
**ID:** DUP-SCR-007
**Location:**
- `fleet_data_source.py` (FleetDataSource: 330 lines)
- `planet_data_source.py` (PlanetDataSource: 221 lines)
- `event_log_data_source.py` (EventLogDataSource: 179 lines)
- `empire_build_queue_data_source.py` (BuildQueueDataSource: 115 lines)

**Issue:** All four data sources implement `ITableDataSource` with the same structural pattern:
1. `get_row_count()` -> `len(self._items)`
2. `get_columns()` -> return column list
3. `get_cell_value(row_index, column_id)` -> null-check row, dispatch to column handler
4. `get_X_at_index(row_index)` -> bounds-check and return item or None

The `get_X_at_index` method (get_ship_at_index, get_planet_at_index, get_event_at_index, get_source_at_index) is the same 4-line bounds-checking pattern in all four classes.

**Impact:** The boilerplate makes each new data source ~30 lines of copy-paste setup. The bounds-checking pattern could have subtle inconsistencies.
**Recommendation:** Create an `AbstractTableDataSource(ITableDataSource)` base class with generic implementations of `get_row_count()`, `get_item_at_index(row_index)`, and the bounds-check pattern. Subclasses would only override `get_cell_value` and `get_cell_image`.
**Effort:** Medium

---

#### MAJOR: `get_column_value` / `_extract_value` Logic Duplicated
**ID:** DUP-SCR-008
**Location:**
- `planet_list_filters.py:146-171` (`get_column_value`)
- `planet_data_source.py:139-171` (`_extract_value`)

**Issue:** `PlanetDataSource._extract_value()` is explicitly documented as "Ported from planet_list_filters.get_column_value()" - it is a direct copy of the function from `planet_list_filters.py`. Both implement the same logic: check for `func` key, then `attr` key with dotted path traversal, then `fmt` formatting. The code is nearly line-for-line identical.

**Impact:** Bug fixes must be applied in both places. The original function still exists and is importable.
**Recommendation:** `PlanetDataSource._extract_value()` should delegate to `planet_list_filters.get_column_value()` rather than duplicating it.
**Effort:** Simple

---

#### MAJOR: Mass Earth Constant Duplicated 4+ Times
**ID:** DUP-SCR-009
**Location:**
- `planet_list_filters.py:19` (`m_earth_const = 5.97e24`)
- `planet_list_filters.py:183` (`m_earth = 5.97e24`)
- `planet_list_filters.py:283` (`m_earth = 5.97e24`)
- `strategy_detail_fmt.py:81` (`m_earth = 5.97e24`)
- `galaxy_test/system_mode.py:409` (imports `MASS_EARTH` from `planet_physics`)

**Issue:** The Earth mass constant `5.97e24` is defined as a local variable in 4 different places across 2 files, plus it already exists as a proper constant in `game.strategy.data.planet_physics.MASS_EARTH`. The `galaxy_test/system_mode.py` correctly imports the constant, but the other files hardcode the magic number.

**Impact:** If the constant needs to change (unlikely for Earth mass, but the pattern signals broader magic number issues), 4 locations must be found and updated.
**Recommendation:** Replace all `5.97e24` literals with `from game.strategy.data.planet_physics import MASS_EARTH` (or from a `game.core.constants` location). Also replace `9.81` gravity constant similarly.
**Effort:** Simple

---

#### MAJOR: Screenshot Handling Pattern Duplicated
**ID:** DUP-SCR-010
**Location:**
- `build_queue_screen.py:533-537` (`_take_screenshot`)
- `planet_list_window.py:448-454` (`_take_screenshot`)
- `strategy_ui_action_router.py:103-111` (inline screenshot logic)
- `workshop_screen.py:70` (stores instance, handles separately)

**Issue:** The screenshot handling follows the same 3-line pattern:
```python
sm = ScreenshotManager.instance()
sm.capture(label="some_label")
sm.show_toast(self.manager, self.screen_width)
```
Each screen reimplements this as a private `_take_screenshot()` method. The F11/F12 key check is also duplicated in each screen's event handler.

**Impact:** If screenshot behavior changes (e.g., adding a sound effect, changing toast position), multiple locations need updating.
**Recommendation:** Add a `ScreenshotManager.capture_and_toast(label, manager, width)` convenience method. For the F11/F12 detection, consider handling it in a shared base class or in the input mapper.
**Effort:** Simple

---

#### MINOR: Header Sort/Swap Handling Pattern Duplicated Across Windows
**ID:** DUP-SCR-011
**Location:**
- `fleet_report_window.py:305-314` (update method)
- `planet_list_window.py:325-334` (update method)
- `empire_build_queue_window.py:455-467` (update method)
- `event_log_window.py:278-290` (update method)

**Issue:** All four windows check `virtual_table.check_header_presses()` and handle `swap_column` and `sort_column` results with the same if/elif pattern:
```python
header_result = self.virtual_table.check_header_presses()
if header_result.get('swap_column'):
    col_dict, direction = header_result['swap_column']
    self.column_manager.swap_column(col_dict['id'], direction)
    self.virtual_table.rebuild_headers()
    self.virtual_table.rebuild_row_pool()
    self._refresh_list()
elif header_result.get('sort_column'):
    # sort handling
```

**Impact:** Boilerplate that must be copy-pasted into each new VirtualTable-backed window.
**Recommendation:** Add a `VirtualTable.process_header_actions()` method that handles swap/sort internally and returns a bool indicating if refresh is needed.
**Effort:** Simple

---

#### MINOR: Kill Pattern with VirtualTable + Close Callback
**ID:** DUP-SCR-012
**Location:**
- `fleet_report_window.py:358-370`
- `planet_list_window.py:527-542`
- `event_log_window.py:373-379`
- `empire_build_queue_window.py:554-559`
- `build_queue_list_window.py:123-129`
- `empire_panel_window.py:499-503`

**Issue:** All windows follow the same `kill()` pattern: clean up VirtualTable (if any), clean up child panels, call `on_close_callback`, call `super().kill()`. The VirtualTable cleanup is particularly repetitive:
```python
if self.virtual_table:
    self.virtual_table.kill()
```

**Impact:** Easy to forget cleanup steps when adding new windows.
**Recommendation:** Consider a `VirtualTableWindow(UIWindow)` mixin or base class that handles VirtualTable cleanup and close callback invocation automatically.
**Effort:** Medium

---

#### MINOR: Tri-State Filter Widget Polling Pattern Duplicated
**ID:** DUP-SCR-013
**Location:**
- `fleet_report_sidebar.py:507-512` (in `check_button_presses`)
- `empire_build_queue_sidebar.py:193-209` (`check_tri_state_presses`)

**Issue:** Both sidebars poll tri-state filter widgets with the same loop:
```python
for attr_name, widget in self.tri_state_widgets.items():
    new_state = widget.check_pressed()
    if new_state is not None:
        widget.set_state(new_state)
        # handle state change
```

**Impact:** Minor — only 2 occurrences. But the pattern would grow with more sidebars.
**Recommendation:** Extract a `poll_tri_state_widgets(widgets_dict)` helper or make the `ColumnToggleSection` (from DUP-SCR-001) also handle tri-state filters.
**Effort:** Simple

---

#### MINOR: Population Formatting with K/M Suffixes Duplicated
**ID:** DUP-SCR-014
**Location:**
- `strategy_detail_fmt.py:109-121` (population K/M/raw formatting)
- `planet_list_filters.py:297-308` (resource quantity K/M formatting)

**Issue:** The pattern of formatting large numbers with K/M suffixes appears in both files:
```python
if value >= 1_000_000:
    str = f"{value / 1_000_000:.1f}M"
elif value >= 1_000:
    str = f"{value / 1_000:.0f}K"
else:
    str = str(value)
```

**Impact:** Minor — the formatting thresholds or precision could diverge between the two uses.
**Recommendation:** Extract a `format_quantity(value) -> str` utility function in a shared formatting module.
**Effort:** Simple

---

#### MINOR: Sidebar Panel Layout Initialization Pattern
**ID:** DUP-SCR-015
**Location:**
- `fleet_report_window.py:91-96` (sidebar_panel creation)
- `planet_list_window.py:99-104` (sidebar_panel creation)
- `event_log_window.py:99-104` (sidebar_panel creation)
- `empire_build_queue_window.py:121-126` (sidebar_panel creation)
- `design_selector_window.py:93-98` (sidebar_panel creation)

**Issue:** All 5 windows create their sidebar panel with the same UIPanel constructor call:
```python
self.sidebar_panel = UIPanel(
    relative_rect=pygame.Rect(0, 0, self.sidebar_width, height),
    manager=manager,
    container=self,
    anchors={'left': 'left', 'top': 'top', 'bottom': 'bottom'}
)
```

**Impact:** Boilerplate that adds ~5 lines to each new window.
**Recommendation:** This would be addressed by the VirtualTableWindow base class (DUP-SCR-012), which could provide a standard sidebar creation method.
**Effort:** Medium (part of larger refactor)

---

#### MINOR: `_get_column_value` Duplicated Between Window and DataSource
**ID:** DUP-SCR-016
**Location:**
- `empire_build_queue_window.py:481-489` (`_get_column_value`)
- `empire_build_queue_data_source.py:93-114` (`_get_column_value`)

**Issue:** Both the window and data source classes implement `_get_column_value` methods that delegate to the same ViewModel. The window method exists for sort support, but it duplicates the system/sector special-case handling from the data source.

**Impact:** Column value extraction logic must be maintained in two places.
**Recommendation:** Have the window delegate to the data source's method for column value extraction, or move sorting into the ViewModel which already knows about column values.
**Effort:** Simple

---

## Top 5 Priority Consolidations

1. **DUP-SCR-002 + DUP-SCR-003 + DUP-SCR-011: VirtualTable lifecycle methods** - Add `full_refresh()`, `rebuild_and_refresh()`, `handle_mousewheel()`, and `process_header_actions()` to VirtualTable itself. This eliminates ~80 lines of boilerplate across 5+ windows with zero risk (pure addition to VirtualTable API). **Effort: Simple, Impact: High.**

2. **DUP-SCR-001: Column Toggle Section** - Extract a reusable `ColumnToggleSection` component from the 4 sidebar implementations. This is the most duplicated single pattern. **Effort: Simple, Impact: High.**

3. **DUP-SCR-004: Selection Dialog Base Class** - Create `SelectionDialog` base for 3 selection windows. Eliminates ~150 lines of duplicate layout code and simplifies adding new selection dialogs. **Effort: Medium, Impact: Medium.**

4. **DUP-SCR-005 + DUP-SCR-008: Formatter Delegation** - Fix `StrategyDetailFormatter` to call `strategy_detail_fmt` functions instead of reimplementing them. Fix `PlanetDataSource._extract_value` to delegate to `planet_list_filters.get_column_value`. Both are simple function call replacements. **Effort: Simple, Impact: Medium.**

5. **DUP-SCR-007: Abstract Data Source Base** - Create `AbstractTableDataSource` with generic bounds-checking and row-count implementations. Reduces ~120 lines of boilerplate across 4 data sources. **Effort: Medium, Impact: Medium.**
