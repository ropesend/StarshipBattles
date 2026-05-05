# Test Coverage Audit — Shard 03 Findings

## Summary

| Metric | Count |
|--------|-------|
| Files in scope | 35 |
| CRITICAL findings | 3 |
| MAJOR findings | 12 |
| MINOR findings | 8 |
| ADVISORY findings | 6 |
| LOC ceiling violations | 5 |
| Files fully covered (Tier 3, verified) | 5 |

**Layers represented:** Core (3), Research (1), Simulation (6), Strategy (10), UI (15)

---

## CRITICAL — Tier 0 Non-UI Files With Zero Unit Tests

### 1. `game/simulation/interfaces/ability_protocols.py` (359 LOC, Tier 0)

**Zero candidate test files.** All 46 symbols untested. This file defines 9 `@runtime_checkable` Protocol classes (IAbility, IWeaponAbility, etc.) and 9 TypeGuard functions (is_ability, is_weapon, etc.) that form the simulation layer's internal typing contract. Every combat component ability is expected to satisfy these protocols.

**Untested paths (all symbols):**
| Symbol | Line | Type |
|--------|------|------|
| IAbility | 44 | Protocol |
| IAbility.stack_group | 59 | property |
| IAbility.tags | 64 | property |
| IAbility.get_ui_rows | 68 | method |
| IAbility.get_effect_summary | 77 | method |
| IAbility.sync_data | 88 | method |
| IResourceConsumptionAbility | 98 | Protocol |
| IResourceConsumptionAbility.trigger | 106 | property |
| IResourceConsumptionAbility.resource_type | 111 | property |
| IResourceConsumptionAbility.amount | 116 | property |
| IResourceConsumptionAbility.check_available | 120 | method |
| IResourceStorageAbility | 126 | Protocol |
| IResourceStorageAbility.resource_type | 134 | property |
| IResourceStorageAbility.max_amount | 139 | property |
| IResourceGenerationAbility | 145 | Protocol |
| IResourceGenerationAbility.resource_type | 153 | property |
| IResourceGenerationAbility.rate | 158 | property |
| IWeaponAbility | 168 | Protocol |
| IWeaponAbility.damage | 176 | property |
| IWeaponAbility.range | 181 | property |
| IWeaponAbility.reload_time | 186 | property |
| IWeaponAbility.firing_arc | 191 | property |
| IWeaponAbility.get_damage | 195 | method |
| IBeamWeaponAbility | 212 | Protocol |
| IBeamWeaponAbility.base_accuracy | 220 | property |
| IBeamWeaponAbility.accuracy_falloff | 225 | property |
| ISeekerWeaponAbility | 231 | Protocol |
| ISeekerWeaponAbility.projectile_speed | 239 | property |
| ISeekerWeaponAbility.endurance | 244 | property |
| ISeekerWeaponAbility.turn_rate | 249 | property |
| ISeekerWeaponAbility.projectile_damage | 254 | property |
| ISeekerWeaponAbility.projectile_hp | 259 | property |
| IProjectileWeaponAbility | 265 | Protocol |
| IProjectileWeaponAbility.projectile_speed | 273 | property |
| IWarpJumpAbility | 283 | Protocol |
| IWarpJumpAbility.max_tonnage | 291 | property |
| IWarpJumpAbility.energy_cost | 296 | property |
| is_ability | 317 | TypeGuard |
| is_resource_consumption | 322 | TypeGuard |
| is_resource_storage | 327 | TypeGuard |
| is_resource_generation | 332 | TypeGuard |
| is_weapon | 337 | TypeGuard |
| is_beam_weapon | 342 | TypeGuard |
| is_seeker_weapon | 347 | TypeGuard |
| is_projectile_weapon | 352 | TypeGuard |
| is_warp_jump | 357 | TypeGuard |

**Suggested tests:**
- `test_is_ability_with_mock`: Create mock objects with/without required attrs, verify TypeGuard narrowing
- `test_is_weapon_variants`: Verify is_beam_weapon/is_seeker_weapon/is_projectile_weapon properly disambiguate
- `test_is_projectile_weapon_excludes_seeker`: Verify the `not hasattr(obj, 'turn_rate')` guard at line 354
- `test_isinstance_protocol_compliance`: Verify concrete ability classes pass isinstance checks against their protocols (e.g., `isinstance(BeamWeaponAbility(...), IBeamWeaponAbility)`)
- `test_duck_vs_runtime_checkable`: Verify that duck-typed TypeGuard checks (hasattr) match @runtime_checkable isinstance behavior for real ability classes

### 2. `game/strategy/engine/handlers/base.py` (391 LOC, Tier 0)

**Zero candidate test files.** All 18 symbols untested. This is the foundation of the command-handler dispatch system — `add_move_order_if_needed` (the chain-aware MOVE auto-queue helper), `BaseCommandHandler` with its resolution helpers, and `CommandHandlerRegistry`. Every command handler in the strategy layer depends on this module.

**Untested paths by symbol:**
| Symbol | Line | Risk |
|--------|------|------|
| add_move_order_if_needed | 32 | Core movement-path logic; chain-aware start_hex resolution (BUG-70); path stripping at line 79 |
| ICommandHandler (Protocol) | 84 | Protocol definition |
| BaseCommandHandler._resolve_fleet | 111 | Returns (fleet, None) or (None, ValidationResult) tuple pattern |
| BaseCommandHandler._resolve_player_fleet | 134 | BUG-125: authorizes against session.active_empire.id — security-critical; returns (None, error) when no active empire |
| BaseCommandHandler._resolve_fleet_required | 158 | Raises ValueError instead of returning tuple |
| BaseCommandHandler._resolve_planet | 185 | Returns (planet, None) or (None, ValidationResult) |
| BaseCommandHandler._resolve_planet_optional | 202 | Configurable required/optional behavior via boolean flag |
| BaseCommandHandler._emit_validated_order | 227 | PROJ-319 DUP-X-02 consolidation; conditional Order creation + logging |
| BaseCommandHandler._resolve_build_entity | 249 | BUG-103: dispatches on entity_type string ("planet"/"fleet") |
| BaseCommandHandler._resolve_queue | 270 | Multi-queue resolution for planets with facilities; base_queue_pattern matching |
| BaseCommandHandler._resolve_queue_owner | 303 | Mirrors _resolve_queue but returns owner object; fleet yard prefix matching |
| BaseCommandHandler._build_colonize_target | 345 | Wraps planet in dict when population/cargo amounts specified |
| CommandHandlerRegistry | 362 | Registry class |
| CommandHandlerRegistry.register | 368 | Keyed dispatch registration |
| CommandHandlerRegistry.dispatch | 377 | Returns error for unknown command types |

**Suggested tests:**
- `test_add_move_order_if_needed_already_at_target`: start_hex == target_hex returns success without adding order
- `test_add_move_order_if_needed_no_path`: find_hybrid_path returns empty list → ValidationResult.error
- `test_add_move_order_if_needed_chain_aware`: verify last MOVE order target used as start_hex (BUG-70 regression)
- `test_add_move_order_if_needed_path_set_on_first_order`: path stripped and assigned when fleet at start (line 78-79)
- `test_resolve_player_fleet_no_active_empire`: session.active_empire is None → error tuple
- `test_resolve_player_fleet_wrong_owner`: fleet.owner_id != active.id → error tuple
- `test_resolve_fleet_required_raises`: fleet not found → ValueError
- `test_resolve_queue_facility_queue_id`: matches facility.instance_id → returns facility queue
- `test_resolve_queue_owner_fleet_yard_prefix`: fleet yard queue_id pattern resolves to fleet
- `test_emit_validated_order_invalid_result`: returns result without adding order
- `test_emit_validated_order_valid_result`: adds Order and logs
- `test_dispatch_unknown_command`: returns ValidationResult.error
- `test_dispatch_known_command`: calls handler.execute

### 3. `game/strategy/services/ability_sources/warp_point.py` (64 LOC, Tier 0)

**Zero candidate test files.** All 9 symbols untested. Implements IAbilitySource for warp point intrinsic abilities (PROJ-303). Handles local-to-global coordinate translation in `affects_hex` at line 56.

**Untested paths:**
| Symbol | Line | Risk |
|--------|------|------|
| WarpPointAbilitySource | 13 | Frozen dataclass adapter |
| source_kind | 20 | Always returns 'warp_point' |
| source_label | 24 | Fallback to "Warp Point → {dest}" when no name field |
| source_id | 33 | Fallback to id(obj) when no destination_id |
| owner_id | 39 | Always None (warp points are ownerless) |
| get_abilities | 42 | Handles None intrinsic_abilities (or {}) gracefully |
| affects_hex | 45 | Global coordinate translation; sys_loc + wp_loc; TypeError catch at line 57 |
| affects_system | 60 | Identity comparison |
| get_activation_state | 63 | Always None |

**Suggested tests:**
- `test_warp_point_source_label_fallback`: warp point without name attribute uses destination_id fallback
- `test_affects_hex_global_translation`: verify sys_loc + wp_loc coordinate math
- `test_affects_hex_no_location`: wp_loc or sys_loc is None → False
- `test_affects_hex_typeerror_catch`: TypeError in coordinate addition → False (line 57-58)
- `test_get_abilities_none_intrinsic`: warp_point with None intrinsic_abilities → empty dict
- `test_source_id_no_destination`: fallback to id(self.warp_point) when no destination_id

---

## MAJOR — Tier 1 or Key Untested Branches

### 4. `game/ui/screens/transfer_view_model.py` (322 LOC, Tier 0)

**Zero candidate test files.** All 19 symbols untested. Despite being named a "ViewModel" it's categorized as Tier 0. This is pure-business-logic (no pygame) with transfer math, pending states, row building from DTOs, filtering, and sentinel value handling (MAX_LOAD = float('inf'), MAX_DROP = float('-inf')). Highly testable without UI dependencies.

**Key untested logic:**
- `apply_arrow` (line 83): MAX_LOAD/MAX_DROP sentinel reset to 0 before delta (lines 94-95)
- `apply_max` (line 100): direction-based sentinel assignment
- `format_pending` (line 131): MAX_LOAD → "Load Max", MAX_DROP → "Drop Max", positive → "Load N", negative → "Drop N"
- `select_source` (line 156): rebuilds available_targets excluding selected, picks first as current_target
- `get_amounts` (line 199): dispatches on FleetInfo vs PlanetInfo for resource/population extraction
- `build_row_data` (line 226): 8 resource types + species keys + pod rows ordering
- `_build_pod_rows` (line 269): merges known pod designs with actual present pods from both sides
- `visible_rows` (line 309): filter_empty toggling
- `toggle_filter_empty` (line 143): returns new boolean state

**Suggested tests:**
- `test_apply_arrow_resets_max_load`: current value is MAX_LOAD, delta -1 → -1 (not inf-1)
- `test_apply_arrow_resets_max_drop`: current value is MAX_DROP, delta +1 → +1
- `test_format_pending_max_load`: returns "Load Max"
- `test_format_pending_positive`: returns "Load 5"
- `test_format_pending_negative`: returns "Drop 5"
- `test_select_source_rebuilds_targets`: source excluded from targets, first target auto-selected
- `test_get_amounts_fleet_info`: extracts cargo_resources and passengers_current
- `test_get_amounts_planet_info`: extracts stockpile and population_details with passengers_ prefix
- `test_build_pod_rows_merged_pods`: unknown pod from source appears in result
- `test_filter_empty_hides_zero_rows`: rows with both amts = 0 hidden when filter_empty=True

### 5. `game/simulation/components/abilities/harvester.py` (181 LOC, Tier 2)

6 untested symbols. The `StagingYardAbility` and `PlanetaryYardAbility` classes have zero direct test references — their `_parse_attrs` methods and `StagingYardAbility` class itself have no heuristic matches. These are critical for planet-side construction (staging yards hold completed fighters/drop pods; planetary yards enable base construction queues).

**Untested:**
- `ResourceHarvesterAbility._parse_attrs` (line 16): Handles both dict and non-dict data attribs; sets defaults (resource_type="Unknown", base_harvest_rate=0.0)
- `LocalStorageAbility._parse_attrs` (line 57): Same pattern; also sets `_base_capacity`
- **`StagingYardAbility`** (line 91-111): Entire class has no heuristic test matches. `_parse_attrs` handles dict fallback `float(data)` for v1.0 compat
- **`StagingYardAbility._parse_attrs`** (line 100): `float(data)` path at line 104 (non-dict data)
- **`PlanetaryYardAbility`** (line 113-131): Class itself has no heuristic test matches. Constructor at line 123 calls super().__init__()
- `SpaceShipyardAbility._parse_attrs` (line 138): Empty production_rates dict fallback; non-dict data fallback (lines 143-146)

**Suggested tests:**
- `test_staging_yard_parse_attrs_legacy_number_data`: pass a number instead of dict → capacity_mass = float(data)
- `test_staging_yard_parse_attrs_none_data`: pass None → capacity_mass = 0.0
- `test_planetary_yard_init_and_value`: verify get_primary_value returns 1.0; get_ui_rows returns marker row
- `test_space_shipyard_parse_attrs_empty_dict`: verify defaults when dict has no relevant keys
- `test_space_shipyard_parse_attrs_equal_rates`: production_rates with all-equal values → single rate row
- `test_space_shipyard_parse_attrs_mixed_rates`: different rate values → range row (min-max)

### 6. `game/research/data/research_tracker.py` (293 LOC, Tier 2)

Tier 0 classification, but actually Tier 2 with test files. 2 untested symbols. The `_clamp_allocations_to_budget` method (line 219) has complex proportional scaling logic with remainder assignment to the largest allocator.

**Untested paths:**
- `ResearchTracker._clamp_allocations_to_budget` (line 219):
  - Line 222-223: total <= budget → early return (no-op)
  - Line 225-228: budget == 0 → all allocations set to 0
  - Line 230-244: Proportional scaling with remainder to last (largest) node — ensure exact budget match
  - Single-node scenario: last node gets all remaining budget regardless of scale
  - Rounding: integer truncation of `int(state.rp_allocation * scale)` could cause budget mismatch if remainder logic fails

**Suggested tests:**
- `test_clamp_under_budget`: allocations within budget → no change
- `test_clamp_zero_budget`: all allocations become 0
- `test_clamp_proportional_single_node`: one node with all RP gets entire new budget
- `test_clamp_proportional_multi`: multiple nodes scaled down; verify exact budget match

### 7. `game/simulation/validation/ship_validator.py` (438 LOC, Tier 2)

Has candidate test files but coverage claims need verification. Key areas:
- `LayerRestrictionDefinitionRule._check_allow_rules` (line 196): Complex allow-rule parsing with allow_classification, allow_id, allow_ability — all must be explicitly verified to match at least one allow rule if any exist (line 232: no match → error)
- `ResourceDependencyRule._do_validate` (line 342): Instance-based checks (`isinstance(ab, ResourceConsumption)`) rather than protocol-based; resource name stored with `res_name` (could be empty string → skipped)
- `ClassRequirementsRule._do_validate` (line 293): ShipStatsCalculator integration; `crew_capacity < 0` clamp at line 324-325

**Suggested tests:**
- `test_allow_rules_no_match`: all allow rules present but component doesn't match any → error
- `test_allow_rules_match_classification`: component classification matches allow_classification → passes
- `test_allow_rules_match_ability`: component has ability matching allow_ability → passes
- `test_resource_dependency_empty_name`: ResourceConsumption with res_name="" → no resource added to needed set
- `test_resource_dependency_zero_capacity`: ResourceStorage with capacity=0 → not added to stored set

### 8. `game/strategy/data/galaxy_system_generator.py` (354 LOC, Tier 2)

Has test files but 3 untested internal loaders. Key untested logic:
- `_apply_intrinsic_abilities` (line 248): Shared roller (DUP-X-12); idempotent check (line 268: entities with non-empty intrinsic_abilities are skipped); seeded vs unseeded RNG branching (line 265-266)
- `_apply_system_archetype` (line 327): Archetype chance roll (~15%); 'void' exclusion (line 347); pre-set archetype skip (line 341); uniform random pick (line 350)
- `generate_systems` (line 103): Placement exhaustion (consecutive_failures > 10 → break at line 183); separate RNG streams for storms + intrinsics (lines 162-168); spatial index incremental update (line 212)

**Suggested tests:**
- `test_apply_intrinsic_abilities_idempotent`: entity already has intrinsic_abilities → unchanged
- `test_apply_intrinsic_abilities_no_types_data`: empty types_data → no-op
- `test_apply_system_archetype_preset`: system.archetype is not None → skip
- `test_apply_system_archetype_void_excluded`: 'void' archetype not selectable
- `test_generate_systems_placement_exhaustion`: 10 consecutive failures → break

### 9. `game/ui/screens/strategy_superweapons.py` (400 LOC, Tier 2)

4 untested private methods. Exceeds UI 300-line soft limit. Key untested:
- `_queue_implode_planet` (line 101): Confirmation callback; QueueImplodePlanetMissionCommand construction
- `_show_confirmation` (line 365): Delegates to scene.ui.show_confirmation_dialog with is_warning flag
- `_show_system_picker` (line 378): Delegates to scene.ui.show_system_picker
- `_show_ship_picker` (line 390): Delegates to scene.ui.show_ship_picker; ability_name parameter forwarding

**LOC ceiling: 400 lines exceeds the 300-line UI soft limit per Pattern #2.4.**

### 10. `game/strategy/data/resource_generation_config.py` (149 LOC, Tier 2)

3 untested symbols. The `get_resource_generation_config` lru_cached getter (line 134) has broad exception catch (line 147) with fallback to defaults. The `get_affinity` method (line 119) defaults to 1.0 for unknown planet_type/resource pairs.

**Suggested tests:**
- `test_get_resource_generation_config_cache_clear_needed`: tests calling the getter must clear cache
- `test_get_affinity_unknown_type`: unknown planet_type_name → 1.0
- `test_get_affinity_unknown_resource`: unknown resource_name → 1.0
- `test_fallback_to_defaults_on_load_failure`: verify defaults match DEFAULT_* class constants

### 11. `game/ui/screens/battle_screen.py` (687 LOC, Tier 1/2)

13 untested symbols. Most are visual-mode methods (`_update_headless`, `_update_visual_effects`, `draw_hud`, `print_headless_summary`, `_add_hit_effect`, `_on_shield_hit`, `_on_component_hit`, `_on_component_destroyed`, `_on_ship_destroyed`, `_subscribe_combat_events`, `_resolve_focus_target`, `_update_tick_rate`, `stats_panel_width`).

**LOC ceiling: 687 lines far exceeds both the 300-line UI soft limit and the 500-line production ceiling.**

### 12. `game/simulation/replay/replay_serialization.py` (640 LOC, Tier 2)

Appears covered (Tier 3 would confirm) but **exceeds 500 LOC ceiling**. Contains `compute_components_registry_hash` (line 582) with intentional broad catches (lines 603, 618). The hash drift detection in `from_dict` at lines 390-394 handles KeyError on unknown TelemetryLevel name with opaque fallback.

**LOC ceiling: 640 lines exceeds 500.**

### 13. `game/strategy/engine/production_engine.py` (666 LOC, Tier 3)

Appears fully covered but **exceeds 500 LOC ceiling**. Note that `process_construction_tick` is a complex multi-queue iteration method.

**LOC ceiling: 666 lines exceeds 500.**

### 14. `game/strategy/generation/storm_generator.py` (223 LOC, Tier 2)

3 untested private methods. `_find_valid_center` (line 170) has a max_radius clamping at line 206 (`min(max_radius, 30)`) and up to 50 placement attempts.

**Suggested tests:**
- `test_find_valid_center_all_hexes_occupied`: 50 attempts exhausted → None
- `test_collect_occupied_hexes_includes_stars_and_planets`: verify star occupied_hexes + planet.locations are in occupied set

### 15. `game/ui/screens/builder/stat_definitions.py` (77 LOC, Tier 2)

5 untested symbols. `StatDefinition.get_value` (line 34) has three dispatch paths: callable getter, string getter (getattr), and default attr_key lookup. `format_value` (line 43) handles both callable formatters and format strings. `get_display_unit` (line 48) handles callable unit functions.

**Suggested tests:**
- `test_stat_definition_get_value_callable_getter`: getter is a callable → returns getter(ship)
- `test_stat_definition_get_value_string_getter`: getter is a string → returns getattr(ship, getter, 0)
- `test_stat_definition_format_value_format_string`: formatter is "{:.2f}" → formats with .format()
- `test_stat_definition_get_display_unit_callable`: unit is callable → returns unit(ship, val)

---

## MINOR — Partially Tested

### 16. `game/core/input_actions.py` (344 LOC, Tier 2)

1 untested symbol: `KeyBinding._key_display_name` (line 301). This is indirectly tested via `display_text()` (line 287) which calls `_key_display_name()` at line 297, so the private method IS exercised. Severity reduced to MINOR.

### 17. `game/core/paths.py` (197 LOC, Tier 2)

3 untested symbols. `_find_project_root` (line 21) runs at module load (line 43) so it's implicitly exercised whenever anything imports from `game.core.paths`. `Paths.get_planets_v3_dir` (line 183) and `Paths.get_stars_dir` (line 187) are simple pathlib.Path constructors. MINOR.

### 18. `game/simulation/components/component_resource_manager.py` (112 LOC, Tier 2)

1 untested symbol: `__init__`. All methods exercised via test file. `get_resource_cost` (line 80) has lazy formula evaluation logic (lines 98-108) — only builds eval_context when a formula string is encountered. `evaluated_resource_cost` fallback at line 94 uses `or component.data.get(...)`.

**Suggested test:**
- `test_get_resource_cost_lazy_eval_context`: component without formulas in resource_cost → eval_context is never built

### 19. `game/strategy/generation/planet_image_registry.py` (129 LOC, Tier 2)

2 untested: `__init__` and `_load_classifications`. However `get_random_image` (line 65) is tested and exercises the loaded data. The `rng=None` path at line 76-77 creates `random.Random()` without seed. MINOR.

### 20. `game/ui/components/table/column_manager.py` (176 LOC, Tier 2)

2 untested: `is_column_visible` (line 125) and `get_toggleable_columns` (line 153). Both are simple predicates/queries. MINOR.

### 21. `game/ui/screens/empire_build_queue_formatter.py` (189 LOC, Tier 2)

1 untested: `format_turns_remaining` (line 117). Pure formatting function. The `turns <= 0` → "Complete" path at line 126-127 is untested. MINOR.

### 22. `game/ui/screens/planet_data_source.py` (100 LOC, Tier 2)

5 untested symbols (all init/private methods). `_get_planet_icon` (line 64) has image loading with rotation + scaling, asset manager integration, and cache key construction — this is pygame rendering code. ADVISORY for rendering, MINOR for business logic.

### 23. `game/ui/screens/planet_selection_window.py` (232 LOC, Tier 3)

2 untested: `PlanetSelectionUiBuilder` and its `build` method. The builder constructs pygame_gui widgets — ADVISORY for UI rendering code coupling.

### 24. `game/ui/screens/builder/interaction_controller.py` (132 LOC, Tier 2)

2 untested: `handle_event` (line 61) and `update` (line 106). Both involve pygame event handling. `handle_event` has drag-drop logic with shift-hold multi-placement (lines 90-103). ADVISORY for pygame rendering/event code.

---

## ADVISORY — `__init__.py` Re-exports / Docstrings / UI Rendering

### 25. `game/core/__init__.py` (179 LOC, Tier 1)
Re-export shim. No symbols to test. Imported by many files as side effect.

### 26. `game/strategy/combat/__init__.py` (6 LOC, Tier 0)
Docstring only. No code to test.

### 27. `game/strategy/facade/dto/__init__.py` (30 LOC, Tier 1)
Re-export shim with `__all__` list. No logic.

### 28. `game/strategy/services/__init__.py` (5 LOC, Tier 1)
Single class re-export. No logic.

### 29. `game/ui/screens/build_queue_renderer.py` (241 LOC, Tier 0)
Zero tests, but entirely pygame_gui widget construction and rendering. All methods create/manipulate pygame_gui elements. ADVISORY for rendering code.

### 30. `game/ui/screens/builder/left_panel.py` (485 LOC, Tier 0)
Zero tests. 485 lines of pygame_gui widget construction, bulk-add UI with slider/text sync, filter dropdowns, component list management with sorting. Contains business logic mixed with rendering — would benefit from ViewModel extraction.

**LOC ceiling: 485 lines exceeds the 300-line UI soft limit.**

### 31. `game/ui/screens/data_list_window_mixin.py` (88 LOC, Tier 0)
Zero tests. Mixin used by PlanetListWindow and StarListWindow. Contains `_toggle_column`, `_save_preset`, `_sync_slider_text` — these delegate to subclasses' pygame_gui elements. ADVISORY.

---

## Tier 3 — Verified Coverage

### 32. `game/simulation/battle_outcome.py` (203 LOC, Tier 3)
All 9 symbols marked tested. 16 candidate test files. Frozen dataclasses — correctness verified via integration test paths (battle_runner, replay serialization, post_battle_hook).

### 33. `game/strategy/data/ship_instance_serializer.py` (176 LOC, Tier 3)
All 6 symbols tested. Serialization round-trips and cloning verified.

### 34. `game/strategy/engine/production_engine.py` (666 LOC, Tier 3)
All 19 symbols tested. 15 candidate test files. Note: exceeds 500 LOC ceiling.

### 35. `game/ui/utils/formatters.py` (90 LOC, Tier 3)
All 3 symbols tested. Pure formatting functions with complete path coverage.

---

## File Coverage Verification Table

| File | LOC | Tier | Symbols | Untested | Coverage Notes |
|------|-----|------|---------|----------|----------------|
| game/core/__init__.py | 179 | 1 | 0 | 0 | Re-exports only — ADVISORY |
| game/core/input_actions.py | 344 | 2 | 6 | 1 | _key_display_name indirectly tested via display_text |
| game/core/paths.py | 197 | 2 | 13 | 3 | _find_project_root runs at import time |
| game/research/data/research_tracker.py | 293 | 2 | 21 | 2 | _clamp_allocations_to_budget untested (MAJOR) |
| game/simulation/battle_outcome.py | 203 | 3 | 9 | 0 | VERIFIED — frozen DTOs |
| game/simulation/components/abilities/harvester.py | 181 | 2 | 21 | 6 | StagingYardAbility/PlanetaryYardAbility untested |
| game/simulation/components/component_resource_manager.py | 112 | 2 | 6 | 1 | __init__ only; lazy eval_context path untested |
| game/simulation/interfaces/ability_protocols.py | 359 | 0 | 46 | 46 | **CRITICAL** — zero tests |
| game/simulation/replay/replay_serialization.py | 640 | 2 | 22 | - | LOC ceiling (640 > 500) |
| game/simulation/validation/ship_validator.py | 438 | 2 | - | - | Complex allow-rule logic needs verification |
| game/strategy/combat/__init__.py | 6 | 0 | 0 | 0 | Docstring only — ADVISORY |
| game/strategy/data/design_role_registry.py | 98 | 2 | 4 | 1 | _build_default untested |
| game/strategy/data/galaxy_system_generator.py | 354 | 2 | 13 | 3 | Internal loaders untested |
| game/strategy/data/resource_generation_config.py | 149 | 2 | 6 | 3 | __init__, _load, _use_defaults untested |
| game/strategy/data/ship_instance_serializer.py | 176 | 3 | 6 | 0 | VERIFIED |
| game/strategy/engine/handlers/base.py | 391 | 0 | 18 | 18 | **CRITICAL** — zero tests |
| game/strategy/engine/production_engine.py | 666 | 3 | 19 | 0 | VERIFIED (LOC ceiling) |
| game/strategy/facade/dto/__init__.py | 30 | 1 | 0 | 0 | Re-exports — ADVISORY |
| game/strategy/generation/planet_image_registry.py | 129 | 2 | 7 | 2 | __init__/_load untested |
| game/strategy/generation/storm_generator.py | 223 | 2 | 5 | 3 | Private helpers untested |
| game/strategy/services/__init__.py | 5 | 1 | 0 | 0 | Re-export — ADVISORY |
| game/strategy/services/ability_sources/warp_point.py | 64 | 0 | 9 | 9 | **CRITICAL** — zero tests |
| game/ui/components/table/column_manager.py | 176 | 2 | 12 | 2 | MINOR |
| game/ui/screens/battle_screen.py | 687 | 2 | 36 | 13 | LOC ceiling (687 > 300 UI) |
| game/ui/screens/build_queue_renderer.py | 241 | 0 | 7 | 7 | ADVISORY — rendering |
| game/ui/screens/builder/interaction_controller.py | 132 | 2 | 6 | 2 | ADVISORY — pygame events |
| game/ui/screens/builder/left_panel.py | 485 | 0 | 13 | 13 | ADVISORY — rendering (LOC ceiling) |
| game/ui/screens/builder/stat_definitions.py | 77 | 2 | 7 | 5 | Multiple dispatch paths untested |
| game/ui/screens/data_list_window_mixin.py | 88 | 0 | 4 | 4 | ADVISORY — mixin |
| game/ui/screens/empire_build_queue_formatter.py | 189 | 2 | 9 | 1 | MINOR |
| game/ui/screens/planet_data_source.py | 100 | 2 | 7 | 5 | ADVISORY for icon rendering |
| game/ui/screens/planet_selection_window.py | 232 | 2 | 6 | 2 | ADVISORY for widget construction |
| game/ui/screens/strategy_superweapons.py | 400 | 2 | 18 | 4 | LOC ceiling (400 > 300 UI) |
| game/ui/screens/transfer_view_model.py | 322 | 0 | 19 | 19 | **MAJOR** — pure logic, zero tests |
| game/ui/utils/formatters.py | 90 | 3 | 3 | 0 | VERIFIED |

---

## LOC Ceiling Violations

| File | LOC | Limit | Exceeded By | Layer |
|------|-----|-------|-------------|-------|
| game/ui/screens/battle_screen.py | 687 | 300 (UI) / 500 (production) | +387 / +187 | UI |
| game/strategy/engine/production_engine.py | 666 | 500 | +166 | Strategy |
| game/simulation/replay/replay_serialization.py | 640 | 500 | +140 | Simulation |
| game/ui/screens/builder/left_panel.py | 485 | 300 (UI) | +185 | UI |
| game/ui/screens/strategy_superweapons.py | 400 | 300 (UI) | +100 | UI |

---

## Context Usage Estimate

| Phase | Files Read | Est. Tokens |
|-------|-----------|-------------|
| Production files (all 35) | 35 | ~25,000 |
| Coverage matrix slices | 2 extracts | ~8,000 |
| Documentation reference | 3 docs | ~12,000 |
| Test file reads | 0 (used matrix data) | 0 |
| Report generation | 1 write | ~5,000 |
| **Total estimated** | | **~50,000** |

---

## Priority Remediation Order

1. **`game/strategy/engine/handlers/base.py`** — Write tests for all 18 symbols. This is the foundation of command dispatch. Every command handler depends on it. (391 LOC, CRITICAL)
2. **`game/simulation/interfaces/ability_protocols.py`** — Write tests verifying TypeGuard + Protocol conformance for all ability types. (359 LOC, CRITICAL)
3. **`game/strategy/services/ability_sources/warp_point.py`** — Test IAbilitySource adapter including coordinate translation edge cases. (64 LOC, CRITICAL)
4. **`game/ui/screens/transfer_view_model.py`** — Pure-Python ViewModel with no pygame deps. Very testable. (322 LOC, MAJOR)
5. **`game/simulation/components/abilities/harvester.py`** — Cover StagingYardAbility and PlanetaryYardAbility. (181 LOC, MAJOR)
