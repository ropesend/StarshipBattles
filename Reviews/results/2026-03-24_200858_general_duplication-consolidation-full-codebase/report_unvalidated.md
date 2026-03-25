# Review Report: 2026-03-24_200858_general_duplication-consolidation-full-codebase

## Metadata
- **Date:** 2026-03-24
- **Type:** General Review
- **Description:** Find all duplicated functionality across 110K LOC vibe-coded codebase
- **Agents Used:** 12

## Executive Summary
- **Total Findings:** 114
- **Critical:** 0 | **Major:** 45 | **Minor:** 69 | **Info:** 0
- **Overall Assessment:** Needs Improvement

## Priority Findings (Top 10)

### 1. MAJOR: `_has_attrs` Helper Duplicated Across 3 Protocol Modules
**ID:** DUP-CEA-001
**Agent:** Core Engine Ai
**Location:** `game/core/protocols.py:694`
**Effort:** Simple

**ID:** DUP-CEA-001
**Location:** `game/core/protocols.py:694`, `game/ai/protocols.py:174`, `game/simulation/interfaces/entity_protocols.py:480`, `game/simulation/interfaces/ability_protocols.py:315`
**Issue:** The exact same helper function is copy-pasted in 4 separate files:
```python
def _has_attrs(obj: Any, *attrs: str) -> bool:
    """Check if obj has all specified attributes (duck typing helper)."""
    return all(hasattr(obj, attr) for attr in attrs)
```
Each module defines its own privat...

---

### 2. MAJOR: Firing Arc Check Logic Duplicated Across AI and Simulation
**ID:** DUP-XL-001
**Agent:** Cross Layer
**Location:** `Unknown`
**Effort:** Simple

**ID:** DUP-XL-001
**Location:**
- `game/ai/combat_utils.py:219-229` (`is_in_pdc_arc` function)
- `game/simulation/components/abilities/weapons.py:218-245` (`WeaponAbility.check_firing_solution`)
- `game/simulation/combat/weapon_firing_system.py:251-256` (inline in seeker launch logic)

**Issue:** The same geometric pattern -- compute `comp_facing = (ship_angle + facing_angle) % 360`, compute `diff = (target_angle - comp_facing + 180) % 360 - 180`, check `abs(diff) <= firing_arc / 2` -- is imple...

---

### 3. MAJOR: Compact Number Formatting (K/M Suffixes) Reimplemented in 4+ UI Files
**ID:** DUP-XL-002
**Agent:** Cross Layer
**Location:** `Unknown`
**Effort:** Simple

**ID:** DUP-XL-002
**Location:**
- `game/ui/panels/planet_report_panel.py:311-318` (`_format_compact_number`)
- `game/ui/screens/empire_build_queue_formatter.py:185-192` (inline in function)
- `game/ui/screens/planet_list_filters.py:301-306` (inline)
- `game/ui/screens/strategy_detail_fmt.py:109-121` (inline, twice)

**Issue:** The same pattern -- check `>= 1_000_000` format as `M`, check `>= 1_000` format as `k`/`K`, else integer -- is copy-pasted across at least 4 UI files. There are minor inc...

---

### 4. MAJOR: ShipFactory Lazy Initialization Copy-Pasted Between UI Modules
**ID:** DUP-XL-003
**Agent:** Cross Layer
**Location:** `Unknown`
**Effort:** Simple

**ID:** DUP-XL-003
**Location:**
- `game/ui/screens/setup_data_io.py:24-40` (`_get_ship_factory`)
- `game/ui/screens/setup_screen.py:36-52` (`_get_ship_factory`)

**Issue:** Both files contain an identical `_get_ship_factory()` function with the same module-level `_ship_factory = None` singleton pattern, the same imports, the same `GameRegistries` construction from `get_default_registry_provider()`, and the same `ShipFactory(registry_provider=registries)` call. This is a textbook copy-paste.

**...

---

### 5. MAJOR: Entity Lookup 4-Layer Delegation Chain (Fleet/Planet by ID)
**ID:** DUP-XL-004
**Agent:** Cross Layer
**Location:** `Unknown`
**Effort:** Medium

**ID:** DUP-XL-004
**Location:**
- `game/strategy/facade/strategy_session_facade.py:82-93` (`_get_fleet_by_id` -> delegates to session)
- `game/strategy/engine/game_session.py:208-219` (`_get_fleet_by_id` -> delegates to galaxy)
- `game/strategy/data/galaxy.py:385-396` (`get_fleet_by_id` -> delegates to registry)
- `game/strategy/data/galaxy_entity_registry.py:145-154` (`get_fleet_by_id` -> actual lookup)

Same chain exists for `get_planet_by_id` (facade -> session -> galaxy -> registry) and `_g...

---

### 6. MAJOR: Repeated Scrollable Panel Pattern (Scroll State + Scrollbar Drawing + Mousewheel Handling)
**ID:** DUP-PAT-001
**Agent:** Pattern Abstraction
**Location:** `Unknown`
**Effort:** Medium

**ID:** DUP-PAT-001
**Location:**
- `game/ui/widgets/scrollable_json_panel.py` - `ScrollableJsonPanel`
- `game/ui/screens/test_lab/json_viewer.py` - `ScrollableJSONViewer`
- `game/ui/screens/test_lab/results_panel.py` - `ResultsPanel`
- `game/ui/screens/test_lab/test_run_details.py` - `TestRunDetailsPanel`
- `game/ui/screens/test_lab/dialogs.py` - (2 dialog classes)
- `game/ui/panels/modifier_impact_grid.py` - `ModifierImpactGrid`
- `game/ui/screens/builder/weapons_panel.py` - `WeaponsReportPane...

---

### 7. MAJOR: Serializable Data Classes Without Shared Base (to_dict/from_dict Pattern)
**ID:** DUP-PAT-002
**Agent:** Pattern Abstraction
**Location:** `Unknown`
**Effort:** Complex

**ID:** DUP-PAT-002
**Location:** 18 files with `to_dict() -> Dict` and 15 files with `from_dict(cls, ...)`:
- `game/strategy/data/fleet.py`, `empire.py`, `planet.py`, `stars.py`, `storm.py`, `ship_instance.py`, `design_metadata.py`, `race_config.py`, `galaxy.py`, `order_types.py`
- `game/strategy/engine/game_session.py`, `game_config.py`
- `game/strategy/events/event_log.py` (2 classes)
- `game/strategy/services/fleet_navigation_service.py`
- `game/simulation/battle_state.py` (5 classes)
- `gam...

---

### 8. MAJOR: Custom-Drawn Panel Components Without Shared Base (Test Lab)
**ID:** DUP-PAT-003
**Agent:** Pattern Abstraction
**Location:** `Unknown`
**Effort:** Simple

**ID:** DUP-PAT-003
**Location:**
- `game/ui/screens/test_lab/ship_panels.py` - `ShipPanel`, `TabbedShipPanel`, `ComponentPanel`
- `game/ui/screens/test_lab/results_panel.py` - `ResultsPanel`
- `game/ui/screens/test_lab/test_run_details.py` - `TestRunDetailsPanel`
- `game/ui/screens/test_lab/test_run_card.py` - `TestRunCard`
- `game/ui/screens/test_lab/json_viewer.py` - `ScrollableJSONViewer`
- `game/ui/screens/test_lab/component_dropdown.py` - `ComponentDropdown`

**Issue:** All 8 classes share...

---

### 9. MAJOR: Sidebar Component Pattern Without Shared Base
**ID:** DUP-PAT-004
**Agent:** Pattern Abstraction
**Location:** `Unknown`
**Effort:** Simple

**ID:** DUP-PAT-004
**Location:**
- `game/ui/screens/fleet_report_sidebar.py` - `FleetReportSidebar`
- `game/ui/screens/empire_build_queue_sidebar.py` - `EmpireBuildQueueSidebar`
- `game/ui/screens/event_log_sidebar.py` - `EventLogSidebar`

**Issue:** All three sidebars share this structural pattern:
1. Accept a `UIPanel` container, `manager`, and domain-specific state
2. Store `self.panel`, `self.manager`, and compute `self.sidebar_width`
3. Have `column_toggle_buttons: Dict[str, UIButton]` for...

---

### 10. MAJOR: Screen/Scene Classes Without Shared Base Implementation
**ID:** DUP-PAT-005
**Agent:** Pattern Abstraction
**Location:** `Unknown`
**Effort:** Medium

**ID:** DUP-PAT-005
**Location:** 12 screen classes and 3 scene classes:
- `game/ui/screens/battle_screen.py` - `BattleScreen`
- `game/ui/screens/setup_screen.py` - `BattleSetupScreen`
- `game/ui/screens/workshop_screen.py` - `DesignWorkshopScreen`
- `game/ui/screens/strategy_screen.py` - `StrategyScreen`
- `game/ui/screens/formation_editor.py` - `FormationEditorScreen`
- `game/ui/screens/build_queue_screen.py` - `BuildQueueScreen`
- `game/ui/screens/galaxy_test/screen.py` - `GalaxyTestScreen`
-...

---


## Findings by Severity

### Major (45)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-CEA-001 | `_has_attrs` Helper Duplicated Across 3  | `game/core/protocols.py:694` | Simple |
| DUP-XL-001 | Firing Arc Check Logic Duplicated Across | `Unknown` | Simple |
| DUP-XL-002 | Compact Number Formatting (K/M Suffixes) | `Unknown` | Simple |
| DUP-XL-003 | ShipFactory Lazy Initialization Copy-Pas | `Unknown` | Simple |
| DUP-XL-004 | Entity Lookup 4-Layer Delegation Chain ( | `Unknown` | Medium |
| DUP-PAT-001 | Repeated Scrollable Panel Pattern (Scrol | `Unknown` | Medium |
| DUP-PAT-002 | Serializable Data Classes Without Shared | `Unknown` | Complex |
| DUP-PAT-003 | Custom-Drawn Panel Components Without Sh | `Unknown` | Simple |
| DUP-PAT-004 | Sidebar Component Pattern Without Shared | `Unknown` | Simple |
| DUP-PAT-005 | Screen/Scene Classes Without Shared Base | `Unknown` | Medium |
| DUP-CMP-001 | ToHitAttackModifier and ToHitDefenseModi | `abilities/defense.py:53-97` | Simple |
| DUP-CMP-002 | EmissiveArmor duplicates ToHitAttackModi | `abilities/defense.py:100-117` | Simple |
| DUP-CMP-003 | ResourceConsumption, ResourceStorage, Re | `abilities/resources.py:10-230` | Medium |
| DUP-SIM-001 | Duplicated Physics Formulas (acceleratio | `ship_stats.py:237-241` | Simple |
| DUP-SIM-002 | Hull Auto-Equip Logic Duplicated in __in | `ship.py:78-88` | Simple |
| DUP-SIM-003 | Component Addition Boilerplate Duplicate | `ship.py:502-531` | Medium |
| DUP-SYS-001 | Three-Layer Passthrough Delegation Chain | `battle_controller.py:523-538` | Complex |
| DUP-SYS-002 | Duplicate `run_ticks` Loop Implementatio | `battle_controller.py:287-310` | Medium |
| DUP-SYS-003 | Two Different Classes Named `BattleConfi | `game/core/config.py:111` | Simple |
| DUP-SYS-004 | Repeated Team-Alive Counting in BattleEn | `systems/battle_engine.py:520-5` | Simple |
| DUP-SD-01 | Duplicated Companion Star Generation Log | `stars.py:445-550` | Simple |
| DUP-SD-02 | Duplicated Planet Registration (register | `galaxy_entity_registry.py:34-5` | Simple |
| DUP-SD-03 | Repeated HexCoord Deserialization Error  | `planet.py:296-309` | Simple |
| DUP-SD-04 | Structural Cargo Load/Unload Mirroring i | `fleet_resource_aggregator.py:2` | Simple |
| DUP-SE-001 | Duplicated `_setup_mission_move` vs `add | `command_handlers.py:30-79` | Simple |
| DUP-SE-002 | Duplicated Combat Event Logging in `_res | `conflict_resolution_engine.py:` | Simple |
| DUP-SS-01 | Population Extraction Logic Duplicated W | `game/strategy/services/cargo_t` | Simple |
| DUP-SS-02 | Superweapon Validation Methods Share Rep | `game/strategy/validation/super` | Simple |
| DUP-UIW-001 | Duplicated Portrait Loading and Ship Cla | `game/ui/panels/design_report_p` | Medium |
| DUP-UIW-002 | Duplicated Resource Icon Loading | `game/ui/panels/build_queue_por` | Simple |
| DUP-UIW-003 | Duplicated HP/Damage Color Threshold Fun | `game/ui/panels/ship_stats_rend` | Simple |
| DUP-UIW-004 | Slider+Label Boilerplate in Race Config  | `game/ui/panels/race_environmen` | Complex |
| DUP-UIW-005 | Duplicate Placeholder Portrait Generatio | `game/ui/panels/design_report_p` | Simple |
| DUP-SCR-001 | Column Toggle Sidebar Pattern Duplicated | `Unknown` | Simple |
| DUP-SCR-002 | VirtualTable Refresh Boilerplate Duplica | `Unknown` | Simple |
| DUP-SCR-003 | Mouse Wheel Scroll Handling Duplicated i | `Unknown` | Simple |
| DUP-SCR-004 | Selection Window Pattern Duplicated Acro | `Unknown` | Medium |
| DUP-SCR-005 | Star/Planet Info Formatting Duplicated i | `Unknown` | Simple |
| DUP-SCR-006 | Facade-or-Session Command Dispatch Patte | `Unknown` | Simple |
| DUP-SCR-007 | Data Source Classes Share Identical Boil | `Unknown` | Medium |
| DUP-SCR-008 | `get_column_value` / `_extract_value` Lo | `Unknown` | Simple |
| DUP-SCR-009 | Mass Earth Constant Duplicated 4+ Times | `Unknown` | Simple |
| DUP-SCR-010 | Screenshot Handling Pattern Duplicated | `Unknown` | Simple |
| DUP-UIS-001 | Repeated Registry Provider Null-Check +  | `game/ui/services/vehicle_class` | Simple |
| DUP-UIS-002 | Parallel _get_provider() / _get_registri | `game/ui/services/vehicle_class` | Medium |

### Minor (69)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| DUP-CEA-002 | `TICK_DURATION` Class Constants Duplicat | `game/ai/behaviors.py:192` | Simple |
| DUP-CEA-003 | `SimulationConstants.TICKS_PER_SECOND` v | `game/core/constants.py:65` | Simple |
| DUP-CEA-004 | `resources.py` Imports `json` Directly D | `game/core/resources.py:11` | Simple |
| DUP-CEA-005 | Inline Angle Normalization in `projectil | `game/simulation/entities/proje` | Simple |
| DUP-CEA-006 | `quickstart_builder.py` Uses Raw `json.l | `game/strategy/quickstart_build` | Simple |
| DUP-CEA-007 | Similar `_flee_direction` Logic Used in  | `game/ai/behaviors.py:71-85` | Simple |
| DUP-XL-005 | HP-to-Color Mapping Duplicated in Two UI | `Unknown` | Simple |
| DUP-XL-006 | Radiation Formatting Duplicated with Fal | `Unknown` | Simple |
| DUP-XL-007 | `angle_to_target` via `math.atan2` Inlin | `Unknown` | Simple |
| DUP-XL-008 | `_format_value` Implemented Independentl | `Unknown` | Medium |
| DUP-XL-009 | `replace('_', ' ').title()` Pattern Repe | `Unknown` | Simple |
| DUP-XL-010 | ComponentCacheManager Uses Manual Single | `Unknown` | Simple |
| DUP-PAT-006 | UIWindow Subclass Initialization Pattern | `Unknown` | Simple |
| DUP-PAT-007 | Selection Window Pattern (Fleet/Planet/S | `Unknown` | Simple |
| DUP-PAT-008 | InputHandler Classes Without Shared Inte | `Unknown` | Simple |
| DUP-PAT-009 | Renderer Classes Without Shared Interfac | `Unknown` | Simple |
| DUP-PAT-010 | FilterManager Classes with Parallel Stru | `Unknown` | Medium |
| DUP-PAT-011 | Race Configuration Panel Pattern | `Unknown` | Simple |
| DUP-PAT-012 | Value Formatting Methods Scattered Acros | `Unknown` | Simple |
| DUP-CMP-004 | Duplicate default stats dictionaries in  | `modifiers.py:120-157` | Simple |
| DUP-CMP-005 | WeaponAbility __init__ and sync_data bot | `abilities/weapons.py:51-148` | Simple |
| DUP-CMP-006 | CargoStorage duplicates ResourceStorage  | `abilities/cargo.py:14-79` | Medium |
| DUP-CMP-007 | EmpireStorageAbility duplicates Resource | `abilities/harvester.py:46-93` | Medium |
| DUP-CMP-008 | apply_modifier_effects duplicates _apply | `modifiers.py:15-49` | Simple |
| DUP-SIM-004 | `_has_attrs` Duck Typing Helper Duplicat | `interfaces/ability_protocols.p` | Simple |
| DUP-SIM-005 | `max_mass_budget` Lookup Repeated 3 Time | `ship.py:103` | Simple |
| DUP-SIM-006 | Overlapping Ability Aggregation APIs (ge | `ship.py:617-633` | Medium |
| DUP-SIM-007 | `cached_summary` Property Exists on Both | `ship.py:533-536` | Simple |
| DUP-SIM-008 | Validator Helper Calls validate_design 3 | `ship_validator_helper.py:44` | Simple |
| DUP-SIM-009 | Modifier Service Late Import and Creatio | `ship.py:522-525` | Simple |
| DUP-SIM-010 | Ship.layers_dict Property Duplicates Ser | `ship.py:800-815` | Simple |
| DUP-SYS-005 | Repeated DI Guard Clause Boilerplate (PR | `services/design_loader.py:52-5` | Simple |
| DUP-SYS-006 | Repeated List/Tuple Format Validation in | `battle_state.py:196-235` | Simple |
| DUP-SYS-007 | State Capture Duplication Between Battle | `battle_controller.py:206-212` | Simple |
| DUP-SYS-008 | Repeated "No Active Battle" Guard Patter | `services/battle_service.py:115` | Simple |
| DUP-SYS-009 | `BattleController.run_headless` Safety L | `battle_controller.py:281-282` | Simple |
| DUP-SD-05 | Constrained Mass Generation in Both Star | `stars.py:627-650` | Medium |
| DUP-SD-06 | Duplicated `_generate_mass` in PlanetGen | `planet_gen.py:197-240` | Simple |
| DUP-SD-07 | Repeated `to_dict`/`from_dict` Serializa | `Unknown` | Complex |
| DUP-SD-08 | Duplicate `can_build_type` Logic Between | `planet.py:166-186` | Simple |
| DUP-SD-09 | Duplicated `occupied_hexes` Property Pat | `stars.py:116-127` | Simple |
| DUP-SD-10 | `_facility_is_shipyard` Wrapper in build | `build_queue_source.py:114-126` | Simple |
| DUP-SE-003 | Duplicated `_spawn_complex` and `_spawn_ | `production_engine.py:595-655` | Medium |
| DUP-SE-004 | Duplicated `_spawn_ship` and `_spawn_fle | `production_engine.py:657-736` | Simple |
| DUP-SE-005 | Duplicated Fleet Iteration + Empire Iter | `Unknown` | N |
| DUP-SE-006 | Duplicated `process_join_fleet` Merge+Ev | `fleet_order_processor.py:79-13` | Simple |
| DUP-SE-007 | Duplicated Registries Resolution Pattern | `game_session.py:86-96` | Simple |
| DUP-SE-008 | Duplicated `session.turn_engine._registr | `superweapon_command_handlers.p` | Simple |
| DUP-SE-009 | Backward Compatibility Alias `process_en | `fleet_order_processor.py:645-6` | Simple |
| DUP-SS-03 | Two Component Iteration Implementations | `game/strategy/services/compone` | Medium |
| DUP-SS-04 | Name Slugification Functions | `game/strategy/systems/race_lib` | Simple |
| DUP-SS-05 | Hex Axial Distance Calculation Inlined i | `game/strategy/generation/densi` | Simple |
| DUP-SS-06 | Loader Classes Share Structural Pattern | `game/strategy/generation/loade` | Medium |
| DUP-UIW-006 | Duplicate Image Scaling/Centering Logic | `game/ui/utils/pygame_utils.py:` | Simple |
| DUP-UIW-007 | Two Competing Section Header Patterns | `game/ui/utils/pygame_utils.py:` | Simple |
| DUP-UIW-008 | Duplicate Element Cleanup Patterns | `Unknown` | Medium |
| DUP-UIW-009 | Duplicate Vehicle Type Color Maps | `game/ui/panels/build_queue_por` | Simple |
| DUP-UIW-010 | Duplicate update_config/set_from_config  | `race_environment_panel.py:450-` | Simple |
| DUP-UIW-011 | Colors Module Has Both Module-Level and  | `game/ui/colors.py:8-9` | Medium |
| DUP-SCR-011 | Header Sort/Swap Handling Pattern Duplic | `Unknown` | Simple |
| DUP-SCR-012 | Kill Pattern with VirtualTable + Close C | `Unknown` | Medium |
| DUP-SCR-013 | Tri-State Filter Widget Polling Pattern  | `Unknown` | Simple |
| DUP-SCR-014 | Population Formatting with K/M Suffixes  | `Unknown` | Simple |
| DUP-SCR-015 | Sidebar Panel Layout Initialization Patt | `Unknown` | Medium |
| DUP-SCR-016 | `_get_column_value` Duplicated Between W | `Unknown` | Simple |
| DUP-UIS-003 | Bounding-Box Center Camera Pattern | `game/ui/research/research_scen` | Medium |
| DUP-UIS-004 | Ships Folder Path Construction Duplicate | `game/ui/services/ship_io.py:95` | Simple |
| DUP-UIS-005 | ShipIOAdapter is a Thin Pass-Through wit | `game/ui/services/ship_io_adapt` | Medium |
| DUP-UIS-006 | BattleOrchestrator Overlap with battle_f | `game/ui/orchestration/battle_o` | Simple |


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
| Total Findings | 114 |
| Critical | 0 |
| Major | 45 |
| Minor | 69 |
| Info | 0 |
| Agents Used | 12 |

---
*Report generated: 2026-03-24 20:17*
