# Review Report: 2026-02-13_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-13
- **Type:** Review
- **Description:** 
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 245
- **Critical:** 10 | **Major:** 80 | **Minor:** 115 | **Info:** 40
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 288
- **Confirmed:** 132 | **Downgraded:** 0 | **Rejected:** 43
- **Rejection Rate:** 14.9%
- **Findings Without Verdict:** 113

## Priority Findings (Top 10)

### 1. CRITICAL: AI Layer Imports in Simulation Factory
**ID:** ADR-SIM-001
**Agent:** Validated
**Location:** `game/simulation/factories/ai_f`
**Effort:** Medium

**Location:** `game/simulation/factories/ai_f`

---

### 2. CRITICAL: Test Framework Coupling in Production UI
**ID:** ADR-UI1-001
**Agent:** Validated
**Location:** `game/ui/screens/test_lab/scree`
**Effort:** Medium

**Location:** `game/ui/screens/test_lab/scree`

---

### 3. CRITICAL: Test Framework Import in Battle Screen
**ID:** ADR-UI1-002
**Agent:** Validated
**Location:** `game/ui/screens/battle_screen.`
**Effort:** Simple

**Location:** `game/ui/screens/battle_screen.`

---

### 4. CRITICAL: ResourceRegistry Return Type Inconsisten
**ID:** CON-SIM-001
**Agent:** Validated
**Location:** `game/simulation/systems/resour`
**Effort:** Simple

**Location:** `game/simulation/systems/resour`

---

### 5. CRITICAL: CollisionSystem raycasting edge cases un
**ID:** TCG-FND-001
**Agent:** Validated
**Location:** `game/engine/collision.py`
**Effort:** Medium

**Location:** `game/engine/collision.py`

---

### 6. CRITICAL: ResearchService leaky bucket algorithm e
**ID:** TCG-FND-002
**Agent:** Validated
**Location:** `game/research/systems/research`
**Effort:** Medium

**Location:** `game/research/systems/research`

---

### 7. CRITICAL: No dedicated tests for game/strategy/dat
**ID:** TCG-STR-001
**Agent:** Validated
**Location:** `game/strategy/data/naming.py`
**Effort:** Simple

**Location:** `game/strategy/data/naming.py`

---

### 8. CRITICAL: No dedicated tests for game/strategy/dat
**ID:** TCG-STR-002
**Agent:** Validated
**Location:** `game/strategy/data/physics.py`
**Effort:** Medium

**Location:** `game/strategy/data/physics.py`

---

### 9. CRITICAL: BattleStateViewer has no unit tests
**ID:** TCG-UI1-001
**Agent:** Validated
**Location:** `game/ui/screens/battle_state_v`
**Effort:** Medium

**Location:** `game/ui/screens/battle_state_v`

---

### 10. CRITICAL: TestLabValidationManager has no unit tes
**ID:** TCG-UI1-002
**Agent:** Validated
**Location:** `game/ui/screens/test_lab/valid`
**Effort:** Complex

**Location:** `game/ui/screens/test_lab/valid`

---


## Findings by Severity

### Critical (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-001 | AI Layer Imports in Simulation Factory | `game/simulation/factories/ai_f` | Medium |
| ADR-UI1-001 | Test Framework Coupling in Production UI | `game/ui/screens/test_lab/scree` | Medium |
| ADR-UI1-002 | Test Framework Import in Battle Screen | `game/ui/screens/battle_screen.` | Simple |
| CON-SIM-001 | ResourceRegistry Return Type Inconsisten | `game/simulation/systems/resour` | Simple |
| TCG-FND-001 | CollisionSystem raycasting edge cases un | `game/engine/collision.py` | Medium |
| TCG-FND-002 | ResearchService leaky bucket algorithm e | `game/research/systems/research` | Medium |
| TCG-STR-001 | No dedicated tests for game/strategy/dat | `game/strategy/data/naming.py` | Simple |
| TCG-STR-002 | No dedicated tests for game/strategy/dat | `game/strategy/data/physics.py` | Medium |
| TCG-UI1-001 | BattleStateViewer has no unit tests | `game/ui/screens/battle_state_v` | Medium |
| TCG-UI1-002 | TestLabValidationManager has no unit tes | `game/ui/screens/test_lab/valid` | Complex |

### Major (80)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-002 | TYPE_CHECKING Import of AI Controller | `game/simulation/systems/battle` | Simple |
| ADR-SIM-003 | God Class - BattleController | `game/simulation/battle_control` | Complex |
| ADR-SIM-004 | God Class - Ship Entity | `game/simulation/entities/ship.` | Complex |
| ADR-SIM-005 | Documented Circular Import in Ship.add_c | `game/simulation/entities/ship.` | Medium |
| ADR-UI2-002 | God Class Potential in ShipThemeManager | `game/ui/assets/ship_theme_mana` | Medium |
| ADR-UI1-003 | God Class - TestLabScreen (1908 lines, 7 | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-004 | God Class - StrategyScreen (811 lines, 4 | `game/ui/screens/strategy_scree` | Medium |
| ADR-UI1-005 | God Class - BuilderMain (1121 lines, 44 | `game/ui/screens/builder/main.p` | Medium |
| ADR-UI1-006 | God Class - BuildQueueScreen (1098 lines | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-007 | Circular Dependency Workarounds (Late Im | `game/ui/screens/column_manager` | Medium |
| ADR-UI1-008 | Private Attribute Access - StrategyEvent | `game/ui/screens/strategy_event` | Simple |
| ADR-UI1-009 | Private Attribute Access - WorkshopEvent | `game/ui/screens/workshop_event` | Simple |
| ADR-UI1-010 | Direct ViewModel State Mutation | `game/ui/screens/workshop_scree` | Simple |
| CON-SIM-002 | Duplicate Exception Handler in design_lo | `game/simulation/services/desig` | Simple |
| CON-SIM-003 | Magic Numbers in Projectile Guidance Sys | `game/simulation/entities/proje` | Simple |
| CON-SIM-004 | Singleton Fallback Pattern in Validation | `game/simulation/entities/ship_` | Complex |
| CON-SIM-005 | Inconsistent Parameter Naming - resource | `game/simulation/components/abi` | Simple |
| CON-SIM-006 | Type Hint Gaps in Physics and Combat Mod | `game/simulation/entities/ship_` | Medium |
| CON-SIM-007 | AIControllerFactory Uses Positional Para | `game/simulation/factories/ai_f` | Simple |
| CON-SIM-008 | Magic Numbers in Targeting and Combat Sy | `game/simulation/combat/targeti` | Simple |
| CON-STR-001 | Logging Pattern Inconsistency - Mixed Mo | `Unknown` | Simple |
| CON-STR-002 | Protocol Interface Decorator Inconsisten | `game/strategy/engine/command_h` | Simple |
| CON-STR-003 | Inconsistent Return Type for validate() | `game/strategy/data/race_config` | Medium |
| CON-STR-004 | Inconsistent `from __future__ import ann | `game/strategy/` | Medium |
| CON-UI2-001 | Inconsistent Dependency Injection Patter | `game/ui/services/*.py` | Medium |
| CON-UI2-004 | Return Type Inconsistency for Failure Ca | `game/ui/services/ship_io_adapt` | Medium |
| CON-UI1-001 | Inconsistent Constructor Parameter Order | `Unknown` | Complex |
| CON-UI1-002 | Incomplete God Class Decomposition (test | `game/ui/screens/test_lab/scree` | Complex |
| CON-UI1-003 | Direct Singleton Access Instead of Depen | `Unknown` | Medium |
| CON-UI1-004 | Mixed Event Handler Naming (handle_event | `Unknown` | Simple |
| DUP-FND-001 | Entity Position/State Access Patterns in | `game/ai/combat_utils.py:49-82` | Medium |
| DUP-SIM-001 | Serialization to_dict/from_dict Pattern | `game/simulation/battle_state.p` | Medium |
| DUP-SIM-002 | Resource Ability Classes Share Identical | `game/simulation/components/abi` | Simple |
| DUP-SIM-003 | Team Iteration Pattern Duplicated in Bat | `game/simulation/systems/battle` | Simple |
| DUP-STR-001 | Build Queue Source Collection - Near-Ide | `game/strategy/data/build_queue` | Simple |
| DUP-STR-002 | Facility Shipyard Detection - Duplicated | `game/strategy/data/build_queue` | Simple |
| DUP-STR-003 | Mission Command Handler Duplication | `game/strategy/engine/superweap` | Simple |
| DUP-STR-004 | `to_dict` / `from_dict` Boilerplate Patt | `Unknown` | Complex |
| DUP-STR-005 | Fleet Resolution Pattern in Command Hand | `Unknown` | Simple |
| DUP-STR-006 | ColonizeValidator Colony Pod Iteration P | `game/strategy/validation/colon` | Simple |
| DUP-STR-007 | Component Layer Iteration Pattern - Repe | `Unknown` | Medium |
| LEG-STR-001 | Legacy Behavior Branch in FleetOrderProc | `game/strategy/engine/fleet_ord` | Medium |
| LEG-STR-002 | Backward Compatibility Comment in GameSe | `game/strategy/engine/game_sess` | Medium |
| LEG-STR-003 | Legacy Items in ProductionEngine | `game/strategy/engine/productio` | Medium |
| TCG-FND-003 | AIController navigation and avoidance al | `game/ai/controller.py` | Medium |
| TCG-FND-004 | TargetEvaluator rule evaluation missing | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-005 | Behavior classes missing state transitio | `game/ai/behaviors.py` | Medium |
| TCG-FND-006 | TechTree validation methods lack test co | `game/research/data/tech_tree.p` | Simple |
| TCG-FND-007 | TechRequirement fuzzy resolution edge ca | `game/research/data/tech_node.p` | Simple |
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
| TCG-STR-008 | GameInitializer._setup_initial_scenario | `game/strategy/engine/game_init` | Simple |
| TCG-STR-009 | ShipStatsCalculator.has_warp_capability | `game/strategy/services/ship_st` | Medium |
| TCG-UI2-001 | UIConfig class has no dedicated test cov | `game/ui/config.py` | Simple |
| TCG-UI2-004 | BattleUIService projectile color mapping | `game/ui/services/battle_ui_ser` | Simple |
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
| TCG-UI1-017 | StrategyRenderer draw methods test only | `tests/unit/ui/screens/test_str` | Medium |
| TCG-UI1-018 | DesignStatsPanel tests use bypass-init p | `tests/unit/ui/panels/test_desi` | Medium |

### Minor (115)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | behaviors.py File Growing Large | `game/ai/behaviors.py` | Simple |
| ADR-SIM-006 | Possible Circular Import Comment in ship | `game/simulation/entities/ship_` | Simple |
| ADR-UI2-003 | Lazy Import Pattern in ship_factory.py C | `game/ui/services/ship_factory.` | Simple |
| ADR-UI1-011 | Simulation Layer TYPE_CHECKING Imports | `Unknown` | Simple |
| ADR-UI1-012 | Planet Filter Cached Attributes | `game/ui/screens/planet_list_fi` | Simple |
| ADR-UI1-013 | Strategy Renderer Temporary Attributes | `game/ui/screens/strategy_rende` | Simple |
| ADR-UI1-014 | FleetCapabilityCalculator Private Method | `game/ui/screens/column_manager` | Simple |
| ADR-UI1-015 | InputMapper Private Method Access | `game/ui/screens/keybindings_sc` | Simple |
| CON-FND-007 | Inconsistent Docstring Format - Google S | `Unknown` | Simple |
| CON-FND-008 | Boolean Property Naming - is_alive() vs | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-009 | Inconsistent Type Hint Coverage | `game/core/logger.py:27-41` | Simple |
| CON-FND-010 | Inconsistent Import Organization | `game/ai/controller.py:51-66` | Simple |
| CON-FND-011 | Magic Numbers in AI Layer | `game/ai/controller.py:445` | Simple |
| CON-FND-012 | Inconsistent Error Handling - Broad Exce | `game/ai/controller.py:217-223` | Simple |
| CON-FND-013 | Inconsistent `__all__` Export Patterns | `game/core/constants.py:1-15` | Simple |
| CON-FND-014 | Redundant Protocol Definition | `game/core/validation.py:23-60` | Simple |
| CON-SIM-009 | Abbreviated Parameter Names in solve_lea | `game/simulation/combat/targeti` | Simple |
| CON-SIM-010 | Mixed Logging Initialization Patterns | `game/simulation/services/regis` | Simple |
| CON-SIM-011 | STAT_BINDINGS Type Hint Inconsistency | `game/simulation/components/abi` | Simple |
| CON-SIM-012 | sync_data() Inconsistent Implementation | `game/simulation/components/abi` | Medium |
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
| CON-UI2-012 | Inconsistent Use of Optional vs Default | `game/ui/services/input_mapper.` | Simple |
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
| DUP-UI2-004 | Image Transform Operations Scattered Wit | `game/ui/utils.py:66-94` | Simple |
| DUP-UI2-005 | Validation Service Pattern Has Single-Pu | `game/ui/services/validation_se` | N |
| DUP-UI2-006 | Camera Coordinate Transform Duplication | `game/ui/renderer/camera.py:116` | Medium |
| UNK-08 | Population/Number Formatting Duplication | `Unknown` | Unknown |
| UNK-09 | RaceThemeGallery Not Using BaseGallery | `Unknown` | Unknown |
| UNK-10 | Window Kill/Cleanup Pattern Slightly Inc | `Unknown` | Unknown |
| UNK-11 | Dropdown Recreation Utility | `Unknown` | Unknown |
| LEG-FND-003 | Raw Ship vs Adapter Access Pattern in Fo | `game/ai/behaviors.py:276-400` | Medium |
| LEG-FND-004 | Singleton Pattern Still in Use Despite D | `Unknown` | Complex |
| LEG-FND-005 | Unused AI_STATE_ERROR ErrorCode | `game/core/error_codes.py:153` | Simple |
| LEG-SIM-006 | Module Identity Drift Fallback in Abilit | `game/simulation/components/abi` | Medium |
| LEG-SIM-007 | Component Ability Index Fallback Pattern | `game/simulation/components/com` | Simple |
| LEG-STR-004 | Backward Compatibility Comment in FleetN | `game/strategy/services/fleet_n` | Simple |
| LEG-STR-005 | Backward Compat Default in Planet.from_d | `game/strategy/data/planet.py:3` | Simple |
| LEG-STR-006 | Backward Compat Defaults in RaceConfig.f | `game/strategy/data/race_config` | N |
| LEG-STR-007 | Old Layer Format Detection in DesignMeta | `game/strategy/data/design_meta` | Simple |
| LEG-STR-008 | Save Compatibility Field in DesignMetada | `game/strategy/data/design_meta` | Simple |
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
| TCG-SIM-015 | interfaces/ai_controller.py Interface Te | `game/simulation/interfaces/ai_` | Simple |
| TCG-SIM-016 | validation/ship_validator.py Missing Com | `game/simulation/validation/shi` | Simple |
| TCG-STR-010 | DensityMap.from_config() lacks test cove | `game/strategy/generation/densi` | Simple |
| TCG-STR-011 | RegionClassifier._classify_spiral edge c | `game/strategy/generation/regio` | Simple |
| TCG-STR-012 | calculate_habitability has no negative t | `game/strategy/formulas/habitab` | Simple |
| TCG-STR-013 | EmpireEconomyCalculator doesn't test des | `game/strategy/engine/empire_ec` | Simple |
| TCG-STR-014 | Component inspector service lacks edge c | `game/strategy/services/compone` | Simple |
| TCG-STR-015 | Fleet.trigger_speed_recalculation has no | `game/strategy/data/fleet.py::t` | Simple |
| TCG-STR-016 | Transfer order validator edge cases | `game/strategy/validation/trans` | Simple |
| TCG-UI2-007 | InputMapper save_user_overrides file per | `game/ui/services/input_mapper.` | Simple |
| TCG-UI2-008 | ScreenshotManager capture_strategy_layer | `game/ui/services/screenshot_ma` | Simple |
| TCG-UI2-009 | BattleOrchestrator lacks tests for AI co | `game/ui/orchestration/battle_o` | Simple |
| TCG-UI2-010 | SpriteManager thread safety tests are li | `game/ui/renderer/sprites.py` | Medium |
| TCG-UI2-011 | colors.py basic constants not tested | `game/ui/colors.py` | Simple |
| TCG-UI1-019 | StrategyScreen tests have incomplete met | `tests/unit/ui/screens/test_str` | Medium |
| TCG-UI1-020 | Screen transition handling untested | `Unknown` | Simple |
| TCG-UI1-021 | Input handling edge cases untested | `game/ui/screens/strategy_input` | Simple |
| TCG-UI1-022 | Source code inspection used instead of b | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-023 | Mock verification without assertions on | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-024 | Test helper function tests its own mock | `tests/unit/ui/panels/test_desi` | Simple |
| TCG-UI1-025 | Missing parameterized edge case tests | `Unknown` | Simple |
| TCG-UI1-026 | No end-to-end battle UI flow tests | `Unknown` | Medium |
| TCG-UI1-027 | Strategy screen + build queue integratio | `Unknown` | Medium |
| TCG-UI1-028 | Workshop + ship I/O roundtrip untested | `Unknown` | Medium |
| TCG-UI1-029 | No resize handling tests | `Unknown` | Simple |

### Info (40)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-007 | Heavy Use of TYPE_CHECKING for Forward R | `Unknown` | N |
| ADR-UI2-005 | BattleOrchestrator Correctly Documents C | `game/ui/orchestration/battle_o` | N |
| ADR-UI1-016 | Test Lab Executor Private Field Access | `game/ui/screens/test_lab/test_` | Simple |
| ADR-UI1-017 | Deep Object Chain in StrategyUI | `game/ui/screens/strategy_ui.py` | Simple |
| ADR-UI1-018 | Large Method Counts in UI Screens | `Unknown` | N |
| CON-FND-016 | ResourceType is a Class, Not an Enum | `game/core/constants.py:83-92` | Simple |
| CON-FND-017 | TechNode/TechTree Separate from Core Reg | `game/research/data/tech_tree.p` | N |
| CON-FND-018 | Research Layer Has Direct pygame Import | `game/research/ui/research_scen` | Complex |
| CON-SIM-017 | ResourceRegistry Class Name Deviation | `game/simulation/systems/resour` | Simple |
| CON-SIM-018 | Excellent Pattern Adherence - Facade/Del | `game/simulation/entities/ship_` | N |
| CON-STR-011 | Well-Established Consistent Patterns | `Unknown` | N |
| CON-STR-012 | Consistent Class Naming Suffixes | `Unknown` | N |
| CON-UI2-015 | Protocol Definition Location | `game/ui/interfaces/battle_ui.p` | N |
| CON-UI2-016 | __init__.py Export Patterns | `game/ui/__init__.py` | N |
| CON-UI1-015 | Good Pattern Adoption - Facade/Delegate | `strategy_ui.py` | N |
| CON-UI1-016 | Consistent Callback Naming Pattern | `Unknown` | N |
| CON-UI1-017 | Good Class Naming Suffix Consistency | `Unknown` | N |
| CON-UI1-018 | Well-Organized builder/ Module Structure | `game/ui/screens/builder/` | N |
| CON-UI1-019 | Consistent Logging Pattern | `Unknown` | N |
| DUP-SIM-008 | Natural Similarity in Dataclass State Cl | `game/simulation/battle_state.p` | N |
| DUP-STR-013 | Validated Design Component Iteration | `Unknown` | Medium |
| DUP-STR-014 | Well-Consolidated Component Inspector | `game/strategy/services/compone` | N |
| DUP-UI2-007 | Color Constants Could Be Centralized Fur | `game/ui/colors.py:7-45` | N |
| UNK-13 | Ship Stats Renderer Already Extracted | `Unknown` | Unknown |
| UNK-14 | Strategy Detail Formatters Properly Sepa | `Unknown` | Unknown |
| LEG-SIM-009 | TechPresetLoader Only Used in Tests | `game/simulation/systems/tech_p` | Unknown |
| LEG-STR-009 | Test Mock Compatibility in FleetOrderPro | `game/strategy/engine/fleet_ord` | Simple |
| LEG-STR-010 | Intercept Function Accepts Both Fleet an | `game/strategy/data/pathfinding` | N |
| LEG-UI2-005 | Singleton Pattern Still in Use for Asset | `game/ui/assets/ship_theme_mana` | N |
| LEG-UI2-006 | hasattr() Check in Camera for Defensive | `game/ui/renderer/camera.py:58` | Simple |
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
| Total Findings | 245 |
| Critical | 10 |
| Major | 80 |
| Minor | 115 |
| Info | 40 |
| Agents Used | 25 |

---
*Report generated: 2026-02-13 06:00*
