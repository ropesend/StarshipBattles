# PROJ-62: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State
`planet_list_window.py` is 1136 lines with 21 methods and ~35 instance variables. Three modules have already been extracted:
- `planet_list_filters.py` (173 lines) - gather, filter, sort, get_column_value
- `planet_list_presets.py` (183 lines) - PresetManager, capture/apply state
- `planet_report_panel.py` (269 lines) - Right-side detail panel widget

### Method Inventory
| Method | Lines | Category |
|--------|-------|----------|
| `__init__` | 16-158 (143 lines) | Initialization |
| `_get_system_name` | 159-162 (4 lines) | Data accessor |
| `_get_owner_name` | 164-181 (18 lines) | Data accessor |
| `_get_mass_earth` | 183-185 (3 lines) | Data accessor |
| `_get_resource_str` | 187-201 (15 lines) | Data accessor |
| `_compute_planet_ranges` | 203-249 (47 lines) | Data processing |
| `_init_sidebar` | 251-462 (212 lines) | UI construction |
| `_rebuild_headers` | 464-526 (63 lines) | Column management |
| `_swap_columns` | 528-551 (24 lines) | Column management |
| `refresh_list` | 554-595 (42 lines) | Coordination |
| `_rebuild_row_pool` | 597-653 (57 lines) | Virtual rendering |
| `_update_visible_rows` | 655-743 (89 lines) | Virtual rendering |
| `process_event` | 745-874 (130 lines) | Event handling |
| `update` | 876-1029 (154 lines) | Update loop |
| `_capture_current_state` | 1030-1035 (6 lines) | Presets |
| `_apply_state` | 1037-1045 (9 lines) | Presets |
| `_get_visible_columns` | 1047-1049 (3 lines) | Column management |
| `_take_screenshot` | 1051-1055 (5 lines) | Utility |
| `_show_screenshot_toast` | 1058-1070 (13 lines) | Utility |
| `_on_planet_selected` | 1072-1120 (49 lines) | Selection |
| `kill` | 1122-1135 (14 lines) | Cleanup |

### Callers
- `game/ui/screens/strategy_ui.py` line 17 - creates PlanetListWindow instances
- Tests: `tests/integration/ui/test_planet_list_window.py`, `tests/repro_issues/test_crash_planet_list*.py`
- Benchmark: `tests/performance/benchmark_planet_list.py`

## Swarm Findings Summary

### Architecture
The file follows a common pygame_gui pattern: UIWindow subclass managing child widgets. The main complexity comes from:
1. **Sidebar construction** (212 lines of dense widget creation)
2. **Virtual scrolling** (row pool + icon cache + scroll math)
3. **Update loop** (154 lines checking many independent button states)

### Key Patterns to Reuse
- **race_setup_screen.py**: Extracted panels into separate classes, main screen coordinates
- **strategy_ui.py**: Composition with specialized renderers/panels
- **workshop_screen.py**: MVVM with event router and data loader

### Dependencies & Risks
1. **Bidirectional state** - Sidebar UI widgets must sync with filter state. Mitigation: sidebar builder returns widget references; main window owns state.
2. **Scroll calculations** - Row pool + scroll offset math is fragile. Mitigation: keep all scroll math in one class (VirtualListRenderer).
3. **Widget cleanup** - Extracted classes must properly kill() their widgets. Mitigation: each class responsible for its own cleanup.

### Opportunities Discovered
- `_compute_planet_ranges()` is pure data processing - belongs in filters module
- Data accessors (`_get_system_name`, `_get_owner_name`, etc.) have no UI dependencies
- Column definitions (lines 71-93) could be data-driven from a config

## Design Decisions

### 1. Sidebar: `build_sidebar()` function
Returns a dict/namespace of widget references. No class needed because sidebar construction is a one-time operation with no ongoing behavior.

```python
# planet_list_sidebar.py
def build_sidebar(manager, container, sidebar_width, rect_height,
                  planet_ranges, columns, preset_manager):
    """Build all sidebar widgets. Returns dict of widget references."""
    # ... all sidebar construction code ...
    return {
        'txt_name_filter': txt_name_filter,
        'btn_apply': btn_apply,
        'btn_all_types': btn_all_types,
        'btn_none_types': btn_none_types,
        'btn_all_owners': btn_all_owners,
        'btn_none_owners': btn_none_owners,
        'ui_filters': ui_filters,
        'dd_presets': dd_presets,
        'txt_preset_name': txt_preset_name,
        'btn_save_preset': btn_save_preset,
        'sidebar_panel': sidebar_panel,
    }
```

### 2. Column Manager: `ColumnManager` class
Owns columns list, sort state, header widgets. Exposes methods for header rebuilding, column swapping, visibility toggling.

```python
# planet_list_columns.py
class ColumnManager:
    def __init__(self, columns, manager, header_container):
        self.columns = columns
        self.sort_column_id = 'owner'
        self.sort_descending = False
        self.header_elements = []

    def get_visible_columns(self): ...
    def rebuild_headers(self): ...
    def swap_columns(self, col_ref, direction): ...
    def handle_header_clicks(self): ...  # Returns True if sort/order changed
    def toggle_visibility(self, col_id): ...
```

### 3. Virtual List Renderer: `VirtualListRenderer` class
Owns row pool, icon cache, dirty tracking. Updates visible rows based on scroll position.

```python
# planet_list_renderer.py
class VirtualListRenderer:
    def __init__(self, list_panel, row_height, manager):
        self.row_pool = []
        self._icon_cache = {}
        self._last_scroll_pct = -1.0
        self._last_filtered_count = -1

    def rebuild_row_pool(self, visible_columns): ...
    def update_visible_rows(self, filtered_planets, scroll_bar): ...
    def get_clicked_planet_index(self, mouse_pos, list_abs_rect,
                                  scroll_bar, filtered_planets): ...
    def kill(self): ...
```

See [decisions.md](decisions.md) for the full log with rationale.
