# Consistency Violations Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 134 (109 in game/ui/screens/, 25 in game/ui/panels/)
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 7 | **Minor:** 7 | **Info:** 2

## Findings

---

#### CRITICAL: Duplicate Class Name `ModifierEditorPanel` in Two Modules
**ID:** CON-UI1-001
**Location:** `game/ui/panels/builder_widgets.py:21` and `game/ui/screens/builder/modifier_editor.py:20`
**Issue:** Two completely different classes share the identical name `ModifierEditorPanel`. The one in `panels/builder_widgets.py` uses dependency injection (`registries` kwarg, per PROJ-50) while the one in `screens/builder/modifier_editor.py` is labeled "legacy" and uses `component_service=None` with a fallback pattern. `workshop_screen.py` imports from `panels/builder_widgets.py` (line 13) while `builder/main.py` imports from `screens/builder/modifier_editor.py` (line 45). A developer looking up `ModifierEditorPanel` will find conflicting implementations with no clear indication of which is canonical.
**Impact:** High confusion risk. A developer refactoring or debugging modifier editing could work on the wrong class entirely. Import autocomplete may suggest the wrong one. Violates the project's "eradicate old systems completely" migration policy.
**Recommendation:** Rename or delete the legacy `screens/builder/modifier_editor.py` version. If it must exist, rename it to `LegacyModifierEditorPanel` and add a deprecation notice. The `panels/builder_widgets.py` version is canonical (uses DI per PROJ-50).
**Effort:** Medium

---

#### CRITICAL: Duplicate Class Name `ColumnManager` in Two Modules
**ID:** CON-UI1-002
**Location:** `game/ui/screens/column_manager.py:49` and `game/ui/screens/planet_list_columns.py:11`
**Issue:** Two completely different classes share the name `ColumnManager`. The one in `column_manager.py` manages fleet report columns (with `ShipInstance`-specific value extraction and `DEFAULT_FLEET_COLUMNS`). The one in `planet_list_columns.py` manages planet list columns (with sort state, header UI buttons, and `header_container`). They have overlapping method names (`get_visible_columns`) but fundamentally different interfaces and responsibilities.
**Impact:** Namespace collision. Importing both in a single module requires aliasing. Searching the codebase for `ColumnManager` yields ambiguous results. A developer unfamiliar with the codebase cannot tell which `ColumnManager` is which without reading the file.
**Recommendation:** Rename to `FleetColumnManager` (in `column_manager.py`) and `PlanetColumnManager` (in `planet_list_columns.py`) to reflect their specific domains. Alternatively, rename the files: `fleet_column_manager.py` and `planet_list_column_manager.py`.
**Effort:** Medium

---

#### MAJOR: Mixed Event Handling Method Names (`handle_event` vs `process_event`)
**ID:** CON-UI1-003
**Location:** 34 files using `handle_event`, 16 files using `process_event` across screens/ and panels/
**Issue:** Two competing naming conventions for the primary event dispatch method. Custom screen classes (implementing `IScene` protocol) use `handle_event` (e.g., `BattleScreen`, `StrategyScreen`, `SetupScreen`, `FormationEditorScreen`, all builder sub-panels, all test_lab components). UIWindow subclasses use `process_event` (e.g., `DesignSelectorWindow`, `EmpireBuildQueueWindow`, `FleetReportWindow`, `PlanetListWindow`, `SaveSelectionWindow`, `RaceBrowserDialog`). However, some panels in `game/ui/panels/` use `handle_event` (e.g., `ModifierImpactGrid`, `RaceIdentityPanel`, `ComponentModifierGridPanel`, `BuilderWidgets`) while others use `process_event` (e.g., `SystemTreePanel`, `ShipDetailPanel`).
**Impact:** Cannot predict which method name to call without checking the class. Cognitive overhead when navigating between screen types. The pattern in `panels/` is inconsistent even within itself.
**Recommendation:** Standardize: UIWindow subclasses override `process_event` (required by pygame_gui framework). Custom panels/components should consistently use `handle_event`. Document this as a convention.
**Effort:** Complex

---

#### MAJOR: Mixed `draw()` Parameter Naming (`screen` vs `surface` vs `screen_surface`)
**ID:** CON-UI1-004
**Location:** 42 `draw()` methods across screens/ and panels/
**Issue:** The `draw(self, ...)` method uses three different parameter names for the same concept (a `pygame.Surface` to draw on): `screen` (dominant, ~25 occurrences: BattleScreen, BuilderScreen, StrategyScreen, etc.), `surface` (secondary, ~12 occurrences: all test_lab components, BattleStateViewer panels, component_dropdown, widgets.py), and `screen_surface` (~2 occurrences: GalaxyModeHelper, SystemModeHelper in galaxy_test/). Additionally, type annotations are inconsistent: some annotate as `pygame.Surface`, some as `Any`, and many lack annotations entirely.
**Impact:** Moderate confusion. When reading code that calls `self.child.draw(screen)`, the recipient might name the parameter `surface`, creating a mental mapping burden. New code authors must check existing files to pick the "right" name.
**Recommendation:** Standardize on `screen` (the dominant convention). Update `surface` and `screen_surface` usages. Always type-annotate as `pygame.Surface`.
**Effort:** Simple

---

#### MAJOR: Mixed `update()` Parameter Naming (`dt` vs `time_delta`)
**ID:** CON-UI1-005
**Location:** 21 `update()` methods in screens/
**Issue:** The time-step parameter for `update()` uses two names: `dt` (dominant, ~14 occurrences: BattleScreen, MenuScene, KeybindingsScene, FormationEditorScreen, SetupScreen, StrategyScreen, BuilderScreen, GalaxyTestScreen, WorkshopScreen, TestLabScreen, etc.) and `time_delta` (~7 occurrences: BuildQueueScreen, DesignSelectorWindow, EmpireBuildQueueWindow, FleetReportWindow, PlanetSelectionWindow, SaveSelectionWindow, PlanetListWindow). The split aligns roughly with UIWindow subclasses using `time_delta` (matching pygame_gui's convention) and custom screens using `dt`.
**Impact:** Inconsistency forces developers to check each class when calling `update()`. For facade/delegate classes that wrap both types, the parameter name must be chosen arbitrarily.
**Recommendation:** UIWindow subclasses should keep `time_delta` (pygame_gui convention). All other custom screens should use `dt`. Document this as an explicit convention.
**Effort:** Simple

---

#### MAJOR: Two Logging Systems Used in Parallel
**ID:** CON-UI1-006
**Location:** `game/ui/screens/builder/main.py:62,71-73` (stdlib `logging`), `game/ui/screens/test_lab/data_extractor.py:13` and 3 other test_lab files (`simulation_tests.logging_config.get_logger`), vs ~46 other files using `game.core.logger` functions
**Issue:** Three distinct logging mechanisms coexist: (1) **`game.core.logger`** module-level functions (`log_debug`, `log_info`, `log_warning`, `log_error`) -- dominant pattern used by ~46 files. (2) **stdlib `logging`** with `logging.getLogger(__name__)` -- used only in `builder/main.py` with hardcoded `logger.setLevel(logging.DEBUG)`. (3) **`simulation_tests.logging_config.get_logger`** -- used by 4 test_lab files (`data_extractor.py`, `screen.py`, `test_executor.py`, `validation_manager.py`). The `builder/main.py` file also has scattered imports (logging imported at line 62 inside a try/except, then again at line 71 at module scope) and a hardcoded debug level that will override any runtime configuration.
**Impact:** Inconsistent log output formatting, routing, and level control. The hardcoded `setLevel(DEBUG)` in builder/main.py can produce unexpected verbose output. Test_lab files use a different logger that may not integrate with the core logging pipeline.
**Recommendation:** Migrate all files to use `game.core.logger` functions exclusively. Remove the stdlib `logging` import and `setLevel` call from `builder/main.py`. Migrate test_lab files from `simulation_tests.logging_config.get_logger` to `game.core.logger`.
**Effort:** Simple

---

#### MAJOR: UIWindow Base Class Import Inconsistency
**ID:** CON-UI1-007
**Location:** 15 UIWindow subclasses across screens/
**Issue:** UIWindow subclasses use two different import patterns: (1) `from pygame_gui.elements import UIWindow` then `class X(UIWindow)` -- 10 classes (BuildQueueListWindow, CargoQuickDialog, DesignSelectorWindow, EmpireBuildQueueWindow, EmpirePanelWindow, EventLogWindow, FleetReportWindow, PlanetListWindow, PlanetSelectionWindow, TransferDialog). (2) `import pygame_gui` then `class X(pygame_gui.elements.UIWindow)` -- 5 classes (FleetOrdersWindow, NewGameSetupScreen, RaceBrowserDialog, RaceSetupScreen, SaveSelectionWindow). Both work identically but create visual inconsistency when scanning class definitions.
**Impact:** Low functional impact but moderate cognitive overhead. Developers establishing patterns for new windows may copy either style. Code reviews must account for both.
**Recommendation:** Standardize on `from pygame_gui.elements import UIWindow` (the dominant pattern, used by 10 of 15 classes). Update the 5 outlier classes.
**Effort:** Simple

---

#### MAJOR: Confusing Sibling File Names `strategy_detail_fmt.py` and `strategy_detail_formatter.py`
**ID:** CON-UI1-008
**Location:** `game/ui/screens/strategy_detail_fmt.py` and `game/ui/screens/strategy_detail_formatter.py`
**Issue:** Two files with nearly identical names serve related but different roles. `strategy_detail_fmt.py` contains standalone formatting functions (`format_spectrum_html`, `format_fleet_info`, etc.) while `strategy_detail_formatter.py` contains the `StrategyDetailFormatter` class that imports from `strategy_detail_fmt.py`. The abbreviation `fmt` vs full word `formatter` creates ambiguity -- is `_fmt` a shorter version of `_formatter` or a different thing?
**Impact:** Developers searching for "strategy detail format" find two files and must open both to determine which to modify. The abbreviated `_fmt` suffix breaks the project's general convention of using full words in filenames.
**Recommendation:** Rename `strategy_detail_fmt.py` to `strategy_detail_format_utils.py` or `strategy_detail_html.py` to clearly distinguish it as the utility functions module vs the formatter class module.
**Effort:** Simple

---

#### MAJOR: Mixed Class Suffix Convention for Strategy Delegates
**ID:** CON-UI1-009
**Location:** `game/ui/screens/strategy_colonization.py:21` (`ColonizationSystem`), `game/ui/screens/strategy_fleet_ops.py:20` (`FleetOperations`), `game/ui/screens/strategy_superweapons.py:29` (`SuperweaponOperations`)
**Issue:** Three strategy delegates extracted from `StrategyScreen` use inconsistent class name suffixes: `ColonizationSystem` uses "System" while `FleetOperations` and `SuperweaponOperations` use "Operations". All three follow the same structural pattern (extracted delegate, takes `scene` + `facade`, handles commands). The `SuperweaponOperations` docstring even says "Extracted following ColonizationSystem pattern for consistency" -- yet the name does not follow that pattern.
**Impact:** When searching for all strategy operation delegates, the naming inconsistency means you cannot use a single pattern to find them. A developer may not recognize `ColonizationSystem` as the same kind of delegate as `FleetOperations`.
**Recommendation:** Standardize on `Operations` suffix: rename `ColonizationSystem` to `ColonizationOperations`. All three delegates should share the suffix.
**Effort:** Simple

---

#### MINOR: Panel Classes Scattered Between `screens/` and `panels/` Directories
**ID:** CON-UI1-010
**Location:** 13 `*Panel` classes in `screens/` (e.g., `ComponentDetailPanel`, `LayerPanel`, `BuilderLeftPanel`, `BuilderRightPanel`, `WeaponsReportPanel`, `ModifierEditorPanel`, `ResultsPanel`, `ShipPanel`, `TestRunDetailsPanel`, `ScrollableJsonPanel`, `StrategyMenuPanel`) vs 17 `*Panel` classes in `panels/`
**Issue:** Classes with the `Panel` suffix exist in both `game/ui/screens/` and `game/ui/panels/`. There is no clear boundary for when a panel belongs in `screens/` vs `panels/`. For example, `ComponentDetailPanel` is in `screens/builder/detail_panel.py` while `ComponentModifierGridPanel` is in `panels/`. The `StrategyMenuPanel` is in `screens/` despite being a panel.
**Impact:** Developers creating new panel classes must guess which directory is correct. The organizational intent of having a separate `panels/` directory is undermined when half the panels live in `screens/`.
**Recommendation:** Establish a clear rule: `panels/` contains reusable, self-contained panels; `screens/` contains panels tightly coupled to their parent screen. Document this in CLAUDE.md or a README. Over time, migrate screen-specific panels from `panels/` to their parent screen's subdirectory, or migrate reusable panels from `screens/` to `panels/`.
**Effort:** Complex

---

#### MINOR: Missing Module-Level Docstrings in 18 Files
**ID:** CON-UI1-011
**Location:** `battle_ui.py`, `builder/components.py`, `builder/drop_target.py`, `builder/grouping_strategies.py`, `builder/left_panel.py`, `builder/panel_layout_config.py`, `builder/preset_ui.py`, `builder/structure_list_items.py`, `builder/weapons_panel.py`, `builder_utils.py` (has comment not docstring), `formation_editor.py`, `planet_list_window.py`, `planet_selection_window.py`, `transfer_dialog.py`, `workshop_screen.py`, `panels/battle_panels.py`, `panels/strategy_widgets.py`, `panels/system_tree_panel.py`
**Issue:** 18 out of 134 Python files (13%) lack a module-level docstring. The dominant pattern (116 files, 87%) has a proper `"""..."""` docstring at the top of the file. The project conventions require docstrings on public APIs, and module-level docstrings are the first thing a developer sees when opening a file.
**Impact:** Minor degradation of code navigation and discoverability. Files without docstrings are harder to identify in IDE hover previews and documentation generators.
**Recommendation:** Add module-level docstrings to these 18 files following the established project pattern (brief description, optional cross-layer import notes, optional PROJ references).
**Effort:** Simple

---

#### MINOR: `__init__.py` Export Patterns Inconsistent Across Subpackages
**ID:** CON-UI1-012
**Location:** `screens/__init__.py` (empty), `screens/builder/__init__.py` (imports only, no `__all__`), `screens/formation/__init__.py` (docstring + imports + `__all__`), `screens/galaxy_test/__init__.py` (docstring + imports + `__all__`), `screens/test_lab/__init__.py` (full docstring + imports + `__all__`), `panels/__init__.py` (empty)
**Issue:** Four different patterns for `__init__.py`: (1) Empty (screens, panels), (2) Imports without `__all__` or docstring (builder), (3) Docstring + imports + `__all__` (formation, galaxy_test), (4) Comprehensive docstring + module listing + imports + `__all__` (test_lab). The most complete pattern (test_lab) is the best practice but only one package follows it.
**Impact:** Inconsistent import behavior. Packages without `__all__` expose internal implementation details on wildcard import. The builder package lacks `__all__`, meaning `from game.ui.screens.builder import *` could import unintended names.
**Recommendation:** Standardize on the test_lab pattern: brief module docstring, explicit imports, and `__all__` list. Apply to `builder/__init__.py` first (add `__all__`), then consider adding lightweight `__init__.py` content to `screens/` and `panels/` top-level packages.
**Effort:** Simple

---

#### MINOR: Scene vs Screen Class Naming Convention Split
**ID:** CON-UI1-013
**Location:** `MenuScene` (menu_scene.py), `KeybindingsScene` (keybindings_scene.py) vs `BattleScreen`, `StrategyScreen`, `BuilderScreen`, `FormationEditorScreen`, `GalaxyTestScreen`, `TestLabScreen`, `BuildQueueScreen`, `BattleSetupScreen`, `DesignWorkshopScreen`, `NewGameSetupScreen`, `RaceSetupScreen`
**Issue:** Two IScene-implementing classes use the `Scene` suffix while 11 others use `Screen`. All implement the same protocol (`handle_event`, `update`, `draw`, `handle_resize`). The `Scene` suffix is used only for the menu and keybindings screens, which are simpler full-screen UIs.
**Impact:** Minor naming inconsistency. When searching for "all screens", the `Scene` classes are missed. The distinction between Scene and Screen is not documented and appears arbitrary.
**Recommendation:** If `Scene` and `Screen` represent a meaningful distinction (e.g., Scene = lightweight overlay, Screen = full game mode), document it explicitly. Otherwise, standardize on `Screen` for all IScene implementors and rename `MenuScene` to `MenuScreen` and `KeybindingsScene` to `KeybindingsScreen`.
**Effort:** Simple

---

#### MINOR: Function-Level Logger Imports in `design_selector_window.py` and `strategy_renderer.py`
**ID:** CON-UI1-014
**Location:** `game/ui/screens/design_selector_window.py:232,503,522,535` and `game/ui/screens/strategy_renderer.py:563`
**Issue:** Five methods in these two files import logger functions at function scope (`from game.core.logger import log_info, log_debug`) instead of at module scope. Every other file in the codebase that uses `game.core.logger` imports it at the top of the file. There is no comment explaining why these are deferred imports (unlike the `INTENTIONAL LATE IMPORT` comments used for circular dependency avoidance in `column_manager.py`).
**Impact:** Minor inconsistency. Function-level imports add overhead per-call and obscure dependencies. Without an explanatory comment, future maintainers cannot tell if the deferral is intentional or accidental.
**Recommendation:** Move these imports to module scope, matching the dominant pattern. If deferred import is truly needed (circular dependency), add an `# INTENTIONAL LATE IMPORT:` comment explaining why.
**Effort:** Simple

---

#### MINOR: `builder/main.py` Has Scattered Imports and Hardcoded Log Level
**ID:** CON-UI1-015
**Location:** `game/ui/screens/builder/main.py:62-73,75`
**Issue:** `builder/main.py` has imports scattered throughout the file rather than grouped at the top: `import logging` at line 62 (inside try/except), `from game.ui.colors import COLORS` at line 67, `import logging` again at line 71 (module scope), `logger.setLevel(logging.DEBUG)` at line 73, and `from .detail_panel import ComponentDetailPanel` at line 75 (after the logging setup). The standard convention groups all imports at the top, with late imports only where circular dependencies require it. The hardcoded `setLevel(DEBUG)` overrides any runtime logging configuration.
**Impact:** Hard to determine the full dependency set of this module by scanning the top. The hardcoded debug level may cause excessive log output in production.
**Recommendation:** Consolidate all imports at the top of the file. Remove the duplicate `import logging`. Remove `logger.setLevel(logging.DEBUG)` (let the application configure log levels). Move to `game.core.logger` functions per CON-UI1-006.
**Effort:** Simple

---

#### MINOR: Broad Exception Catch Without Justification Comment in `race_environment_panel.py`
**ID:** CON-UI1-016
**Location:** `game/ui/panels/race_environment_panel.py:475`
**Issue:** `except Exception:` with no justification comment. All other broad exception catches in the codebase include an `# Intentional broad catch:` comment explaining why (e.g., `builder/event_bus.py:55`, `planet_list_window.py:418`, `workshop_ship_io.py:259`, `workshop_data_reloader.py:20`). This one silently swallows errors and sets the label to empty string.
**Impact:** Minor inconsistency with established commenting convention. Could mask real errors in the `RacePointBudget` calculation.
**Recommendation:** Add an `# Intentional broad catch:` comment explaining the rationale (e.g., "budget calculation failure is non-critical for UI display"). Consider catching a more specific exception type.
**Effort:** Simple

---

#### INFO: Return Type Annotations Present on Only ~30% of Methods in screens/
**ID:** CON-UI1-017
**Location:** Across all 109 files in screens/
**Issue:** 332 method signatures include return type annotations (`-> Type`) while 874 do not (~27.5%). The `panels/` directory is better at ~47% (120 with vs 137 without). The project convention calls for "type hints on all function signatures" but this is far from achieved. Notable files with good coverage: `keybindings_scene.py` (21 annotated), `empire_build_queue_window.py` (21), `strategy_window_manager.py` (20), `formation_editor.py` (53). Files with near-zero coverage: `builder/main.py`, `builder/left_panel.py`, `workshop_screen.py`.
**Impact:** Reduced IDE support, harder refactoring, less self-documenting code. The inconsistency means some modules are well-typed while neighboring modules provide no type information.
**Recommendation:** Prioritize adding return type annotations to public methods in the most-touched files. Consider a lint rule to enforce return annotations on new code.
**Effort:** Complex

---

#### INFO: `from __future__ import annotations` Used in Only ~26% of Files
**ID:** CON-UI1-018
**Location:** 29 of 109 screens files, 6 of 25 panels files
**Issue:** The `from __future__ import annotations` import (enabling PEP 563 postponed evaluation) is used in about 26% of screens files and 24% of panels files. This import is needed for forward references and `TYPE_CHECKING` patterns to work correctly. Files that use it tend to be newer (PROJ-86 extractions, build queue, strategy delegates). Older files do not use it.
**Impact:** Low immediate impact, but inconsistency means some files can reference not-yet-defined types in annotations while others cannot. Some `TYPE_CHECKING` blocks may not work correctly without it.
**Recommendation:** Consider adopting `from __future__ import annotations` as a standard first-line import for all files. Apply incrementally when files are touched.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **CON-UI1-001 (CRITICAL): Duplicate `ModifierEditorPanel` class name** -- Two different classes with the same name imported by different screens. Highest confusion risk and violates the project's eradication policy for old systems.

2. **CON-UI1-002 (CRITICAL): Duplicate `ColumnManager` class name** -- Two unrelated column managers with the same class name. Namespace collision creates ambiguity in search results and imports.

3. **CON-UI1-003 (MAJOR): Mixed `handle_event` vs `process_event` naming** -- The most pervasive naming inconsistency, affecting 50 classes. The pattern is partially predictable (UIWindow = process_event) but not consistently followed in panels/.

4. **CON-UI1-006 (MAJOR): Three parallel logging systems** -- stdlib `logging`, `simulation_tests.logging_config.get_logger`, and `game.core.logger` all coexist. The `builder/main.py` hardcoded debug level is particularly problematic.

5. **CON-UI1-009 (MAJOR): Mixed suffix convention for strategy delegates** -- `ColonizationSystem` vs `FleetOperations` / `SuperweaponOperations` breaks the ability to find all delegates by pattern. Simple rename fix with high clarity benefit.
