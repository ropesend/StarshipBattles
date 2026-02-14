# Review Report: 2026-02-13_223809_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-13
- **Type:** Review
- **Description:** 
- **Agents Used:** 22

## Executive Summary
- **Total Findings:** 243
- **Critical:** 12 | **Major:** 83 | **Minor:** 108 | **Info:** 40
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Inconsistent Return Type for Not-Found Scenarios
**ID:** CON-SIM-001
**Agent:** Consistency Simulation
**Location:** `game/simulation/components/component.py:679-704`
**Effort:** Medium

**ID:** CON-SIM-001
**Location:** `game/simulation/components/component.py:679-704` vs `game/simulation/services/battle_service.py:274-289`
**Issue:** `create_component()` returns `None` on not-found, while similar factory methods like `BattleService.get_winner()` have explicit return type documentation. However, `add_modifier()` returns `False` on not-found (boolean). This creates API inconsistency: some methods return None, others return False for failure cases.
**Impact:** Callers must know e...

---

### 2. CRITICAL: Inconsistent Return Type for Not-Found Cases
**ID:** CON-STR-001
**Agent:** Consistency Strategy
**Location:** `Unknown`
**Effort:** Medium

**ID:** CON-STR-001
**Location:** Multiple files
**Issue:** Some methods return `None` for not-found cases while similar methods raise exceptions. The `Galaxy.get_planet_by_id()` returns `None`, while `RaceConfig.load()` also returns `None`, but `GameSession.from_dict()` raises `PersistenceException` for missing fields. This inconsistency in error handling patterns within the same layer can lead to bugs when callers assume one pattern but encounter another.
**Impact:** Callers may not handle `No...

---

### 3. CRITICAL: Inconsistent Dependency Injection Patterns Across Services
**ID:** CON-UI2-001
**Agent:** Consistency Ui Framework
**Location:** `game/ui/services/`
**Effort:** Medium

**ID:** CON-UI2-001
**Location:** `game/ui/services/` (multiple files)
**Issue:** The service layer has three incompatible DI patterns:
1. **Strict DI (required):** `VehicleClassService.__init__` raises `ValueError` if `registry_provider` is None
2. **Lazy DI (optional with fallback):** `ComponentService.__init__` accepts `None` and calls `get_default_registry_provider()` lazily
3. **Class-level default:** `ValidationService.__init__` accepts `None` and uses `get_or_create_validator()` in a gett...

---

### 4. CRITICAL: Duplicate Component Ability Extraction Pattern
**ID:** DUP-STR-001
**Agent:** Duplication Strategy
**Location:** `game/strategy/engine/harvesting_engine.py:30-75, 169-211`
**Effort:** Medium

**ID:** DUP-STR-001
**Location:** `game/strategy/engine/harvesting_engine.py:30-75, 169-211` AND `game/strategy/data/fleet_capability_calculator.py:14-18, 31-44, 172-186`
**Issue:** The pattern for extracting abilities from component entries (inline dict abilities vs registry lookup) is duplicated across multiple files. `HarvestingEngine` has `get_harvester_info()`, `get_harvester_from_registry()`, `_get_storage_info()`, `_get_storage_from_registry()`. `FleetCapabilityCalculator` uses `ship_has_...

---

### 5. CRITICAL: Tkinter Root Initialization Duplicated Across 4 Files
**ID:** DUP-UI2-001
**Agent:** Duplication Ui Framework
**Location:** `Unknown`
**Effort:** Simple

**ID:** DUP-UI2-001
**Location:**
- `game/ui/services/ship_io.py:20-32`
- `game/ui/services/screenshot_manager.py:95-104`
- `game/ui/screens/formation_editor.py:23-30`
- `game/ui/screens/workshop_ship_io.py:18-26`

**Issue:** Identical Tkinter initialization pattern with try/except blocks is duplicated across 4 files. Each file separately:
1. Creates a `tkinter.Tk()` instance
2. Calls `withdraw()` to hide it
3. Handles `TclError` and `RuntimeError` exceptions
4. Sets a module-level variable to N...

---

### 6. CRITICAL: Screenshot Toast Notification Pattern Duplicated in 3+ Locations
**ID:** DUP-UI1-001
**Agent:** Duplication Ui Screens
**Location:** `game/ui/screens/planet_list_window.py:412-424`
**Effort:** Simple

**ID:** DUP-UI1-001
**Location:** `game/ui/screens/planet_list_window.py:412-424` AND `game/ui/screens/build_queue_screen.py:1055-1068` AND `game/ui/screens/strategy_input_handler.py:868-881`
**Issue:** The `_show_screenshot_toast()` method is implemented nearly identically in three different files. All three create a UIMessageWindow with similar dimensions, positioning (center, y=80), HTML message format, and exception handling. The only differences are:
- Which manager reference they use (self...

---

### 7. CRITICAL: AIController Integration with StrategyManager Missing Edge Case Tests
**ID:** TCG-FND-001
**Agent:** Test Coverage Foundation
**Location:** `game/ai/controller.py`
**Effort:** Medium

**ID:** TCG-FND-001
**Location:** `game/ai/controller.py` (production) / `tests/unit/ai/test_ai.py` (test gap)
**Issue:** AIController.update() has complex behavior involving target selection, strategy resolution, and behavior dispatch. While basic scenarios are tested, critical edge cases are missing:
- No tests for what happens when StrategyManager returns a strategy with missing policy references
- No tests for behavior fallback when an unknown strategy type is used
- No tests for race condit...

---

### 8. CRITICAL: Commands Module Has No Dedicated Unit Tests
**ID:** TCG-STR-001
**Agent:** Test Coverage Strategy
**Location:** `game/strategy/engine/commands.py`
**Effort:** Simple

**ID:** TCG-STR-001
**Location:** `game/strategy/engine/commands.py` (production) / None (test gap)
**Issue:** The `commands.py` module defines 19 command dataclasses (IssueColonizeCommand, IssueMoveCommand, IssueBuildShipCommand, IssueInterceptCommand, IssueJoinFleetCommand, QueueColonizeMissionCommand, ClearFleetOrdersCommand, IssueTransferCommand, and 11 superweapon commands). None of these have dedicated unit tests for their construction, validation, or dataclass behavior.
**Impact:** Comman...

---

### 9. CRITICAL: Physics Module Has No Unit Tests
**ID:** TCG-STR-002
**Agent:** Test Coverage Strategy
**Location:** `game/strategy/data/physics.py`
**Effort:** Simple

**ID:** TCG-STR-002
**Location:** `game/strategy/data/physics.py` (production) / None (test gap)
**Issue:** The `physics.py` module contains `SectorEnvironment` class and `calculate_incident_radiation()` function that implements radiation falloff physics (1/r^2.1). No unit tests exist for this module despite it containing numerical calculations that could have off-by-one errors, division by zero risks, or incorrect falloff behavior.
**Impact:** Radiation calculations affect planet habitability a...

---

### 10. CRITICAL: No Tests for game_renderer.py (Ship Rendering Logic)
**ID:** TCG-UI2-001
**Agent:** Test Coverage Ui Framework
**Location:** `game/ui/renderer/game_renderer.py`
**Effort:** Medium

**ID:** TCG-UI2-001
**Location:** `game/ui/renderer/game_renderer.py` (production) / No corresponding test file
**Issue:** The `game_renderer.py` module contains the `draw_ship()` function which renders ships with theme images, layers, components, and direction indicators. This is a visually critical path with zoom-dependent behavior, culling logic, and complex coordinate transformations. There are no unit tests for this module.
**Impact:** Visual bugs in ship rendering would go undetected. The ...

---


## Findings by Severity

### Critical (12)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CON-SIM-001 | Inconsistent Return Type for Not-Found S | `game/simulation/components/com` | Medium |
| CON-STR-001 | Inconsistent Return Type for Not-Found C | `Unknown` | Medium |
| CON-UI2-001 | Inconsistent Dependency Injection Patter | `game/ui/services/` | Medium |
| DUP-STR-001 | Duplicate Component Ability Extraction P | `game/strategy/engine/harvestin` | Medium |
| DUP-UI2-001 | Tkinter Root Initialization Duplicated A | `Unknown` | Simple |
| DUP-UI1-001 | Screenshot Toast Notification Pattern Du | `game/ui/screens/planet_list_wi` | Simple |
| TCG-FND-001 | AIController Integration with StrategyMa | `game/ai/controller.py` | Medium |
| TCG-STR-001 | Commands Module Has No Dedicated Unit Te | `game/strategy/engine/commands.` | Simple |
| TCG-STR-002 | Physics Module Has No Unit Tests | `game/strategy/data/physics.py` | Simple |
| TCG-UI2-001 | No Tests for game_renderer.py (Ship Rend | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI1-001 | No Tests for Builder Subsystem (14 Produ | `game/ui/screens/builder/*.py` | Complex |
| TCG-UI1-002 | No Tests for Ship Detail Panel | `game/ui/panels/ship_detail_pan` | Medium |

### Major (83)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Research UI Layer Contains Late Import o | `game/research/ui/research_scen` | Medium |
| ADR-FND-002 | Research UI Subdirectory Uses Pygame Dir | `game/research/ui/research_cont` | Complex |
| ADR-SIM-001 | Simulation Depends on game.engine (Physi | `game/simulation/entities/ship.` | Medium |
| ADR-SIM-002 | Simulation Depends on game.engine (Spati | `game/simulation/systems/battle` | Medium |
| ADR-SIM-003 | Circular Import Risk - Ship and Modifier | `game/simulation/entities/ship.` | Medium |
| ADR-STR-001 | Strategy Layer Imports AI Layer (Permitt | `game/strategy/adapters/simulat` | Simple |
| ADR-STR-002 | Galaxy Class Approaching God Class Terri | `game/strategy/data/galaxy.py:1` | Complex |
| ADR-UI2-001 | ShipFactory uses pygame.math.Vector2 in  | `game/ui/services/ship_factory.` | Simple |
| ADR-UI2-002 | ShipIO module-level Tkinter initializati | `game/ui/services/ship_io.py:20` | Medium |
| ADR-UI2-003 | Camera class uses pygame.math.Vector2 in | `game/ui/renderer/camera.py:14,` | Medium |
| CON-FND-001 | Inconsistent Singleton Pattern Usage | `game/core/registry.py:379-397` | Medium |
| CON-FND-002 | Inconsistent Return Type for Missing Ite | `game/core/json_utils.py:33-67` | Simple |
| CON-FND-003 | Mixed Method Naming for Accessor Functio | `game/ai/interfaces/controllabl` | Complex |
| CON-FND-004 | Inconsistent Parameter Ordering for Simi | `game/ai/combat_utils.py:66-96` | Simple |
| CON-FND-005 | Logging Pattern Inconsistency | `game/ai/combat_utils.py:19` | Simple |
| CON-SIM-002 | Inconsistent Method Verb Prefixes for Re | `Unknown` | Medium |
| CON-SIM-003 | Mixed Docstring Formats | `Unknown` | Complex |
| CON-SIM-004 | Inconsistent Error Handling Patterns | `game/simulation/battle_control` | Medium |
| CON-SIM-005 | Ability Class Naming Inconsistency | `game/simulation/components/abi` | Complex |
| CON-SIM-006 | Inconsistent Use of TYPE_CHECKING Guard | `game/simulation/services/desig` | Simple |
| CON-STR-002 | Mixed Verb Prefixes for Similar Operatio | `game/strategy/data/fleet.py` | Medium |
| CON-STR-003 | Inconsistent Docstring Presence and Form | `Unknown` | Complex |
| CON-STR-004 | Inconsistent Constructor DI Pattern Appl | `game/strategy/engine/` | Medium |
| CON-STR-005 | Mixed Static Methods and Instance Method | `game/strategy/services/ship_st` | Medium |
| CON-STR-006 | Inconsistent Type Hints on Module-Level  | `game/strategy/engine/harvestin` | Simple |
| CON-UI2-002 | Inconsistent Return Value Conventions fo | `game/ui/services/ship_io_adapt` | Medium |
| CON-UI2-003 | Singleton Pattern Inconsistency - instan | `game/ui/renderer/sprites.py:8-` | Simple |
| CON-UI2-004 | Mixed Docstring Styles | `Unknown` | Simple |
| CON-UI2-005 | Module-Level Side Effects in ship_io.py | `game/ui/services/ship_io.py:20` | Medium |
| DUP-FND-001 | Singleton Clear Pattern Duplication | `game/core/profiling.py:39-42` | Medium |
| DUP-FND-002 | Strategy Metadata Dual Service Pattern | `game/core/strategy_metadata.py` | Complex |
| DUP-FND-003 | JSON Loading with Fallback Pattern | `game/core/resources.py:54-98` | Simple |
| DUP-SIM-001 | Ability `__init__` Pattern Duplication A | `game/simulation/components/abi` | Simple |
| DUP-SIM-002 | Repeated `sync_data` Pattern Across Prop | `game/simulation/components/abi` | Simple |
| DUP-SIM-003 | Repeated `recalculate` Pattern for Singl | `game/simulation/components/abi` | Medium |
| DUP-SIM-004 | `to_dict` / `from_dict` Serialization Pa | `game/simulation/battle_state.p` | Medium |
| DUP-STR-002 | Duplicated "Find Nearest" System Pattern | `game/strategy/data/pathfinding` | Simple |
| DUP-STR-003 | Duplicated Star Generation Logic | `game/strategy/data/stars.py:37` | Medium |
| DUP-STR-004 | Ship Spawning Duplication in ProductionE | `game/strategy/engine/productio` | Simple |
| DUP-STR-005 | Duplicated Complex Spawning Logic | `game/strategy/engine/productio` | Simple |
| DUP-UI2-002 | Battle Factory Functions Follow Identica | `game/ui/services/battle_factor` | Medium |
| DUP-UI2-003 | Service DI Pattern Duplicated with Incon | `Unknown` | Medium |
| DUP-UI2-004 | BattleUIService Repeated Null-Check Patt | `game/ui/services/battle_ui_ser` | Simple |
| DUP-UI1-002 | Column Manager Fragmentation Across Wind | `game/ui/screens/column_manager` | Medium |
| DUP-UI1-003 | Filter State Management Pattern Repeated | `game/ui/screens/fleet_report_f` | Medium |
| DUP-UI1-004 | Compact Number Formatting Logic Isolated | `game/ui/panels/planet_report_p` | Simple |
| LEG-FND-001 | Excessive getattr() Fallbacks in AI Comb | `game/ai/combat_utils.py:44-212` | Medium |
| LEG-FND-002 | Singleton Pattern Still Used for Core Se | `game/core/singleton.py` | Complex |
| LEG-SIM-001 | Module Identity Drift Fallback in Abilit | `game/simulation/components/abi` | Medium |
| LEG-SIM-002 | Singleton Pattern in Component Cache Man | `game/simulation/components/com` | Complex |
| LEG-SIM-003 | Dead Fallback Code in BattleController._ | `game/simulation/battle_control` | Simple |
| LEG-STR-001 | Backward Compatibility Fallback in GameS | `game/strategy/engine/game_sess` | Medium |
| LEG-STR-002 | Legacy Behavior Comments in FleetOrderPr | `game/strategy/engine/fleet_ord` | Medium |
| LEG-STR-003 | Backward Compatibility Default in Planet | `game/strategy/data/planet.py:3` | Simple |
| LEG-STR-004 | Backward Compatibility in FleetNavigatio | `game/strategy/services/fleet_n` | Medium |
| LEG-STR-005 | Legacy Production Items in ProductionEng | `game/strategy/engine/productio` | Medium |
| LEG-UI2-001 | BattleOrchestrator Class Is Unused In Ga | `game/ui/orchestration/battle_o` | Simple |
| LEG-UI2-002 | IBattleUI Protocol Is Exported But Never | `game/ui/interfaces/battle_ui.p` | Simple |
| TCG-FND-002 | TargetEvaluator Rule Types Missing Compr | `game/ai/target_evaluator.py` | Medium |
| TCG-FND-003 | PhysicsBody Missing Dedicated Unit Tests | `game/engine/physics.py` | Simple |
| TCG-FND-004 | TechTree.validate_requirements() Return  | `game/research/data/tech_tree.p` | Simple |
| TCG-FND-005 | SpatialGrid Remove/Update Operations Not | `game/engine/spatial.py` | Simple |
| TCG-FND-006 | AIFactory Missing Tests | `game/ai/ai_factory.py` | Simple |
| UNK-01 | Missing integration tests for component  | `game/simulation/combat/damage_` | Unknown |
| UNK-04 | Resource consumption during combat tick  | `game/simulation/systems/resour` | Unknown |
| TCG-STR-003 | DTO Modules Have Limited Direct Unit Tes | `game/strategy/facade/dto/*.py` | Medium |
| TCG-STR-004 | FleetNavigationService Unit Tests Are Th | `game/strategy/services/fleet_n` | Medium |
| TCG-STR-005 | ShipStatsCalculator Edge Cases Untested | `game/strategy/services/ship_st` | Medium |
| TCG-STR-006 | Superweapon Command Handlers Have Limite | `game/strategy/engine/superweap` | Medium |
| TCG-STR-007 | GameSession.handle_command Has No Direct | `game/strategy/engine/game_sess` | Simple |
| TCG-UI2-002 | No Tests for battle_factories.py (Battle | `game/ui/services/battle_factor` | Simple |
| TCG-UI2-003 | config.py Has No Test Coverage | `game/ui/config.py` | Simple |
| TCG-UI2-004 | utils.py Has Thin Test Coverage | `game/ui/utils.py` | Simple |
| TCG-UI2-005 | ship_io_adapter.py Needs Error Path Test | `game/ui/services/ship_io_adapt` | Simple |
| TCG-UI1-003 | No Tests for Planet Report Panel | `game/ui/panels/planet_report_p` | Medium |
| TCG-UI1-004 | No Tests for Design Report Panel | `game/ui/panels/design_report_p` | Simple |
| TCG-UI1-005 | No Tests for Strategy Widgets (Atmospher | `game/ui/panels/strategy_widget` | Simple |
| TCG-UI1-006 | No Tests for System Tree Panel | `game/ui/panels/system_tree_pan` | Medium |
| TCG-UI1-007 | No Tests for Component Modifier Grid Pan | `game/ui/panels/component_modif` | Medium |
| TCG-UI1-008 | No Tests for Modifier Impact Grid | `game/ui/panels/modifier_impact` | Simple |
| TCG-UI1-009 | No Tests for Race Theme/Portrait/Flag Ga | `game/ui/panels/race_theme_gall` | Medium |
| TCG-UI1-010 | No Tests for Formation Editor Subsystem | `game/ui/screens/formation/*.py` | Simple |
| TCG-UI1-011 | Galaxy Test Screen No Tests | `game/ui/screens/galaxy_test/*.` | Simple |

### Minor (108)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | TYPE_CHECKING Block in ai_factory.py Imp | `game/ai/ai_factory.py:27-29` | Simple |
| ADR-SIM-004 | Circular Import Risk - ShipSerializer an | `game/simulation/entities/ship_` | Simple |
| ADR-SIM-005 | God Class Indicator - Ship Class (810 LO | `game/simulation/entities/ship.` | Complex |
| ADR-SIM-006 | God Class Indicator - Component Class (7 | `game/simulation/components/com` | Medium |
| ADR-STR-003 | Production Engine Approaching 500+ LOC | `game/strategy/engine/productio` | Medium |
| ADR-STR-004 | FleetOrderProcessor Approaching 500+ LOC | `game/strategy/engine/fleet_ord` | Medium |
| ADR-UI2-004 | TYPE_CHECKING import of GameRegistries f | `game/ui/services/ship_factory.` | N |
| ADR-UI2-005 | BattleOrchestrator imports from engine l | `game/ui/orchestration/battle_o` | Simple |
| ADR-UI2-006 | Inconsistent use of Any type hints maski | `game/ui/services/validation_se` | Medium |
| CON-FND-006 | Inconsistent Docstring Style | `game/engine/physics.py:82-87` | Simple |
| CON-FND-007 | Type Hint Inconsistency for Vector2 | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-008 | Constants Naming - Mixed Casing for Simi | `game/core/config.py:49-91` | Simple |
| CON-FND-009 | Inconsistent Use of `clear()` vs `reset( | `game/core/registry.py:217-237` | Simple |
| CON-FND-010 | Mixed `Optional` vs `| None` Type Hint S | `game/core/registry.py:81` | Simple |
| CON-FND-011 | Incomplete `__all__` Exports | `game/core/constants.py:3-15` | Simple |
| CON-FND-012 | Inconsistent Boolean Naming - `is_` vs ` | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-013 | Error Code Enum Incomplete Coverage | `game/core/error_codes.py:52-15` | Simple |
| CON-FND-014 | Factory Function Naming Inconsistency | `game/research/ui/research_scen` | Simple |
| CON-FND-018 | Inconsistent Default Parameter Handling | `game/research/data/research_tr` | Simple |
| CON-SIM-007 | Boolean Parameter Naming | `Unknown` | Simple |
| CON-SIM-008 | Inconsistent Private Member Naming | `Unknown` | Simple |
| CON-SIM-009 | Magic Numbers in Physics Calculations | `game/simulation/entities/ship_` | Simple |
| CON-SIM-010 | Inconsistent sync_data Method Implementa | `game/simulation/components/abi` | Simple |
| CON-SIM-011 | Inconsistent Default Parameter Values | `Unknown` | Simple |
| CON-SIM-012 | Component Type Checking via String vs is | `game/simulation/entities/ship_` | Medium |
| CON-SIM-013 | Inconsistent Use of Dataclass Fields | `game/simulation/battle_state.p` | Simple |
| CON-SIM-014 | Inconsistent List Return Types | `game/simulation/entities/ship.` | Simple |
| CON-SIM-015 | Callback Naming Convention | `game/simulation/battle_control` | Simple |
| CON-SIM-016 | Inconsistent Context Parameter Usage | `game/simulation/entities/ship.` | Medium |
| CON-SIM-017 | Formula String Convention | `game/simulation/components/abi` | Simple |
| CON-STR-007 | Inconsistent Private Method Naming Conve | `game/strategy/data/galaxy.py` | Simple |
| CON-STR-008 | Inconsistent Import Organization | `Unknown` | Simple |
| CON-STR-009 | Inconsistent Boolean Property Naming | `game/strategy/data/fleet.py` | Simple |
| CON-STR-010 | Inconsistent Error Code Usage | `game/strategy/validation/colon` | Medium |
| CON-STR-011 | Inconsistent to_dict/from_dict Pattern I | `Unknown` | Medium |
| CON-STR-012 | Inconsistent Use of TYPE_CHECKING Block | `Unknown` | Simple |
| CON-STR-013 | Inconsistent Constant Naming | `game/strategy/data/stars.py` | Simple |
| CON-UI2-006 | Inconsistent Method Naming - get_ vs loa | `Unknown` | Simple |
| CON-UI2-007 | Inconsistent Type Hint Coverage | `game/ui/services/ship_io.py:42` | Simple |
| CON-UI2-008 | Inconsistent Error Logging Patterns | `game/ui/services/ship_io.py:72` | Simple |
| CON-UI2-009 | Inconsistent Private Method Naming | `Unknown` | Simple |
| CON-UI2-010 | Boolean Parameter Naming Inconsistency | `game/ui/services/battle_factor` | Simple |
| CON-UI2-011 | Inconsistent Import Organization | `game/ui/services/ship_io.py:1-` | Simple |
| CON-UI2-012 | Magic Numbers in Rendering Code | `game/ui/renderer/game_renderer` | Simple |
| DUP-FND-004 | Serialization Method Naming Convention | `game/core/input_actions.py:307` | Simple |
| DUP-FND-005 | Distance Calculation Access Patterns | `game/ai/combat_utils.py:142-16` | Simple |
| DUP-FND-006 | Flee Direction Calculation | `game/ai/behaviors.py:70-84` | N |
| DUP-FND-007 | Camera Factory Pattern | `game/research/ui/research_scen` | Simple |
| DUP-SIM-005 | `get_ui_rows` Return Pattern Duplication | `game/simulation/components/abi` | Simple |
| DUP-SIM-006 | Registry Null Check Pattern | `game/simulation/entities/ship.` | Simple |
| DUP-SIM-007 | Ability Aggregation Logic Split Between  | `game/simulation/entities/abili` | Simple |
| DUP-SIM-008 | WeaponAbility Formula Handling Pattern | `game/simulation/components/abi` | Simple |
| DUP-SIM-009 | SeekerWeaponAbility Property Pattern | `game/simulation/components/abi` | Simple |
| DUP-SIM-010 | LayerRestrictionDefinitionRule Block/All | `game/simulation/validation/shi` | Medium |
| DUP-STR-006 | Resource Consumption Loop Pattern | `game/strategy/data/fleet_resou` | Simple |
| DUP-STR-007 | has_resources/consume Pattern in FleetRe | `game/strategy/data/fleet_resou` | Simple |
| DUP-STR-008 | Duplicate Fleet-Like Proxy Pattern | `game/strategy/data/pathfinding` | Simple |
| DUP-STR-009 | Serialization to_dict/from_dict Pattern  | `game/strategy/data/stars.py:48` | Complex |
| DUP-STR-010 | Layer Iteration Pattern | `game/strategy/engine/harvestin` | Simple |
| DUP-UI2-005 | Image Loading Pattern Repeated Without C | `Unknown` | Medium |
| DUP-UI2-006 | Ship Cloning Logic in create_hypothetica | `game/ui/services/battle_factor` | Simple |
| DUP-UI2-007 | Singleton Pattern with Same Structure | `Unknown` | N |
| DUP-UI1-005 | RaceThemeGallery Not Using BaseGallery | `game/ui/panels/race_theme_gall` | Simple |
| DUP-UI1-006 | Report Panel Pattern Similarity | `game/ui/panels/planet_report_p` | Medium |
| DUP-UI1-007 | Portrait/Image Loading Logic Scattered | `game/ui/panels/design_report_p` | Simple |
| DUP-UI1-008 | Sidebar Builder Pattern Could Be General | `game/ui/screens/planet_list_si` | Medium |
| LEG-FND-003 | Stale PROJ Reference Comments | `Unknown` | Simple |
| LEG-FND-004 | Defensive hasattr() Checks in AI Layer | `game/ai/interfaces/controllabl` | Simple |
| LEG-FND-005 | Unused Error Codes | `game/core/error_codes.py:63-64` | Simple |
| LEG-FND-006 | PhysicsBody.update() Rarely Used | `game/engine/physics.py:82-101` | Simple |
| LEG-SIM-004 | Defensive hasattr Checks for Attributes  | `Unknown` | Simple |
| LEG-SIM-005 | getattr with Defaults for Always-Present | `Unknown` | Simple |
| LEG-SIM-006 | Stale Docstring Reference to Removed Fal | `game/simulation/services/modif` | Simple |
| LEG-SIM-007 | Similar Stale Documentation in vehicle_d | `game/simulation/services/vehic` | Simple |
| LEG-SIM-008 | Fallback Comment in battle_engine.py | `game/simulation/systems/battle` | Simple |
| LEG-SIM-009 | Unused Parameter in _apply_results_to_fl | `game/simulation/battle_control` | Simple |
| LEG-STR-006 | Unused Import StarType in galaxy.py | `game/strategy/data/galaxy.py:1` | Simple |
| LEG-STR-007 | Reserved/Placeholder Field sprite_previe | `game/strategy/data/design_meta` | Simple |
| LEG-STR-008 | Backward Compatibility Comment in race_c | `game/strategy/data/race_config` | Simple |
| LEG-STR-009 | Backward Compatibility Comment in game_c | `game/strategy/engine/game_conf` | Simple |
| LEG-STR-010 | Support for Old Layer Format in DesignMe | `game/strategy/data/design_meta` | Simple |
| LEG-UI2-003 | WHITE and BLACK Color Constants Are Dead | `game/ui/colors.py:7-8` | Simple |
| LEG-UI2-004 | get_visible_bounding_box Function Has No | `game/ui/utils.py:97-113` | Simple |
| TCG-FND-007 | Resources Module (game/core/resources.py | `game/core/resources.py` | Simple |
| TCG-FND-008 | ResearchService.estimate_turns_to_breakt | `game/research/systems/research` | Simple |
| TCG-FND-009 | Profiler Test Coverage Could Be Enhanced | `game/core/profiling.py` | Simple |
| TCG-FND-010 | Controllable Interface Adapter Test Enha | `game/ai/interfaces/controllabl` | Simple |
| UNK-02 | Defense ability classes undertested in i | `game/simulation/components/abi` | Unknown |
| UNK-03 | Crew ability classes have minimal test c | `game/simulation/components/abi` | Unknown |
| UNK-05 | BattleLogger tests exist but outside sim | `tests/unit/combat/test_battle_` | Unknown |
| UNK-06 | Formula system exception handling edge c | `game/simulation/formula_system` | Unknown |
| UNK-07 | ShipStatQuerier class lacks dedicated te | `game/simulation/entities/ship_` | Unknown |
| UNK-08 | ship_serialization module could use erro | `game/simulation/entities/ship_` | Unknown |
| TCG-STR-008 | QuickstartBuilder Has Thin Test Coverage | `game/strategy/quickstart_build` | Simple |
| TCG-STR-009 | DesignMetadata Tests Are Sparse | `game/strategy/data/design_meta` | Simple |
| TCG-STR-010 | FleetResourceAggregator Edge Cases | `game/strategy/data/fleet_resou` | Simple |
| TCG-STR-011 | PlacementStrategies Lack Regression Test | `game/strategy/generation/place` | Simple |
| TCG-STR-012 | RegionClassifier Tests Thin | `game/strategy/generation/regio` | Simple |
| TCG-STR-013 | TransferValidator Missing Specific Edge  | `game/strategy/validation/trans` | Simple |
| TCG-STR-014 | ColonizeValidator "Any Planet" Logic Com | `game/strategy/validation/colon` | Medium |
| TCG-UI2-006 | BattleOrchestrator Missing Edge Case Tes | `game/ui/orchestration/battle_o` | Simple |
| TCG-UI2-007 | screenshot_manager.py Tests Could Mock L | `game/ui/services/screenshot_ma` | Medium |
| TCG-UI2-008 | colors.py Has Test Coverage but Missing  | `game/ui/colors.py` | Simple |
| TCG-UI1-012 | Incomplete Edge Case Testing for BattleS | `tests/unit/ui/test_battle_scre` | Simple |
| TCG-UI1-013 | Workshop Screen Tests Are Mock-Heavy | `tests/unit/ui/screens/test_wor` | Medium |
| TCG-UI1-014 | Strategy Screen Missing Superweapon Targ | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-015 | Build Queue Screen Missing Drag Handler  | `tests/unit/ui/screens/test_bui` | Medium |
| TCG-UI1-016 | Test Lab Scene Tests Cover Only Logic, N | `tests/unit/ui/test_lab_scene/` | Medium |

### Info (40)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-004 | Core Layer Properly Isolates Strategy an | `game/core/constants.py:84` | N |
| ADR-SIM-007 | TYPE_CHECKING Used Extensively for Layer | `Unknown` | N |
| ADR-STR-005 | Cross-Layer Imports via TYPE_CHECKING (G | `Unknown` | N |
| ADR-UI2-007 | DesignLoaderAdapter directly imports Sim | `game/ui/services/design_loader` | Medium |
| ADR-UI2-008 | Screenshot manager uses hardcoded strate | `game/ui/services/screenshot_ma` | Complex |
| CON-FND-015 | Module Docstring Completeness Variation | `game/engine/spatial.py:1-6` | N |
| CON-FND-016 | Import Organization Consistency | `Unknown` | N |
| CON-FND-017 | Configuration Class vs Module Constants  | `game/core/config.py` | N |
| CON-SIM-018 | Singleton Pattern Usage | `game/simulation/components/com` | Complex |
| CON-SIM-019 | Ability Registry as Module-Level Dict | `game/simulation/components/abi` | Medium |
| CON-SIM-020 | Late Import Comments | `game/simulation/entities/ship_` | N |
| CON-STR-014 | Natural Variation in Method Signatures | `game/strategy/engine/` | None |
| CON-STR-015 | Facade vs Direct Access Pattern Variatio | `game/strategy/facade/strategy_` | None |
| CON-STR-016 | Delegate Pattern Consistency | `game/strategy/data/fleet.py` | Simple |
| CON-STR-017 | Event System Consistency | `game/strategy/events/event_typ` | None |
| CON-STR-018 | Interface Naming Convention | `game/strategy/interfaces/` | None |
| CON-UI2-013 | Inconsistent __all__ Export Patterns | `game/ui/__init__.py` | Simple |
| CON-UI2-014 | Comment Style Variation | `Unknown` | Simple |
| DUP-FND-008 | Singleton Pattern Consistency | `Unknown` | N |
| DUP-FND-009 | Combat Utils Consolidation Success | `game/ai/combat_utils.py` | N |
| DUP-SIM-011 | Consistent Use of Helper Class Pattern | `game/simulation/components/mod` | N |
| DUP-SIM-012 | Well-Factored Combat Subsystems | `game/simulation/combat/targeti` | N |
| DUP-STR-011 | Similar DTO from_X Factory Methods | `game/strategy/facade/dto/fleet` | N |
| DUP-STR-012 | NavigationState Pattern | `game/strategy/services/fleet_n` | N |
| DUP-UI2-008 | Adapter Classes Follow Consistent Patter | `Unknown` | N |
| DUP-UI1-009 | Well-Refactored Gallery System | `game/ui/panels/base_gallery.py` | N |
| DUP-UI1-010 | DesignStatsPanel Successful Extraction | `game/ui/panels/design_stats_pa` | N |
| LEG-FND-007 | Fallback Behaviors Are Intentional Desig | `game/ai/__init__.py:38-52` | N |
| LEG-SIM-010 | Documented Technical Debt in ability_man | `game/simulation/components/abi` | N |
| LEG-SIM-011 | Consistent Use of Fallback Patterns in D | `game/simulation/services/regis` | N |
| LEG-STR-011 | hasattr() Checks for Standard Attributes | `Unknown` | Medium |
| LEG-STR-012 | Placeholder Production Sources in Empire | `game/strategy/engine/empire_ec` | Simple |
| LEG-UI2-005 | Singleton Pattern Still Used in UI Layer | `Unknown` | N |
| TCG-FND-011 | Test Organization Observation | `Unknown` | Simple |
| TCG-FND-012 | TechRequirement Negation Logic Test Enha | `game/research/data/tech_node.p` | Simple |
| TCG-STR-015 | Test Organization Inconsistency | `Unknown` | Complex |
| TCG-STR-016 | Mock-Heavy Tests May Miss Integration Bu | `Unknown` | Complex |
| TCG-UI2-009 | Excellent Test Coverage on BattleUIServi | `game/ui/services/battle_ui_ser` | N |
| TCG-UI1-017 | Panels Module Missing __init__ Tests | `game/ui/panels/__init__.py` | Simple |
| TCG-UI1-018 | Test Patterns Vary Between Screen Tests | `Unknown` | Simple |


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
| Total Findings | 243 |
| Critical | 12 |
| Major | 83 |
| Minor | 108 |
| Info | 40 |
| Agents Used | 22 |

---
*Report generated: 2026-02-13 23:15*
