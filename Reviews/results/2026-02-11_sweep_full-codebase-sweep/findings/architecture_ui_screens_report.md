# Architecture Drift Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/ and game/ui/panels/)
- **Files Scanned:** 134 (109 in screens/, 25 in panels/)
- **Total Issues Found:** 23
- **Critical:** 2 | **Major:** 10 | **Minor:** 7 | **Info:** 4

## Findings

---

### Critical Issues

#### CRITICAL: Test Lab UI Imports From test_framework and simulation_tests Packages
**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:16-18`, `game/ui/screens/test_lab/test_executor.py:11-13`, `game/ui/screens/test_lab/data_extractor.py:13`, `game/ui/screens/test_lab/validation_manager.py:12,48`, `game/ui/screens/battle_screen.py:450`
**Issue:** Six files in the UI layer import directly from `test_framework` and `simulation_tests` packages, which are test infrastructure outside the `game/` package hierarchy entirely. These imports include:
- `from test_framework.registry import TestRegistry`
- `from test_framework.runner import TestRunner`
- `from test_framework.test_history import TestHistory`
- `from test_framework.battle_state_capture import BattleStateCapture`
- `from simulation_tests.logging_config import get_logger`
- `from simulation_tests.scenarios.validation import Validator`

**Impact:** The production UI layer depends on test infrastructure packages. This means: (1) test packages must be available at runtime, not just during testing; (2) changes to test infrastructure can break the game UI; (3) the Combat Lab screen cannot be distributed without the test framework; (4) circular conceptual dependency -- tests should depend on the game, not the other way around.
**Recommendation:** Extract the shared interfaces (TestRegistry, TestRunner, TestHistory) into a lightweight `game/core/test_protocol.py` or `game/combat_lab/` package that both the UI and test framework can depend on. The test framework's data loading, registry, and runner capabilities needed by the UI should be abstracted behind interfaces in the game package.
**Effort:** Complex

#### CRITICAL: Simulation Layer Imports tkinter GUI Framework
**ID:** ADR-UI1-002
**Location:** `game/simulation/systems/persistence.py:3-4`
**Issue:** The simulation layer's `ShipIO` class imports `tkinter` at the top level for file dialog functionality. This is a direct UI framework dependency in the simulation layer, which should have zero UI dependencies. The UI screens (`builder/main.py:44`, `workshop_data_loader.py:115`) import from this module, inheriting and propagating the violation.
**Impact:** Prevents headless operation of ship I/O; simulation layer cannot be tested without tkinter installed; violates the strict "simulation depends on core ONLY" rule. The file dialog functionality is a UI concern that has leaked into the data persistence layer.
**Recommendation:** Split `ShipIO` into two classes: (1) `ShipSerializer` in simulation layer for pure JSON serialization/deserialization (no UI), and (2) `ShipFileDialog` in UI layer for file picker integration. The UI screens should use the UI-layer wrapper.
**Effort:** Medium

---

### Major Issues

#### MAJOR: TestLabScreen God Class (1877 lines, 75 methods)
**ID:** ADR-UI1-003
**Location:** `game/ui/screens/test_lab/screen.py:32-1908`
**Issue:** `TestLabScreen` is an extreme god class with 1877 lines and 75 methods. Despite partial decomposition into `TestLabExecutor`, `TestLabPanelManager`, `TestLabDataExtractor`, and `TestLabValidationManager`, the main class still contains the vast majority of logic. It handles rendering, event routing, state management, data loading, and scenario configuration all in one class.
**Impact:** Very difficult to test individual behaviors in isolation; high risk of regressions when making changes; cognitive overload for developers; inhibits parallel development.
**Recommendation:** Continue decomposition: extract rendering logic into a dedicated renderer, state management into a state machine, and event handling into an event router (following the pattern established by StrategyScreen's decomposition into StrategyRenderer, StrategyInputHandler, StrategyEventRouter, etc.).
**Effort:** Complex

#### MAJOR: BuilderScreen God Class (1042 lines, 44 methods)
**ID:** ADR-UI1-004
**Location:** `game/ui/screens/builder/main.py:81-1123`
**Issue:** `BuilderScreen` has 1042 lines and 44 methods. It manages component selection, drag-and-drop, ship class changes, data reloading, panel layout, grouping strategies, and event dispatch.
**Impact:** Hard to test, hard to modify safely, mixes rendering with business logic.
**Recommendation:** Extract remaining responsibilities: ship class change logic, grouping/filtering logic, and event dispatch into separate collaborator classes.
**Effort:** Medium

#### MAJOR: FormationEditorScreen God Class (701 lines, 51 methods) with tkinter Coupling
**ID:** ADR-UI1-005
**Location:** `game/ui/screens/formation_editor.py:1-929`
**Issue:** `FormationEditorScreen` has 701 lines and 51 methods. Additionally, it imports `tkinter` at module level and initializes a `tkinter.Tk()` root at import time (line 21), which can cause crashes in headless environments. The tkinter root is created as a module-level side effect.
**Impact:** Module-level tkinter initialization is a side effect that runs when the module is imported, even if the formation editor is never used. Can cause test failures in CI environments without displays.
**Recommendation:** (1) Move tkinter initialization to lazy/on-demand inside the methods that use file dialogs; (2) continue splitting the 51-method class into FormationCore (data model), FormationRenderer, and FormationInputHandler (partially done already).
**Effort:** Medium

#### MAJOR: StrategyScreen God Class (768 lines, 45 methods)
**ID:** ADR-UI1-006
**Location:** `game/ui/screens/strategy_screen.py:40-811`
**Issue:** Despite significant decomposition (StrategyRenderer, StrategyInputHandler, StrategyEventRouter, StrategyUI, etc.), `StrategyScreen` still has 768 lines and 45 methods. It remains the central coordinator with many lazy imports inside methods (14 unique lazy import blocks).
**Impact:** Still difficult to test in isolation; the high number of lazy imports suggests ongoing circular dependency concerns.
**Recommendation:** Continue extracting responsibilities. The 14 lazy import blocks should be analyzed to determine if they indicate deeper design issues or can be resolved through better dependency injection.
**Effort:** Complex

#### MAJOR: Extensive Private Attribute Access Across Module Boundaries
**ID:** ADR-UI1-007
**Location:** `game/ui/screens/strategy_event_router.py:60,100,130,227,238,240,242`, `game/ui/screens/strategy_input_handler.py:230,243,246,358,367,374,397,415,424,493,508,523,538,553,573,581,588,724,810`, `game/ui/screens/cargo_quick_dialog.py:58`
**Issue:** Multiple UI screen modules extensively access private (underscore-prefixed) attributes of other classes:
- `strategy_event_router.py` accesses `self.ui._window_manager` (7 times) and `self.ui.scene._handle_quit_confirmed()`
- `strategy_input_handler.py` accesses `self.scene._superweapons`, `self.scene._camera_nav`, `self.scene._fleet_ops`, `self.scene._colonization`, `self.scene._get_system_at_hex()`, `self.scene.ui._has_modal_open()` (20+ times)
- `cargo_quick_dialog.py` accesses `scene._facade`

**Impact:** Violates encapsulation; changes to private APIs of StrategyScreen, StrategyUI, or StrategyWindowManager will cascade to all dependent modules; makes refactoring risky.
**Recommendation:** Expose public interfaces on StrategyScreen and StrategyUI for the operations that extracted helpers need. Convert the most-used private attributes to public properties or provide public accessor methods.
**Effort:** Medium

#### MAJOR: UI Layer Mutates Strategy Data Objects With Temporary Attributes
**ID:** ADR-UI1-008
**Location:** `game/ui/screens/planet_list_filters.py:26-35`, `game/ui/screens/strategy_renderer.py:446-447`
**Issue:** Two UI modules dynamically attach temporary attributes to strategy-layer data objects:
- `planet_list_filters.py` sets `p._temp_system_ref`, `p._cached_gravity_g`, `p._cached_mass_earth`, `p._cached_name_lower`, `p._cached_type_category` on Planet objects
- `strategy_renderer.py` sets `p._temp_screen_pos` and `p._temp_draw_r` (screen coordinates and pixel radii) on Planet objects

**Impact:** Strategy-layer data objects accumulate UI-specific state that pollutes their namespace, can cause subtle bugs if these temp attributes leak to other systems, and creates implicit coupling between UI rendering logic and the Planet data model. Screen coordinates should never be stored on domain objects.
**Recommendation:** Use a separate dictionary (e.g., `planet_render_cache: Dict[Planet, RenderInfo]`) in the renderer to store screen positions. For planet list filters, use a wrapper dataclass `FilteredPlanet` that holds the planet reference and cached filter values.
**Effort:** Medium

#### MAJOR: BattleScreen God Class (621 lines, 32 methods)
**ID:** ADR-UI1-009
**Location:** `game/ui/screens/battle_screen.py:40-660`
**Issue:** `BattleScreen` has 621 lines and 32 methods, handling simulation updates, rendering, input, test mode management, and UI panel coordination.
**Impact:** Mixes simulation control with rendering and input handling; the test mode logic adds significant complexity.
**Recommendation:** Extract test mode logic into a `BattleTestMode` class. Separate rendering from simulation update logic.
**Effort:** Medium

#### MAJOR: FleetReportWindow God Class (1075 lines, 29 methods)
**ID:** ADR-UI1-010
**Location:** `game/ui/screens/fleet_report_window.py:7-1093`
**Issue:** `FleetReportWindow` has 1075 lines and 29 methods, managing ship list rendering, column management, filtering, sorting, detail panels, and ship image loading.
**Impact:** Difficult to modify individual features without risk of affecting others.
**Recommendation:** Extract ship list rendering, column management, and detail panel coordination into separate collaborator classes.
**Effort:** Medium

#### MAJOR: BuildQueueScreen God Class (1057 lines, 31 methods)
**ID:** ADR-UI1-011
**Location:** `game/ui/screens/build_queue_screen.py:42-1098`
**Issue:** `BuildQueueScreen` has 1057 lines and 31 methods. While some functionality has been extracted to `BuildQueueController`, `BuildQueueDragHandler`, and `BuildQueuePortraitLoader`, the main screen class still contains significant rendering and event handling logic.
**Impact:** Complex to maintain; rendering mixed with business logic.
**Recommendation:** Extract remaining rendering logic and event handling into separate collaborator classes.
**Effort:** Medium

#### MAJOR: EmpireBuildQueueWindow God Class (791 lines, 30 methods)
**ID:** ADR-UI1-012
**Location:** `game/ui/screens/empire_build_queue_window.py:22-863`
**Issue:** `EmpireBuildQueueWindow` has 791 lines and 30 methods. Some filtering has been extracted to `BuildQueueFilterManager` and formatting to `EmpireBuildQueueFormatter`, but the main class is still very large.
**Impact:** Hard to test and maintain. Mixes UI layout with business logic.
**Recommendation:** Continue decomposition following established patterns.
**Effort:** Medium

---

### Minor Issues

#### MINOR: UIConfig and DisplayConfig in Core Layer
**ID:** ADR-UI1-013
**Location:** `game/core/config.py:132-159` (UIConfig), `game/core/config.py:18-46` (DisplayConfig)
**Issue:** `UIConfig` (panel padding, element spacing, toast dimensions, font sizes) and `DisplayConfig` (screen resolutions) are defined in the core layer but are purely UI concerns. While they are currently only consumed by UI-layer code, their placement in core establishes a precedent for UI config to live in non-UI layers.
**Impact:** Low immediate impact since only UI code consumes these. However, it muddies the "core has no UI awareness" principle and could encourage future developers to add more UI config to core.
**Recommendation:** Move `UIConfig` and `DisplayConfig` to `game/ui/config.py`. Core layer can retain `PhysicsConfig`, `AIConfig`, and `BattleConfig` which are legitimately non-UI.
**Effort:** Simple

#### MINOR: UI Color Constants (WHITE, BLACK, BLUE, FONT_MAIN) in Core Constants
**ID:** ADR-UI1-014
**Location:** `game/core/constants.py:42-49`
**Issue:** Color tuples (`WHITE`, `BLACK`, `BLUE`, `RED`, `GREEN`) and `FONT_MAIN` are defined in `game/core/constants.py`. These are rendering-specific constants that belong in the UI layer.
**Impact:** No operational issue (only consumed by UI code via test_lab screens), but contributes to core layer bloat and blurs the boundary between core and UI concerns.
**Recommendation:** Move to `game/ui/colors.py` (which already exists and defines `COLORS` dict) or a dedicated `game/ui/constants.py`.
**Effort:** Simple

#### MINOR: Circular Import Avoidance via Late Imports in column_manager and fleet_report_filters
**ID:** ADR-UI1-015
**Location:** `game/ui/screens/column_manager.py:181,191,196,224`, `game/ui/screens/fleet_report_filters.py:238,246`
**Issue:** Six late imports in `column_manager.py` and `fleet_report_filters.py` are explicitly marked with "INTENTIONAL LATE IMPORT: Avoid circular import" comments. The imported modules are strategy-layer calculators (`FleetSpeedCalculator`, `ShipStatsCalculator`, `FleetCapabilityCalculator`).
**Impact:** Late imports add runtime overhead and make dependencies less visible. The pattern suggests these UI modules have a dependency that strategy modules might also have on them, creating a latent circular dependency.
**Recommendation:** Review whether these calculators should be injected via dependency injection rather than imported at call time. Consider using a service locator or passing the calculators as constructor parameters.
**Effort:** Simple

#### MINOR: Module-Level tkinter Initialization Side Effects
**ID:** ADR-UI1-016
**Location:** `game/ui/screens/formation_editor.py:20-25`, `game/ui/screens/builder/main.py:22-23`
**Issue:** `formation_editor.py` creates a `tkinter.Tk()` root at module import time (line 21). `builder/main.py` also imports tkinter at the top level. These module-level initializations create side effects on import.
**Impact:** Importing these modules in headless/CI environments can fail or produce warnings. The tkinter root creation at module level is a side effect that should be deferred.
**Recommendation:** Move tkinter initialization inside the methods that use file dialogs, wrapped in try/except.
**Effort:** Simple

#### MINOR: Deep Attribute Chains Violating Law of Demeter
**ID:** ADR-UI1-017
**Location:** `game/ui/screens/test_lab/screen.py:435,463,465`, `game/ui/screens/builder/main.py:804,1021,1037`, `game/ui/screens/strategy_event_router.py:104`
**Issue:** Several files use deep attribute chains (3-4 levels):
- `self.game.battle_scene._battle_service.create_battle()` (4 levels + private)
- `self.game.battle_scene.camera.fit_objects(ships)` (4 levels)
- `self.game.battle_scene.camera.target_zoom = self.game.battle_scene.camera.zoom` (4 levels)
- `self.right_panel.class_dropdown.relative_rect.y` (4 levels)
- `self.ui._window_manager.fleet_orders_window.handle_global_event(event)` (4 levels + private)

**Impact:** Makes code brittle to structural changes; each intermediate object becomes a coupling point.
**Recommendation:** Introduce facade methods at each level to reduce chain length. For example, `self.game.fit_battle_camera(ships)` instead of `self.game.battle_scene.camera.fit_objects(ships)`.
**Effort:** Medium

#### MINOR: Circular Import Avoidance in new_game_setup_screen
**ID:** ADR-UI1-018
**Location:** `game/ui/screens/new_game_setup_screen.py:397-398,425-426`
**Issue:** Two late imports explicitly commented as "Import here to avoid circular imports":
- `from game.ui.screens.race_setup_screen import RaceBrowserDialog`
- `from game.ui.screens.race_setup_screen import RaceSetupScreen`

**Impact:** These are intra-module circular dependencies within the UI screens package, suggesting the new_game_setup_screen and race_setup_screen have a bidirectional relationship.
**Recommendation:** Consider extracting shared types (like RaceBrowserDialog) into a separate module that both screens can import cleanly.
**Effort:** Simple

#### MINOR: TestLabScreen Directly Accesses battle_screen Private _battle_service
**ID:** ADR-UI1-019
**Location:** `game/ui/screens/test_lab/screen.py:435`
**Issue:** `self.game.battle_scene._battle_service.create_battle()` -- TestLabScreen reaches through the game object, into battle_scene, accesses a private `_battle_service`, and calls `create_battle()`. This is a 4-level deep chain with private access.
**Impact:** Tightly couples TestLabScreen to BattleScreen's internal implementation.
**Recommendation:** Provide a public method on BattleScreen like `ensure_battle_engine()` that TestLabScreen can call.
**Effort:** Simple

---

### Informational

#### INFO: WeaponsReportPanel File Size (1037 lines, 19 methods)
**ID:** ADR-UI1-020
**Location:** `game/ui/screens/builder/weapons_panel.py:1-1037`
**Issue:** `WeaponsReportPanel` has 1037 lines. With 19 methods, it's under the 20-method threshold but the line count is high. The class handles both data aggregation and rendering of weapons statistics.
**Impact:** Large but currently manageable. Worth monitoring as features are added.
**Recommendation:** Consider separating weapons data aggregation from rendering in a future refactor.
**Effort:** Medium

#### INFO: RaceSummaryPanel (671 lines, 25 methods) in Panels
**ID:** ADR-UI1-021
**Location:** `game/ui/panels/race_summary_panel.py:14-696`
**Issue:** `RaceSummaryPanel` is the largest panel at 671 lines and 25 methods. It handles portrait rendering, stat display, theme preview, and layout management.
**Impact:** Approaching god class territory but still within reason for a composite UI panel.
**Recommendation:** Monitor growth; consider extracting sub-panels if it grows further.
**Effort:** Simple

#### INFO: WorkshopViewModel (551 lines, 36 methods)
**ID:** ADR-UI1-022
**Location:** `game/ui/screens/workshop_viewmodel.py:30-580`
**Issue:** `WorkshopViewModel` has 36 methods in 551 lines. As a ViewModel in MVVM architecture, it legitimately handles many operations, but 36 methods is on the high side.
**Impact:** Complexity is manageable if methods are small and focused, which they appear to be.
**Recommendation:** Review whether some operations could be grouped into sub-ViewModels.
**Effort:** Simple

#### INFO: StrategyUI Thin Facade (357 lines, 38 methods)
**ID:** ADR-UI1-023
**Location:** `game/ui/screens/strategy_ui.py:19-375`
**Issue:** `StrategyUI` has 38 methods in only 357 lines, meaning methods average ~9 lines each. This is a thin facade delegating to extracted managers (WindowManager, PanelManager, EventRouter, DetailFormatter). The high method count is a natural consequence of the facade pattern.
**Impact:** No significant concern -- this is the intended design from PROJ-86 god class decomposition.
**Recommendation:** No action needed. The facade pattern is working as intended.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **ADR-UI1-001 (CRITICAL):** Test Lab UI imports from test_framework/simulation_tests -- production UI depends on test infrastructure packages, preventing clean distribution and creating a reversed dependency direction.

2. **ADR-UI1-002 (CRITICAL):** Simulation layer's persistence.py imports tkinter -- GUI framework in the simulation layer violates headless operation guarantees and the core "simulation depends on core ONLY" rule.

3. **ADR-UI1-003 (MAJOR):** TestLabScreen god class (1877 lines, 75 methods) -- the largest class in the UI screens by far, making it extremely difficult to maintain and test.

4. **ADR-UI1-007 (MAJOR):** Extensive private attribute access across module boundaries (30+ occurrences) -- StrategyInputHandler and StrategyEventRouter routinely access private members of StrategyScreen and StrategyUI, creating tight coupling that undermines the decomposition effort.

5. **ADR-UI1-008 (MAJOR):** UI layer mutates strategy data objects with temporary rendering attributes -- screen coordinates and filter caches are dynamically attached to Planet domain objects, violating data flow direction.
