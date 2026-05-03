# Module Review: game/ui/

**Module Specialist:** MOD-UI
**Review Date:** 2026-02-23
**Scope:** Screen architecture, rendering patterns, event handling, component reuse, cross-layer imports

---

## Summary

**Total Findings:** 24
**Severity Distribution:**
- Critical: 5
- Major: 10
- Minor: 6
- Info: 3

**Overall Module Health Rating: 6.5/10 (Good with room for improvement)**

**Strengths:**
- Extensive refactoring already completed (PROJ-86, PROJ-88, PROJ-89 decompositions)
- Good use of centralized config constants (UIConfig, builder_utils.py)
- Clean separation of concerns in many areas (renderer/input handler extraction)
- IScene protocol adoption for standardized screen lifecycle
- Event bus pattern for decoupled communication
- Dependency injection patterns emerging (DesignLoaderAdapter, ShipIOAdapter)

**Weaknesses:**
- Several remaining god classes (>1000 lines)
- Heavy cross-layer imports (acceptable for UI but numerous)
- Inconsistent magic number management
- Some error handling gaps
- Mixed rendering patterns (pygame_gui vs manual drawing)

---

## Findings

### MOD-UI-001: God Class - TestLabScreen (1,906 lines)
**Severity:** Critical
**File:** `game/ui/screens/test_lab/screen.py`
**Deliberate:** No - Clear technical debt

**Description:**
Largest file in the UI module. While some helpers extracted (panel_manager, validation_manager, test_executor), main screen class still handles UI layout, test execution orchestration, category management, test history, validation workflows, JSON viewing, and event routing.

**Recommendation:**
Extract test execution to TestExecutor, create TestCategoryManager, extract layout to TestLabLayout helper.

---

### MOD-UI-002: God Class - FleetReportWindow (1,108 lines)
**Severity:** Critical
**File:** `game/ui/screens/fleet_report_window.py`

**Description:**
Handles three-panel layout, ship filtering/sorting, column management, image caching, multi-select state, ship detail rendering, scrolling/pagination. Already has good extractions (FleetListViewModel, ColumnManager) but still very large.

**Recommendation:**
Extract ship list rendering to FleetListRenderer, sidebar to FleetSummaryPanel, image caching to ImageCache utility.

---

### MOD-UI-003: God Class - BuildQueueScreen (1,084 lines)
**Severity:** Critical
**File:** `game/ui/screens/build_queue_screen.py`

**Description:**
Three-column layout with extractions already done (BuildQueueController, BuildQueueDragHandler, BuildQueuePortraitLoader, BuildQueueSelector). Still handles layout, rendering, event routing, and integration.

**Recommendation:**
Extract layout calculations to BuildQueueLayout helper. Consider splitting into mode-specific screens.

---

### MOD-UI-004: God Class - WeaponsReportPanel (1,037 lines)
**Severity:** Critical
**File:** `game/ui/screens/builder/weapons_panel.py`

**Description:**
Complex weapons visualization with 100+ layout constants, range bar rendering, hit probability gradients, damage falloff visualization, interactive tooltips, target stats integration, multiple drawing modes.

**Deliberate:** Partially - Weapon visualization is inherently complex, but size suggests opportunities.

**Recommendation:**
Extract range bar rendering to WeaponRangeBarRenderer, gradient/color logic to WeaponColorScheme, tooltip to WeaponTooltipRenderer.

---

### MOD-UI-005: God Class - RaceSetupScreen (946 lines)
**Severity:** Major
**File:** `game/ui/screens/race_setup_screen.py`

**Description:**
7-tab wizard for race configuration. Already has good extractions (panels, validator, asset loader) but coordinator is still large.

**Recommendation:**
Extract tab navigation to RaceSetupTabController, validation feedback to RaceValidationDisplay.

---

### MOD-UI-006: Heavy Cross-Layer Imports
**Severity:** Major
**Files:** Multiple (100+ imports from simulation/strategy)
**Deliberate:** Yes - UI layer expected to import domain layers

**Description:**
Extensive imports from game.simulation and game.strategy. Comments explicitly mark these as "acceptable for UI". Architecturally sound since UI is the top layer, but creates coupling and testing difficulty.

**Recommendation:**
Continue TYPE_CHECKING guards. Expand facade pattern for complex domain interactions. Ensure domain layers NEVER import from UI.

---

### MOD-UI-007: Inconsistent Magic Number Management
**Severity:** Major
**Files:** Multiple screens with inline magic numbers

**Description:**
While UIConfig and builder_utils.py provide centralized constants, many screens still use inline magic numbers. Some use class-level constants (good), others use inline literals (bad), centralized config is underutilized.

**Recommendation:**
Audit all screen layouts. Move to class-level or config modules. Use UIConfig for common values.

---

### MOD-UI-008: Mixed Rendering Approaches
**Severity:** Major
**Pattern:** Screens use both pygame_gui and manual pygame drawing

**Description:**
Some screens use pygame_gui (UIPanel, UIButton), others do manual screen.blit() and pygame.draw calls. 919 pygame.Rect occurrences, extensive manual rendering in strategy_renderer, formation_editor, schematic_view, weapons_panel.

**Deliberate:** Partially - Complex custom visualizations need manual rendering.

**Recommendation:**
Document when to use pygame_gui vs manual rendering. Extract common manual rendering patterns to utility functions.

---

### MOD-UI-009: Singleton Pattern Usage in Asset Managers
**Severity:** Major
**Files:** `assets/ship_theme_manager.py`, `services/screenshot_manager.py`, `renderer/sprites.py`

**Description:**
Three classes use SingletonMeta. Thread-safety overhead may be unnecessary for single-threaded UI.

**Recommendation:**
Consider dependency injection instead. If singletons kept, add reset() methods for test isolation.

---

### MOD-UI-010: Limited Error Handling in UI Code
**Severity:** Major
**Pattern:** Only 128 error handling occurrences across 27 files

**Description:**
Many screens lack comprehensive error handling for file I/O, asset loading failures, simulation timeouts, invalid user input. Good examples exist in builder/event_bus.py and workshop_ship_io.py.

**Recommendation:**
Add try-except around file I/O, asset loading, cross-layer calls. Display user-friendly error messages.

---

### MOD-UI-011: EventBus Pattern Underutilized
**Severity:** Minor
**File:** `screens/builder/event_bus.py`

**Description:**
Only builder/workshop screens use EventBus for decoupled communication. Other screens use direct method calls and callbacks.

**Recommendation:**
Consider expanding EventBus to strategy, test_lab screens for better testability.

---

### MOD-UI-012: FormationEditor Complexity (941 lines)
**Severity:** Major
**File:** `game/ui/screens/formation_editor.py`

**Description:**
Already has good extraction of input handler (422 lines) and renderer (427 lines), but main class still large with FormationCore data model, Tkinter file dialog integration, multi-select operations.

**Recommendation:**
Extract FormationCore to separate module. Extract file I/O to FormationSerializer.

---

### MOD-UI-013: StrategyInputHandler Event Routing Complexity (898 lines)
**Severity:** Major
**File:** `game/ui/screens/strategy_input_handler.py`

**Description:**
Handles all strategy screen input with InputMapper integration, multiple input modes (SELECT, MOVE, JOIN, COLONIZE_TARGET, etc.), fleet/superweapon/UI action routing.

**Recommendation:**
Extract input mode state machine, fleet command routing, mouse click routing to separate classes.

---

### MOD-UI-014: EmpireBuildQueueWindow Complexity (863 lines)
**Severity:** Major
**File:** `game/ui/screens/empire_build_queue_window.py`

**Description:**
Empire-wide build queue with multi-column display, filtering (via EmpireBuildQueueFilterManager), sorting, queue item aggregation, production time calculations.

**Recommendation:**
Extract rendering and aggregation to separate classes.

---

### MOD-UI-015: StrategyRenderer Complexity (764 lines)
**Severity:** Major
**File:** `game/ui/screens/strategy_renderer.py`
**Deliberate:** Yes - Already extracted from StrategyScreen

**Description:**
Handles all galaxy map rendering: hex grid, warp lanes, system/planet icons, fleet rendering, hover highlights, animations. Current size acceptable for dedicated renderer.

**Recommendation:**
Consider further extraction only if specific areas grow significantly.

---

### MOD-UI-016: Missing IScene Protocol Coverage
**Severity:** Minor
**Deliberate:** Yes - Windows/dialogs use pygame_gui lifecycle

**Description:**
Not all screens implement IScene protocol. Main scenes do (BattleScreen, StrategyScreen, TestLabScreen, etc.) but windows and dialogs don't.

**Recommendation:**
Document which screens should implement IScene. Consider IWindow protocol for common window patterns.

---

### MOD-UI-017: Inconsistent Constructor Complexity
**Severity:** Minor
**Description:**
Some `__init__` methods have 10+ parameters as dependency injection grows. BuildQueueScreen has 11 parameters.

**Recommendation:**
Group related parameters into config objects or use builder pattern.

---

### MOD-UI-018: BattleStateViewer Complexity (687 lines)
**Severity:** Major
**File:** `game/ui/screens/battle_state_viewer.py`

**Description:**
JSON viewer for battle state inspection. Specialized debug tool.

**Recommendation:**
Extract JSONTreeRenderer and JSONNavigator if used frequently.

---

### MOD-UI-019: UIConfig Underutilization
**Severity:** Minor
**File:** `game/ui/config.py`

**Description:**
UIConfig has only 66 lines with 20+ constants. Room for expansion. Many screens still use local constants.

**Recommendation:**
Expand UIConfig. Consider splitting into domain-specific configs (BattleUIConfig, StrategyUIConfig).

---

### MOD-UI-020: WorkshopScreen Complexity (613 lines)
**Severity:** Major
**File:** `game/ui/screens/workshop_screen.py`
**Deliberate:** Yes - Already heavily refactored with clean MVVM separations (PROJ-38, PROJ-61)

**Description:**
Ship design workshop with WorkshopViewModel, WorkshopEventRouter, WorkshopShipIO, WorkshopDataReloader, multiple panels. Current architecture is good.

**Recommendation:**
Monitor panel initialization logic for further extraction opportunities.

---

### MOD-UI-021: Panel Classes Mixed Between panels/ and screens/
**Severity:** Minor
**Description:**
28 files in game/ui/panels/, some panels also in game/ui/screens/. Not clear when panel goes in panels/ vs screens/.

**Recommendation:**
Establish guideline: panels/ for reusable, screens/ for screen-specific.

---

### MOD-UI-022: Good Pattern - Extract-Refactor Documentation
**Severity:** Info (Positive)
**Description:**
Many files have PROJ-XX comments documenting extraction history. Continue this pattern.

---

### MOD-UI-023: Good Pattern - Centralized Builder Constants
**Severity:** Info (Positive)
**File:** `game/ui/screens/builder_utils.py`
**Description:**
Excellent example of centralized layout constants using frozen dataclasses. Use as template for other screens.

---

### MOD-UI-024: Test Coverage Gap for UI Module
**Severity:** Info
**Description:**
UI module likely has lower test coverage due to Pygame dependencies. No unit tests for most screen classes.

**Recommendation:**
Focus testing on extracted business logic (controllers, validators, formatters). Consider visual regression testing.

---

## Top 5 Priority Issues

1. **MOD-UI-001 (Critical):** TestLabScreen 1,906 lines — largest file, high maintenance burden
2. **MOD-UI-004 (Critical):** WeaponsReportPanel 1,037 lines — overly complex visualization
3. **MOD-UI-007 (Major):** Inconsistent magic number management — layout adjustments error-prone
4. **MOD-UI-010 (Major):** Limited error handling — crashes from unhandled exceptions
5. **MOD-UI-006 (Major):** Heavy cross-layer imports — testing difficulty, change risk
