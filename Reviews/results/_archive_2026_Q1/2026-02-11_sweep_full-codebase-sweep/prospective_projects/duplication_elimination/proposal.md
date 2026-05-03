# Prospective Project: Duplication Elimination

## Overview
This project eliminates all identified code duplication across the codebase: copy-pasted logic, parallel implementations of the same algorithm, duplicated utility functions, near-identical class implementations, and fragmented data loading patterns. It includes both precisely-located DUP findings and UNK (unknown location) findings from the simulation duplication sweep that identified structural duplication patterns requiring investigation. Eliminating duplication reduces bug surface area, ensures consistent behavior, and simplifies maintenance.

## Grouping Rationale
All 59 findings address the same fundamental problem: the same logic exists in multiple places. They share the same fix strategy (extract to a shared utility, delete duplicates, update callers) and often interact with each other (e.g., multiple duplication findings in the strategy engine touch overlapping files). The UNK-prefixed findings from the simulation duplication sweep describe structural patterns that require investigation before fixing, so grouping them here provides a research-then-fix workflow. The DUP and UNK types are a natural pair -- DUP findings have precise locations while UNK findings describe the same kind of problem but need location discovery first.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 59 total (9 Critical, 26 Major, 19 Minor, 5 Info)

## Suggested Execution Order
**Execute fourth** (Order 4), after architecture layer violations, in parallel with legacy cleanup. Some duplications exist because of layer violations (e.g., duplicated helper functions that could not be shared due to circular imports), so fixing layer violations first may naturally eliminate some duplication. The UNK findings require investigation time that can proceed in parallel with other cleanup work.

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-001 | Duplicated Resource Loading Logic (load_resources vs load_resources_data) | `game/core/resources.py:55-98` | Simple |
| UNK-01 | Physics formula duplication between ShipPhysicsMixin and movement | `Unknown` | Unknown |
| UNK-10 | Two parallel ability aggregation systems | `Unknown` | Unknown |
| DUP-STR-001 | Mission Command Handlers are Copy-Paste clones | `game/strategy/engine/superweap` | Simple |
| DUP-STR-002 | _calculate_maintenance_cost Duplicated Across modules | `game/strategy/engine/maintenan` | Simple |
| DUP-UI2-001 | Portrait Loading Logic Duplicated in 5+ locations | `game/ui/assets/ship_theme_mana` | Medium |
| DUP-UI2-002 | Ship Image Scaling Pipeline Duplicated Between renderers | `game/ui/renderer/game_renderer` | Simple |
| DUP-UI1-001 | BuildQueueScreen instantiation duplicated | `game/ui/screens/strategy_scree` | Simple |
| DUP-UI1-002 | Two separate ColumnManager classes with identical logic | `game/ui/screens/column_manager` | Medium |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-002 | StrategyMetadataService Uses Hand-Rolled singleton pattern | `game/core/strategy_metadata.py` | Simple |
| DUP-FND-003 | Repeated "Flee Away" Vector Pattern Across AI behaviors | `game/ai/behaviors.py:95-101` | Simple |
| DUP-FND-004 | Repeated Entity ID Fallback Pattern in AI combat utils | `game/ai/combat_utils.py:65` | Simple |
| DUP-FND-005 | Inline Angle Difference Calculation Instead of utility | `game/ai/controller.py:462` | Simple |
| UNK-02 | Hull auto-equip code duplicated between loaders | `Unknown` | Unknown |
| UNK-03 | Modifier application duplicated between systems | `Unknown` | Unknown |
| UNK-04 | Superweapon ability classes are nearly identical | `Unknown` | Unknown |
| UNK-05 | Turret arc lookup logic duplicated in Modifier and Ability | `Unknown` | Unknown |
| UNK-06 | BeamWeaponAbility.get_damage() duplicates base pattern | `Unknown` | Unknown |
| UNK-11 | Two independent formula evaluation systems | `Unknown` | Unknown |
| UNK-12 | Duplicate default stats dictionaries | `Unknown` | Unknown |
| UNK-14 | WeaponAbility.__init__ formula parsing redundancy | `Unknown` | Unknown |
| UNK-15 | Missile type checking uses inconsistent patterns | `Unknown` | Unknown |
| UNK-18 | Ship stat recalculation scattered across methods | `Unknown` | Unknown |
| UNK-19 | Component data loading spread across 4 files | `Unknown` | Unknown |
| DUP-STR-003 | _find_system_at_location Duplicated in Validation and Engine | `game/strategy/validation/super` | Simple |
| DUP-STR-004 | _get_harvester_info / _lookup_harvester_ duplicated | `game/strategy/engine/harvestin` | Simple |
| DUP-STR-005 | _get_storage_info / _lookup_storage_in_registries duplicated | `game/strategy/engine/harvestin` | Medium |
| DUP-STR-006 | _spawn_complex Duplicated Between Colony and Production | `game/strategy/engine/productio` | Simple |
| DUP-UI2-003 | Layer Color Constants Duplicated with Drawing Code | `game/ui/renderer/game_renderer` | Simple |
| DUP-UI2-004 | BattleUIService get_engine() Null-Check Pattern Repeated | `game/ui/services/battle_ui_ser` | Simple |
| DUP-UI2-005 | ShipThemeManager Internal Methods Repeat pattern | `game/ui/assets/ship_theme_mana` | Simple |
| DUP-UI1-003 | Screenshot capture and toast notification duplicated | `game/ui/screens/build_queue_sc` | Simple |
| DUP-UI1-004 | Resource display formatting duplicated between screens | `game/ui/screens/strategy_ui.py` | Simple |
| DUP-UI1-005 | Star system/star formatting duplicated between formatters | `game/ui/screens/strategy_detai` | Simple |
| DUP-UI1-006 | Event log window open methods duplicated | `game/ui/screens/strategy_windo` | Simple |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-006 | `_resolve_resource_path` Reimplements Paths utility | `game/core/resources.py:31-52` | Simple |
| DUP-FND-007 | Repeated Zero-Vector Guard Pattern in AI behaviors | `game/ai/behaviors.py:97-98` | Simple |
| DUP-FND-008 | AIController._get_hp_percent and _is_in_pdc_arc trivial wrappers | `game/ai/controller.py:269-273` | Simple |
| DUP-FND-009 | `load_data` Duplication Between StrategyManager and AI | `game/ai/strategy_manager.py:83` | Medium |
| UNK-07 | Ability constructor data-extraction pattern repeated | `Unknown` | Unknown |
| UNK-08 | Propulsion sync_data methods are near-identical | `Unknown` | Unknown |
| UNK-09 | ShipValidatorHelper calls validate_design in redundant pattern | `Unknown` | Unknown |
| UNK-13 | get_total_sensor_score and get_total_ecm_score are near-identical | `Unknown` | Unknown |
| UNK-16 | Resource endurance calculations in combat duplicated | `Unknown` | Unknown |
| UNK-17 | apply_modifier_effects partially duplicated | `Unknown` | Unknown |
| UNK-20 | Validation result handling duplicated between callers | `Unknown` | Unknown |
| DUP-STR-007 | Direct Superweapon Command Handlers Follow Copy-Paste template | `game/strategy/engine/superweap` | Medium |
| DUP-STR-008 | Fleet Lookup Pattern Duplicated in Command Handlers | `game/strategy/engine/command_h` | Simple |
| DUP-STR-009 | Superweapon Order Processing Has Repeated dispatch pattern | `game/strategy/engine/superweap` | Simple |
| DUP-UI2-006 | Lazy DI Provider Pattern in Services repeated | `game/ui/services/component_ser` | Simple |
| DUP-UI2-007 | Topdown Thumbnail Loading Reimplements Base pattern | `game/ui/screens/design_image_h` | Simple |
| DUP-UI1-007 | Thin wrapper/proxy methods in StrategyUI (fragmentation) | `game/ui/screens/strategy_ui.py` | Simple |
| DUP-UI1-008 | Population count formatting (K/M suffixes) duplicated | `game/ui/screens/strategy_detai` | Simple |
| DUP-UI1-009 | Window centering pattern repeated ~15 times | `game/ui/screens/strategy_scree` | Simple |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-FND-010 | Paths Class Maintains Both String and Path APIs | `game/core/paths.py:46-134` | Medium |
| UNK-21 | Persistence layer uses old Ship.from_dict pattern | `Unknown` | Unknown |
| DUP-STR-010 | Design Data Layer Iteration Pattern Used across strategy | `Unknown` | Medium |
| DUP-UI2-008 | Hardcoded Magic Color Tuples Throughout renderer | `Unknown` | Medium |
| DUP-UI1-010 | StrategyDetailFormatter._format_star_system repeated patterns | `game/ui/screens/strategy_detai` | N |

## Affected Files

**Core:**
- `game/core/paths.py`
- `game/core/resources.py`
- `game/core/strategy_metadata.py`

**AI:**
- `game/ai/behaviors.py`
- `game/ai/combat_utils.py`
- `game/ai/controller.py`
- `game/ai/strategy_manager.py`

**Simulation (UNK findings -- locations to be determined):**
- `game/simulation/components/abilities/` (multiple files)
- `game/simulation/entities/ship_physics_mixin.py`
- `game/simulation/entities/ability_aggregator.py`

**Strategy:**
- `game/strategy/engine/command_handlers.py`
- `game/strategy/engine/harvesting_engine.py`
- `game/strategy/engine/maintenance_engine.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `game/strategy/validation/superweapon_validator.py`

**UI:**
- `game/ui/assets/ship_theme_manager.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/column_manager.py`
- `game/ui/screens/design_image_handler.py`
- `game/ui/screens/strategy_detail_formatter.py`
- `game/ui/screens/strategy_screen.py`
- `game/ui/screens/strategy_ui.py`
- `game/ui/screens/strategy_window_manager.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/component_service.py`

## Effort Estimate
- **Simple tasks:** 29
- **Medium tasks:** 8
- **Complex tasks:** 0
- **Unknown (UNK findings):** 22
- **Overall scope:** Large (due to investigation needed for UNK findings)

## Overlap with Existing Projects
- **PROJ-108** (Duplication Elimination) - Direct overlap. This project was likely created from an earlier analysis. Should be merged or superseded.
- **PROJ-95** (Resource API Consistency and Clean-Sheet Conventions) - Partial overlap on resource loading duplication.

## Suggested Phases
1. **Phase 1: Investigation** - Locate all UNK findings (21 items with unknown locations). Determine exact file paths and line ranges. Some may turn out to be false positives or already resolved.
2. **Phase 2: Foundation and AI Deduplication** - Extract shared utilities for resource loading, AI vector/angle patterns, entity ID fallbacks.
3. **Phase 3: Simulation Deduplication** - Consolidate ability aggregation systems, formula evaluation, physics calculations, component data loading.
4. **Phase 4: Strategy Deduplication** - Extract shared helpers for command handlers, system lookups, harvester/storage info, spawn patterns.
5. **Phase 5: UI Deduplication** - Consolidate portrait loading, image scaling, screenshot patterns, formatting utilities, window centering helper.
