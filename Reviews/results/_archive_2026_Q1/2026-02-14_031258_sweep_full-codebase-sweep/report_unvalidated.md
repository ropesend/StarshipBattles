# Review Report: 2026-02-14_031258_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-14
- **Type:** Review
- **Description:** 
- **Agents Used:** 24

## Executive Summary
- **Total Findings:** 274
- **Critical:** 17 | **Major:** 96 | **Minor:** 119 | **Info:** 42
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Strategy Layer Imports from AI Layer
**ID:** ADR-STR-001
**Agent:** Architecture Strategy
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Effort:** Medium

**ID:** ADR-STR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Issue:** Strategy layer directly imports from the AI layer, violating the documented architecture where Strategy can only depend on Simulation and Core. The comment on line 28-29 incorrectly claims "strategy can depend on AI" but the architecture documentation (docs/architecture/ARCHITECTURE.md lines 35-40) explicitly states Strategy can only depend on "Simulation (via interfaces), Core".
**Code:**
```python
# ...

---

### 2. CRITICAL: Inconsistent Return Convention for Not-Found Scenarios
**ID:** CON-SIM-001
**Agent:** Consistency Simulation
**Location:** `game/simulation/services/battle_service.py:274-289`
**Effort:** Medium

**ID:** CON-SIM-001
**Location:** `game/simulation/services/battle_service.py:274-289` vs `game/simulation/systems/battle_engine.py:615-634`
**Issue:** `BattleService.get_winner()` returns `Optional[int]` (None when no battle), while `BattleEngine.get_winner()` always returns `int` (-1 for draw, never None). This inconsistency in return semantics for the same operation at different abstraction levels creates confusion about what "no winner" means.
**Impact:** Callers must handle different return...

---

### 3. CRITICAL: Inconsistent Return Pattern for Not-Found Scenarios
**ID:** CON-UI1-001
**Agent:** Consistency Ui Screens
**Location:** `game/ui/screens/`
**Effort:** Complex

**ID:** CON-UI1-001
**Location:** `game/ui/screens/` (multiple files)
**Issue:** Methods handling "not found" scenarios use inconsistent patterns: some return `None`, others raise exceptions, others return empty collections. For example:
- `get_hovered_component()` returns `None` (left_panel.py:475)
- `get_target_layer_at()` returns `None` (layer_panel.py:447)
- `load_battle_setup()` returns `None` on error (setup_data_io.py:233)
- Some methods raise exceptions on invalid input

**Impact:** Call...

---

### 4. CRITICAL: Duplicate ColumnManager Classes
**ID:** DUP-UI1-001
**Agent:** Duplication Ui Screens
**Location:** `game/ui/screens/column_manager.py:49-234`
**Effort:** Medium

**ID:** DUP-UI1-001
**Location:** `game/ui/screens/column_manager.py:49-234` AND `game/ui/screens/planet_list_columns.py:11-201`
**Issue:** Two completely separate `ColumnManager` classes exist with overlapping functionality:
- `column_manager.py` - Generic column manager for FleetReportWindow with value extraction
- `planet_list_columns.py` - Column manager for PlanetListWindow with header button UI

Both have:
- `get_visible_columns()` method with identical implementation
- Column visibility t...

---

### 5. CRITICAL: BattleOrchestrator is Defined but Never Used
**ID:** LEG-UI2-001
**Agent:** Legacy Ui Framework
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-99`
**Effort:** Medium

**ID:** LEG-UI2-001
**Location:** `game/ui/orchestration/battle_orchestrator.py:1-99`
**Issue:** The entire `BattleOrchestrator` class (created in PROJ-17) is defined and exported but never imported or used anywhere in the production codebase. The class provides `create_ai_controllers()` and `create_ai_for_ship()` methods, but actual AI controller creation is done differently via `BattleController` and `AIControllerFactory` (see `battle_factories.py`).
**Impact:** Dead code module (99 lines) tha...

---

### 6. CRITICAL: PhysicsBody Class Has No Direct Unit Tests
**ID:** TCG-FND-001
**Agent:** Test Coverage Foundation
**Location:** `game/engine/physics.py`
**Effort:** Medium

**ID:** TCG-FND-001
**Location:** `game/engine/physics.py` (production) / No corresponding test file
**Issue:** The `PhysicsBody` class (base physics entity with position, velocity, acceleration, drag model) has no dedicated unit tests. While Ship extends this class and may exercise some functionality, the base class's core methods (`update()`, `apply_force()`, `forward_vector()`) are not directly tested in isolation. This is critical because PhysicsBody defines the fundamental physics behavior ...

---

### 7. CRITICAL: SpatialGrid Missing Comprehensive Unit Tests
**ID:** TCG-FND-002
**Agent:** Test Coverage Foundation
**Location:** `game/engine/spatial.py`
**Effort:** Simple

**ID:** TCG-FND-002
**Location:** `game/engine/spatial.py` (production) / No corresponding test file
**Issue:** The `SpatialGrid` class is critical infrastructure for all proximity queries (collision detection, target acquisition). There are no dedicated unit tests for this class. Tests exist only in `tests/unit/engine/collision_edge_cases/` which focus on collision scenarios rather than the SpatialGrid API directly.
**Impact:** Bugs in spatial partitioning (incorrect cell calculations, missing ...

---

### 8. CRITICAL: AIControllerFactory Missing Test Coverage
**ID:** TCG-FND-003
**Agent:** Test Coverage Foundation
**Location:** `game/ai/ai_factory.py`
**Effort:** Simple

**ID:** TCG-FND-003
**Location:** `game/ai/ai_factory.py` (production) / No corresponding test file
**Issue:** The `AIControllerFactory` class has no dedicated unit tests. This factory is responsible for creating AI controllers for all ships in combat. The two-phase initialization pattern (create factory, then set_grid) and the RuntimeError on premature usage are untested.
**Impact:** Factory failures could break combat AI initialization entirely. The grid-not-set RuntimeError path is never veri...

---

### 9. CRITICAL: No Direct Tests for Ship Entity Core Methods
**ID:** TCG-SIM-001
**Agent:** Test Coverage Simulation
**Location:** `game/simulation/entities/ship.py`
**Effort:** Complex

**ID:** TCG-SIM-001
**Location:** `game/simulation/entities/ship.py` (production) / `tests/unit/simulation/entities/` (test gap)
**Issue:** The Ship class is 800+ lines with 40+ public methods but has no dedicated `test_ship.py` file. Key untested methods include:
- `die()` - death logic and state transitions
- `update()` - per-tick updates with context handling
- `recalculate_stats()` - stat aggregation pipeline
- `add_component()` / `remove_component()` - component management
- `change_class()...

---

### 10. CRITICAL: No Tests for Propulsion Abilities
**ID:** TCG-SIM-002
**Agent:** Test Coverage Simulation
**Location:** `game/simulation/components/abilities/propulsion.py`
**Effort:** Medium

**ID:** TCG-SIM-002
**Location:** `game/simulation/components/abilities/propulsion.py` (production) / No corresponding test file
**Issue:** Four propulsion ability classes with zero dedicated tests:
- `CombatPropulsion` - thrust calculation
- `ManeuveringThruster` - turn rate calculation
- `StrategicMovement` - movement point calculation
- `WarpJump` - warp capability with tonnage limit

These are core movement abilities. The `STAT_BINDINGS`, `recalculate()`, `sync_data()`, and `get_ui_rows()` m...

---


## Findings by Severity

### Critical (17)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-STR-001 | Strategy Layer Imports from AI Layer | `game/strategy/adapters/simulat` | Medium |
| CON-SIM-001 | Inconsistent Return Convention for Not-F | `game/simulation/services/battl` | Medium |
| CON-UI1-001 | Inconsistent Return Pattern for Not-Foun | `game/ui/screens/` | Complex |
| DUP-UI1-001 | Duplicate ColumnManager Classes | `game/ui/screens/column_manager` | Medium |
| LEG-UI2-001 | BattleOrchestrator is Defined but Never  | `game/ui/orchestration/battle_o` | Medium |
| TCG-FND-001 | PhysicsBody Class Has No Direct Unit Tes | `game/engine/physics.py` | Medium |
| TCG-FND-002 | SpatialGrid Missing Comprehensive Unit T | `game/engine/spatial.py` | Simple |
| TCG-FND-003 | AIControllerFactory Missing Test Coverag | `game/ai/ai_factory.py` | Simple |
| TCG-SIM-001 | No Direct Tests for Ship Entity Core Met | `game/simulation/entities/ship.` | Complex |
| TCG-SIM-002 | No Tests for Propulsion Abilities | `game/simulation/components/abi` | Medium |
| TCG-STR-001 | PopulationEngine has no unit tests | `game/strategy/engine/populatio` | Medium |
| TCG-STR-002 | HarvestingEngine has no unit tests | `game/strategy/engine/harvestin` | Medium |
| TCG-UI2-001 | Missing Tests for Validation Service Err | `game/ui/services/validation_se` | Medium |
| TCG-UI1-001 | BattleScreen has minimal functional test | `game/ui/screens/battle_screen.` | Complex |
| TCG-UI1-002 | BattleUI panel rendering has no test fil | `game/ui/screens/battle_ui.py` | Medium |
| TCG-UI1-003 | battle_panels.py (ShipStatsPanel, Seeker | `game/ui/panels/battle_panels.p` | Medium |
| TCG-UI1-004 | InteractionController (drag-drop for shi | `game/ui/screens/builder/intera` | Medium |

### Major (96)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Research UI imports game.ui.renderer.cam | `game/research/ui/research_scen` | Medium |
| ADR-SIM-001 | Ship Class is Approaching God Class Terr | `game/simulation/entities/ship.` | Simple |
| ADR-SIM-002 | Intentional Late Imports for Circular De | `Unknown` | Medium |
| ADR-STR-002 | ShipDisplayFormatter in Strategy Layer ( | `game/strategy/data/ship_displa` | Medium |
| ADR-STR-003 | Circular Import Workaround in Galaxy | `game/strategy/data/galaxy.py:4` | Medium |
| ADR-UI2-001 | ShipIO Direct Import of Simulation Entit | `game/ui/services/ship_io.py:20` | Medium |
| ADR-UI2-002 | Camera Uses pygame.math.Vector2 Instead  | `game/ui/renderer/camera.py:14,` | Simple |
| ADR-UI1-001 | God Class - TestLabScreen (1906 lines) | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-002 | God Class - fleet_report_window.py (1093 | `game/ui/screens/fleet_report_w` | Medium |
| ADR-UI1-003 | God Class - build_queue_screen.py (1084  | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-004 | God Class - weapons_panel.py (1037 lines | `game/ui/screens/builder/weapon` | Medium |
| CON-FND-004 | Inconsistent Singleton Pattern Usage | `game/core/singleton.py` | Medium |
| CON-FND-005 | Mixed Logging Patterns | `game/core/logger.py` | Medium |
| CON-FND-008 | Inconsistent Error Handling Return Patte | `game/core/json_utils.py:33-97` | Simple |
| CON-FND-014 | game/research/ - Data Class Serializatio | `game/research/data/research_tr` | Simple |
| CON-SIM-002 | Mixed Naming for Result/Error Types | `Unknown` | Medium |
| CON-SIM-003 | Inconsistent Private Member Naming | `Unknown` | Complex |
| CON-SIM-004 | Inconsistent Use of TYPE_CHECKING for Im | `Unknown` | Simple |
| CON-SIM-005 | Mixed Docstring Styles | `Unknown` | Complex |
| CON-SIM-006 | Dual Patterns for Querying Components/Ab | `game/simulation/entities/ship.` | Medium |
| CON-STR-001 | Inconsistent Method Verb Prefixes for Lo | `Unknown` | Medium |
| CON-STR-002 | Mixed Return Type Patterns for Not-Found | `game/strategy/services/ship_st` | Medium |
| CON-STR-003 | Inconsistent Static Method vs Instance M | `game/strategy/validation/*.py` | Medium |
| CON-STR-004 | Inconsistent Type Hint Coverage | `game/strategy/data/pathfinding` | Simple |
| CON-UI2-001 | Inconsistent Dependency Injection Patter | `game/ui/services/` | Medium |
| CON-UI2-002 | Mixed Return Type Conventions for IO Ope | `game/ui/services/ship_io_adapt` | Medium |
| CON-UI2-003 | Inconsistent Type Hint Completeness | `Unknown` | Simple |
| CON-UI2-004 | Inconsistent Method Naming for Registry/ | `game/ui/services/` | Simple |
| CON-UI2-005 | Two Singleton Patterns in Use | `game/ui/renderer/sprites.py` | Simple |
| CON-UI1-002 | Mixed UIConfig Usage vs Magic Numbers | `game/ui/screens/` | Medium |
| CON-UI1-003 | Inconsistent Method Verb Prefixes for Da | `game/ui/screens/` | Medium |
| CON-UI1-004 | Inconsistent Event Handler Naming | `game/ui/screens/` | Medium |
| CON-UI1-005 | Missing Type Hints on Key Public Methods | `game/ui/screens/battle_panels.` | Medium |
| CON-UI1-006 | Inconsistent Docstring Format | `Unknown` | Medium |
| DUP-FND-001 | Strategy Data Loading Duplication | `game/core/strategy_metadata.py` | Simple |
| DUP-FND-002 | Singleton Clear Pattern Repetition | `game/core/strategy_metadata.py` | Medium |
| DUP-SIM-001 | Ability Pattern Boilerplate Duplication | `game/simulation/components/abi` | Medium |
| DUP-SIM-002 | Formula Evaluation Pattern Duplication | `game/simulation/components/abi` | Simple |
| DUP-SIM-003 | Resource Type Handling Duplication | `game/simulation/entities/ship_` | Medium |
| DUP-SIM-004 | Validation Pattern Repetition in Loaders | `game/simulation/components/com` | Medium |
| DUP-STR-001 | Component Ability Extraction Pattern Rep | `game/strategy/engine/harvestin` | Medium |
| DUP-STR-002 | Layer Iteration Pattern Duplicated in 7+ | `Unknown` | Medium |
| DUP-STR-003 | Maintenance Cost Calculation Has Near-Du | `game/strategy/engine/maintenan` | Medium |
| DUP-UI2-010 | Registry Provider Access Pattern Duplica | `game/ui/services/component_ser` | Medium |
| DUP-UI2-011 | Service Adapter Boilerplate Pattern | `game/ui/services/ship_io_adapt` | Medium |
| DUP-UI2-012 | Singleton Manager Pattern Duplication | `game/ui/assets/ship_theme_mana` | Medium |
| DUP-UI1-002 | Duplicate draw_stat_bar Implementations | `game/ui/panels/battle_panels.p` | Simple |
| DUP-UI1-003 | Duplicate HP Color Calculation Logic | `game/ui/panels/ship_stats_rend` | Simple |
| DUP-UI1-004 | Duplicate Number Magnitude Formatting | `Unknown` | Simple |
| DUP-UI1-005 | RaceThemeGallery Does Not Extend BaseGal | `game/ui/panels/race_theme_gall` | Medium |
| LEG-FND-001 | Unused Error Codes in error_codes.py | `game/core/error_codes.py:82-10` | Simple |
| LEG-FND-002 | Singleton Pattern Pervasive Despite DI P | `game/core/singleton.py` | Complex |
| LEG-FND-003 | Defensive getattr Fallbacks in AI Module | `game/ai/controller.py:125-127,` | Medium |
| LEG-FND-004 | Strategy Fallback Patterns in AI Documen | `game/ai/__init__.py:38-48` | Medium |
| LEG-SIM-001 | Unused designs.py Factory Functions | `game/simulation/designs.py:11-` | Simple |
| LEG-SIM-002 | Unused BattleConfig.isolated Field | `game/simulation/battle_config.` | Simple |
| LEG-SIM-003 | Unused validate_state Method in BattleSt | `game/simulation/managers/battl` | Simple |
| LEG-UI2-002 | Defensive getattr Checks for Attributes  | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI2-003 | VehicleClassService Methods Appear Unuse | `game/ui/services/vehicle_class` | Simple |
| LEG-UI1-001 | Legacy Single-Selection Fields Maintaine | `game/ui/screens/empire_build_q` | Simple |
| LEG-UI1-002 | Unused Imports Across Multiple Files | `Unknown` | Simple |
| LEG-UI1-003 | Fallback Pattern to Direct scene.ships A | `game/ui/panels/battle_panels.p` | Medium |
| TCG-FND-004 | game/core/paths.py Missing Test Coverage | `game/core/paths.py` | Simple |
| TCG-FND-005 | game/core/hex_math.py Edge Cases Underte | `game/core/hex_math.py` | Simple |
| TCG-FND-006 | OrbitBehavior Missing Edge Case Tests | `game/ai/behaviors.py` | Simple |
| TCG-FND-007 | ErraticBehavior Uses random Without Seed | `game/ai/behaviors.py` | Simple |
| TCG-FND-008 | Research UI Components Have Thin Coverag | `game/research/ui/research_rend` | Medium |
| TCG-FND-009 | game/core/strategy_metadata.py Serializa | `game/core/strategy_metadata.py` | Simple |
| TCG-FND-010 | collision.py Missing Direct Tests | `game/engine/collision.py` | Medium |
| TCG-SIM-003 | ResourceConsumption and ResourceGenerati | `game/simulation/components/abi` | Medium |
| TCG-SIM-004 | WeaponFiringSystem Tests Missing Edge Ca | `game/simulation/combat/weapon_` | Medium |
| TCG-SIM-005 | BattleEngine Missing Tick Processing Edg | `game/simulation/systems/battle` | Complex |
| TCG-SIM-006 | FormulaSystem Tests Only Cover Exception | `game/simulation/formula_system` | Medium |
| TCG-SIM-007 | No Tests for BattleService Serialization | `game/simulation/services/battl` | Medium |
| TCG-SIM-008 | No Tests for DesignLoader Error Recovery | `game/simulation/services/desig` | Medium |
| TCG-SIM-018 | Superweapons Ability Tests Missing Activ | `game/simulation/components/abi` | Medium |
| TCG-STR-003 | EmpireEconomyCalculator missing from tes | `game/strategy/engine/empire_ec` | Medium |
| TCG-STR-004 | physics.py radiation calculation unteste | `game/strategy/data/physics.py` | Simple |
| TCG-STR-005 | ResupplyEngine coverage gap | `game/strategy/engine/resupply_` | Simple |
| TCG-STR-006 | SimulationBattleResolver integration tes | `game/strategy/adapters/simulat` | Medium |
| TCG-STR-007 | FleetNavigationService warp detection ed | `game/strategy/services/fleet_n` | Simple |
| TCG-UI2-002 | BattleUIService Missing Tests for Edge-C | `game/ui/services/battle_ui_ser` | Medium |
| TCG-UI2-003 | GameRenderer Missing Tests for Component | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI2-004 | Camera Missing Tests for Viewport Bounda | `game/ui/renderer/camera.py` | Simple |
| TCG-UI2-005 | ShipThemeManager Missing Tests for Concu | `game/ui/assets/ship_theme_mana` | Complex |
| TCG-UI2-006 | BattleOrchestrator Missing Tests for Shi | `game/ui/orchestration/battle_o` | Medium |
| TCG-UI1-005 | FleetOrdersWindow has no tests | `game/ui/screens/fleet_orders_w` | Medium |
| TCG-UI1-006 | SaveSelectionWindow has no tests | `game/ui/screens/save_selection` | Medium |
| TCG-UI1-007 | PlanetListWindow has no direct test file | `game/ui/screens/planet_list_wi` | Medium |
| TCG-UI1-008 | EmpirePanelWindow has no tests | `game/ui/screens/empire_panel_w` | Simple |
| TCG-UI1-009 | NewGameSetupScreen has no tests | `game/ui/screens/new_game_setup` | Medium |
| TCG-UI1-010 | StrategyEventRouter has no tests | `game/ui/screens/strategy_event` | Simple |
| TCG-UI1-011 | FormationInputHandler only has indirect  | `game/ui/screens/formation/inpu` | Medium |
| TCG-UI1-012 | builder/ subpackage has no test files at | `game/ui/screens/builder/*.py` | Complex |
| TCG-UI1-013 | test_lab/ subpackage has minimal direct  | `game/ui/screens/test_lab/*.py` | Medium |
| TCG-UI1-014 | RaceDescriptionPanel, ModifierImpactGrid | `game/ui/panels/race_descriptio` | Medium |

### Minor (119)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-002 | Research UI subpackage uses pygame direc | `game/research/ui/research_cont` | Medium |
| ADR-SIM-003 | Component Module Contains Multiple Conce | `game/simulation/components/com` | Simple |
| ADR-SIM-004 | TYPE_CHECKING Usage for Engine Layer | `Unknown` | N |
| ADR-STR-004 | Intentional Late Imports - Documented bu | `Unknown` | Complex |
| ADR-STR-005 | RGB Color Tuples in Game Config | `game/strategy/engine/game_conf` | Simple |
| ADR-UI2-003 | Game Renderer Inline Import of ShipTheme | `game/ui/renderer/game_renderer` | Simple |
| ADR-UI2-004 | BattleOrchestrator Mixing Layer Concerns | `game/ui/orchestration/battle_o` | N |
| ADR-UI1-005 | Near-God Classes (500-1000 lines) | `Unknown` | Simple |
| ADR-UI1-006 | Inconsistent Cross-Layer Import Document | `Unknown` | Simple |
| CON-FND-001 | Inconsistent Verb Prefix for Retrieval M | `game/ai/combat_utils.py:50-140` | Simple |
| CON-FND-002 | Mixed Boolean Naming Patterns | `game/ai/interfaces/controllabl` | Medium |
| CON-FND-006 | Inconsistent Docstring Format | `Unknown` | Simple |
| CON-FND-007 | Import Organization Variations | `Unknown` | Simple |
| CON-FND-009 | Inconsistent Method Visibility Conventio | `game/research/ui/research_rend` | N |
| CON-FND-011 | Singleton Pattern vs Dependency Injectio | `game/ai/strategy_manager.py:20` | Medium |
| CON-FND-012 | game/core/ - Internal Consistency Good | `game/core/` | Simple |
| CON-FND-013 | game/ai/ - Internal Consistency Good | `game/ai/` | Simple |
| CON-FND-016 | Camera Protocol Usage | `game/research/ui/research_scen` | Simple |
| CON-SIM-007 | Inconsistent Method Verb Prefixes | `Unknown` | Simple |
| CON-SIM-008 | Inconsistent Parameter Naming for Ship R | `Unknown` | Simple |
| CON-SIM-009 | Inconsistent Boolean Naming Patterns | `Unknown` | Simple |
| CON-SIM-010 | Magic Numbers in Ship/Component Initiali | `game/simulation/entities/ship.` | Simple |
| CON-SIM-011 | Inconsistent Use of dataclass vs Manual  | `game/simulation/` | Simple |
| CON-SIM-012 | Inconsistent Error Handling Strategy | `Unknown` | Medium |
| CON-SIM-013 | Inconsistent Manager/Service/Helper Clas | `game/simulation/` | Medium |
| CON-SIM-014 | Inconsistent __init__.py Export Patterns | `game/simulation/services/__ini` | Simple |
| CON-STR-005 | Inconsistent Boolean Naming Prefixes | `game/strategy/data/fleet.py` | Simple |
| CON-STR-006 | Inconsistent Docstring Format | `Unknown` | Medium |
| CON-STR-007 | Inconsistent Import Organization | `game/strategy/engine/command_h` | Simple |
| CON-STR-008 | Mixed Parameter Ordering Conventions | `game/strategy/validation/colon` | None |
| CON-STR-009 | Inconsistent `__init__.py` Export Patter | `game/strategy/*/` | Simple |
| CON-STR-010 | Inconsistent Use of Dataclass vs Regular | `game/strategy/data/` | None |
| CON-STR-011 | Inconsistent Error Message Format | `game/strategy/systems/save_gam` | Simple |
| CON-STR-012 | Magic Numbers Not Extracted to Constants | `game/strategy/formulas/habitab` | Simple |
| CON-UI2-006 | Inconsistent Docstring Styles | `Unknown` | Simple |
| CON-UI2-007 | Inconsistent Private Member Naming | `game/ui/services/input_mapper.` | Simple |
| CON-UI2-008 | Inconsistent Error Handling Patterns | `game/ui/services/ship_io.py` | Simple |
| CON-UI2-009 | Inconsistent Import Organization | `Unknown` | Simple |
| CON-UI2-010 | Magic Numbers in Renderer | `game/ui/renderer/game_renderer` | Simple |
| CON-UI2-011 | Inconsistent Boolean Parameter Naming | `game/ui/services/battle_factor` | Simple |
| CON-UI2-012 | Inconsistent Method Prefix Verbs | `game/ui/assets/ship_theme_mana` | Simple |
| CON-UI1-007 | Inconsistent Import Organization | `Unknown` | Simple |
| CON-UI1-008 | Mixed Boolean Naming Conventions | `game/ui/screens/` | Simple |
| CON-UI1-009 | Inconsistent Private Method Prefix Usage | `game/ui/panels/` | Simple |
| CON-UI1-010 | Inconsistent Window Class Inheritance | `game/ui/screens/` | Simple |
| CON-UI1-011 | Missing UIConfig Constants for Common Va | `game/ui/screens/` | Simple |
| CON-UI1-012 | Inconsistent Error Handling Granularity | `game/ui/screens/` | Simple |
| CON-UI1-013 | Inconsistent Logging Import Patterns | `game/ui/screens/` | Simple |
| CON-UI1-014 | Inconsistent kill() Method Implementatio | `game/ui/panels/` | Simple |
| DUP-FND-003 | StrategyManager and StrategyMetadataServ | `game/ai/strategy_manager.py:63` | N |
| DUP-FND-004 | Position Access Patterns in AI Module | `game/ai/behaviors.py` | Simple |
| DUP-FND-005 | Serialization Pattern (to_dict/from_dict | `game/research/data/research_tr` | Simple |
| DUP-SIM-005 | Target Validation Pattern Duplication | `game/simulation/combat/targeti` | Simple |
| DUP-SIM-006 | Component Iteration Pattern | `game/simulation/entities/ship.` | Simple |
| DUP-SIM-007 | UI Row Generation Pattern | `game/simulation/components/abi` | Medium |
| DUP-SIM-008 | Physics Constants Duplication | `game/simulation/entities/ship_` | Simple |
| DUP-SIM-009 | Registries DI Guard Clause Pattern | `game/simulation/entities/ship.` | N |
| DUP-SIM-010 | Projectile Type Check Pattern | `game/simulation/combat/targeti` | N |
| DUP-STR-004 | Distance Calculation From Center Repeate | `Unknown` | Simple |
| DUP-STR-005 | Density Primitive Gaussian Falloff Patte | `Unknown` | Simple |
| DUP-STR-006 | Fleet-Like Object Creation for Pathfindi | `Unknown` | Simple |
| DUP-STR-007 | Roman Numeral Conversion Delegation | `Unknown` | N |
| DUP-UI2-013 | Battle Factory Helper Pattern | `game/ui/services/battle_factor` | None |
| DUP-UI2-014 | DTO Conversion Method Structure | `game/ui/services/battle_ui_ser` | None |
| DUP-UI2-015 | Image Loading Exception Handling Pattern | `game/ui/assets/ship_theme_mana` | Simple |
| DUP-UI2-016 | Empty __init__.py Files | `game/ui/renderer/__init__.py` | Simple |
| DUP-UI1-006 | Duplicate Portrait Loading Logic | `game/ui/screens/design_image_h` | Simple |
| DUP-UI1-007 | World-to-Screen Coordinate Transforms | `Unknown` | None |
| DUP-UI1-008 | Filter/Sort Pattern Duplication | `Unknown` | Medium |
| DUP-UI1-009 | Event Router Pattern Similarity | `game/ui/screens/workshop_event` | None |
| LEG-FND-005 | Unused hex_lerp and hex_linedraw Functio | `game/core/hex_math.py:224-250` | Simple |
| LEG-FND-006 | is_camera TypeGuard Never Used | `game/core/protocols.py:577-579` | Simple |
| LEG-FND-007 | Profiling Module Has Inconsistent API | `game/core/profiling.py:63-64` | Simple |
| LEG-FND-008 | Mock Detection Pattern in combat_utils | `game/ai/combat_utils.py:44` | Simple |
| LEG-FND-009 | PROJ Comments Reference Old Project Numb | `Unknown` | Simple |
| LEG-SIM-004 | Unused Documentation Constants in physic | `game/simulation/physics_consta` | Simple |
| LEG-SIM-005 | Singleton Pattern in ComponentCacheManag | `game/simulation/components/com` | Complex |
| LEG-SIM-006 | KNOWN_ISSUE Comment for Module Identity  | `game/simulation/components/abi` | Medium |
| LEG-SIM-007 | Excessive hasattr() Checks | `Unknown` | Medium |
| LEG-SIM-008 | Fallback Comments Suggesting Incomplete  | `Unknown` | Medium |
| LEG-UI2-004 | ComponentService.is_modifier_allowed Dup | `game/ui/services/component_ser` | Simple |
| LEG-UI2-005 | ScreenshotManager Uses Singleton Pattern | `game/ui/services/screenshot_ma` | Medium |
| LEG-UI2-006 | ShipThemeManager and SpriteManager Use S | `game/ui/assets/ship_theme_mana` | Medium |
| LEG-UI2-007 | Inconsistent DI Patterns Across Services | `game/ui/services/component_ser` | Simple |
| LEG-UI1-004 | Empty __init__ Method | `game/ui/screens/race_asset_loa` | Simple |
| LEG-UI1-005 | Disabled Feature Left as pass Statement | `game/ui/screens/builder/schema` | Simple |
| LEG-UI1-006 | get_component_at Returns None Unconditio | `game/ui/screens/builder/schema` | Simple |
| LEG-UI1-007 | Legacy Pattern Comment Without Active Co | `game/ui/screens/builder/stats_` | Simple |
| LEG-UI1-008 | Excessive hasattr Checks Suggesting Duck | `Unknown` | Complex |
| LEG-UI1-009 | Formation File Format Comment Suggests R | `game/ui/screens/formation_edit` | Simple |
| LEG-UI1-010 | Fallback Mode in Build Queue Controller | `game/ui/panels/build_queue_con` | Medium |
| TCG-FND-011 | game/core/__init__.py - No Tests Needed | `game/core/__init__.py` | None |
| TCG-FND-012 | game/ai/interfaces/__init__.py - No Test | `game/ai/interfaces/__init__.py` | None |
| TCG-FND-013 | Test Behaviors (DoNothing, StationaryFir | `game/ai/behaviors.py` | Simple |
| TCG-FND-014 | FormationBehavior Complex Logic Needs Mo | `game/ai/behaviors.py` | Medium |
| TCG-FND-015 | IControllable Interface Tests Could Be M | `game/ai/interfaces/controllabl` | Simple |
| TCG-SIM-009 | CombatEndurance Missing Boundary Tests | `game/simulation/entities/comba` | Simple |
| TCG-SIM-010 | ShipStatQuerier Not Directly Tested | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-011 | ShipValidatorHelper Not Directly Tested | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-012 | LayerData Entity Has Minimal Tests | `game/simulation/entities/layer` | Simple |
| TCG-SIM-013 | ModifierSchema Validation Not Comprehens | `game/simulation/components/mod` | Simple |
| TCG-SIM-014 | BattleConfig Tests Could Be More Thoroug | `game/simulation/battle_config.` | Simple |
| TCG-SIM-015 | PhysicsConstants Could Test Derived Valu | `game/simulation/physics_consta` | Simple |
| TCG-STR-008 | ConflictResolutionEngine draw handling | `game/strategy/engine/conflict_` | Simple |
| TCG-STR-009 | DensityMap edge cases with negative weig | `game/strategy/generation/densi` | Simple |
| TCG-STR-010 | QuickstartBuilder scenario validation | `game/strategy/quickstart_build` | Simple |
| TCG-STR-011 | GameSession from_dict missing fields han | `game/strategy/engine/game_sess` | Simple |
| TCG-UI2-007 | InputMapper Missing Tests for Numpad Key | `game/ui/services/input_mapper.` | Simple |
| TCG-UI2-008 | ScreenshotManager Missing Tests for Very | `game/ui/services/screenshot_ma` | Simple |
| TCG-UI2-009 | ShipFactory Missing Tests for Invalid De | `game/ui/services/ship_factory.` | Simple |
| TCG-UI2-010 | TkinterUtils Missing Tests for Dialog Ca | `game/ui/services/tkinter_utils` | Complex |
| TCG-UI1-015 | RaceBrowserDialog tests are minimal - on | `tests/unit/ui/test_race_browse` | Simple |
| TCG-UI1-016 | SystemSelectionWindow and PlanetSelectio | `game/ui/screens/system_selecti` | Simple |
| TCG-UI1-017 | DesignSelectorWindow tests don't cover r | `tests/unit/ui/screens/test_des` | Simple |
| TCG-UI1-018 | GalaxyTestScreen (galaxy_test/ subpackag | `game/ui/screens/galaxy_test/*.` | Simple |
| TCG-UI1-019 | race_asset_loader.py, workshop_data_load | `game/ui/screens/race_asset_loa` | Simple |
| TCG-UI1-020 | column_manager.py and fleet_report_filte | `game/ui/screens/column_manager` | Simple |
| TCG-UI1-021 | workshop_event_router.py, workshop_data_ | `game/ui/screens/workshop_event` | Simple |
| TCG-UI1-022 | setup_renderer.py has no tests (setup sc | `game/ui/screens/setup_renderer` | Simple |

### Info (42)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-005 | Well-Structured Protocol-Based AI Decoup | `game/simulation/interfaces/ai_` | N |
| ADR-STR-006 | Extensive TYPE_CHECKING Imports | `Unknown` | N |
| ADR-UI2-005 | TYPE_CHECKING Blocks Used Appropriately | `Unknown` | N |
| ADR-UI1-007 | Proper Architecture Patterns Observed | `Unknown` | Unknown |
| CON-FND-003 | Class Suffix Patterns | `Unknown` | N |
| CON-FND-010 | Registry Pattern Adherence | `game/core/registry.py` | N |
| CON-FND-015 | game/engine/ - Internal Consistency Good | `game/engine/` | N |
| CON-SIM-015 | Ability Classes Have Consistent Pattern | `game/simulation/components/abi` | N |
| CON-SIM-016 | Validation Rules Follow Template Method  | `game/simulation/validation/shi` | N |
| CON-SIM-017 | Registry Pattern Well Implemented | `Unknown` | N |
| CON-SIM-018 | Projectile State Inconsistent with Ship  | `game/simulation/battle_state.p` | Simple |
| CON-SIM-019 | Consistent Use of PROJ- References in Co | `Unknown` | N |
| CON-STR-013 | Intentional Pattern Variations | `game/strategy/data/pathfinding` | N |
| CON-STR-014 | Well-Organized Facade Pattern | `game/strategy/facade/` | N |
| CON-UI2-013 | Different Service Class Suffixes | `game/ui/services/` | None |
| CON-UI2-014 | Constants Module Location | `game/ui/colors.py` | Simple |
| CON-UI1-015 | Natural Variation in Class Structure | `game/ui/screens/builder/` | N |
| CON-UI1-016 | Two Panel Patterns Coexist | `game/ui/panels/` | N |
| CON-UI1-017 | Module-Level Functions vs Class Methods | `game/ui/screens/` | N |
| CON-UI1-018 | Facade Pattern Used Correctly | `game/ui/screens/strategy_scree` | N |
| DUP-FND-006 | Well-Consolidated Distance Calculations | `game/core/math.py:143-149` | N |
| DUP-SIM-011 | Well-Factored Delegation Patterns | `game/simulation/entities/ship_` | N |
| DUP-SIM-012 | Ability Aggregation Well Centralized | `game/simulation/entities/abili` | N |
| DUP-STR-008 | Consistent Use of Component Inspector | `Unknown` | N |
| DUP-STR-009 | DTO Pattern Well-Applied | `Unknown` | N |
| DUP-UI2-017 | Well-Consolidated Tkinter Utilities | `game/ui/services/tkinter_utils` | None |
| DUP-UI1-010 | Previously Resolved Duplication (DUP-UI1 | `game/ui/screens/test_lab/forma` | N |
| LEG-FND-010 | Singleton Pattern is Intentional for Inf | `game/core/singleton.py` | Simple |
| LEG-SIM-009 | Clean Migration Indicators | `Unknown` | N |
| LEG-SIM-010 | Healthy Ability System Architecture | `game/simulation/components/abi` | N |
| LEG-UI2-008 | hasattr Checks for Scene/UI Attributes | `game/ui/services/screenshot_ma` | Simple |
| LEG-UI1-011 | Module-Level Singleton Pattern | `game/ui/screens/builder_utils.` | None |
| LEG-UI1-012 | Backward Compatibility Comment in Docume | `game/ui/screens/fleet_report_f` | None |
| TCG-FND-016 | Test File Organization Follows Good Patt | `Unknown` | None |
| TCG-FND-017 | Research Module Has Strong Test Coverage | `game/research/` | None |
| TCG-FND-018 | AI Module Has Good Coverage But Could Us | `game/ai/` | Medium |
| TCG-SIM-016 | Ability Base Class Tests Are Exemplary | `game/simulation/components/abi` | N |
| TCG-SIM-017 | Damage Calculator Tests Are Comprehensiv | `game/simulation/combat/damage_` | N |
| TCG-STR-012 | Test organization could be improved | `tests/unit/strategy/` | Simple |
| TCG-UI2-011 | Test Organization Observation | `tests/unit/ui/` | N |
| TCG-UI1-023 | Test files use bypass-init pattern consi | `Unknown` | N |
| TCG-UI1-024 | Some panels have excellent test coverage | `tests/unit/ui/panels/` | N |


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
| Total Findings | 274 |
| Critical | 17 |
| Major | 96 |
| Minor | 119 |
| Info | 42 |
| Agents Used | 24 |

---
*Report generated: 2026-02-14 03:48*
