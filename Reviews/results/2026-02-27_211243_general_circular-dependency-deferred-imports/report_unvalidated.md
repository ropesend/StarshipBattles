# Review Report: 2026-02-27_211243_general_circular-dependency-deferred-imports

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review — Architecture Focus
- **Description:** Validate and quantify circular dependency / deferred import hazards in game/
- **Agents Used:** 3

## Executive Summary
- **Total Findings:** 35
- **Critical:** 3 | **Major:** 15 | **Minor:** 11 | **Info:** 6
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: TurnEngine has 15 deferred imports -- fragile initialization
**ID:** CA-001
**Agent:** Coupling Analyst
**Location:** `game/strategy/engine/turn_engine.py:80-160`
**Effort:** Medium

**ID:** CA-001
**Location:** `game/strategy/engine/turn_engine.py:80-160` (constructor body)
**Issue:** TurnEngine defers ALL 15 sub-engine imports to its constructor body. If any import fails at runtime (e.g., a module rename or circular dependency introduced later), the error manifests at turn-processing time rather than at import time, making debugging significantly harder.
**Impact:** The deferred imports mask potential circular dependencies rather than resolving them. If one of the 15 sub-e...

---

### 2. CRITICAL: OrderType/FleetOrder in monolithic fleet.py causes 15+ deferred imports
**ID:** RS-001
**Agent:** Remediation Strategist
**Location:** `game/strategy/data/fleet.py:20-61`
**Effort:** Medium

**ID:** RS-001
**Location:** `game/strategy/data/fleet.py:20-61` (definitions), `game/strategy/engine/command_handlers.py` (11 sites), 3 other files
**Issue:** The `OrderType` enum and `FleetOrder` class are defined in `fleet.py` alongside the heavyweight `Fleet` class. Importing `OrderType` transitively imports `Fleet`, which imports `FleetResourceAggregator`, `FleetCapabilityCalculator`, `FleetBattleAdapter`, `ShipInstance`, and their dependency trees. This forces 15 files to use deferred impo...

---

### 3. CRITICAL: command_handlers.py has 16 deferred imports within method bodies
**ID:** RS-002
**Agent:** Remediation Strategist
**Location:** `game/strategy/engine/command_handlers.py`
**Effort:** Simple

**ID:** RS-002
**Location:** `game/strategy/engine/command_handlers.py` (lines 50, 93, 263, 307, 355, 380, 409, 500, 527, 578, 601, 620, 666)
**Issue:** Every command handler method in this 713-line file starts with `from game.strategy.data.fleet import FleetOrder, OrderType`. The `create_default_registry()` function also defers importing all superweapon handlers. The `add_move_order_if_needed()` and `create_auto_load_population_order()` helper functions do the same.
**Impact:** 16 deferred impo...

---

### 4. MAJOR: StrategyBuildQueueManager duplicates deferred imports across 3 methods
**ID:** CA-002
**Agent:** Coupling Analyst
**Location:** `game/ui/screens/strategy_build_queue_manager.py:48-53, 171-173, 214-216`
**Effort:** Simple

**ID:** CA-002
**Location:** `game/ui/screens/strategy_build_queue_manager.py:48-53, 171-173, 214-216`
**Issue:** The same 3 imports (`BuildQueueScreen`, `DesignLibrary`, `DesignLoaderAdapter`) are repeated identically in `on_build_yard_click()`, `on_navigate_to_hex_build()`, and `on_fleet_build_click()`. This is copy-paste duplication in import statements.
**Impact:** If any of these imports need to change (e.g., module rename), 3 locations must be updated instead of 1. The deferred pattern pro...

---

### 5. MAJOR: Fleet data model is a coupling bottleneck with 38 importers
**ID:** CA-003
**Agent:** Coupling Analyst
**Location:** `game/strategy/data/fleet.py`
**Effort:** Medium

**ID:** CA-003
**Location:** `game/strategy/data/fleet.py` (entire module)
**Issue:** Fleet is imported by 38 files across strategy engines, validators, UI screens, facades, and DTOs. It contains OrderType enum, Order class, and Fleet class all in one module. Any change to Fleet's interface has a very wide blast radius.
**Impact:** Changes to Fleet (e.g., adding/removing an order type, changing the fleet interface) require verification across 38 files. This makes refactoring Fleet risky and slow...

---

### 6. MAJOR: Ship entity at 857 lines with 32 importers
**ID:** CA-004
**Agent:** Coupling Analyst
**Location:** `game/simulation/entities/ship.py`
**Effort:** Complex

**ID:** CA-004
**Location:** `game/simulation/entities/ship.py` (entire module)
**Issue:** Ship is the largest single-class file at 857 lines with 32 importers. It serves as a data container, stat calculator, combat participant, and serialization target all in one class.
**Impact:** High fan-in + large file size = high risk of merge conflicts and unintended side effects when modifying Ship behavior. Testing requires loading the full Ship class even when only a subset of its functionality is need...

---

### 7. MAJOR: Galaxy class is a bidirectional coupling hub
**ID:** CA-005
**Agent:** Coupling Analyst
**Location:** `game/strategy/data/galaxy.py`
**Effort:** Medium

**ID:** CA-005
**Location:** `game/strategy/data/galaxy.py` (entire module)
**Issue:** Galaxy has both high fan-out (19 modules) and high fan-in (20 modules), giving it an instability of 0.49. This means it's equally likely to be affected by changes in its dependencies as it is to cause ripple effects to its dependents. It imports 16 modules at top level including generators, spatial indexes, and data classes.
**Impact:** Galaxy acts as a coupling crossroads: changes to ANY of its 19 dependencie...

---

### 8. MAJOR: `game.strategy.data.fleet` is the most deferred module in the codebase
**ID:** IIA-001
**Agent:** Import Inventory Analyst
**Location:** `Unknown`
**Effort:** Medium

**ID:** IIA-001
**Location:** 18 inline imports across 6 files:
- `game/strategy/engine/command_handlers.py` (11 occurrences)
- `game/strategy/data/empire.py`
- `game/strategy/services/action_time_resolver.py` (3 occurrences)
- `game/strategy/data/fleet_capability_calculator.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/strategy_build_queue_manager.py`

**Issue:** `FleetOrder` and `OrderType` from `game.strategy.data.fleet` are imported inline 11 times in `command_handlers.py...

---

### 9. MAJOR: `game.strategy.engine.turn_engine` uses factory-pattern deferred imports for all sub-engines
**ID:** IIA-002
**Agent:** Import Inventory Analyst
**Location:** `game/strategy/engine/turn_engine.py`
**Effort:** Simple

**ID:** IIA-002
**Location:** `game/strategy/engine/turn_engine.py` lines 155-287 (13 inline imports)

**Issue:** `TurnEngine.__init__` lazily creates each sub-engine (FleetMovementEngine, ProductionEngine, FleetOrderProcessor, ConflictResolutionEngine, ResourceManagementEngine, PopulationEngine, ResupplyEngine, HarvestingEngine, MaintenanceEngine, ActionExecutionEngine, EnvironmentalHazardEngine) inside conditional `if self._xxx is None:` blocks, importing each engine module inline. This is by ...

---

### 10. MAJOR: `game.simulation.components.abilities.weapons.py` imports formula_system 7 times
**ID:** IIA-003
**Agent:** Import Inventory Analyst
**Location:** `game/simulation/components/abilities/weapons.py`
**Effort:** Simple

**ID:** IIA-003
**Location:** `game/simulation/components/abilities/weapons.py` lines 63, 81, 96, 132, 140, 148, 209

**Issue:** `safe_evaluate_math_formula` from `game.simulation.formula_system` is imported inline 7 separate times within the `WeaponAbility.__init__` and `sync_data` methods. Each conditional branch (`if isinstance(raw_damage, str) and raw_damage.startswith('=')`) repeats the import.

**Impact:** Code duplication. The same import appears in every branch that handles formula strin...

---


## Findings by Severity

### Critical (3)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CA-001 | TurnEngine has 15 deferred imports -- fr | `game/strategy/engine/turn_engi` | Medium |
| RS-001 | OrderType/FleetOrder in monolithic fleet | `game/strategy/data/fleet.py:20` | Medium |
| RS-002 | command_handlers.py has 16 deferred impo | `game/strategy/engine/command_h` | Simple |

### Major (15)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CA-002 | StrategyBuildQueueManager duplicates def | `game/ui/screens/strategy_build` | Simple |
| CA-003 | Fleet data model is a coupling bottlenec | `game/strategy/data/fleet.py` | Medium |
| CA-004 | Ship entity at 857 lines with 32 importe | `game/simulation/entities/ship.` | Complex |
| CA-005 | Galaxy class is a bidirectional coupling | `game/strategy/data/galaxy.py` | Medium |
| IIA-001 | `game.strategy.data.fleet` is the most d | `Unknown` | Medium |
| IIA-002 | `game.strategy.engine.turn_engine` uses  | `game/strategy/engine/turn_engi` | Simple |
| IIA-003 | `game.simulation.components.abilities.we | `game/simulation/components/abi` | Simple |
| IIA-005 | `game.core.registry` deferred in 12 file | `Unknown` | Complex |
| IIA-006 | Strategy data layer has extensive intern | `Unknown` | Complex |
| IIA-007 | UI screens have 128 inline imports, domi | `game/ui/screens/` | Complex |
| RS-003 | UI files unnecessarily defer command imp | `game/ui/screens/strategy_fleet` | Simple |
| RS-004 | strategy_build_queue_manager.py bypasses | `game/ui/screens/strategy_build` | Simple |
| RS-005 | action_time_resolver.py wraps OrderType  | `game/strategy/services/action_` | Simple |
| RS-006 | FleetOrder.to_dict() imports Planet at r | `game/strategy/data/fleet.py:78` | Medium |
| RS-007 | fleet_capability_calculator.py uses serv | `game/strategy/data/fleet_capab` | Medium |

### Minor (11)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CA-006 | WorkshopScreen has 24 top-level imports  | `game/ui/screens/workshop_scree` | Simple |
| CA-007 | app.py has 32 fan-out as application roo | `game/app.py:1-60` | N |
| CA-008 | protocols.py at 952 lines is the largest | `game/core/protocols.py` | Medium |
| CA-009 | Deferred imports mask potential startup  | `game/strategy/engine/game_sess` | Simple |
| IIA-004 | 45 redundant inline imports duplicate to | `Unknown` | Simple |
| IIA-009 | `game/simulation/components/component.py | `game/simulation/components/com` | Simple |
| RS-008 | Inconsistent command import patterns acr | `Unknown` | Simple |
| RS-009 | fleet.py's trigger_speed_recalculation() | `game/strategy/data/fleet.py:19` | Simple |
| RS-010 | ship_instance.py has 3 documented cross- | `game/strategy/data/ship_instan` | N |
| RS-011 | fleet_report_filters.py has 4 intentiona | `game/ui/screens/fleet_report_f` | Simple |
| RS-012 | fleet_data_source.py has 4 intentional l | `game/ui/screens/fleet_data_sou` | Simple |

### Info (6)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CA-010 | Simulation adapter correctly uses deferr | `game/strategy/adapters/simulat` | N |
| CA-011 | No actual circular dependencies detected | `Unknown` | Simple |
| IIA-008 | app.py has 20 inline imports -- intentio | `game/app.py` | N |
| IIA-010 | Conditional/factory imports in turn_engi | `Unknown` | Simple |
| RS-013 | app.py has 14 deferred imports for lazy  | `game/app.py:123, 245, 246, 261` | N |
| RS-014 | No linting infrastructure exists | `Unknown` | Medium |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Coupling Analyst Report](findings/coupling_analyst_report.md)
- [Import Inventory Analyst Report](findings/import_inventory_analyst_report.md)
- [Remediation Strategist Report](findings/remediation_strategist_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 35 |
| Critical | 3 |
| Major | 15 |
| Minor | 11 |
| Info | 6 |
| Agents Used | 3 |

---
*Report generated: 2026-02-27 21:39*
