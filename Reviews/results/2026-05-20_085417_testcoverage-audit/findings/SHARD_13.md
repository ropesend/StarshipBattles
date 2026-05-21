# Test Coverage Audit — Shard 13

**Date:** 2026-05-20  
**Files:** 45 production, ~9466 LOC  
**Layer distribution:** core(3), ai(2), assets(1), engine(1), simulation(8), strategy(18), ui(12)

---

## Summary

| Category | Count | Notes |
|---|---|---|
| **TRUE Tier 0 (zero tests)** | 4 | Raw ABCs, re-export inits, or module-level functions with no direct test |
| **Tier 1 (minimal/no symbols)** | 4 | `__init__.py` re-exports; symbols tested via integration |
| **Tier 2 (partial)** | 33 | Most have solid test files; specific gaps identified below |
| **Tier 3 (apparently covered)** | 4 | Dedicated test files with comprehensive coverage |
| **Baseline corrections** | 3 | Baseline misclassified `registry.py`, `ui.py`, `defense.py` as Tier 0 — they have tests |

### Severity Distribution

| Severity | Count | Key files |
|---|---|---|
| **CRITICAL** | 2 | `interfaces/engines/combat.py`, `superweapon_handlers/__init__.py` |
| **MAJOR** | 4 | `conflict_modifier_collection.py`, `turn_engine.py` (3 hooks), untested error paths |
| **MINOR** | 17 | Partial coverage gaps, `__init__` methods, UI event handlers |
| **ADVISORY** | 10 | `__init__.py` re-exports, `__repr__`, `__getattr__`, `__post_init__`, Protocol-only files |

---

## Tier 0 (Zero Tests — Critical)

### 1. `game/strategy/interfaces/engines/combat.py` — CRITICAL (112 LOC)
**What it is:** Two ABCs — `IConflictEngine` and `IEnvironmentalHazardEngine` — that define the strategy layer's combat/environmental contract surface.
**Why critical:** These ABCs are the DI seam between the strategy layer and the simulation layer. Implementations `ConflictResolutionEngine` and `EnvironmentalHazardEngine` ARE tested, but the ABC contract itself is never validated in isolation.
**Risk:** If a method signature drifts between the ABC and implementation, no test catches it. The `__init_subclass__` / `@abstractmethod` enforcement is only checked at class-definition time; runtime contract tests would catch interface drift.
**Test gap:**
- No `isinstance(ConflictResolutionEngine(), IConflictEngine)` test (line 24-71)
- No `isinstance(EnvironmentalHazardEngine(), IEnvironmentalHazardEngine)` test (line 74-112)
- No test verifying `__subclasshook__` or abstract method enforcement

### 2. `game/strategy/engine/superweapon_handlers/__init__.py` — CRITICAL (24 LOC)
**What it is:** Re-export module — imports 5 `process_*` handler functions from submodules and exposes via `__all__`.
**Why critical:** The re-export surface is the public API for superweapon dispatch. If a submodule import fails silently or `__all__` drifts, dispatch breaks at runtime.
**Risk:** Missing handler import = silent dispatch failure during turn processing.
**Test gap:**
- No test verifying all 5 `__all__` exports are resolvable at import time (lines 12-23)
- No test verifying `process_*` functions match the `SuperweaponResult` return annotation
- Individual handler modules (`close_warp_point.py`, etc.) ARE tested — the problem is only the aggregate `__init__.py` re-export surface

---

## Tier 0 (Baseline-Corrected — Actually Tested)

### 3. `game/core/protocols/registry.py` — BASELINE ERROR (39 LOC, previously marked Tier 0)
**Verified:** `IRegistryProvider` is comprehensively tested in `tests/unit/core/test_registry_provider.py` (370 lines, 12 tests):
- `test_protocol_exists` — line 25
- `test_protocol_is_runtime_checkable` — line 30
- `test_protocol_requires_get_components` — line 50
- `test_protocol_requires_get_modifiers` — line 64
- `test_protocol_requires_get_vehicle_classes` — line 76
- `test_protocol_requires_get_resources` — line 358
- DefaultRegistryProvider and TestRegistryProvider conformance tested at lines 109, 182, 300
**Severity:** NONE — reclassify to Tier 2 (adequately tested)

### 4. `game/simulation/entities/stat_contributors/defense.py` — BASELINE ERROR (112 LOC, previously marked Tier 0)
**Verified:** All 5 functions comprehensively tested in `tests/unit/simulation/entities/stat_contributors/test_defense.py` (246 lines):
- `contribute_armor` — lines 80-101 (armor pool aggregation, no-armor-layer guard)
- `contribute_shield_projection` — lines 105-121 (capacity summation)
- `contribute_shield_regeneration` — lines 123-201 (rate summation, energy cost first-match, type filtering)
- `apply_armor_and_repair_scores` — lines 204-226 (active-pool filter, emissive/shield-regen/repair)
- `init_armor_pool` — lines 229-245 (fill, damaged pool preservation, no-layer guard)
**Severity:** NONE — reclassify to Tier 3 (comprehensively tested)

---

## Tier 1 (Minimal/No Symbols Tested — Major)

### 5. `game/core/protocols/ui.py` — MAJOR (112 LOC, baseline Tier 0 corrected)
**What it is:** `IScene`, `ICamera` protocols and `is_camera` TypeGuard.
**Actual coverage:**
- `ICamera` + `is_camera`: Tested in `tests/unit/core/test_protocols.py` lines 313-369 (protocol existence, runtime_checkable, Camera satisfaction, interface methods, coordinate transforms)
- `IScene`: Tested in `tests/unit/ui/test_scene_protocol.py` class `TestISceneProtocolCompliance` (scene protocol compliance)
**Gap:**
- No `is_scene` TypeGuard exists but isn't needed (IScene is never checked via duck typing in hot paths)
- No test for `IScene.handle_resize(width, height)` method signature conformance (line 28-30)
**Severity:** MAJOR — ICamera well-tested; IScene compliance tested but `handle_resize` signature never validated against any implementation

### 6. `game/ai/__init__.py` — ADVISORY (109 LOC)
**What it is:** Docstring + re-exports of `AIController`, 8 behavior classes, `PolicyManager`, `TargetEvaluator`, `AIControllerFactory`.
**Coverage:** All re-exported symbols have their own tests. This file has no code logic beyond imports.
**Gap:** No test for `__all__` completeness (109 lines of explicit `__all__`).
**Severity:** ADVISORY

### 7. `game/core/protocols/__init__.py` — ADVISORY (162 LOC)
**What it is:** Re-exports 50+ symbols from 8 sub-modules.
**Coverage:** All re-exported symbols have tests in their sub-module test files. `test_protocols_public_api.py` checks many symbols.
**Gap:** No test verifying every `__all__` entry is resolvable at import time.
**Severity:** ADVISORY

### 8. `game/strategy/interfaces/__init__.py` — ADVISORY (58 LOC)
**What it is:** Re-exports engine ABCs from `game.strategy.interfaces.engines`.
**Coverage:** `tests/unit/strategy/interfaces/test_engines_package_layout.py` tests package layout.
**Gap:** No test verifying all 18 `__all__` entries resolve.
**Severity:** ADVISORY

### 9. `game/ui/__init__.py` — ADVISORY (27 LOC)
**What it is:** Eager imports of submodules for pytest-xdist race condition prevention.
**Coverage:** Implicitly exercised via conftest.py.
**Severity:** ADVISORY

---

## Tier 2 (Partial Coverage — Detailed Gaps)

### 10. `game/ai/carrier_controller.py` — MINOR (407 LOC)
**Test file:** `tests/unit/ai/test_carrier_controller.py`
**Covered:** `__init__`, `update`, `_maybe_launch_fighter_wave`, `_maybe_launch_satellite_wave`
**Gaps (untested private methods, heuristic confirmed):**
- `_maybe_launch_wave` (line 144) — Core mass-budget launch logic. No unit test exercising budget accumulation + enemy-in-range + pop + dispatch flow.
- `_sum_launch_rate` (line 209) — Component iteration with error handling. No test with real/fake components.
- `_enemy_in_launch_radius` (line 234) — Spatial grid query + team filtering. No test.
- `_pop_fighter_cvs` (line 256) — Legacy count-based pop. No test.
- `_pop_cvs` (line 265) — Count-based CV removal. No test.
- `_pop_cvs_within_budget` (line 302) — Mass-budget CV removal. No test.
- `_find_tactical_launch_ability` (line 361) — Legacy ability lookup. No test.
- `_unwrap_ship` (line 396) — Adapter unwrap. No test.
- `_ship_is_alive` (line 400) — Stub-safe alive check. No test.
**Severity:** MINOR — public API tested; 9 private helpers untested but individually small

### 11. `game/assets/asset_manager.py` — MINOR (374 LOC)
**Test files:** `tests/unit/assets/test_asset_manager_resolutions.py`, `tests/unit/core/test_asset_manager.py`
**Covered:** `load_manifest`, `load_image`, `load_group`, `get_random_from_group`, `load_star_image`, `get_star_core_info`, `get_star_asset_key_for_type`, `load_external_image`, `load_planet_image`, `_load_image`, `get_missing_texture`, `get_default_asset_manager`, `set_default_asset_manager`
**Gaps:**
- `__init__` (line 30) — No test verifying caches/star_metadata initialized correctly after construction
- `_load_star_metadata` (line 38) — No test with valid and missing metadata paths
- `clear` (line 47) — No test verifying caches reset correctly
**Severity:** MINOR — init/clear/load_metadata are simple, gap is small

### 12. `game/engine/collision.py` — MAJOR (201 LOC)
**Test files:** `tests/unit/engine/collision_edge_cases/`, integration tests in combat
**Covered:** `__init__`, `process_beam_attack` (tested via combat integration)
**Gaps:**
- `process_ramming` (line 161) — **Untested.** Ramming has 4 branches (rammer weaker, target weaker, equal HP, no target). Zero direct unit tests. The method computes collision radius, applies `GUARANTEED_KILL_DAMAGE`, `RAMMING_DAMAGE_FACTOR`, and logs. This is combat-critical code with no isolated test.
**Severity:** MAJOR — `process_ramming` is a combat simulation method with 3 damage branches + edge cases (no target, dead ship, non-ramming policy), zero direct tests

### 13. `game/simulation/components/abilities/harvester.py` — MINOR (181 LOC)
**Test files:** `tests/unit/simulation/abilities/test_empire_storage.py`, `tests/unit/simulation/components/abilities/test_colonize_harvester.py`
**Covered:** `ResourceHarvesterAbility` (get_primary_value, get_ui_rows), `LocalStorageAbility` (recalculate, get_primary_value, get_ui_rows)
**Gaps:**
- `ResourceHarvesterAbility._parse_attrs` (line 16) — No direct test for dict-vs-non-dict parsing branches
- `LocalStorageAbility._parse_attrs` (line 57) — No direct test
- `StagingYardAbility` (line 91) — Entire class untested. `_parse_attrs` handles dict and scalar input
- `StagingYardAbility._parse_attrs` (line 100) — Dict vs non-dict branch
- `PlanetaryYardAbility` (line 113) — Entire class untested. Marker ability.
- `SpaceShipyardAbility._parse_attrs` (line 138) — Dict vs non-dict branch
**Severity:** MINOR — StagingYardAbility and PlanetaryYardAbility are integration-tested but have no unit tests

### 14. `game/simulation/components/ability_manager.py` — MINOR (285 LOC)
**Test file:** `tests/unit/simulation/components/test_ability_manager.py`
**Covered:** `get_abilities`, `get_ability`, `has_ability`, `has_ability_with_tag`, `has_pdc_ability`, `get_ui_rows`, `instantiate_and_index`
**Gaps (heuristic):**
- `__init__` (line 47) — Tests use AbilityManager indirectly; no direct test verifying state after construction
- `_build_index` (line 71) — MRO index building. Tested indirectly but no test for the MRO-completeness guarantee (all parent class names indexed, 'object' stops)
- `_instantiate` (line 195) — Complex sync logic with existing_map reuse. Tested indirectly.
- `_get_abilities_polymorphic` (line 250) — Fallback path. Has a KNOWN_ISSUE comment (Module Identity Drift) at line 278. Tests exercise this but the fallback path's edge cases are not isolated.
**Severity:** MINOR — core methods tested; internal helpers exercised indirectly

### 15. `game/simulation/components/component.py` — MINOR (406 LOC)
**Test files:** 81 candidate files via integration
**Covered:** Most public API is integration-tested
**Gaps (heuristic):**
- `mark_hp_cache_dirty` (line 226) — Public API method. Only sets a boolean, but no test verifies that calling it causes `hp_ratio` to recalculate on next access.
**Severity:** MINOR — one line setter, gap is trivial

### 16. `game/simulation/components/component_resource_manager.py` — MINOR (112 LOC)
**Test file:** `tests/unit/simulation/components/test_component_resource_manager.py`
**Covered:** `can_afford_activation`, `consume_activation`, `try_activate`, `get_resource_cost`
**Gaps:**
- `__init__` (line 32) — Tests create ComponentResourceManager indirectly; no direct test
**Severity:** MINOR — trivial init

### 17. `game/simulation/components/component_stats_calculator.py` — MAJOR (360 LOC)
**Test files:** `tests/unit/regressions/test_bug_regressions_2026_01.py`, `tests/unit/simulation/components/test_component_stats_calculator.py`
**Covered:** `parse_formulas`, `apply_formula_defaults`, `calculate_modifier_stats`, `apply_base_stats`, `reset_and_evaluate_formulas`, `recalculate`
**Gaps:**
- `build_formula_context` (line 28) — Standalone function. Mentioned in test comments but not directly tested. Has 3 branches: explicit context → ship reference → omit key. Only the "ship attached" path is exercised through `recalculate`. The `ship_class_mass` omission behavior is documented as "intentional" but never verified by a test.
- `_evaluate_formulas_in_abilities` (line 288) — Recursive formula evaluator. Has runtime-variable preservation logic (`_RUNTIME_VARIABLES` at line 303). No direct test for the recursive traversal or for runtime-variable preservation.
**Severity:** MAJOR — `build_formula_context` has 3 code paths with critical correctness implications; only 1 path is exercised. `_evaluate_formulas_in_abilities` has complex recursive logic with no isolated test.

### 18. `game/simulation/entities/ship_validator_helper.py` — MINOR (70 LOC)
**Test file:** `tests/unit/simulation/entities/test_ship_validator_helper.py`
**Covered:** `check_validity`, `get_validation_warnings`, `get_missing_requirements`
**Gaps:**
- `__init__` (line 25) — Trivial reference storage. No direct test needed.
**Severity:** MINOR

### 19. `game/simulation/services/design_loader.py` — MINOR (130 LOC)
**Test files:** `tests/unit/simulation/services/test_simulation_design_loader.py`, `tests/unit/ui/services/test_design_loader_adapter.py`
**Covered:** `load_ship_from_design_data`, `load_ship_from_file`
**Gaps:**
- `__init__` (line 39) — Null-registries validation not directly tested
**Severity:** MINOR — registries validation exercised through `load_ship_from_design_data`

### 20. `game/strategy/combat/team_spec_builder.py` — MINOR (198 LOC)
**Test file:** `tests/unit/strategy/combat/test_team_spec_builder.py`
**Covered:** `team_spec_for_fleet_group`, `pick_formation_for_fleet`, `ship_spec_from_instance`
**Gaps:**
- `group_fleets_by_owner` (line 49) — Grouping helper with insertion-order guarantee. Tested indirectly through `compute_owner_to_team_id`. No test for empty fleet list, single-fleet, or duplicate-owner scenarios.
- `compute_owner_to_team_id` (line 67) — Team ID assignment. Tested indirectly. No test for empty fleet list.
**Severity:** MINOR — both tested via integration with `team_spec_for_fleet_group`

### 21. `game/strategy/data/carried_vehicle.py` — MINOR (115 LOC)
**Test files:** 28 candidate files via integration
**Covered:** `to_dict`, `from_dict`, class construction
**Gaps:**
- `__post_init__` (line 50) — Vehicle type validation + normalisation. Tested indirectly through `from_dict` and construction but no test for invalid vehicle_type rejection (`ValueError` at line 55-58) or for the lowercasing normalisation (line 53).
**Severity:** MINOR — trivial validation

### 22. `game/strategy/data/star_system.py` — ADVISORY (153 LOC)
**Test files:** 23 candidate files
**Covered:** `WarpPoint` (`to_dict`, `from_dict`), `StarSystem` (`__init__`, `primary_star`, `add_warp_point`, `to_dict`, `from_dict`)
**Gaps:**
- `__repr__` (line 91) — String representation. Not tested. Low impact.
**Severity:** ADVISORY

### 23. `game/strategy/data/stars.py` — ADVISORY (165 LOC)
**Test files:** 16 candidate files
**Covered:** `Star` (`__init__`, `occupied_hexes`, `to_dict`, `from_dict`), `StarType`
**Gaps:**
- `__getattr__` (line 161) — Legacy shim for `StarGenerator` re-export. Not tested. The `StarGenerator` re-export is a deprecation path.
**Severity:** ADVISORY — legacy shim

### 24. `game/strategy/engine/conflict_modifier_collection.py` — MAJOR (92 LOC)
**What it is:** Two standalone module functions extracted from `ConflictResolutionEngine`.
**Test coverage:**
- `lookup_environmental_effects`: Tested via `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py` lines 233-242 (galaxy=None, no get_system_at_location paths). Also tested in integration `test_combat_owned_sector_effect_isolation.py`.
- `collect_team_modifiers`: Tested via `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py` lines 251+ (exception-swallow path), `tests/unit/strategy/engine/test_conflict_resolution_modifier_logging.py` lines 54+.
**Gap:** Tests call `engine._lookup_environmental_effects(...)` and `engine._collect_team_modifiers(...)` — methods on `ConflictResolutionEngine`, NOT the standalone module functions. The module functions are the actual extracted code; tests exercise a delegation path. No test directly imports and calls `from game.strategy.engine.conflict_modifier_collection import lookup_environmental_effects, collect_team_modifiers` with a mock engine. The module-level function signatures are untested.
**Severity:** MAJOR — functions exercised through engine methods but the extracted module's API is not independently tested

### 25. `game/strategy/engine/game_config.py` — ADVISORY (261 LOC)
**Test files:** 30 candidate files
**Covered:** `GameConfig` (`__post_init__` validation, `to_dict`, `from_dict`, `get_player_theme_path`), `PlayerConfig` (`to_dict`, `from_dict`)
**Gaps:**
- `_get_default_asset_path` (line 17) — One-line helper returning `Paths.SHIP_THEMES_DIR`. Untested directly.
- `_get_default_players` (line 123) — Default 2-player setup factory. Untested directly. Called via `field(default_factory=_get_default_players)`.
**Severity:** ADVISORY — both are trivial callables, tested implicitly through GameConfig construction

### 26. `game/strategy/engine/order_handlers/launch_fighters.py` — MAJOR (294 LOC)
**Test files:** `tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py`, `tests/unit/strategy/engine/test_issuer_execution_contract.py`
**Covered:** `__init__`, `supported_order_types`, `execute_action_order`, `execute_for_issuer`
**Gaps:**
- `_run_with_issuer` (line 147) — Core execution. Tested indirectly through `execute_action_order`/`execute_for_issuer`. No test for the `count <= 0` branch (line 165), insufficient fighters branch (line 173), or `CarriedVehicle.from_dict` fallback (line 197).
- `_find_ship` (line 240) — Ship lookup by instance_id. No test for ship not found path.
- `_create_fighter_group` (line 248) — FighterWing creation + empire.deployed_groups append. Tested indirectly.
- `_mint_group_id` (line 268) — ID collision avoidance. No test for the collision case (candidate already in existing set).
- `_carried_vehicle_to_ship_instance` (line 278) — Thin delegate to `carried_vehicle_to_ship_instance`. Tested indirectly.
**Severity:** MAJOR — 5 private methods untested; `_run_with_issuer` has 3 untested error branches

### 27. `game/strategy/engine/planet_command_handlers.py` — MINOR (346 LOC)
**Test files:** `tests/unit/strategy/engine/test_planet_command_handlers.py`, `tests/unit/strategy/engine/test_typed_planet_intents.py`
**Covered:** All 8 command handlers tested
**Gaps:**
- `_apply_planet_environmental_target` (line 205) — Shared helper for 4 Set*Target handlers. Tested indirectly through the handlers. No direct test for the `is_clear` branch (line 234) when value is an empty dict.
- `register` (line 331) — Module-level registration function. Tested via integration (command registry construction). No isolated test.
**Severity:** MINOR — both gaps exercised through handler-level tests

### 28. `game/strategy/engine/resupply_engine.py` — MINOR (294 LOC)
**Test files:** `tests/unit/strategy/engine/test_resupply_engine.py`, `tests/unit/strategy/engine/test_engine_validation.py`
**Covered:** `process_fuel_generation`, `process_fleet_resupply`, `_calculate_fuel_distribution`, `_transfer_fuel`, `_validate_tick_inputs`
**Gaps:**
- `__init__` (line 58) — Null-registries validation. Tested indirectly.
- `_process_facility_generation` (line 113) — Single-facility processing. Tested indirectly through `process_fuel_generation`.
- `_get_fuel_generation_rate` (line 146) — Facility component scanning for fuel generation. Tested indirectly.
**Severity:** MINOR — all exercised via public API

### 29. `game/strategy/engine/turn_engine.py` — MAJOR (830 LOC)
**Test files:** 17 candidate files
**Covered:** `__init__`, `process_turn`, `_process_tick`, `_time_phase`, `_run_phases`, all 18 engine properties, `validate_colonize_order`
**Gaps:**
- `_tick_phase_log_turn_start` (line 348) — Logging hook. No direct test verifying `_log_empire_state` is called only on tick 1.
- `_tick_phase_log_after_construction` (line 353) — Logging hook. No direct test.
- `_tick_phase_accumulate_env_events` (line 360) — Environment event accumulation. Tested indirectly but no test verifying events flow correctly through this hook.
**Severity:** MAJOR — 3 phase hooks are logging/diagnostics only, but are part of the tick pipeline and never verified

### 30. `game/strategy/services/ability_metadata.py` — MINOR (566 LOC)
**Test files:** 5 candidate files
**Covered:** `get_ability_metadata`, `ability_has_role_tag`, `ability_has_kind_tag`, `abilities_with_role_tag`, `abilities_with_kind_tag`, `ability_action_time_field`, `ability_drains_energy`, all dataclasses, all public API
**Gaps:**
- `_multiplier_effect` (line 177) — Internal EffectFacet factory. Not tested directly.
- `_rate_effect` (line 194) — Internal EffectFacet factory. Not tested directly.
- `_energy_drain` (line 210) — Internal EnergyFacet factory. Not tested directly.
**Severity:** MINOR — 3 private factory functions; their output is tested through the public API

### 31. `game/strategy/services/fleet_write_service.py` — MINOR (136 LOC)
**Test files:** 6 candidate files
**Covered:** `set_location`, `set_path`, `append_order`, `insert_order`, `pop_order`, `clear_orders`, `add_ship`, `remove_ship`, `set_display_name`, `set_fleet_policy`, `append_construction_item`, `pop_construction_item`, `set_construction_queue_paused`
**Gaps:**
- `swap_orders` (line 88) — Order reordering by index. No test for index bounds.
- `add_task_force` (line 132) — Delegates to `fleet.add_task_force`. No isolated test.
- `remove_task_force` (line 135) — Delegates to `fleet.remove_task_force`. No isolated test.
**Severity:** MINOR — thin delegation methods

### 32. `game/ui/effects/hit_effects.py` — MINOR (233 LOC)
**Test file:** `tests/unit/ui/effects/test_hit_effects.py`
**Covered:** `HitEffectType`, `HitEffect` (progress, is_alive), `create_hit_effect`, `update_effects`, `draw_effects`, all 4 `_draw_*` functions
**Gaps:**
- `HitEffect.update` (line 76) — One-liner `self.elapsed += dt`. Tests call `update_effects` which calls `update`, but no direct test for the `update` method in isolation.
**Severity:** MINOR — trivial one-liner

### 33. `game/ui/screens/builder/grouping_strategies.py` — ADVISORY (79 LOC)
**Test files:** `tests/unit/ui/screens/builder/test_grouping_strategies.py`, others
**Covered:** `DefaultGroupingStrategy`, `TypeGroupingStrategy`, `FlatGroupingStrategy`, `get_component_group_key`
**Gaps:**
- `GroupingStrategy` (line 6) — Protocol definition. No runtime_checkable test. Protocol conformance is tested implicitly through usage.
**Severity:** ADVISORY — Protocol is structural, not runtime-checked

### 34. `game/ui/screens/builder/stat_definitions.py` — ADVISORY (77 LOC)
**Test files:** `tests/unit/ui/screens/builder/test_stat_definitions.py`, `tests/unit/workshop/test_stats_visibility.py`
**Covered:** `get_value`, `format_value`, `get_display_unit`, `get_status`
**Gaps:**
- `StatDefinition.__init__` (line 25) — Direct attribute assignment. No isolated test for default parameter behavior (`key=None`, `getter=None`, `validator=None`).
**Severity:** ADVISORY — trivial init

### 35. `game/ui/screens/race_setup/input_handler.py` — MINOR (174 LOC)
**Test file:** `tests/unit/ui/screens/test_race_setup_delegate_factory.py`
**Covered:** `__init__`, event routing integration
**Gaps:**
- `handle` (line 30) — Main event router. 174-line giant switch. Tested through integration but no isolated test for each event branch. The LLM dialog button branches (lines 40-81), the gallery-click fallback chain (lines 123-130), and the text-entry descriptor panel branch (lines 164-171) are complex but covered by integration.
**Severity:** MINOR — integration-tested but method has 15 distinct event branches; isolated tests would surface regressions faster

### 36. `game/ui/screens/strategy_windows/list_windows.py` — MINOR (132 LOC)
**Test file:** `tests/unit/ui/screens/strategy_windows/test_planet_list_registrar_reuse.py`
**Covered:** `PlanetListRegistrar.open` (reuse path)
**Gaps:**
- `navigate_camera_to` (line 21) — Shared camera navigation helper. No test for the `_camera_nav` attribute absence path (line 26).
- `PlanetListRegistrar.__init__` (line 33) — Trivial. No direct test.
- `PlanetListRegistrar._on_navigate` (line 79) — Window kill + camera nav. No direct test.
- `StarListRegistrar` (line 86) — Entire class. No direct test. `open` logic has `facade_state` resolution branch (lines 112-113) that is not tested.
- `StarListRegistrar.__init__` (line 89) — Trivial.
- `StarListRegistrar._on_navigate` (line 128) — No direct test.
**Severity:** MINOR — PlanetListRegistrar partially tested; StarListRegistrar completely untested as a unit

### 37. `game/ui/screens/strategy_windows/orders_window_ctrl.py` — MINOR (111 LOC)
**Test file:** `tests/unit/ui/screens/strategy_windows/test_orders_window_ctrl.py`
**Covered:** `open` (fleet and planet branches)
**Gaps:**
- `OrdersRegistrar.__init__` (line 31) — Trivial reference storage
**Severity:** MINOR

### 38. `game/ui/screens/test_lab/screen_actions.py` — MAJOR (390 LOC)
**Test files:** `tests/unit/test_lab/test_data_paths.py`, `tests/unit/test_lab/test_render_progress_no_game_handle.py`, `tests/unit/test_lab/test_visual_run.py`
**Covered:** `_render_progress`, `_draw_and_flip` (partially), `_switch_to_battle` (partially), `_on_run`, `_show_ships_json`, `_show_components_json`
**Gaps (heuristic confirmed, 11 untested):**
- `_require_display_surface` (line 86) — Surface initialization check. Tested via `test_render_progress_no_game_handle.py`.
- `_get_engine` (line 104) — One-liner. Not directly tested.
- `_ensure_engine` (line 108) — Engine creation on first access. Not tested.
- `_on_view_battle_states` (line 209) — Battle state viewer launcher. Not tested.
- `_on_use_seed_from_run` (line 232) — Seed copy callback. Not tested.
- `_on_copy_results` (line 238) — Clipboard copy. Not tested.
- `_on_run_visual_baseline` (line 281) — Baseline run. Not tested.
- `_on_run_headless` (line 286) — Headless run. Not tested.
- `_on_run_all_tests` (line 296) — Batch test runner. Not tested.
- `_continue_batch_test` (line 301) — Batch continuation. Not tested.
- `_prompt_for_custom_seed` (line 305) — Tkinter dialog. Not tested.
**Severity:** MAJOR — 11 untested methods; `_on_run_headless`, `_on_run_all_tests`, and `_continue_batch_test` affect test execution UX

### 39. `game/ui/screens/workshop_event_router.py` — MAJOR (592 LOC)
**Test files:** `tests/unit/ui/screens/test_workshop_event_router_add_component.py`, `tests/unit/ui/screens/test_workshop_event_router_select_component.py`, `tests/unit/builder/test_layer_targeted_actions.py`
**Covered:** `_handle_quick_add`, `_handle_move_individual`, `_handle_move_group`, `_handle_select_component_type`, `_handle_select_group`, `_handle_select_individual`, `_handle_remove_group`, `_handle_remove_individual`, `_handle_add_component`
**Gaps (heuristic confirmed, 20 untested):**
- `__init__` (line 36) — Trivial. Not directly tested.
- `_get_vehicle_classes` (line 44) — Registry access. Not tested.
- `handle_event` (line 48) — Main event dispatch. Not tested in isolation.
- `_handle_panel_action` (line 109) — Panel action dispatch. Tested indirectly.
- `_handle_button_pressed` (line 381) — Button press handler. Not tested.
- `_handle_dropdown_changed` (line 417) — Dropdown change handler. Not tested.
- `_apply_confirmation_dropdown` (line 441) — Shared confirmation handler. Not tested.
- `_apply_resolver_dropdown` (line 479) — Shared resolver handler. Not tested.
- `_handle_class_dropdown` (line 501) — Class change handler. Not tested.
- `_handle_vehicle_type_dropdown` (line 517) — Vehicle type handler. Not tested.
- `_handle_movement_dropdown` (line 542) — Movement policy handler. Not tested.
- `_handle_targeting_dropdown` (line 554) — Targeting handler. Not tested.
- `_handle_role_dropdown` (line 566) — Design role handler. Not tested.
- `_handle_confirmation` (line 580) — Dialog confirm handler. Not tested.
**Severity:** MAJOR — 14 untested methods including the main `handle_event` dispatcher and all dropdown/button handlers; these are UI event routing but contain confirmation dialog logic and state mutation

### 40. `game/ui/screens/workshop_ship_io.py` — MINOR (280 LOC)
**Test files:** `tests/unit/builder/test_builder_io_integration.py`, `tests/unit/workshop/test_workshop_ship_io_facade_state.py`
**Covered:** `save_ship`, `load_ship`, `select_target`
**Gaps:**
- `__init__` (line 43) — Multi-parameter constructor. Tested indirectly.
- `_design_catalog` (line 67) — Lazy catalog resolution with null-guard chain. Not directly tested. Has 4 null-check branches.
- `_prompt_design_name` (line 266) — Tkinter dialog wrapper. Not directly tested.
**Severity:** MINOR — `_design_catalog` has a multi-stage null guard chain that isn't covered

### 41. `game/ui/services/image/background.py` — MINOR (288 LOC)
**Test file:** `tests/unit/ui/services/image/test_background.py` (141 lines)
**Covered:** `__init__` validation (null provider, empty prompt), `start`, `cancel`, `status`, `result`, `error`, `wait`, `_run` (error wrapping, unexpected exception wrapping)
**Gaps:**
- `elapsed_seconds` (line 184) — Property with 3 branches (not started, finished, running). Not tested.
- `_run` (line 193) — Partially tested. The success path (DONE status) is tested via `_SlowSuccessProvider`. The `ImageCancelled` path at line 203 and `ImageException` path at line 210 are tested. The `CANCELLED` pre-check at line 197 is tested via `cancel` before `start`.
- `shutdown_all_image_calls` (line 267) — Module-level function. Not tested.
**Severity:** MINOR — `elapsed_seconds` and `shutdown_all_image_calls` are small but untested

---

## Tier 3 (Apparently Covered)

### 42. `game/strategy/data/galaxy_state.py` — VERIFIED (69 LOC)
**Test file:** `tests/unit/strategy/data/test_galaxy_state.py`
**Status:** CONFIRMED. Pure dataclass with no methods — standard construction is tested.

### 43. `game/strategy/engine/turn_engine_settings.py` — VERIFIED (77 LOC)
**Test file:** `tests/unit/strategy/engine/test_turn_engine_settings.py`
**Status:** CONFIRMED. Both `TurnEngineSettings` dataclass and `load_turn_engine_settings` function tested.

### 44. `game/strategy/facade/dto/fleet_hierarchy_dto.py` — VERIFIED (104 LOC)
**Test file:** `tests/unit/strategy/facade/test_fleet_hierarchy_dto.py`
**Status:** CONFIRMED. All 3 DTOs (`ShipInfoExtended`, `SquadronInfo`, `TaskForceInfo`) and their `from_*` factory methods tested.

### 45. `game/ui/screens/strategy_render/dyson_spheres.py` — VERIFIED (129 LOC)
**Test file:** `tests/unit/ui/screens/strategy_render/test_dyson_spheres.py`
**Status:** CONFIRMED. Note: file contains a PRESERVED LATENT BUG (line 104: `screen_diameter` undefined, line 112: same). The bug is documented and flagged for a follow-up ticket, but the test file exists and covers rendering paths.

---

## File Coverage Verification Table

| # | File | LOC | Tier | Tests Exist? | Key Gaps |
|---|---|---|---|---|---|
| 1 | `game/ai/__init__.py` | 109 | 1 | Implicit | __all__ completeness not verified |
| 2 | `game/ai/carrier_controller.py` | 407 | 2 | Yes | 9 private helpers untested |
| 3 | `game/assets/asset_manager.py` | 374 | 2 | Yes | __init__, _load_star_metadata, clear |
| 4 | `game/core/protocols/__init__.py` | 162 | 1 | Implicit | __all__ completeness |
| 5 | `game/core/protocols/registry.py` | 39 | 2* | **YES** | **Baseline error — actually tested** |
| 6 | `game/core/protocols/ui.py` | 112 | 2* | Yes | handle_resize signature never validated |
| 7 | `game/engine/collision.py` | 201 | 2 | Yes | process_ramming (3 damage branches) — MAJOR |
| 8 | `game/simulation/components/abilities/harvester.py` | 181 | 2 | Yes | StagingYardAbility, PlanetaryYardAbility, _parse_attrs branches |
| 9 | `game/simulation/components/ability_manager.py` | 285 | 2 | Yes | _build_index MRO completeness, _get_abilities_polymorphic fallback |
| 10 | `game/simulation/components/component.py` | 406 | 2 | Yes | mark_hp_cache_dirty |
| 11 | `game/simulation/components/component_resource_manager.py` | 112 | 2 | Yes | __init__ |
| 12 | `game/simulation/components/component_stats_calculator.py` | 360 | 2 | Yes | build_formula_context (3 paths), _evaluate_formulas_in_abilities — MAJOR |
| 13 | `game/simulation/entities/ship_validator_helper.py` | 70 | 2 | Yes | __init__ |
| 14 | `game/simulation/entities/stat_contributors/defense.py` | 112 | 3* | **YES** | **Baseline error — comprehensively tested** |
| 15 | `game/simulation/services/design_loader.py` | 130 | 2 | Yes | __init__ null validation |
| 16 | `game/strategy/combat/team_spec_builder.py` | 198 | 2 | Yes | group_fleets_by_owner, compute_owner_to_team_id |
| 17 | `game/strategy/data/carried_vehicle.py` | 115 | 2 | Yes | __post_init__ validation |
| 18 | `game/strategy/data/galaxy_state.py` | 69 | 3 | Yes | None — verified |
| 19 | `game/strategy/data/star_system.py` | 153 | 2 | Yes | __repr__ |
| 20 | `game/strategy/data/stars.py` | 165 | 2 | Yes | __getattr__ legacy shim |
| 21 | `game/strategy/engine/conflict_modifier_collection.py` | 92 | 0* | Indirect | **Module functions not directly tested** — MAJOR |
| 22 | `game/strategy/engine/game_config.py` | 261 | 2 | Yes | _get_default_asset_path, _get_default_players |
| 23 | `game/strategy/engine/order_handlers/launch_fighters.py` | 294 | 2 | Yes | _run_with_issuer (3 error branches), 4 private helpers — MAJOR |
| 24 | `game/strategy/engine/planet_command_handlers.py` | 346 | 2 | Yes | _apply_planet_environmental_target, register |
| 25 | `game/strategy/engine/resupply_engine.py` | 294 | 2 | Yes | __init__, _process_facility_generation, _get_fuel_generation_rate |
| 26 | `game/strategy/engine/superweapon_handlers/__init__.py` | 24 | 0 | **NO** | **Re-export surface not verified** — CRITICAL |
| 27 | `game/strategy/engine/turn_engine.py` | 830 | 2 | Yes | 3 tick-phase logging hooks — MAJOR |
| 28 | `game/strategy/engine/turn_engine_settings.py` | 77 | 3 | Yes | None — verified |
| 29 | `game/strategy/facade/dto/fleet_hierarchy_dto.py` | 104 | 3 | Yes | None — verified |
| 30 | `game/strategy/interfaces/__init__.py` | 58 | 1 | Implicit | __all__ completeness |
| 31 | `game/strategy/interfaces/engines/combat.py` | 112 | 0 | **NO** | **ABC contract never validated** — CRITICAL |
| 32 | `game/strategy/services/ability_metadata.py` | 566 | 2 | Yes | _multiplier_effect, _rate_effect, _energy_drain |
| 33 | `game/strategy/services/fleet_write_service.py` | 136 | 2 | Yes | swap_orders, add_task_force, remove_task_force |
| 34 | `game/ui/__init__.py` | 27 | 1 | Implicit | None |
| 35 | `game/ui/effects/hit_effects.py` | 233 | 2 | Yes | HitEffect.update |
| 36 | `game/ui/screens/builder/grouping_strategies.py` | 79 | 2 | Yes | GroupingStrategy protocol |
| 37 | `game/ui/screens/builder/stat_definitions.py` | 77 | 2 | Yes | StatDefinition.__init__ defaults |
| 38 | `game/ui/screens/race_setup/input_handler.py` | 174 | 2 | Yes | handle (15 event branches, integration only) |
| 39 | `game/ui/screens/strategy_render/dyson_spheres.py` | 129 | 3 | Yes | Preserved latent bug (screen_diameter undefined) |
| 40 | `game/ui/screens/strategy_windows/list_windows.py` | 132 | 2 | Partial | StarListRegistrar entirely untested — MINOR |
| 41 | `game/ui/screens/strategy_windows/orders_window_ctrl.py` | 111 | 2 | Yes | OrdersRegistrar.__init__ |
| 42 | `game/ui/screens/test_lab/screen_actions.py` | 390 | 2 | Yes | 11 untested methods — MAJOR |
| 43 | `game/ui/screens/workshop_event_router.py` | 592 | 2 | Yes | 14 untested methods — MAJOR |
| 44 | `game/ui/screens/workshop_ship_io.py` | 280 | 2 | Yes | _design_catalog, _prompt_design_name |
| 45 | `game/ui/services/image/background.py` | 288 | 2 | Yes | elapsed_seconds, shutdown_all_image_calls |

*Rows marked with `*` represent baseline reclassification (original Tier 0 was incorrect).

---

## Prioritized Remediation Plan

### CRITICAL (2)
1. **`game/strategy/interfaces/engines/combat.py`** — Add `isinstance` conformance tests for `ConflictResolutionEngine` and `EnvironmentalHazardEngine` against their ABCs. Add runtime signature tests for `resolve_all_conflicts` and `process_environmental_tick`.
2. **`game/strategy/engine/superweapon_handlers/__init__.py`** — Add test verifying all 5 `__all__` entries resolve to callable `process_*` functions.

### MAJOR (4 + 3 from Tier 2)
3. **`game/engine/collision.py`** — Add unit tests for `process_ramming`: rammer weaker, target weaker, equal HP, no target, dead ship, non-ramming policy.
4. **`game/simulation/components/component_stats_calculator.py`** — Add tests for `build_formula_context` (no ship, explicit context, ship present). Add tests for `_evaluate_formulas_in_abilities` (runtime variable preservation, nested structure traversal).
5. **`game/strategy/engine/conflict_modifier_collection.py`** — Add direct unit tests for both module-level functions with a mock engine.
6. **`game/strategy/engine/order_handlers/launch_fighters.py`** — Add tests for `_run_with_issuer` error branches (count<=0, insufficient fighters), `_find_ship` not-found, `_mint_group_id` collision.
7. **`game/strategy/engine/turn_engine.py`** — Add tests for the 3 `_tick_phase_log_*` hooks verifying correct tick-gating.
8. **`game/ui/screens/test_lab/screen_actions.py`** — Add tests for `_on_run_headless`, `_on_run_all_tests`, `_continue_batch_test`, `_on_view_battle_states`.
9. **`game/ui/screens/workshop_event_router.py`** — Add tests for `handle_event`, `_handle_button_pressed`, `_handle_dropdown_changed`, `_handle_confirmation`.

### MINOR (17 gaps — address opportunistically)
Mostly `__init__` methods, private factory functions, and `__repr__`/`__getattr__` dunders. Low ROI unless they contain branching logic.

### ADVISORY (10 — `__init__.py` re-exports and Protocol definitions)
No production impact. Address during regular maintenance.
