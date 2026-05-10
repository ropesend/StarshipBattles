# Architecture Drift Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 131 (106 in game/ui/screens/, 25 in game/ui/panels/)
- **Total Issues Found:** 9
- **Critical:** 0 | **Major:** 4 | **Minor:** 3 | **Info:** 2

## Findings

#### MAJOR: God Class - TestLabScreen (1906 lines, 74 methods)
**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:32-1906`
**Issue:** TestLabScreen class is exceptionally large with 74 methods and 1906 lines of code, far exceeding the 500-line/30-method threshold for god classes.
**Impact:** Difficult to test in isolation, hard to understand, and high risk of unintended coupling. Changes in one area risk breaking unrelated functionality.
**Recommendation:** Extract responsibilities into focused sub-components:
- Extract battle configuration logic into a dedicated TestBattleSetup class
- Extract UI panel management to TestLabPanelController
- Extract test execution coordination to TestLabExecutionService
**Effort:** Complex

#### MAJOR: Inappropriate Intimacy - TestLabScreen accessing BattleScene private members
**ID:** ADR-UI1-002
**Location:** `game/ui/screens/test_lab/screen.py:431-433`
**Issue:** TestLabScreen directly accesses private attributes of BattleScene (`_battle_service`, `_ai_factory`):
```python
self.game.battle_scene._battle_service.create_battle(
    ai_factory=self.game.battle_scene._ai_factory
)
```
**Impact:** Creates tight coupling between TestLabScreen and BattleScene implementation details. Changes to BattleScene's private members will break TestLabScreen.
**Recommendation:** Add public methods to BattleScene such as `ensure_battle_engine()` or `create_battle_with_factory()` that encapsulate this behavior.
**Effort:** Simple

#### MAJOR: Inappropriate Intimacy - RaceAptitudesPanel accessing private cost calculation
**ID:** ADR-UI1-003
**Location:** `game/ui/panels/race_aptitudes_panel.py:175,277`
**Issue:** RaceAptitudesPanel directly calls a private method on RacePointBudget:
```python
cost = self.point_budget._single_aptitude_cost(current_value)
```
**Impact:** UI panel is coupled to internal implementation of point budget calculation. Changes to RacePointBudget internals will break the UI.
**Recommendation:** Make `_single_aptitude_cost` a public method `get_aptitude_cost()` or expose the cost through the public interface.
**Effort:** Simple

#### MAJOR: Inappropriate Intimacy - StrategyInputHandler accessing scene private members
**ID:** ADR-UI1-004
**Location:** `game/ui/screens/strategy_input_handler.py:230-588`
**Issue:** StrategyInputHandler extensively accesses private members of StrategyScreen:
```python
self.scene._superweapons.handle_self_destruct(...)
self.scene._camera_nav.zoom_to_galaxy()
self.scene._fleet_ops.handle_move_designation(...)
self.scene._colonization.handle_colonize_designation(...)
```
**Impact:** Tight coupling between input handler and scene implementation. The input handler is essentially reaching into the scene's implementation details rather than working through a clean interface.
**Recommendation:** Either:
1. Make these subsystems public attributes (they represent distinct features, not implementation details)
2. Create a StrategySceneInterface protocol that exposes the needed operations
**Effort:** Medium

#### MINOR: Deep Attribute Chains - Law of Demeter Violations
**ID:** ADR-UI1-005
**Location:** `game/ui/screens/test_lab/screen.py:461-464`, `game/ui/screens/strategy_event_router.py:104`
**Issue:** Multiple instances of deep attribute access chains:
```python
self.game.battle_scene.camera.fit_objects(ships)
self.game.battle_scene.camera.target_zoom = self.game.battle_scene.camera.zoom
self.ui.window_manager.fleet_orders_window.handle_global_event(event)
```
**Impact:** Fragile code that breaks when intermediate objects change. Difficult to mock for testing.
**Recommendation:** Provide facade methods that encapsulate deep operations, e.g., `battle_scene.fit_camera_to_ships(ships)`.
**Effort:** Medium

#### MINOR: Late Imports to Avoid Circular Dependencies
**ID:** ADR-UI1-006
**Location:** `game/ui/screens/column_manager.py:181-224`, `game/ui/screens/fleet_report_filters.py:237-246`, `game/ui/screens/new_game_setup_screen.py:397-425`
**Issue:** Multiple intentional late imports to avoid circular dependencies:
```python
# INTENTIONAL LATE IMPORT: Avoid circular import with strategy services
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
```
**Impact:** While these are legitimate workarounds, they indicate an underlying design issue where module responsibilities are not cleanly separated. The need for circular import avoidance suggests coupling that could be improved.
**Recommendation:** Long-term, consider refactoring to eliminate the need for late imports by:
1. Moving shared types to a common module
2. Using dependency injection
3. Restructuring module boundaries
**Effort:** Complex

#### MINOR: Builder accessing Ship internals through deep chains
**ID:** ADR-UI1-007
**Location:** `game/ui/screens/builder/left_panel.py:267-309`, `game/ui/screens/builder/layer_panel.py:316-508`
**Issue:** Builder panels reach deeply into ship structure:
```python
current_ship_layers = [l.name for l in self.builder.ship.layers.keys()]
for l_type, layers in self.builder.ship.layers.items():
```
**Impact:** UI code is tightly coupled to Ship's internal layer representation.
**Recommendation:** Create a ShipViewModel or ShipAdapter that provides UI-friendly access to ship data without exposing internal structures.
**Effort:** Medium

#### INFO: Large Screen Files Approaching God Class Threshold
**ID:** ADR-UI1-008
**Location:** Multiple files
**Issue:** Several screen files are large and approaching god class size:
- `build_queue_screen.py`: 1098 lines, 31 methods
- `fleet_report_window.py`: 1093 lines, 29 methods
- `builder/weapons_panel.py`: 1037 lines
- `race_setup_screen.py`: 946 lines, 32 methods
- `formation_editor.py`: 934 lines
- `test_lab/test_run_details.py`: 893 lines
- `strategy_input_handler.py`: 881 lines
- `empire_build_queue_window.py`: 863 lines
- `strategy_screen.py`: 819 lines, 46 methods
**Impact:** While not yet god classes, these files are at risk of becoming difficult to maintain.
**Recommendation:** Monitor these files and consider extraction when functionality is added.
**Effort:** N/A (informational)

#### INFO: Test Framework Coupling in UI Layer
**ID:** ADR-UI1-009
**Location:** `game/ui/screens/test_lab/*.py`, `game/ui/screens/battle_screen.py:456`
**Issue:** The test_lab screen module imports from test_framework and simulation_tests packages:
```python
from test_framework.registry import TestRegistry
from test_framework.test_history import TestHistory
from simulation_tests.logging_config import get_logger
```
**Impact:** This is architecturally appropriate since test_lab is a development/testing UI feature. However, it creates a dependency that means the test_lab UI cannot be used if test_framework is not installed.
**Recommendation:** This is acceptable for a development tool. If test_lab is intended for end-user use, consider making test_framework imports optional with graceful degradation.
**Effort:** N/A (acceptable for development tooling)

## Top 5 Priority Issues

1. **ADR-UI1-001 (MAJOR)**: TestLabScreen god class - 1906 lines, 74 methods. The largest single file in the UI layer, significantly impacting maintainability and testability.

2. **ADR-UI1-002 (MAJOR)**: TestLabScreen accessing BattleScene._battle_service and _ai_factory. Direct private attribute access creates fragile coupling.

3. **ADR-UI1-004 (MAJOR)**: StrategyInputHandler accessing multiple scene private members. Pervasive pattern throughout the input handler.

4. **ADR-UI1-003 (MAJOR)**: RaceAptitudesPanel calling _single_aptitude_cost private method. Simple fix by making the method public.

5. **ADR-UI1-006 (MINOR)**: Late imports to avoid circular dependencies. Indicates underlying architectural boundaries that could be cleaner.

## Notes

- **No Layer Violations Found**: All imports in game/ui/screens/ and game/ui/panels/ correctly respect the layer hierarchy. UI properly imports from core, simulation, strategy, and ai layers.
- **No Pygame Boundary Violations**: Pygame usage is appropriately contained within the UI layer.
- **No Circular Dependencies Detected**: While late imports exist to avoid potential circulars, no actual circular import chains were found.
- **TYPE_CHECKING Usage**: Properly used throughout for type hints without runtime imports.
