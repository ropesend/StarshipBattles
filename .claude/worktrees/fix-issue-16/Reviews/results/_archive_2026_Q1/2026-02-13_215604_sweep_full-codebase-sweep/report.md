# Review Report: 2026-02-13_215604_sweep_full-codebase-sweep

## Metadata
- **Date:** 2026-02-13
- **Type:** Review
- **Description:** 
- **Agents Used:** 23

## Executive Summary
- **Total Findings:** 297
- **Critical:** 19 | **Major:** 101 | **Minor:** 125 | **Info:** 52
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: AI Layer Dependency from Strategy Layer
**ID:** ADR-STR-001
**Agent:** Architecture Strategy
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Effort:** Medium

**ID:** ADR-STR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Issue:** The strategy layer directly imports from the AI layer (`from game.ai.ai_factory import AIControllerFactory`). According to the architecture rules, Strategy should depend only on Core and Simulation - NOT on AI.
**Impact:** The architecture diagram shows AI depends on Strategy, not the other way around. This creates a potential circular dependency risk and violates layer separation. The strategy layer s...

---

### 2. CRITICAL: Return Type Inconsistency in registry.py
**ID:** CON-FND-001
**Agent:** Consistency Foundation
**Location:** `game/core/registry.py:98-120`
**Effort:** Medium

**ID:** CON-FND-001
**Location:** `game/core/registry.py:98-120` vs `game/core/registry.py:383-397`
**Issue:** `get_default_registries()` raises `StateException` when not initialized, but `get_default_registry_provider()` silently creates an instance if None. This inconsistency in error handling for the same conceptual operation (getting default registry access) creates confusing API semantics.
**Impact:** Developers may expect consistent behavior between these two "get_default" functions. One r...

---

### 3. CRITICAL: Inconsistent Return Type Pattern for "Not Found" Scenarios
**ID:** CON-SIM-001
**Agent:** Consistency Simulation
**Location:** `game/simulation/systems/battle_engine.py:352-357`
**Effort:** Medium

**ID:** CON-SIM-001
**Location:** `game/simulation/systems/battle_engine.py:352-357`, `game/simulation/entities/ship.py` (various methods)
**Issue:** `get_ship_by_name()` returns `None` on not-found, but some component lookup methods in Ship raise exceptions while others return `None`. The `get_ability()` method returns `None` on not-found, but `from_dict()` raises exceptions on missing data.
**Impact:** Callers must remember different error handling patterns for similar lookup operations. This ...

---

### 4. CRITICAL: Mixed Parameter Naming for Ship References
**ID:** CON-SIM-002
**Agent:** Consistency Simulation
**Location:** `Unknown`
**Effort:** Medium

**ID:** CON-SIM-002
**Location:** Multiple files across `game/simulation/combat/`, `game/simulation/managers/`, `game/simulation/validation/`
**Issue:** Ship parameters use inconsistent naming: `ship` (dominant), `source_ship` (weapon_firing_system.py), `s` (battle_engine.py loops), `owner` (projectile.py). The `targeting_system.py` uses `ship` for shooter and `candidate`/`target` for targets, but `weapon_firing_system.py` uses `ship` and `target` inconsistently.
**Impact:** Makes it harder to u...

---

### 5. CRITICAL: Method Returns Inconsistent Types for Not-Found
**ID:** CON-STR-001
**Agent:** Consistency Strategy
**Location:** `game/strategy/data/pathfinding.py:26-105`
**Effort:** Simple

**ID:** CON-STR-001
**Location:** `game/strategy/data/pathfinding.py:26-105` vs `game/strategy/data/galaxy.py`
**Issue:** `find_path_interstellar()` returns `None` when no path exists, while most path/find methods throughout the codebase return empty lists. This mixed return type pattern can cause subtle bugs where callers check `if path:` expecting empty list behavior.
**Impact:** Code calling pathfinding functions must handle both `None` and empty list cases, increasing bug risk and cognitive ...

---

### 6. CRITICAL: Mixed DI Patterns - Some Services Require Provider, Others Optional
**ID:** CON-UI2-001
**Agent:** Consistency Ui Framework
**Location:** `game/ui/services/vehicle_class_service.py:36-47`
**Effort:** Medium

**ID:** CON-UI2-001
**Location:** `game/ui/services/vehicle_class_service.py:36-47`, `game/ui/services/component_service.py:31-50`, `game/ui/services/validation_service.py:33-46`
**Issue:** `VehicleClassService` requires `registry_provider` (raises `ValueError` if None) while `ComponentService` and `ValidationService` make it optional with lazy resolution. The docstring in `ComponentService` explicitly documents this inconsistency: "Services may choose strict required pattern (raises ValueError ...

---

### 7. CRITICAL: Inconsistent Return Types for Not-Found Cases
**ID:** CON-UI1-001
**Agent:** Consistency Ui Screens
**Location:** `Unknown`
**Effort:** Medium

**ID:** CON-UI1-001
**Location:** Multiple files in `game/ui/panels/` and `game/ui/screens/`
**Issue:** Methods for finding/getting items return inconsistent types when items are not found. Some return `None` (e.g., `get_hovered_component` in `left_panel.py:460`), others return `-1` (e.g., `get_clicked_planet_index` in `planet_list_renderer.py:182`), and some raise exceptions. This creates ambiguity in calling code about how to check for "not found" cases.
**Impact:** Potential runtime errors if...

---

### 8. CRITICAL: Design Layer Iteration Pattern Duplicated Across Multiple Engines
**ID:** DUP-STR-001
**Agent:** Duplication Strategy
**Location:** `game/strategy/engine/harvesting_engine.py:227-245`
**Effort:** Medium

**ID:** DUP-STR-001
**Location:** `game/strategy/engine/harvesting_engine.py:227-245` AND `game/strategy/engine/resupply_engine.py:139-156` AND `game/strategy/engine/maintenance_engine.py:44-68` AND `game/strategy/engine/production_engine.py:71-82` AND `game/strategy/data/build_queue_source.py:93-111`
**Issue:** The pattern of iterating through `design_data.get("layers", {}).values()` to scan components for abilities is repeated in 5+ locations with near-identical structure. Each location handle...

---

### 9. CRITICAL: Duplicate Transfer Dialog Implementations
**ID:** DUP-UI1-001
**Agent:** Duplication Ui Screens
**Location:** `Unknown`
**Effort:** Unknown

**ID:** DUP-UI1-001

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\transfer_dialog.py` (337 lines)
- `C:\Dev\Starship Battles\game\ui\screens\cargo_quick_dialog.py` (326 lines)

**Description:**
Two dialog classes implement nearly identical cargo/population transfer functionality with significant code overlap:

1. **Common patterns duplicated:**
   - Colony/planet lookup logic (`get_planets_at_hex`, filtering for `owner_id is not None`)
   - Passenger/population iteration logic (check...

---

### 10. CRITICAL: Repeated List Window Patterns Without Base Class
**ID:** DUP-UI1-002
**Agent:** Duplication Ui Screens
**Location:** `Unknown`
**Effort:** Unknown

**ID:** DUP-UI1-002

**Location:**
- `C:\Dev\Starship Battles\game\ui\screens\planet_list_window.py` (517 lines)
- `C:\Dev\Starship Battles\game\ui\screens\fleet_report_window.py` (1094 lines)
- `C:\Dev\Starship Battles\game\ui\screens\empire_build_queue_window.py` (864 lines)
- `C:\Dev\Starship Battles\game\ui\screens\design_selector_window.py` (552 lines)
- `C:\Dev\Starship Battles\game\ui\screens\save_selection_window.py` (396 lines)
- `C:\Dev\Starship Battles\game\ui\screens\event_log_window...

---


## Findings by Severity

### Critical (19)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-STR-001 | AI Layer Dependency from Strategy Layer | `game/strategy/adapters/simulat` | Medium |
| CON-FND-001 | Return Type Inconsistency in registry.py | `game/core/registry.py:98-120` | Medium |
| CON-SIM-001 | Inconsistent Return Type Pattern for "No | `game/simulation/systems/battle` | Medium |
| CON-SIM-002 | Mixed Parameter Naming for Ship Referenc | `Unknown` | Medium |
| CON-STR-001 | Method Returns Inconsistent Types for No | `game/strategy/data/pathfinding` | Simple |
| CON-UI2-001 | Mixed DI Patterns - Some Services Requir | `game/ui/services/vehicle_class` | Medium |
| CON-UI1-001 | Inconsistent Return Types for Not-Found  | `Unknown` | Medium |
| DUP-STR-001 | Design Layer Iteration Pattern Duplicate | `game/strategy/engine/harvestin` | Medium |
| DUP-UI1-001 | Duplicate Transfer Dialog Implementation | `Unknown` | Unknown |
| DUP-UI1-002 | Repeated List Window Patterns Without Ba | `Unknown` | Unknown |
| DUP-UI1-003 | RaceThemeGallery Does Not Extend BaseGal | `Unknown` | Unknown |
| TCG-FND-001 | `game/core/profiling.py` - Missing Unit  | `game/core/profiling.py` | Medium |
| TCG-FND-014 | `game/engine/collision.py` - Division by | `game/engine/collision.py` | Simple |
| UNK-06 | Damage Pipeline Armor Calculations Spars | `Unknown` | Unknown |
| TCG-UI2-001 | SystemTreePanel Has No Unit Tests | `game/ui/panels/system_tree_pan` | Complex |
| TCG-UI2-002 | BaseGallery Abstract Class Has No Tests | `game/ui/panels/base_gallery.py` | Medium |
| TCG-UI1-001 | BattleStateViewer Has No Tests | `game/ui/screens/battle_state_v` | Medium |
| TCG-UI1-002 | TestLab Submodules Completely Untested | `game/ui/screens/test_lab/*.py` | Complex |
| TCG-UI1-003 | Builder Submodule Interaction Controller | `game/ui/screens/builder/intera` | Medium |

### Major (101)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | game/research/ui/research_scene.py Late  | `game/research/ui/research_scen` | Simple |
| ADR-FND-002 | protocols.py Exceeds 500 Line Threshold  | `game/core/protocols.py` | Medium |
| ADR-FND-003 | behaviors.py Exceeds 500 Line Threshold  | `game/ai/behaviors.py` | Medium |
| UNK-01 | BattleEngine imports from game.engine (n | `Unknown` | Unknown |
| UNK-03 | Component class exceeds 500 LOC threshol | `Unknown` | Unknown |
| ADR-STR-002 | God Class - Galaxy (914 lines) | `game/strategy/data/galaxy.py:1` | Complex |
| ADR-STR-003 | Late Import to Avoid Circular Dependency | `game/strategy/data/galaxy.py:4` | Medium |
| ADR-STR-004 | Facade Accessing Private Members | `game/strategy/facade/strategy_` | Simple |
| ADR-UI2-003 | God Class Potential - InputMapper | `game/ui/services/input_mapper.` | Medium |
| ADR-UI1-001 | God Class - TestLabScreen (1906 lines, 7 | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-002 | Inappropriate Intimacy - TestLabScreen a | `game/ui/screens/test_lab/scree` | Simple |
| ADR-UI1-003 | Inappropriate Intimacy - RaceAptitudesPa | `game/ui/panels/race_aptitudes_` | Simple |
| ADR-UI1-004 | Inappropriate Intimacy - StrategyInputHa | `game/ui/screens/strategy_input` | Medium |
| CON-FND-002 | Mixed Singleton Patterns | `game/core/singleton.py` | Simple |
| CON-FND-003 | Inconsistent Method Naming for State Acc | `game/ai/interfaces/controllabl` | Medium |
| CON-FND-004 | Inconsistent Logging Patterns | `game/ai/combat_utils.py:19` | Simple |
| CON-FND-005 | Docstring Format Inconsistency | `Unknown` | Simple |
| CON-FND-006 | Type Hint Gaps in Engine Module | `game/engine/physics.py:56-107` | Medium |
| CON-SIM-003 | Inconsistent Ability Naming Suffix Patte | `game/simulation/components/abi` | Complex |
| CON-SIM-004 | Docstring Format Inconsistency | `Unknown` | Medium |
| CON-SIM-005 | Inconsistent `TYPE_CHECKING` Import Guar | `game/simulation/components/abi` | Simple |
| CON-SIM-006 | Inconsistent Private Member Naming | `game/simulation/components/abi` | Medium |
| CON-SIM-007 | Mixed Error Handling Patterns | `game/simulation/services/desig` | Medium |
| CON-SIM-008 | Inconsistent Registry Access Pattern | `game/simulation/components/abi` | Medium |
| CON-STR-002 | Inconsistent Method Verb Prefixes for Re | `Unknown` | Medium |
| CON-STR-003 | Validator Classes Use Static Methods Whi | `game/strategy/validation/*.py` | Medium |
| CON-STR-004 | Mixed Error Handling Patterns | `game/strategy/validation/*.py` | Medium |
| CON-STR-005 | Inconsistent Parameter Naming for Same C | `Unknown` | Medium |
| CON-STR-006 | Inconsistent Docstring Style | `Unknown` | Medium |
| CON-STR-007 | Import Organization Inconsistency | `Unknown` | Simple |
| CON-UI2-002 | Inconsistent Return Type Conventions for | `game/ui/services/ship_io_adapt` | Simple |
| CON-UI2-003 | Inconsistent Private Method Naming - Sin | `game/ui/services/input_mapper.` | N |
| CON-UI2-004 | Singleton Pattern vs Dependency Injectio | `game/ui/services/screenshot_ma` | Complex |
| CON-UI2-005 | Inconsistent Type Hints - `Any` vs Prope | `game/ui/services/validation_se` | Medium |
| CON-UI2-006 | Missing Type Hints on Multiple Functions | `game/ui/renderer/game_renderer` | Medium |
| CON-UI1-002 | Mixed Class Naming Suffixes for Similar  | `game/ui/screens/` | Complex |
| CON-UI1-003 | Inconsistent Method Prefixes for List Op | `Unknown` | Medium |
| CON-UI1-004 | Type Hints Missing on Many Methods in pa | `game/ui/panels/battle_panels.p` | Medium |
| CON-UI1-005 | Inconsistent Event Handler Naming | `Unknown` | Complex |
| CON-UI1-006 | Docstring Format Inconsistency | `Unknown` | Complex |
| CON-UI1-007 | Inconsistent Import Organization | `Unknown` | Medium |
| DUP-FND-001 | Singleton Pattern Used by Many Classes w | `game/core/strategy_metadata.py` | Medium |
| DUP-FND-002 | JSON Loading with Fallback Defaults Patt | `game/ai/strategy_manager.py:91` | Medium |
| DUP-FND-003 | get_position/get_rotation Access Pattern | `game/ai/combat_utils.py:66-96` | Simple |
| DUP-STR-002 | Ability Extraction Pattern Repeated | `game/strategy/engine/harvestin` | Simple |
| DUP-STR-003 | Maintenance Cost Calculation Duplicated | `game/strategy/engine/maintenan` | Simple |
| DUP-STR-004 | Ship Spawning Logic Duplicated Between P | `game/strategy/engine/productio` | Simple |
| DUP-STR-005 | Complex Spawning Logic Duplicated Betwee | `game/strategy/engine/productio` | Simple |
| DUP-STR-006 | Fleet Lookup Pattern Repeated in Facade | `game/strategy/facade/strategy_` | Simple |
| DUP-UI2-001 | Duplicated ID-Based Expansion Tracking P | `game/ui/panels/battle_panels.p` | Simple |
| DUP-UI2-002 | Duplicated Font Creation in Battle Panel | `game/ui/panels/battle_panels.p` | Simple |
| DUP-UI2-003 | Duplicated Ship Cloning Logic in Battle  | `game/ui/services/battle_factor` | Simple |
| DUP-UI2-004 | Duplicated Directory Creation Pattern in | `game/ui/services/ship_io.py:50` | Simple |
| DUP-UI1-004 | Duplicate InputMapper Tooltip/Keyboard I | `Unknown` | Unknown |
| DUP-UI1-006 | Repeated ScrollingContainer Setup Patter | `Unknown` | Unknown |
| DUP-UI1-007 | Duplicate Resource Icon Loading | `Unknown` | Unknown |
| DUP-UI1-008 | Similar Panel Base Classes in battle_pan | `Unknown` | Unknown |
| DUP-UI1-009 | Duplicate Graph Widget Base Logic | `Unknown` | Unknown |
| LEG-FND-001 | hasattr defensive checks in collision.py | `game/engine/collision.py:107` | Medium |
| LEG-FND-002 | getattr with fallback defaults for core  | `game/engine/collision.py:138,1` | Medium |
| LEG-SIM-001 | Dead Code - `_apply_results_to_fleet` Me | `game/simulation/battle_control` | Simple |
| LEG-SIM-002 | Unused Import - `copy` Module in battle_ | `game/simulation/battle_control` | Simple |
| LEG-SIM-003 | Unused Import - `time` Module in battle_ | `game/simulation/systems/battle` | Simple |
| LEG-STR-001 | Dead Code Methods in HarvestingEngine | `game/strategy/engine/harvestin` | Simple |
| LEG-STR-002 | Legacy Behavior Branch in FleetOrderProc | `game/strategy/engine/fleet_ord` | Medium |
| LEG-STR-003 | Backward Compatibility O(n) Fallback in  | `game/strategy/engine/game_sess` | Medium |
| LEG-UI2-001 | Singleton Pattern Still Used Where DI Av | `game/ui/services/screenshot_ma` | Complex |
| LEG-UI2-002 | ShipFactory Legacy Registries Fallback P | `game/ui/services/ship_factory.` | Medium |
| LEG-UI2-003 | ComponentService Inconsistent DI Pattern | `game/ui/services/component_ser` | Medium |
| TCG-FND-002 | `game/core/protocols.py` - Incomplete Pr | `game/core/protocols.py` | Medium |
| TCG-FND-003 | `game/core/resources.py` - Edge Cases No | `game/core/resources.py` | Simple |
| TCG-FND-004 | `game/core/registry.py` - TestRegistryPr | `game/core/registry.py` | Simple |
| TCG-FND-007 | `game/ai/behaviors.py` - Orbit and Errat | `game/ai/behaviors.py` | Medium |
| TCG-FND-008 | `game/ai/controller.py` - `navigate_to`  | `game/ai/controller.py` | Medium |
| TCG-FND-009 | `game/ai/ai_factory.py` - No Unit Tests | `game/ai/ai_factory.py` | Simple |
| TCG-FND-011 | `game/research/data/tech_tree.py` - `val | `game/research/data/tech_tree.p` | Simple |
| TCG-FND-015 | `game/engine/spatial.py` - Large Radius  | `game/engine/spatial.py` | Simple |
| UNK-02 | Propulsion Abilities Lack Direct Unit Te | `Unknown` | Unknown |
| UNK-03 | AbilityManager Instantiation Logic Under | `Unknown` | Unknown |
| UNK-07 | Hit/Miss Resolution RNG Seeding Not Veri | `Unknown` | Unknown |
| UNK-08 | Seeker Weapon Guidance State Not Tested  | `Unknown` | Unknown |
| UNK-10 | Heavy Mock Usage in BattleEngine Tests | `Unknown` | Unknown |
| UNK-13 | No End-to-End Battle Simulation Tests | `Unknown` | Unknown |
| TCG-UI2-003 | ShipDetailPanel Missing Comprehensive Te | `game/ui/panels/ship_detail_pan` | Medium |
| TCG-UI2-004 | BattleUIService Conversion Logic Underte | `game/ui/services/battle_ui_ser` | Simple |
| TCG-UI2-005 | InputMapper Missing Error Path Tests | `game/ui/services/input_mapper.` | Simple |
| TCG-UI2-006 | ShipIOAdapter and DesignLoaderAdapter Mi | `game/ui/services/ship_io_adapt` | Medium |
| TCG-UI2-007 | SpriteManager Has No Tests for File Syst | `game/ui/renderer/sprites.py` | Simple |
| TCG-UI2-008 | draw_ship Renderer Function Has No Unit  | `game/ui/renderer/game_renderer` | Medium |
| TCG-UI2-009 | ScreenshotManager Missing Integration Te | `game/ui/services/screenshot_ma` | Simple |
| TCG-UI2-010 | ShipThemeManager Portrait Loading Not Fu | `game/ui/assets/ship_theme_mana` | Simple |
| TCG-UI1-004 | Galaxy Test Screen Has No Tests | `game/ui/screens/galaxy_test/*.` | Medium |
| TCG-UI1-005 | Ship Stats Renderer Undertested | `game/ui/panels/ship_stats_rend` | Simple |
| TCG-UI1-006 | Column Manager Missing Tests | `game/ui/screens/column_manager` | Simple |
| TCG-UI1-007 | Race Browser Dialog Untested | `game/ui/screens/race_browser_d` | Medium |
| TCG-UI1-008 | Save Selection Window Untested | `game/ui/screens/save_selection` | Medium |
| TCG-UI1-009 | Planet Report Panel Untested | `game/ui/panels/planet_report_p` | Medium |
| TCG-UI1-010 | System Tree Panel Untested | `game/ui/panels/system_tree_pan` | Medium |
| TCG-UI1-011 | Builder Left Panel Untested | `game/ui/screens/builder/left_p` | Medium |
| TCG-UI1-012 | Schematic View Untested | `game/ui/screens/builder/schema` | Medium |
| TCG-UI1-013 | Workshop Data Reloader Untested | `game/ui/screens/workshop_data_` | Medium |

### Minor (125)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-004 | TYPE_CHECKING Block in protocols.py for  | `game/core/protocols.py:36-38` | N |
| UNK-02 | AI Controller interface imports from gam | `Unknown` | Unknown |
| ADR-STR-005 | Late Imports for Cross-Layer Operations | `game/strategy/data/ship_instan` | Simple |
| ADR-UI2-002 | TYPE_CHECKING Import Pattern in ship_fac | `game/ui/services/ship_factory.` | N |
| ADR-UI1-005 | Deep Attribute Chains - Law of Demeter V | `game/ui/screens/test_lab/scree` | Medium |
| ADR-UI1-006 | Late Imports to Avoid Circular Dependenc | `game/ui/screens/column_manager` | Complex |
| ADR-UI1-007 | Builder accessing Ship internals through | `game/ui/screens/builder/left_p` | Medium |
| CON-FND-007 | Boolean Naming Prefix Inconsistency | `game/ai/interfaces/controllabl` | Simple |
| CON-FND-008 | Verb Prefix Inconsistency for Similar Op | `game/core/registry.py` | Simple |
| CON-FND-009 | Import Organization Inconsistency | `game/core/profiling.py:1-12` | Simple |
| CON-FND-010 | Constants Location Inconsistency | `game/ai/behaviors.py:135-136` | Simple |
| CON-FND-011 | Class Naming Suffix Inconsistency | `game/ai/` | Simple |
| CON-FND-012 | Private Member Prefix Inconsistency | `game/research/ui/research_cont` | Simple |
| CON-FND-013 | Magic Numbers in Rendering Code | `game/research/ui/research_rend` | Simple |
| CON-FND-014 | Inconsistent Parameter Ordering | `game/ai/target_evaluator.py:23` | Simple |
| CON-FND-018 | Defensive Programming Inconsistency | `game/ai/combat_utils.py` | Medium |
| CON-SIM-009 | Inconsistent Verb Prefix for Retrieval M | `Unknown` | Simple |
| CON-SIM-010 | Inconsistent Use of `Optional` vs Union  | `game/simulation/combat/targeti` | Simple |
| CON-SIM-011 | Boolean Method Naming Inconsistency | `game/simulation/systems/battle` | Simple |
| CON-SIM-012 | Inconsistent Class vs Static Method Usag | `game/simulation/components/abi` | Simple |
| CON-SIM-013 | Inconsistent Constant Definition Style | `game/simulation/physics_consta` | Simple |
| CON-SIM-014 | Import Organization Inconsistency | `Unknown` | Simple |
| CON-SIM-015 | Inconsistent Method Ordering in Classes | `game/simulation/systems/battle` | Simple |
| CON-SIM-016 | Inconsistent Line Length in Docstrings | `Unknown` | Simple |
| CON-STR-008 | Boolean Naming Inconsistency | `game/strategy/data/fleet.py` | Simple |
| CON-STR-009 | Magic Numbers in Formulas | `game/strategy/services/fleet_s` | Simple |
| CON-STR-010 | Inconsistent __all__ Exports | `Unknown` | Simple |
| CON-STR-011 | Result Dataclass Naming Convention | `game/strategy/engine/fleet_ord` | Simple |
| CON-STR-012 | Engine Class Naming vs Interface Naming | `game/strategy/interfaces/engin` | Medium |
| CON-STR-013 | Underscore Prefix Inconsistency for Priv | `game/strategy/engine/harvestin` | Simple |
| CON-STR-014 | Type Hint Usage Gaps | `Unknown` | Medium |
| CON-UI2-007 | Inconsistent Docstring Format Between Mo | `Unknown` | Simple |
| CON-UI2-008 | Inconsistent Method Verb Prefixes for Ge | `game/ui/services/component_ser` | N |
| CON-UI2-009 | Inconsistent Error Handling - Exceptions | `game/ui/services/ship_factory.` | Medium |
| CON-UI2-010 | Inconsistent Import Organization | `game/ui/services/screenshot_ma` | Simple |
| CON-UI2-011 | Inconsistent Naming - `registry_provider | `game/ui/services/ship_factory.` | Simple |
| CON-UI2-012 | Hardcoded Color Tuples Instead of Using  | `game/ui/renderer/game_renderer` | Simple |
| CON-UI2-013 | Inconsistent Module-Level Docstrings | `game/ui/renderer/sprites.py` | Simple |
| CON-UI2-014 | Boolean Method Naming - Missing `is_`/`h | `game/ui/services/battle_ui_ser` | N |
| CON-UI2-015 | Magic Numbers in Configuration | `game/ui/renderer/camera.py:17-` | Simple |
| CON-UI1-008 | Inconsistent Private Member Naming | `Unknown` | Simple |
| CON-UI1-009 | Boolean Parameter Naming Inconsistency | `game/ui/screens/planet_list_fi` | Simple |
| CON-UI1-010 | Magic Numbers in Layout Code | `Unknown` | Simple |
| CON-UI1-011 | Inconsistent kill()/cleanup Method Patte | `Unknown` | Simple |
| CON-UI1-012 | Inconsistent Column Configuration Patter | `planet_list_window.py` | Medium |
| CON-UI1-013 | Inconsistent Scroll Bar Handling | `planet_list_window.py` | Simple |
| CON-UI1-014 | Inconsistent Callback Naming | `Unknown` | Simple |
| CON-UI1-015 | Empty __init__.py Files | `game/ui/screens/__init__.py` | Simple |
| CON-UI1-016 | Inconsistent Use of Type Aliases | `empire_build_queue_window.py` | Simple |
| DUP-FND-004 | Direction Calculation Repeated in Behavi | `game/ai/behaviors.py:70-84` | Simple |
| DUP-FND-005 | to_dict/from_dict Serialization Pattern | `game/research/data/research_tr` | Simple |
| DUP-FND-006 | Identical Depth/Layout Calculation Patte | `game/research/data/tech_tree.p` | Simple |
| DUP-FND-007 | Navigation Angle Calculation Pattern | `game/ai/controller.py:434-450` | Simple |
| DUP-STR-007 | find_ship_with_ability Wrapper in Superw | `game/strategy/validation/super` | Simple |
| DUP-STR-008 | Planet/Fleet Build Capability Checks Sim | `game/strategy/data/planet.py:2` | Simple |
| DUP-STR-009 | Queue Tick Processing Partially Duplicat | `game/strategy/engine/productio` | Simple |
| DUP-STR-010 | HexCoord Serialization Pattern Repeated | `game/strategy/data/fleet.py:32` | Simple |
| DUP-STR-011 | collect_build_queues Pattern Duplicated | `game/strategy/data/build_queue` | Complex |
| DUP-UI2-005 | Registry Provider Lazy Resolution Patter | `game/ui/services/component_ser` | Medium |
| DUP-UI2-006 | get_bounding_rect Pattern with Different | `game/ui/utils.py:110` | Simple |
| DUP-UI2-007 | Singleton Managers Follow Similar Patter | `game/ui/services/screenshot_ma` | Medium |
| DUP-UI2-008 | Scale Image Pattern Repeated in Multiple | `Unknown` | Medium |
| DUP-UI2-009 | AIControllerFactory Created Multiple Tim | `game/ui/services/battle_factor` | Simple |
| DUP-UI1-010 | Repeated Window Cleanup Patterns | `Unknown` | Unknown |
| DUP-UI1-011 | Duplicate Font Creation | `Unknown` | Unknown |
| DUP-UI1-012 | Repeated Button Rect Calculation Pattern | `Unknown` | Unknown |
| DUP-UI1-013 | Repeated Row Label Clear Pattern | `Unknown` | Unknown |
| DUP-UI1-014 | Formation Editor State Machine Duplicati | `Unknown` | Unknown |
| DUP-UI1-015 | Duplicate Sanitize Object ID Methods | `Unknown` | Unknown |
| DUP-UI1-016 | Repeated Color Constants | `Unknown` | Unknown |
| DUP-UI1-017 | Similar Handle Resize Patterns | `Unknown` | Unknown |
| LEG-FND-003 | Fallback resource file handling in resou | `game/core/resources.py:7-10,67` | Simple |
| LEG-FND-004 | Input action key name fallback logic | `game/core/input_actions.py:286` | Simple |
| LEG-FND-005 | AI combat_utils uses defensive fallback  | `game/ai/combat_utils.py:79-125` | Simple |
| LEG-FND-006 | Research system standalone sandbox desig | `game/research/__init__.py:1-8` | Simple |
| LEG-SIM-004 | Unused Import - `BattleEndCondition` in  | `game/simulation/battle_control` | Simple |
| LEG-SIM-005 | Unused Import - `log_debug` in battle_co | `game/simulation/battle_control` | Simple |
| LEG-SIM-006 | Unused Import - `log_debug` in battle_st | `game/simulation/battle_state.p` | Simple |
| LEG-SIM-007 | hasattr Checks on Known Dataclass Fields | `game/simulation/managers/battl` | Simple |
| LEG-SIM-008 | Defensive Fallback Comment Indicates Inc | `game/simulation/battle_control` | Simple |
| LEG-SIM-009 | Excessive hasattr Checks in Serializatio | `game/simulation/battle_state.p` | Medium |
| LEG-SIM-010 | Vestigial Format Version Comment | `game/simulation/entities/ship_` | Simple |
| LEG-STR-004 | Unused sprite_preview Field Placeholder | `game/strategy/data/design_meta` | Simple |
| LEG-STR-005 | Fallback Fleet-Like Object Creation in F | `game/strategy/services/fleet_n` | Simple |
| LEG-STR-006 | Legacy Species Default in _execute_load | `game/strategy/engine/fleet_ord` | Simple |
| LEG-STR-007 | TODO Comment for Future Feature | `game/strategy/engine/fleet_ord` | Simple |
| LEG-STR-008 | try/except for Mock Compatibility | `game/strategy/engine/fleet_ord` | Simple |
| LEG-STR-009 | Old Format Warning in DesignMetadata | `game/strategy/data/design_meta` | Simple |
| LEG-UI2-004 | Unused Method get_type_for_class in Vehi | `game/ui/services/vehicle_class` | Simple |
| LEG-UI2-005 | Potentially Unused Method is_modifier_al | `game/ui/services/component_ser` | Simple |
| LEG-UI2-006 | ShipIOAdapter get_ships_folder Method Un | `game/ui/services/ship_io_adapt` | Simple |
| LEG-UI2-007 | BattleOrchestrator.create_ai_for_ship Un | `game/ui/orchestration/battle_o` | Simple |
| LEG-UI2-008 | hasattr Checks in BattleUIService May In | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI2-009 | InputMapper._defaults_path Stored But Ne | `game/ui/services/input_mapper.` | Simple |
| TCG-FND-005 | `game/core/input_actions.py` - Missing T | `game/core/input_actions.py` | Simple |
| TCG-FND-006 | `game/core/paths.py` - No Direct Unit Te | `game/core/paths.py` | Simple |
| TCG-FND-010 | `game/ai/target_evaluator.py` - Speed Ru | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-012 | `game/research/systems/research_service. | `game/research/systems/research` | Simple |
| TCG-FND-013 | `game/research/ui/research_controls.py`  | `game/research/ui/research_cont` | Medium |
| TCG-FND-016 | `game/engine/physics.py` - Drag Clamping | `game/engine/physics.py` | Simple |
| UNK-04 | ShipStatsCalculator Phase Methods Not In | `Unknown` | Unknown |
| UNK-05 | BattleStateManager Serialization Edge Ca | `Unknown` | Unknown |
| UNK-09 | Component Stat Aggregation Order Depende | `Unknown` | Unknown |
| UNK-11 | Combat Endurance Tests Use Manual Abilit | `Unknown` | Unknown |
| UNK-12 | Missing Parametrization in Weapon Tests | `Unknown` | Unknown |
| UNK-14 | Fighter Launch Integration Not Tested | `Unknown` | Unknown |
| UNK-01 | game/strategy/data/physics.py - Indirect | `Unknown` | Unknown |
| UNK-02 | StrategySessionFacade.get_fleet_remainin | `Unknown` | Unknown |
| UNK-03 | FleetNavigationService - Incomplete Meth | `Unknown` | Unknown |
| UNK-07 | Test Fixtures Could Be Consolidated | `Unknown` | Unknown |
| UNK-09 | Facade Integration Tests Are Lightweight | `Unknown` | Unknown |
| TCG-UI2-011 | Camera.update_input() Only Tests Individ | `game/ui/renderer/camera.py` | Simple |
| TCG-UI2-012 | ValidationService Missing Boundary Tests | `game/ui/services/validation_se` | Simple |
| TCG-UI2-013 | BattleFactories Service Has No Dedicated | `game/ui/services/battle_factor` | Simple |
| TCG-UI2-014 | IBattleUI Protocol Tests Are Type-Only | `game/ui/interfaces/battle_ui.p` | Simple |
| TCG-UI2-015 | ComponentService Missing Registry Integr | `game/ui/services/component_ser` | Simple |
| TCG-UI2-016 | VehicleClassService Edge Cases | `game/ui/services/vehicle_class` | Simple |
| TCG-UI1-014 | BattleUI Missing draw() Test | `game/ui/screens/battle_ui.py` | Simple |
| TCG-UI1-015 | FormationRenderer Missing Tests | `game/ui/screens/formation/rend` | Simple |
| TCG-UI1-016 | Strategy Panel Manager Untested | `game/ui/screens/strategy_panel` | Simple |
| TCG-UI1-017 | Empire Panel Window Undertested | `game/ui/screens/empire_panel_w` | Simple |
| TCG-UI1-018 | Fleet Orders Window Undertested | `game/ui/screens/fleet_orders_w` | Simple |
| TCG-UI1-019 | Design Selector Window Edge Cases | `game/ui/screens/design_selecto` | Simple |
| TCG-UI1-020 | Base Gallery Panel Missing Tests | `game/ui/panels/base_gallery.py` | Simple |
| TCG-UI1-021 | Design Report Panel Undertested | `game/ui/panels/design_report_p` | Simple |

### Info (52)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-005 | Well-Structured Dependency Injection in  | `game/ai/ai_factory.py:25-29` | N |
| ADR-STR-006 | TYPE_CHECKING Patterns Used Throughout | `Unknown` | N |
| ADR-UI2-001 | pygame.math.Vector2 Usage in UI Services | `game/ui/services/ship_factory.` | N |
| ADR-UI2-004 | Well-Documented Cross-Layer Orchestratio | `game/ui/orchestration/battle_o` | N |
| ADR-UI1-008 | Large Screen Files Approaching God Class | `Unknown` | N |
| ADR-UI1-009 | Test Framework Coupling in UI Layer | `game/ui/screens/test_lab/*.py` | N |
| CON-FND-015 | Natural Variation - Module-Level vs Clas | `game/core/json_utils.py` | None |
| CON-FND-016 | Protocol Usage Variation | `game/core/protocols.py` | None |
| CON-FND-017 | Exception Hierarchy Well-Structured | `game/core/exceptions.py` | None |
| CON-SIM-017 | Natural Variation in Ability Structure | `game/simulation/components/abi` | N |
| CON-SIM-018 | Validation Rule Template Method Pattern | `game/simulation/validation/bas` | N |
| CON-SIM-019 | Consistent Use of STAT_BINDINGS | `game/simulation/components/abi` | N |
| CON-SIM-020 | Protocol Pattern for AI Controller | `game/simulation/interfaces/ai_` | N |
| CON-SIM-021 | Consistent Use of TYPE_CHECKING in Core  | `game/simulation/systems/battle` | N |
| CON-STR-015 | Adapter Pattern Usage | `game/strategy/adapters/simulat` | Simple |
| CON-STR-016 | Formula Module Organization | `game/strategy/formulas/` | Simple |
| CON-STR-017 | Event System Pattern Adherence | `game/strategy/events/` | N |
| CON-UI2-016 | Intentional Pattern Variation - Adapter  | `game/ui/services/` | N |
| CON-UI2-017 | Different __init__.py Export Styles | `game/ui/services/__init__.py` | N |
| CON-UI2-018 | Cross-Layer Import Documentation Quality | `game/ui/renderer/game_renderer` | Simple |
| CON-UI1-017 | Logging Usage Variations | `game/ui/screens/` | N |
| CON-UI1-018 | Different Panel Creation Patterns | `game/ui/panels/` | N |
| DUP-FND-008 | SingletonMeta Usage is Consistent and We | `game/core/singleton.py` | N |
| DUP-STR-012 | Consistent Delegate Pattern (Good Design | `game/strategy/data/fleet.py` | N |
| DUP-STR-013 | Well-Consolidated Component Inspector | `game/strategy/services/compone` | N |
| DUP-UI2-010 | Similar Ship Loading Patterns Between Se | `game/ui/services/ship_io.py:10` | Simple |
| DUP-UI1-018 | Well-Extracted BaseGallery Pattern | `Unknown` | Unknown |
| DUP-UI1-019 | Existing PROJ-43 DTO Pattern | `Unknown` | Unknown |
| DUP-UI1-020 | FormationEditor Delegation Pattern | `Unknown` | Unknown |
| DUP-UI1-021 | Modular Strategy Screen Architecture | `Unknown` | Unknown |
| LEG-FND-007 | getattr usage in AI behaviors is appropr | `game/ai/behaviors.py:281,334,3` | N |
| LEG-FND-008 | AI controllable adapter uses getattr for | `game/ai/interfaces/controllabl` | N |
| LEG-SIM-011 | Module Identity Drift Known Issue | `game/simulation/components/abi` | N |
| LEG-SIM-012 | PROJ Reference Comments Throughout | `Unknown` | N |
| LEG-STR-010 | project_path_as_dicts Backward Compatibi | `game/strategy/services/fleet_n` | Simple |
| LEG-STR-011 | has_race_config Check in _transfer_found | `game/strategy/engine/fleet_ord` | Simple |
| LEG-UI2-010 | Fallback Patterns Throughout UI Layer | `Unknown` | Simple |
| LEG-UI2-011 | Direct Simulation Layer Imports in UI Se | `Unknown` | N |
| TCG-FND-017 | No End-to-End AI Strategy Resolution Tes | `game/ai/strategy_manager.py` | Medium |
| TCG-FND-018 | Research UI Integration with Service Lay | `game/research/ui/research_scen` | Medium |
| UNK-01 | All Core Simulation Modules Have Test Co | `Unknown` | Unknown |
| UNK-15 | Simulation Tests Directory Well Organize | `Unknown` | Unknown |
| UNK-04 | Command Handler Chain Coverage is Compre | `Unknown` | Unknown |
| UNK-05 | Fleet Order Processing Coverage is Stron | `Unknown` | Unknown |
| UNK-06 | Colonize Validation Coverage is Excellen | `Unknown` | Unknown |
| UNK-08 | Density Primitives Have Good Individual  | `Unknown` | Unknown |
| UNK-10 | All Major Categories Covered | `Unknown` | Unknown |
| TCG-UI2-017 | test_utils.py Could Use Parameterized Te | `tests/unit/ui/test_utils.py` | Simple |
| TCG-UI2-018 | Missing conftest.py Fixtures for UI Mana | `tests/unit/ui/conftest.py` | Simple |
| TCG-UI1-022 | Heavy Mocking Pattern in Screen Tests | `tests/unit/ui/screens/test_wor` | Medium |
| TCG-UI1-023 | Battle Panels Tests Reload Module | `tests/unit/ui/test_battle_pane` | Medium |
| TCG-UI1-024 | Missing Serialization Round-Trip Tests | `Unknown` | Medium |


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
| Total Findings | 297 |
| Critical | 19 |
| Major | 101 |
| Minor | 125 |
| Info | 52 |
| Agents Used | 23 |

---
*Report generated: 2026-02-13 22:35*
