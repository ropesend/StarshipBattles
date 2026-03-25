# Review Report: 2026-03-24_200858_general_duplication-consolidation-full-codebase

## Metadata
- **Date:** 2026-03-24
- **Type:** General Review
- **Description:** Find all duplicated functionality across 110K LOC vibe-coded codebase
- **Agents Used:** 25

## Executive Summary
- **Total Findings:** 97
- **Critical:** 0 | **Major:** 26 | **Minor:** 71 | **Info:** 0
- **Overall Assessment:** Needs Improvement

### Validation Summary
- **Original Findings:** 114
- **Confirmed:** 97 | **Downgraded:** 17 | **Rejected:** 17
- **Rejection Rate:** 14.9%
- **Findings Without Verdict:** 0

## Priority Findings (Top 10)

### 1. MAJOR: `_has_attrs` Helper Duplicated Across 3
**ID:** DUP-CEA-001
**Agent:** Validated
**Location:** `game/core/protocols.py:694`
**Effort:** Simple

**Location:** `game/core/protocols.py:694`

---

### 2. MAJOR: Firing Arc Check Logic Duplicated Across
**ID:** DUP-XL-001
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Simple

**Location:** `Unknown`

---

### 3. MAJOR: Compact Number Formatting (K/M Suffixes)
**ID:** DUP-XL-002
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Simple

**Location:** `Unknown`

---

### 4. MAJOR: ShipFactory Lazy Initialization Copy-Pas
**ID:** DUP-XL-003
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Simple

**Location:** `Unknown`

---

### 5. MAJOR: Repeated Scrollable Panel Pattern (Scrol
**ID:** DUP-PAT-001
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Medium

**Location:** `Unknown`

---

### 6. MAJOR: Serializable Data Classes Without Shared
**ID:** DUP-PAT-002
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Complex

**Location:** `Unknown`

---

### 7. MAJOR: Screen/Scene Classes Without Shared Base
**ID:** DUP-PAT-005
**Agent:** Validated
**Location:** `Unknown`
**Effort:** Medium

**Location:** `Unknown`

---

### 8. MAJOR: ToHitAttackModifier and ToHitDefenseModi
**ID:** DUP-CMP-001
**Agent:** Validated
**Location:** `abilities/defense.py:53-97`
**Effort:** Simple

**Location:** `abilities/defense.py:53-97`

---

### 9. MAJOR: Duplicated Physics Formulas (acceleratio
**ID:** DUP-SIM-001
**Agent:** Validated
**Location:** `ship_stats.py:237-241`
**Effort:** Simple

**Location:** `ship_stats.py:237-241`

---

### 10. MAJOR: Hull Auto-Equip Logic Duplicated in __in
**ID:** DUP-SIM-002
**Agent:** Validated
**Location:** `ship.py:78-88`
**Effort:** Simple

**Location:** `ship.py:78-88`

---


## Findings by Severity

### Major (26)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-CEA-001 | `_has_attrs` Helper Duplicated Across 3 | `game/core/protocols.py:694` | Simple |
| DUP-XL-001 | Firing Arc Check Logic Duplicated Across | `Unknown` | Simple |
| DUP-XL-002 | Compact Number Formatting (K/M Suffixes) | `Unknown` | Simple |
| DUP-XL-003 | ShipFactory Lazy Initialization Copy-Pas | `Unknown` | Simple |
| DUP-PAT-001 | Repeated Scrollable Panel Pattern (Scrol | `Unknown` | Medium |
| DUP-PAT-002 | Serializable Data Classes Without Shared | `Unknown` | Complex |
| DUP-PAT-005 | Screen/Scene Classes Without Shared Base | `Unknown` | Medium |
| DUP-CMP-001 | ToHitAttackModifier and ToHitDefenseModi | `abilities/defense.py:53-97` | Simple |
| DUP-SIM-001 | Duplicated Physics Formulas (acceleratio | `ship_stats.py:237-241` | Simple |
| DUP-SIM-002 | Hull Auto-Equip Logic Duplicated in __in | `ship.py:78-88` | Simple |
| DUP-SIM-003 | Component Addition Boilerplate Duplicate | `ship.py:502-531` | Medium |
| DUP-SYS-002 | Duplicate `run_ticks` Loop Implementatio | `battle_controller.py:287-310` | Medium |
| DUP-SYS-004 | Repeated Team-Alive Counting in BattleEn | `systems/battle_engine.py:520-5` | Simple |
| DUP-SD-01 | Duplicated Companion Star Generation Log | `stars.py:445-550` | Simple |
| DUP-SD-02 | Duplicated Planet Registration (register | `galaxy_entity_registry.py:34-5` | Simple |
| DUP-SE-001 | Duplicated `_setup_mission_move` vs `add | `command_handlers.py:30-79` | Simple |
| DUP-SE-002 | Duplicated Combat Event Logging in `_res | `conflict_resolution_engine.py:` | Simple |
| DUP-UIW-001 | Duplicated Portrait Loading and Ship Cla | `game/ui/panels/design_report_p` | Medium |
| DUP-UIW-003 | Duplicated HP/Damage Color Threshold Fun | `game/ui/panels/ship_stats_rend` | Simple |
| DUP-UIW-005 | Duplicate Placeholder Portrait Generatio | `game/ui/panels/design_report_p` | Simple |
| DUP-SCR-001 | Column Toggle Sidebar Pattern Duplicated | `Unknown` | Simple |
| DUP-SCR-004 | Selection Window Pattern Duplicated Acro | `Unknown` | Medium |
| DUP-SCR-005 | Star/Planet Info Formatting Duplicated i | `Unknown` | Simple |
| DUP-SCR-008 | `get_column_value` / `_extract_value` Lo | `Unknown` | Simple |
| DUP-SCR-009 | Mass Earth Constant Duplicated 4+ Times | `Unknown` | Simple |
| DUP-UIS-001 | Repeated Registry Provider Null-Check + | `game/ui/services/vehicle_class` | Simple |

### Minor (71)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-PAT-003 | Custom-Drawn Panel Components Without Sh | `Unknown` | Simple |
| DUP-PAT-004 | Sidebar Component Pattern Without Shared | `Unknown` | Simple |
| DUP-CMP-002 | EmissiveArmor duplicates ToHitAttackModi | `abilities/defense.py:100-117` | Simple |
| DUP-CMP-003 | ResourceConsumption, ResourceStorage, Re | `abilities/resources.py:10-230` | Medium |
| DUP-SYS-001 | Three-Layer Passthrough Delegation Chain | `battle_controller.py:523-538` | Complex |
| DUP-SYS-003 | Two Different Classes Named `BattleConfi | `game/core/config.py:111` | Simple |
| DUP-SD-03 | Repeated HexCoord Deserialization Error | `planet.py:296-309` | Simple |
| DUP-SS-01 | Population Extraction Logic Duplicated W | `game/strategy/services/cargo_t` | Simple |
| DUP-SS-02 | Superweapon Validation Methods Share Rep | `game/strategy/validation/super` | Simple |
| DUP-UIW-002 | Duplicated Resource Icon Loading | `game/ui/panels/build_queue_por` | Simple |
| DUP-SCR-002 | VirtualTable Refresh Boilerplate Duplica | `Unknown` | Simple |
| DUP-SCR-003 | Mouse Wheel Scroll Handling Duplicated i | `Unknown` | Simple |
| DUP-SCR-006 | Facade-or-Session Command Dispatch Patte | `Unknown` | Simple |
| DUP-SCR-007 | Data Source Classes Share Identical Boil | `Unknown` | Medium |
| DUP-SCR-010 | Screenshot Handling Pattern Duplicated | `Unknown` | Simple |
| DUP-UIS-002 | Parallel _get_provider() / _get_registri | `game/ui/services/vehicle_class` | Medium |
| DUP-CEA-002 | `TICK_DURATION` Class Constants Duplicat | `game/ai/behaviors.py:192` | Simple |
| DUP-CEA-003 | `SimulationConstants.TICKS_PER_SECOND` v | `game/core/constants.py:65` | Simple |
| DUP-CEA-005 | Inline Angle Normalization in `projectil | `game/simulation/entities/proje` | Simple |
| DUP-CEA-006 | `quickstart_builder.py` Uses Raw `json.l | `game/strategy/quickstart_build` | Simple |
| DUP-XL-005 | HP-to-Color Mapping Duplicated in Two UI | `Unknown` | Simple |
| DUP-XL-006 | Radiation Formatting Duplicated with Fal | `Unknown` | Simple |
| DUP-XL-007 | `angle_to_target` via `math.atan2` Inlin | `Unknown` | Simple |
| DUP-XL-008 | `_format_value` Implemented Independentl | `Unknown` | Medium |
| DUP-XL-009 | `replace('_', ' ').title()` Pattern Repe | `Unknown` | Simple |
| DUP-PAT-006 | UIWindow Subclass Initialization Pattern | `Unknown` | Simple |
| DUP-PAT-007 | Selection Window Pattern (Fleet/Planet/S | `Unknown` | Simple |
| DUP-PAT-008 | InputHandler Classes Without Shared Inte | `Unknown` | Simple |
| DUP-PAT-009 | Renderer Classes Without Shared Interfac | `Unknown` | Simple |
| DUP-PAT-010 | FilterManager Classes with Parallel Stru | `Unknown` | Medium |
| DUP-PAT-011 | Race Configuration Panel Pattern | `Unknown` | Simple |
| DUP-PAT-012 | Value Formatting Methods Scattered Acros | `Unknown` | Simple |
| DUP-CMP-005 | WeaponAbility __init__ and sync_data bot | `abilities/weapons.py:51-148` | Simple |
| DUP-CMP-006 | CargoStorage duplicates ResourceStorage | `abilities/cargo.py:14-79` | Medium |
| DUP-CMP-007 | EmpireStorageAbility duplicates Resource | `abilities/harvester.py:46-93` | Medium |
| DUP-CMP-008 | apply_modifier_effects duplicates _apply | `modifiers.py:15-49` | Simple |
| DUP-SIM-004 | `_has_attrs` Duck Typing Helper Duplicat | `interfaces/ability_protocols.p` | Simple |
| DUP-SIM-005 | `max_mass_budget` Lookup Repeated 3 Time | `ship.py:103` | Simple |
| DUP-SIM-006 | Overlapping Ability Aggregation APIs (ge | `ship.py:617-633` | Medium |
| DUP-SIM-007 | `cached_summary` Property Exists on Both | `ship.py:533-536` | Simple |
| DUP-SIM-008 | Validator Helper Calls validate_design 3 | `ship_validator_helper.py:44` | Simple |
| DUP-SIM-009 | Modifier Service Late Import and Creatio | `ship.py:522-525` | Simple |
| DUP-SIM-010 | Ship.layers_dict Property Duplicates Ser | `ship.py:800-815` | Simple |
| DUP-SYS-007 | State Capture Duplication Between Battle | `battle_controller.py:206-212` | Simple |
| DUP-SYS-008 | Repeated "No Active Battle" Guard Patter | `services/battle_service.py:115` | Simple |
| DUP-SD-06 | Duplicated `_generate_mass` in PlanetGen | `planet_gen.py:197-240` | Simple |
| DUP-SD-07 | Repeated `to_dict`/`from_dict` Serializa | `Unknown` | Complex |
| DUP-SD-09 | Duplicated `occupied_hexes` Property Pat | `stars.py:116-127` | Simple |
| DUP-SD-10 | `_facility_is_shipyard` Wrapper in build | `build_queue_source.py:114-126` | Simple |
| DUP-SE-003 | Duplicated `_spawn_complex` and `_spawn_ | `production_engine.py:595-655` | Medium |
| DUP-SE-004 | Duplicated `_spawn_ship` and `_spawn_fle | `production_engine.py:657-736` | Simple |
| DUP-SE-005 | Duplicated Fleet Iteration + Empire Iter | `Unknown` | N |
| DUP-SE-006 | Duplicated `process_join_fleet` Merge+Ev | `fleet_order_processor.py:79-13` | Simple |
| DUP-SE-007 | Duplicated Registries Resolution Pattern | `game_session.py:86-96` | Simple |
| DUP-SE-008 | Duplicated `session.turn_engine._registr | `superweapon_command_handlers.p` | Simple |
| DUP-SE-009 | Backward Compatibility Alias `process_en | `fleet_order_processor.py:645-6` | Simple |
| DUP-SS-04 | Name Slugification Functions | `game/strategy/systems/race_lib` | Simple |
| DUP-SS-06 | Loader Classes Share Structural Pattern | `game/strategy/generation/loade` | Medium |
| DUP-UIW-006 | Duplicate Image Scaling/Centering Logic | `game/ui/utils/pygame_utils.py:` | Simple |
| DUP-UIW-007 | Two Competing Section Header Patterns | `game/ui/utils/pygame_utils.py:` | Simple |
| DUP-UIW-008 | Duplicate Element Cleanup Patterns | `Unknown` | Medium |
| DUP-UIW-010 | Duplicate update_config/set_from_config | `race_environment_panel.py:450-` | Simple |
| DUP-UIW-011 | Colors Module Has Both Module-Level and | `game/ui/colors.py:8-9` | Medium |
| DUP-SCR-011 | Header Sort/Swap Handling Pattern Duplic | `Unknown` | Simple |
| DUP-SCR-012 | Kill Pattern with VirtualTable + Close C | `Unknown` | Medium |
| DUP-SCR-013 | Tri-State Filter Widget Polling Pattern | `Unknown` | Simple |
| DUP-SCR-014 | Population Formatting with K/M Suffixes | `Unknown` | Simple |
| DUP-SCR-015 | Sidebar Panel Layout Initialization Patt | `Unknown` | Medium |
| DUP-SCR-016 | `_get_column_value` Duplicated Between W | `Unknown` | Simple |
| DUP-UIS-004 | Ships Folder Path Construction Duplicate | `game/ui/services/ship_io.py:95` | Simple |
| DUP-UIS-005 | ShipIOAdapter is a Thin Pass-Through wit | `game/ui/services/ship_io_adapt` | Medium |


## Agent Reports

- [Core Engine Ai Report](findings/core_engine_ai_report.md)
- [Cross Layer Report](findings/cross_layer_report.md)
- [Pattern Abstraction Report](findings/pattern_abstraction_report.md)
- [Simulation Components Report](findings/simulation_components_report.md)
- [Simulation Entities Report](findings/simulation_entities_report.md)
- [Simulation Systems Report](findings/simulation_systems_report.md)
- [Strategy Data Report](findings/strategy_data_report.md)
- [Strategy Engine Report](findings/strategy_engine_report.md)
- [Strategy Services Report](findings/strategy_services_report.md)
- [Ui Components Report](findings/ui_components_report.md)
- [Ui Screens Report](findings/ui_screens_report.md)
- [Ui Services Report](findings/ui_services_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 97 |
| Critical | 0 |
| Major | 26 |
| Minor | 71 |
| Info | 0 |
| Agents Used | 25 |

---
*Report generated: 2026-03-24 20:24*
