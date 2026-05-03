# Review Report: 2026-02-10_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-11
- **Type:** Review
- **Description:** 
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 303
- **Critical:** 61 | **Major:** 116 | **Minor:** 99 | **Info:** 27
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Research/UI Cross-Layer Dependency
**ID:** ADR-FND-001
**Agent:** Architecture Foundation
**Location:** `game/research/ui/research_scene.py:14`
**Effort:** Medium

**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:14` AND `game/research/ui/research_renderer.py:12`
**Issue:** Research layer imports from game.ui.renderer.camera: `from game.ui.renderer.camera import Camera`. Per architecture rules, research layer should only depend on core. This creates cross-layer dependency on UI subsystem.
**Impact:** Violates layer separation principle. Creates implicit coupling to entire UI subsystem. Makes research layer harder to test in isolation.
...

---

### 2. CRITICAL: Pygame Import in Simulation Layer
**ID:** ADR-SIM-001
**Agent:** Architecture Simulation
**Location:** `game/simulation/services/design_loader.py:69`
**Effort:** Simple

**ID:** ADR-SIM-001
**Location:** `game/simulation/services/design_loader.py:69`
**Issue:** Direct pygame import: `import pygame; ship.position = pygame.math.Vector2(center_x, center_y)`. Simulation layer must not depend on pygame. game.core.math.Vector2 exists as framework-agnostic alternative.
**Impact:** Violates strict layer boundary (Simulation must not depend on UI/Pygame). Creates tight coupling to pygame implementation.
**Recommendation:** Replace pygame.math.Vector2 with game.core.math....

---

### 3. CRITICAL: AI Layer Imports (Mitigated but Present)
**ID:** ADR-SIM-002
**Agent:** Architecture Simulation
**Location:** `game/simulation/systems/battle_engine.py:73,278,348,508`
**Effort:** Medium

**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/battle_engine.py:73,278,348,508`, `game/simulation/factories/ai_factory.py:57-58`
**Issue:** Runtime imports from game.ai in factory methods and deprecated legacy paths. Uses TYPE_CHECKING blocks to minimize compile-time coupling. Factory pattern and PROJ-43/PROJ-17 comments acknowledge this as designed compromise.
**Impact:** Cross-layer dependency exists but is controlled. Deprecated paths still active with warnings.
**Recommendation:*...

---

### 4. CRITICAL: Private Attribute Access in BattleUIService
**ID:** ADR-UI2-001
**Agent:** Architecture Ui Framework
**Location:** `game/ui/services/battle_ui_service.py:133-134`
**Effort:** Simple

**ID:** ADR-UI2-001
**Location:** `game/ui/services/battle_ui_service.py:133-134`
**Issue:** Accessing private _resources attribute: `getattr(ship_resources, '_resources', {})`. Violates encapsulation by relying on private implementation details.
**Impact:** If resources object changes internal structure, this breaks silently.
**Recommendation:** Use public method like get_all_resources() or define explicit API.
**Effort:** Simple

---

### 5. CRITICAL: Excessive getattr() Chains Indicating Fragile Contract
**ID:** ADR-UI2-002
**Agent:** Architecture Ui Framework
**Location:** `game/ui/services/battle_ui_service.py:132-195`
**Effort:** Medium

**ID:** ADR-UI2-002
**Location:** `game/ui/services/battle_ui_service.py:132-195`
**Issue:** 20+ getattr() calls with fallback defaults suggest ship object has unstable interface. Each defensive check indicates missing protocol/interface contract.
**Impact:** Fragile data transformation layer. Silent failures in battle rendering.
**Recommendation:** Define explicit IShipDTO conversion protocol that Ship implements.
**Effort:** Medium

---

### 6. CRITICAL: Unauthorized AI Layer Dependencies (8 files)
**ID:** ADR-UI1-001
**Agent:** Architecture Ui Screens
**Location:** `game/ui/screens/builder/main.py:724`
**Effort:** Medium

**ID:** ADR-UI1-001
**Location:** `game/ui/screens/builder/main.py:724`, `game/ui/screens/builder/right_panel.py:13,114,206`, `game/ui/screens/setup_renderer.py:7,10`, `game/ui/screens/setup_screen.py`, `game/ui/screens/workshop_data_loader.py`, `game/ui/panels/ship_stats_renderer.py:12`, `game/ui/orchestration/battle_orchestrator.py`, `game/ui/screens/workshop_event_router.py`
**Issue:** 8 UI files import from game.ai.strategy_manager. UI should not depend on AI layer. StrategyManager singleton...

---

### 7. CRITICAL: UI Importing Simulation Service Internals
**ID:** ADR-UI1-002
**Agent:** Architecture Ui Screens
**Location:** `game/ui/screens/strategy_screen.py:425,438`
**Effort:** Medium

**ID:** ADR-UI1-002
**Location:** `game/ui/screens/strategy_screen.py:425,438`, `game/ui/screens/build_queue_screen.py`, `game/ui/panels/build_queue_controller.py`, `game/ui/services/design_loader_adapter.py`
**Issue:** 4 files import SimulationDesignLoader directly. UI couples to simulation service implementation details. TYPE_CHECKING guards insufficient for runtime coupling.
**Impact:** Blocks future simulation layer refactoring. UI directly couples to internal service.
**Recommendation:** Cr...

---

### 8. CRITICAL: Error Code String Literal vs Enum Inconsistency
**ID:** CON-FND-001
**Agent:** Consistency Foundation
**Location:** `game/ai/strategy_manager.py:48`
**Effort:** Medium

**ID:** CON-FND-001
**Location:** `game/ai/strategy_manager.py:48` ("AI001"), `game/core/exceptions.py:18` ("V002"), `game/core/exceptions.py:29` ("P003"), `game/core/validation.py:89` ("E001")
**Issue:** ErrorCode enum exists in error_codes.py but raw strings used in 4 locations. "AI001" and "E001" don't exist in the enum.
**Impact:** Programmatic error handling unpredictable. Violates PROJ-45 error code standardization.
**Recommendation:** Standardize all error codes to use ErrorCode.ENUM_NAME...

---

### 9. CRITICAL: Inconsistent Static Method Naming Convention
**ID:** CON-FND-002
**Agent:** Consistency Foundation
**Location:** `game/ai/controller.py:269,277`
**Effort:** Simple

**ID:** CON-FND-002
**Location:** `game/ai/controller.py:269,277` (_stat_ prefix) vs `game/ai/target_evaluator.py:403,416` (_default_ prefix)
**Issue:** Two different naming prefixes for static utility methods with identical purpose. _stat_get_hp_percent() vs _default_get_hp_percent() do the same thing.
**Impact:** Cognitive load for API discovery. Indicates incomplete refactoring.
**Recommendation:** Rename all _stat_* to _default_* for consistency.
**Effort:** Simple

---

### 10. CRITICAL: Missing Return Type on Helper Method
**ID:** CON-FND-003
**Agent:** Consistency Foundation
**Location:** `game/ai/controller.py:97-106`
**Effort:** Simple

**ID:** CON-FND-003
**Location:** `game/ai/controller.py:97-106` (get_engage_distance_multiplier)
**Issue:** Returns float but has no return type hint. All other AIController methods have return type hints.
**Impact:** Breaks type checking consistency in AIController.
**Recommendation:** Add -> float return type hint.
**Effort:** Simple

---


## Findings by Severity

### Critical (61)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Research/UI Cross-Layer Dependency | `game/research/ui/research_scen` | Medium |
| ADR-SIM-001 | Pygame Import in Simulation Layer | `game/simulation/services/desig` | Simple |
| ADR-SIM-002 | AI Layer Imports (Mitigated but Present) | `game/simulation/systems/battle` | Medium |
| ADR-UI2-001 | Private Attribute Access in BattleUIServ | `game/ui/services/battle_ui_ser` | Simple |
| ADR-UI2-002 | Excessive getattr() Chains Indicating Fr | `game/ui/services/battle_ui_ser` | Medium |
| ADR-UI1-001 | Unauthorized AI Layer Dependencies (8 fi | `game/ui/screens/builder/main.p` | Medium |
| ADR-UI1-002 | UI Importing Simulation Service Internal | `game/ui/screens/strategy_scree` | Medium |
| CON-FND-001 | Error Code String Literal vs Enum Incons | `game/ai/strategy_manager.py:48` | Medium |
| CON-FND-002 | Inconsistent Static Method Naming Conven | `game/ai/controller.py:269,277` | Simple |
| CON-FND-003 | Missing Return Type on Helper Method | `game/ai/controller.py:97-106` | Simple |
| CON-FND-004 | Inconsistent IControllable Protocol Docu | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-005 | Invalid Error Code in Documentation Exam | `game/core/validation.py:89` | Simple |
| CON-SIM-001 | Inconsistent Result Type Naming (BattleR | `game/simulation/battle_state.p` | Complex |
| CON-SIM-002 | Inconsistent get_winner() Return Type | `game/simulation/systems/battle` | Medium |
| CON-SIM-003 | Missing Return Type Hints on Key Methods | `game/simulation/entities/ship_` | Medium |
| CON-STR-001 | Duplicate Method Names with Inconsistent | `game/strategy/data/fleet.py:12` | Simple |
| CON-STR-002 | Inconsistent Return Type Annotations in  | `game/strategy/data/planet.py:2` | Medium |
| CON-STR-003 | Overuse of Any Type Hint | `game/strategy/engine/commands.` | Simple |
| CON-UI2-001 | Inconsistent DI Pattern (registry_provid | `game/ui/services/vehicle_class` | Medium |
| CON-UI2-002 | Null/None Handling Inconsistency in Serv | `game/ui/services/battle_ui_ser` | Medium |
| CON-UI2-003 | Type Hints Missing on Private Methods | `game/ui/services/battle_ui_ser` | Simple |
| CON-UI2-005 | Return Type Inconsistency for File Opera | `game/ui/services/ship_io_adapt` | Medium |
| DUP-FND-001 | Singleton Initialization Pattern Duplica | `game/core/logger.py` | Medium |
| DUP-SIM-001 | Duplicated Ability Aggregation Logic | `game/simulation/entities/abili` | Medium |
| DUP-SIM-002 | Near-Duplicate ResourceConsumption Extra | `game/simulation/entities/comba` | Simple |
| DUP-SIM-003 | Modifier Effect Validation Duplication | `game/simulation/components/mod` | Medium |
| DUP-STR-001 | Component Ability Extraction Loop - Iden | `game/strategy/validation/colon` | Medium |
| DUP-STR-002 | Component Layer Iteration Pattern - Frag | `game/strategy/validation/colon` | Medium |
| DUP-UI2-001 | Service Provider Initialization Pattern  | `game/ui/services/component_ser` | Simple |
| DUP-UI1-001 | Duplicate ColumnManager Implementations | `game/ui/screens/column_manager` | Complex |
| DUP-UI1-002 | Duplicate Value Formatting Logic | `game/ui/screens/test_lab/test_` | Simple |
| DUP-UI1-003 | Duplicate Empire Resource Formatting | `game/ui/screens/build_queue_he` | Simple |
| LEG-FND-001 | Backward Compatibility Shims in Validati | `game/core/validation.py:71-184` | Medium |
| LEG-SIM-001 | Bootstrap Registry Fallback in load_comp | `game/simulation/components/com` | Complex |
| LEG-STR-001 | Save Game Format Backward Compatibility  | `game/strategy/systems/save_gam` | Medium |
| LEG-STR-002 | Global Registry Fallback in Simulation A | `game/strategy/adapters/simulat` | Medium |
| LEG-UI2-001 | Singleton Pattern Still in Use (SpriteMa | `game/ui/renderer/sprites.py:1-` | Complex |
| LEG-UI2-002 | Deprecated Flag-Based Action Attributes  | `game/ui/screens/strategy_scree` | Simple |
| LEG-UI1-001 | Deprecated Action Flags for Scene Transi | `game/ui/screens/battle_screen.` | Medium |
| LEG-UI1-002 | Backward Compatibility Shims for BuildQu | `game/ui/screens/build_queue_sc` | Medium |
| TCG-FND-001 | Hex Math Module - No Unit Test Coverage | `game/core/hex_math.py` | Medium |
| TCG-FND-002 | AI Behaviors Module - No Unit Tests | `game/ai/behaviors.py` | Complex |
| TCG-FND-003 | Registry Loading - No Error Path Tests | `game/core/resources.py` | Medium |
| TCG-SIM-001 | Registry Loader Service Completely Untes | `game/simulation/services/regis` | Medium |
| TCG-SIM-002 | Physics Constants Untested | `game/simulation/physics_consta` | Simple |
| TCG-SIM-003 | Battle Configuration Untested | `game/simulation/battle_config.` | Simple |
| TCG-SIM-004 | Component Status/Modifier Constants Unte | `game/simulation/components/com` | Simple |
| TCG-STR-001 | Core Radiation Physics Untested | `game/strategy/data/physics.py` | Simple |
| TCG-STR-002 | Major facade for ALL UI-engine communica | `game/strategy/facade/strategy_` | Complex |
| TCG-STR-003 | Galaxy generation placement and region c | `game/strategy/generation/place` | Complex |
| TCG-UI2-001 | No Test Coverage for game_renderer.py Cr | `c:\Dev\Starship Battles\game\u` | Complex |
| TCG-UI2-002 | SpriteManager Singleton Lacks Comprehens | `c:\Dev\Starship Battles\game\u` | Complex |
| TCG-UI2-003 | ShipThemeManager Lazy Loading Has Untest | `c:\Dev\Starship Battles\game\u` | Complex |
| TCG-UI1-001 | Core Battle Systems with Zero Test Cover | `game/ui/screens/battle_screen.` | Complex |
| TCG-UI1-002 | Strategy Screen Lacks Direct Test Covera | `game/ui/screens/strategy_scree` | Complex |
| TCG-UI1-003 | Large Build Queue Screen Undertested | `game/ui/screens/build_queue_sc` | Complex |
| TCG-UI1-004 | Fleet Report Window Completely Untested | `game/ui/screens/fleet_report_w` | Complex |
| TCG-UI1-005 | Formation Editor Screen Not Covered in U | `game/ui/screens/formation_edit` | Complex |
| TCG-UI1-006 | Race Setup Screen Lacks Adequate Testing | `game/ui/screens/race_setup_scr` | Complex |
| TCG-UI1-007 | Workshop Screen Untested Despite Complex | `game/ui/screens/workshop_scree` | Complex |
| TCG-UI1-008 | Battle UI Panel Rendering Untested | `game/ui/panels/battle_panels.p` | Medium |

### Major (116)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-002 | God Module - behaviors.py (513 lines, 11 | `game/ai/behaviors.py` | Medium |
| ADR-FND-003 | High Complexity - AIController (479 line | `game/ai/controller.py` | Complex |
| ADR-FND-004 | High Complexity - TargetEvaluator (459 l | `game/ai/target_evaluator.py` | Complex |
| ADR-SIM-003 | God Class - Ship (804 lines, 46 methods) | `game/simulation/entities/ship.` | Complex |
| ADR-SIM-004 | God Class - BattleEngine (674 lines, 20  | `game/simulation/systems/battle` | Complex |
| ADR-STR-001 | God Class - ProductionEngine (731 lines, | `game/strategy/engine/productio` | Medium |
| ADR-STR-002 | God Class - Galaxy (707 lines, 33 method | `game/strategy/data/galaxy.py` | Medium |
| ADR-STR-003 | God Class - ShipInstance (688 lines, 44  | `game/strategy/data/ship_instan` | Medium |
| ADR-STR-004 | God Class - Stars (560 lines, 17 methods | `game/strategy/data/stars.py` | Simple |
| ADR-UI2-003 | ShipThemeManager Singleton Thread Safety | `game/ui/assets/ship_theme_mana` | Simple |
| ADR-UI2-004 | game_renderer.py Tight Coupling to Simul | `game/ui/renderer/game_renderer` | Medium |
| ADR-UI2-005 | DesignLoaderAdapter Lazy Import Pattern | `game/ui/services/design_loader` | Simple |
| ADR-UI1-003 | God Class - TestLabScreen (1837 lines, 6 | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-004 | God Class - BuilderScreen (1124 lines, 4 | `game/ui/screens/builder/main.p` | Complex |
| ADR-UI1-005 | God Class - FormationEditorScreen (929 l | `game/ui/screens/formation_edit` | Medium |
| CON-FND-006 | StrategyManager Thread Safety Gap | `game/ai/strategy_manager.py:38` | Medium |
| CON-FND-007 | Inconsistent Error Code Format in Strate | `game/ai/strategy_manager.py:48` | Medium |
| CON-FND-008 | Parameter Naming Inconsistency (policy v | `game/ai/controller.py` | Simple |
| CON-FND-009 | Missing Type Hints on Module-Level Funct | `game/ai/target_evaluator.py:35` | Simple |
| CON-FND-010 | Inconsistent Import Organization | `game/ai/target_evaluator.py:1-` | Simple |
| CON-FND-011 | Boolean Parameter Naming | `game/ai/controller.py:108` | Simple |
| CON-SIM-004 | Inconsistent Optional vs Empty Collectio | `game/simulation/systems/resour` | Medium |
| CON-SIM-005 | Inconsistent Error Handling Exception Ty | `game/simulation/battle_control` | Medium |
| CON-SIM-006 | Ability Class Method Naming Inconsistenc | `Unknown` | Complex |
| CON-SIM-007 | Inconsistent Docstring Patterns in Manag | `Unknown` | Medium |
| CON-SIM-008 | Inconsistent Type Hints for Data Paramet | `Unknown` | Complex |
| CON-SIM-009 | Inconsistent Lazy Initialization Pattern | `Unknown` | Medium |
| CON-SIM-010 | Inconsistent Facade Pattern on Ship Clas | `game/simulation/entities/ship.` | Medium |
| CON-SIM-011 | Inconsistent to_dict/from_dict Implement | `Unknown` | Medium |
| CON-STR-004 | Missing Return Type Hints on Public Meth | `game/strategy/data/galaxy.py:1` | Medium |
| CON-STR-005 | Inconsistent Parameter Documentation For | `Unknown` | Simple |
| CON-STR-007 | Inconsistent Parameter Naming Convention | `game/strategy/engine/game_sess` | Medium |
| CON-STR-008 | Inconsistent Boolean Method Naming | `Unknown` | Medium |
| CON-STR-009 | Inconsistent Docstring Format | `Unknown` | Medium |
| CON-STR-010 | Inconsistent Error Handling Return Value | `Unknown` | Medium |
| CON-STR-011 | Inconsistent to_dict/from_dict Signature | `Unknown` | Complex |
| CON-STR-006 | Inconsistent Return Documentation | `Unknown` | Medium |
| CON-UI2-006 | ShipThemeManager Singleton Pattern Viola | `game/ui/assets/ship_theme_mana` | Medium |
| CON-UI2-007 | Inconsistent Constructor Parameter Namin | `Unknown` | Simple |
| CON-UI2-008 | Camera Class API Inconsistency | `game/ui/renderer/camera.py:8-1` | Medium |
| CON-UI2-009 | BattleUIService Conversion Methods Lack  | `game/ui/services/battle_ui_ser` | Medium |
| CON-UI2-010 | Inconsistent Method Prefix Patterns | `Unknown` | Simple |
| CON-UI1-001 | Event Handler Naming Inconsistency (hand | `Unknown` | Complex |
| CON-UI1-002 | Type Hint Coverage Inconsistency | `Unknown` | Medium |
| CON-UI1-003 | Docstring Coverage Gap | `Unknown` | Medium |
| CON-UI1-004 | Return Type Inconsistency in Similar Fun | `Unknown` | Complex |
| CON-UI1-005 | Click Handler Parameter Inconsistency | `Unknown` | Medium |
| DUP-FND-002 | Position and Rotation Helper Functions D | `game/ai/target_evaluator.py:35` | Simple |
| DUP-FND-003 | JSON File Loading Pattern (15 files) | `game/core/resources.py` | Simple |
| DUP-FND-004 | HP Percentage and PDC Arc Check Utilitie | `game/ai/controller.py:269-282` | Simple |
| DUP-SIM-004 | Ability Instance Retrieval Pattern Dupli | `game/simulation/components/com` | Complex |
| DUP-SIM-005 | Component Status Checking Pattern Repeat | `game/simulation/combat/weapon_` | Simple |
| DUP-SIM-006 | Ability Value Extraction Pattern (get_pr | `game/simulation/entities/abili` | Medium |
| DUP-SIM-007 | Serialization Stat Verification Logic | `game/simulation/entities/ship_` | Simple |
| DUP-STR-003 | "Find Ship With Ability" Logic Duplicate | `game/strategy/validation/colon` | Simple |
| DUP-STR-004 | "Get Available/Committed Pods" Pattern D | `game/strategy/validation/colon` | Medium |
| DUP-STR-005 | Resource Consumption Verification - Dupl | `game/strategy/data/fleet_resou` | Medium |
| DUP-STR-006 | Ship Component Inspection - Nearly Ident | `game/strategy/data/fleet_capab` | Simple |
| DUP-UI2-002 | Cache Hit Check Pattern in ShipThemeMana | `game/ui/assets/ship_theme_mana` | Medium |
| DUP-UI2-003 | Placeholder Image Generation (3 location | `game/ui/utils.py:154-156` | Simple |
| DUP-UI2-004 | Double-Checked Locking Pattern (Singleto | `game/ui/assets/ship_theme_mana` | Medium |
| DUP-UI1-004 | Three Similar Format Functions for Star/ | `game/ui/screens/strategy_detai` | Medium |
| DUP-UI1-005 | Gallery Pattern Duplication (RacePortrai | `game/ui/panels/race_portrait_g` | Complex |
| DUP-UI1-006 | Draw Utilities Duplication | `game/ui/screens/battle_panels.` | Simple |
| DUP-UI1-007 | Filter Manager Pattern Duplication | `game/ui/screens/empire_build_q` | Medium |
| DUP-UI1-008 | Build Queue Formatting Fragmentation | `game/ui/screens/build_queue_he` | Medium |
| LEG-FND-002 | Proxy Pattern for Global Logger Access | `game/core/logger.py:68-69, 71-` | Medium |
| LEG-FND-003 | Global Proxy for Profiler Access | `game/core/profiling.py:135-146` | Medium |
| LEG-FND-004 | Orphaned Factory Methods in ValidationRe | `game/core/validation.py:105-11` | Simple |
| LEG-SIM-002 | Dead Delegation Methods in BattleControl | `game/simulation/battle_control` | Simple |
| LEG-SIM-003 | Backward Compatibility Wrapper Functions | `game/simulation/components/com` | Medium |
| LEG-SIM-004 | Deprecated AI Controller Initialization  | `game/simulation/systems/battle` | Medium |
| LEG-STR-003 | Deprecated Parameter Support in GameSess | `game/strategy/engine/game_sess` | Simple |
| LEG-STR-004 | hasattr() Defensive Checks for Fleet Pro | `game/strategy/services/fleet_n` | Simple |
| LEG-STR-005 | Facility.construction_queue Defensive Ch | `game/strategy/engine/productio` | Simple |
| LEG-STR-006 | Legacy Mass Field in DesignMetadata | `game/strategy/data/design_meta` | Medium |
| LEG-STR-007 | Fleet Order Serialization Format Multipl | `game/strategy/data/fleet.py:36` | Complex |
| LEG-UI2-003 | Legacy Backward Compat Conversion Method | `game/ui/screens/builder/compon` | Simple |
| LEG-UI2-004 | Deprecated base_path Parameter (ShipThem | `game/ui/assets/ship_theme_mana` | Simple |
| LEG-UI2-005 | Deprecated Property Access (StrategyScre | `game/ui/screens/strategy_scree` | Simple |
| LEG-UI1-003 | Legacy Tuple-Based Component Selection A | `game/ui/screens/builder/compon` | Simple |
| LEG-UI1-004 | Unused Getters in Stats Configuration | `game/ui/screens/builder/stats_` | Simple |
| LEG-UI1-005 | Hardcoded Backward Compat Fallback for I | `game/ui/screens/strategy_input` | Medium |
| LEG-UI1-006 | Backward Compatibility Properties in Wor | `game/ui/screens/workshop_viewm` | Simple |
| LEG-UI1-007 | Legacy Component Editor Still Used | `game/ui/screens/builder/legacy` | Medium |
| TCG-FND-004 | Core Input Mapper - Incomplete Test Cove | `game/core/input_mapper.py` | Medium |
| TCG-FND-005 | Paths Module - No Unit Tests | `game/core/paths.py` | Medium |
| TCG-FND-006 | Screenshot Manager - No Unit Tests | `game/core/screenshot_manager.p` | Medium |
| TCG-FND-007 | AI Controller - Incomplete Coverage | `game/ai/controller.py` | Medium |
| TCG-FND-008 | Strategy Manager - Singleton State Not F | `game/ai/strategy_manager.py` | Medium |
| TCG-FND-009 | Target Evaluator - Rule Evaluation Edge  | `game/ai/target_evaluator.py` | Medium |
| TCG-FND-010 | Research Service - Turn Processing Edge  | `game/research/systems/research` | Medium |
| TCG-SIM-005 | Modifier Schema Validation Untested | `game/simulation/components/mod` | Medium |
| TCG-SIM-006 | Modifier Effects Evaluation Untested | `game/simulation/components/mod` | Medium |
| TCG-SIM-007 | Marker Abilities Untested | `game/simulation/components/abi` | Simple |
| TCG-SIM-008 | Stat Keys and Ability Bindings Untested | `game/simulation/components/abi` | Simple |
| TCG-SIM-009 | Modifier Application Logic Untested | `game/simulation/components/mod` | Simple |
| TCG-STR-004 | Star, Spectrum, and StarGenerator classe | `game/strategy/data/stars.py` | Medium |
| TCG-STR-005 | Planet naming utility functions includin | `game/strategy/data/planet_nami` | Simple |
| TCG-STR-006 | Interface contracts for TurnEngine sub-e | `game/strategy/interfaces/engin` | Medium |
| TCG-STR-007 | QuickstartBuilder factory for creating t | `game/strategy/quickstart_build` | Medium |
| TCG-STR-008 | Configuration classes and loaders for pl | `game/strategy/data/classificat` | Simple |
| TCG-UI2-004 | Camera.py Lacks Edge Case and Integratio | `c:\Dev\Starship Battles\game\u` | Medium |
| TCG-UI2-005 | BattleUIService DTO Conversion Missing E | `c:\Dev\Starship Battles\game\u` | Medium |
| TCG-UI2-006 | game/ui/utils.py Image Scaling Functions | `c:\Dev\Starship Battles\game\u` | Medium |
| TCG-UI2-007 | Vehicle/Component Service Tests Missing  | `c:\Dev\Starship Battles\game\u` | Medium |
| TCG-UI1-009 | Menu Scene Not Tested | `game/ui/screens/menu_scene.py` | Simple |
| TCG-UI1-010 | Battle Setup Screen Partially Untested | `game/ui/screens/setup_screen.p` | Medium |
| TCG-UI1-011 | Strategy Input Handler Missing Core Test | `game/ui/screens/strategy_input` | Medium |
| TCG-UI1-012 | Strategy Renderer Completely Untested | `game/ui/screens/strategy_rende` | Medium |
| TCG-UI1-013 | Strategy Detail Formatters Undertested | `game/ui/screens/strategy_detai` | Medium |
| TCG-UI1-014 | Strategy Superweapon Operations Untested | `game/ui/screens/strategy_super` | Medium |
| TCG-UI1-015 | Planet List Components Partially Unteste | `game/ui/screens/planet_list_*.` | Medium |
| TCG-UI1-016 | Window Management Components Undertested | `game/ui/screens/strategy_windo` | Medium |
| TCG-UI1-017 | Design Selector and Related Windows Unte | `game/ui/screens/design_selecto` | Medium |
| TCG-UI1-018 | Race Setup and Asset Components Poorly T | `game/ui/screens/race_asset_loa` | Simple |

### Minor (99)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-005 | Missing Type Annotations in TargetEvalua | `game/ai/target_evaluator.py:35` | Simple |
| ADR-SIM-005 | Private Attribute Access (_registries) | `game/simulation/systems/battle` | Simple |
| ADR-SIM-006 | Private Attribute Modification (_hp_rati | `game/simulation/battle_state.p` | Simple |
| ADR-UI2-006 | Inconsistent DI Patterns Across Services | `Unknown` | Medium |
| ADR-UI2-007 | SpriteManager Singleton Without Validati | `game/ui/renderer/sprites.py:58` | Simple |
| ADR-UI2-008 | ShipThemeManager Inefficient Path Resolu | `game/ui/assets/ship_theme_mana` | Simple |
| ADR-UI1-006 | Law of Demeter Violations (27 files) | `Unknown` | Medium |
| ADR-UI1-007 | Strategy Data Objects in UI Layer | `Unknown` | Medium |
| CON-FND-012 | Non-standard Class Suffixes | `Unknown` | None |
| CON-FND-013 | Mixed Dictionary vs Object Access Patter | `game/ai/controller.py:94-96` | Medium |
| CON-FND-014 | Incomplete Docstrings in Public Methods | `game/ai/controller.py:92` | Simple |
| CON-FND-015 | Unused Static/Instance Method Duplicatio | `game/ai/controller.py:268-274` | Simple |
| CON-FND-016 | Inconsistent Constants Naming | `game/ai/behaviors.py:87,103,12` | Simple |
| CON-FND-017 | Missing Docstrings on Test/Debug Classes | `game/ai/behaviors.py:396-472` | Simple |
| CON-FND-018 | Inconsistent Return Value Convention | `game/research/data/tech_tree.p` | None |
| CON-FND-019 | Missing Registry Exception Handling | `game/core/registry.py:222-260` | Simple |
| CON-SIM-012 | Parameter Naming Inconsistency | `Unknown` | Simple |
| CON-SIM-013 | Docstring Completeness Varies | `Unknown` | Simple |
| CON-SIM-014 | Inconsistent Method Ordering in Classes | `Unknown` | Simple |
| CON-SIM-015 | Inconsistent Default Parameter Values | `Unknown` | Simple |
| CON-SIM-016 | Missing Module-Level Constants | `Unknown` | Simple |
| CON-STR-012 | Comment Style Inconsistency in Data Stru | `Unknown` | Simple |
| CON-STR-013 | Enum Value Naming Consistent | `Unknown` | None |
| CON-STR-014 | Private Method Naming Consistent | `Unknown` | None |
| CON-STR-015 | Type Import Organization | `Unknown` | Simple |
| CON-STR-016 | Dataclass Field Ordering | `Unknown` | Simple |
| CON-UI2-011 | Docstring Style Inconsistency | `Unknown` | Simple |
| CON-UI2-012 | Magic Numbers in Renderer Viewport | `game/ui/renderer/camera.py:109` | Simple |
| CON-UI2-013 | Overloaded Semantic Meaning of "is_alive | `game/ui/interfaces/battle_ui.p` | Simple |
| CON-UI1-006 | Error Handling Strategy Mixing | `Unknown` | Medium |
| CON-UI1-007 | Class Suffix Naming Overload | `Unknown` | Simple |
| CON-UI1-008 | Import Organization Inconsistency | `Unknown` | Simple |
| CON-UI1-009 | Magic Numbers in UI Rendering | `Unknown` | Medium |
| DUP-FND-005 | Validation Result Creation Pattern Redun | `game/core/validation.py` | Simple |
| DUP-FND-006 | Distance Calculation Across Modules (5 f | `game/ai/target_evaluator.py:10` | Simple |
| DUP-SIM-008 | Validation Rule Duplication Pattern | `game/simulation/validation/shi` | Simple |
| DUP-SIM-009 | Distance/Position Calculation Patterns | `game/simulation/combat/targeti` | Simple |
| DUP-SIM-010 | Resource Consumption Tracking Duplicated | `game/simulation/entities/comba` | Medium |
| DUP-STR-007 | Distance/Location Calculation Patterns i | `game/strategy/data/pathfinding` | Simple |
| DUP-STR-008 | Loader Pattern Duplication in 3 Configur | `game/strategy/generation/loade` | Simple |
| DUP-STR-009 | Density Primitive Evaluation Falloff Pat | `game/strategy/generation/densi` | Simple |
| DUP-UI2-005 | Scale/Rotation Utility Functions Fragmen | `game/ui/utils.py` | Simple |
| DUP-UI1-009 | Similar K/M Number Formatting | `Unknown` | Simple |
| DUP-UI1-010 | Team 1/Team 2 Display Loop Duplication | `game/ui/screens/battle_panels.` | Simple |
| LEG-FND-005 | Unused Parameters in Target Evaluator | `game/ai/target_evaluator.py` | Simple |
| LEG-FND-006 | MagicMock Detection in Production Code | `game/ai/target_evaluator.py:53` | Simple |
| LEG-FND-007 | Inconsistent "old_" Variable Naming Patt | `game/research/systems/research` | Simple |
| LEG-SIM-005 | Commented Legacy Code - Removed Componen | `game/simulation/components/com` | Simple |
| LEG-SIM-006 | Safe Evaluation Wrapper - Redundant Indi | `game/simulation/formula_system` | Simple |
| LEG-STR-008 | Unused "legacy" Comment in RaceConfig | `game/strategy/data/race_config` | Simple |
| LEG-STR-009 | Migration Guide Documentation Without Co | `game/strategy/services/fleet_n` | Simple |
| LEG-STR-010 | Convenience References for Backward Comp | `game/strategy/engine/game_sess` | Simple |
| LEG-STR-011 | Design Metadata Backward-Compatible Defa | `game/strategy/data/design_meta` | Medium |
| LEG-STR-012 | Empire Serialization Legacy Visual Ident | `game/strategy/data/empire.py:1` | Simple |
| LEG-UI2-006 | Backwards Compat Wrapper Methods | `game/ui/screens/build_queue_sc` | Medium |
| LEG-UI2-007 | Fallback Image Creation Pattern | `game/ui/assets/ship_theme_mana` | Medium |
| LEG-UI2-008 | Legacy Modifier Editing Pattern | `game/ui/screens/builder/legacy` | Medium |
| LEG-UI1-008 | Sync Methods for Backward Compatibility  | `game/ui/screens/builder/right_` | Simple |
| LEG-UI1-009 | DesignReportPanel Backward Compatibility | `game/ui/panels/design_report_p` | Simple |
| LEG-UI1-010 | Deprecated action_return_to_test_lab Fla | `game/ui/screens/test_lab/scree` | Simple |
| LEG-UI1-011 | Dead Legacy Buttons List | `game/ui/screens/test_lab/scree` | Simple |
| TCG-FND-011 | Core Math Module - Vector2 Methods Not F | `game/core/math.py` | Simple |
| TCG-FND-012 | Logger Module - No Unit Tests | `game/core/logger.py` | Simple |
| TCG-FND-013 | Profiling Module - Coverage Gaps | `game/core/profiling.py` | Simple |
| TCG-FND-014 | Validation Module - Error Boundary Tests | `game/core/validation.py` | Simple |
| TCG-FND-015 | Error Codes Module - Enum Coverage | `game/core/error_codes.py` | Simple |
| TCG-FND-016 | JSON Utils Module - Edge Cases | `game/core/json_utils.py` | Simple |
| TCG-FND-017 | Configuration Module - Edge Cases | `game/core/config.py` | Simple |
| TCG-FND-018 | AI Interfaces - Adapter Coverage | `game/ai/interfaces/controllabl` | Simple |
| TCG-FND-019 | Research Tracker - Serialization Edge Ca | `game/research/data/research_tr` | Simple |
| TCG-FND-020 | Engine Physics - Floating Point Edge Cas | `game/engine/physics.py` | Simple |
| TCG-FND-021 | Spatial Grid - Query Performance Edge Ca | `game/engine/spatial.py` | Simple |
| TCG-SIM-010 | Marker Ability UI Output Not Tested | `game/simulation/components/abi` | Simple |
| TCG-SIM-011 | Component Health Manager Edge Cases | `game/simulation/components/com` | Simple |
| TCG-SIM-012 | Resource Manager Edge Cases | `game/simulation/systems/resour` | Simple |
| TCG-SIM-013 | Ability Aggregator Layer Scope Not Fully | `game/simulation/entities/abili` | Simple |
| TCG-SIM-014 | Combat Endurance Calculation Verificatio | `game/simulation/entities/comba` | Simple |
| TCG-SIM-015 | Hit/Miss Resolution Integration | `game/simulation/combat/targeti` | Medium |
| TCG-SIM-016 | Ship Formation Positioning | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-017 | Projectile Physics Integration | `game/simulation/entities/proje` | Medium |
| TCG-SIM-018 | Ship Stats Calculator Phase Ordering | `game/simulation/entities/ship_` | Medium |
| TCG-STR-009 | FleetNavigationService tests exist in `f | `game/strategy/services/fleet_n` | Medium |
| TCG-STR-010 | Pathfinding functions are tested but int | `game/strategy/data/pathfinding` | Medium |
| TCG-STR-011 | ConflictResolutionEngine has unit tests  | `game/strategy/engine/conflict_` | Medium |
| TCG-STR-012 | AstrophysicsLoader, GalaxyLayoutsLoader, | `game/strategy/generation/loade` | Simple |
| TCG-STR-013 | BuildQueueSource collection functions ar | `game/strategy/data/build_queue` | Simple |
| TCG-STR-014 | SimulationBattleResolver implementation  | `game/strategy/adapters/simulat` | Simple |
| TCG-STR-015 | Display formatter has unit tests but edg | `game/strategy/data/ship_displa` | Simple |
| TCG-UI2-008 | game/ui/colors.py Has No Dedicated Test  | `c:\Dev\Starship Battles\game\u` | Simple |
| TCG-UI2-009 | widgets.py Legacy Code Lacks Button/Labe | `c:\Dev\Starship Battles\game\u` | Simple |
| TCG-UI2-010 | ShipIOAdapter and ValidationService Miss | `c:\Dev\Starship Battles\game\u` | Simple |
| TCG-UI2-011 | Orchestration/Interfaces Missing Cross-L | `c:\Dev\Starship Battles\game\u` | Simple |
| TCG-UI1-019 | Panel Component Test Coverage Gaps | `game/ui/panels/` | Medium |
| TCG-UI1-020 | Test Quality: Insufficient Assertions in | `tests/unit/ui/screens/test_str` | Simple |
| TCG-UI1-021 | Test Quality: Over-Mocking in Event Proc | `tests/unit/ui/screens/` | Medium |
| TCG-UI1-022 | Missing Error Path Testing | `Unknown` | Medium |
| TCG-UI1-023 | Edge Case Testing Gaps | `Unknown` | Medium |
| TCG-UI1-024 | Screen Resize Handling Untested | `Unknown` | Simple |
| TCG-UI1-025 | Builder Subdirectory Test Organization | `game/ui/screens/builder/` | Simple |

### Info (27)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-007 | Simulation-AI Coupling is Controlled | `Unknown` | None |
| ADR-UI2-009 | TYPE_CHECKING Import Not Isolated in Bat | `game/ui/services/battle_ui_ser` | Medium |
| ADR-UI2-010 | BattleOrchestrator Cross-Layer Imports ( | `game/ui/orchestration/battle_o` | None |
| ADR-UI1-008 | TYPE_CHECKING Imports Insufficient | `Unknown` | Complex |
| ADR-UI1-009 | Private Attribute Access to Session | `game/ui/screens/strategy_scree` | Simple |
| CON-SIM-017 | Unused Imports in Several Files | `Unknown` | Simple |
| CON-SIM-018 | Inconsistent Test Data Naming | `Unknown` | Simple |
| CON-SIM-019 | Docstring Cross-Reference Format | `Unknown` | Simple |
| CON-SIM-020 | Inconsistent Comment Style | `Unknown` | Simple |
| CON-STR-017 | Late Import Comments Inconsistent | `Unknown` | Simple |
| CON-STR-018 | Missing TypedDict for Complex Returns | `Unknown` | Medium |
| CON-STR-019 | Inconsistent Logging Levels | `Unknown` | Simple |
| CON-STR-020 | Inconsistent None Checking Patterns | `Unknown` | Simple |
| CON-UI2-014 | PROJ References Without Version Tracking | `Unknown` | None |
| CON-UI2-015 | Legacy Widgets Class | `game/ui/widgets.py` | Medium |
| CON-UI1-010 | Getter Method Naming Consistent | `Unknown` | None |
| CON-UI1-011 | Boolean Method Naming Mostly Consistent | `Unknown` | None |
| CON-UI1-012 | Private Method Naming Edge Cases | `Unknown` | None |
| LEG-FND-008 | TypeGuard Import Fallback | `game/core/protocols.py:32-36` | Simple |
| LEG-SIM-007 | Legacy Fallback Pattern Comment in Resul | `game/simulation/battle_control` | Simple |
| LEG-STR-013 | Classification Config Backward Compatibi | `game/strategy/data/classificat` | Simple |
| LEG-STR-014 | Registry Fallback Pattern in Facade | `game/strategy/facade/strategy_` | Simple |
| TCG-UI2-012 | __init__.py Files Have Module-Level Impo | `c:\Dev\Starship Battles\game\u` | Simple |
| TCG-UI1-026 | Formation Tests Spread Across Multiple L | `Unknown` | Simple |
| TCG-UI1-027 | Integration Tests Cover Some Untested Sc | `tests/integration/ui/` | Medium |
| TCG-UI1-028 | Test Lab Scene Only Partially Tested | `game/ui/screens/test_lab/` | Medium |
| TCG-UI1-029 | Some Tests Check State But Don't Verify  | `Unknown` | Simple |


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
| Total Findings | 303 |
| Critical | 61 |
| Major | 116 |
| Minor | 99 |
| Info | 27 |
| Agents Used | 25 |

---
*Report generated: 2026-02-11 05:59*
