# PROJ-220 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## New Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/ui/filters/__init__.py` | Production | 1 | Package init, exports FilterState + FilterStateManager |
| `game/ui/filters/filter_state.py` | Production | 1 | FilterState enum (YES/NO/IGNORE) |
| `game/ui/filters/filter_state_manager.py` | Production | 1 | FilterStateManager base class |
| `game/ui/components/filters/__init__.py` | Production | 2 | Package init, exports TriStateFilterWidget |
| `game/ui/components/filters/tri_state_widget.py` | Production | 2 | TriStateFilterWidget pygame component |
| `game/ui/screens/planet_list_filter_manager.py` | Production | 5 | PlanetListFilterManager (wraps FilterStateManager) |
| `tests/unit/ui/filters/__init__.py` | Test | 1 | Test package init |
| `tests/unit/ui/filters/test_filter_state.py` | Test | 1 | FilterState enum tests |
| `tests/unit/ui/filters/test_filter_state_manager.py` | Test | 1 | FilterStateManager tests |
| `tests/unit/ui/components/filters/__init__.py` | Test | 2 | Test package init |
| `tests/unit/ui/components/filters/test_tri_state_widget.py` | Test | 2 | TriStateFilterWidget tests |
| `tests/unit/ui/screens/test_planet_list_filter_manager.py` | Test | 5 | PlanetListFilterManager tests |

## Modified Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `data/builder_theme.json` | Config | 2 | Add `@tri_state_radio` theme entry |
| `game/ui/screens/fleet_report_filters.py` | Production | 3 | Refactor exclusion functions to accept FilterState |
| `game/ui/screens/fleet_report_view_model.py` | Production | 3 | Replace 16 bool attrs with FilterStateManager |
| `game/ui/screens/fleet_report_sidebar.py` | Production | 3 | Replace paired buttons with TriStateFilterWidget |
| `game/ui/screens/fleet_report_window.py` | Production | 3 | Update filter toggle wiring |
| `game/ui/screens/empire_build_queue_filter_manager.py` | Production | 4 | Replace 3 filter dicts with FilterStateManager |
| `game/ui/screens/empire_build_queue_viewmodel.py` | Production | 4 | Update toggle/filter API for tri-state |
| `game/ui/screens/empire_build_queue_sidebar.py` | Production | 4 | Replace toggle buttons with TriStateFilterWidget |
| `game/ui/screens/empire_build_queue_window.py` | Production | 4 | Update filter state wiring |
| `game/ui/screens/planet_list_window.py` | Production | 5 | Delegate state to PlanetListFilterManager |
| `game/ui/screens/planet_list_presets.py` | Production | 5 | Fix owner filter preset restore |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Test | 3 | Update 59 tests for FilterState API |
| `tests/unit/ui/test_fleet_list_view_model.py` | Test | 3 | Update for FilterStateManager API |
| `tests/unit/ui/screens/test_fleet_report_window.py` | Test | 3 | Update for tri-state sidebar |
| `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` | Test | 4 | Update 32 tests for FilterState API |
| `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` | Test | 4 | Update 51 tests for tri-state API |
| `tests/unit/ui/screens/test_empire_build_queue_window.py` | Test | 4 | Update 119 tests for tri-state API |
