# Review Report: 2026-02-27_141256_general_strategy-workshop-duplication

## Metadata
- **Date:** 2026-02-27 14:12
- **Type:** General Review
- **Description:** strategy-workshop-duplication
- **Agents Used:** 6

## Executive Summary
- **Total Findings:** 66
- **Critical:** 11 | **Major:** 28 | **Minor:** 24 | **Info:** 3
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Parallel Delegate/Manager Hierarchies
**ID:** AR-01
**Agent:** Architecture Consolidation
**Location:** `Unknown`
**Effort:** Complex

**ID:** AR-01
**Location:** Strategy: `fleet.py`, `fleet_battle_adapter.py`, `fleet_resource_aggregator.py`, `fleet_capability_calculator.py`, `ship_instance.py`, `ship_resource_manager.py`, `ship_cargo_manager.py`, `ship_display_formatter.py`. UI: `workshop_viewmodel.py`, `workshop_data_loader.py`, `workshop_event_router.py`, `workshop_data_reloader.py`, `builder/event_bus.py`, `builder/modifier_logic.py`, `builder/interaction_controller.py`.
**Issue:** Both layers independently implement extra...

---

### 2. CRITICAL: Layer Iteration Pattern - 19+ Duplications
**ID:** AR-02
**Agent:** Architecture Consolidation
**Location:** `Unknown`
**Effort:** Medium

**ID:** AR-02
**Location:** Strategy: `ship_instance.py`, `design_metadata.py`, `ship_stats_calculator.py`, multiple engines. Simulation: `ship.py`, `ship_serialization.py`, `ship_validator.py`. UI: `stats_config.py`, `layer_panel.py`, `weapons_viewmodel.py`, `design_stats_panel.py`.
**Issue:** Core pattern for iterating ship layers and components appears 19+ times with inconsistent format handling.
**Impact:** Bug fixes must be applied in 19+ locations. Different error handling per location.
**...

---

### 3. CRITICAL: Design Metadata Calculations Duplicated Across Layers
**ID:** CQ-80
**Agent:** Cross Layer Duplication
**Location:** `game/strategy/data/design_metadata.py:168-224`
**Effort:** Simple

**ID:** CQ-80
**Location:** `game/strategy/data/design_metadata.py:168-224` and `game/simulation/entities/ship.py:608-614`
**Issue:** DesignMetadata contains two separate implementations for calculating combat power and resource costs - one working on raw design dict, one on Ship object. Builder UI implicitly depends on these.
**Impact:** If calculations change, design library metadata may diverge from actual ship stats.
**Recommendation:** Document DesignMetadata as canonical source. Add contra...

---

### 4. CRITICAL: Design Data Loading Split Between Layers
**ID:** CQ-81
**Agent:** Cross Layer Duplication
**Location:** `game/strategy/systems/design_library.py:190-221`
**Effort:** Medium

**ID:** CQ-81
**Location:** `game/strategy/systems/design_library.py:190-221` and `game/ui/services/design_loader_adapter.py:52-75`
**Issue:** Two separate code paths load designs. Strategy returns raw dict, UI creates Ship object from dict. Both use SimulationDesignLoader internally but with different assumptions.
**Impact:** Workshop save/load cycle may not be symmetric if paths diverge. UI adapter duplicates strategy layer's responsibility.
**Recommendation:** Make DesignLibrary the single so...

---

### 5. CRITICAL: Parallel Cargo Operation Patterns in Fleet vs Ship
**ID:** CQ-01
**Agent:** Strategy Fleet Ships
**Location:** `game/strategy/data/fleet_resource_aggregator.py:263-313`
**Effort:** Medium

**ID:** CQ-01
**Location:** `game/strategy/data/fleet_resource_aggregator.py:263-313` and `game/strategy/data/ship_cargo_manager.py:69-117`
**Issue:** Both `FleetResourceAggregator` and `ShipCargoManager` implement identical cargo loading/unloading patterns with the same business logic structure: check amount validity, calculate space available, use min() to cap at limits, update dict and return actual amount.
**Impact:** Changes to cargo transfer logic must be updated in two places, risking div...

---

### 6. CRITICAL: Dual Implementation of Resource Consumption Verification
**ID:** CQ-02
**Agent:** Strategy Fleet Ships
**Location:** `game/strategy/data/fleet_resource_aggregator.py:47-97`
**Effort:** Medium

**ID:** CQ-02
**Location:** `game/strategy/data/fleet_resource_aggregator.py:47-97` and `game/strategy/data/fleet_resource_aggregator.py:115-162`
**Issue:** `has_resources_for_movement()` and `has_resources_for_warp()` implement virtually identical verification loops. Same pattern repeats for `consume_movement_resources()` and `consume_warp_resources()`. Four methods are nearly identical except for which cost getter is called.
**Impact:** Four methods with near-identical logic create high mainte...

---

### 7. CRITICAL: Layer Iteration Pattern Duplication
**ID:** CQ-20
**Agent:** Strategy Galaxy Economy
**Location:** `game/strategy/engine/production_engine.py:78-83`
**Effort:** Simple

**ID:** CQ-20
**Location:** `game/strategy/engine/production_engine.py:78-83`, `game/strategy/engine/maintenance_engine.py:55-72`, `game/strategy/engine/harvesting_engine.py:150+`, `game/strategy/engine/empire_economy_calculator.py:155-162`, `game/strategy/data/planet.py:86-98`, `game/strategy/data/planet.py:144-153`
**Issue:** Nearly identical layer iteration logic appears in 6+ locations with inconsistent format handling (dict vs list).
**Impact:** Code duplication across 6+ files. Inconsisten...

---

### 8. CRITICAL: Resource Cost Calculation Duplication
**ID:** CQ-21
**Agent:** Strategy Galaxy Economy
**Location:** `game/strategy/engine/maintenance_engine.py:38-78`
**Effort:** Medium

**ID:** CQ-21
**Location:** `game/strategy/engine/maintenance_engine.py:38-78`, `game/strategy/engine/production_engine.py:61-85`, `game/strategy/engine/empire_economy_calculator.py:134-183`
**Issue:** Three independent implementations of "sum all component resource_cost values across layers". MaintenanceEngine handles both dict/list formats while ProductionEngine only handles dict.
**Impact:** Risk of economic bugs where costs differ between systems.
**Recommendation:** Create shared `DesignCos...

---

### 9. CRITICAL: Identical Filter Button Creation Pattern in Multiple Panels
**ID:** CQ-60
**Agent:** Workshop Builder
**Location:** `game/ui/screens/builder/weapons_panel.py:86-111`
**Effort:** Medium

**ID:** CQ-60
**Location:** `game/ui/screens/builder/weapons_panel.py:86-111` and `game/ui/screens/builder/left_panel.py:63-79`
**Issue:** Both panels create button arrays with nearly identical pixel layout calculations and state prefix updates (`"[x] "` / `"[ ] "`).
**Impact:** Changes to button sizing, spacing, or styling require updates in multiple locations.
**Recommendation:** Extract common `ButtonGridLayout` helper that takes button specs and returns positioned buttons.
**Effort:** Medium

---

### 10. CRITICAL: Duplicated Modifier Range/Slider Logic in ModifierControlRow
**ID:** CQ-61
**Agent:** Workshop Builder
**Location:** `game/ui/screens/builder/modifier_row.py:236-246`
**Effort:** Simple

**ID:** CQ-61
**Location:** `game/ui/screens/builder/modifier_row.py:236-246` and `modifier_row.py:315-323`
**Issue:** Slider enable/disable and range update appears in both `update()` and `handle_event()`. Min/max calculation and clamping logic duplicated.
**Impact:** If min/max constraints change, logic must be updated in 3+ places.
**Recommendation:** Extract `_get_local_bounds()` method for consistent min/max handling.
**Effort:** Simple

---


## Findings by Severity

### Critical (11)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-01 | Parallel Delegate/Manager Hierarchies | `Unknown` | Complex |
| AR-02 | Layer Iteration Pattern - 19+ Duplicatio | `Unknown` | Medium |
| CQ-80 | Design Metadata Calculations Duplicated  | `game/strategy/data/design_meta` | Simple |
| CQ-81 | Design Data Loading Split Between Layers | `game/strategy/systems/design_l` | Medium |
| CQ-01 | Parallel Cargo Operation Patterns in Fle | `game/strategy/data/fleet_resou` | Medium |
| CQ-02 | Dual Implementation of Resource Consumpt | `game/strategy/data/fleet_resou` | Medium |
| CQ-20 | Layer Iteration Pattern Duplication | `game/strategy/engine/productio` | Simple |
| CQ-21 | Resource Cost Calculation Duplication | `game/strategy/engine/maintenan` | Medium |
| CQ-60 | Identical Filter Button Creation Pattern | `game/ui/screens/builder/weapon` | Medium |
| CQ-61 | Duplicated Modifier Range/Slider Logic i | `game/ui/screens/builder/modifi` | Simple |
| CQ-62 | Tooltip Detection Logic Duplicated in We | `game/ui/screens/builder/weapon` | Medium |

### Major (28)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-03 | DTO vs Summary vs Info - Three Parallel  | `Unknown` | Major |
| AR-04 | ValidationService vs Strategy Validators | `Unknown` | Major |
| AR-05 | Adapter/Service Pattern Proliferation | `Unknown` | Complex |
| AR-06 | Similar Calculation Patterns Without Sha | `Unknown` | Major |
| AR-07 | Data Container Inconsistency | `Unknown` | Simple |
| CQ-82 | Resource Cost Calculation Duplicated Acr | `game/strategy/engine/productio` | Medium |
| CQ-83 | Ship Display Formatting Located in Wrong | `game/strategy/data/ship_displa` | Complex |
| CQ-84 | Design Library Filtering Logic Partially | `game/strategy/systems/design_l` | Medium |
| CQ-03 | Repeated Component Iteration Pattern in  | `game/strategy/data/fleet_capab` | Simple |
| CQ-04 | Mirrored Resource Aggregation Between Fl | `game/strategy/data/fleet_resou` | Medium |
| CQ-05 | Display/Status Methods Split Between For | `game/strategy/data/ship_displa` | Simple |
| CQ-06 | Parallel Serialization/Deserialization P | `game/strategy/data/fleet.py:36` | Medium |
| CQ-22 | Deserialization Error Handling Pattern | `game/strategy/data/galaxy.py:1` | Medium |
| CQ-23 | Harvester/Storage Ability Extraction Dup | `game/strategy/engine/harvestin` | Medium |
| CQ-24 | Planet/Facility Resource Capacity Aggreg | `game/strategy/engine/harvestin` | Medium |
| CQ-40 | Mission Move Setup Logic Duplicated Acro | `superweapon_command_handlers.p` | Simple |
| CQ-41 | Fleet Resolution Pattern in 19 Command H | `Unknown` | Simple |
| CQ-42 | Path Stripping Logic Duplicated 4 Times | `game_session.py:178-179` | Simple |
| CQ-43 | Same-Location Movement Check Scattered A | `command_handlers.py:162, 190, ` | Simple |
| CQ-44 | Tick Interval Calculation Duplicated in  | `fleet_movement_engine.py:228-2` | Simple |
| CQ-45 | Planet Existence/Location Check Duplicat | `command_handlers.py:137-139, 2` | Simple |
| CQ-63 | Repeated UI Panel Bootstrap Pattern | `game/ui/screens/builder/right_` | Simple |
| CQ-64 | Button Creation for Modifier State Displ | `game/ui/screens/builder/modifi` | Simple |
| CQ-65 | Scrollable Container Setup in Three Pane | `layer_panel.py:81-88` | Simple |
| CQ-66 | Text Entry + Slider + Button Control Pat | `modifier_row.py:124-182` | Medium |
| CQ-67 | Enable/Disable Control Groups in Modifie | `modifier_row.py:236-257` | Simple |
| CQ-68 | Stat Row Display Pattern Duplicated in M | `design_stats_panel.py:33-100` | Medium |
| CQ-69 | Clear/Cleanup Pattern in Multiple Panels | `modifier_row.py:184-195` | Simple |

### Minor (24)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-08 | Formatting Function Duplication | `Unknown` | Simple |
| AR-09 | Event System Inconsistency | `Unknown` | Medium |
| AR-10 | Display ID Generation Not Centralized | `ship_display_formatter.py` | Simple |
| CQ-85 | Metadata Loading with Embedded Metadata  | `game/strategy/systems/design_l` | Simple |
| CQ-86 | Ship Stats Calculator Imports From Simul | `game/strategy/services/ship_st` | N |
| CQ-07 | Resource Cost Accumulation Pattern Repea | `game/strategy/data/fleet_resou` | Simple |
| CQ-08 | Repeated Effectiveness Calculation for C | `game/strategy/services/ship_st` | Complex |
| CQ-09 | FleetOrder Target Serialization Complexi | `game/strategy/data/fleet.py:75` | Medium |
| CQ-25 | Duplicate from_dict Validation Patterns | `game/strategy/data/galaxy.py:5` | Medium |
| CQ-26 | Similar Zone Registration Logic | `game/strategy/data/galaxy.py:2` | Simple |
| CQ-27 | Warp Point Index Rebuild Logic | `game/strategy/data/galaxy.py:2` | Simple |
| CQ-28 | Fuel Storage Ability Hardcoding | `game/strategy/data/planet.py:7` | Simple |
| CQ-46 | Superweapon Handler Structure Has Copy-P | `superweapon_command_handlers.p` | Medium |
| CQ-47 | Validation Result Error Message Inconsis | `Unknown` | Simple |
| CQ-48 | Moving Fleet Auto-Queueing Order Pattern | `command_handlers.py:159-164, 4` | Simple |
| CQ-49 | Log Message Structure Follows Repeated P | `Unknown` | Simple |
| CQ-50 | Empire Finding Logic in TransferCommandH | `command_handlers.py:410-415` | Simple |
| CQ-70 | Offset/Position Constants Scattered Acro | `Unknown` | Simple |
| CQ-71 | Emoji/Unicode in Button/Label Text | `preset_ui.py:34,57,67` | Simple |
| CQ-72 | Color Reference Pattern | `Unknown` | Medium |
| CQ-73 | Layout Configuration Initialization Patt | `panel_layout_config.py:26-30` | Medium |
| CQ-74 | Event Bus Event Type Constants | `builder_utils.py:115-123` | Simple |
| CQ-75 | Service Injection Pattern Inconsistency | `detail_panel.py` | Medium |
| CQ-76 | Error Handling Pattern Duplication | `stats_config.py:368-379, 385-3` | Simple |

### Info (3)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-11 | Cross-Layer Iteration - Missing Componen | `Unknown` | Simple |
| CQ-87 | Multiple Validation Paths for Ships | `game/simulation/entities/ship.` | N |
| CQ-51 | Order Type Categorization Properly Centr | `fleet.py:39-61` | N |


## Agent Reports

- [Architecture Consolidation Report](findings/architecture_consolidation_report.md)
- [Cross Layer Duplication Report](findings/cross_layer_duplication_report.md)
- [Strategy Fleet Ships Report](findings/strategy_fleet_ships_report.md)
- [Strategy Galaxy Economy Report](findings/strategy_galaxy_economy_report.md)
- [Strategy Session Turns Report](findings/strategy_session_turns_report.md)
- [Workshop Builder Report](findings/workshop_builder_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 66 |
| Critical | 11 |
| Major | 28 |
| Minor | 24 |
| Info | 3 |
| Agents Used | 6 |

---
*Report generated: 2026-02-27 14:26*
