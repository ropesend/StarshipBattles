# Review Report: 2026-04-05_110710_general_strategy-layer-health

## Metadata
- **Date:** 2026-04-05
- **Type:** General Review
- **Description:** Strategy layer broad health check
- **Agents Used:** 5

## Executive Summary
- **Total Findings:** 80
- **Critical:** 4 | **Major:** 26 | **Minor:** 35 | **Info:** 15
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: AI Layer Import in Strategy Adapter (Late Import Masking Layer Violation)
**ID:** AR-001
**Agent:** Architecture
**Location:** `game/strategy/adapters/simulation_adapter.py:127`
**Effort:** Medium

**ID:** AR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:127`
**Issue:** `SimulationBattleResolver` performs a runtime late import of `game.ai.ai_factory.AIControllerFactory` when no AI factory is injected. Per the architecture docs, Strategy is allowed to depend on Simulation and Core only -- AI is a forbidden dependency. The late import disguises this as optional but it is a hard runtime dependency in the default code path (no tests or production code injects the factory).
**...

---

### 2. CRITICAL: Oversized File - command_handlers.py (1062 lines)
**ID:** CQ-001
**Agent:** Code Quality
**Location:** `game/strategy/engine/command_handlers.py:1-1062`
**Effort:** Medium

**ID:** CQ-001
**Location:** `game/strategy/engine/command_handlers.py:1-1062`
**Issue:** At 1062 lines this file is more than double the 500-line target. It contains the BaseCommandHandler base class, CommandHandlerRegistry, 14 concrete command handler classes, the `add_move_order_if_needed` utility function, and the `create_default_registry` factory. This is a god-module that aggregates too many responsibilities in one file.
**Impact:** Hard to navigate, increased merge conflicts, and makes co...

---

### 3. CRITICAL: Turn engine module docstring missing 4 phases that exist in code
**ID:** DOCC-006
**Agent:** Docs Consistency
**Location:** `game/strategy/engine/turn_engine.py:1-23`
**Effort:** Simple

**ID:** DOCC-006
**Location:** `game/strategy/engine/turn_engine.py:1-23` (module docstring)
**Issue:** The module-level docstring lists phases but is missing:
  - Phase 0c1: PlanetEnergyEngine (exists in code at line 458)
  - Phase 0f: EnvironmentalHazardEngine (exists in code at line 470)
  - Phase 1.6: PlanetActionEngine (exists in code at line 483)
  - Post-loop: QualityEngine + AtmosphereEngine (exists in code at lines 381-384)
The `_process_tick` method docstring (line 432) is also missing...

---

### 4. CRITICAL: No error handling around turn tick processing loop
**ID:** ERR-001
**Agent:** Error Handling
**Location:** `game/strategy/engine/turn_engine.py:369-370`
**Effort:** Medium

**ID:** ERR-001
**Location:** `game/strategy/engine/turn_engine.py:369-370`
**Issue:** The `process_turn` method iterates 100 ticks, calling `_process_tick` which orchestrates 12+ sub-engine phases. There is zero exception handling around the tick loop or within `_process_tick`. If any sub-engine raises an unexpected exception during tick 37 of 100, the entire turn crashes with no recovery, no partial state logging, and no indication of which phase or tick failed.
**Impact:** A single error in a...

---

### 5. MAJOR: Widespread Facade Bypass -- UI Accesses GameSession Internals Directly
**ID:** AR-002
**Agent:** Architecture
**Location:** `game/ui/screens/strategy_screen.py:134-156`
**Effort:** Complex

**ID:** AR-002
**Location:** `game/ui/screens/strategy_screen.py:134-156`, `game/ui/screens/strategy_build_queue_manager.py:94-265`, `game/ui/screens/strategy_detail_formatter.py:412-413`, `game/ui/screens/strategy_renderer.py`, `game/ui/screens/strategy_window_manager.py:134`, `game/ui/panels/build_queue_portraits.py`
**Issue:** `StrategyScreen` exposes `session.galaxy`, `session.empires`, `session.player_empire`, `session.enemy_empire`, `session.systems`, and `session.human_player_ids` as conv...

---

### 6. MAJOR: data/ Subpackage Depends on engine/ (Upward Dependency)
**ID:** AR-003
**Agent:** Architecture
**Location:** `game/strategy/data/build_queue_source.py:267`
**Effort:** Simple

**ID:** AR-003
**Location:** `game/strategy/data/build_queue_source.py:267`
**Issue:** `build_queue_source.py` (in the `data/` subpackage) imports `_colony_has_planetary_yard` from `game.strategy.engine.production_engine` (a private function from the `engine/` subpackage). The `data/` subpackage should be a lower-level layer containing domain entities and value objects. The `engine/` subpackage contains turn processing logic that depends on `data/`. This creates a bidirectional dependency: `data...

---

### 7. MAJOR: services/ Subpackage Depends on engine/ Commands
**ID:** AR-004
**Agent:** Architecture
**Location:** `game/strategy/services/cargo_transfer_service.py:12`
**Effort:** Medium

**ID:** AR-004
**Location:** `game/strategy/services/cargo_transfer_service.py:12`
**Issue:** `CargoTransferService` (in `services/`) has a top-level import of `IssueTransferCommand` from `game.strategy.engine.commands`. The `services/` subpackage should provide business logic that `engine/` consumes, not depend on engine-specific command types. This creates a `services/ -> engine/` dependency that inverts the expected direction (`engine/ -> services/`).
**Impact:** Makes it harder to test `Carg...

---

### 8. MAJOR: 8 of 12 Sub-Engines Do Not Implement Their Interfaces
**ID:** AR-005
**Agent:** Architecture
**Location:** `game/strategy/engine/production_engine.py`
**Effort:** Simple

**ID:** AR-005
**Location:** `game/strategy/engine/production_engine.py`, `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/engine/fleet_movement_engine.py`, `game/strategy/engine/order_processor.py`, `game/strategy/engine/planet_action_engine.py`, `game/strategy/engine/environmental_hazard_engine.py`, `game/strategy/engine/consumable_management_engine.py`, `game/strategy/engine/planet_energy_engine.py`
**Issue:** `game/strategy/interfaces/engines.py` defines 12 ABC interfaces...

---

### 9. MAJOR: Dead Code / Stale Comments in pathfinding.py
**ID:** CQ-002
**Agent:** Code Quality
**Location:** `game/strategy/data/pathfinding.py:80-140`
**Effort:** Simple

**ID:** CQ-002
**Location:** `game/strategy/data/pathfinding.py:80-140`
**Issue:** The `find_path_interstellar` function contains extensive "thinking aloud" comments left from initial development: "Wait, galaxy.systems is keyed by location", "Optimization: Build name_to_system cache or linear search?", "Cost is distance? Or just +1 hop?", etc. There is also a dead assignment at line 89 (`current_sys = galaxy.systems[...]`) that is immediately overwritten at line 104.
**Impact:** Misleading for m...

---

### 10. MAJOR: Duplicate Stabilizer Check Pattern in SuperweaponOrderProcessor
**ID:** CQ-003
**Agent:** Code Quality
**Location:** `game/strategy/engine/superweapon_order_processor.py:707-815`
**Effort:** Simple

**ID:** CQ-003
**Location:** `game/strategy/engine/superweapon_order_processor.py:707-815`
**Issue:** Three nearly identical private methods `_is_planet_stabilized`, `_is_system_stellar_stabilized`, and `_is_system_warp_stabilized` each iterate empires and scopes calling `find_abilities_in_scope` with the same pattern. They differ only in the ability name string and the scopes checked. This is a DRY violation.
**Impact:** If the stabilizer-checking logic ever changes (e.g., new scope added), it ...

---


## Findings by Severity

### Critical (4)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | AI Layer Import in Strategy Adapter (Lat | `game/strategy/adapters/simulat` | Medium |
| CQ-001 | Oversized File - command_handlers.py (10 | `game/strategy/engine/command_h` | Medium |
| DOCC-006 | Turn engine module docstring missing 4 p | `game/strategy/engine/turn_engi` | Simple |
| ERR-001 | No error handling around turn tick proce | `game/strategy/engine/turn_engi` | Medium |

### Major (26)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-002 | Widespread Facade Bypass -- UI Accesses  | `game/ui/screens/strategy_scree` | Complex |
| AR-003 | data/ Subpackage Depends on engine/ (Upw | `game/strategy/data/build_queue` | Simple |
| AR-004 | services/ Subpackage Depends on engine/  | `game/strategy/services/cargo_t` | Medium |
| AR-005 | 8 of 12 Sub-Engines Do Not Implement The | `game/strategy/engine/productio` | Simple |
| CQ-002 | Dead Code / Stale Comments in pathfindin | `game/strategy/data/pathfinding` | Simple |
| CQ-003 | Duplicate Stabilizer Check Pattern in Su | `game/strategy/engine/superweap` | Simple |
| CQ-004 | Mock Object Hack in FleetNavigationServi | `game/strategy/services/fleet_n` | Medium |
| CQ-005 | Duplicated Ownership Check Pattern in pl | `game/strategy/engine/planet_co` | Simple |
| CQ-006 | Planet Lookup O(N*M) in Facade._get_plan | `game/strategy/facade/strategy_` | Simple |
| CQ-007 | Oversized Files Exceeding 500-Line Targe | `Unknown` | Medium |
| CQ-008 | Broad Exception Catches | `game/strategy/data/empire.py:3` | Simple |
| DC-001 | Three unused imports in design_metadata. | `game/strategy/data/design_meta` | Simple |
| DC-002 | Four unused imports in galaxy.py | `game/strategy/data/galaxy.py:2` | Simple |
| DC-003 | Dead methods in planet_energy_engine.py  | `game/strategy/engine/planet_en` | Simple |
| DC-004 | Dead methods in AstrophysicsLoader (3 me | `game/strategy/generation/loade` | Simple |
| DC-005 | Dead methods: Empire.remove_colony, Game | `game/strategy/data/empire.py:5` | Simple |
| DOCC-001 | Orders system doc still uses FleetOrder  | `docs/systems/orders_system.md` | Simple |
| DOCC-002 | Orders system doc missing ACTIVATE_ABILI | `docs/systems/orders_system.md` | Simple |
| DOCC-003 | Turn engine has undocumented post-loop p | `game/strategy/engine/turn_engi` | Simple |
| DOCC-004 | SetAtmosphereTargetCommand handler not d | `docs/systems/strategy_layer.md` | Simple |
| DOCC-005 | Command names in docs use stale PROJ-238 | `docs/systems/strategy_layer.md` | Simple |
| ERR-002 | `except Exception` without intentional b | `game/strategy/data/fleet.py:39` | Simple |
| ERR-003 | ValueError used instead of ValidationExc | `game/strategy/data/fleet_capab` | Simple |
| ERR-004 | Silent pass in debug logging helper | `game/strategy/engine/turn_engi` | Simple |
| ERR-005 | DesignLibrary PermissionError handler mi | `game/strategy/systems/design_l` | Simple |
| ERR-006 | Missing error logging in design_library  | `game/strategy/systems/design_l` | Simple |

### Minor (35)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-006 | Excessive Late Imports (334 instances) S | `Unknown` | Medium |
| AR-007 | RegistryManager.instance() Singleton Acc | `game/strategy/data/build_queue` | Simple |
| AR-008 | command_handlers.py Is a 1062-Line Monol | `game/strategy/engine/command_h` | Medium |
| AR-009 | PlanetaryFacility Has Top-Level Import f | `game/strategy/data/planetary_f` | Simple |
| AR-010 | data/ Subpackage Has Widespread Upward D | `game/strategy/data/fleet_capab` | Complex |
| CQ-009 | Duplicate TYPE_CHECKING Import Block | `game/strategy/engine/superweap` | Simple |
| CQ-010 | Inconsistent Handler Base Class Usage | `game/strategy/engine/planet_co` | Simple |
| CQ-011 | Superweapon Mission Handlers Are Repetit | `game/strategy/engine/superweap` | Medium |
| CQ-012 | Superweapon Processor Methods Are Repeti | `game/strategy/engine/superweap` | Medium |
| CQ-013 | DesignLibrary Instantiated Repeatedly Pe | `game/strategy/engine/command_h` | Simple |
| CQ-014 | `process_self_destruct` Duplicates `_fin | `game/strategy/engine/superweap` | Simple |
| CQ-015 | Stale Duplicate Step Numbering | `game/strategy/engine/command_h` | Simple |
| DC-006 | Unused imports in fleet.py | `game/strategy/data/fleet.py:8,` | Simple |
| DC-007 | Unused Optional/TYPE_CHECKING in consuma | `game/strategy/engine/consumabl` | Simple |
| DC-008 | Scattered unused typing imports across 1 | `Unknown` | Simple |
| DC-009 | BattleService imported but unused in sim | `game/strategy/adapters/simulat` | Simple |
| DC-010 | Unused variable `owning_empire` in comma | `game/strategy/engine/command_h` | Simple |
| DC-011 | Unused variable `removed_item` in comman | `game/strategy/engine/command_h` | Simple |
| DC-012 | Unused variable `old_location` in fleet_ | `game/strategy/engine/fleet_mov` | Simple |
| DC-013 | Unused variable `parallel_clamped` in li | `game/strategy/generation/densi` | Simple |
| DC-014 | Unused variable `cluster_regions` in reg | `game/strategy/generation/regio` | Simple |
| DOCC-007 | __init__.py exports FleetOrder alias not | `game/strategy/__init__.py:64` | Simple |
| DOCC-008 | Strategy_layer.md __init__.py docstring  | `game/strategy/__init__.py:11` | Simple |
| DOCC-009 | Conventions doc section 1.8 claims old b | `docs/03_CONVENTIONS.md:134-135` | Medium |
| DOCC-010 | Several data files in game/strategy/data | `game/strategy/data/` | Medium |
| DOCC-011 | engine/empire_economy_calculator.py not  | `game/strategy/engine/empire_ec` | Simple |
| DOCC-012 | strategy_layer.md DTO list missing Fleet | `docs/systems/strategy_layer.md` | Simple |
| DOCC-013 | star_image_registry.py in generation/ no | `game/strategy/generation/star_` | Simple |
| DOCC-018 | Facade query method table in strategy_la | `docs/systems/strategy_layer.md` | Simple |
| ERR-007 | build_queue_source silent fallback to em | `game/strategy/data/build_queue` | Simple |
| ERR-008 | game_initializer silently ignores invali | `game/strategy/engine/game_init` | Simple |
| ERR-009 | ship_stats_calculator silent ValueError  | `game/strategy/services/ship_st` | Simple |
| ERR-010 | fleet_dto silent capability resolution f | `game/strategy/facade/dto/fleet` | Simple |
| ERR-011 | design_library delete_design PermissionE | `game/strategy/systems/design_l` | Simple |
| ERR-012 | _resolve_build_entity returns None silen | `game/strategy/engine/command_h` | Simple |

### Info (15)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-011 | Facade Returns Domain Objects via Intern | `game/strategy/facade/strategy_` | Simple |
| AR-012 | Documentation Lists Strategy as Forbidde | `docs/01_ARCHITECTURE.md` | N |
| CQ-016 | `_get_reference_planet` Returns First Pl | `game/strategy/engine/superweap` | Simple |
| CQ-017 | Galaxy.__init__ Does File I/O (CWD-Depen | `game/strategy/data/galaxy.py:1` | Medium |
| CQ-018 | Facade Exposes Private Session Methods | `game/strategy/facade/strategy_` | Simple |
| DC-015 | Documented unused parameters in interfac | `game/strategy/engine/productio` | N |
| DC-016 | `math` imported but unused in planet.py | `game/strategy/data/planet.py:7` | Simple |
| DC-017 | Duplicate `Any` import in planet.py | `game/strategy/data/planet.py:1` | Simple |
| DC-018 | `get_shield_info` imported but unused in | `game/strategy/engine/planet_ac` | Simple |
| DOCC-014 | orders_system.md "Adding a New Order Typ | `docs/systems/orders_system.md` | Simple |
| DOCC-015 | strategy_layer.md TurnEngine docstring e | `docs/systems/strategy_layer.md` | Simple |
| DOCC-016 | orders_system.md Key Files table lists F | `docs/systems/orders_system.md` | Simple |
| DOCC-017 | Production system doc mentions 6 planeta | `docs/systems/production_system` | Simple |
| ERR-013 | Dead code -- _resolve_fleet_required and | `game/strategy/engine/command_h` | Simple |
| ERR-014 | Performance logging uses logger.warning  | `game/strategy/engine/turn_engi` | Simple |


## Agent Reports

- [Architecture Report](findings/architecture_report.md)
- [Code Quality Report](findings/code_quality_report.md)
- [Dead Code Report](findings/dead_code_report.md)
- [Docs Consistency Report](findings/docs_consistency_report.md)
- [Error Handling Report](findings/error_handling_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 80 |
| Critical | 4 |
| Major | 26 |
| Minor | 35 |
| Info | 15 |
| Agents Used | 5 |

---
*Report generated: 2026-04-05 11:16*
