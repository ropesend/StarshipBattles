# Architecture Drift Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens (game/ui/screens/, game/ui/panels/)
- **Files Scanned:** 134 (109 in screens + 25 in panels)
- **Total Issues Found:** 18
- **Critical:** 2 | **Major:** 8 | **Minor:** 5 | **Info:** 3

## Findings

#### CRITICAL: Test Framework Coupling in Production UI Code
**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:16-18, 80, 483`
**Issue:** The test_lab module imports directly from test_framework and simulation_tests packages, creating a hard coupling between production UI code and test infrastructure.
**Impact:** This coupling means the test framework must be installed for the UI to function. It also mixes test-specific concerns with UI rendering, making the test_lab difficult to reuse or maintain separately.
**Recommendation:** Extract test execution logic into an adapter interface that the UI depends on. The test_framework should implement this interface, allowing the UI to work independently.
**Effort:** Medium

```python
from test_framework.registry import TestRegistry
from test_framework.test_history import TestHistory
from simulation_tests.logging_config import get_logger
```

#### CRITICAL: Test Framework Import in Battle Screen
**ID:** ADR-UI1-002
**Location:** `game/ui/screens/battle_screen.py:451-453`
**Issue:** Battle screen conditionally imports test_framework.runner.TestRunner at runtime and accesses private methods (`runner._log_test_execution`).
**Impact:** Production battle screen code depends on test infrastructure. This creates an implicit circular dependency: tests depend on battle_screen, and battle_screen depends on test_framework.
**Recommendation:** Remove test logging from BattleScreen entirely. If test execution logging is needed, it should be injected via callback or handled externally by the test framework.
**Effort:** Simple

```python
from test_framework.runner import TestRunner
runner._log_test_execution(self.test_scenario, headless=False)
```

---

#### MAJOR: God Class - TestLabScreen (1908 lines, 75 methods)
**ID:** ADR-UI1-003
**Location:** `game/ui/screens/test_lab/screen.py`
**Issue:** TestLabScreen is 1908 lines with 75 methods in a single class, far exceeding reasonable class size limits (500 lines, 30 methods).
**Impact:** The class is difficult to understand, test, and maintain. Changes in one area risk breaking unrelated functionality.
**Recommendation:** Continue decomposition - extract remaining logic into PanelManager, ExecutionManager, and EventRouter components.
**Effort:** Complex

#### MAJOR: God Class - StrategyScreen (811 lines, 45 methods)
**ID:** ADR-UI1-004
**Location:** `game/ui/screens/strategy_screen.py`
**Issue:** StrategyScreen has 45 methods - many of which delegate to helper classes (FleetOperations, ColonizationSystem, etc.) but the coordination logic is still too concentrated.
**Impact:** The screen acts as a "god coordinator" with too much knowledge of subsystem internals.
**Recommendation:** Consider introducing a StrategyScreenController to handle high-level coordination, keeping StrategyScreen focused on rendering and event routing.
**Effort:** Medium

#### MAJOR: God Class - BuilderMain (1121 lines, 44 methods)
**ID:** ADR-UI1-005
**Location:** `game/ui/screens/builder/main.py`
**Issue:** The ship builder main screen has 44 methods and over 1100 lines despite having multiple helper classes.
**Impact:** Complex initialization logic, difficulty testing individual features, and risk of introducing bugs when making changes.
**Recommendation:** Split panel initialization into a dedicated BuilderLayout class. Move event handling to BuilderEventRouter (already has EventBus, but not fully utilized).
**Effort:** Medium

#### MAJOR: God Class - BuildQueueScreen (1098 lines, 31 methods)
**ID:** ADR-UI1-006
**Location:** `game/ui/screens/build_queue_screen.py`
**Issue:** BuildQueueScreen exceeds 1000 lines with complex queue management logic mixed with UI rendering.
**Impact:** Difficult to test queue logic independently of UI. Changes to display code risk breaking queue operations.
**Recommendation:** Extract BuildQueueLogic to handle queue mutations, keeping screen focused on presentation.
**Effort:** Medium

#### MAJOR: Circular Dependency Workarounds (Late Imports)
**ID:** ADR-UI1-007
**Location:** `game/ui/screens/column_manager.py:181-224`, `game/ui/screens/fleet_report_filters.py:238-260`
**Issue:** Multiple intentional late imports to avoid circular imports with strategy services:
- FleetSpeedCalculator
- ShipStatsCalculator
- FleetCapabilityCalculator
**Impact:** Late imports indicate design tension between UI and strategy layers. The UI needs calculation logic that lives in strategy, but importing at module level causes cycles.
**Recommendation:** Create a ShipQueryService facade in game/ui/services/ that wraps all ship stat calculations needed by UI. Import this service instead.
**Effort:** Medium

```python
# INTENTIONAL LATE IMPORT: Avoid circular import with strategy services
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
```

#### MAJOR: Private Attribute Access - StrategyEventRouter
**ID:** ADR-UI1-008
**Location:** `game/ui/screens/strategy_event_router.py:60, 100, 103-104, 227-242`
**Issue:** StrategyEventRouter extensively accesses private methods on StrategyUI._window_manager:
- `self.ui._window_manager`
- `wm._on_empire_build_queue_closed()`
- `wm._on_event_log_closed()`
- `wm._on_empire_panel_closed()`
**Impact:** Tight coupling between router and window manager internals. Changes to WindowManager private methods will break the router.
**Recommendation:** Add public methods to WindowManager for closing notifications, or use a proper event/callback system.
**Effort:** Simple

#### MAJOR: Private Attribute Access - WorkshopEventRouter
**ID:** ADR-UI1-009
**Location:** `game/ui/screens/workshop_event_router.py:351-470`
**Issue:** WorkshopEventRouter calls private methods on gui object:
- `gui._save_ship()`
- `gui._load_ship()`
- `gui._show_clear_confirmation()`
- `gui._execute_pending_action()`
**Impact:** Event router depends on internal implementation details of WorkshopScreen.
**Recommendation:** Create a WorkshopActions protocol/interface with public methods that the router can call.
**Effort:** Simple

#### MAJOR: Direct ViewModel State Mutation
**ID:** ADR-UI1-010
**Location:** `game/ui/screens/workshop_screen.py:311, 361`, `game/ui/screens/workshop_data_reloader.py:182`
**Issue:** External code directly mutates private viewmodel state:
- `self.viewmodel._selected_components = new_list`
- `self.viewmodel._selected_components = value`
**Impact:** Bypasses any validation or change notifications in the viewmodel. Can lead to inconsistent state.
**Recommendation:** Add proper setter methods to WorkshopViewModel with validation.
**Effort:** Simple

---

#### MINOR: Simulation Layer TYPE_CHECKING Imports
**ID:** ADR-UI1-011
**Location:** Multiple files (see details below)
**Issue:** UI panels import simulation layer types for type hints:
- `component_modifier_grid_panel.py`: Component
- `modifier_impact_grid.py`: Component
- `design_report_panel.py`: Ship
- `design_stats_panel.py`: Ship
- `ship_stats_renderer.py`: ComponentStatus (runtime import)
**Impact:** While TYPE_CHECKING imports don't create runtime dependencies, they indicate architectural awareness that the UI "knows" about simulation internals.
**Recommendation:** Consider whether these could use protocols instead of concrete types. For ship_stats_renderer.py (runtime import), evaluate if ComponentStatus could be moved to core.
**Effort:** Simple

#### MINOR: Planet Filter Cached Attributes
**ID:** ADR-UI1-012
**Location:** `game/ui/screens/planet_list_filters.py:26-35, 61-89`
**Issue:** Filter code adds temporary attributes to Planet objects (`_temp_system_ref`, `_cached_gravity_g`, etc.) rather than using a separate data structure.
**Impact:** Mutates domain objects with UI-specific cached data. These private attributes could conflict with future Planet implementations.
**Recommendation:** Use a PlanetDisplayData wrapper class or dictionary keyed by planet ID to store cached display values.
**Effort:** Simple

#### MINOR: Strategy Renderer Temporary Attributes
**ID:** ADR-UI1-013
**Location:** `game/ui/screens/strategy_renderer.py:446-454`
**Issue:** Renderer adds temporary screen position attributes to Planet objects:
- `p._temp_screen_pos`
- `p._temp_draw_r`
**Impact:** Domain objects carry UI-specific rendering state.
**Recommendation:** Use a separate rendering cache dictionary keyed by object ID.
**Effort:** Simple

#### MINOR: FleetCapabilityCalculator Private Method Access
**ID:** ADR-UI1-014
**Location:** `game/ui/screens/column_manager.py:227`, `game/ui/screens/fleet_report_filters.py:164, 260`
**Issue:** UI code calls private method `FleetCapabilityCalculator._ship_has_ability()`.
**Impact:** Depends on implementation details that could change.
**Recommendation:** Make `ship_has_ability()` a public method or provide a public query interface.
**Effort:** Simple

#### MINOR: InputMapper Private Method Access
**ID:** ADR-UI1-015
**Location:** `game/ui/screens/keybindings_scene.py:324`
**Issue:** Calls `InputMapper._extract_modifiers(event.mod)` - a private method.
**Impact:** Couples keybinding UI to InputMapper internals.
**Recommendation:** Add public `extract_modifiers()` method to InputMapper.
**Effort:** Simple

---

#### INFO: Test Lab Executor Private Field Access
**ID:** ADR-UI1-016
**Location:** `game/ui/screens/test_lab/test_executor.py:181-182, 327`
**Issue:** Sets private `scenario._override_seed` attribute directly.
**Impact:** Test scenarios need to expose seed override capability properly.
**Recommendation:** Add `set_seed_override()` method to scenario interface.
**Effort:** Simple

#### INFO: Deep Object Chain in StrategyUI
**ID:** ADR-UI1-017
**Location:** `game/ui/screens/strategy_ui.py:248, 257, 276`
**Issue:** Methods delegate to private methods through chains:
- `self._detail_formatter._get_label_for_obj(obj)`
- `self._detail_formatter._format_spectrum(star)`
**Impact:** Minor Law of Demeter violation, but these are delegating to a helper class which is acceptable.
**Recommendation:** Consider making delegated methods public on the formatter.
**Effort:** Simple

#### INFO: Large Method Counts in UI Screens
**ID:** ADR-UI1-018
**Location:** Multiple screens (see summary)
**Issue:** Several screens have high method counts indicating they may need further decomposition:
- `workshop_viewmodel.py`: 36 methods
- `strategy_input_handler.py`: 35 methods
- `race_setup_screen.py`: 32 methods
- `formation_editor.py`: 61 methods (2 classes)
**Impact:** These are within reasonable limits but worth monitoring as they grow.
**Recommendation:** Monitor and extract helpers when methods exceed 40 per class.
**Effort:** N/A (monitoring)

## Top 5 Priority Issues

1. **ADR-UI1-001/002 - Test Framework Coupling** (CRITICAL): Production UI code depends on test infrastructure. This violates separation of concerns and creates deployment challenges.

2. **ADR-UI1-003 - TestLabScreen God Class** (MAJOR): At 1908 lines with 75 methods, this class is extremely difficult to maintain and needs urgent decomposition.

3. **ADR-UI1-007 - Circular Dependency Workarounds** (MAJOR): Late imports indicate structural problems in how UI accesses strategy layer calculations. A proper facade would eliminate these.

4. **ADR-UI1-008/009 - Private Attribute Access in Event Routers** (MAJOR): Event routers depend on internal implementation details. Adding proper public interfaces would improve maintainability.

5. **ADR-UI1-010 - Direct ViewModel State Mutation** (MAJOR): External code bypassing viewmodel encapsulation can lead to state inconsistencies.
