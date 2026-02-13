# PROJ-89: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The remaining UI tier god classes were identified by analyzing all UI-layer files over 500 lines. Two files clearly exceed the threshold and have extractable concerns:

- **DesignSelectorWindow** (`game/ui/screens/design_selector_window.py`): 716 lines, 17 methods. Contains 168 lines of pure image loading/processing that has zero coupling to UI state or event handling.
- **EmpireBuildQueueWindow** (`game/ui/screens/empire_build_queue_window.py`): 948 lines, 30 methods. Contains ~100 lines of pure data formatting (static methods) and ~150 lines of self-contained filter state management.

Four other UI screens were evaluated and **skipped**:
- **RaceSetupScreen**: Already well-decomposed with `race_asset_loader.py`, `race_validator.py`, `race_browser_dialog.py`
- **FleetReportWindow**: Already decomposed with `fleet_report_view_model.py`, `fleet_report_filters.py`, `column_manager.py`
- **FormationEditor**: Moderate size, tightly coupled rendering logic, marginal decomposition gains
- **StrategyScreen**: Already decomposed with `strategy_camera_nav.py`, `strategy_colonization.py`, `strategy_fleet_ops.py`, `strategy_input_handler.py`, `strategy_menu_panel.py`, `strategy_renderer.py`, `strategy_detail_fmt.py`, `strategy_ui.py`

## Swarm Findings Summary

### Architecture

**DesignSelectorWindow (716 lines, 17 methods)**
- UIWindow subclass for browsing and selecting ship designs from the design library
- Image loading methods (`_load_portrait_thumbnail`, `_load_topdown_thumbnail`, `_get_visible_bounding_box`) are 168 lines of pure utility code
- Image methods only depend on `pygame`, `os`, and `DesignMetadata` type hints - zero dependency on UIWindow state
- These methods are called only from `_create_design_row()` and could be reused by FleetReportWindow or other screens
- Remaining 548 lines are core UI: sidebar creation, event handling, filter state, design list rendering

**EmpireBuildQueueWindow (948 lines, 30 methods)**
- UIWindow subclass for empire-wide build queue management
- Data formatting methods (lines 492-933): `_get_queue_summary`, `_get_first_item_text`, `_get_capabilities_text`, `_get_system_name`, `_get_sector_text`, `_get_turns_left_text` - most are `@staticmethod`, pure data transforms
- Filter management (lines 604-865): filter state dicts, `_filter_sources()`, `apply_filters()`, sidebar filter UI builders, filter toggle handlers - self-contained state management cluster
- Column system (lines 548-598): `_get_visible_columns()`, `_get_column_value()`, `toggle_column_visibility()` - bridges formatter and filter systems
- Blast radius: LOW - both classes are UI endpoints with no downstream dependents

### Key Patterns to Reuse
- **fleet_report_filters.py**: `game/ui/screens/fleet_report_filters.py` - Existing pattern for extracting filter logic from a window class. Contains filter state, predicate methods, and toggle handlers in a standalone class.
- **column_manager.py**: `game/ui/screens/column_manager.py` - Existing pattern for extracting column configuration from a window class.
- **fleet_report_view_model.py**: `game/ui/screens/fleet_report_view_model.py` - Existing pattern for extracting data formatting from a window class.

### Dependencies & Risks
1. **Existing tests call methods on window class directly** - Mitigated by facade pattern: original classes keep their public API and delegate to helpers internally. All 1359 lines of existing tests continue to work unchanged.
2. **Image helper depends on pygame** - Acceptable since it is a UI-tier module. Tests already mock pygame for portrait tests.
3. **Filter manager needs galaxy reference for system name lookups** - `_get_system_name` is an instance method (not static) because it needs `self.galaxy`. The formatter will accept galaxy as a parameter for this one method.

### Opportunities Discovered
- **Design image helper is reusable**: The portrait and top-down thumbnail loading could be used by FleetReportWindow, BuildQueueListWindow, or any screen that shows ship design previews. Extracting it now creates a shared utility.
- **Formatter static methods are trivially testable**: All `@staticmethod` formatters can be tested without any pygame or UI mocking.
- **Filter manager pattern aligns with FleetReportWindow**: The extracted filter manager will follow the same pattern as `fleet_report_filters.py`, creating consistency across the codebase.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
