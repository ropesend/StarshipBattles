# Review Report: 2026-02-13_092036_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-13
- **Type:** Review
- **Description:** 
- **Agents Used:** 23

## Executive Summary
- **Total Findings:** 268
- **Critical:** 15 | **Major:** 94 | **Minor:** 114 | **Info:** 45
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Research UI layer imports from game.ui
**ID:** ADR-FND-001
**Agent:** Architecture Foundation
**Location:** `game/research/ui/research_scene.py:19`
**Effort:** Medium

**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:19`
**Issue:** The research module imports `Camera` from `game.ui.renderer.camera`. According to the architecture rules, the research layer should only depend on core. This violates the layer hierarchy by making research dependent on the UI layer.
**Import line:** `from game.ui.renderer.camera import Camera`
**Impact:**
- The research module cannot be used without the UI layer being available
- Creates a circular dependency co...

---

### 2. CRITICAL: Simulation imports AI layer in factory functions
**ID:** ADR-SIM-001
**Agent:** Architecture Simulation
**Location:** `game/simulation/battle_controller.py:718`
**Effort:** Medium

**ID:** ADR-SIM-001
**Location:** `game/simulation/battle_controller.py:718`
**Issue:** The `_create_default_ai_factory()` function contains a runtime import from the AI layer:
```python
def _create_default_ai_factory() -> 'IAIControllerFactory':
    from game.ai.ai_factory import AIControllerFactory
    return AIControllerFactory()
```
This violates the layer dependency rule: Simulation -> Core only. AI should depend on Simulation, not vice versa.
**Impact:**
- Creates bidirectional coupling be...

---

### 3. CRITICAL: Inconsistent Error Handling Return Types
**ID:** CON-STR-001
**Agent:** Consistency Strategy
**Location:** `game/strategy/validation/colonize_validator.py`
**Effort:** Medium

**ID:** CON-STR-001
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`, `game/strategy/validation/superweapon_validator.py`
**Issue:** ColonizeValidator.validate() returns a ValidationResult with errors list, but the error messages are inconsistent with TransferValidator. ColonizeValidator uses lowercase "required" messages while SuperweaponValidator uses proper sentences. Some validators check for None target first, others embed it i...

---

### 4. CRITICAL: Number Formatting with K/M Suffixes Duplicated
**ID:** DUP-UI1-001
**Agent:** Duplication Ui Screens
**Location:** `game/ui/panels/planet_report_panel.py:303-310`
**Effort:** Simple

**ID:** DUP-UI1-001
**Location:** `game/ui/panels/planet_report_panel.py:303-310` AND `game/ui/screens/strategy_detail_fmt.py:101-130`
**Issue:** Two separate implementations of compact number formatting with K/M suffixes. The `planet_report_panel.py` has a `_format_compact_number()` method that formats values with K/M suffixes, while `strategy_detail_fmt.py` has inline code duplicating this logic three times (for total_pop, max_pop, and individual pop.count). The implementations have slight inc...

---

### 5. CRITICAL: PhysicsBody Has Minimal Direct Unit Tests
**ID:** TCG-FND-001
**Agent:** Test Coverage Foundation
**Location:** `game/engine/physics.py`
**Effort:** Medium

**ID:** TCG-FND-001
**Location:** `game/engine/physics.py` (production) / `tests/unit/systems/test_physics_edge_cases.py` (partial tests)
**Issue:** PhysicsBody is the foundational class for all physical entities, yet direct unit tests only cover edge cases (velocity, mass, drag). Missing tests for:
- `update()` method integration (acceleration application, drag factor clamping, position/angle updates)
- `apply_force()` method with various force magnitudes and mass values
- `forward_vector()` me...

---

### 6. CRITICAL: Research UI Components Have No Pygame-Independent Unit Tests
**ID:** TCG-FND-002
**Agent:** Test Coverage Foundation
**Location:** `game/research/ui/research_controls.py`
**Effort:** Complex

**ID:** TCG-FND-002
**Location:** `game/research/ui/research_controls.py`, `game/research/ui/research_renderer.py` (production) / `tests/unit/research/` (tests exist but mock pygame)
**Issue:** The research UI components (ResearchControlPanel, ResearchRenderer) have limited testable behavior extraction. Current tests exist but focus on event formatting and state management. Missing tests for:
- `ResearchRenderer._draw_dashed_line()` math calculations (dashed line rendering for negated requiremen...

---

### 7. CRITICAL: FleetNavigationService Missing Comprehensive Unit Tests
**ID:** TCG-STR-001
**Agent:** Test Coverage Strategy
**Location:** `game/strategy/services/fleet_navigation_service.py`
**Effort:** Medium

**ID:** TCG-STR-001
**Location:** `game/strategy/services/fleet_navigation_service.py` (production) / `tests/unit/strategy/fleet_navigation/` (test gap)
**Issue:** The FleetNavigationService class (468 lines) has tests for individual navigation components (projection, data structures, destination path) but lacks comprehensive unit tests for the service class itself. Key methods like `compute_next_step()`, `calculate_fleet_next_hex()`, and path recalculation logic (`_needs_path_recalculation`) ha...

---

### 8. CRITICAL: Command Handler Coverage Incomplete
**ID:** TCG-STR-002
**Agent:** Test Coverage Strategy
**Location:** `game/strategy/engine/command_handlers.py`
**Effort:** Medium

**ID:** TCG-STR-002
**Location:** `game/strategy/engine/command_handlers.py` (production) / `tests/unit/strategy/test_command_handlers.py` (partial tests)
**Issue:** While test_command_handlers.py exists, review shows it focuses on ColonizeCommandHandler and MoveCommandHandler. Missing test coverage for: InterceptCommandHandler, JoinCommandHandler, ColonizeMissionCommandHandler, ClearOrdersCommandHandler, and TransferCommandHandler. These handlers execute critical game state mutations.
**Impact:...

---

### 9. CRITICAL: Superweapon Order Processor Missing Error Path Tests
**ID:** TCG-STR-003
**Agent:** Test Coverage Strategy
**Location:** `game/strategy/engine/superweapon_order_processor.py`
**Effort:** Medium

**ID:** TCG-STR-003
**Location:** `game/strategy/engine/superweapon_order_processor.py` (production) / `tests/unit/strategy/engine/test_superweapon_order_processor.py` (test gap)
**Issue:** The superweapon tests exist but inspection shows they focus on happy-path execution. Missing tests for: validation failures (wrong ship at wrong location), partial fleet destruction during stellerate, invalid targets, and cooldown enforcement. Superweapon effects are destructive and irreversible.
**Impact:** ...

---

### 10. CRITICAL: Production Engine Tick Consumption Edge Cases
**ID:** TCG-STR-004
**Agent:** Test Coverage Strategy
**Location:** `game/strategy/engine/production_engine.py`
**Effort:** Complex

**ID:** TCG-STR-004
**Location:** `game/strategy/engine/production_engine.py` (production) / `tests/unit/strategy/production_engine/test_tick_consumption.py` (partial)
**Issue:** The test_tick_consumption.py file exists but lacks edge case tests for: queue exhaustion mid-tick, multiple items completing same tick, resource depletion preventing completion, and interactions with fleet production queues. The production engine handles complex multi-tick processing.
**Impact:** Production could comple...

---


## Findings by Severity

### Critical (15)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Research UI layer imports from game.ui | `game/research/ui/research_scen` | Medium |
| ADR-SIM-001 | Simulation imports AI layer in factory f | `game/simulation/battle_control` | Medium |
| CON-STR-001 | Inconsistent Error Handling Return Types | `game/strategy/validation/colon` | Medium |
| DUP-UI1-001 | Number Formatting with K/M Suffixes Dupl | `game/ui/panels/planet_report_p` | Simple |
| TCG-FND-001 | PhysicsBody Has Minimal Direct Unit Test | `game/engine/physics.py` | Medium |
| TCG-FND-002 | Research UI Components Have No Pygame-In | `game/research/ui/research_cont` | Complex |
| TCG-STR-001 | FleetNavigationService Missing Comprehen | `game/strategy/services/fleet_n` | Medium |
| TCG-STR-002 | Command Handler Coverage Incomplete | `game/strategy/engine/command_h` | Medium |
| TCG-STR-003 | Superweapon Order Processor Missing Erro | `game/strategy/engine/superweap` | Medium |
| TCG-STR-004 | Production Engine Tick Consumption Edge  | `game/strategy/engine/productio` | Complex |
| TCG-UI2-001 | game_renderer.py Has No Test Coverage | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI1-001 | Builder Module Completely Untested | `game/ui/screens/builder/` | Complex |
| TCG-UI1-002 | Test Lab Module Minimal Coverage | `game/ui/screens/test_lab/` | Medium |
| TCG-UI1-003 | Galaxy Test Module No Tests | `game/ui/screens/galaxy_test/` | Simple |
| TCG-UI1-004 | Formation Module Missing Core Tests | `game/ui/screens/formation/` | Simple |

### Major (94)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-002 | IControllable interface exceeds god clas | `game/ai/interfaces/controllabl` | Complex |
| ADR-SIM-002 | TYPE_CHECKING import from AI layer | `game/simulation/systems/battle` | Simple |
| ADR-SIM-003 | Ship class exceeds 500 lines (God Class) | `game/simulation/entities/ship.` | Complex |
| ADR-SIM-004 | BattleController exceeds 500 lines (God  | `game/simulation/battle_control` | Medium |
| ADR-STR-001 | Galaxy Class Exceeds Size Threshold (God | `game/strategy/data/galaxy.py:1` | Medium |
| ADR-STR-002 | ProductionEngine Exceeds Size Threshold  | `game/strategy/engine/productio` | Medium |
| ADR-UI2-001 | Direct Simulation Layer Import in ship_i | `game/ui/services/ship_io.py:16` | Medium |
| ADR-UI1-001 | TestLabScreen God Class | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-002 | FleetReportWindow God Class | `game/ui/screens/fleet_report_w` | Medium |
| ADR-UI1-003 | BuildQueueScreen Large Class | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-004 | StrategyScreen Large Class | `game/ui/screens/strategy_scree` | Medium |
| ADR-UI1-005 | Private Facade Access in Dialogs | `game/ui/screens/cargo_quick_di` | Simple |
| ADR-UI1-006 | Private Method Access in BattleUI | `game/ui/screens/battle_ui.py:9` | Simple |
| ADR-UI1-007 | StrategyInputHandler Excessive Scene Cou | `game/ui/screens/strategy_input` | Medium |
| CON-FND-001 | Inconsistent Logging Pattern - Direct lo | `game/ai/combat_utils.py:14` | Simple |
| CON-FND-002 | Mixed os.path.join and Path-style path c | `game/core/paths.py:53-99` | Medium |
| CON-FND-003 | Inconsistent Boolean Property Naming - i | `game/core/profiling.py:63-64` | Medium |
| CON-FND-004 | Inconsistent Return Type for Not-Found C | `game/core/json_utils.py:33-67` | Simple |
| CON-FND-005 | Inconsistent Singleton Reset Patterns | `game/core/singleton.py:84-97` | Simple |
| CON-SIM-001 | Mixed return conventions for "not found" | `game/simulation/systems/resour` | Medium |
| CON-SIM-002 | Inconsistent docstring format across mod | `Unknown` | Medium |
| CON-SIM-003 | Inconsistent use of is_ vs has_ boolean  | `game/simulation/components/com` | Simple |
| CON-SIM-004 | Parameter ordering inconsistency for shi | `game/simulation/combat/targeti` | Simple |
| CON-SIM-005 | Facade pattern inconsistently applied in | `game/simulation/entities/ship.` | Medium |
| CON-STR-002 | Mixed Engine Initialization Patterns | `game/strategy/engine/productio` | Medium |
| CON-STR-003 | Inconsistent Docstring Formats | `Unknown` | Complex |
| CON-STR-004 | Mixed Method Verb Prefixes for Similar O | `Unknown` | Simple |
| CON-STR-005 | Inconsistent Use of TYPE_CHECKING Patter | `game/strategy/data/pathfinding` | Simple |
| CON-UI2-001 | Inconsistent DI Pattern Between Services | `game/ui/services/` | Medium |
| CON-UI2-002 | Mixed Parameter Naming for Registry Inje | `game/ui/services/` | Simple |
| CON-UI2-003 | Singleton Classes Missing Type Hints on  | `game/ui/renderer/sprites.py:26` | Simple |
| CON-UI2-004 | Inconsistent Docstring Presence and Form | `Unknown` | Medium |
| CON-UI2-005 | Static Methods vs Instance Methods Incon | `game/ui/services/ship_io.py:41` | Medium |
| CON-UI1-001 | Inconsistent Class Naming Suffixes | `Unknown` | Medium |
| CON-UI1-002 | Inconsistent Method Naming for Update Op | `game/ui/panels/` | Medium |
| CON-UI1-005 | Inconsistent Event Handler Return Types | `game/ui/screens/` | Complex |
| CON-UI1-006 | Inconsistent Panel Cleanup Methods | `game/ui/panels/` | Medium |
| CON-UI1-010 | Duplicate ColumnManager Classes | `game/ui/screens/column_manager` | Medium |
| DUP-FND-001 | IControllable Protocol Duplicates IShip  | `game/ai/interfaces/controllabl` | Medium |
| DUP-FND-002 | ResearchTracker and ResearchControlPanel | `game/research/data/research_tr` | Simple |
| DUP-FND-003 | Distance Calculation Pattern Repetition  | `game/ai/controller.py:197-201` | Medium |
| UNK-01 | Ability Class Boilerplate Pattern | `Unknown` | Unknown |
| DUP-STR-001 | Duplicated Facility Component Iteration  | `Unknown` | Medium |
| DUP-STR-002 | Duplicated Command Handler Pattern | `Unknown` | Medium |
| DUP-STR-003 | Duplicated Resource Cost Calculation | `Unknown` | Simple |
| DUP-STR-004 | Duplicated Ability Lookup in Validators | `Unknown` | Simple |
| DUP-STR-005 | Duplicated Superweapon Ship Removal Patt | `Unknown` | Simple |
| DUP-UI2-001 | Tkinter Root Initialization Duplicated | `game/ui/services/ship_io.py:20` | Medium |
| DUP-UI2-002 | Registry Provider Lazy Resolution Patter | `game/ui/services/component_ser` | Medium |
| DUP-UI2-003 | Image Bounding Box + Scale Logic Duplica | `game/ui/utils.py:116-162` | Simple |
| DUP-UI1-002 | Virtual Scrolling List Pattern Repeated | `game/ui/screens/planet_list_wi` | Medium |
| DUP-UI1-003 | Filter Toggle Button Pattern Duplicated | `game/ui/screens/fleet_report_w` | Medium |
| DUP-UI1-004 | Placeholder Surface Creation | `game/ui/panels/build_queue_por` | Simple |
| DUP-UI1-005 | Sidebar Filter Section Building Pattern | `game/ui/screens/empire_build_q` | Medium |
| LEG-FND-001 | Unused Import - RegistryManager in resou | `game/core/resources.py:16` | Simple |
| LEG-FND-002 | Extensive getattr() Defensive Patterns S | `game/ai/combat_utils.py:63-181` | Complex |
| LEG-SIM-001 | Empty Factory Module (Dead Package) | `game/simulation/factories/__in` | Simple |
| LEG-SIM-002 | Incomplete Migration - StrategyBattleMod | `game/simulation/combat/battle_` | Medium |
| LEG-SIM-003 | Defensive getattr/hasattr Usage on Core  | `Unknown` | Medium |
| LEG-SIM-004 | Hasattr Checks for ability_instances on  | `Unknown` | Simple |
| LEG-UI2-001 | Global Registry Fallback Pattern in Ship | `game/ui/services/ship_factory.` | Medium |
| LEG-UI2-002 | Global Registry Fallback Pattern in Comp | `game/ui/services/component_ser` | Medium |
| LEG-UI1-001 | Legacy Single-Selection Fields in Empire | `game/ui/screens/empire_build_q` | Medium |
| LEG-UI1-002 | Backward Compatibility Property in TestL | `game/ui/screens/test_lab/scree` | Simple |
| LEG-UI1-003 | Legacy API Method in FleetReportWindow | `game/ui/screens/fleet_report_w` | Medium |
| TCG-FND-003 | CollisionSystem Missing Integration Test | `game/engine/collision.py` | Medium |
| TCG-FND-004 | TechTree.detect_cycles() Has Limited Cyc | `game/research/data/tech_tree.p` | Simple |
| TCG-FND-005 | AI FleeHehavior Has No Direct Tests | `game/ai/behaviors.py` | Simple |
| TCG-FND-006 | TargetEvaluator Rule Processing Missing  | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-007 | AIControllerFactory Missing Error Path T | `game/ai/ai_factory.py` | Simple |
| TCG-STR-005 | No Unit Tests for services/ship_stats_ca | `game/strategy/services/ship_st` | Simple |
| TCG-STR-006 | FleetCapabilityCalculator.can_build_type | `game/strategy/data/fleet_capab` | Simple |
| TCG-STR-007 | EmpireEconomyCalculator Missing Integrat | `game/strategy/engine/empire_ec` | Medium |
| TCG-STR-008 | ConflictResolutionEngine Battle Resoluti | `game/strategy/engine/conflict_` | Medium |
| TCG-STR-009 | GameSession Missing Order Queueing Tests | `game/strategy/engine/game_sess` | Simple |
| TCG-STR-010 | Pathfinding Edge Cases Not Covered | `game/strategy/data/pathfinding` | Medium |
| TCG-STR-011 | GameInitializer._setup_initial_scenario  | `game/strategy/engine/game_init` | Medium |
| TCG-STR-012 | SaveGameService Round-Trip Edge Cases | `game/strategy/systems/save_gam` | Medium |
| TCG-STR-013 | Fleet.merge_with() Tests Incomplete | `game/strategy/data/fleet.py:me` | Simple |
| TCG-STR-023 | No Tests for strategy/events/event_types | `game/strategy/events/event_typ` | Simple |
| TCG-UI2-002 | ShipIOAdapter Has No Dedicated Tests | `game/ui/services/ship_io_adapt` | Simple |
| TCG-UI2-003 | UIConfig Has No Tests | `game/ui/config.py` | Simple |
| TCG-UI2-004 | Camera Tests Missing Edge Cases for offs | `game/ui/renderer/camera.py` | Simple |
| TCG-UI2-005 | DesignLoaderAdapter Missing Error Path T | `game/ui/services/design_loader` | Simple |
| TCG-UI2-006 | BattleUIService Missing Tests for Edge C | `game/ui/services/battle_ui_ser` | Simple |
| TCG-UI2-007 | ValidationService Missing Boundary Value | `game/ui/services/validation_se` | Simple |
| TCG-UI1-005 | Panel Files Missing Tests | `game/ui/panels/` | Medium |
| TCG-UI1-006 | BattlePanel Classes Undertested | `game/ui/panels/battle_panels.p` | Simple |
| TCG-UI1-007 | Strategy Screen Complex Modules | `game/ui/screens/strategy_*.py` | Medium |
| TCG-UI1-008 | Workshop Data Components Untested | `game/ui/screens/workshop_*.py` | Medium |
| TCG-UI1-009 | Fleet Report Components Undertested | `game/ui/screens/fleet_*.py` | Simple |
| TCG-UI1-010 | Build Queue UI Complex Logic Untested | `game/ui/screens/build_queue_*.` | Simple |
| TCG-UI1-011 | Planet List Components | `game/ui/screens/planet_list_*.` | Simple |
| TCG-UI1-012 | Race Configuration Panels | `game/ui/panels/race_*.py` | Simple |

### Minor (114)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | protocols.py exceeds 500 lines | `game/core/protocols.py:1-547` | Simple |
| ADR-SIM-005 | Late import pattern for circular depende | `game/simulation/entities/ship.` | Complex |
| ADR-STR-003 | Circular Import Workaround in galaxy.py | `game/strategy/data/galaxy.py:3` | Simple |
| ADR-STR-004 | ShipInstance Cross-Layer Late Imports | `game/strategy/data/ship_instan` | Complex |
| ADR-STR-005 | ShipStatsCalculator Imports from Simulat | `game/strategy/services/ship_st` | Medium |
| ADR-UI2-002 | TYPE_CHECKING Import from Simulation in  | `game/ui/services/ship_factory.` | Medium |
| ADR-UI2-003 | TYPE_CHECKING Import from Simulation in  | `game/ui/services/battle_ui_ser` | N |
| ADR-UI1-008 | Deep Attribute Chains (Law of Demeter) | `game/ui/screens/test_lab/scree` | Simple |
| ADR-UI1-009 | Panel Accessing Internal Cache | `game/ui/screens/test_lab/valid` | Simple |
| ADR-UI1-010 | Nested Private Format Method Access | `game/ui/screens/race_setup_scr` | Simple |
| ADR-UI1-011 | Workshop Data Reloader Private Attribute | `game/ui/screens/workshop_data_` | Simple |
| ADR-UI1-012 | Strategy Event Router Accesses Scene Pri | `game/ui/screens/strategy_event` | Simple |
| CON-FND-006 | Inconsistent Method Verb Prefixes for Ac | `game/ai/interfaces/controllabl` | N |
| CON-FND-007 | Inconsistent Parameter Naming - node_id  | `game/research/data/tech_tree.p` | Simple |
| CON-FND-008 | Inconsistent Docstring Format - Args/Ret | `Unknown` | Simple |
| CON-FND-009 | Magic Numbers in Research UI - Layout Co | `game/research/ui/research_scen` | Simple |
| CON-FND-010 | Inconsistent Type Hints - Any vs Specifi | `game/engine/collision.py:50-54` | Medium |
| CON-FND-011 | Inconsistent __all__ Export Patterns | `game/core/singleton.py:22` | Simple |
| CON-FND-012 | Inconsistent Private Attribute Naming | `game/ai/interfaces/controllabl` | Simple |
| CON-SIM-006 | Inconsistent private member naming with  | `game/simulation/entities/ship.` | Medium |
| CON-SIM-007 | Logger initialization patterns vary | `game/simulation/components/mod` | Simple |
| CON-SIM-008 | Inconsistent exception handling patterns | `game/simulation/services/desig` | Medium |
| CON-SIM-009 | Ability class naming suffix inconsistenc | `game/simulation/components/abi` | Medium |
| CON-SIM-010 | Constants defined in multiple locations | `game/simulation/projectile.py:` | Simple |
| CON-SIM-011 | Method naming verb inconsistency for ret | `Unknown` | Simple |
| CON-SIM-012 | Inconsistent type hints for callable par | `game/simulation/managers/retre` | Simple |
| CON-SIM-013 | Inconsistent use of dataclasses vs regul | `game/simulation/managers/retre` | Simple |
| CON-SIM-017 | Duplicate code between ability recalcula | `game/simulation/components/abi` | Medium |
| CON-STR-006 | Inconsistent Parameter Naming for Regist | `game/strategy/validation/super` | Simple |
| CON-STR-007 | Inconsistent Boolean Property Naming | `game/strategy/data/fleet.py` | Simple |
| CON-STR-008 | Dual Implementation of Same Logic | `game/strategy/engine/harvestin` | Simple |
| CON-STR-009 | Inconsistent __init__.py Export Patterns | `game/strategy/__init__.py` | Simple |
| CON-STR-010 | Inconsistent Comment Style for Project R | `Unknown` | Simple |
| CON-STR-011 | Missing Type Hints on Return Types | `game/strategy/data/pathfinding` | Simple |
| CON-UI2-006 | Boolean Parameter Naming Inconsistency | `game/ui/services/battle_ui_ser` | N |
| CON-UI2-007 | Inconsistent Error Handling - Return vs  | `game/ui/services/ship_io.py` | Simple |
| CON-UI2-008 | Import Organization Inconsistency | `Unknown` | Simple |
| CON-UI2-009 | Magic Numbers in Rendering Code | `game/ui/renderer/game_renderer` | Simple |
| CON-UI2-010 | Inconsistent Use of Optional Type Annota | `Unknown` | Simple |
| CON-UI2-011 | Inconsistent Private Method Naming | `Unknown` | N |
| CON-UI2-012 | Module-Level Side Effects | `game/ui/services/ship_io.py:20` | Medium |
| CON-UI1-003 | Inconsistent Boolean Parameter Naming | `Unknown` | Simple |
| CON-UI1-004 | Mixed Callback Naming Patterns | `Unknown` | Simple |
| CON-UI1-007 | Inconsistent Exception Handling Patterns | `Unknown` | Simple |
| CON-UI1-008 | Missing Type Hints on Public Methods | `Unknown` | Medium |
| CON-UI1-009 | Inconsistent Docstring Presence | `Unknown` | Medium |
| CON-UI1-011 | Inconsistent Screenshot Handling Pattern | `Unknown` | Simple |
| CON-UI1-012 | Mixed Parameter Ordering Conventions | `Unknown` | Simple |
| CON-UI1-013 | Direct Asset Loading Bypassing Service P | `game/ui/panels/design_report_p` | Simple |
| CON-UI1-017 | Inconsistent Import Organization | `Unknown` | Simple |
| CON-UI1-018 | Screen Protocol Compliance Varies | `Unknown` | Medium |
| DUP-FND-004 | Singleton Clear/Reset Pattern | `game/core/registry.py:217-237` | N |
| DUP-FND-005 | to_dict/from_dict Serialization Pattern | `game/research/data/research_tr` | N |
| DUP-FND-006 | Flee Direction Calculation | `game/ai/behaviors.py:70-85` | Simple |
| DUP-FND-007 | Registry Provider get_* Methods Duplicat | `game/core/registry.py:319-330` | N |
| UNK-02 | Validation Rule _do_validate Guard Claus | `Unknown` | Unknown |
| UNK-03 | Data Extraction Pattern in __init__ Meth | `Unknown` | Unknown |
| UNK-04 | get_effective_stat Default Value Pattern | `Unknown` | Unknown |
| UNK-06 | Resource Cost Evaluation Logic Split | `Unknown` | Unknown |
| DUP-STR-006 | Duplicated to_dict/from_dict Serializati | `Unknown` | Complex |
| DUP-STR-007 | Duplicated "Fleet Not Found" Validation | `Unknown` | Simple |
| DUP-STR-008 | Duplicated Planet Lookup Pattern | `Unknown` | Simple |
| DUP-UI2-004 | Singleton Manager Boilerplate | `game/ui/assets/ship_theme_mana` | Simple |
| DUP-UI2-005 | Multiple Image Transform Scale Patterns | `Unknown` | N |
| DUP-UI2-006 | Clipboard Copy Implementation | `game/ui/services/screenshot_ma` | Simple |
| DUP-UI1-006 | Image Scaling with smoothscale | `game/ui/screens/empire_panel_w` | Simple |
| DUP-UI1-007 | Column Visibility Toggle Handling | `game/ui/screens/planet_list_wi` | Simple |
| DUP-UI1-008 | Screenshot Toast Display | `game/ui/screens/planet_list_wi` | Simple |
| LEG-FND-003 | Singleton Pattern Still Used Extensively | `game/core/singleton.py` | Complex |
| LEG-FND-004 | hasattr() Checks for Mock Detection in P | `game/ai/combat_utils.py:43-47` | Simple |
| LEG-FND-005 | Fallback Behavior Documented Extensively | `game/ai/__init__.py:34-52` | Medium |
| LEG-FND-006 | Commented Strategy Hints in Controller C | `game/ai/controller.py:346` | Simple |
| LEG-FND-007 | Potential Dead Parameters in navigate_to | `game/ai/controller.py:434` | Simple |
| LEG-SIM-005 | V1 Modifier Format Check Still Present | `game/simulation/components/mod` | Simple |
| LEG-SIM-006 | Projectile Type String Conversion Patter | `game/simulation/entities/proje` | Simple |
| LEG-SIM-007 | Legacy Comment References (PROJ-106 Lega | `game/simulation/systems/battle` | Simple |
| LEG-SIM-008 | Stale Docstring Reference to Legacy Beha | `game/simulation/systems/battle` | Simple |
| LEG-UI2-003 | Unused Protocol Import (IBattleUI) | `game/ui/services/battle_ui_ser` | Simple |
| LEG-UI2-004 | Unused Method get_ships_folder in ShipIO | `game/ui/services/ship_io_adapt` | Simple |
| LEG-UI2-005 | Global Registry Fallback in DesignLoader | `game/ui/services/design_loader` | Simple |
| LEG-UI2-006 | Defensive getattr Patterns for Missing A | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI2-007 | hasattr Checks for Potentially Missing A | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI1-004 | Comments Referencing "Legacy Dispatch" i | `game/ui/screens/strategy_input` | Simple |
| LEG-UI1-005 | Pass Statements in Stub Methods | `game/ui/screens/test_lab/ship_` | Simple |
| LEG-UI1-006 | Extensive hasattr() Checks for Optional  | `Unknown` | Complex |
| LEG-UI1-007 | Singleton Instance Access Pattern | `Unknown` | Complex |
| LEG-UI1-008 | Fallback Chains in Workshop Context | `game/ui/screens/workshop_conte` | Simple |
| LEG-UI1-009 | PROJ-40 Migration Comments Still Present | `game/ui/screens/fleet_report_f` | Simple |
| LEG-UI1-010 | getattr() Defensive Patterns | `game/ui/screens/empire_panel_w` | Medium |
| TCG-FND-008 | game/core/protocols.py ICamera Interface | `game/core/protocols.py` | Simple |
| TCG-FND-009 | hex_math.py Missing Tests for Large Coor | `game/core/hex_math.py` | Simple |
| TCG-FND-010 | ResearchService.estimate_turns_to_breakt | `game/research/systems/research` | Medium |
| TCG-FND-011 | SpatialGrid._get_cell() Not Tested with  | `game/engine/spatial.py` | Simple |
| TCG-FND-012 | ResearchTracker.spread_rp_evenly() Distr | `game/research/data/research_tr` | Simple |
| TCG-STR-014 | ResupplyEngine Partial Resupply Tests | `game/strategy/engine/resupply_` | Simple |
| TCG-STR-015 | RegionClassifier._classify_spiral Bounda | `game/strategy/generation/regio` | Simple |
| TCG-STR-016 | QuickstartBuilder.spawn_initial_complexe | `game/strategy/quickstart_build` | Simple |
| TCG-STR-017 | DesignMetadata.from_design_file with Mis | `game/strategy/data/design_meta` | Simple |
| TCG-STR-018 | ShipResourceManager Edge Cases | `game/strategy/data/ship_resour` | Simple |
| TCG-STR-019 | Planet Population Model Edge Cases | `game/strategy/data/planet.py:S` | Simple |
| TCG-STR-020 | FleetDTO Build Validation | `game/strategy/facade/dto/fleet` | Simple |
| TCG-UI2-008 | SpriteManager Test Skips Production Dire | `game/ui/renderer/sprites.py` | Medium |
| TCG-UI2-009 | InputMapper Missing Tests for Modifier C | `game/ui/services/input_mapper.` | Simple |
| TCG-UI2-010 | ShipThemeManager Tests Skip When Federat | `game/ui/assets/ship_theme_mana` | Medium |
| TCG-UI2-011 | ScreenshotManager capture() Region Clipp | `game/ui/services/screenshot_ma` | Simple |
| TCG-UI2-012 | colors.py WHITE and BLACK Constants Not  | `game/ui/colors.py` | Simple |
| TCG-UI1-013 | Event Log Window | `game/ui/screens/event_log_wind` | Simple |
| TCG-UI1-014 | Column Manager | `game/ui/screens/column_manager` | Simple |
| TCG-UI1-015 | Keybindings Scene | `game/ui/screens/keybindings_sc` | Simple |
| TCG-UI1-016 | Battle State Viewer | `game/ui/screens/battle_state_v` | Simple |
| TCG-UI1-017 | Setup Screen Components | `game/ui/screens/setup_*.py` | Simple |
| TCG-UI1-018 | Empire Panel Window | `game/ui/screens/empire_panel_w` | Simple |
| TCG-UI1-019 | Save Selection Window | `game/ui/screens/save_selection` | Simple |
| TCG-UI1-020 | Design Selector Window | `game/ui/screens/design_selecto` | Simple |

### Info (45)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-004 | Research module structure mixes layers i | `game/research/ui/` | Simple |
| ADR-SIM-006 | game/engine layer used by simulation | `Unknown` | Simple |
| ADR-SIM-007 | Component.py approaching god class thres | `game/simulation/components/com` | Simple |
| ADR-STR-006 | Well-Implemented Facade Pattern | `game/strategy/facade/strategy_` | N |
| ADR-STR-007 | Well-Implemented Battle Resolver Interfa | `game/strategy/interfaces/battl` | N |
| ADR-STR-008 | Intentional AI Layer Dependency | `game/strategy/adapters/simulat` | N |
| ADR-UI2-004 | Intentional Cross-Layer Orchestration in | `game/ui/orchestration/battle_o` | N |
| ADR-UI1-013 | Heavy Use of TYPE_CHECKING Imports | `Unknown` | N |
| ADR-UI1-014 | Lazy Imports Inside Functions | `Unknown` | N |
| CON-FND-013 | Optional vs Union[X, None] Usage | `game/core/protocols.py:24-31` | N |
| CON-FND-014 | Import Organization Generally Consistent | `Unknown` | N |
| CON-SIM-014 | Import organization varies slightly | `Unknown` | Simple |
| CON-SIM-015 | Some __init__.py files export different  | `game/simulation/__init__.py` | Simple |
| CON-SIM-016 | Two-stage aggregation pattern well-docum | `game/simulation/entities/abili` | Simple |
| CON-STR-012 | Magic Numbers in Pathfinding | `game/strategy/data/pathfinding` | Simple |
| CON-STR-013 | Legacy Adapter Pattern Documentation | `game/strategy/data/pathfinding` | Simple |
| CON-STR-014 | Event System Enums vs String Constants | `game/strategy/events/event_typ` | Simple |
| CON-UI2-013 | Color Constants Location | `game/ui/colors.py` | Simple |
| CON-UI2-014 | Protocol Inheritance Pattern | `game/ui/interfaces/battle_ui.p` | N |
| CON-UI1-014 | Singleton Usage Consistent | `Unknown` | N |
| CON-UI1-015 | Good Layer Separation in Newer Code | `Unknown` | N |
| CON-UI1-016 | Event Bus Pattern Usage | `game/ui/screens/builder/event_` | N |
| DUP-FND-008 | Angle Difference Calculation Imported wi | `game/ai/behaviors.py:67` | Simple |
| UNK-05 | No significant copy-paste drift detected | `Unknown` | Unknown |
| UNK-07 | Marker Ability Classes (Intentional) | `Unknown` | Unknown |
| UNK-08 | Battle Mode Handlers (Intentional Strate | `Unknown` | Unknown |
| DUP-STR-009 | Well-Consolidated Component Inspection | `game/strategy/services/compone` | N |
| DUP-UI2-007 | Consistent Service Adapter Pattern | `game/ui/services/` | N |
| DUP-UI1-009 | BaseGallery Abstract Class Already Conso | `game/ui/panels/base_gallery.py` | N |
| LEG-FND-008 | Well-Structured Research Module (Clean) | `game/research/` | N |
| LEG-SIM-009 | reset_component_caches() Function Appear | `game/simulation/components/com` | Simple |
| LEG-UI2-008 | Singleton Pattern Usage | `game/ui/renderer/sprites.py:7` | N |
| LEG-UI1-011 | Dual-Path Ship/DTO Support in BattlePane | `game/ui/panels/battle_panels.p` | Deferred |
| LEG-UI1-012 | Build Queue Fallback Mode | `game/ui/panels/build_queue_con` | None |
| TCG-FND-013 | Test Organization - AI Tests Scattered A | `tests/unit/ai/` | Simple |
| TCG-FND-014 | Research UI Tests Could Benefit from Vis | `tests/unit/research/test_resea` | Complex |
| TCG-STR-021 | Component Inspector Good Coverage | `game/strategy/services/compone` | N |
| TCG-STR-022 | Habitability Formula Comprehensive Tests | `game/strategy/formulas/habitab` | N |
| TCG-UI2-013 | BattleOrchestrator Tests Use Heavy Mocki | `game/ui/orchestration/battle_o` | Medium |
| TCG-UI2-014 | test_atlas_fallback_logic Is Empty | `tests/unit/ui/test_sprites.py` | Simple |
| TCG-UI2-015 | utils.py Tests Could Use Parameterizatio | `tests/unit/ui/test_utils.py` | Simple |
| TCG-UI1-021 | Test Quality - Bypass-Init Pattern Usage | `tests/unit/ui/screens/test_for` | Medium |
| TCG-UI1-022 | Test Quality - Mock Heavy Tests | `tests/unit/ui/screens/test_for` | Medium |
| TCG-UI1-023 | Test File Organization | `tests/unit/ui/` | Simple |
| TCG-UI1-024 | Missing Integration Tests | `tests/integration/ui/` | Complex |


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
| Total Findings | 268 |
| Critical | 15 |
| Major | 94 |
| Minor | 114 |
| Info | 45 |
| Agents Used | 23 |

---
*Report generated: 2026-02-13 10:03*
