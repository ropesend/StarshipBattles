# Consistency Violations Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 131
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 5 | **Minor:** 9 | **Info:** 3

## Findings

#### CRITICAL: Inconsistent Return Pattern for Not-Found Scenarios
**ID:** CON-UI1-001
**Location:** `game/ui/screens/` (multiple files)
**Issue:** Methods handling "not found" scenarios use inconsistent patterns: some return `None`, others raise exceptions, others return empty collections. For example:
- `get_hovered_component()` returns `None` (left_panel.py:475)
- `get_target_layer_at()` returns `None` (layer_panel.py:447)
- `load_battle_setup()` returns `None` on error (setup_data_io.py:233)
- Some methods raise exceptions on invalid input

**Impact:** Callers must guess whether to check for None, catch exceptions, or check for empty results. This inconsistency can lead to NoneType errors or unhandled exceptions at runtime.
**Recommendation:** Standardize to: Use Optional[T] with `None` return for "no result found", raise specific exceptions for actual errors (file not found, validation failure). Document the pattern in CLAUDE.md.
**Effort:** Complex

#### MAJOR: Mixed UIConfig Usage vs Magic Numbers
**ID:** CON-UI1-002
**Location:** `game/ui/screens/` (71+ files use hardcoded values)
**Issue:** Only 13 of 80+ files in screens directory import UIConfig. The remaining files use hardcoded magic numbers for dimensions like `pygame.Rect(10, y, 100, 30)`, `pygame.Rect(0, 0, 300, 200)`, etc.
- Files using UIConfig: fleet_report_window.py, planet_list_window.py, empire_build_queue_window.py, etc.
- Files with hardcoded values: new_game_setup_screen.py, design_selector_window.py, fleet_orders_window.py, cargo_quick_dialog.py, etc.

**Impact:** Inconsistent layout constants make global UI adjustments difficult and lead to visual inconsistencies. Hard to maintain minimum resolution requirements (2560x1600).
**Recommendation:** Migrate all hardcoded dimension values to UIConfig constants. Add section-specific constants (e.g., `DIALOG_PADDING`, `FILTER_BUTTON_HEIGHT`).
**Effort:** Medium

#### MAJOR: Inconsistent Method Verb Prefixes for Data Access
**ID:** CON-UI1-003
**Location:** `game/ui/screens/` (80 occurrences of `get_`, 22 of `load_`, 4 of `refresh_`)
**Issue:** Data access methods use inconsistent verb prefixes:
- `get_` prefix: 80+ usages (get_column_value, get_filtered_ships, get_hovered_component)
- `load_` prefix: 22 usages (load_portrait_thumbnail, load_formation, load_ship)
- `refresh_` prefix: 4 usages (refresh_list, refresh_available_components)

Some semantic confusion exists:
- `load_` is used both for file I/O (load_formation) and UI initialization (load_resource_icons)
- `get_` is used for both pure getters (get_column_value) and computed values with side effects

**Impact:** Developers cannot predict method behavior from name alone. Cognitive overhead when navigating codebase.
**Recommendation:** Standardize: `get_*` for pure getters (no I/O, no side effects), `load_*` for file/asset I/O, `fetch_*` for network/external data, `refresh_*`/`rebuild_*` for UI state updates.
**Effort:** Medium

#### MAJOR: Inconsistent Event Handler Naming
**ID:** CON-UI1-004
**Location:** `game/ui/screens/` (multiple patterns)
**Issue:** Event handlers use mixed naming conventions:
- `_handle_*` pattern: 41 usages (_handle_keydown, _handle_row_click, _handle_button_press)
- `on_*` pattern: 34 usages (on_colonize_click, on_ui_selection, on_menu_option)
- `process_event` pattern: some classes use this

No clear rule for when to use `_handle_*` vs `on_*`:
- Some files use both patterns (strategy_screen.py has both `on_colonize_click` and `_handle_*` methods)
- Public callbacks use `on_*`, internal handlers use `_handle_*` in some files but not consistently

**Impact:** Difficult to distinguish between internal handlers and public callback hooks.
**Recommendation:** Standardize: `_handle_*` for internal event handling methods (private), `on_*` for public callback hooks that external code can subscribe to.
**Effort:** Medium

#### MAJOR: Missing Type Hints on Key Public Methods
**ID:** CON-UI1-005
**Location:** `game/ui/screens/battle_panels.py`, `game/ui/screens/setup_screen.py`, others
**Issue:** While 46 files import from `typing` and use type hints, many public methods lack return type annotations:
- `draw(self, screen)` in BattlePanel - no return type
- `handle_click(self, mx, my)` in BattlePanel - returns bool but not annotated
- `_get_ships(self)` - returns list but not annotated

Files with good type coverage: build_queue_screen.py, fleet_report_view_model.py, formation_editor.py
Files with poor type coverage: battle_panels.py, setup_screen.py, many builder/* files

**Impact:** Type checkers cannot verify correctness. IDE autocompletion degraded. Documentation incomplete.
**Recommendation:** Add return type annotations to all public methods. Prioritize facade/public API methods first.
**Effort:** Medium

#### MAJOR: Inconsistent Docstring Format
**ID:** CON-UI1-006
**Location:** Throughout game/ui/screens/ and game/ui/panels/
**Issue:** Multiple docstring styles are in use:
- Google style (Args:/Returns: sections): build_queue_screen.py, ship_detail_panel.py
- Inline comments only: battle_panels.py base BattlePanel class
- No docstrings: Some internal methods

Examples:
- `BuildQueueScreen.__init__` uses proper Args: section
- `BattlePanel.__init__` has no docstring
- `StatRow.__init__` in design_stats_panel.py uses Args: section

**Impact:** Inconsistent documentation makes onboarding harder. Automated doc generation produces mixed results.
**Recommendation:** Standardize on Google-style docstrings for all public methods. Required: one-line summary, Args section for methods with parameters, Returns section for non-void methods.
**Effort:** Medium

#### MINOR: Inconsistent Import Organization
**ID:** CON-UI1-007
**Location:** Throughout game/ui/screens/
**Issue:** Import organization varies between files:
- Most files: `from __future__ import annotations` first when present (28 files)
- Standard library imports not always grouped separately
- `from game.ui.config import UIConfig` sometimes grouped with other game imports, sometimes separate

Some files have cleaner organization (build_queue_screen.py: future -> stdlib -> pygame -> game imports)
Others have mixed organization (battle_panels.py: pygame first, no future import)

**Impact:** Minor readability issue. Makes automated import sorting harder.
**Recommendation:** Standardize import order: `__future__` -> stdlib -> third-party (pygame) -> game modules. Add isort configuration.
**Effort:** Simple

#### MINOR: Mixed Boolean Naming Conventions
**ID:** CON-UI1-008
**Location:** `game/ui/screens/` (multiple files)
**Issue:** Boolean variables and methods use inconsistent prefixes:
- `is_*` prefix: is_selected, is_expanded, is_final, is_warp_capable
- `has_*` prefix: has_yard, has_cargo, has_items
- `show_*` prefix: show_complexes, show_requirements
- No prefix: `visible`, `readonly`

Methods:
- `is_filter_enabled()` in fleet_report_view_model.py
- `is_modifier_allowed()` in modifier_logic.py
- `_is_expanded()` in battle_panels.py

**Impact:** Minor inconsistency. Most usage is reasonable (is_ for state, has_ for existence, show_ for UI display).
**Recommendation:** Document convention: `is_*` for object state, `has_*` for possession/existence, `can_*` for capability, `show_*` for UI visibility toggles.
**Effort:** Simple

#### MINOR: Inconsistent Private Method Prefix Usage
**ID:** CON-UI1-009
**Location:** `game/ui/panels/`, `game/ui/screens/`
**Issue:** Private methods (single underscore) are used inconsistently:
- Panel classes consistently use `_` prefix for internal methods (_show_placeholder, _clear_elements, _build_ship_display)
- Some screen classes expose methods without underscore that should be private
- Some classes use double underscore `__` unnecessarily

**Impact:** API boundary unclear. External code might call internal methods.
**Recommendation:** Consistently use single `_` prefix for all internal methods not intended for external use.
**Effort:** Simple

#### MINOR: Inconsistent Window Class Inheritance
**ID:** CON-UI1-010
**Location:** `game/ui/screens/` (Window classes)
**Issue:** Window classes inherit from pygame_gui differently:
- Some use: `class FleetReportWindow(UIWindow):` with `from pygame_gui.elements import UIWindow`
- Others use: `class RaceBrowserDialog(pygame_gui.elements.UIWindow):`
- Others use: `class FleetOrdersWindow(pygame_gui.elements.UIWindow):`

This is just import style but creates inconsistency in how classes appear in the codebase.

**Impact:** Minor code style inconsistency.
**Recommendation:** Standardize on importing UIWindow directly: `from pygame_gui.elements import UIWindow` then `class X(UIWindow):`.
**Effort:** Simple

#### MINOR: Missing UIConfig Constants for Common Values
**ID:** CON-UI1-011
**Location:** `game/ui/screens/` and `game/ui/panels/`
**Issue:** Several commonly-used dimension values appear repeatedly but are not in UIConfig:
- `row_height = 28` appears in multiple places (modifier_row.py, build_queue_selector.py)
- `y += 30` / `y += 35` spacing values repeated throughout
- Portrait sizes (120, 150) used in multiple panels
- Margin values (10, 20) hardcoded everywhere

**Impact:** Changing common spacing requires finding all instances manually.
**Recommendation:** Add to UIConfig: ROW_HEIGHT_COMPACT=28, PORTRAIT_SMALL=120, PORTRAIT_MEDIUM=150, MARGIN_STANDARD=10, SECTION_GAP=35
**Effort:** Simple

#### MINOR: Inconsistent Error Handling Granularity
**ID:** CON-UI1-012
**Location:** `game/ui/screens/` (50+ exception handlers)
**Issue:** Exception handling varies in granularity:
- Very broad: `except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:` (setup_data_io.py:50)
- Appropriately narrow: `except ValueError:` (column_manager.py:128)
- Too broad: `except Exception as e:` (event_bus.py:55 - but has justification comment)

Some files log errors, others silently return None.

**Impact:** Error diagnosis harder with broad catches. Some errors may be masked.
**Recommendation:** Prefer specific exceptions. When broad catch needed, document why with comment. Always log the error.
**Effort:** Simple

#### MINOR: Inconsistent Logging Import Patterns
**ID:** CON-UI1-013
**Location:** `game/ui/screens/` (60+ log calls)
**Issue:** Logging imports vary:
- Most use: `from game.core.logger import log_info, log_warning, log_debug` (selective imports)
- Some use: `from game.core.logger import log_error` only
- Not all files with error handling import logging

Files without logging that handle errors: column_manager.py, planet_list_columns.py (use silent return None)

**Impact:** Error diagnosis incomplete when logging not used consistently.
**Recommendation:** All files that handle exceptions should import and use appropriate log functions.
**Effort:** Simple

#### MINOR: Inconsistent kill() Method Implementations
**ID:** CON-UI1-014
**Location:** `game/ui/panels/`, `game/ui/screens/`
**Issue:** Panel/widget classes implement cleanup differently:
- Some have comprehensive `kill()` methods (ship_detail_panel.py: clears elements, kills panel)
- Some only kill the main container (design_stats_panel.py: kills scroll container)
- Some have no kill() method (rely on pygame_gui cleanup)

**Impact:** Potential memory leaks or orphaned UI elements if cleanup is incomplete.
**Recommendation:** All panel classes should implement `kill()` that cleans up all managed UI elements and clears internal state.
**Effort:** Simple

#### INFO: Natural Variation in Class Structure
**ID:** CON-UI1-015
**Location:** `game/ui/screens/builder/`, `game/ui/panels/`
**Issue:** Different architectural approaches used:
- Some classes are pure data holders (StatRow)
- Some are pygame_gui wrappers (DesignStatsPanel, ShipDetailPanel)
- Some inherit from pygame_gui (FleetReportWindow extends UIWindow)
- Some use composition (BuildQueueScreen contains UIManager)

**Impact:** This is natural variation based on purpose, not a consistency issue.
**Recommendation:** Document the patterns in architecture docs: when to extend pygame_gui vs wrap vs compose.
**Effort:** N/A

#### INFO: Two Panel Patterns Coexist
**ID:** CON-UI1-016
**Location:** `game/ui/panels/`
**Issue:** Two patterns for panel implementation:
1. **Widget pattern**: Class manages its own UI elements, has `kill()` method (PlanetReportPanel, ShipDetailPanel, DesignStatsPanel)
2. **Pure render pattern**: Class only draws to surface, no managed elements (BattlePanel, DataGraph)

**Impact:** This is intentional separation between managed UI panels and raw rendering. Not a consistency violation.
**Recommendation:** Document both patterns. Widget pattern for interactive panels, pure render for performance-critical drawing.
**Effort:** N/A

#### INFO: Module-Level Functions vs Class Methods
**ID:** CON-UI1-017
**Location:** `game/ui/screens/`
**Issue:** Some modules use module-level functions for shared logic:
- `compute_planet_production()` in planet_report_panel.py
- `get_damage_color()` in ship_detail_panel.py
- `format_planet_info()` in strategy_detail_fmt.py
- `calculate_fleet_stats()` in fleet_report_filters.py

While most logic is in class methods.

**Impact:** This is appropriate - pure functions that don't need instance state are correctly module-level.
**Recommendation:** Continue pattern: pure utility functions at module level, stateful operations as class methods.
**Effort:** N/A

#### INFO: Facade Pattern Used Correctly
**ID:** CON-UI1-018
**Location:** `game/ui/screens/strategy_screen.py`
**Issue:** StrategyScreen uses StrategySessionFacade for UI-to-engine communication while maintaining internal property shortcuts for convenience (`self.galaxy`, `self.empires`).
**Impact:** This is the correct facade pattern usage - facade for cross-layer communication, properties for internal convenience.
**Recommendation:** Good pattern. Document that internal property shortcuts are acceptable within the same class.
**Effort:** N/A

## Top 5 Priority Issues

1. **CON-UI1-001 (CRITICAL)**: Inconsistent return patterns for not-found scenarios create runtime error risk. Standardize None returns for "not found" vs exceptions for actual errors.

2. **CON-UI1-002 (MAJOR)**: Mixed UIConfig usage vs magic numbers (only 13/80+ files use UIConfig). High-value cleanup for UI maintainability.

3. **CON-UI1-005 (MAJOR)**: Missing type hints on key public methods (BattlePanel, SetupScreen). Impacts type safety and IDE support.

4. **CON-UI1-003 (MAJOR)**: Inconsistent method verb prefixes (get_ vs load_ vs refresh_). Document conventions to reduce cognitive load.

5. **CON-UI1-004 (MAJOR)**: Mixed event handler naming (_handle_* vs on_*). Clarify public callback hooks vs internal handlers.
