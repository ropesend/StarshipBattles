# Consistency Violations Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 126 files (101 in screens/, 25 in panels/)
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 6 | **Minor:** 9 | **Info:** 2

## Findings

#### CRITICAL: Inconsistent Return Types for Not-Found Cases
**ID:** CON-UI1-001
**Location:** Multiple files in `game/ui/panels/` and `game/ui/screens/`
**Issue:** Methods for finding/getting items return inconsistent types when items are not found. Some return `None` (e.g., `get_hovered_component` in `left_panel.py:460`), others return `-1` (e.g., `get_clicked_planet_index` in `planet_list_renderer.py:182`), and some raise exceptions. This creates ambiguity in calling code about how to check for "not found" cases.
**Impact:** Potential runtime errors if callers use wrong pattern (`if result:` vs `if result is not None` vs `if result >= 0`). Risk of bugs when integrating code.
**Recommendation:** Standardize on returning `None` for "not found" cases in methods returning objects, or use `Optional[int]` and return `None` for index-based methods. Document the convention.
**Effort:** Medium

---

#### MAJOR: Mixed Class Naming Suffixes for Similar Components
**ID:** CON-UI1-002
**Location:** `game/ui/screens/` directory
**Issue:** Similar UI components use inconsistent naming suffixes:
- `UIWindow` subclasses: `FleetReportWindow`, `EmpireBuildQueueWindow`, `EventLogWindow`, `SaveSelectionWindow`
- Non-UIWindow classes named "Window": `StrategyWindowManager` (not a window, it's a manager)
- Scene classes: `MenuScene`, `KeybindingsScene` vs `BattleScreen`, `StrategyScreen`
- Dialog classes: `TransferDialog`, `CargoQuickDialog`, `RaceBrowserDialog` (all inherit from UIWindow but named "Dialog")
- Setup classes: `RaceSetupScreen`, `NewGameSetupScreen` (inherit from UIWindow but named "Screen")
**Impact:** Cognitive overhead; unclear from class name whether it inherits UIWindow. Hard to understand hierarchy.
**Recommendation:** Establish convention: UIWindow subclasses = "Window", non-pygame_gui scenes = "Scene", modal overlays inheriting UIWindow = "Dialog". Rename `RaceSetupScreen` -> `RaceSetupWindow`, `NewGameSetupScreen` -> `NewGameSetupWindow`.
**Effort:** Complex (rename refactor)

---

#### MAJOR: Inconsistent Method Prefixes for List Operations
**ID:** CON-UI1-003
**Location:** Multiple files
**Issue:** List refresh/rebuild operations use inconsistent method naming:
- `refresh_list()` in `planet_list_window.py:154`, `fleet_report_window.py:768`
- `_refresh_list()` in `empire_build_queue_window.py:201`
- `rebuild_list()` in `fleet_orders_window.py:76`
- `_rebuild_list()` in `event_log_window.py:194`
- `_rebuild_design_list()` in `design_selector_window.py:281`
- `_refresh_designs()` in `design_selector_window.py:230`
- `_refresh_items_list()` in `build_queue_screen.py:571`
**Impact:** Inconsistent API design; hard to predict method names when navigating codebase.
**Recommendation:** Standardize: `refresh_list()` for public full-refresh, `_rebuild_list()` for private UI rebuilding. "refresh" implies data+UI update; "rebuild" implies UI-only reconstruction.
**Effort:** Medium

---

#### MAJOR: Type Hints Missing on Many Methods in panels/
**ID:** CON-UI1-004
**Location:** `game/ui/panels/battle_panels.py`, `game/ui/panels/system_tree_panel.py`, `game/ui/panels/strategy_widgets.py`
**Issue:** While most newer files use type hints consistently (e.g., `empire_treasury_panel.py`, `ship_detail_panel.py`), older panel files have methods without type hints:
- `battle_panels.py`: `draw(self, screen)`, `handle_click(self, mx, my)`, `_get_ships(self)` - no return type hints
- `system_tree_panel.py`: `add_child(self, item)`, `set_expanded(self, expanded)` - no parameter/return hints
- `strategy_widgets.py`: `clear(self)`, `render(self, star, vertical=False)` - no hints at all
**Impact:** Reduced IDE support, harder to understand expected types, potential type errors at runtime.
**Recommendation:** Add type hints to all public methods per project convention. Parameter types and return types required for all `def` statements.
**Effort:** Medium

---

#### MAJOR: Inconsistent Event Handler Naming
**ID:** CON-UI1-005
**Location:** Multiple files in screens/ and panels/
**Issue:** Event handler methods use three different naming patterns:
1. `handle_*` prefix: `handle_click()`, `handle_event()`, `handle_resize()`, `handle_row_click()`
2. `_handle_*` private prefix: `_handle_keydown()`, `_handle_column_toggle_click()`, `_handle_filter_toggle_click()`
3. `on_*` prefix: `on_click()`, `on_asset_selected()`, `on_theme_selected()`
Mixed in same files:
- `fleet_orders_window.py`: `_handle_keydown()`, `handle_global_event()`
- `ship_detail_panel.py`: `process_event()` only, delegates to nothing
- `race_identity_panel.py`: `handle_event()`, `_set_dropdown_value()`
**Impact:** Inconsistent mental model; unclear which pattern to use for new handlers.
**Recommendation:** Standardize: `handle_*` for public event routing methods, `_handle_*` for internal event processing, `on_*` for callbacks fired to external listeners.
**Effort:** Complex

---

#### MAJOR: Docstring Format Inconsistency
**ID:** CON-UI1-006
**Location:** Throughout screens/ and panels/
**Issue:** Three different docstring styles are used:
1. Google-style with Args/Returns sections (e.g., `empire_build_queue_window.py`, `build_queue_controller.py`)
2. Simple one-line docstrings without param docs (e.g., `battle_panels.py`, `planet_list_window.py`)
3. reST-style with :param: notation (rare but present)
Some classes have comprehensive docstrings while sister classes have none:
- `EmpireBuildQueueWindow`: Full docstring with Args
- `PlanetListWindow`: No class docstring at all
**Impact:** Inconsistent documentation; unclear expectations for new code.
**Recommendation:** Adopt Google-style docstrings project-wide. All public classes and methods should have docstrings with Args/Returns sections.
**Effort:** Complex

---

#### MAJOR: Inconsistent Import Organization
**ID:** CON-UI1-007
**Location:** Throughout screens/ and panels/
**Issue:** Import organization varies significantly:
1. Some files use `from __future__ import annotations` (e.g., `transfer_dialog.py`, `cargo_quick_dialog.py`)
2. Others don't (e.g., `planet_list_window.py`, `battle_panels.py`)
3. `TYPE_CHECKING` block usage is inconsistent - some files import types in TYPE_CHECKING block, others import directly
4. Import grouping varies: some separate pygame imports from game imports, others mix them
5. `pygame_gui.elements` imports vary: some use `from pygame_gui.elements import UIWindow, UIPanel, ...`, others use `import pygame_gui` then `pygame_gui.elements.UIWindow`
**Impact:** Code style inconsistency; harder to maintain consistent patterns.
**Recommendation:** All files should use `from __future__ import annotations`. Group imports: stdlib, third-party (pygame, pygame_gui), then local (game.*). Use TYPE_CHECKING for type-hint-only imports.
**Effort:** Medium

---

#### MINOR: Inconsistent Private Member Naming
**ID:** CON-UI1-008
**Location:** Multiple files in panels/
**Issue:** Private member naming is inconsistent:
- Some use underscore prefix: `self._scroll_container`, `self._elements`, `self._stats_panel`
- Others don't prefix private members: `self.panel`, `self.ui_manager`, `self.snapshot`
Within same class (e.g., `EmpireTreasuryPanel`): `self.panel` (public) vs `self._scroll_container` (private)
**Impact:** Unclear which members are part of public API vs internal implementation.
**Recommendation:** Prefix all internal/private instance variables with `_`. Only use non-prefixed names for intentionally public attributes.
**Effort:** Simple

---

#### MINOR: Boolean Parameter Naming Inconsistency
**ID:** CON-UI1-009
**Location:** `game/ui/screens/planet_list_filters.py`, `game/ui/panels/system_tree_panel.py`
**Issue:** Boolean parameters don't consistently use is_/has_/should_ prefixes:
- `flat_view` instead of `use_flat_view` or `is_flat_view` (`system_tree_panel.py:135`)
- `vertical` instead of `is_vertical` (`strategy_widgets.py:31`)
- `show_obsolete` is correct pattern (`design_selector_window.py:63`)
- `show_complexes` is correct pattern (`planet_list_window.py:457`)
**Impact:** Minor readability issue; inconsistent API feel.
**Recommendation:** Boolean parameters should use is_/has_/can_/should_ prefix when it improves clarity. At minimum, document which pattern is preferred.
**Effort:** Simple

---

#### MINOR: Magic Numbers in Layout Code
**ID:** CON-UI1-010
**Location:** Multiple files
**Issue:** While `UIConfig` constants exist and are used in many places, some files still use inline magic numbers:
- `event_log_window.py:18-22`: `HEADER_HEIGHT = 50`, `ROW_HEIGHT = 28` defined locally instead of using UIConfig
- `empire_treasury_panel.py:22-28`: Local constants like `ROW_HEIGHT = 28`, `SECTION_GAP = 15`
- `fleet_orders_window.py:88`: `row_height = UIConfig.ROW_HEIGHT_STANDARD` (correct)
- `planet_list_window.py:37-38`: Uses `UIConfig.ROW_HEIGHT_LARGE` (correct)
Inconsistent use of centralized config vs local constants.
**Impact:** Harder to maintain consistent UI appearance; potential drift in layout values.
**Recommendation:** Move all shared layout constants to `UIConfig`. Local constants are acceptable only for truly module-specific values.
**Effort:** Simple

---

#### MINOR: Inconsistent kill()/cleanup Method Patterns
**ID:** CON-UI1-011
**Location:** Multiple Window/Panel classes
**Issue:** Cleanup patterns vary:
- Some use `kill()` that calls `super().kill()` last (correct for UIWindow)
- Some use `kill()` that clears references first
- Some don't have explicit cleanup methods at all
- `planet_list_window.py`: Has `kill()` with callback invocation
- `empire_build_queue_window.py`: Has `kill()` with element cleanup + callback
- `battle_panels.py`: No kill method (uses pygame surfaces, not pygame_gui elements)
**Impact:** Potential memory leaks or cleanup bugs if pattern is wrong.
**Recommendation:** Standard pattern: clear child elements, clear references, invoke callback, then `super().kill()`.
**Effort:** Simple

---

#### MINOR: Inconsistent Column Configuration Patterns
**ID:** CON-UI1-012
**Location:** `planet_list_window.py`, `empire_build_queue_window.py`, `fleet_report_window.py`
**Issue:** Column definitions use slightly different dict structures:
- `planet_list_window.py:73-84`: Uses `attr`, `func`, `fmt`, `visible`, `type`
- `empire_build_queue_window.py` (via filter_manager): Uses `id`, `title`, `width`, `visible`
- `column_manager.py:141`: Expects specific column dict structure
**Impact:** Multiple column configuration patterns create confusion; harder to share column-related utilities.
**Recommendation:** Create a `ColumnDefinition` dataclass with standard fields. All windows should use this.
**Effort:** Medium

---

#### MINOR: Inconsistent Scroll Bar Handling
**ID:** CON-UI1-013
**Location:** `planet_list_window.py`, `empire_build_queue_window.py`, `event_log_window.py`
**Issue:** Mouse wheel scrolling is implemented slightly differently in each window:
- Same basic pattern but with copy-pasted code
- Some calculate `row_percent`, others hardcode scroll amounts
- Variable names vary: `total_h`, `total_height`, `content_height`
**Impact:** Code duplication; potential for divergent behavior.
**Recommendation:** Extract scroll wheel handling to a shared utility function or base class method.
**Effort:** Simple

---

#### MINOR: Inconsistent Callback Naming
**ID:** CON-UI1-014
**Location:** Various Window/Dialog classes
**Issue:** Callback parameters use different naming:
- `on_close_callback` (most common, e.g., `EmpireBuildQueueWindow`)
- `on_load_callback`, `on_cancel_callback` (`SaveSelectionWindow`)
- `on_select_callback` (`DesignSelectorWindow`)
- `callback` (too generic)
- `on_navigate_to_hex` (action-specific)
**Impact:** Minor inconsistency; callbacks are easily understood but naming varies.
**Recommendation:** Use `on_<action>_callback` pattern consistently. Or drop `_callback` suffix since `on_` prefix already implies callback.
**Effort:** Simple

---

#### MINOR: Empty __init__.py Files
**ID:** CON-UI1-015
**Location:** `game/ui/screens/__init__.py`, `game/ui/panels/__init__.py`
**Issue:** Both `__init__.py` files are empty (1 line each). Neither exports any public API, requiring all imports to use full module paths.
**Impact:** Verbose import statements; no clear "public API" definition for these packages.
**Recommendation:** Either keep empty (current state is acceptable) or add `__all__` with key exports. Consistency with rest of codebase is most important.
**Effort:** Simple

---

#### MINOR: Inconsistent Use of Type Aliases
**ID:** CON-UI1-016
**Location:** `empire_build_queue_window.py`, `build_queue_controller.py`
**Issue:** Some files use `Any` for pygame_gui manager type while others properly type it:
- `empire_build_queue_window.py:94`: `manager: Any`
- `design_selector_window.py:33`: `manager: pygame_gui.UIManager`
- `event_log_window.py:49`: `manager: Any`
**Impact:** Type checker cannot verify correct usage; inconsistent typing discipline.
**Recommendation:** Always use `pygame_gui.UIManager` type, not `Any`. If circular import issues, use TYPE_CHECKING block.
**Effort:** Simple

---

#### INFO: Logging Usage Variations
**ID:** CON-UI1-017
**Location:** `game/ui/screens/` (42 files with logging)
**Issue:** Logging import and usage is generally consistent (`log_debug`, `log_info`, `log_warning`, `log_error` from `game.core.logger`). Some files don't use logging at all (pure UI rendering), which is acceptable.
**Impact:** None - this is natural variation based on module purpose.
**Recommendation:** No action needed. Current pattern is acceptable.
**Effort:** N/A

---

#### INFO: Different Panel Creation Patterns
**ID:** CON-UI1-018
**Location:** `game/ui/panels/`
**Issue:** Two panel instantiation patterns exist:
1. Panels that create their own UIPanel container (e.g., `DesignReportPanel`, `ShipDetailPanel`)
2. Panels that take an existing UIPanel as parameter (e.g., `EmpireTreasuryPanel`, `RaceEnvironmentPanel`)
**Impact:** This is intentional design variation based on use case, not inconsistency.
**Recommendation:** Document which pattern to use when: standalone panels create their own container; embedded/tab panels receive parent container.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **CON-UI1-001 (CRITICAL)**: Inconsistent return types for not-found cases - potential runtime bugs when calling code uses wrong check pattern.

2. **CON-UI1-002 (MAJOR)**: Mixed class naming suffixes (Window/Screen/Dialog/Scene) - cognitive overhead and unclear inheritance relationships.

3. **CON-UI1-004 (MAJOR)**: Missing type hints on older panel files - reduces IDE support and type safety.

4. **CON-UI1-006 (MAJOR)**: Docstring format inconsistency - unclear documentation standards for new code.

5. **CON-UI1-007 (MAJOR)**: Inconsistent import organization - code style drift, harder to maintain consistency.
