# Consistency Violations Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 127 (102 in screens, 25 in panels)
- **Total Issues Found:** 23
- **Critical:** 0 | **Major:** 4 | **Minor:** 14 | **Info:** 5

---

## Findings

#### MAJOR: Inconsistent Constructor Parameter Ordering
**ID:** CON-UI1-001
**Location:** Multiple panel and screen constructors across `game/ui/screens/` and `game/ui/panels/`
**Issue:** Constructor parameters have inconsistent ordering across similar classes:
- `BaseGallery.__init__(panel, manager, race_config, x, y, width, height, ...)`
- `RaceEnvironmentPanel.__init__(panel, manager, race_config)` (no position params)
- `BattlePanel.__init__(scene, x, y, w, h)` (scene first, no manager)
- `FleetReportWindow.__init__(rect, manager, fleet, empire, ...)` (rect first)
**Impact:** Makes it harder to remember parameter order; increases error likelihood when creating new instances.
**Recommendation:** Standardize constructor order: `(container/parent, manager, position_rect, ...domain_params, ...optional_callbacks)`
**Effort:** Complex (many files affected, but can be done incrementally)

#### MAJOR: Incomplete God Class Decomposition (test_lab/screen.py)
**ID:** CON-UI1-002
**Location:** `game/ui/screens/test_lab/screen.py` (~1900 lines)
**Issue:** Test Lab screen is still a large monolithic class despite having helper modules. Contrast with strategy screen which successfully applied PROJ-86 decomposition pattern.
**Impact:** Harder to maintain and test; higher cognitive load when working in this module.
**Recommendation:** Apply PROJ-86 decomposition pattern - extract event router, panel manager, state manager as separate classes.
**Effort:** Complex

#### MAJOR: Direct Singleton Access Instead of Dependency Injection
**ID:** CON-UI1-003
**Location:**
- `game/ui/screens/race_setup_screen.py:404` - `ShipThemeManager.instance()`
- `game/ui/screens/fleet_report_window.py:735` - `ShipThemeManager.instance()`
- `game/ui/panels/ship_stats_renderer.py:243` - `StrategyMetadataService.instance()`
**Issue:** Some files access singletons directly instead of receiving dependencies through constructor injection, violating the DI principle from CLAUDE.md.
**Impact:** Harder to test in isolation; creates hidden dependencies; violates project conventions.
**Recommendation:** Pass `theme_manager` or service instances as constructor parameters. Already done correctly in newer code like `BuildQueueScreen`.
**Effort:** Medium

#### MAJOR: Mixed Event Handler Naming (handle_event vs process_event)
**ID:** CON-UI1-004
**Location:** Multiple files across game/ui/screens/ and game/ui/panels/
**Issue:** Two different method names are used for handling pygame events:
- `handle_event(self, event)` - Used in 37 files (IScene protocol implementations, custom panels)
- `process_event(self, event)` - Used in 17 files (pygame_gui UIWindow subclasses)
**Impact:** Cognitive overhead when working across files. However, this appears to be an intentional split based on class hierarchy.
**Recommendation:** Document this as intentional pattern: pygame_gui UIWindow subclasses use `process_event` (inherited API), while IScene implementations use `handle_event`. Add clarifying comments in base classes.
**Effort:** Simple (documentation only)

#### MINOR: Inconsistent Event Handler Return Type Annotations
**ID:** CON-UI1-005
**Location:**
- `game/ui/screens/battle_state_viewer.py:308` - `def handle_event(self, event) -> bool:`
- `game/ui/screens/battle_screen.py:303` - `def handle_event(self, event):` (no annotation)
- `game/ui/screens/formation_editor.py:527` - `def handle_event(self, event) -> None:`
**Issue:** The `handle_event` method has inconsistent return type patterns: some return `bool`, some return `None` implicitly, some have explicit type annotations.
**Impact:** Callers cannot rely on consistent return type; reduces static analysis effectiveness.
**Recommendation:** Establish convention: IScene `handle_event` returns `None`, panel/widget `handle_event` returns `bool` for event consumption. Add annotations to all implementations.
**Effort:** Medium

#### MINOR: Mixed Screen/Scene Class Naming Suffix
**ID:** CON-UI1-006
**Location:** `game/ui/screens/menu_scene.py`, `game/ui/screens/keybindings_scene.py`
**Issue:** Uses `*Scene` suffix while most similar classes use `*Screen` suffix (BattleScreen, StrategyScreen, etc.)
**Impact:** Inconsistent terminology makes class hierarchy less clear.
**Recommendation:** The pattern appears intentional: `*Scene` for IScene protocol implementations, `*Screen` for screen-specific implementations. Document this distinction.
**Effort:** Simple (documentation)

#### MINOR: Inconsistent UI Manager Attribute Names
**ID:** CON-UI1-007
**Location:** Multiple files
**Issue:** Different names for pygame_gui manager reference:
- `self.ui_manager` in `BaseGallery`, `RaceSetupScreen`, `FleetReportWindow`
- `self.manager` in `StrategyUI`, some panels
- `self._ui_manager` in `KeybindingsScene`
**Impact:** Inconsistent access patterns across related classes.
**Recommendation:** Standardize on `self.ui_manager` for public access, `self._ui_manager` for private. Update over time as files are touched.
**Effort:** Medium

#### MINOR: Inconsistent Type Hint Coverage
**ID:** CON-UI1-008
**Location:** `game/ui/screens/builder/components.py`, `game/ui/panels/battle_panels.py`
**Issue:** Some older files lack type hints while newer files have complete coverage.
- `ComponentListItem.__init__` has no type hints
- `BattlePanel` methods lack return type hints
- Newer files like `BaseGallery`, `StrategyEventRouter` have complete type hints
**Impact:** Reduced IDE support and static analysis in older files.
**Recommendation:** Add type hints to files missing them during maintenance work.
**Effort:** Medium

#### MINOR: Inconsistent Future Annotations Usage
**ID:** CON-UI1-009
**Location:** Multiple files
**Issue:** Some files use `from __future__ import annotations`, others don't:
- Used in: `strategy_ui.py`, `strategy_event_router.py`, `keybindings_scene.py`, `ship_detail_panel.py`
- Not used in: `battle_panels.py`, `ship_stats_renderer.py`, `menu_scene.py`
**Impact:** Inconsistent forward reference handling; affects type annotation parsing.
**Recommendation:** Add `from __future__ import annotations` to all files for PEP 563 compliance.
**Effort:** Simple

#### MINOR: Inconsistent Event Handler Return Values
**ID:** CON-UI1-010
**Location:** `BattlePanel.handle_click()`, `ShipStatsPanel.handle_click()`, `BattleControlPanel.handle_click()`
**Issue:** `handle_click()` returns different types:
- `BattlePanel.handle_click()` returns `False` or action tuples like `("focus_ship", ship_id)`
- `ShipStatsPanel.handle_click()` returns `True`, `False`, or `("focus_ship", ship_id)`
- `BattleControlPanel.handle_click()` returns `"end_battle"` or `False`
**Impact:** Callers must handle multiple return types; defensive coding required.
**Recommendation:** Standardize: return `bool` for consumed, emit events via callback for actions.
**Effort:** Medium

#### MINOR: Two Initialization Method Naming Conventions
**ID:** CON-UI1-011
**Location:** Across UI classes
**Issue:** Both `_create_*` and `_init_*` prefixes used for initialization helpers:
- `_create_ui()`, `_create_buttons()` in `MenuScene`, `RaceSetupScreen`
- `_init_layout()`, `_init_sidebar()` in `FleetReportWindow`
- `_build_ui()`, `_build_action_rows()` in `KeybindingsScene`
**Impact:** Slight confusion about method purpose.
**Recommendation:** Standardize: `_create_*` for building UI elements, `_init_*` for setup logic, `_build_*` for section construction.
**Effort:** Simple

#### MINOR: Missing Module Docstrings
**ID:** CON-UI1-012
**Location:** `game/ui/screens/builder/components.py`, several other files
**Issue:** Some files lack module-level docstrings. Most files have good docstrings with project references (PROJ-12, PROJ-43, PROJ-86, etc.)
**Impact:** Reduced discoverability and context.
**Recommendation:** Add module docstrings to files missing them.
**Effort:** Simple

#### MINOR: Inconsistent Panel Base Class Usage
**ID:** CON-UI1-013
**Location:** `game/ui/panels/`
**Issue:** Mix of inheritance patterns:
- `BattlePanel` is a custom base class for battle UI
- `BaseGallery` is an ABC for gallery panels
- Other panels like `RaceEnvironmentPanel` are standalone classes
**Impact:** Inconsistent API surface across panels.
**Recommendation:** Document which panels should inherit from base classes and when.
**Effort:** Simple (documentation)

#### MINOR: Mixed Responsibility in test_lab Subdirectory
**ID:** CON-UI1-014
**Location:** `game/ui/screens/test_lab/screen.py`
**Issue:** Main screen file handles too many responsibilities despite having helper modules. Related to CON-UI1-002.
**Impact:** Large file size (~1900 lines), harder to navigate.
**Recommendation:** Further decomposition following the builder/ pattern which is well-organized.
**Effort:** Complex

#### INFO: Good Pattern Adoption - Facade/Delegate Pattern
**ID:** CON-UI1-015
**Location:** `strategy_ui.py`, `strategy_event_router.py`, `strategy_window_manager.py`
**Issue:** None - this is a positive finding showing successful god class decomposition (PROJ-86 pattern).
**Impact:** Good maintainability achieved for strategy module.
**Recommendation:** Continue applying this pattern to other large screens (test_lab, workshop).
**Effort:** N/A

#### INFO: Consistent Callback Naming Pattern
**ID:** CON-UI1-016
**Location:** All panel and screen constructors
**Issue:** None - callback parameter naming is consistent: `on_*_callback` pattern used throughout.
- `on_select_callback` in `BaseGallery`
- `on_close_callback` in `FleetReportWindow`
- `on_complete_callback` in `RaceSetupScreen`
**Impact:** Good consistency.
**Recommendation:** Maintain current convention.
**Effort:** N/A

#### INFO: Good Class Naming Suffix Consistency
**ID:** CON-UI1-017
**Location:** All UI files
**Issue:** None - class naming suffixes are highly consistent:
- Screens: `*Screen` (BattleScreen, StrategyScreen)
- Windows: `*Window` (FleetReportWindow, EmpireBuildQueueWindow)
- Panels: `*Panel` (ShipDetailPanel, PlanetReportPanel)
- Renderers: `*Renderer` (StrategyRenderer)
- Handlers: `*Handler` (StrategyInputHandler)
**Impact:** Good discoverability and organization.
**Recommendation:** Maintain current convention.
**Effort:** N/A

#### INFO: Well-Organized builder/ Module Structure
**ID:** CON-UI1-018
**Location:** `game/ui/screens/builder/`
**Issue:** None - positive finding. Good separation with `EventBus`, `StateManager`, component panels.
**Impact:** Good maintainability.
**Recommendation:** Use as reference for other complex UI modules.
**Effort:** N/A

#### INFO: Consistent Logging Pattern
**ID:** CON-UI1-019
**Location:** 53 files across screens/ and panels/
**Issue:** None - logging uses centralized `log_debug`, `log_info`, `log_warning`, `log_error` from `game.core.logger` consistently.
**Impact:** Good debugging capability.
**Recommendation:** Maintain current convention.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **CON-UI1-003: Direct Singleton Access** - Violates DI principle from CLAUDE.md. Medium effort to fix by passing dependencies through constructors. Should be addressed during normal maintenance.

2. **CON-UI1-001: Inconsistent Constructor Parameter Ordering** - High cognitive overhead when creating instances. Complex effort but can be done incrementally. Consider establishing a documented standard.

3. **CON-UI1-002: Incomplete God Class Decomposition (test_lab)** - 1900-line file is hard to maintain. Complex effort but would significantly improve maintainability. Apply PROJ-86 pattern.

4. **CON-UI1-004: Mixed Event Handler Naming** - Document the intentional split between `handle_event` (IScene) and `process_event` (UIWindow) to clarify for future developers.

5. **CON-UI1-005: Inconsistent Return Type Annotations** - Add type annotations to `handle_event` methods across all implementations for better static analysis.

---

## Positive Patterns Observed

- **Class naming suffixes** are highly consistent (Panel, Screen, Window, Handler, Renderer)
- **Callback parameter naming** consistently uses `on_*_callback` pattern
- **Logging** uses centralized log_* functions from game.core.logger
- **Facade/Delegate pattern** successfully applied to strategy module (PROJ-86)
- **BaseGallery abstraction** provides good reuse for asset selection galleries
- **Event routing separation** well-implemented in strategy screens
- **Boolean naming** consistently uses is_/has_/can_/show_ prefixes
- **Method verb prefixes** are consistent (get_, load_, _handle_, _update_)

---

## Conclusion

The UI modules show generally good consistency with the project's established patterns. The main areas for improvement are:

1. **Dependency Injection** - Some singleton access violates project DI conventions
2. **Constructor parameter ordering** - Varies significantly and should be standardized
3. **God class decomposition** - Applied well to strategy screens but test_lab still needs work
4. **Type hints** - Present in newer code but missing from older files

The codebase demonstrates excellent adoption of:
- Facade/Delegate pattern for complex screens
- BaseGallery abstraction for asset selection
- Event routing separation
- Consistent callback and naming patterns

Overall code quality is high, with most violations being MINOR consistency issues rather than CRITICAL problems. The identified MAJOR issues are well-scoped and can be addressed incrementally during normal maintenance work.
