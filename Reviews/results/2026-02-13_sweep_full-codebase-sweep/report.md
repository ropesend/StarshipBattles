# Review Report: 2026-02-13_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-13
- **Type:** Review
- **Description:** 
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 273
- **Critical:** 17 | **Major:** 93 | **Minor:** 109 | **Info:** 54
- **Overall Assessment:** Requires Immediate Attention

### Validation Summary
- **Original Findings:** 273
- **Confirmed:** 0 | **Downgraded:** 0 | **Rejected:** 0
- **Rejection Rate:** 0.0%
- **Findings Without Verdict:** 273

## Priority Findings (Top 10)

### 1. CRITICAL: Research UI Layer Imports Concrete Camer
**ID:** ADR-FND-001
**Agent:** Validated
**Location:** `game/research/ui/research_scen`
**Effort:** Medium

**Location:** `game/research/ui/research_scen`

---

### 2. CRITICAL: AI Layer Imports in Simulation Factory
**ID:** ADR-SIM-001
**Agent:** Validated
**Location:** `game/simulation/factories/ai_f`
**Effort:** Medium

**Location:** `game/simulation/factories/ai_f`

---

### 3. CRITICAL: Test Framework Coupling in Production UI
**ID:** ADR-UI1-001
**Agent:** Validated
**Location:** `game/ui/screens/test_lab/scree`
**Effort:** Medium

**Location:** `game/ui/screens/test_lab/scree`

---

### 4. CRITICAL: Test Framework Import in Battle Screen
**ID:** ADR-UI1-002
**Agent:** Validated
**Location:** `game/ui/screens/battle_screen.`
**Effort:** Simple

**Location:** `game/ui/screens/battle_screen.`

---

### 5. CRITICAL: Inconsistent Singleton Pattern Usage - S
**ID:** CON-FND-001
**Agent:** Validated
**Location:** `game/core/registry.py:79-120`
**Effort:** Medium

**Location:** `game/core/registry.py:79-120`

---

### 6. CRITICAL: Inconsistent DI Pattern - Some Services
**ID:** CON-UI2-001
**Agent:** Validated
**Location:** `game/ui/services/vehicle_class`
**Effort:** Medium

**Location:** `game/ui/services/vehicle_class`

---

### 7. CRITICAL: String-to-Enum Migration Support Code in
**ID:** LEG-SIM-001
**Agent:** Validated
**Location:** `game/simulation/systems/battle`
**Effort:** Medium

**Location:** `game/simulation/systems/battle`

---

### 8. CRITICAL: Backward Compatibility Aliases in RacePo
**ID:** LEG-UI1-001
**Agent:** Validated
**Location:** `game/ui/panels/race_portrait_g`
**Effort:** Simple

**Location:** `game/ui/panels/race_portrait_g`

---

### 9. CRITICAL: Projectile Entity Has No Unit Tests
**ID:** TCG-SIM-001
**Agent:** Validated
**Location:** `game/simulation/entities/proje`
**Effort:** Medium

**Location:** `game/simulation/entities/proje`

---

### 10. CRITICAL: ShipStatQuerier Has No Unit Tests
**ID:** TCG-SIM-002
**Agent:** Validated
**Location:** `game/simulation/entities/ship_`
**Effort:** Medium

**Location:** `game/simulation/entities/ship_`

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
| CON-UI2-001 | Inconsistent DI Pattern - Some Services | `game/ui/services/vehicle_class` | Medium |
| LEG-SIM-001 | String-to-Enum Migration Support Code in | `game/simulation/systems/battle` | Medium |
| LEG-UI1-001 | Backward Compatibility Aliases in RacePo | `game/ui/panels/race_portrait_g` | Simple |
| TCG-SIM-001 | Projectile Entity Has No Unit Tests | `game/simulation/entities/proje` | Medium |
| TCG-SIM-002 | ShipStatQuerier Has No Unit Tests | `game/simulation/entities/ship_` | Medium |
| TCG-SIM-003 | ShipValidator Rules Have No Unit Tests | `game/simulation/validation/shi` | Complex |
| TCG-STR-001 | No dedicated tests for game/strategy/dat | `game/strategy/data/naming.py` | Simple |
| TCG-STR-002 | No dedicated tests for game/strategy/dat | `game/strategy/data/physics.py` | Medium |
| TCG-UI1-001 | BattleScreen has no unit tests | `game/ui/screens/battle_screen.` | Complex |
| TCG-UI1-002 | BattleUI has no unit tests | `game/ui/screens/battle_ui.py` | Medium |
| TCG-UI1-003 | BattleStateViewer has no unit tests | `game/ui/screens/battle_state_v` | Medium |
| TCG-UI1-004 | BattlePanels (ShipStatsPanel, SeekerMoni | `game/ui/panels/battle_panels.p` | Medium |

### Major (93)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-002 | protocols.py is Approaching God Class Te | `game/core/protocols.py` | Medium |
| ADR-SIM-002 | TYPE_CHECKING Import of AI Controller | `game/simulation/systems/battle` | Simple |
| ADR-SIM-003 | God Class - BattleController | `game/simulation/battle_control` | Complex |
| ADR-SIM-004 | God Class - Ship Entity | `game/simulation/entities/ship.` | Complex |
| ADR-STR-001 | Simulation Layer Coupling via Direct Imp | `game/strategy/services/ship_st` | Medium |
| ADR-STR-002 | Simulation Adapter Has Top-Level Simulat | `game/strategy/adapters/simulat` | Simple |
| ADR-STR-003 | Galaxy Class Approaching God Class Statu | `game/strategy/data/galaxy.py` | Complex |
| ADR-UI2-001 | pygame.math.Vector2 Usage in game_render | `game/ui/renderer/game_renderer` | Simple |
| ADR-UI2-002 | God Class Potential in ShipThemeManager | `game/ui/assets/ship_theme_mana` | Medium |
| ADR-UI1-003 | God Class - TestLabScreen (1908 lines, 7 | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-004 | God Class - StrategyScreen (811 lines, 4 | `game/ui/screens/strategy_scree` | Medium |
| ADR-UI1-005 | God Class - BuilderMain (1121 lines, 44 | `game/ui/screens/builder/main.p` | Medium |
| ADR-UI1-006 | God Class - BuildQueueScreen (1098 lines | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-007 | Circular Dependency Workarounds (Late Im | `game/ui/screens/column_manager` | Medium |
| ADR-UI1-008 | Private Attribute Access - StrategyEvent | `game/ui/screens/strategy_event` | Simple |
| ADR-UI1-009 | Private Attribute Access - WorkshopEvent | `game/ui/screens/workshop_event` | Simple |
| ADR-UI1-010 | Direct ViewModel State Mutation | `game/ui/screens/workshop_scree` | Simple |
| CON-FND-002 | Inconsistent Logging Pattern - Logger Si | `game/core/logger.py` | Medium |
| CON-FND-003 | Mixed Return Semantics for Not-Found Cas | `game/core/registry.py:98-120` | Simple |
| CON-FND-004 | Inconsistent Method Naming for Position/ | `game/ai/interfaces/controllabl` | Complex |
| CON-FND-005 | Class Naming Suffix Inconsistency - Serv | `game/ai/strategy_manager.py` | Simple |
| CON-UI2-002 | Singleton vs Dependency Injection Patter | `game/ui/services/screenshot_ma` | Complex |
| CON-UI2-003 | Mixed Return Type Patterns for Error Han | `game/ui/services/ship_io.py:42` | Medium |
| CON-UI2-004 | Inconsistent Parameter Naming for Regist | `Unknown` | Simple |
| CON-UI2-005 | Missing Type Hints on Public Functions | `game/ui/renderer/game_renderer` | Simple |
| CON-UI2-006 | Docstring Inconsistency - Some Use Googl | `game/ui/services/screenshot_ma` | Simple |
| CON-UI2-007 | Inconsistent Module-Level vs Class-Level | `game/ui/colors.py:7-14` | Simple |
| SP-001 | Inconsistent Constructor Parameter Order | `Unknown` | High |
| PP-002 | Incomplete God Class Decomposition | `game/ui/screens/test_lab/scree` | High |
| PP-006 | Direct Singleton Access in Some Files | `game/ui/screens/race_setup_scr` | Medium |
| DUP-FND-001 | Clamp Function Duplication | `game/core/math.py:187-203` | Simple |
| DUP-FND-002 | Entity Position/State Access Patterns in | `game/ai/combat_utils.py:49-82` | Medium |
| DUP-FND-003 | Singleton Pattern Documentation/Structur | `Unknown` | Medium |
| DUP-STR-001 | Mission Command Handler Duplication | `game/strategy/engine/superweap` | Simple |
| DUP-STR-002 | Direct vs Mission Command Validation Asy | `game/strategy/engine/superweap` | Medium |
| DUP-STR-003 | `to_dict` / `from_dict` Boilerplate Patt | `Unknown` | Complex |
| DUP-STR-004 | Fleet Resolution Pattern in Command Hand | `Unknown` | Simple |
| DUP-STR-005 | ColonizeValidator Colony Pod Iteration P | `game/strategy/validation/colon` | Simple |
| DUP-UI2-001 | Duplicated Lazy DI Provider Resolution P | `game/ui/services/component_ser` | Medium |
| DUP-UI2-002 | Directory Creation Pattern Duplicated in | `game/ui/services/ship_io.py:49` | Simple |
| DUP-UI2-003 | Singleton Manager Pattern Triplicated | `game/ui/assets/ship_theme_mana` | Medium |
| DUP-UI2-004 | Service Adapter Wrapping Pattern | `game/ui/services/ship_io_adapt` | Medium |
| LEG-FND-001 | Unused Exception Classes (AIException, T | `game/core/exceptions.py:216-23` | Simple |
| LEG-FND-002 | Backward Compatibility Wrapper - load_re | `game/core/resources.py:101-114` | Simple |
| LEG-SIM-002 | V1 Modifier Format Validation Code Still | `game/simulation/components/mod` | Simple |
| LEG-SIM-003 | Defensive hasattr Check for Always-Prese | `game/simulation/systems/battle` | Simple |
| LEG-SIM-004 | retreat_status Attribute Accessed via ha | `game/simulation/managers/retre` | Simple |
| LEG-UI2-001 | Dead Code - draw_hud and draw_bar Functi | `game/ui/renderer/game_renderer` | Simple |
| LEG-UI2-002 | Unused Method - create_ai_for_ship in Ba | `game/ui/orchestration/battle_o` | Simple |
| LEG-UI2-003 | Unused Method - capture_step in Screensh | `game/ui/services/screenshot_ma` | Simple |
| LEG-UI1-002 | Legacy BuilderScreen (builder/main.py) P | `game/ui/screens/builder/main.p` | Complex |
| LEG-UI1-003 | Legacy Tuple Format Support in Component | `game/ui/screens/builder/detail` | Medium |
| LEG-UI1-004 | Legacy API Comment in FleetReportWindow | `game/ui/screens/fleet_report_w` | Simple |
| LEG-UI1-005 | Legacy Single-Selection Fields in Empire | `game/ui/screens/empire_build_q` | Medium |
| LEG-UI1-006 | Fallback Mode in BuildQueueController | `game/ui/panels/build_queue_con` | Medium |
| UNK-03 | game/research/data/tech_tree.py - Missin | `Unknown` | Unknown |
| UNK-04 | game/research/ui/research_controls.py - | `Unknown` | Unknown |
| UNK-05 | game/research/ui/research_scene.py - No | `Unknown` | Unknown |
| UNK-17 | No integration tests for AI module | `Unknown` | Unknown |
| UNK-18 | No integration tests for Research module | `Unknown` | Unknown |
| TCG-SIM-004 | BattleController Missing Edge Case Tests | `game/simulation/battle_control` | Medium |
| TCG-SIM-005 | DamageCalculator Armor Penetration Edge | `game/simulation/combat/damage_` | Simple |
| TCG-SIM-006 | WeaponFiringSystem Missing Multishot Tes | `game/simulation/combat/weapon_` | Medium |
| TCG-SIM-007 | TargetingSystem Missing AI Priority Test | `game/simulation/combat/targeti` | Medium |
| TCG-SIM-008 | BattleEngine Tick Processing Incomplete | `game/simulation/systems/battle` | Medium |
| TCG-SIM-009 | FormulaSystem Overflow/Underflow Not Tes | `game/simulation/formula_system` | Simple |
| TCG-SIM-010 | Design System Serialization Roundtrip Ga | `game/simulation/designs.py` | Medium |
| TCG-STR-003 | No dedicated tests for game/strategy/eng | `game/strategy/engine/commands.` | Simple |
| TCG-STR-004 | TurnEngine.validate_colonize_order lacks | `game/strategy/engine/turn_engi` | Simple |
| TCG-STR-005 | FleetOrder.to_dict() serialization has w | `game/strategy/data/fleet.py::F` | Medium |
| TCG-STR-006 | QuickstartBuilder has no comprehensive t | `game/strategy/quickstart_build` | Medium |
| TCG-STR-007 | StrategySessionFacade has incomplete que | `game/strategy/facade/strategy_` | Medium |
| TCG-STR-008 | GameInitializer._setup_initial_scenario | `game/strategy/engine/game_init` | Simple |
| TCG-STR-009 | ShipStatsCalculator.has_warp_capability | `game/strategy/services/ship_st` | Medium |
| TCG-UI2-001 | UIConfig class has no dedicated test cov | `game/ui/config.py` | Simple |
| TCG-UI2-002 | game_renderer draw_ship lacks edge case | `game/ui/renderer/game_renderer` | Medium |
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
| TCG-UI1-017 | StrategyRenderer draw methods test only | `tests/unit/ui/screens/test_str` | Medium |
| TCG-UI1-018 | DesignStatsPanel tests use bypass-init p | `tests/unit/ui/panels/test_desi` | Medium |

### Minor (109)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | behaviors.py File Growing Large | `game/ai/behaviors.py` | Simple |
| ADR-SIM-005 | Possible Circular Import Workaround | `game/simulation/entities/ship_` | Simple |
| ADR-STR-004 | TYPE_CHECKING Block Indicates Tight Coup | `game/strategy/data/fleet_battl` | Simple |
| ADR-STR-005 | Late Import Pattern Inconsistency | `Unknown` | Simple |
| ADR-STR-006 | Potential Circular Dependency Risk in Fl | `game/strategy/data/fleet_battl` | Simple |
| ADR-UI2-003 | Lazy Import Pattern in ship_factory.py C | `game/ui/services/ship_factory.` | Simple |
| ADR-UI2-004 | TYPE_CHECKING Import for GameRegistries | `game/ui/services/ship_factory.` | Simple |
| ADR-UI1-011 | Simulation Layer TYPE_CHECKING Imports | `Unknown` | Simple |
| ADR-UI1-012 | Planet Filter Cached Attributes | `game/ui/screens/planet_list_fi` | Simple |
| ADR-UI1-013 | Strategy Renderer Temporary Attributes | `game/ui/screens/strategy_rende` | Simple |
| ADR-UI1-014 | FleetCapabilityCalculator Private Method | `game/ui/screens/column_manager` | Simple |
| ADR-UI1-015 | InputMapper Private Method Access | `game/ui/screens/keybindings_sc` | Simple |
| CON-FND-006 | Inconsistent Parameter Naming - entity v | `game/ai/combat_utils.py` | Simple |
| CON-FND-007 | Inconsistent Docstring Format - Google S | `Unknown` | Simple |
| CON-FND-008 | Boolean Property Naming - is_alive() vs | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-009 | Inconsistent Type Hint Coverage | `game/core/logger.py:27-41` | Simple |
| CON-FND-010 | Inconsistent Import Organization | `game/ai/controller.py:51-66` | Simple |
| CON-FND-011 | Magic Numbers in AI Layer | `game/ai/controller.py:445` | Simple |
| CON-FND-012 | Inconsistent Error Handling - Broad Exce | `game/ai/controller.py:217-223` | Simple |
| CON-FND-013 | Inconsistent `__all__` Export Patterns | `game/core/constants.py:1-15` | Simple |
| CON-FND-014 | Redundant Protocol Definition | `game/core/validation.py:23-60` | Simple |
| CON-UI2-008 | Inconsistent Boolean Method Naming | `game/ui/services/component_ser` | N |
| CON-UI2-009 | Redundant Exception Handling in ship_io. | `game/ui/services/ship_io.py:71` | Simple |
| CON-UI2-010 | Inconsistent Import Organization | `game/ui/renderer/sprites.py:1-` | Simple |
| CON-UI2-011 | Method Prefix Inconsistency - get_ vs lo | `game/ui/assets/ship_theme_mana` | Simple |
| CON-UI2-012 | Inconsistent Private Method Naming | `game/ui/assets/ship_theme_mana` | N |
| CON-UI2-013 | Magic Numbers in game_renderer.py | `game/ui/renderer/game_renderer` | Medium |
| CON-UI2-014 | Inconsistent Error Logging Format | `game/ui/services/ship_io.py:72` | Simple |
| CON-UI2-015 | Unused Comments as Section Headers | `game/ui/renderer/game_renderer` | Simple |
| NC-001 | Mixed Screen/Scene Terminology | `game/ui/screens/menu_scene.py` | Low |
| NC-002 | Inconsistent Event Handler Prefixes | `Unknown` | Medium |
| NC-003 | Inconsistent Module Naming for Related C | `game/ui/screens/` | N |
| SP-002 | Inconsistent UI Manager Attribute Names | `Unknown` | Medium |
| API-001 | Mixed Callback Parameter Names | `Unknown` | N |
| API-002 | Inconsistent Event Handler Return Types | `BattlePanel.handle_click()` | Medium |
| PP-003 | Inconsistent Type Hint Coverage | `game/ui/screens/builder/compon` | Medium |
| PP-004 | Missing Module Docstrings | `Unknown` | Low |
| PP-005 | Inconsistent Future Annotations Usage | `Unknown` | Low |
| MOD-002 | Mixed Responsibility in screen.py | `game/ui/screens/test_lab/scree` | High |
| MOD-003 | Inconsistent Panel Base Class Usage | `game/ui/panels/` | Low |
| MOD-004 | Inconsistent Error Logging | `Unknown` | Low |
| DUP-FND-004 | Entity ID Extraction Pattern Duplication | `game/ai/combat_utils.py:65` | Simple |
| DUP-FND-005 | Flee Direction Calculation | `game/ai/behaviors.py:70-84` | Simple |
| DUP-FND-006 | Tech Tree Validation Method Patterns | `game/research/data/tech_tree.p` | Simple |
| DUP-FND-007 | Serialization to_dict/from_dict Patterns | `game/research/data/research_tr` | Complex |
| DUP-STR-006 | Gaussian Factor Calculation Pattern | `game/strategy/formulas/habitab` | Simple |
| DUP-STR-007 | Path Start Hex Determination Logic | `Unknown` | Simple |
| DUP-STR-008 | Ship Ability Check Wrappers | `Unknown` | Simple |
| DUP-STR-009 | Resource Dictionary Accumulation Pattern | `game/strategy/services/ship_st` | Simple |
| DUP-UI2-005 | Font Creation Throughout UI Without Cent | `game/ui/renderer/game_renderer` | Simple |
| DUP-UI2-006 | Image Scaling Utility Functions Have Ove | `game/ui/utils.py:32-64` | Simple |
| DUP-UI2-007 | Placeholder Surface Creation Pattern | `game/ui/utils.py:141-143` | Simple |
| DUP-UI2-008 | Error Exception Handling Pattern in Ship | `game/ui/services/ship_io.py:71` | Simple |
| DUP-UI2-009 | Tkinter Initialization Error Handling | `game/ui/services/ship_io.py:21` | Medium |
| DUP-UI2-010 | Return Value Conventions Partially Docum | `game/ui/services/ship_io_adapt` | Simple |
| LEG-FND-003 | Backward Compatibility Comment in Valida | `game/core/validation.py:100-10` | Simple |
| LEG-FND-004 | Extensive getattr() with Defaults in AI | `game/ai/controller.py` | Medium |
| LEG-FND-005 | Raw Ship vs Adapter Access Pattern in Fo | `game/ai/behaviors.py:276-400` | Medium |
| LEG-FND-006 | DEBUG_SCREENSHOTS Hardcoded True | `game/core/constants.py:41` | Simple |
| LEG-FND-007 | Singleton Pattern Still in Use Despite D | `Unknown` | Complex |
| LEG-SIM-005 | Fallback Pattern Comment Suggesting Inco | `game/simulation/entities/ship.` | Simple |
| LEG-SIM-006 | Ability Manager Fallback for Module Iden | `game/simulation/components/abi` | Medium |
| LEG-SIM-007 | Component Fallback Delegation Pattern | `game/simulation/components/com` | Simple |
| LEG-SIM-008 | Unused AbilityStatBinding.describe() Met | `game/simulation/components/abi` | Simple |
| UNK-01 | Save metadata duplicates turn_number fie | `Unknown` | Unknown |
| UNK-02 | _get_fleet_by_id has O(n) fallback for b | `Unknown` | Unknown |
| LEG-UI2-004 | Duplicate Exception Handlers in ShipIO | `game/ui/services/ship_io.py:71` | Simple |
| LEG-UI2-005 | Comment References "legacy behavior" in | `game/ui/services/ship_factory.` | Medium |
| LEG-UI2-006 | Basic Color Constants (BLUE, RED, GREEN) | `game/ui/colors.py:9-11` | Simple |
| LEG-UI2-007 | ShipIOAdapter vs ShipIO Direct Access | `game/ui/services/ship_io_adapt` | Medium |
| LEG-UI2-008 | Excessive getattr() with Defaults in bat | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI1-007 | Backward Compat Attribute Exposure in Ri | `game/ui/screens/builder/right_` | Simple |
| LEG-UI1-008 | Backward Compatibility in WorkshopEventR | `game/ui/screens/workshop_event` | Simple |
| LEG-UI1-009 | Test Lab Screen Legacy Game Parameter | `game/ui/screens/test_lab/scree` | Medium |
| LEG-UI1-010 | Compatibility Setter in BuilderStateMana | `game/ui/screens/builder/state_` | Simple |
| LEG-UI1-011 | Deprecated Properties in StrategyScreen | `game/ui/screens/strategy_scree` | Complex |
| UNK-15 | Excessive mocking may hide real issues | `Unknown` | Unknown |
| UNK-20 | No performance tests for SpatialGrid | `Unknown` | Unknown |
| UNK-21 | No regression test suite for combat form | `Unknown` | Unknown |
| TCG-SIM-011 | AbilityAggregator Missing Concurrent Mod | `game/simulation/entities/abili` | Simple |
| TCG-SIM-012 | ShipCombatEngine Heat Management Not Tes | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-013 | ShipFormation Missing Complex Formation | `tests/unit/simulation/entities` | Simple |
| TCG-SIM-014 | BattleStateSerializer Version Migration | `tests/unit/simulation/test_bat` | Simple |
| TCG-SIM-015 | PropulsionAbility Strategic Movement Not | `game/simulation/components/abi` | Simple |
| TCG-SIM-016 | ProjectileManager Missing Batch Update T | `game/simulation/projectile_man` | Simple |
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
| TCG-UI1-023 | Mock verification without assertions on | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-024 | Test helper function tests its own mock | `tests/unit/ui/panels/test_desi` | Simple |
| TCG-UI1-025 | Missing parameterized edge case tests | `Unknown` | Simple |
| TCG-UI1-026 | No end-to-end battle UI flow tests | `Unknown` | Medium |
| TCG-UI1-027 | Strategy screen + build queue integratio | `Unknown` | Medium |
| TCG-UI1-028 | Workshop + ship I/O roundtrip untested | `Unknown` | Medium |
| TCG-UI1-029 | No resize handling tests | `Unknown` | Simple |

### Info (54)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-006 | Heavy Use of TYPE_CHECKING for Forward R | `Unknown` | N |
| ADR-STR-007 | Well-Architected Adapter Pattern in Plac | `game/strategy/adapters/simulat` | N |
| ADR-UI2-005 | BattleOrchestrator Correctly Documents C | `game/ui/orchestration/battle_o` | N |
| ADR-UI1-016 | Test Lab Executor Private Field Access | `game/ui/screens/test_lab/test_` | Simple |
| ADR-UI1-017 | Deep Object Chain in StrategyUI | `game/ui/screens/strategy_ui.py` | Simple |
| ADR-UI1-018 | Large Method Counts in UI Screens | `Unknown` | N |
| CON-FND-015 | os.path vs pathlib.Path Mixed Usage | `game/core/paths.py:53-103` | Simple |
| CON-FND-016 | ResourceType is a Class, Not an Enum | `game/core/constants.py:83-92` | Simple |
| CON-FND-017 | TechNode/TechTree Separate from Core Reg | `game/research/data/tech_tree.p` | N |
| CON-FND-018 | Research Layer Has Direct pygame Import | `game/research/ui/research_scen` | Complex |
| CON-UI2-016 | Cross-Layer Imports Documented But Incon | `game/ui/orchestration/battle_o` | Simple |
| CON-UI2-017 | DTO Classes Could Use __slots__ | `game/ui/interfaces/battle_ui.p` | Simple |
| CON-UI2-018 | UIConfig Class Has No Methods | `game/ui/config.py:17-67` | N |
| SP-003 | Two Initialization Naming Conventions | `Unknown` | Low |
| API-003 | Consistent Pattern | `Unknown` | N |
| PP-001 | Good Pattern Adoption | `strategy_ui.py` | N |
| MOD-001 | Well-Organized Module Structure | `game/ui/screens/builder/` | N |
| DUP-FND-008 | Well-Consolidated Utilities | `game/core/` | N |
| DUP-STR-010 | Validated Design Component Iteration | `Unknown` | Medium |
| DUP-STR-011 | Well-Consolidated Component Inspector | `game/strategy/services/compone` | N |
| DUP-UI2-011 | Camera Zoom Clamping Pattern | `game/ui/renderer/camera.py:114` | Simple |
| DUP-UI2-012 | Vector2 Import and Usage Consistency | `game/ui/interfaces/battle_ui.p` | Simple |
| LEG-FND-008 | Well-Organized Research Module | `game/research/` | N |
| LEG-SIM-009 | TechPresetLoader Used Only in Tests | `game/simulation/systems/tech_p` | N |
| UNK-03 | PlayerConfig backwards compatibility com | `Unknown` | Unknown |
| UNK-04 | FleetOrderProcessor legacy behavior is i | `Unknown` | Unknown |
| UNK-05 | project_path_as_dicts backward compatibi | `Unknown` | Unknown |
| UNK-06 | expected_stats fallback in ShipStatsCalc | `Unknown` | Unknown |
| UNK-07 | DesignMetadata sprite_preview placeholde | `Unknown` | Unknown |
| LEG-UI2-009 | Singleton Pattern Still in Use for Asset | `game/ui/assets/ship_theme_mana` | N |
| LEG-UI2-010 | Anticipatory Code in _CONTEXT_OVERLAP | `game/ui/services/input_mapper.` | Simple |
| LEG-UI1-012 | Legacy Keys Filtering in stats_config.py | `game/ui/screens/builder/stats_` | Simple |
| UNK-01 | game/core/resources.py - No dedicated te | `Unknown` | Unknown |
| UNK-02 | game/ai/controller.py - Excellent covera | `Unknown` | Unknown |
| UNK-06 | game/engine/spatial.py - Good coverage i | `Unknown` | Unknown |
| UNK-07 | game/engine/physics.py - Good coverage i | `Unknown` | Unknown |
| UNK-08 | game/engine/collision.py - Good coverage | `Unknown` | Unknown |
| UNK-09 | Profiler.toggle() not explicitly tested | `Unknown` | Unknown |
| UNK-10 | TargetEvaluator._eval_speed_rule() - Par | `Unknown` | Unknown |
| UNK-11 | TargetEvaluator._eval_least_armor_rule() | `Unknown` | Unknown |
| UNK-12 | ResearchTracker.spread_rp_evenly() - Com | `Unknown` | Unknown |
| UNK-13 | AI targeting critical path - Well covere | `Unknown` | Unknown |
| UNK-14 | Research breakthrough critical path - We | `Unknown` | Unknown |
| UNK-16 | Test isolation technique is good | `Unknown` | Unknown |
| UNK-19 | No integration tests for Engine module | `Unknown` | Unknown |
| UNK-22 | No fuzz tests for JSON parsing | `Unknown` | Unknown |
| TCG-SIM-017 | Test Organization Inconsistency | `tests/unit/simulation/` | N |
| TCG-SIM-018 | Simulation Integration Tests Sparse | `tests/integration/` | N |
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
| Total Findings | 273 |
| Critical | 17 |
| Major | 93 |
| Minor | 109 |
| Info | 54 |
| Agents Used | 25 |

---
*Report generated: 2026-02-13 00:54*
