# Architecture Drift Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 130 (105 in game/ui/screens/, 25 in game/ui/panels/)
- **Total Issues Found:** 14
- **Critical:** 0 | **Major:** 7 | **Minor:** 5 | **Info:** 2

## Findings

### Layer Violations

**No critical layer violations found.** The UI layer appropriately imports from core, simulation, strategy, and ai layers, following the established architecture rules. All pygame usage is correctly confined to the UI layer.

### God Classes / Large File Complexity

#### MAJOR: TestLabScreen God Class
**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:1-1911`
**Issue:** TestLabScreen class spans 1911 lines with 75 methods, significantly exceeding the recommended 500 lines / 30 methods threshold for maintainability.
**Impact:** Difficult to test individual behaviors in isolation, high cognitive load for maintenance, violates Single Responsibility Principle.
**Recommendation:** Extract distinct responsibilities into separate classes:
- TestListRenderer for rendering test lists
- TestCategoryManager for category/filtering logic
- TestExecutionCoordinator for test run coordination
- BattleSceneIntegration for battle scene interactions
**Effort:** Complex

#### MAJOR: FleetReportWindow God Class
**ID:** ADR-UI1-002
**Location:** `game/ui/screens/fleet_report_window.py:1-1093`
**Issue:** FleetReportWindow class spans 1093 lines with 29 methods, handling list rendering, filtering, sorting, and detail display in a single class.
**Impact:** Tightly couples display logic with data manipulation; difficult to test filtering independently.
**Recommendation:** Extract FleetReportListRenderer, FleetReportFilterManager, and ShipDetailFormatter into separate modules.
**Effort:** Medium

#### MAJOR: BuildQueueScreen Large Class
**ID:** ADR-UI1-003
**Location:** `game/ui/screens/build_queue_screen.py:1-1098`
**Issue:** BuildQueueScreen class spans 1098 lines with 31 methods, combining queue management, rendering, and user interaction.
**Impact:** Changes to queue rendering require touching the same file as queue logic changes.
**Recommendation:** Extract rendering logic to BuildQueueRenderer and separate queue mutation logic into BuildQueueOperations.
**Effort:** Medium

#### MAJOR: StrategyScreen Large Class
**ID:** ADR-UI1-004
**Location:** `game/ui/screens/strategy_screen.py:1-810`
**Issue:** StrategyScreen class has 810 lines with 45 methods, acting as a central coordinator with too many direct responsibilities.
**Impact:** High coupling between different strategy map features; testing individual features requires mocking the entire scene.
**Recommendation:** Continue the extraction pattern already started (FleetOperations, CameraNavigator, etc.) by extracting remaining inline logic.
**Effort:** Medium

### Inappropriate Intimacy / Encapsulation Violations

#### MAJOR: Private Facade Access in Dialogs
**ID:** ADR-UI1-005
**Location:** `game/ui/screens/cargo_quick_dialog.py:58`, `game/ui/screens/transfer_dialog.py:33`
**Issue:** Both dialogs access `scene._facade` (private attribute with underscore prefix), breaking encapsulation and creating hidden coupling.
**Impact:** Changes to scene's internal facade handling require changes to dialog code; violates Law of Demeter.
**Recommendation:** Pass facade explicitly to dialog constructors, or provide public accessor method `scene.get_facade()`.
**Effort:** Simple

#### MAJOR: Private Method Access in BattleUI
**ID:** ADR-UI1-006
**Location:** `game/ui/screens/battle_ui.py:98`
**Issue:** BattleUI calls `self.scene._trigger_return_to_test_lab()`, directly invoking a private method on another object.
**Impact:** Tight coupling between BattleUI and internal implementation details of the scene.
**Recommendation:** Add a public method `scene.trigger_return_to_test_lab()` or use an event/callback pattern.
**Effort:** Simple

#### MAJOR: StrategyInputHandler Excessive Scene Coupling
**ID:** ADR-UI1-007
**Location:** `game/ui/screens/strategy_input_handler.py:230-588`
**Issue:** StrategyInputHandler accesses 15+ private attributes of scene including `scene._fleet_ops`, `scene._colonization`, `scene._superweapons`, `scene._camera_nav`, `scene._facade`.
**Impact:** InputHandler is tightly coupled to scene's internal structure; any refactoring of scene internals breaks the handler.
**Recommendation:** Either make these subsystems public (without underscore) since they're part of the stable interface, or use dependency injection to pass required services directly to InputHandler.
**Effort:** Medium

### Minor Issues

#### MINOR: Deep Attribute Chains (Law of Demeter)
**ID:** ADR-UI1-008
**Location:** `game/ui/screens/test_lab/screen.py:436-469`
**Issue:** Multiple deep attribute chains like `self.game.battle_scene._battle_service.create_battle()` and `self.game.battle_scene.camera.fit_objects()`.
**Impact:** Changes to intermediate object structure break calling code.
**Recommendation:** Provide facade methods that hide the depth of the call chain.
**Effort:** Simple

#### MINOR: Panel Accessing Internal Cache
**ID:** ADR-UI1-009
**Location:** `game/ui/screens/test_lab/validation_manager.py:134-138`, `game/ui/screens/test_lab/screen.py:252`
**Issue:** Accesses `data_extractor._components_cache` (private cache) directly.
**Impact:** Couples callers to internal caching implementation.
**Recommendation:** Add public method `data_extractor.get_components()` that manages caching internally.
**Effort:** Simple

#### MINOR: Nested Private Format Method Access
**ID:** ADR-UI1-010
**Location:** `game/ui/screens/race_setup_screen.py:543`, `game/ui/screens/strategy_ui.py:248,257,276`
**Issue:** Accesses private formatting methods of owned panels (e.g., `_environment_panel._format_radiation()`).
**Impact:** Parent screen depends on panel implementation details.
**Recommendation:** Use public formatting API or delegate formatting to panel entirely.
**Effort:** Simple

#### MINOR: Workshop Data Reloader Private Attribute Mutation
**ID:** ADR-UI1-011
**Location:** `game/ui/screens/workshop_data_reloader.py:182`
**Issue:** Directly mutates `self.viewmodel._selected_components = []` from external class.
**Impact:** Bypasses any validation or change notification the viewmodel might implement.
**Recommendation:** Add `viewmodel.clear_selection()` public method.
**Effort:** Simple

#### MINOR: Strategy Event Router Accesses Scene Private Dialog
**ID:** ADR-UI1-012
**Location:** `game/ui/screens/strategy_event_router.py:129-130`
**Issue:** Checks and handles `self.ui.scene._quit_confirm_dialog` by accessing private attribute.
**Impact:** Router knows about scene's internal dialog management.
**Recommendation:** Use scene method like `scene.is_quit_dialog_visible()` and `scene.confirm_quit()`.
**Effort:** Simple

### Info / Observations

#### INFO: Heavy Use of TYPE_CHECKING Imports
**ID:** ADR-UI1-013
**Location:** Multiple files (44 files use TYPE_CHECKING blocks)
**Issue:** Extensive use of TYPE_CHECKING imports throughout screens/panels. While technically correct for avoiding runtime circular imports, this pattern can mask actual circular dependency issues.
**Impact:** None immediate; the architecture is stable but the pattern could hide future dependency problems.
**Recommendation:** Periodically review whether TYPE_CHECKING imports could be converted to runtime imports if underlying circular dependencies are resolved.
**Effort:** N/A (observation only)

#### INFO: Lazy Imports Inside Functions
**ID:** ADR-UI1-014
**Location:** 80+ instances across screens/ and panels/
**Issue:** Many functions contain lazy imports (imports inside function bodies) for services and utilities.
**Impact:** Slight runtime overhead; can indicate design where module boundaries aren't clearly defined.
**Recommendation:** Most lazy imports appear intentional for deferred loading or avoiding import cycles. No action needed unless specific performance issues arise.
**Effort:** N/A (observation only)

## Top 5 Priority Issues

1. **ADR-UI1-001 (TestLabScreen God Class)** - At 1911 lines with 75 methods, this is the largest maintainability concern in the UI layer. Should be broken into focused components.

2. **ADR-UI1-007 (StrategyInputHandler Excessive Coupling)** - Accesses 15+ private scene attributes, creating tight coupling that will make future refactoring difficult.

3. **ADR-UI1-005 (Private Facade Access)** - Multiple dialogs accessing `scene._facade` breaks encapsulation; easily fixed by adding public accessor.

4. **ADR-UI1-002/003/004 (Additional God Classes)** - FleetReportWindow, BuildQueueScreen, and StrategyScreen all exceed complexity thresholds and should be decomposed.

5. **ADR-UI1-006 (Battle UI Private Method Call)** - Direct call to private method couples UI to scene internals; should use public interface or event system.

## Architecture Health Assessment

The UI layer generally follows the layered architecture correctly:
- **Layer Dependencies:** Correct (UI imports from core, simulation, strategy, ai)
- **Pygame Confinement:** Correct (no pygame outside UI)
- **Circular Dependencies:** None detected at module level (TYPE_CHECKING used appropriately)

The main concerns are internal to the UI layer:
- **God Classes:** Several screens exceed maintainability thresholds
- **Inappropriate Intimacy:** Frequent access to private attributes of collaborating objects
- **Law of Demeter Violations:** Some deep attribute chains that couple code to object structure

These issues don't break the layered architecture but reduce maintainability and testability within the UI layer itself.
