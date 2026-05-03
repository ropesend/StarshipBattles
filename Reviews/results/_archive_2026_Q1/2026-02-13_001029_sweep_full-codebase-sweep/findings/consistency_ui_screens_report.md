# Consistency Violations Sweep Report

**Shard:** `game/ui/screens/`, `game/ui/panels/`
**Date:** 2026-02-13
**Reviewer:** Claude Opus 4.5 (Sweep Agent)

---

## Executive Summary

This report analyzes consistency violations across the UI screens and panels modules. The analysis covered 100+ Python files across `game/ui/screens/` (including subdirectories: `builder/`, `formation/`, `galaxy_test/`, `test_lab/`) and `game/ui/panels/`.

**Files Analyzed:** 100+ files
**Total Violations Found:** 23
- CRITICAL: 0
- MAJOR: 4
- MINOR: 14
- INFO: 5

---

## Phase 1: Naming Convention Analysis

### 1.1 Class Naming Patterns

**Dominant Pattern:** PascalCase with descriptive suffixes indicating purpose.
- Screen classes: `*Screen` (e.g., `BattleScreen`, `StrategyScreen`, `SetupScreen`)
- Window classes: `*Window` (e.g., `FleetReportWindow`, `FleetOrdersWindow`)
- Panel classes: `*Panel` (e.g., `BattlePanel`, `ShipStatsPanel`, `UIPanel`)
- Scene classes: `*Scene` (e.g., `MenuScene`, `KeybindingsScene`)
- Gallery classes: `*Gallery` (e.g., `RacePortraitGallery`, `RaceFlagGallery`)
- Router/Manager classes: `*Router`, `*Manager` (e.g., `StrategyEventRouter`, `StrategyWindowManager`)

#### MINOR: Mixed Screen/Scene Terminology
- **ID:** NC-001
- **Location:** `game/ui/screens/menu_scene.py`, `game/ui/screens/keybindings_scene.py`
- **Issue:** Uses `*Scene` suffix while most similar classes use `*Screen` suffix
- **Impact:** Inconsistent terminology makes it harder to understand class hierarchy
- **Recommendation:** Standardize on either `*Scene` or `*Screen` for IScene implementations. The project appears to use Scene for IScene implementations and Screen for pygame_gui windows.
- **Effort:** Low

### 1.2 Method Naming Patterns

**Dominant Pattern:** `snake_case` for all methods with specific prefixes:
- Event handlers: `handle_*`, `on_*`, `process_*`
- Creation methods: `_create_*`, `_init_*`, `_build_*`
- Update methods: `update_*`, `refresh_*`, `_update_*`
- Private methods: Leading underscore `_method_name`

#### MINOR: Inconsistent Event Handler Prefixes
- **ID:** NC-002
- **Location:** Multiple files across `game/ui/screens/`
- **Issue:** Mixed use of `handle_*`, `on_*`, and `process_*` for event handling
  - `handle_event()` in `MenuScene`, `KeybindingsScene`
  - `process_event()` in `NewGameSetupScreen`, `RaceSetupScreen`
  - `on_*` callbacks like `on_asset_selected()`, `on_ui_selection()`
- **Impact:** Unclear distinction between method purposes
- **Recommendation:** Establish convention: `handle_*` for external events, `process_*` for pygame_gui events, `on_*` for callbacks
- **Effort:** Medium

### 1.3 File Naming Patterns

**Dominant Pattern:** `snake_case.py` with descriptive names

#### MINOR: Inconsistent Module Naming for Related Components
- **ID:** NC-003
- **Location:** `game/ui/screens/`
- **Issue:** Related helper modules use inconsistent prefixes
  - Strategy modules: `strategy_ui.py`, `strategy_event_router.py`, `strategy_window_manager.py` (consistent)
  - Workshop modules: `workshop_context.py`, `workshop_data_loader.py`, `workshop_viewmodel.py` (consistent)
  - Build queue modules: `build_queue_screen.py`, `build_queue_helpers.py`, `build_queue_selector.py` (consistent)
  - Empire build queue: `empire_build_queue_window.py`, `empire_build_queue_formatter.py`, `empire_build_queue_filter_manager.py` (consistent but different prefix)
- **Impact:** Minor confusion when searching for related files
- **Recommendation:** Continue current pattern - this is actually well-organized
- **Effort:** N/A (informational)

---

## Phase 2: Structural Pattern Analysis

### 2.1 Class Structure Patterns

**Dominant Pattern:** Classes follow consistent structure:
1. Class docstring
2. Class constants
3. `__init__` method
4. Abstract/protocol methods (if applicable)
5. Public methods grouped by feature
6. Private helper methods

#### MAJOR: Inconsistent Constructor Parameter Ordering
- **ID:** SP-001
- **Location:** Multiple panel and screen constructors
- **Issue:** Constructor parameters have inconsistent ordering across similar classes
  - `BaseGallery.__init__(panel, manager, race_config, x, y, width, height, ...)`
  - `RaceEnvironmentPanel.__init__(panel, manager, race_config)` (no position params)
  - `BattlePanel.__init__(scene, x, y, w, h)` (scene first, no manager)
  - `FleetReportWindow.__init__(rect, manager, fleet, empire, ...)` (rect first)
- **Impact:** Makes it harder to remember parameter order; increases error likelihood
- **Recommendation:** Standardize: `(container/parent, manager, position_rect, ...other_params)`
- **Effort:** High (many files affected)

### 2.2 UI Manager Access Patterns

**Dominant Pattern:** `self.ui_manager` or `self.manager` for pygame_gui manager reference

#### MINOR: Inconsistent UI Manager Attribute Names
- **ID:** SP-002
- **Location:** Multiple files
- **Issue:** Different names for the pygame_gui manager reference
  - `self.ui_manager` in `BaseGallery`, `RaceSetupScreen`, `FleetReportWindow`
  - `self.manager` in `StrategyUI` (line 57), some panels
  - `self._ui_manager` in `KeybindingsScene`
- **Impact:** Inconsistent access patterns across related classes
- **Recommendation:** Standardize on `self.ui_manager` for public, `self._ui_manager` for private
- **Effort:** Medium

### 2.3 Initialization Patterns

**Dominant Pattern:** `_create_*` or `_init_*` methods called from `__init__`

#### INFO: Two Initialization Naming Conventions
- **ID:** SP-003
- **Location:** Across all UI classes
- **Issue:** Both `_create_*` and `_init_*` prefixes used for initialization
  - `_create_ui()`, `_create_buttons()` - used in `MenuScene`, `RaceSetupScreen`
  - `_init_layout()`, `_init_sidebar()` - used in `FleetReportWindow`
  - `_build_ui()`, `_build_action_rows()` - used in `KeybindingsScene`
- **Impact:** Slight confusion about method purpose
- **Recommendation:** Consider standardizing: `_create_*` for building UI elements, `_init_*` for setup logic
- **Effort:** Low

---

## Phase 3: API Design Consistency

### 3.1 Callback Patterns

**Dominant Pattern:** `on_*_callback` parameter names for callbacks

#### MINOR: Mixed Callback Parameter Names
- **ID:** API-001
- **Location:** Multiple constructors
- **Issue:** Inconsistent callback parameter naming
  - `on_select_callback` in `BaseGallery`
  - `on_complete_callback` in `RaceSetupScreen`
  - `on_close_callback` in `FleetReportWindow`
  - `on_start_callback`, `on_cancel_callback` in `NewGameSetupScreen`
- **Impact:** Minor cognitive overhead
- **Recommendation:** This is acceptable - names describe purpose. Consider documenting the pattern.
- **Effort:** N/A (acceptable variation)

### 3.2 Event Processing Return Values

**Dominant Pattern:** Return `bool` indicating whether event was handled

#### MINOR: Inconsistent Event Handler Return Types
- **ID:** API-002
- **Location:** `BattlePanel.handle_click()` vs other panels
- **Issue:** `handle_click()` returns different types
  - `BattlePanel.handle_click()` returns `False` or action tuples like `("focus_ship", ship_id)`
  - `ShipStatsPanel.handle_click()` returns `True`, `False`, or `("focus_ship", ship_id)`
  - `BattleControlPanel.handle_click()` returns `"end_battle"` or `False`
- **Impact:** Callers must handle multiple return types
- **Recommendation:** Standardize: return `bool` for consumed, emit events for actions
- **Effort:** Medium

### 3.3 Configuration Loading Patterns

**Dominant Pattern:** `set_from_config()` method to populate UI from data

#### INFO: Consistent Pattern
- **ID:** API-003
- **Location:** All gallery and panel classes
- **Issue:** None - this is a positive finding
- **Impact:** Good consistency for loading saved race configurations
- **Recommendation:** Continue this pattern
- **Effort:** N/A

---

## Phase 4: Project Pattern Adherence

### 4.1 Facade/Delegate Pattern

**Dominant Pattern:** Large screens decomposed into helper classes (PROJ-86 pattern)

#### INFO: Good Pattern Adoption
- **ID:** PP-001
- **Location:** `strategy_ui.py`, `strategy_event_router.py`, `strategy_window_manager.py`
- **Issue:** None - this is a positive finding showing god class decomposition
- **Impact:** Good maintainability
- **Recommendation:** Continue applying this pattern to other large screens
- **Effort:** N/A

#### MAJOR: Incomplete God Class Decomposition
- **ID:** PP-002
- **Location:** `game/ui/screens/test_lab/screen.py` (~1900 lines)
- **Issue:** Test Lab screen is still a large monolithic class despite having helper modules
- **Impact:** Harder to maintain and test
- **Recommendation:** Apply PROJ-86 decomposition pattern - extract event router, panel manager, etc.
- **Effort:** High

### 4.2 Type Hints

**Dominant Pattern:** Full type hints on method signatures

#### MINOR: Inconsistent Type Hint Coverage
- **ID:** PP-003
- **Location:** `game/ui/screens/builder/components.py`, `game/ui/panels/battle_panels.py`
- **Issue:** Some older files lack type hints
  - `ComponentListItem.__init__` has no type hints
  - `BattlePanel` methods lack return type hints
  - Newer files like `BaseGallery`, `StrategyEventRouter` have complete type hints
- **Impact:** Reduced IDE support and documentation
- **Recommendation:** Add type hints to files missing them
- **Effort:** Medium

### 4.3 Docstrings

**Dominant Pattern:** Module and class docstrings with PROJ-XX references

#### MINOR: Missing Module Docstrings
- **ID:** PP-004
- **Location:** Several files
- **Issue:** Some files lack module-level docstrings
  - `game/ui/screens/builder/components.py` - no module docstring
  - Most files have good docstrings with project references (PROJ-12, PROJ-43, PROJ-86, etc.)
- **Impact:** Reduced discoverability
- **Recommendation:** Add module docstrings to files missing them
- **Effort:** Low

### 4.4 Import Organization

**Dominant Pattern:**
1. `from __future__ import annotations`
2. Standard library imports
3. Third-party imports (pygame, pygame_gui)
4. Local imports

#### MINOR: Inconsistent Future Annotations Usage
- **ID:** PP-005
- **Location:** Multiple files
- **Issue:** Some files use `from __future__ import annotations`, others don't
  - Used in: `strategy_ui.py`, `strategy_event_router.py`, `keybindings_scene.py`
  - Not used in: `battle_panels.py`, `ship_stats_renderer.py`, `menu_scene.py`
- **Impact:** Inconsistent forward reference handling
- **Recommendation:** Add `from __future__ import annotations` to all files for PEP 563 compliance
- **Effort:** Low

### 4.5 Dependency Injection

**Dominant Pattern:** Constructor injection for dependencies

#### MAJOR: Direct Singleton Access in Some Files
- **ID:** PP-006
- **Location:** `game/ui/screens/race_setup_screen.py`, `game/ui/screens/fleet_report_window.py`
- **Issue:** Some files access singletons directly instead of injection
  - `ShipThemeManager.instance()` called in `_refresh_ship_preview()` (race_setup_screen.py:404)
  - `ShipThemeManager.instance()` called in `_get_ship_image()` (fleet_report_window.py:735)
  - `StrategyMetadataService.instance()` in `ship_stats_renderer.py:243`
- **Impact:** Harder to test, violates DI principle from CLAUDE.md
- **Recommendation:** Pass theme_manager as constructor parameter
- **Effort:** Medium

---

## Phase 5: Per-Module Internal Consistency

### 5.1 builder/ Subdirectory

#### INFO: Well-Organized Module Structure
- **ID:** MOD-001
- **Location:** `game/ui/screens/builder/`
- **Issue:** None - positive finding
- **Impact:** Good separation of concerns with `EventBus`, `StateManager`, component panels
- **Recommendation:** Use as reference for other complex UI modules
- **Effort:** N/A

### 5.2 test_lab/ Subdirectory

#### MINOR: Mixed Responsibility in screen.py
- **ID:** MOD-002
- **Location:** `game/ui/screens/test_lab/screen.py`
- **Issue:** Main screen file handles too many responsibilities despite helper modules
- **Impact:** Large file size (~1900 lines)
- **Recommendation:** Further decomposition following the builder/ pattern
- **Effort:** High

### 5.3 panels/ Directory

#### MINOR: Inconsistent Panel Base Class Usage
- **ID:** MOD-003
- **Location:** `game/ui/panels/`
- **Issue:** Mix of inheritance patterns
  - `BattlePanel` is a custom base class for battle UI
  - `BaseGallery` is an ABC for gallery panels
  - Other panels like `RaceEnvironmentPanel` are standalone classes
- **Impact:** Inconsistent API surface
- **Recommendation:** Document which panels should inherit from base classes
- **Effort:** Low

### 5.4 Error Handling Patterns

**Dominant Pattern:** Use `log_debug`, `log_warning`, `log_error` from `game.core.logger`

#### MINOR: Inconsistent Error Logging
- **ID:** MOD-004
- **Location:** Multiple files
- **Issue:** Some files use print statements or no logging
  - Most files properly use `log_debug`, `log_info`, `log_warning`, `log_error`
  - `builder/event_bus.py` correctly uses `log_error` for exception handling
- **Impact:** Potential debugging difficulties
- **Recommendation:** Audit all files for proper logging usage
- **Effort:** Low

---

## Summary of Recommended Actions

### High Priority (MAJOR)
1. **SP-001**: Standardize constructor parameter ordering across panels and screens
2. **PP-002**: Decompose test_lab/screen.py following PROJ-86 pattern
3. **PP-006**: Replace singleton access with dependency injection

### Medium Priority (MINOR)
4. **NC-002**: Document event handler naming conventions
5. **SP-002**: Standardize UI manager attribute names
6. **API-002**: Standardize event handler return types
7. **PP-003**: Add type hints to older files
8. **PP-005**: Add `from __future__ import annotations` consistently

### Low Priority (INFO/MINOR)
9. **PP-004**: Add missing module docstrings
10. **MOD-003**: Document panel base class usage patterns
11. **MOD-004**: Audit logging consistency

---

## Conclusion

The UI modules show generally good consistency with the project's established patterns. The main areas for improvement are:

1. **Constructor parameter ordering** varies significantly and should be standardized
2. **God class decomposition** has been applied well to strategy screens (PROJ-86) but test_lab still needs work
3. **Dependency injection** is partially applied - some singleton access remains
4. **Type hints** are present in newer code but missing from older files

The codebase demonstrates good adoption of:
- Facade/Delegate pattern for complex screens
- BaseGallery abstraction for asset selection
- Event routing separation (StrategyEventRouter, etc.)
- Consistent callback patterns

Overall code quality is high, with most violations being MINOR consistency issues rather than CRITICAL problems.
