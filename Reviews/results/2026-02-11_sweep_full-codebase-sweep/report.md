# Review Report: 2026-02-11_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-11
- **Type:** Sweep Review (automated parallel analysis)
- **Description:** full-codebase-sweep
- **Agents Used:** 23

## Executive Summary
- **Total Findings:** 397
- **Critical:** 44 | **Major:** 156 | **Minor:** 144 | **Info:** 53
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Pygame imported in game/core/input_mapper.py (Core Layer Violation)
**ID:** ADR-FND-001
**Agent:** Architecture Foundation
**Location:** `game/core/input_mapper.py:26,34-38,146-160,162-178,202`
**Effort:** Medium

**ID:** ADR-FND-001
**Location:** `game/core/input_mapper.py:26,34-38,146-160,162-178,202`
**Issue:** The core layer must have NO framework dependencies, but `input_mapper.py` imports `pygame` at the top level and uses `pygame.KMOD_CTRL`, `pygame.KMOD_SHIFT`, `pygame.KMOD_ALT`, `pygame.KEYDOWN`, and `pygame.K_*` constants throughout. This directly violates the "Core - NO dependencies on simulation, strategy, ui, or ai" rule and the "Pygame is UI-only" rule.
**Impact:** Any code importing `game.c...

---

### 2. CRITICAL: Pygame imported in game/core/screenshot_manager.py (Core Layer Violation)
**ID:** ADR-FND-002
**Agent:** Architecture Foundation
**Location:** `game/core/screenshot_manager.py:4,51,67-79,147,172-180,186`
**Effort:** Simple

**ID:** ADR-FND-002
**Location:** `game/core/screenshot_manager.py:4,51,67-79,147,172-180,186`
**Issue:** `ScreenshotManager` imports `pygame` at the top level and uses `pygame.display.get_surface()`, `pygame.image.save()`, `pygame.Surface()`, `pygame.Rect()`, and `pygame.error` throughout. This is a clear violation of the architecture rule that pygame is UI-only and that core has no framework dependencies.
**Impact:** The `ScreenshotManager` singleton cannot be instantiated without pygame. It a...

---

### 3. CRITICAL: Research scene imports from game.ui (Layer Violation)
**ID:** ADR-FND-003
**Agent:** Architecture Foundation
**Location:** `game/research/ui/research_scene.py:19`
**Effort:** Medium

**ID:** ADR-FND-003
**Location:** `game/research/ui/research_scene.py:19`
**Issue:** `ResearchTreeScene` imports `from game.ui.renderer.camera import Camera`. The architecture rules state that `game/research/` depends on core only, with NO simulation, NO strategy, NO ui dependencies. This is a direct violation of the layer boundary.
**Impact:** The research package cannot be used independently of the UI layer. This creates a circular-like dependency concern: research depends on UI, and UI presum...

---

### 4. CRITICAL: AIControllerFactory runtime imports from game.ai layer
**ID:** ADR-SIM-001
**Agent:** Architecture Simulation
**Location:** `game/simulation/factories/ai_factory.py:57-58`
**Effort:** Medium

**ID:** ADR-SIM-001
**Location:** `game/simulation/factories/ai_factory.py:57-58`
**Issue:** The `AIControllerFactory.create_for_ship()` method performs runtime imports of `from game.ai.controller import AIController` and `from game.ai.interfaces import ShipControllableAdapter`. The simulation layer's architectural rule is "depends on Core ONLY (NO strategy, NO ui, NO ai, NO pygame)". While the factory pattern was introduced specifically to isolate this cross-layer dependency (PROJ-43 Phase 8), ...

---

### 5. CRITICAL: persistence.py imports tkinter UI framework
**ID:** ADR-SIM-002
**Agent:** Architecture Simulation
**Location:** `game/simulation/systems/persistence.py:3-4,11-12,46,84`
**Effort:** Simple

**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/persistence.py:3-4,11-12,46,84`
**Issue:** `persistence.py` imports `tkinter` and `from tkinter import filedialog` at the module level. It creates a `tkinter.Tk()` root window at module-level initialization (line 11-12). The `ShipIO.save_ship()` and `ShipIO.load_ship()` methods use `filedialog.asksaveasfilename()` and `filedialog.askopenfilename()` to display native file dialogs. This is a direct UI framework dependency in the simulation...

---

### 6. CRITICAL: Pygame in Core Layer -- ScreenshotManager
**ID:** ADR-UI2-001
**Agent:** Architecture Ui Framework
**Location:** `game/core/screenshot_manager.py:4`
**Effort:** Medium

**ID:** ADR-UI2-001
**Location:** `game/core/screenshot_manager.py:4`
**Issue:** `import pygame` in the core layer violates the strict rule that `game/core/` has NO dependencies on UI frameworks. The `ScreenshotManager` class uses `pygame.display.get_surface()`, `pygame.Surface`, `pygame.Rect`, `pygame.image.save()`, and `pygame.error` throughout. This is a full pygame dependency embedded in the foundation layer.
**Impact:** The core layer cannot be used headlessly (e.g., for simulation-only tes...

---

### 7. CRITICAL: Pygame in Core Layer -- InputMapper
**ID:** ADR-UI2-002
**Agent:** Architecture Ui Framework
**Location:** `game/core/input_mapper.py:26`
**Effort:** Complex

**ID:** ADR-UI2-002
**Location:** `game/core/input_mapper.py:26`
**Issue:** `import pygame` in the core layer. `InputMapper` directly references `pygame.KMOD_CTRL`, `pygame.KMOD_SHIFT`, `pygame.KMOD_ALT`, `pygame.key.name()`, and other pygame constants. The entire keybinding system is tightly coupled to pygame event types.
**Impact:** The input mapping system cannot be tested or used without pygame. This prevents headless operation and makes the core layer depend on a specific rendering framewor...

---

### 8. CRITICAL: Test Lab UI Imports From test_framework and simulation_tests Packages
**ID:** ADR-UI1-001
**Agent:** Architecture Ui Screens
**Location:** `game/ui/screens/test_lab/screen.py:16-18`
**Effort:** Complex

**ID:** ADR-UI1-001
**Location:** `game/ui/screens/test_lab/screen.py:16-18`, `game/ui/screens/test_lab/test_executor.py:11-13`, `game/ui/screens/test_lab/data_extractor.py:13`, `game/ui/screens/test_lab/validation_manager.py:12,48`, `game/ui/screens/battle_screen.py:450`
**Issue:** Six files in the UI layer import directly from `test_framework` and `simulation_tests` packages, which are test infrastructure outside the `game/` package hierarchy entirely. These imports include:
- `from test_frame...

---

### 9. CRITICAL: Simulation Layer Imports tkinter GUI Framework
**ID:** ADR-UI1-002
**Agent:** Architecture Ui Screens
**Location:** `game/simulation/systems/persistence.py:3-4`
**Effort:** Medium

**ID:** ADR-UI1-002
**Location:** `game/simulation/systems/persistence.py:3-4`
**Issue:** The simulation layer's `ShipIO` class imports `tkinter` at the top level for file dialog functionality. This is a direct UI framework dependency in the simulation layer, which should have zero UI dependencies. The UI screens (`builder/main.py:44`, `workshop_data_loader.py:115`) import from this module, inheriting and propagating the violation.
**Impact:** Prevents headless operation of ship I/O; simulation ...

---

### 10. CRITICAL: Inconsistent Error Handling Strategy Between load_resources and load_resources_data
**ID:** CON-FND-009
**Agent:** Consistency Foundation
**Location:** `game/core/resources.py:55-98`
**Effort:** Simple

**ID:** CON-FND-009
**Location:** `game/core/resources.py:55-98` vs `game/core/resources.py:101-142`
**Issue:** `load_resources_data()` (the DI-friendly pure function) and `load_resources()` (the legacy wrapper) contain nearly identical code with duplicated error handling. Both independently call `_resolve_resource_path()`, `load_json_required()`, and handle the same exception types with the same fallback logic. However, `load_resources_data()` uses `copy.deepcopy()` on defaults and returned dat...

---


## Findings by Severity

### Critical (44)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Pygame imported in game/core/input_mappe | `game/core/input_mapper.py:26,3` | Medium |
| ADR-FND-002 | Pygame imported in game/core/screenshot_ | `game/core/screenshot_manager.p` | Simple |
| ADR-FND-003 | Research scene imports from game.ui (Lay | `game/research/ui/research_scen` | Medium |
| ADR-SIM-001 | AIControllerFactory runtime imports from | `game/simulation/factories/ai_f` | Medium |
| ADR-SIM-002 | persistence.py imports tkinter UI framew | `game/simulation/systems/persis` | Simple |
| ADR-UI2-001 | Pygame in Core Layer -- ScreenshotManage | `game/core/screenshot_manager.p` | Medium |
| ADR-UI2-002 | Pygame in Core Layer -- InputMapper | `game/core/input_mapper.py:26` | Complex |
| ADR-UI1-001 | Test Lab UI Imports From test_framework  | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-002 | Simulation Layer Imports tkinter GUI Fra | `game/simulation/systems/persis` | Medium |
| CON-FND-009 | Inconsistent Error Handling Strategy Bet | `game/core/resources.py:55-98` | Simple |
| CON-STR-011 | Facade `_find_fleet_by_id` Does O(n) Sca | `game/strategy/facade/strategy_` | Small |
| CON-UI2-001 | Inconsistent DI Pattern Across Services  | `game/ui/services/vehicle_class` | Medium |
| CON-UI1-001 | Duplicate Class Name `ModifierEditorPane | `game/ui/panels/builder_widgets` | Medium |
| CON-UI1-002 | Duplicate Class Name `ColumnManager` in  | `game/ui/screens/column_manager` | Medium |
| DUP-FND-001 | Duplicated Resource Loading Logic (`load | `game/core/resources.py:55-98` | Simple |
| UNK-01 | Physics formula duplication between Ship | `Unknown` | Unknown |
| UNK-10 | Two parallel ability aggregation systems | `Unknown` | Unknown |
| DUP-STR-001 | Mission Command Handlers are Copy-Paste  | `game/strategy/engine/superweap` | Simple |
| DUP-STR-002 | _calculate_maintenance_cost Duplicated A | `game/strategy/engine/maintenan` | Simple |
| DUP-UI2-001 | Portrait Loading Logic Duplicated in 5+  | `game/ui/assets/ship_theme_mana` | Medium |
| DUP-UI2-002 | Ship Image Scaling Pipeline Duplicated B | `game/ui/renderer/game_renderer` | Simple |
| DUP-UI1-001 | BuildQueueScreen instantiation duplicate | `game/ui/screens/strategy_scree` | Simple |
| DUP-UI1-002 | Two separate ColumnManager classes with  | `game/ui/screens/column_manager` | Medium |
| LEG-FND-001 | Backward Compatibility Wrapper `load_res | `game/core/resources.py:101-143` | Medium |
| LEG-SIM-001 | Empty ABILITY_CLASS_MAP dict still impor | `game/simulation/components/abi` | Simple |
| LEG-SIM-007 | resource_manager.py re-exports ability c | `game/simulation/systems/resour` | Medium |
| LEG-SIM-008 | component.py uses get_default_registry_p | `game/simulation/components/com` | Medium |
| LEG-UI2-001 | Legacy widgets.py Module - Entire File i | `game/ui/widgets.py:1-102` | Simple |
| LEG-UI1-001 | Legacy BuilderScreen (builder/main.py) - | `game/ui/screens/builder/main.p` | Medium |
| TCG-FND-001 | PhysicsBody.apply_force() and forward_ve | `game/engine/physics.py` | Simple |
| TCG-FND-002 | AIController.update() Integration Path N | `game/ai/controller.py` | Medium |
| TCG-FND-003 | CollisionSystem.process_beam_attack() Hi | `game/engine/collision.py` | Medium |
| TCG-SIM-001 | BattleService has no unit tests | `game/simulation/services/battl` | Medium |
| TCG-SIM-002 | ProjectileManager has no unit tests | `game/simulation/projectile_man` | Complex |
| TCG-SIM-003 | AbilityAggregator has no unit tests | `game/simulation/entities/abili` | Medium |
| TCG-SIM-004 | ShipPhysicsMixin has no unit tests | `game/simulation/entities/ship_` | Medium |
| TCG-SIM-005 | ShipFormation has no unit tests | `game/simulation/entities/ship_` | Simple |
| TCG-STR-001 | planet_gen.py Has No Dedicated Unit Test | `game/strategy/data/planet_gen.` | Complex |
| TCG-STR-002 | FleetOrderProcessor Transfer Logic Has T | `game/strategy/engine/fleet_ord` | Medium |
| TCG-STR-003 | GameSession.handle_command() Dispatch Ha | `game/strategy/engine/game_sess` | Medium |
| TCG-UI1-001 | Entire builder/ subpackage has zero test | `game/ui/screens/builder/` | Medium |
| TCG-UI1-002 | Entire test_lab/ subpackage has zero tes | `game/ui/screens/test_lab/` | Medium |
| TCG-UI1-003 | Entire formation/ subpackage has zero te | `game/ui/screens/formation/` | Simple |
| TCG-UI1-004 | BattleScreen and BattleUI have zero unit | `game/ui/screens/battle_screen.` | Medium |

### Major (156)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-004 | Core protocols.py TYPE_CHECKING import f | `game/core/protocols.py:42` | Simple |
| ADR-FND-005 | AI controllable.py TYPE_CHECKING import  | `game/ai/interfaces/controllabl` | Simple |
| ADR-FND-006 | Research UI files use pygame directly (M | `game/research/ui/research_cont` | Medium |
| ADR-FND-007 | AIController deep attribute chain (Law o | `game/ai/controller.py:410` | Simple |
| ADR-SIM-003 | battle_config.py TYPE_CHECKING import fr | `game/simulation/battle_config.` | Simple |
| ADR-SIM-004 | battle_engine.py TYPE_CHECKING import fr | `game/simulation/systems/battle` | Simple |
| ADR-SIM-005 | God class - battle_controller.py (848 li | `game/simulation/battle_control` | Large |
| ADR-SIM-006 | God class - ship.py (809 lines) | `game/simulation/entities/ship.` | Large |
| ADR-SIM-007 | God class - component.py (719 lines) | `game/simulation/components/com` | Medium |
| ADR-STR-003 | ProductionEngine God Class (701 lines, 1 | `game/strategy/engine/productio` | Complex |
| ADR-STR-004 | Galaxy God Class (698 lines, 26 methods) | `game/strategy/data/galaxy.py:9` | Complex |
| ADR-STR-005 | ShipInstance God Class (658 lines, 44 me | `game/strategy/data/ship_instan` | Medium |
| ADR-STR-006 | Fleet God Class (353 lines, 41 methods) | `game/strategy/data/fleet.py:69` | Medium |
| ADR-STR-008 | ShipDisplayFormatter in Strategy Data La | `game/strategy/data/ship_displa` | Medium |
| ADR-STR-011 | hex_to_pixel/pixel_to_hex Usage in Galax | `game/strategy/data/galaxy.py:5` | Simple |
| ADR-UI2-003 | Renderer Directly Accesses Simulation Do | `game/ui/renderer/game_renderer` | Medium |
| ADR-UI2-004 | ShipFactory Uses pygame.math.Vector2 Ins | `game/ui/services/ship_factory.` | Simple |
| ADR-UI2-005 | DesignLoaderAdapter Has Hard Runtime Imp | `game/ui/services/design_loader` | Simple |
| ADR-UI2-006 | Pygame TYPE_CHECKING Import in AI Layer | `game/ai/interfaces/controllabl` | Simple |
| ADR-UI1-003 | TestLabScreen God Class (1877 lines, 75  | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-004 | BuilderScreen God Class (1042 lines, 44  | `game/ui/screens/builder/main.p` | Medium |
| ADR-UI1-005 | FormationEditorScreen God Class (701 lin | `game/ui/screens/formation_edit` | Medium |
| ADR-UI1-006 | StrategyScreen God Class (768 lines, 45  | `game/ui/screens/strategy_scree` | Complex |
| ADR-UI1-007 | Extensive Private Attribute Access Acros | `game/ui/screens/strategy_event` | Medium |
| ADR-UI1-008 | UI Layer Mutates Strategy Data Objects W | `game/ui/screens/planet_list_fi` | Medium |
| ADR-UI1-009 | BattleScreen God Class (621 lines, 32 me | `game/ui/screens/battle_screen.` | Medium |
| ADR-UI1-010 | FleetReportWindow God Class (1075 lines, | `game/ui/screens/fleet_report_w` | Medium |
| ADR-UI1-011 | BuildQueueScreen God Class (1057 lines,  | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-012 | EmpireBuildQueueWindow God Class (791 li | `game/ui/screens/empire_build_q` | Medium |
| CON-FND-001 | Mixed Singleton Patterns Across Core Lay | `game/core/strategy_metadata.py` | Simple |
| CON-FND-002 | Inconsistent Logging Approach Between ga | `game/ai/combat_utils.py:19` | Medium |
| CON-FND-010 | __init__.py Export Inconsistency Across  | `game/core/__init__.py` | Simple |
| CON-FND-011 | Unused json Import in registry.py | `game/core/registry.py:45` | Simple |
| CON-FND-014 | Mixed Return Conventions for "Not Found" | `Unknown` | Medium |
| CON-FND-015 | StrategyManager Methods Lack Type Hints | `game/ai/strategy_manager.py:83` | Simple |
| CON-FND-017 | StrategyMetadataService Uses Manual Sing | `game/core/strategy_metadata.py` | Simple |
| CON-STR-001 | Duplicate `to_roman` Implementation | `game/strategy/data/naming.py:5` | Small |
| CON-STR-002 | Inconsistent Entity Lookup Verb Prefixes | `game/strategy/facade/strategy_` | Small |
| CON-STR-006 | Duplicated `_calculate_maintenance_cost` | `game/strategy/engine/maintenan` | Small |
| CON-STR-007 | Duplicated `_get_harvester_info` / `_loo | `game/strategy/engine/harvestin` | Small |
| CON-STR-008 | Duplicated `_find_system_at_location` O( | `game/strategy/engine/superweap` | Small |
| CON-STR-012 | Inconsistent `__eq__` Return Value Conve | `game/strategy/data/fleet.py:41` | Small |
| CON-STR-013 | Missing Type Hints on Public Methods | `game/strategy/data/fleet.py` | Medium |
| CON-STR-016 | `SectorEnvironment` Class Missing Type H | `game/strategy/data/physics.py:` | Small |
| CON-UI2-002 | Complete Absence of Type Hints in render | `game/ui/renderer/camera.py:all` | Medium |
| CON-UI2-003 | Complete Absence of Type Hints in widget | `game/ui/widgets.py:1-102` | Simple |
| CON-UI2-004 | Singleton Pattern Used in renderer/ and  | `game/ui/renderer/sprites.py:7` | Complex |
| CON-UI2-005 | Missing Docstrings on Public Methods in  | `game/ui/renderer/sprites.py:27` | Medium |
| CON-UI2-006 | Inconsistent Error Handling - traceback  | `game/ui/renderer/sprites.py:11` | Simple |
| CON-UI1-003 | Mixed Event Handling Method Names (`hand | `Unknown` | Complex |
| CON-UI1-004 | Mixed `draw()` Parameter Naming (`screen | `Unknown` | Simple |
| CON-UI1-005 | Mixed `update()` Parameter Naming (`dt`  | `Unknown` | Simple |
| CON-UI1-006 | Two Logging Systems Used in Parallel | `game/ui/screens/builder/main.p` | Simple |
| CON-UI1-007 | UIWindow Base Class Import Inconsistency | `Unknown` | Simple |
| CON-UI1-008 | Confusing Sibling File Names `strategy_d | `game/ui/screens/strategy_detai` | Simple |
| CON-UI1-009 | Mixed Class Suffix Convention for Strate | `game/ui/screens/strategy_colon` | Simple |
| DUP-FND-002 | StrategyMetadataService Uses Hand-Rolled | `game/core/strategy_metadata.py` | Simple |
| DUP-FND-003 | Repeated "Flee Away" Vector Pattern Acro | `game/ai/behaviors.py:95-101` | Simple |
| DUP-FND-004 | Repeated Entity ID Fallback Pattern in A | `game/ai/combat_utils.py:65` | Simple |
| DUP-FND-005 | Inline Angle Difference Calculation Inst | `game/ai/controller.py:462` | Simple |
| UNK-02 | Hull auto-equip code duplicated between  | `Unknown` | Unknown |
| UNK-03 | Modifier application duplicated between  | `Unknown` | Unknown |
| UNK-04 | Superweapon ability classes are nearly i | `Unknown` | Unknown |
| UNK-05 | Turret arc lookup logic duplicated in Mo | `Unknown` | Unknown |
| UNK-06 | BeamWeaponAbility.get_damage() duplicate | `Unknown` | Unknown |
| UNK-11 | Two independent formula evaluation syste | `Unknown` | Unknown |
| UNK-12 | Duplicate default stats dictionaries | `Unknown` | Unknown |
| UNK-14 | WeaponAbility.__init__ formula parsing r | `Unknown` | Unknown |
| UNK-15 | Missile type checking uses inconsistent  | `Unknown` | Unknown |
| UNK-18 | Ship stat recalculation scattered across | `Unknown` | Unknown |
| UNK-19 | Component data loading spread across 4 f | `Unknown` | Unknown |
| DUP-STR-003 | _find_system_at_location Duplicated in V | `game/strategy/validation/super` | Simple |
| DUP-STR-004 | _get_harvester_info / _lookup_harvester_ | `game/strategy/engine/harvestin` | Simple |
| DUP-STR-005 | _get_storage_info / _lookup_storage_in_r | `game/strategy/engine/harvestin` | Medium |
| DUP-STR-006 | _spawn_complex Duplicated Between Colony | `game/strategy/engine/productio` | Simple |
| DUP-UI2-003 | Layer Color Constants Duplicated with Dr | `game/ui/renderer/game_renderer` | Simple |
| DUP-UI2-004 | BattleUIService get_engine() Null-Check  | `game/ui/services/battle_ui_ser` | Simple |
| DUP-UI2-005 | ShipThemeManager Internal Methods Repeat | `game/ui/assets/ship_theme_mana` | Simple |
| DUP-UI1-003 | Screenshot capture and toast notificatio | `game/ui/screens/build_queue_sc` | Simple |
| DUP-UI1-004 | Resource display formatting duplicated b | `game/ui/screens/strategy_ui.py` | Simple |
| DUP-UI1-005 | Star system/star formatting duplicated b | `game/ui/screens/strategy_detai` | Simple |
| DUP-UI1-006 | Event log window open methods duplicated | `game/ui/screens/strategy_windo` | Simple |
| LEG-FND-002 | StrategyMetadataService Uses Hand-Rolled | `game/core/strategy_metadata.py` | Simple |
| LEG-FND-003 | Dead Instance Attributes `attack_state`  | `game/ai/controller.py:90-91` | Simple |
| LEG-FND-004 | Duplicate Path Resolution Logic in resou | `game/core/resources.py:31-52` | Simple |
| LEG-FND-005 | Unused Protocol Classes and TypeGuard Fu | `game/core/protocols.py:85-110,` | Simple |
| LEG-SIM-002 | ability_aggregator dict-format branch is | `game/simulation/entities/abili` | Simple |
| LEG-SIM-003 | persistence.py ShipIO calls Ship.from_di | `game/simulation/systems/persis` | Medium |
| LEG-SIM-004 | persistence.py imports tkinter (UI depen | `game/simulation/systems/persis` | Medium |
| LEG-SIM-005 | designs.py hardcoded ship factories only | `game/simulation/designs.py:11-` | Medium |
| LEG-SIM-009 | String-based missile type checking is a  | `game/simulation/entities/proje` | Simple |
| LEG-SIM-010 | Multiple hasattr/getattr checks for alwa | `Unknown` | Simple |
| LEG-SIM-013 | ResourceDependencyRule has dual-path val | `game/simulation/validation/shi` | Simple |
| LEG-SIM-014 | WeaponAbility.recalculate() uses hasattr | `game/simulation/components/abi` | Simple |
| LEG-SIM-019 | _apply_results_to_fleet is a complete st | `game/simulation/battle_control` | Complex |
| LEG-SIM-020 | is_v2_format() implies V1 format still e | `game/simulation/components/mod` | Simple |
| LEG-UI2-002 | SpriteManager Atlas Fallback - Dead Code | `game/ui/renderer/sprites.py:40` | Simple |
| LEG-UI2-003 | draw_hud() and draw_bar() in game_render | `game/ui/renderer/game_renderer` | Simple |
| LEG-UI2-004 | BattleOrchestrator Never Used in Product | `game/ui/orchestration/battle_o` | Medium |
| LEG-UI2-005 | show_overlay Hack - State Passed via Dyn | `game/ui/renderer/game_renderer` | Simple |
| LEG-UI2-006 | draw_ship() Uses Singleton ShipThemeMana | `game/ui/renderer/game_renderer` | Medium |
| LEG-UI1-002 | Backward Compatibility Aliases in Race G | `game/ui/panels/race_flag_galle` | Simple |
| LEG-UI1-003 | Deprecated Methods on BattleScreen (hand | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-004 | Legacy Tuple Format Support in detail_pa | `game/ui/screens/builder/detail` | Medium |
| LEG-UI1-005 | Backwards Compatibility Fallbacks in wor | `game/ui/screens/workshop_event` | Simple |
| LEG-UI1-006 | Legacy Shim Skip List in detail_panel.py | `game/ui/screens/builder/detail` | Simple |
| TCG-FND-004 | SpatialGrid.query_radius() Boundary and  | `game/engine/spatial.py` | Simple |
| TCG-FND-005 | AIController._handle_formation_master()  | `game/ai/controller.py` | Medium |
| TCG-FND-006 | AIController._check_formation_integrity( | `game/ai/controller.py` | Simple |
| TCG-FND-007 | AIController.check_avoidance() Collision | `game/ai/controller.py` | Medium |
| TCG-FND-008 | AIController.navigate_to() Core Navigati | `game/ai/controller.py` | Simple |
| TCG-FND-009 | ResearchService.process_turn() Leaky Buc | `game/research/systems/research` | Simple |
| TCG-FND-010 | TechNode.get_effective_price() Only Part | `game/research/data/tech_node.p` | Simple |
| TCG-FND-011 | ResearchRenderer Test Coverage is Minima | `game/research/ui/research_rend` | Simple |
| TCG-FND-012 | ResearchControlPanel.handle_event() Lack | `game/research/ui/research_cont` | Medium |
| TCG-FND-024 | No Integration Test for AI Controller +  | `tests/integration/ai_strategy/` | Medium |
| TCG-SIM-006 | ShipSerializer has no dedicated unit tes | `game/simulation/entities/ship_` | Medium |
| TCG-SIM-007 | VehicleDesignService has no unit tests | `game/simulation/services/vehic` | Medium |
| TCG-SIM-008 | ModifierService has no unit tests | `game/simulation/services/modif` | Medium |
| TCG-SIM-009 | CombatEndurance calculations have no uni | `game/simulation/entities/comba` | Simple |
| TCG-SIM-010 | ShipStatQuerier has no unit tests | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-011 | ShipLoader functions have no dedicated u | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-012 | DamageCalculator _damage_layer weighted  | `game/simulation/combat/damage_` | Simple |
| TCG-SIM-013 | BattleState serialization round-trip not | `game/simulation/battle_state.p` | Medium |
| TCG-SIM-024 | No tests for BattleEngine.update tick pr | `game/simulation/systems/battle` | Complex |
| TCG-SIM-025 | No boundary tests for physics formula ca | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-026 | No tests for resource consumption during | `game/simulation/components/abi` | Medium |
| TCG-SIM-027 | ShipCombatEngine combat cooldowns only p | `game/simulation/entities/ship_` | Simple |
| TCG-STR-004 | FleetBattleAdapter Has Minimal Test Cove | `game/strategy/data/fleet_battl` | Medium |
| TCG-STR-005 | FleetResourceAggregator Lacks Atomic Ope | `game/strategy/data/fleet_resou` | Medium |
| TCG-STR-006 | QuickstartBuilder.spawn_initial_complexe | `game/strategy/quickstart_build` | Medium |
| TCG-STR-007 | Superweapon Command Handlers Missing Err | `game/strategy/engine/superweap` | Medium |
| TCG-STR-008 | DesignMetadata.from_design_file() and fr | `game/strategy/data/design_meta` | Medium |
| TCG-STR-009 | ColonizeValidator Chain Validation Not T | `game/strategy/validation/colon` | Simple |
| TCG-STR-010 | EmpireEconomyCalculator Registry Fallbac | `game/strategy/engine/empire_ec` | Simple |
| TCG-STR-011 | TurnEngine._process_tick() Integration N | `game/strategy/engine/turn_engi` | Medium |
| TCG-STR-012 | FleetCapabilityCalculator.can_build_type | `game/strategy/data/fleet_capab` | Simple |
| TCG-STR-013 | ShipResourceManager Missing Boundary Tes | `game/strategy/data/ship_resour` | Simple |
| TCG-UI2-001 | ShipThemeManager.get_portrait_image() an | `game/ui/assets/ship_theme_mana` | Simple |
| TCG-UI2-002 | Slider Widget Tests Have Weak Assertions | `tests/unit/ui/test_ui_widgets.` | Simple |
| TCG-UI2-003 | test_no_duplicate_color_values Is a No-O | `tests/unit/ui/test_colors.py` | Simple |
| TCG-UI2-004 | Camera.update_input() Has No Direct Unit | `game/ui/renderer/camera.py` | Medium |
| TCG-UI2-005 | game_renderer.py draw_ship() Overlay Mod | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI2-006 | ShipFactory.setup_formation() Does Not T | `game/ui/services/ship_factory.` | Simple |
| TCG-UI2-007 | Widgets Button.draw() and Slider.draw()  | `game/ui/widgets.py` | Medium |
| TCG-UI1-005 | battle_state_viewer.py has zero tests (6 | `game/ui/screens/battle_state_v` | Simple |
| TCG-UI1-006 | galaxy_test/ subpackage has zero test co | `game/ui/screens/galaxy_test/` | Medium |
| TCG-UI1-007 | WorkshopViewModel has no direct tests (5 | `game/ui/screens/workshop_viewm` | Medium |
| TCG-UI1-008 | FleetReportFilters and FleetReportViewMo | `game/ui/screens/fleet_report_f` | Simple |
| TCG-UI1-009 | ColumnManager has no tests (233 lines, p | `game/ui/screens/column_manager` | Simple |
| TCG-UI1-010 | setup_data_io.py has no tests (233 lines | `game/ui/screens/setup_data_io.` | Medium |
| TCG-UI1-011 | WorkshopShipIO has no tests (261 lines) | `game/ui/screens/workshop_ship_` | Medium |
| TCG-UI1-012 | 16 panel files have no tests | `game/ui/panels/` | Complex |
| TCG-UI1-013 | WorkshopEventRouter has no tests (496 li | `game/ui/screens/workshop_event` | Medium |
| TCG-UI1-014 | WorkshopDataLoader and WorkshopDataReloa | `game/ui/screens/workshop_data_` | Simple |
| TCG-UI1-015 | StrategyEventRouter, StrategyPanelManage | `game/ui/screens/strategy_event` | Medium |

### Minor (144)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-008 | UIConfig class in game/core/config.py co | `game/core/config.py:132-198` | Simple |
| ADR-FND-009 | ScreenshotManager.capture_strategy_layer | `game/core/screenshot_manager.p` | Simple |
| ADR-FND-010 | Engine collision.py TYPE_CHECKING import | `game/engine/collision.py:55` | Simple |
| ADR-FND-011 | Constants file mixes UI concerns (colors | `game/core/constants.py:42-49` | Simple |
| ADR-SIM-008 | UI data flow - screen dimensions in simu | `game/simulation/services/desig` | Simple |
| ADR-SIM-009 | Visual properties embedded in simulation | `game/simulation/entities/proje` | Medium |
| ADR-SIM-010 | Pervasive color_hint in ability display_ | `game/simulation/components/abi` | Large |
| ADR-SIM-011 | Circular dependency workarounds via late | `game/simulation/entities/ship.` | Large |
| ADR-SIM-012 | modifier_introspection.py contains UI-sp | `game/simulation/components/mod` | Simple |
| ADR-STR-001 | Pervasive Lazy Imports to Avoid Circular | `Unknown` | Complex |
| ADR-STR-002 | Galaxy Circular Dependency with Placemen | `game/strategy/data/galaxy.py:3` | Medium |
| ADR-STR-007 | FleetBattleAdapter Accesses Private Meth | `game/strategy/data/fleet_battl` | Simple |
| ADR-STR-009 | Color Tuples Embedded in Strategy Game C | `game/strategy/engine/game_conf` | Medium |
| ADR-STR-013 | EmpireEconomyCalculator Provides "Displa | `game/strategy/engine/empire_ec` | Simple |
| ADR-UI2-007 | ScreenshotManager Accesses Private _rend | `game/core/screenshot_manager.p` | Medium |
| ADR-UI2-008 | ValidationService Has Eager Runtime Impo | `game/ui/services/validation_se` | Simple |
| ADR-UI2-009 | game_renderer.py Uses Lazy Import Inside | `game/ui/renderer/game_renderer` | Simple |
| ADR-UI1-013 | UIConfig and DisplayConfig in Core Layer | `game/core/config.py:132-159` | Simple |
| ADR-UI1-014 | UI Color Constants (WHITE, BLACK, BLUE,  | `game/core/constants.py:42-49` | Simple |
| ADR-UI1-015 | Circular Import Avoidance via Late Impor | `game/ui/screens/column_manager` | Simple |
| ADR-UI1-016 | Module-Level tkinter Initialization Side | `game/ui/screens/formation_edit` | Simple |
| ADR-UI1-017 | Deep Attribute Chains Violating Law of D | `game/ui/screens/test_lab/scree` | Medium |
| ADR-UI1-018 | Circular Import Avoidance in new_game_se | `game/ui/screens/new_game_setup` | Simple |
| ADR-UI1-019 | TestLabScreen Directly Accesses battle_s | `game/ui/screens/test_lab/scree` | Simple |
| CON-FND-003 | Inconsistent os.path vs pathlib Usage in | `game/core/paths.py:50-103` | Medium |
| CON-FND-004 | Missing Type Hints on HexCoord Methods | `game/core/hex_math.py:75-119` | Simple |
| CON-FND-005 | Missing Type Hints on game/engine/ Class | `game/engine/spatial.py:6-35` | Simple |
| CON-FND-006 | Duplicate Enum Import in constants.py | `game/core/constants.py:1` | Simple |
| CON-FND-007 | Inconsistent Docstring Presence on game/ | `game/engine/spatial.py` | Simple |
| CON-FND-008 | ResourceType Uses Class Constants Instea | `game/core/constants.py:95-104` | Simple |
| CON-FND-012 | Missing Module Docstring in logger.py | `game/core/logger.py:1` | Simple |
| CON-FND-013 | Inconsistent Method Naming in Logger Cla | `game/core/logger.py:43-57` | Simple |
| CON-FND-016 | Inconsistent Naming Between is_alive Pro | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-022 | Inconsistent Use of import Inside Functi | `game/ai/behaviors.py:443,452` | Simple |
| CON-STR-003 | Inconsistent Logging Module Usage | `Unknown` | Medium |
| CON-STR-004 | Inconsistent Type Annotation Styles | `game/strategy/engine/empire_ec` | Small |
| CON-STR-009 | Inconsistent DI Patterns Across Engines | `Unknown` | Medium |
| CON-STR-010 | Inconsistent Delegate/Facade Naming | `game/strategy/data/` | Medium |
| CON-STR-014 | Inconsistent Validation Return Types | `game/strategy/validation/` | Medium |
| CON-STR-015 | Module-Level Functions vs Static Methods | `game/strategy/services/compone` | None |
| CON-STR-017 | Global Module-Level Cache Pattern (Poten | `game/strategy/data/homeworld_p` | Small |
| CON-STR-018 | Duplicate `import math` in `stars.py` | `game/strategy/data/stars.py` | Trivial |
| CON-STR-020 | `pathfinding.py` Contains Dead/Questiona | `game/strategy/data/pathfinding` | Small |
| CON-STR-021 | `build_queue_source.py` Contains Heavily | `game/strategy/data/build_queue` | Small |
| CON-STR-022 | `DesignLibrary` Uses Late Imports Inside | `game/strategy/systems/design_l` | Small |
| CON-UI2-007 | Hardcoded Magic Colors in renderer/game_ | `game/ui/renderer/game_renderer` | Medium |
| CON-UI2-008 | Hardcoded Font Creation in game_renderer | `game/ui/renderer/game_renderer` | Medium |
| CON-UI2-009 | game/ui/__init__.py Imports Screens but  | `game/ui/__init__.py:14-16` | Simple |
| CON-UI2-010 | Mixed Naming for Internal Provider Acces | `game/ui/services/component_ser` | Simple |
| CON-UI2-011 | Inconsistent Return Patterns for load_sh | `game/ui/services/ship_io_adapt` | Medium |
| CON-UI2-012 | Camera.fit_objects Sets zoom Directly, B | `game/ui/renderer/camera.py:153` | Simple |
| CON-UI2-013 | draw_ship Contains Inline Import of Ship | `game/ui/renderer/game_renderer` | Simple |
| CON-UI1-010 | Panel Classes Scattered Between `screens | `Unknown` | Complex |
| CON-UI1-011 | Missing Module-Level Docstrings in 18 Fi | `battle_ui.py` | Simple |
| CON-UI1-012 | `__init__.py` Export Patterns Inconsiste | `screens/__init__.py` | Simple |
| CON-UI1-013 | Scene vs Screen Class Naming Convention  | `MenuScene` | Simple |
| CON-UI1-014 | Function-Level Logger Imports in `design | `game/ui/screens/design_selecto` | Simple |
| CON-UI1-015 | `builder/main.py` Has Scattered Imports  | `game/ui/screens/builder/main.p` | Simple |
| CON-UI1-016 | Broad Exception Catch Without Justificat | `game/ui/panels/race_environmen` | Simple |
| DUP-FND-006 | `_resolve_resource_path` Reimplements Pr | `game/core/resources.py:31-52` | Simple |
| DUP-FND-007 | Repeated Zero-Vector Guard Pattern in AI | `game/ai/behaviors.py:97-98` | Simple |
| DUP-FND-008 | AIController._get_hp_percent and _is_in_ | `game/ai/controller.py:269-273` | Simple |
| DUP-FND-009 | `load_data` Duplication Between Strategy | `game/ai/strategy_manager.py:83` | Medium |
| UNK-07 | Ability constructor data-extraction patt | `Unknown` | Unknown |
| UNK-08 | Propulsion sync_data methods are near-id | `Unknown` | Unknown |
| UNK-09 | ShipValidatorHelper calls validate_desig | `Unknown` | Unknown |
| UNK-13 | get_total_sensor_score and get_total_ecm | `Unknown` | Unknown |
| UNK-16 | Resource endurance calculations in comba | `Unknown` | Unknown |
| UNK-17 | apply_modifier_effects partially duplica | `Unknown` | Unknown |
| UNK-20 | Validation result handling duplicated be | `Unknown` | Unknown |
| DUP-STR-007 | Direct Superweapon Command Handlers Foll | `game/strategy/engine/superweap` | Medium |
| DUP-STR-008 | Fleet Lookup Pattern Duplicated in Colon | `game/strategy/engine/command_h` | Simple |
| DUP-STR-009 | Superweapon Order Processing Has Repeate | `game/strategy/engine/superweap` | Simple |
| DUP-UI2-006 | Lazy DI Provider Pattern in Services | `game/ui/services/component_ser` | Simple |
| DUP-UI2-007 | Topdown Thumbnail Loading Reimplements B | `game/ui/screens/design_image_h` | Simple |
| DUP-UI1-007 | Thin wrapper/proxy methods in StrategyUI | `game/ui/screens/strategy_ui.py` | Simple |
| DUP-UI1-008 | Population count formatting (K/M suffixe | `game/ui/screens/strategy_detai` | Simple |
| DUP-UI1-009 | Window centering pattern repeated ~15 ti | `game/ui/screens/strategy_scree` | Simple |
| LEG-FND-006 | `LayerType.from_string()` Static Method  | `game/core/constants.py:117-119` | Simple |
| LEG-FND-007 | `ScreenshotManager.capture_step()` Never | `game/core/screenshot_manager.p` | Simple |
| LEG-FND-008 | Python 3.9 Compatibility Shim for TypeGu | `game/core/protocols.py:32-36` | Simple |
| LEG-FND-009 | Color Constants (WHITE, BLACK, BLUE, RED | `game/core/constants.py:42-46` | Simple |
| LEG-FND-010 | `json` Import in resources.py Only Neede | `game/core/resources.py:13` | Simple |
| LEG-FND-011 | `_get_hp_percent` and `_is_in_pdc_arc` W | `game/ai/controller.py:269-273` | Simple |
| LEG-FND-012 | `FONT_MAIN` Constant Defined but Unused  | `game/core/constants.py:49` | Simple |
| LEG-SIM-006 | FORMULA_* string constants are documenta | `game/simulation/physics_consta` | Simple |
| LEG-SIM-011 | shots_hit attribute dynamically added in | `game/simulation/projectile_man` | Simple |
| LEG-SIM-012 | combat_endurance.py legacy fallback for  | `game/simulation/entities/comba` | Simple |
| LEG-SIM-015 | CargoStorage uses string layer instead o | `game/simulation/components/abi` | Simple |
| LEG-SIM-016 | ability_manager.py has [KNOWN_ISSUE] wor | `game/simulation/components/abi` | Complex |
| LEG-SIM-017 | Ship.base_mass is always 0.0 - vestigial | `game/simulation/entities/ship.` | Simple |
| LEG-SIM-018 | Duplicate shield_regen_cost initializati | `game/simulation/entities/ship_` | Simple |
| LEG-UI2-007 | Unnecessary hasattr Guard on LayerType.v | `game/ui/services/battle_ui_ser` | Simple |
| LEG-UI2-008 | getattr(ship, 'id', id(ship)) - Ship.id  | `game/ui/services/battle_ui_ser` | Simple |
| LEG-UI2-009 | Excessive getattr Usage in _convert_proj | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI2-010 | interfaces/__init__.py Re-exports Never  | `game/ui/interfaces/__init__.py` | Simple |
| LEG-UI1-007 | Duplicate show_overlay Toggle Keybinding | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-008 | Stale Comment about Removed Duplicate Me | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-009 | Hardcoded 1920x1080 Fallback Resolution | `game/ui/screens/new_game_setup` | Simple |
| LEG-UI1-010 | Duplicate Assignment on Consecutive Line | `game/ui/screens/builder/left_p` | Simple |
| LEG-UI1-011 | Unnecessary hasattr Guard for _facade | `game/ui/screens/strategy_windo` | Simple |
| LEG-UI1-012 | Dead hasattr Check for print_headless_su | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-013 | Monkey-Patching Domain Objects with Temp | `game/ui/screens/strategy_rende` | Medium |
| LEG-UI1-014 | Unused Module-Level Constants | `game/ui/screens/builder/stats_` | Simple |
| TCG-FND-013 | StrategyManager.resolve_strategy() Defau | `game/ai/strategy_manager.py` | Simple |
| TCG-FND-014 | HexCoord Arithmetic with Non-HexCoord Ty | `game/core/hex_math.py` | Simple |
| TCG-FND-015 | pixel_to_hex() Rounding Edge Cases at Ce | `game/core/hex_math.py` | Simple |
| TCG-FND-016 | RegistryManager.hydrate() Partial Resour | `game/core/registry.py` | Simple |
| TCG-FND-017 | combat_utils.is_in_pdc_arc() Missing Tes | `game/ai/combat_utils.py` | Simple |
| TCG-FND-018 | TargetEvaluator._eval_speed_rule() Slowe | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-019 | ResearchTracker.spread_rp_evenly() Does  | `game/research/data/research_tr` | Simple |
| TCG-SIM-014 | Abilities base class (Ability) has no is | `game/simulation/components/abi` | Simple |
| TCG-SIM-015 | ColonizeAbility and HarvesterAbility hav | `game/simulation/components/abi` | Simple |
| TCG-SIM-016 | ModifierIntrospection has no unit tests | `game/simulation/components/mod` | Simple |
| TCG-SIM-017 | ComponentHealthManager has no unit tests | `game/simulation/components/com` | Simple |
| TCG-SIM-018 | ComponentResourceManager has no unit tes | `game/simulation/components/com` | Simple |
| TCG-SIM-019 | TechPresetLoader has no unit tests | `game/simulation/systems/tech_p` | Simple |
| TCG-SIM-020 | LayerData has no unit tests | `game/simulation/entities/layer` | Simple |
| TCG-STR-014 | ShipDisplayFormatter.get_resource_percen | `game/strategy/data/ship_displa` | Simple |
| TCG-STR-015 | ShipCargoManager.load_cargo() and unload | `game/strategy/data/ship_cargo_` | Simple |
| TCG-STR-016 | SuperweaponOrderProcessor._find_system_a | `game/strategy/engine/superweap` | Simple |
| TCG-STR-017 | EventTypes Enum and EventLog Serializati | `game/strategy/events/event_typ` | Simple |
| TCG-STR-018 | Facade DTO from_* Methods Missing Edge C | `game/strategy/facade/dto/` | Simple |
| TCG-STR-019 | RegionClassifier Has No Test for Ring/Ba | `game/strategy/generation/regio` | Simple |
| TCG-STR-020 | placement_strategies.py DensityBasedPlac | `game/strategy/generation/place` | Simple |
| TCG-STR-021 | GameConfig and PlayerConfig Missing Vali | `game/strategy/engine/game_conf` | Simple |
| TCG-UI2-008 | Camera.update() Target Following Does No | `game/ui/renderer/camera.py` | Simple |
| TCG-UI2-009 | ValidationService Does Not Test Thread S | `game/ui/services/validation_se` | Simple |
| TCG-UI2-010 | BattleUIService conftest mock_ship Uses  | `tests/unit/ui/services/battle_` | Simple |
| TCG-UI2-011 | Slider.handle_event() MOUSEBUTTONUP Retu | `game/ui/widgets.py` | Simple |
| TCG-UI2-012 | ShipIOAdapter Does Not Test save_ship Ca | `game/ui/services/ship_io_adapt` | Simple |
| TCG-UI2-013 | ComponentService.is_modifier_allowed() D | `game/ui/services/component_ser` | Simple |
| TCG-UI2-014 | DesignLoaderAdapter Does Not Test Defaul | `game/ui/services/design_loader` | Simple |
| TCG-UI2-015 | game_renderer.py draw_hud() Does Not Tes | `game/ui/renderer/game_renderer` | Simple |
| TCG-UI1-016 | planet_list_presets.py, planet_list_side | `game/ui/screens/planet_list_pr` | Simple |
| TCG-UI1-017 | builder_selection.py has no tests (110 l | `game/ui/screens/builder_select` | Simple |
| TCG-UI1-018 | build_queue_helpers.py has no tests (63  | `game/ui/screens/build_queue_he` | Simple |
| TCG-UI1-019 | save_selection_window.py has no tests (3 | `game/ui/screens/save_selection` | Medium |
| TCG-UI1-020 | new_game_setup_screen.py has no tests (6 | `game/ui/screens/new_game_setup` | Medium |
| TCG-UI1-021 | empire_panel_window.py has no tests (526 | `game/ui/screens/empire_panel_w` | Medium |
| TCG-UI1-022 | race_browser_dialog.py has no tests (290 | `game/ui/screens/race_browser_d` | Medium |
| TCG-UI1-023 | build_queue_list_window.py and build_que | `game/ui/screens/build_queue_li` | Simple |
| TCG-UI1-024 | race_asset_loader.py has no tests (276 l | `game/ui/screens/race_asset_loa` | Medium |
| TCG-UI1-025 | workshop_context.py has no tests (158 li | `game/ui/screens/workshop_conte` | Simple |

### Info (53)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-012 | Research package has clean data/systems  | `game/research/data/` | N |
| ADR-SIM-013 | battle_state.py is a large data containe | `game/simulation/battle_state.p` | N |
| ADR-SIM-014 | game.engine dependencies are architectur | `Unknown` | N |
| ADR-STR-010 | Misleading Docstring in ShipStatsCalcula | `game/strategy/services/ship_st` | Simple |
| ADR-STR-012 | DesignMetadata Contains sprite_preview F | `game/strategy/data/design_meta` | Simple |
| ADR-UI2-010 | Consistent Use of Facade/Adapter Pattern | `game/ui/services/` | N |
| ADR-UI1-020 | WeaponsReportPanel File Size (1037 lines | `game/ui/screens/builder/weapon` | Medium |
| ADR-UI1-021 | RaceSummaryPanel (671 lines, 25 methods) | `game/ui/panels/race_summary_pa` | Simple |
| ADR-UI1-022 | WorkshopViewModel (551 lines, 36 methods | `game/ui/screens/workshop_viewm` | Simple |
| ADR-UI1-023 | StrategyUI Thin Facade (357 lines, 38 me | `game/ui/screens/strategy_ui.py` | N |
| CON-FND-018 | Screenshot Manager Accesses Private Rend | `game/core/screenshot_manager.p` | Medium |
| CON-FND-019 | game/engine/ Is Internally Consistent Bu | `game/engine/spatial.py` | Simple |
| CON-FND-020 | game/research/ Has Clean Internal Consis | `game/research/` | N |
| CON-FND-021 | game/ai/ Has Mostly Good Internal Consis | `game/ai/` | Simple |
| CON-STR-005 | NameRegistry Class Style Inconsistencies | `game/strategy/data/naming.py` | Small |
| CON-STR-019 | Superweapon Mission Command Handlers Hav | `game/strategy/engine/superweap` | Small |
| CON-STR-023 | `event_log.py` Uses Python 3.10+ `X | Y` | `game/strategy/events/event_log` | Trivial |
| CON-UI2-014 | Service Class Naming Convention - "Servi | `game/ui/services/` | N |
| CON-UI2-015 | colors.py Has No Module Docstring and No | `game/ui/colors.py:1-35` | Simple |
| CON-UI2-016 | Inconsistent Docstring Style Between ren | `game/ui/renderer/camera.py:24-` | Simple |
| CON-UI1-017 | Return Type Annotations Present on Only  | `Unknown` | Complex |
| CON-UI1-018 | `from __future__ import annotations` Use | `Unknown` | Simple |
| DUP-FND-010 | Paths Class Maintains Both String and Pa | `game/core/paths.py:46-134` | Medium |
| UNK-21 | Persistence layer uses old Ship.from_dic | `Unknown` | Unknown |
| DUP-STR-010 | Design Data Layer Iteration Pattern Used | `Unknown` | Medium |
| DUP-UI2-008 | Hardcoded Magic Color Tuples Throughout  | `Unknown` | Medium |
| DUP-UI1-010 | StrategyDetailFormatter._format_star_sys | `game/ui/screens/strategy_detai` | N |
| LEG-FND-013 | `DEBUG_SCREENSHOTS = True` Always Enable | `game/core/constants.py:53` | Simple |
| LEG-FND-014 | `profiling.py` Comment References "backw | `game/core/profiling.py:104` | Simple |
| LEG-SIM-021 | ShipStatsCalculator._check_mass_limits h | `game/simulation/entities/ship_` | Simple |
| LEG-SIM-022 | TechPresetLoader has no production calle | `game/simulation/systems/tech_p` | Medium |
| LEG-SIM-023 | EmpireStorageAbility uses non-standard s | `game/simulation/components/abi` | Simple |
| LEG-UI2-011 | SpriteManager and ShipThemeManager Use S | `game/ui/renderer/sprites.py:7` | Complex |
| LEG-UI2-012 | game/ui/__init__.py Purpose is xdist Rac | `game/ui/__init__.py:1-27` | Simple |
| LEG-UI1-015 | Deprecated Properties on StrategyScreen  | `game/ui/screens/strategy_scree` | Simple |
| LEG-UI1-016 | test_lab/screen.py Accepts Game Object " | `game/ui/screens/test_lab/scree` | Medium |
| TCG-FND-020 | Collision Edge Case Tests Use Heavy Mock | `tests/unit/engine/collision_ed` | Complex |
| TCG-FND-021 | ScreenshotManager Tests Are Fragile Due  | `tests/unit/core/test_screensho` | Simple |
| TCG-FND-022 | StrategyMetadataService Uses Legacy Sing | `game/core/strategy_metadata.py` | Simple |
| TCG-FND-023 | ErraticBehavior Uses `import random` Ins | `game/ai/behaviors.py` | Simple |
| TCG-SIM-021 | Weapon ability classes tested primarily  | `game/simulation/components/abi` | Medium |
| TCG-SIM-022 | Defense ability classes tested primarily | `game/simulation/components/abi` | Simple |
| TCG-SIM-023 | ShipIO (persistence.py) inherently diffi | `game/simulation/systems/persis` | N |
| TCG-STR-022 | Test Organization -- Some Test Files in  | `Unknown` | Simple |
| TCG-STR-023 | Validation Module Has No __init__.py Tes | `tests/unit/strategy/validation` | Simple |
| TCG-STR-024 | Heavy Mock Usage in FleetOrderProcessor  | `tests/unit/strategy/test_fleet` | Medium |
| TCG-UI2-016 | test_atlas_fallback_logic Is Empty (Pass | `tests/unit/ui/test_sprites.py` | Simple |
| TCG-UI2-017 | Inconsistent Import Patterns in Service  | `Unknown` | Simple |
| TCG-UI2-018 | BattleUIService Integration Tests Are Co | `tests/unit/ui/services/battle_` | Simple |
| TCG-UI1-026 | Tests using inspect.getsource() verify s | `tests/unit/ui/screens/test_pla` | Medium |
| TCG-UI1-027 | Some tests use .called instead of .asser | `tests/unit/ui/screens/test_fle` | Simple |
| TCG-UI1-028 | Heavy mock usage in screen tests may mas | `Unknown` | Complex |
| TCG-UI1-029 | No tests for StrategyFleetOps or Strateg | `game/ui/screens/strategy_fleet` | Medium |


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
| Total Findings | 397 |
| Critical | 44 |
| Major | 156 |
| Minor | 144 |
| Info | 53 |
| Agents Used | 23 |

---
*Report generated: 2026-02-11 22:27*
