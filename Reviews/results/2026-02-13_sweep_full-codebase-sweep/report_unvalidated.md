# Review Report: 2026-02-13_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-13
- **Type:** Review
- **Description:** 
- **Agents Used:** 23

## Executive Summary
- **Total Findings:** 288
- **Critical:** 17 | **Major:** 102 | **Minor:** 125 | **Info:** 44
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Research UI Layer Imports Concrete Camera from game.ui
**ID:** ADR-FND-001
**Agent:** Architecture Foundation
**Location:** `game/research/ui/research_scene.py:19`
**Effort:** Medium

**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:19`
**Issue:** The research scene imports the concrete Camera class from `game.ui.renderer.camera`, creating a direct dependency from the research layer to the UI layer.
**Code:**
```python
from game.ui.renderer.camera import Camera
```
**Impact:**
- The research layer cannot be tested without the full UI layer loaded
- Creates a coupling that violates the architectural intent for research to be a standalone module
- If Camera...

---

### 2. CRITICAL: AI Layer Imports in Simulation Factory
**ID:** ADR-SIM-001
**Agent:** Architecture Simulation
**Location:** `game/simulation/factories/ai_factory.py:56-58`
**Effort:** Medium

**ID:** ADR-SIM-001
**Location:** `game/simulation/factories/ai_factory.py:56-58`
**Issue:** The simulation layer directly imports and instantiates classes from the AI layer (`game.ai.controller.AIController`, `game.ai.interfaces.ShipControllableAdapter`). According to architecture rules, simulation should only depend on core, not on ai.
**Import Lines:**
```python
from game.ai.controller import AIController
from game.ai.interfaces import ShipControllableAdapter
```
**Impact:**
- Breaks layer is...

---

### 3. CRITICAL: Test Framework Coupling in Production UI Code
**ID:** ADR-UI1-001
**Agent:** Architecture Ui Screens
**Location:** `game/ui/screens/test_lab/screen.py:16-18, 80, 483`
**Effort:** Medium

**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:16-18, 80, 483`
**Issue:** The test_lab module imports directly from test_framework and simulation_tests packages, creating a hard coupling between production UI code and test infrastructure.
**Impact:** This coupling means the test framework must be installed for the UI to function. It also mixes test-specific concerns with UI rendering, making the test_lab difficult to reuse or maintain separately.
**Recommendation:** Extrac...

---

### 4. CRITICAL: Test Framework Import in Battle Screen
**ID:** ADR-UI1-002
**Agent:** Architecture Ui Screens
**Location:** `game/ui/screens/battle_screen.py:451-453`
**Effort:** Simple

**ID:** ADR-UI1-002
**Location:** `game/ui/screens/battle_screen.py:451-453`
**Issue:** Battle screen conditionally imports test_framework.runner.TestRunner at runtime and accesses private methods (`runner._log_test_execution`).
**Impact:** Production battle screen code depends on test infrastructure. This creates an implicit circular dependency: tests depend on battle_screen, and battle_screen depends on test_framework.
**Recommendation:** Remove test logging from BattleScreen entirely. If test...

---

### 5. CRITICAL: Inconsistent Singleton Pattern Usage - SingletonMeta vs Module-Level Globals
**ID:** CON-FND-001
**Agent:** Consistency Foundation
**Location:** `game/core/registry.py:79-120`
**Effort:** Medium

**ID:** CON-FND-001
**Location:** `game/core/registry.py:79-120`, `game/core/registry.py:379-398`
**Issue:** The codebase uses two incompatible singleton patterns side-by-side. `RegistryManager` uses `SingletonMeta`, but `_default_registries` and `_default_provider` use module-level global variables with manual getter/setter functions. This creates confusion about which pattern is authoritative and risks inconsistent state management.
**Impact:** Developers must understand both patterns; potenti...

---

### 6. CRITICAL: ResourceRegistry Return Type Inconsistency for Not-Found Cases
**ID:** CON-SIM-001
**Agent:** Consistency Simulation
**Location:** `game/simulation/systems/resource_manager.py:120-131`
**Effort:** Simple

**ID:** CON-SIM-001
**Location:** `game/simulation/systems/resource_manager.py:120-131`
**Issue:** `get_resource()` returns `Optional[ResourceState]` (None if not found), while `get_value()` and `get_max_value()` return `0.0` if resource not found. The class docstring documents "Optional[T] (None = not found)" for single-value lookups, but `get_value()` violates this by returning 0.0 - masking the difference between "resource doesn't exist" and "resource has zero value".
**Impact:** Bugs where c...

---

### 7. CRITICAL: ID-Based Expansion Tracking Pattern Duplicated in Battle Panels
**ID:** UNK-01
**Agent:** Duplication Ui Screens
**Location:** `Unknown`
**Effort:** Unknown

**Files:**
- `C:\Dev\Starship Battles\game\ui\panels\battle_panels.py` (lines 59-86, 263-286)

**Description:**
`ShipStatsPanel` and `SeekerMonitorPanel` both implement nearly identical ID-based expansion state tracking patterns:

```python
# ShipStatsPanel (lines 59-86)
def _get_ship_id(self, ship):
    ship_id = getattr(ship, 'id', None)
    if isinstance(ship_id, str):
        return ship_id
    ship_name = getattr(ship, 'name', None)
    if isinstance(ship_name, str):
        return ship_nam...

---

### 8. CRITICAL: Multi-Select Row Click Handling Duplicated Across Windows
**ID:** UNK-02
**Agent:** Duplication Ui Screens
**Location:** `Unknown`
**Effort:** Unknown

**Files:**
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (lines 883-928)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (lines 304-337)

**Description:**
Both windows implement nearly identical Ctrl+click multi-select logic:

```python
# FleetReportWindow._handle_row_click (lines 883-928)
mods = pygame.key.get_mods()
ctrl_held = bool(mods & pygame.KMOD_CTRL)

if ctrl_held:
    if ship_index in self.selected_indices:
        if len(self.selected_indi...

---

### 9. CRITICAL: CollisionSystem raycasting edge cases untested
**ID:** TCG-FND-001
**Agent:** Test Coverage Foundation
**Location:** `game/engine/collision.py`
**Effort:** Medium

**ID:** TCG-FND-001
**Location:** `game/engine/collision.py` (production) / `tests/unit/systems/test_collision_system.py` (partial coverage)
**Issue:** While `test_collision_system.py` exists and tests basic beam hit/miss scenarios, the following critical edge cases are not tested:
- Division by zero when direction vector has length 0 (`a == 0` guard at line 87-88)
- Tangent hits where discriminant equals exactly 0 (edge of sphere)
- Multiple valid intersection points (entry and exit) - test onl...

---

### 10. CRITICAL: ResearchService leaky bucket algorithm edge cases untested
**ID:** TCG-FND-002
**Agent:** Test Coverage Foundation
**Location:** `game/research/systems/research_service.py`
**Effort:** Medium

**ID:** TCG-FND-002
**Location:** `game/research/systems/research_service.py` (production) / `tests/unit/research/test_research_service.py` (partial)
**Issue:** The stochastic research system has critical edge cases that are not explicitly tested:
- Roll exactly at the breakthrough threshold (roll == current_chance)
- MAX_CHANCE cap behavior when chance accumulates past 95%
- Decay applied to locked nodes with accumulated chance (lines 77-91)
- Price curve calculations with level=0 input
- `tech...

---


## Findings by Severity

### Critical (17)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Research UI Layer Imports Concrete Camer | `game/research/ui/research_scen` | Medium |
| ADR-SIM-001 | AI Layer Imports in Simulation Factory | `game/simulation/factories/ai_f` | Medium |
| ADR-UI1-001 | Test Framework Coupling in Production UI | `game/ui/screens/test_lab/scree` | Medium |
| ADR-UI1-002 | Test Framework Import in Battle Screen | `game/ui/screens/battle_screen.` | Simple |
| CON-FND-001 | Inconsistent Singleton Pattern Usage - S | `game/core/registry.py:79-120` | Medium |
| CON-SIM-001 | ResourceRegistry Return Type Inconsisten | `game/simulation/systems/resour` | Simple |
| UNK-01 | ID-Based Expansion Tracking Pattern Dupl | `Unknown` | Unknown |
| UNK-02 | Multi-Select Row Click Handling Duplicat | `Unknown` | Unknown |
| TCG-FND-001 | CollisionSystem raycasting edge cases un | `game/engine/collision.py` | Medium |
| TCG-FND-002 | ResearchService leaky bucket algorithm e | `game/research/systems/research` | Medium |
| TCG-SIM-001 | No Unit Tests for ship_stats.py (ShipSta | `game/simulation/entities/ship_` | Complex |
| TCG-SIM-002 | No Unit Tests for ship_stat_querier.py | `game/simulation/entities/ship_` | Medium |
| TCG-SIM-003 | No Unit Tests for ship_validator_helper. | `game/simulation/entities/ship_` | Simple |
| TCG-STR-001 | No dedicated tests for game/strategy/dat | `game/strategy/data/naming.py` | Simple |
| TCG-STR-002 | No dedicated tests for game/strategy/dat | `game/strategy/data/physics.py` | Medium |
| TCG-UI1-001 | BattleStateViewer has no unit tests | `game/ui/screens/battle_state_v` | Medium |
| TCG-UI1-002 | TestLabValidationManager has no unit tes | `game/ui/screens/test_lab/valid` | Complex |

### Major (102)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-002 | protocols.py is Approaching God Class Te | `game/core/protocols.py` | Medium |
| ADR-SIM-002 | TYPE_CHECKING Import of AI Controller | `game/simulation/systems/battle` | Simple |
| ADR-SIM-003 | God Class - BattleController | `game/simulation/battle_control` | Complex |
| ADR-SIM-004 | God Class - Ship Entity | `game/simulation/entities/ship.` | Complex |
| ADR-SIM-005 | Documented Circular Import in Ship.add_c | `game/simulation/entities/ship.` | Medium |
| ADR-UI2-001 | pygame.math.Vector2 Usage in game_render | `game/ui/renderer/game_renderer` | Simple |
| ADR-UI2-002 | God Class Potential in ShipThemeManager | `game/ui/assets/ship_theme_mana` | Medium |
| ADR-UI1-003 | God Class - TestLabScreen (1908 lines, 7 | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-004 | God Class - StrategyScreen (811 lines, 4 | `game/ui/screens/strategy_scree` | Medium |
| ADR-UI1-005 | God Class - BuilderMain (1121 lines, 44  | `game/ui/screens/builder/main.p` | Medium |
| ADR-UI1-006 | God Class - BuildQueueScreen (1098 lines | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-007 | Circular Dependency Workarounds (Late Im | `game/ui/screens/column_manager` | Medium |
| ADR-UI1-008 | Private Attribute Access - StrategyEvent | `game/ui/screens/strategy_event` | Simple |
| ADR-UI1-009 | Private Attribute Access - WorkshopEvent | `game/ui/screens/workshop_event` | Simple |
| ADR-UI1-010 | Direct ViewModel State Mutation | `game/ui/screens/workshop_scree` | Simple |
| CON-FND-002 | Inconsistent Logging Pattern - Logger Si | `game/core/logger.py` | Medium |
| CON-FND-003 | Mixed Return Semantics for Not-Found Cas | `game/core/registry.py:98-120` | Simple |
| CON-FND-004 | Inconsistent Method Naming for Position/ | `game/ai/interfaces/controllabl` | Complex |
| CON-FND-005 | Class Naming Suffix Inconsistency - Serv | `game/ai/strategy_manager.py` | Simple |
| CON-SIM-002 | Duplicate Exception Handler in design_lo | `game/simulation/services/desig` | Simple |
| CON-SIM-003 | Magic Numbers in Projectile Guidance Sys | `game/simulation/entities/proje` | Simple |
| CON-SIM-004 | Singleton Fallback Pattern in Validation | `game/simulation/entities/ship_` | Complex |
| CON-SIM-005 | Inconsistent Parameter Naming - resource | `game/simulation/components/abi` | Simple |
| CON-SIM-006 | Type Hint Gaps in Physics and Combat Mod | `game/simulation/entities/ship_` | Medium |
| CON-SIM-007 | AIControllerFactory Uses Positional Para | `game/simulation/factories/ai_f` | Simple |
| CON-SIM-008 | Magic Numbers in Targeting and Combat Sy | `game/simulation/combat/targeti` | Simple |
| CON-STR-001 | Logging Pattern Inconsistency - Mixed Mo | `Unknown` | Simple |
| CON-STR-002 | Protocol Interface Decorator Inconsisten | `game/strategy/engine/command_h` | Simple |
| CON-STR-003 | Inconsistent Return Type for validate()  | `game/strategy/data/race_config` | Medium |
| CON-STR-004 | Inconsistent `from __future__ import ann | `game/strategy/` | Medium |
| CON-UI2-001 | Inconsistent Dependency Injection Patter | `game/ui/services/*.py` | Medium |
| CON-UI2-002 | Inconsistent Parameter Naming for Regist | `game/ui/services/ship_factory.` | Simple |
| CON-UI2-003 | Singleton Pattern vs Dependency Injectio | `game/ui/services/screenshot_ma` | Complex |
| CON-UI2-004 | Return Type Inconsistency for Failure Ca | `game/ui/services/ship_io_adapt` | Medium |
| CON-UI2-005 | Mixed Method Verb Prefixes for Similar O | `Unknown` | Simple |
| CON-UI1-001 | Inconsistent Constructor Parameter Order | `Unknown` | Complex |
| CON-UI1-002 | Incomplete God Class Decomposition (test | `game/ui/screens/test_lab/scree` | Complex |
| CON-UI1-003 | Direct Singleton Access Instead of Depen | `Unknown` | Medium |
| CON-UI1-004 | Mixed Event Handler Naming (handle_event | `Unknown` | Simple |
| DUP-FND-001 | Entity Position/State Access Patterns in | `game/ai/combat_utils.py:49-82` | Medium |
| DUP-FND-002 | Singleton Pattern Documentation/Structur | `Unknown` | Medium |
| DUP-SIM-001 | Serialization to_dict/from_dict Pattern  | `game/simulation/battle_state.p` | Medium |
| DUP-SIM-002 | Resource Ability Classes Share Identical | `game/simulation/components/abi` | Simple |
| DUP-SIM-003 | Team Iteration Pattern Duplicated in Bat | `game/simulation/systems/battle` | Simple |
| DUP-STR-001 | Build Queue Source Collection - Near-Ide | `game/strategy/data/build_queue` | Simple |
| DUP-STR-002 | Facility Shipyard Detection - Duplicated | `game/strategy/data/build_queue` | Simple |
| DUP-STR-003 | Mission Command Handler Duplication | `game/strategy/engine/superweap` | Simple |
| DUP-STR-004 | `to_dict` / `from_dict` Boilerplate Patt | `Unknown` | Complex |
| DUP-STR-005 | Fleet Resolution Pattern in Command Hand | `Unknown` | Simple |
| DUP-STR-006 | ColonizeValidator Colony Pod Iteration P | `game/strategy/validation/colon` | Simple |
| DUP-STR-007 | Component Layer Iteration Pattern - Repe | `Unknown` | Medium |
| DUP-UI2-001 | Dependency Injection Pattern Inconsisten | `game/ui/services/vehicle_class` | Medium |
| DUP-UI2-002 | Image Bounding Box and Visible Area Scal | `game/ui/utils.py:97-163` | Medium |
| UNK-03 | Window Open/Close Pattern Repeated in St | `Unknown` | Unknown |
| UNK-04 | Timestamp Formatting Duplicated Within S | `Unknown` | Unknown |
| UNK-05 | Scrollbar + List Panel Pattern Repeated  | `Unknown` | Unknown |
| UNK-06 | Filter Toggle Button Pattern Repeated | `Unknown` | Unknown |
| LEG-FND-001 | Stale Documentation Reference to Removed | `game/ai/target_evaluator.py:16` | Simple |
| LEG-STR-001 | Legacy Behavior Branch in FleetOrderProc | `game/strategy/engine/fleet_ord` | Medium |
| LEG-STR-002 | Backward Compatibility Comment in GameSe | `game/strategy/engine/game_sess` | Medium |
| LEG-STR-003 | Legacy Items in ProductionEngine | `game/strategy/engine/productio` | Medium |
| LEG-UI2-001 | Unused Method - create_ai_for_ship in Ba | `game/ui/orchestration/battle_o` | Simple |
| TCG-FND-003 | AIController navigation and avoidance al | `game/ai/controller.py` | Medium |
| TCG-FND-004 | TargetEvaluator rule evaluation missing  | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-005 | Behavior classes missing state transitio | `game/ai/behaviors.py` | Medium |
| TCG-FND-006 | TechTree validation methods lack test co | `game/research/data/tech_tree.p` | Simple |
| TCG-FND-007 | TechRequirement fuzzy resolution edge ca | `game/research/data/tech_node.p` | Simple |
| TCG-FND-008 | ResearchTracker serialization roundtrip  | `game/research/data/research_tr` | Simple |
| TCG-FND-009 | SpatialGrid query_radius does not filter | `game/engine/spatial.py` | Simple |
| TCG-SIM-004 | designs.py Lacks Any Test Coverage | `game/simulation/designs.py` | Simple |
| TCG-SIM-005 | resource_manager.py (ResourceRegistry) M | `game/simulation/systems/resour` | Medium |
| TCG-SIM-006 | battle_controller.py Missing State Trans | `game/simulation/battle_control` | Medium |
| TCG-SIM-007 | formula_system.py Edge Cases Not Tested | `game/simulation/formula_system` | Simple |
| TCG-SIM-008 | projectile_manager.py Missing Guidance S | `game/simulation/projectile_man` | Medium |
| TCG-SIM-009 | battle_state.py Serialization Round-Trip | `game/simulation/battle_state.p` | Medium |
| TCG-SIM-010 | combat/damage_calculator.py Missing Armo | `game/simulation/combat/damage_` | Medium |
| TCG-STR-003 | No dedicated tests for game/strategy/eng | `game/strategy/engine/commands.` | Simple |
| TCG-STR-004 | TurnEngine.validate_colonize_order lacks | `game/strategy/engine/turn_engi` | Simple |
| TCG-STR-005 | FleetOrder.to_dict() serialization has w | `game/strategy/data/fleet.py::F` | Medium |
| TCG-STR-006 | QuickstartBuilder has no comprehensive t | `game/strategy/quickstart_build` | Medium |
| TCG-STR-007 | StrategySessionFacade has incomplete que | `game/strategy/facade/strategy_` | Medium |
| TCG-STR-008 | GameInitializer._setup_initial_scenario  | `game/strategy/engine/game_init` | Simple |
| TCG-STR-009 | ShipStatsCalculator.has_warp_capability  | `game/strategy/services/ship_st` | Medium |
| TCG-UI2-001 | UIConfig class has no dedicated test cov | `game/ui/config.py` | Simple |
| TCG-UI2-002 | game_renderer draw_ship lacks edge case  | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI2-003 | draw_hud resource bar edge cases not tes | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI2-004 | BattleUIService projectile color mapping | `game/ui/services/battle_ui_ser` | Simple |
| TCG-UI2-005 | ShipThemeManager missing scale factor bo | `game/ui/assets/ship_theme_mana` | Simple |
| TCG-UI1-005 | BuilderScreen (legacy) has no unit tests | `game/ui/screens/builder/main.p` | Complex |
| TCG-UI1-006 | FormationEditorScreen has incomplete tes | `game/ui/screens/formation_edit` | Medium |
| TCG-UI1-007 | PlanetReportPanel has no unit tests | `game/ui/panels/planet_report_p` | Medium |
| TCG-UI1-008 | ShipDetailPanel has no unit tests | `game/ui/panels/ship_detail_pan` | Medium |
| TCG-UI1-009 | BaseGallery abstract class has no unit t | `game/ui/panels/base_gallery.py` | Simple |
| TCG-UI1-010 | DesignReportPanel has no unit tests | `game/ui/panels/design_report_p` | Simple |
| TCG-UI1-011 | Multiple builder submodules have no test | `game/ui/screens/builder/` | Complex |
| TCG-UI1-012 | Multiple test_lab submodules have no tes | `game/ui/screens/test_lab/` | Complex |
| TCG-UI1-013 | GalaxyTest screen module has no tests | `game/ui/screens/galaxy_test/` | Simple |
| TCG-UI1-014 | Formation submodules have no tests | `game/ui/screens/formation/` | Medium |
| TCG-UI1-015 | Workshop helper modules have thin covera | `game/ui/screens/workshop_*.py` | Medium |
| TCG-UI1-016 | Multiple race panel modules lack tests | `game/ui/panels/race_*.py` | Medium |
| TCG-UI1-017 | StrategyRenderer draw methods test only  | `tests/unit/ui/screens/test_str` | Medium |
| TCG-UI1-018 | DesignStatsPanel tests use bypass-init p | `tests/unit/ui/panels/test_desi` | Medium |

### Minor (125)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | behaviors.py File Growing Large | `game/ai/behaviors.py` | Simple |
| ADR-SIM-006 | Possible Circular Import Comment in ship | `game/simulation/entities/ship_` | Simple |
| ADR-UI2-003 | Lazy Import Pattern in ship_factory.py C | `game/ui/services/ship_factory.` | Simple |
| ADR-UI2-004 | TYPE_CHECKING Import for GameRegistries  | `game/ui/services/ship_factory.` | Simple |
| ADR-UI1-011 | Simulation Layer TYPE_CHECKING Imports | `Unknown` | Simple |
| ADR-UI1-012 | Planet Filter Cached Attributes | `game/ui/screens/planet_list_fi` | Simple |
| ADR-UI1-013 | Strategy Renderer Temporary Attributes | `game/ui/screens/strategy_rende` | Simple |
| ADR-UI1-014 | FleetCapabilityCalculator Private Method | `game/ui/screens/column_manager` | Simple |
| ADR-UI1-015 | InputMapper Private Method Access | `game/ui/screens/keybindings_sc` | Simple |
| CON-FND-006 | Inconsistent Parameter Naming - entity v | `game/ai/combat_utils.py` | Simple |
| CON-FND-007 | Inconsistent Docstring Format - Google S | `Unknown` | Simple |
| CON-FND-008 | Boolean Property Naming - is_alive() vs  | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-009 | Inconsistent Type Hint Coverage | `game/core/logger.py:27-41` | Simple |
| CON-FND-010 | Inconsistent Import Organization | `game/ai/controller.py:51-66` | Simple |
| CON-FND-011 | Magic Numbers in AI Layer | `game/ai/controller.py:445` | Simple |
| CON-FND-012 | Inconsistent Error Handling - Broad Exce | `game/ai/controller.py:217-223` | Simple |
| CON-FND-013 | Inconsistent `__all__` Export Patterns | `game/core/constants.py:1-15` | Simple |
| CON-FND-014 | Redundant Protocol Definition | `game/core/validation.py:23-60` | Simple |
| CON-SIM-009 | Abbreviated Parameter Names in solve_lea | `game/simulation/combat/targeti` | Simple |
| CON-SIM-010 | Mixed Logging Initialization Patterns | `game/simulation/services/regis` | Simple |
| CON-SIM-011 | STAT_BINDINGS Type Hint Inconsistency | `game/simulation/components/abi` | Simple |
| CON-SIM-012 | sync_data() Inconsistent Implementation  | `game/simulation/components/abi` | Medium |
| CON-SIM-013 | Inconsistent Method Verb Conventions | `game/simulation/entities/ship_` | Simple |
| CON-SIM-014 | Missing Exports in services/__init__.py | `game/simulation/services/__ini` | Simple |
| CON-SIM-015 | ability_aggregator.py Naming Convention | `game/simulation/entities/abili` | Simple |
| CON-SIM-016 | PROJ Comment Format Inconsistency | `Unknown` | Simple |
| CON-STR-005 | Method Naming Inconsistency - lookup_ vs | `game/strategy/engine/harvestin` | Simple |
| CON-STR-006 | Missing Type Hints on Public API Methods | `game/strategy/data/naming.py:6` | Simple |
| CON-STR-007 | Missing Docstrings in stars.py Methods | `game/strategy/data/stars.py` | Simple |
| CON-STR-008 | Missing `__all__` Export in Package `__i | `Unknown` | Simple |
| CON-STR-009 | Inconsistent Engine Constructor DI Patte | `Unknown` | Simple |
| CON-STR-010 | Duplicate MAINTENANCE_RATE Constant | `game/strategy/engine/maintenan` | Simple |
| CON-UI2-006 | Inconsistent Type Hint Usage for Ship Pa | `game/ui/services/ship_io_adapt` | Simple |
| CON-UI2-007 | Docstring Format Inconsistency | `Unknown` | Simple |
| CON-UI2-008 | Boolean Parameter Naming Without Prefix | `game/ui/services/screenshot_ma` | Simple |
| CON-UI2-009 | Constants Defined at Module Level vs Cla | `game/ui/services/battle_ui_ser` | Simple |
| CON-UI2-010 | Mixed Logging Patterns | `game/ui/services/screenshot_ma` | Simple |
| CON-UI2-011 | Import Organization Inconsistencies | `game/ui/assets/ship_theme_mana` | Simple |
| CON-UI2-012 | Inconsistent Use of Optional vs Default  | `game/ui/services/input_mapper.` | Simple |
| CON-UI2-013 | Thread Safety Documentation Inconsistenc | `game/ui/services/screenshot_ma` | Medium |
| CON-UI2-014 | User Story Comment in Production Code | `game/ui/renderer/game_renderer` | Simple |
| CON-UI1-005 | Inconsistent Event Handler Return Type A | `Unknown` | Medium |
| CON-UI1-006 | Mixed Screen/Scene Class Naming Suffix | `game/ui/screens/menu_scene.py` | Simple |
| CON-UI1-007 | Inconsistent UI Manager Attribute Names | `Unknown` | Medium |
| CON-UI1-008 | Inconsistent Type Hint Coverage | `game/ui/screens/builder/compon` | Medium |
| CON-UI1-009 | Inconsistent Future Annotations Usage | `Unknown` | Simple |
| CON-UI1-010 | Inconsistent Event Handler Return Values | `BattlePanel.handle_click()` | Medium |
| CON-UI1-011 | Two Initialization Method Naming Convent | `Unknown` | Simple |
| CON-UI1-012 | Missing Module Docstrings | `game/ui/screens/builder/compon` | Simple |
| CON-UI1-013 | Inconsistent Panel Base Class Usage | `game/ui/panels/` | Simple |
| CON-UI1-014 | Mixed Responsibility in test_lab Subdire | `game/ui/screens/test_lab/scree` | Complex |
| DUP-FND-003 | Entity ID Extraction Pattern Duplication | `game/ai/combat_utils.py:65` | Simple |
| DUP-FND-004 | Flee Direction Calculation | `game/ai/behaviors.py:70-84` | Simple |
| DUP-FND-005 | Tech Tree Validation Method Patterns | `game/research/data/tech_tree.p` | Simple |
| DUP-FND-006 | Serialization to_dict/from_dict Patterns | `game/research/data/research_tr` | Complex |
| DUP-SIM-004 | Vector2 Conversion Pattern in Projectile | `game/simulation/projectile_man` | Simple |
| DUP-SIM-005 | get_ui_rows Color Mapping Pattern in Res | `game/simulation/components/abi` | Simple |
| DUP-SIM-006 | ship_id_map Pattern Repeated in RetreatM | `game/simulation/managers/retre` | Simple |
| DUP-SIM-007 | Validation Pattern in modifier_schema.py | `game/simulation/components/mod` | Medium |
| DUP-STR-008 | Gaussian Factor Calculation Pattern | `game/strategy/formulas/habitab` | Simple |
| DUP-STR-009 | Path Start Hex Determination Logic | `Unknown` | Simple |
| DUP-STR-010 | Ship Ability Check Wrappers | `Unknown` | Simple |
| DUP-STR-011 | Resource Dictionary Accumulation Pattern | `game/strategy/services/ship_st` | Simple |
| DUP-STR-012 | Fleet and Ship Delegation Pattern | `Unknown` | Medium |
| DUP-UI2-003 | Singleton Manager Pattern Repetition | `game/ui/assets/ship_theme_mana` | Simple |
| DUP-UI2-004 | Image Transform Operations Scattered Wit | `game/ui/utils.py:66-94` | Simple |
| DUP-UI2-005 | Validation Service Pattern Has Single-Pu | `game/ui/services/validation_se` | N |
| DUP-UI2-006 | Camera Coordinate Transform Duplication  | `game/ui/renderer/camera.py:116` | Medium |
| UNK-07 | HP/Damage Color Calculation Functions | `Unknown` | Unknown |
| UNK-08 | Population/Number Formatting Duplication | `Unknown` | Unknown |
| UNK-09 | RaceThemeGallery Not Using BaseGallery | `Unknown` | Unknown |
| UNK-10 | Window Kill/Cleanup Pattern Slightly Inc | `Unknown` | Unknown |
| UNK-11 | Dropdown Recreation Utility | `Unknown` | Unknown |
| LEG-FND-002 | Extensive getattr() with Defaults in AI  | `game/ai/controller.py` | Medium |
| LEG-FND-003 | Raw Ship vs Adapter Access Pattern in Fo | `game/ai/behaviors.py:276-400` | Medium |
| LEG-FND-004 | Singleton Pattern Still in Use Despite D | `Unknown` | Complex |
| LEG-FND-005 | Unused AI_STATE_ERROR ErrorCode | `game/core/error_codes.py:153` | Simple |
| LEG-SIM-006 | Module Identity Drift Fallback in Abilit | `game/simulation/components/abi` | Medium |
| LEG-SIM-007 | Component Ability Index Fallback Pattern | `game/simulation/components/com` | Simple |
| LEG-SIM-NEW-001 | Duplicate Exception Handling in design_l | `game/simulation/services/desig` | Simple |
| LEG-STR-004 | Backward Compatibility Comment in FleetN | `game/strategy/services/fleet_n` | Simple |
| LEG-STR-005 | Backward Compat Default in Planet.from_d | `game/strategy/data/planet.py:3` | Simple |
| LEG-STR-006 | Backward Compat Defaults in RaceConfig.f | `game/strategy/data/race_config` | N |
| LEG-STR-007 | Old Layer Format Detection in DesignMeta | `game/strategy/data/design_meta` | Simple |
| LEG-STR-008 | Save Compatibility Field in DesignMetada | `game/strategy/data/design_meta` | Simple |
| LEG-UI2-002 | Comment References "legacy behavior" in  | `game/ui/services/ship_factory.` | Medium |
| LEG-UI2-003 | Excessive getattr() with Defaults in bat | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI2-004 | ModifierEditorPanel Marked as Legacy | `game/ui/screens/builder/modifi` | Medium |
| TCG-FND-010 | PhysicsBody x/y property setters not tes | `game/engine/physics.py` | Simple |
| TCG-FND-011 | ShipControllableAdapter formation method | `game/ai/interfaces/controllabl` | Simple |
| TCG-FND-012 | Logger module singleton behavior not ful | `game/core/logger.py` | Simple |
| TCG-FND-013 | Config module edge cases for clamp value | `game/core/config.py` | Simple |
| TCG-FND-014 | Error code enum completeness not verifie | `game/core/error_codes.py` | Simple |
| TCG-FND-015 | Profiling decorator edge cases not teste | `game/core/profiling.py` | Simple |
| TCG-FND-016 | hex_ring negative radius input not teste | `game/core/hex_math.py` | Simple |
| TCG-SIM-011 | components/abilities/weapons.py Tests Sp | `game/simulation/components/abi` | Simple |
| TCG-SIM-012 | components/abilities/defense.py Tests La | `game/simulation/components/abi` | Simple |
| TCG-SIM-013 | components/abilities/propulsion.py Missi | `game/simulation/components/abi` | Simple |
| TCG-SIM-014 | services/design_loader.py Has No Tests | `game/simulation/services/desig` | Simple |
| TCG-SIM-015 | interfaces/ai_controller.py Interface Te | `game/simulation/interfaces/ai_` | Simple |
| TCG-SIM-016 | validation/ship_validator.py Missing Com | `game/simulation/validation/shi` | Simple |
| TCG-STR-010 | DensityMap.from_config() lacks test cove | `game/strategy/generation/densi` | Simple |
| TCG-STR-011 | RegionClassifier._classify_spiral edge c | `game/strategy/generation/regio` | Simple |
| TCG-STR-012 | calculate_habitability has no negative t | `game/strategy/formulas/habitab` | Simple |
| TCG-STR-013 | EmpireEconomyCalculator doesn't test des | `game/strategy/engine/empire_ec` | Simple |
| TCG-STR-014 | Component inspector service lacks edge c | `game/strategy/services/compone` | Simple |
| TCG-STR-015 | Fleet.trigger_speed_recalculation has no | `game/strategy/data/fleet.py::t` | Simple |
| TCG-STR-016 | Transfer order validator edge cases | `game/strategy/validation/trans` | Simple |
| TCG-UI2-006 | Camera fit_objects edge case with dead t | `game/ui/renderer/camera.py` | Simple |
| TCG-UI2-007 | InputMapper save_user_overrides file per | `game/ui/services/input_mapper.` | Simple |
| TCG-UI2-008 | ScreenshotManager capture_strategy_layer | `game/ui/services/screenshot_ma` | Simple |
| TCG-UI2-009 | BattleOrchestrator lacks tests for AI co | `game/ui/orchestration/battle_o` | Simple |
| TCG-UI2-010 | SpriteManager thread safety tests are li | `game/ui/renderer/sprites.py` | Medium |
| TCG-UI2-011 | colors.py basic constants not tested | `game/ui/colors.py` | Simple |
| TCG-UI1-019 | StrategyScreen tests have incomplete met | `tests/unit/ui/screens/test_str` | Medium |
| TCG-UI1-020 | Screen transition handling untested | `Unknown` | Simple |
| TCG-UI1-021 | Input handling edge cases untested | `game/ui/screens/strategy_input` | Simple |
| TCG-UI1-022 | Source code inspection used instead of b | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-023 | Mock verification without assertions on  | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-024 | Test helper function tests its own mock | `tests/unit/ui/panels/test_desi` | Simple |
| TCG-UI1-025 | Missing parameterized edge case tests | `Unknown` | Simple |
| TCG-UI1-026 | No end-to-end battle UI flow tests | `Unknown` | Medium |
| TCG-UI1-027 | Strategy screen + build queue integratio | `Unknown` | Medium |
| TCG-UI1-028 | Workshop + ship I/O roundtrip untested | `Unknown` | Medium |
| TCG-UI1-029 | No resize handling tests | `Unknown` | Simple |

### Info (44)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-007 | Heavy Use of TYPE_CHECKING for Forward R | `Unknown` | N |
| ADR-UI2-005 | BattleOrchestrator Correctly Documents C | `game/ui/orchestration/battle_o` | N |
| ADR-UI1-016 | Test Lab Executor Private Field Access | `game/ui/screens/test_lab/test_` | Simple |
| ADR-UI1-017 | Deep Object Chain in StrategyUI | `game/ui/screens/strategy_ui.py` | Simple |
| ADR-UI1-018 | Large Method Counts in UI Screens | `Unknown` | N |
| CON-FND-015 | os.path vs pathlib.Path Mixed Usage | `game/core/paths.py:53-103` | Simple |
| CON-FND-016 | ResourceType is a Class, Not an Enum | `game/core/constants.py:83-92` | Simple |
| CON-FND-017 | TechNode/TechTree Separate from Core Reg | `game/research/data/tech_tree.p` | N |
| CON-FND-018 | Research Layer Has Direct pygame Import | `game/research/ui/research_scen` | Complex |
| CON-SIM-017 | ResourceRegistry Class Name Deviation | `game/simulation/systems/resour` | Simple |
| CON-SIM-018 | Excellent Pattern Adherence - Facade/Del | `game/simulation/entities/ship_` | N |
| CON-STR-011 | Well-Established Consistent Patterns | `Unknown` | N |
| CON-STR-012 | Consistent Class Naming Suffixes | `Unknown` | N |
| CON-UI2-015 | Protocol Definition Location | `game/ui/interfaces/battle_ui.p` | N |
| CON-UI2-016 | __init__.py Export Patterns | `game/ui/__init__.py` | N |
| CON-UI1-015 | Good Pattern Adoption - Facade/Delegate  | `strategy_ui.py` | N |
| CON-UI1-016 | Consistent Callback Naming Pattern | `Unknown` | N |
| CON-UI1-017 | Good Class Naming Suffix Consistency | `Unknown` | N |
| CON-UI1-018 | Well-Organized builder/ Module Structure | `game/ui/screens/builder/` | N |
| CON-UI1-019 | Consistent Logging Pattern | `Unknown` | N |
| DUP-FND-007 | Well-Consolidated Utilities | `game/core/` | N |
| DUP-SIM-008 | Natural Similarity in Dataclass State Cl | `game/simulation/battle_state.p` | N |
| DUP-STR-013 | Validated Design Component Iteration | `Unknown` | Medium |
| DUP-STR-014 | Well-Consolidated Component Inspector | `game/strategy/services/compone` | N |
| DUP-UI2-007 | Color Constants Could Be Centralized Fur | `game/ui/colors.py:7-45` | N |
| UNK-12 | BaseGallery Already Extracted (RESOLVED) | `Unknown` | Unknown |
| UNK-13 | Ship Stats Renderer Already Extracted | `Unknown` | Unknown |
| UNK-14 | Strategy Detail Formatters Properly Sepa | `Unknown` | Unknown |
| LEG-FND-006 | Well-Organized Research Module | `game/research/` | N |
| LEG-SIM-009 | TechPresetLoader Only Used in Tests | `game/simulation/systems/tech_p` | Unknown |
| LEG-STR-009 | Test Mock Compatibility in FleetOrderPro | `game/strategy/engine/fleet_ord` | Simple |
| LEG-STR-010 | Intercept Function Accepts Both Fleet an | `game/strategy/data/pathfinding` | N |
| LEG-UI2-005 | Singleton Pattern Still in Use for Asset | `game/ui/assets/ship_theme_mana` | N |
| LEG-UI2-006 | hasattr() Check in Camera for Defensive  | `game/ui/renderer/camera.py:58` | Simple |
| TCG-FND-017 | Research system UI rendering tests use m | `game/research/ui/research_rend` | N |
| TCG-FND-018 | Test file organization follows productio | `Unknown` | N |
| TCG-SIM-017 | Test Organization Could Use Consolidatio | `Unknown` | N |
| TCG-SIM-018 | No Performance/Load Tests for Simulation | `game/simulation/systems/battle` | N |
| TCG-STR-017 | Test fixtures use hardcoded component ID | `Unknown` | Complex |
| TCG-STR-018 | Heavy mocking in TurnEngine tests | `tests/unit/strategy/turn_engin` | Medium |
| TCG-UI2-012 | Test organization could be improved | `tests/unit/ui/` | Complex |
| TCG-UI1-030 | No error recovery tests for UI screens | `Unknown` | Complex |
| TCG-UI1-031 | No performance/stress tests for panels w | `game/ui/panels/battle_panels.p` | Medium |
| TCG-UI1-032 | UI panels lack null/empty data tests | `Unknown` | Simple |


## Agent Reports

- [Architecture Foundation Report](findings/architecture_foundation_report.md)
- [Architecture Simulation Report](findings/architecture_simulation_report.md)
- [Architecture Strategy Report](findings/architecture_strategy_report.md)
- [Architecture Ui Framework Report](findings/architecture_ui_framework_report.md)
- [Architecture Ui Screens Report](findings/architecture_ui_screens_report.md)
- [Consistency Foundation Report](findings/consistency_foundation_report.md)
- [Consistency Simulation Report](findings/consistency_simulation_report.md)
- [Consistency Strategy Report](findings/consistency_strategy_report.md)
- [Consistency Ui Framework Report](findings/consistency_ui_framework_report.md)
- [Consistency Ui Screens Report](findings/consistency_ui_screens_report.md)
- [Duplication Foundation Report](findings/duplication_foundation_report.md)
- [Duplication Simulation Report](findings/duplication_simulation_report.md)
- [Duplication Strategy Report](findings/duplication_strategy_report.md)
- [Duplication Ui Framework Report](findings/duplication_ui_framework_report.md)
- [Duplication Ui Screens Report](findings/duplication_ui_screens_report.md)
- [Legacy Foundation Report](findings/legacy_foundation_report.md)
- [Legacy Simulation Report](findings/legacy_simulation_report.md)
- [Legacy Strategy Report](findings/legacy_strategy_report.md)
- [Legacy Ui Framework Report](findings/legacy_ui_framework_report.md)
- [Legacy Ui Screens Report](findings/legacy_ui_screens_report.md)
- [Test Coverage Foundation Report](findings/test_coverage_foundation_report.md)
- [Test Coverage Simulation Report](findings/test_coverage_simulation_report.md)
- [Test Coverage Strategy Report](findings/test_coverage_strategy_report.md)
- [Test Coverage Ui Framework Report](findings/test_coverage_ui_framework_report.md)
- [Test Coverage Ui Screens Report](findings/test_coverage_ui_screens_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 288 |
| Critical | 17 |
| Major | 102 |
| Minor | 125 |
| Info | 44 |
| Agents Used | 23 |

---
*Report generated: 2026-02-13 05:51*
