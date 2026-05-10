# Architecture Drift Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 94
- **Total Issues Found:** 9
- **Critical:** 2 | **Major:** 3 | **Minor:** 2 | **Info:** 2

## Findings

#### CRITICAL: Unauthorized AI Layer Dependencies (8 files)
**ID:** ADR-UI1-001
**Location:** `game/ui/screens/builder/main.py:724`, `game/ui/screens/builder/right_panel.py:13,114,206`, `game/ui/screens/setup_renderer.py:7,10`, `game/ui/screens/setup_screen.py`, `game/ui/screens/workshop_data_loader.py`, `game/ui/panels/ship_stats_renderer.py:12`, `game/ui/orchestration/battle_orchestrator.py`, `game/ui/screens/workshop_event_router.py`
**Issue:** 8 UI files import from game.ai.strategy_manager. UI should not depend on AI layer. StrategyManager singleton accessed for strategy names/data in dropdowns.
**Impact:** Violates layer isolation. Creates hidden dependency on AI system initialization. Makes testing UI components in isolation impossible.
**Recommendation:** Create game.strategy.facade.strategy_names_service or game.core.strategies.strategy_registry to expose strategy metadata without cross-layer coupling.
**Effort:** Medium

#### CRITICAL: UI Importing Simulation Service Internals
**ID:** ADR-UI1-002
**Location:** `game/ui/screens/strategy_screen.py:425,438`, `game/ui/screens/build_queue_screen.py`, `game/ui/panels/build_queue_controller.py`, `game/ui/services/design_loader_adapter.py`
**Issue:** 4 files import SimulationDesignLoader directly. UI couples to simulation service implementation details. TYPE_CHECKING guards insufficient for runtime coupling.
**Impact:** Blocks future simulation layer refactoring. UI directly couples to internal service.
**Recommendation:** Create game.ui.services.ship_design_service that wraps SimulationDesignLoader.
**Effort:** Medium

#### MAJOR: God Class - TestLabScreen (1837 lines, 67 methods)
**ID:** ADR-UI1-003
**Location:** `game/ui/screens/test_lab/screen.py`
**Issue:** Monolithic screen with 1837 lines and 67 methods mixing test discovery, UI layout, test execution, result visualization, metadata extraction, and JSON viewing.
**Impact:** Extremely difficult to modify or test. Hidden dependencies on test framework.
**Recommendation:** Extract TestLabController (business logic), TestLabUI (rendering), TestLabPanels (panel managers). Target <500 lines.
**Effort:** Complex

#### MAJOR: God Class - BuilderScreen (1124 lines, 44 methods)
**ID:** ADR-UI1-004
**Location:** `game/ui/screens/builder/main.py`
**Issue:** Mixed responsibilities: UI setup, ship state management, component selection, modifier application, file I/O, serialization, theme management.
**Impact:** Hard to test in isolation. High cyclomatic complexity.
**Recommendation:** Continue PROJ-44 extraction. Extract file I/O, component logic, modifier logic. Target <400 lines.
**Effort:** Complex

#### MAJOR: God Class - FormationEditorScreen (929 lines, 61 methods)
**ID:** ADR-UI1-005
**Location:** `game/ui/screens/formation_editor.py`
**Issue:** 929 lines with FormationCore + FormationEditorScreen. Tightly couples data model, rendering, input handling, file I/O. Partial extraction in progress.
**Impact:** Difficult to maintain and extend.
**Recommendation:** Further extract file I/O to FormationIO service.
**Effort:** Medium

#### MINOR: Law of Demeter Violations (27 files)
**ID:** ADR-UI1-006
**Location:** strategy_screen.py (self.scene.galaxy.X), strategy_input_handler.py, battle_screen.py (_battle_service.engine), and 24+ other files
**Issue:** Deep attribute chains (2-4 levels) in 27 files. Accessing nested objects through multiple levels.
**Impact:** Brittle refactoring. Violates encapsulation.
**Recommendation:** Create accessor properties/methods to hide internal structures.
**Effort:** Medium

#### MINOR: Strategy Data Objects in UI Layer
**ID:** ADR-UI1-007
**Location:** strategy_detail_fmt.py, strategy_renderer.py, strategy_screen.py
**Issue:** UI imports OrderType from strategy and duck-types strategy objects directly.
**Impact:** UI tight-coupled to Strategy domain model.
**Recommendation:** Move display logic to Strategy facade; pass DTOs to UI.
**Effort:** Medium

#### INFO: TYPE_CHECKING Imports Insufficient
**ID:** ADR-UI1-008
**Location:** 8+ panel files with TYPE_CHECKING Ship/Component
**Issue:** TYPE_CHECKING guards don't prevent runtime coupling to domain objects. UI panels still expect Ship/Component interfaces.
**Impact:** Acknowledged design trade-off.
**Recommendation:** Create DTOs or view models for complete decoupling.
**Effort:** Complex

#### INFO: Private Attribute Access to Session
**ID:** ADR-UI1-009
**Location:** `game/ui/screens/strategy_screen.py` (self.session._facade)
**Issue:** Accessing private _facade attribute of session object.
**Impact:** Low - works but violates encapsulation.
**Recommendation:** Expose through public property.
**Effort:** Simple

## Top 5 Priority Issues
1. **ADR-UI1-001**: AI layer coupling (8 files) - create strategy facade
2. **ADR-UI1-002**: Simulation service coupling (4 files) - wrap in UI service
3. **ADR-UI1-003**: TestLabScreen god class (1837 lines) - major decomposition needed
4. **ADR-UI1-004**: BuilderScreen god class (1124 lines) - continue extraction
5. **ADR-UI1-006**: Law of Demeter violations (27 files) - add accessor methods
