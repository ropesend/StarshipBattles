# Shard 04 — Test Coverage Audit Report

**Coverage source:** Verified (corrected Phase 1 heuristic)
**File count:** 45 | **LOC estimate:** ~9610
**Tiers verified:** 0=10, 1=4, 2=27, 3=4

## Phase 1 Heuristic Corrections

| File | Heuristic Tier | Actual Tier | Correction |
|------|---------------|-------------|------------|
| `game/ui/screens/transfer_mass_preview.py` | 0 (NO_TESTS) | 2 (PARTIAL) | Tests exist via `test_transfer_mass_preview.py` — but only through `TransferViewModel` wrapper; internal helpers `_resolve_pending_qty`, `_mass_per_unit_for_cargo_key`, `_qty_for_cargo_key`, `_get_catalog` are indirectly exercised |
| `game/ui/services/image/null_provider.py` | 0 (NO_TESTS) | 2 (PARTIAL) | `test_null_provider.py` exists with 4 tests covering `__init__`, `__repr__`, `__str__`, `generate_image` |
| `game/simulation/components/abilities/launch.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/strategy/__init__.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/strategy/engine/handlers/launch_satellites.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/strategy/engine/handlers/recover_fighters.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/strategy/interfaces/engines/population.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/ui/screens/star_data_source.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/ui/screens/strategy_render/__init__.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/ui/screens/test_lab/details/resource_outcomes.py` | 0 (NO_TESTS) | 0 (CONFIRMED) | No test file exists — confirmed |
| `game/strategy/engine/handlers/construction_queue.py` | 2 (PARTIAL) | 2 (CONFIRMED) | Only `SetBuildQueuePausedCommandHandler` tested; `AddTo...`, `RemoveFrom...`, `Reorder...` UNTESTED |

---

## Tier 0 — CRITICAL (Non-UI) / ADVISORY (UI)

### 1. `game/simulation/components/abilities/launch.py` — CRITICAL — NO TESTS
- **LOC:** 176 | **Layer:** simulation | **Severity:** CRITICAL
- **Symbols:** `_LaunchAbilityBase`, `_LaunchAbilityBase._parse_attrs`, `_LaunchAbilityBase.recalculate`, `_LaunchAbilityBase.get_primary_value`, `_LaunchAbilityBase.get_ui_rows`, `StrategicMineLayerAbility`, `StrategicFighterLaunchAbility`, `StrategicSatelliteLaunchAbility`, `TacticalMineLayerAbility`, `TacticalFighterLaunchAbility`, `TacticalSatelliteLaunchAbility`
- **Untested code paths:**
  - `_parse_attrs` — dict path (L73-77), numeric fallback (L78-81), else fallback (L82-85)
  - `recalculate` — multiplier application + rounding (L93-103)
  - `get_primary_value` — L105-106
  - `get_ui_rows` — standard row + conditional launch-rate row (L108-120)
  - All six concrete subclasses — no test exercises their construction/instantiation
- **STAT_BINDINGS** (L55-68): two `AbilityStatBinding` entries — never validated that `recalculate` consumes them correctly
- **Gap:** Entire file has zero test coverage. This is the launch ability skeleton for all six launch types (3 strategic + 3 tactical). These feed into carrier AI, FMS command handlers, and battle engine launch paths.

### 2. `game/strategy/__init__.py` — ADVISORY — NO TESTS
- **LOC:** 79 | **Layer:** strategy | **Severity:** ADVISORY
- **Content:** Re-exports only — `Fleet`, `ShipInstance`, `OrderType`, `Order`, `HexCoord`, `TurnEngine`, `GameSession`, `GameConfig`, `StrategySessionFacade`, `FleetInfo`, `SystemInfo`, `PlanetInfo`, `EmpireInfo`, `IBattleResolver`, `BattleResult`
- **Gap:** No unit test verifies the `__all__` list matches actual re-exports. Import path stability is implicitly tested by other import-dependent tests.

### 3. `game/strategy/engine/handlers/launch_satellites.py` — CRITICAL — NO TESTS
- **LOC:** 155 | **Layer:** strategy | **Severity:** CRITICAL
- **Symbols:** `LaunchSatellitesCommandHandler`, `execute`, `_execute_fleet`, `_execute_planet`, `register`
- **Untested code paths (entire file):**
  - `execute` — invariant check + planet/fleet dispatch (L46-56)
  - `_execute_fleet` — fleet resolution, carrier lookup, bay count, count validation, order creation (L58-108)
  - `_execute_planet` — planet resolution, yard count, count validation, order creation (L110-145)
  - `register` — registry registration (L148-152)
- **Gap:** This handler issues strategic satellite launch orders. It is the only path for launching satellites from carriers or planet staging yards. Completely untested despite being critical to the FMS (Fleet Mine Satellite) command system.

### 4. `game/strategy/engine/handlers/recover_fighters.py` — CRITICAL — NO TESTS
- **LOC:** 110 | **Layer:** strategy | **Severity:** CRITICAL
- **Symbols:** `RecoverFightersCommandHandler`, `execute`, `_execute_fleet`, `_execute_planet`, `register`
- **Untested code paths (entire file):**
  - `execute` — invariant check + planet/fleet dispatch (L41-49)
  - `_execute_fleet` — fleet resolution, carrier lookup, order creation (L51-82)
  - `_execute_planet` — planet resolution, order creation (L84-100)
  - `register` — registry registration (L103-108)
- **Gap:** Same pattern as launch handler. Recovers fighters back into carriers/planets. Zero test coverage.

### 5. `game/strategy/interfaces/engines/population.py` — CRITICAL — NO TESTS
- **LOC:** 134 | **Layer:** strategy | **Severity:** CRITICAL
- **Symbols:** `IPopulationEngine`, `IOrganicsConsumptionEngine`, `IHappinessEngine`
- **Content:** Three ABCs with abstract methods. These are protocol/interface definitions.
- **Gap:** Protocol conformance is implicitly tested by tests of concrete implementations (`OrganicsConsumptionEngine`, `PopulationEngine`, `HappinessEngine`). However, no explicit test verifies that the ABCs' signatures match their concrete implementations, creating a drift risk.
- **Note:** The heuristic listed these as `TIER_0_NO_TESTS`. Given they are ABCs, the lack of dedicated tests is less severe — concrete implementations are tested. But the contract definition itself is untested.

### 6. `game/ui/screens/star_data_source.py` — ADVISORY — NO TESTS
- **LOC:** 71 | **Layer:** UI | **Severity:** ADVISORY
- **Symbols:** `StarDataSource`, `__init__`, `get_star_at_index`, `_stars`, `_render_icon`, `_get_star_icon`, `_make_circle_icon`
- **Untested code paths:**
  - `_get_star_icon` — image_id path with cache hit (L53-54), asset manager load (L57-61), circle fallback (L63-64)
  - `_make_circle_icon` — L66-71
  - `__init__` — delegation to `ListDataSource.__init__` (L26-27)
- **Gap:** UI data source with icon rendering. No dedicated test file. The `ListDataSource` base is tested, but star-specific icon logic is not.

### 7. `game/ui/screens/strategy_render/__init__.py` — ADVISORY — NO TESTS
- **LOC:** 9 | **Layer:** UI | **Severity:** ADVISORY
- **Content:** Docstring only — no code, no re-exports.
- **Gap:** None meaningful. Package marker file.

### 8. `game/ui/screens/test_lab/details/resource_outcomes.py` — ADVISORY — NO TESTS
- **LOC:** 294 | **Layer:** UI | **Severity:** ADVISORY
- **Symbols:** `is_resource_test`, `draw_resource_outcomes`, `_draw_fuel_outcomes`, `_draw_energy_outcomes`, `_draw_ammo_outcomes`
- **Untested code paths:**
  - `is_resource_test` — test_id prefix matching (L18-21)
  - `draw_resource_outcomes` — full rendering path with 3 sub-renderer dispatches (L24-64)
  - `_draw_fuel_outcomes` — 6 value rows + tolerance check + velocity status (L67-141)
  - `_draw_energy_outcomes` — 6 value rows + efficiency calc (L144-214)
  - `_draw_ammo_outcomes` — seeker vs non-seeker branching (L217-294)
- **Gap:** Pure rendering functions. All internal logic (initial/final/consumed calculations, tolerance checks, seeker vs non-seeker branching) is untestable non-parametrically.

### 9. `game/ui/screens/transfer_mass_preview.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 209 | **Layer:** UI (pure math) | **Severity:** MINOR (corrected from TIER_0_NO_TESTS)
- **Tests exist:** `tests/unit/ui/screens/test_transfer_mass_preview.py` (376 LOC, 14 test methods)
- **Tested:** `compute_mass_preview` through `TransferViewModel.compute_mass_preview` — base cases, resource pending, population pending, MAX sentinels, capacity overflow, mass-neutral items
- **Untested internal functions (not directly exercised):**
  - `_resolve_pending_qty` (L119-136) — exercised only indirectly via `compute_mass_preview`; `TypeError/ValueError` catch path (L134-136) not tested
  - `_mass_per_unit_for_cargo_key` (L139-153) — `passengers_` prefix, `drop_pod:`/`vehicle:` prefixes, catalog lookup, unknown key → 0.0
  - `_qty_for_cargo_key` (L156-183) — `passengers_<species>`, bare `passengers`, item keys, resource keys
  - `_get_catalog` (L189-203) — lazy-load path with module-level cache
- **Gap:** Coverage is through `TransferViewModel` wrapper, not the standalone `compute_mass_preview` export from this module. Direct invocation path not tested.

### 10. `game/ui/services/image/null_provider.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 62 | **Layer:** UI | **Severity:** MINOR (corrected from TIER_0_NO_TESTS)
- **Tests exist:** `tests/unit/ui/services/image/test_null_provider.py` (28 LOC, 4 test methods)
- **Tested:** `__init__`, `__repr__`, `__str__`, `generate_image` (raises), protocol conformance
- **Untested:** `PROVIDER_NAME` constant (L19) — implicitly verified by test string assertions
- **Gap:** Well-covered for a 62-LOC file. No significant gaps.

---

## Tier 1 — MAJOR

### 11. `game/simulation/combat/__init__.py` — ADVISORY — NO SYMBOLS
- **LOC:** 20 | **Layer:** simulation | **Severity:** ADVISORY
- **Content:** Re-exports `TargetingSystem`, `DamageCalculator`, `WeaponFiringSystem` with `__all__`
- **Gap:** Import-path stability implicitly tested by downstream consumers. No dedicated import test.

### 12. `game/ui/colors.py` — ADVISORY — CONSTANTS ONLY
- **LOC:** 421 | **Layer:** UI | **Severity:** ADVISORY
- **Content:** Color constant definitions (~200+ named tuples). No functions, no classes, no logic.
- **Gap:** No test verifies color values against design specs. Implicitly tested by UI rendering tests that import specific colors. Color drift is invisible until a visual regression is noticed.

### 13. `game/ui/services/image/__init__.py` — ADVISORY — RE-EXPORTS
- **LOC:** 62 | **Layer:** UI | **Severity:** ADVISORY
- **Content:** Re-exports from submodules + side-effect `register_image_provider("null", NullImageProvider)` on import (L42)
- **Gap:** The side-effect registration at import time (L42) is not explicitly tested. Implicitly verified by factory tests.

### 14. `game/ui/utils/__init__.py` — ADVISORY — RE-EXPORTS
- **LOC:** 57 | **Layer:** UI | **Severity:** ADVISORY
- **Content:** Re-exports from `pygame_utils`, `json_diff`, `formatters`, `portraits`
- **Gap:** Import-path stability. Tests for `test_utils.py` exist but test the submodules, not the `__init__` re-export surface.

---

## Tier 2 — PARTIAL COVERAGE (27 files)

### 15. `game/ai/ai_factory.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 213 | **Layer:** AI | **Test file:** `tests/unit/simulation/factories/test_ai_factory.py`
- **Untested (from heuristic, verified):**
  - `set_engine` (L78-91) — engine injection for `CarrierAIController`
  - `_ship_has_tactical_launch` (L167-192) — static method with `iter_components`, exception handling, ability checks
  - `_resolve_vehicle_type` (L194-200) — fallback to "Ship"
- **Additional gaps:**
  - `_ship_has_tactical_launch` — `is_active` filter path (L181), `has_ability` None check (L183), exception catch for stub iteration failures (L190-191)
  - `create_for_ship` — `CarrierAIController` path when `_engine` is set AND ship has tactical launch (L157-164)
  - `create_for_ship` — `SatelliteAIController` path (L148-151)

### 16. `game/simulation/battle_config.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 73 | **Test file:** `tests/unit/simulation/test_battle_config.py`
- **Untested:** `_default_end_condition` (L28-30) — lazy-import factory function
- **Gap:** Single function. The `BattleConfig` dataclass has good defaults; `_default_end_condition` is a late-import helper that creates a `TeamEliminatedCondition`.

### 17. `game/simulation/entities/ship_layer_manager.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 167 | **Test file:** `tests/unit/simulation/entities/test_ship_layer_manager.py`
- **Untested:** `__init__` (L38-39) — trivial assignment; implicitly covered by method tests
- **Additional gap verification needed:** Layer initialization, hull equipping, class change paths tested.

### 18. `game/strategy/data/container.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 352 | **Test files:** `tests/unit/strategy/data/test_container.py`, `tests/unit/simulation/components/abilities/test_container_ability.py`
- **Heuristic untested (verified):**
  - `_get_resource_catalog` (L80-84) — module-level lazy cache
  - `_resource_mass_per_unit` (L98-108) — raises `KeyError` for unknown resources
  - `Container.__init__` (L121-136) — negative `capacity_mass` check (L130-131)
- **Additional gaps:**
  - `Container.to_dict` (L289-311) — serialization of items with `instance_id`, `mass`, `state`
  - `Container.from_dict` (L313-342) — deserialization with `ContainableKind` reconstruction
  - `Container.accepts` (L176-182) — `allowed_type_ids` filtering
  - `Container.add` — `ItemContainable` with `quantity != 1` error (L202-203)
  - `Container.add` — `PopulationContainable` with `isinstance(quantity, bool)` edge (L211)
  - `Container.remove` — `ItemContainable` by `instance_id` matching (L240-244)
  - `Container.contents` — iterator across all three slices (L264-285)
  - `AddResult` / `RemoveResult` enums — value correctness

### 19. `game/strategy/data/homeworld_presets.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 137 | **Test file:** `tests/unit/strategy/data/test_homeworld_presets.py`
- **Heuristic untested (verified):**
  - `_get_presets_path` (L19-21)
  - `get_preset_id_from_name` (L117-131)
  - `clear_cache` (L134-137)
- **Additional gaps:**
  - `load_homeworld_presets` — cache hit path (L34-35), `None` data or missing "presets" key (L38-39)
  - `apply_preset_to_config` — `preset is None` no-op (L78-79), `base_reproduction_rate` path (L102-103)
  - `get_available_homeworld_names` (L106-114)

### 20. `game/strategy/data/star_generation_config.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 200 | **Test file:** `tests/unit/strategy/data/test_star_generation_config.py`
- **Heuristic untested (verified):**
  - `__init__` (L90-100) — data with "star_generation" key vs fallback
  - `_load_from_json` (L102-151) — all config field reads with defaults
  - `_use_defaults` (L153-176) — all field assignments
- **Additional gaps:**
  - `get_star_generation_config` (L179-200) — cache decorator, `AstrophysicsLoader` success path, exception fallback (ImportError, FileNotFoundError, OSError, TypeError)

### 21. `game/strategy/engine/game_initializer.py` — CRITICAL — HEAVILY UNTESTED
- **LOC:** 446 | **Layer:** strategy | **Test file:** `tests/unit/strategy/engine/test_game_initializer.py`
- **Severity:** CRITICAL (Tier 2 but 446 LOC with 6/10 symbols untested)
- **Heuristic untested (verified):**
  - `_PlanetShortageError` (L36-39)
  - `_wire_fleet_lookups` (L149-181) — fleet-at-hex, fleet-in-system closures
  - `_create_empires` (L183-221) — empire construction from config
  - `_initialize_galaxy` (L223-274) — galaxy type routing, density map, system generation
  - `_empire_home_indices` (L276-300) — N=1 vs N≥2 mode, hand-rolled linspace
  - `_setup_initial_scenario` (L302-397) — per-empire homeworld assignment, `_adjust_homeworld_to_race`, `_ensure_homeworld_resource_quality`, `_PlanetShortageError` raise
- **Untested code paths (detailed):**
  - `initialize` — retry loop (L82-122), seed perturbation (L86-91), `empire_mutator` fallback (L103-108), `ValidationException` after all retries exhausted (L124-136)
  - `_wire_fleet_lookups` — `_at_hex` closure, `_in_system` closure with `hex_distance` + exception handler
  - `_create_empires` — `race_config is None` fallback (L199-208), `get_player_theme_path` (L194)
  - `_initialize_galaxy` — `random.seed` call (L250), `DensityBasedPlacementStrategy` path (L259-262), `generate_warp_lanes` (L271)
  - `_empire_home_indices` — `num_empires <= 1` edge (L292), `round()` based linspace (L297-300)
  - `_setup_initial_scenario` — planet-shortage check (L331-337), per-empire iteration (L344-397), `_adjust_homeworld_to_race`, `PlanetWriteService` lazy construction
  - `_adjust_homeworld_to_race` (L399-433) — `PlanetType` lookup with `KeyError`, preference-driven field setting, gas-factor atmosphere building
  - `_ensure_homeworld_resource_quality` (L435-446) — quality floor enforcement
- **Gap:** Game initialization is the most critical untested area in this shard. The retry loop for N=1 planet shortages, empire creation, galaxy initialization, and homeworld setup are all untested.

### 22. `game/strategy/engine/handlers/construction_queue.py` — CRITICAL — HEAVILY UNTESTED
- **LOC:** 341 | **Layer:** strategy | **Test file:** `tests/unit/strategy/engine/test_set_build_queue_paused_command.py`
- **Severity:** CRITICAL (341 LOC with only 1 of 4 handlers tested)
- **Tested:** `SetBuildQueuePausedCommandHandler` (FEAT-17)
- **Untested (entirely):**
  - `AddToConstructionQueueCommandHandler` (L37-188) — entity resolution, queue resolution, index validation, design validation, cost calculation, queue item creation, insert vs append
  - `RemoveFromConstructionQueueCommandHandler` (L191-229) — entity resolution, queue resolution, index validation, pop
  - `ReorderConstructionQueueCommandHandler` (L232-272) — entity resolution, queue resolution, index validation, pop+insert
  - `register` (L330-341) — registry registration for all 4 handlers
- **Untested helpers:**
  - `_resolve_design_data` (L106-122) — `DesignCatalog` lookup via `session.services`
  - `_check_design_valid` (L124-161) — `DesignValidator` call, `has_issues` check, `ValueError/KeyError` exception path
  - `_load_design_cost` (L163-188) — `DesignCostCalculator` call, design data lookup failure
- **Gap:** The three C(R)UD handlers (Add, Remove, Reorder) for construction queues have zero test coverage. These are fundamental to the build/construction system and affect both planets and fleets.

### 23. `game/strategy/engine/organics_consumption_engine.py` — MAJOR — PARTIAL COVERAGE
- **LOC:** 126 | **Layer:** strategy | **Test file:** `tests/unit/strategy/engine/test_organics_consumption_engine.py`
- **Heuristic untested (verified):**
  - `_get_planet_mutator` (L70-77) — lazy default construction
  - `_validate_tick_inputs` (L79-88) — None-colony detection, `ValidationException` raise
  - `_process_colony` (L100-126) — per-population iteration, consumption ratio caching, stockpile drain
- **Gap:** Core consumption loop has partial coverage. The mutator pattern and validation guard are untested.

### 24. `game/strategy/generation/loaders/galaxy_layouts_loader.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 182 | **Test file:** `tests/unit/strategy/generation/density/test_layout_loader.py`
- **Untested:** `_scale_primitive` (L132-162) — scaling and position field transformation
- **Additional gaps:**
  - `load` — `load_json_required` success and failure paths
  - `get_layout_config` — `ValidationException` raise
  - `scale_layout_for_radius` — primitive list iteration
  - `load_and_scale` — full orchestrator
  - `SCALING_FIELDS` / `POSITION_FIELDS` — constant correctness

### 25. `game/strategy/services/intercept_calculator.py` — MAJOR — PARTIAL COVERAGE
- **LOC:** 189 | **Layer:** strategy | **Test files:** `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py`, `tests/unit/strategy/pathfinding/test_intercept_recursion.py`
- **Heuristic untested (verified):**
  - `_ChaserProxyCapabilities` (L31-38)
  - `_ChaserProxy` (L41-52)
  - `_extract_chaser_info` (L55-66) — `NavigationState` vs `Fleet` duck-typing
  - `InterceptCalculator.__init__` (L92-93) — trivial
  - `_evaluate_intercept_candidates` (L143-189) — candidate scoring loop
- **Untested code paths (detailed):**
  - `calculate_intercept_point` — `chaser_speed <= 0` (L116-117), fallback to `target_fleet.location` (L139), project_fleet_path empty (L123)
  - `_evaluate_intercept_candidates` — `path_to_target` empty (L169-170), `best_intercept is not None` break condition (L186-187), near-exact intercept break (L180-181)
  - `project_fleet_path` — module-level function (L69-81)

### 26. `game/strategy/services/replay_verification_coordinator.py` — MINOR — GOOD COVERAGE
- **LOC:** 441 | **Test file:** `tests/unit/strategy/services/test_replay_verification_coordinator.py`
- **Untested:** `_worker_loop` (L288-324), `_write_sidecar` (L387-409)
- **Gap:** Internal worker methods. The `_worker_loop` is the background thread loop; `_write_sidecar` is a thin wrapper over `write_verification_sidecar`. Both are indirectly exercised by integration-level coordinator tests.

### 27. `game/strategy/services/strategic_ability_scanner.py` — MAJOR — PARTIAL COVERAGE
- **LOC:** 423 | **Layer:** strategy | **Test file:** `tests/unit/strategy/services/test_strategic_ability_scanner.py`
- **Heuristic untested (verified):**
  - `find_harvest_boosters_for_colony` (L64-189) — full PROJ-412 pipeline with `IAbilitySource` walk, scope filtering, owner filtering, dedup
  - `_is_component_functionally_active` (L376-394) — activation state lookup
  - `_extract_ability` (L397-423) — delegation to `extract_abilities_from_component`
- **Untested code paths (detailed):**
  - `find_harvest_boosters_for_colony` — `galaxy is None`/`empire is None` guard (L103-104), `get_system`/`get_global_hex` attribute checks (L106-109), `system is None` (L111-112), `colony_hex is None` guard (L170-171), `source.affects_hex` exception catch (L175-176), scope routing (168-185)
  - `_is_component_functionally_active` — `getattr` returns None (L391-392)
  - `_extract_ability` — dict vs list return shape
- **Gap:** The `find_harvest_boosters_for_colony` function (153 LOC) is the main gap — it's the PROJ-412 universal ability pipeline entry point and has zero coverage.

### 28. `game/strategy/services/system_effects_collector.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 411 | **Test files:** `tests/unit/strategy/services/test_system_effects_collector.py`, `tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py`
- **Untested:** `_build_provider` (L158-192) — builds provider dicts from source+entry pairs
- **Additional gaps:**
  - `_collect_providers` — `affects_hex` exception catch (L230-234), `get_abilities` exception catch (L237-242), owner-aware scope violation detection (L260-270)
  - `_aggregate_value` — D16 mixed-kind validation (L330-346), rate-adaptation (L351-356)
  - `_aggregate_status` — precedence chain (L291-307)

### 29. `game/ui/screens/builder/interaction_controller.py` — ADVISORY — UI EVENTS
- **LOC:** 132 | **Layer:** UI | **Test file:** `tests/unit/builder/test_builder_interaction.py`
- **Untested:** `handle_event` (L61-104), `update` (L106-112)
- **Gap:** UI event handling methods. These are pygame event-loop methods that are inherently hard to unit-test.

### 30. `game/ui/screens/event_log_window.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 735 | **Test files:** 5 test files including `test_event_log_window.py`
- **Heuristic untested (verified):**
  - `EventLogUiBuilder` (L77-86)
  - `_init_layout` (L208-264)
  - `_create_filter_buttons` (L266-319)
  - `_update_filter_buttons` (L374-380)
  - `update_events_only` (L615-640)
- **Gap:** Layout and widget-construction methods. These are UI construction code; the `EventLogUiBuilder` pattern allows stubbing in tests.

### 31. `game/ui/screens/fleet_data_source.py` — MAJOR — HEAVILY UNTESTED
- **LOC:** 332 | **Test file:** `tests/unit/ui/screens/test_fleet_data_source.py`
- **Heuristic untested (18/24 symbols, verified):**
  - `__init__` — trivial (L60-68)
  - `_get_column_handlers` — handler dict construction (L129-148)
  - `_get_column_value` — dispatch logic (L150-175)
  - `_format_status`, `_format_resources`, `_format_serial`, `_format_design`, `_format_name`, `_format_hp_pct`, `_format_tonnage`, `_format_speed`, `_format_warp`, `_format_spaceyard`, `_format_transport`, `_format_cargo`
  - `_get_ship_image` (L272-318) — portrait vs topdown routing
  - `_create_placeholder` (L320-332)
- **Gap:** Column value formatting functions — the core business logic of the data source. Many are untested despite having logic branches (e.g., `_format_status` with DESTROYED/DERELICT/DAMAGED/OK states, `_format_resources` with resource abbreviation mapping, `_format_warp` with late-import branching).

### 32. `game/ui/screens/per_player_ui_state.py` — MINOR — GOOD COVERAGE
- **LOC:** 57 | **Test file:** `tests/unit/ui/screens/test_per_player_ui_state.py`
- **Untested:** `__init__` (L34-35) — trivial assignment
- **Gap:** Minimal. Core save/load/has/discard tested.

### 33. `game/ui/screens/planet_abilities_controller.py` — MAJOR — PARTIAL COVERAGE
- **LOC:** 257 | **Test file:** `tests/unit/ui/screens/test_planet_abilities_controller_scanner.py`
- **Heuristic untested (verified):**
  - `__init__` (L96-99) — trivial
  - `get_component_status` (L189-207) — status string formatting
  - `is_component_active` (L213-225) — phase check
  - `toggle_ability` (L229-248) — command dispatch
- **Untested code paths:**
  - `get_component_status` — `ActivationPhase.ACTIVATING` (L203-205), `DEACTIVATING` (L206-208), `ACTIVE` (L209-210), fallback "Inactive" (L211)
  - `is_component_active` — `facility is None` guard (L222-223)
  - `toggle_ability` — `DeactivatePlanetAbilityCommand` path (when `is_active=True`)
- **Gap:** Controller command emission and status formatting are untested.

### 34. `game/ui/screens/planet_data_source.py` — MAJOR — PARTIAL COVERAGE
- **LOC:** 100 | **Test file:** `tests/unit/ui/screens/test_planet_data_source.py`
- **Heuristic untested (verified):**
  - `__init__` (L25-48) — trivial
  - `_planets` (L56-59) — property alias
  - `_render_icon` (L61-62) — delegation
  - `_get_planet_icon` (L64-94) — image_id path, rotation, asset manager load, missing texture fallback
  - `_get_blank_icon` (L96-100) — cache path
- **Gap:** Image rendering methods are untested. These use pygame surfaces and asset manager calls that are hard to mock in unit tests.

### 35. `game/ui/screens/planet_list_event_router.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 301 | **Test files:** `tests/unit/ui/screens/test_planet_list_components.py`, `tests/unit/ui/screens/test_planet_list_window.py`
- **Heuristic untested (verified):**
  - `process_event` (L47-163) — full event dispatch
  - `_set_all_filters` (L169-181) — batch filter toggle
  - `_set_all_effects` (L183-189) — FEAT-25 batch effects
  - `_toggle_filter` (L191-199) — single filter toggle
  - `_navigate_to_selected` (L205-220) — camera navigation
- **Gap:** Event router is implicitly tested through window-level integration tests.

### 36. `game/ui/screens/race_setup/renderer.py` — ADVISORY — UI MODALS
- **LOC:** 234 | **Test files:** `tests/unit/ui/screens/test_race_setup_screen.py`
- **Heuristic untested (verified):**
  - `close_save_update_dialog` (L131-138) — kill + clear
  - `close_llm_dialog` (L182-188) — kill + clear
  - `close_llm_error_popup` (L222-226) — kill + clear
- **Gap:** Dialog close methods. These are UI widget lifecycle management; implicitly tested through screen-level tests.

### 37. `game/ui/screens/race_validator.py` — MINOR — PARTIAL COVERAGE
- **LOC:** 96 | **Test file:** `tests/unit/ui/screens/test_race_validator.py`
- **Heuristic untested:** `__init__` (L34-36) — `RacePointBudget` construction
- **Additional gap:** `validate` — `RacePointBudget.get_remaining_points()` overflow check (L89-94)
- **Severity:** MINOR. The `validate` method is tested; only the budget boundary edge case may be uncovered.

### 38. `game/ui/screens/strategy_colonization.py` — MAJOR — HEAVILY UNTESTED
- **LOC:** 273 | **Test files:** `tests/unit/ui/screens/test_strategy_colonization.py`
- **Heuristic untested (verified):**
  - `__init__` (L28-37)
  - `issue_colonize_order` (L117-142)
  - `queue_colonize_mission` (L191-222)
  - `request_colonize_order` (L224-244)
  - `_resolve_planet_global_hex` (L259-273)
- **Untested code paths:**
  - `issue_colonize_order` — successful command path (L137-142), failed command path (L138-140)
  - `queue_colonize_mission` — `planet_id = planet.id if planet else None` (L208), success/failure return paths
  - `request_colonize_order` — `planet` truthy path (L236-242) with planet global hex resolution, `_resolve_planet_global_hex` returns None (L240-242)
  - `handle_colonize_designation` (L144-189) — mouse-target designation workflow
  - `on_colonize_click` (L51-115) — fleet-at-system, fleet-in-deep-space, zone registry check
- **Gap:** Core colonization command-issuing methods are untested.

### 39. `game/ui/screens/strategy_render/grid.py` — ADVISORY — RENDERING
- **LOC:** 175 | **Test files:** `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py`, `tests/unit/ui/screens/strategy_render/test_grid_cache.py`
- **Heuristic untested (verified):**
  - `GridLayer.__init__` (L119-121)
  - `GridLayer._ensure_surface` (L150-159)
- **Gap:** Renderer internals. Cache logic is tested (`test_grid_cache.py`); `__init__` is trivial.

### 40. `game/ui/screens/strategy_ui.py` — ADVISORY — UI FACADE
- **LOC:** 567 | **Test files:** `tests/unit/ui/screens/test_strategy_ui_menu.py`, `tests/unit/ui/screens/test_strategy_ui_tooltips.py`
- **Heuristic untested (44/56 symbols):** Most methods are UI delegation (window opening, context menus, event routing).
- **Untested methods (sample):**
  - `_get_planetary_ids` (L28-31) — LRU-cached resource catalog query
  - `__getattr__` (L129-140) — widget attribute delegation
  - `_apply_hotkey_tooltips` (L146-148)
  - `open_fleet_context_menu` (L186-215) — menu construction + clamping
  - `close_fleet_context_menu` (L217-221)
  - `open_planet_context_menu` (L227-248)
  - `close_planet_context_menu` (L250-254)
  - `_build_planet_menu_callbacks` (L256-267)
  - `_build_fleet_menu_callbacks` (L269-280)
  - `_on_fleet_context_menu_action` (L282-294)
  - `hide_ui` / `show_ui` (L300-315)
  - `handle_resize` (L318-333)
  - `show_system_info` / `show_sector_info` (L335-350)
  - 29 additional window-management delegation methods
- **Gap:** StrategyUI is a facade/delegator — most methods delegate to sub-managers. The delegation pattern itself is thin and low-risk for bugs. All severity is ADVISORY.

### 41. `game/ui/services/modifier_icon_service.py` — MINOR — GOOD COVERAGE
- **LOC:** 87 | **Test files:** `tests/unit/ui/services/test_modifier_icon_service.py`
- **Untested:** `__init__` (L37-46) — trivial
- **Gap:** `get_icon` — fallback `mod_{id}.png` path (L63-64) when not in map, `os.path.exists` failure for mapped keys (L70-71)
- **Severity:** MINOR. Core icon loading covered.

---

## Tier 3 — APPARENTLY COVERED (4 files)

### 42. `game/research/systems/research_service.py` — LIKELY COVERED
- **LOC:** 232 | **Test files:** `tests/unit/research/test_research_service.py`, `tests/unit/research/test_research_service_edge_cases.py`
- **Heuristic:** 4/4 symbols tested
- **Gap check:** `process_turn` — locked-node decay path (L77-93), `rp_allocation <= 0` skip (L103-115), `calculate_added_chance` (L188-203), `estimate_turns_to_breakthrough` (L206-232)
- **Likely covered by edge case tests.**

### 43. `game/simulation/physics_constants.py` — COVERED
- **LOC:** 72 | **Test file:** `tests/unit/simulation/test_physics_constants.py`
- **Heuristic:** 2/2 symbols tested
- **Functions:** `compute_acceleration`, `compute_max_speed` — both have zero-mass guard clauses tested.

### 44. `game/strategy/engine/session/persistence_adapter.py` — COVERED
- **LOC:** 227 | **Test files:** `tests/unit/strategy/engine/session/test_persistence_adapter.py`, `tests/unit/strategy/engine/test_restore_path_parity.py`
- **Heuristic:** 3/3 symbols tested

### 45. `game/strategy/services/ship_instance_factory.py` — COVERED
- **LOC:** 173 | **Test files:** `tests/unit/strategy/services/test_ship_instance_factory.py`
- **Heuristic:** 3/3 symbols tested
- **Gap note:** `build_full_hp_components_from_design` — `ShipSerializer.from_dict` exception catch (L60-65), `registries is None` guard (L53-54)

---

## Summary Statistics

| Severity | Count | Details |
|----------|-------|---------|
| **CRITICAL** | 8 | 6 truly untested Tier 0 files + 2 heavily untested Tier 2 files (`game_initializer`, `construction_queue`) |
| **MAJOR** | 9 | `organics_consumption_engine`, `intercept_calculator`, `strategic_ability_scanner`, `fleet_data_source`, `planet_abilities_controller`, `planet_data_source`, `strategy_colonization`, `population.py` (ABC untested), `construction_queue.py` |
| **MINOR** | 14 | Partial coverage gaps across Tier 2 files |
| **ADVISORY** | 14 | UI rendering/event, `__init__.py` re-exports, constants-only files |

### Top 10 Priority Gaps

| Priority | File | LOC | Gap |
|----------|------|-----|-----|
| 1 | `game/simulation/components/abilities/launch.py` | 176 | Entirely untested — 6 launch ability classes |
| 2 | `game/strategy/engine/game_initializer.py` | 446 | 60% untested — galaxy/empire initialization, retry loop |
| 3 | `game/strategy/engine/handlers/construction_queue.py` | 341 | 3/4 handlers untested (Add, Remove, Reorder) |
| 4 | `game/strategy/engine/handlers/launch_satellites.py` | 155 | Entirely untested — satellite launch handler |
| 5 | `game/strategy/engine/handlers/recover_fighters.py` | 110 | Entirely untested — fighter recovery handler |
| 6 | `game/strategy/services/strategic_ability_scanner.py` | 423 | `find_harvest_boosters_for_colony` untested |
| 7 | `game/ui/screens/strategy_colonization.py` | 273 | Command methods untested (issue, queue, request) |
| 8 | `game/ui/screens/fleet_data_source.py` | 332 | 18/24 symbols untested — all format methods |
| 9 | `game/ui/screens/planet_abilities_controller.py` | 257 | `toggle_ability`, `get_component_status` untested |
| 10 | `game/strategy/services/intercept_calculator.py` | 189 | `_evaluate_intercept_candidates` untested |

### Phase 1 Heuristic Accuracy

| Metric | Value |
|--------|-------|
| Correct tier assignments | 43/45 (95.6%) |
| Files with wrong tier | 2 (`transfer_mass_preview.py`, `null_provider.py` — both marked TIER_0_NO_TESTS but have tests) |
| Symbol coverage accuracy | ~85% (most untested-symbol lists were correct) |

---

## File Coverage Verification Table

| # | File | LOC | Tier | Test File(s) | Coverage | Severity |
|---|------|-----|------|-------------|----------|----------|
| 1 | `game/ai/ai_factory.py` | 213 | 2 | `test_ai_factory.py` | PARTIAL (6/9 sym) | MINOR |
| 2 | `game/research/systems/research_service.py` | 232 | 3 | `test_research_service.py`, edge_cases | COVERED (4/4) | — |
| 3 | `game/simulation/battle_config.py` | 73 | 2 | `test_battle_config.py` | PARTIAL (1/2 sym) | MINOR |
| 4 | `game/simulation/combat/__init__.py` | 20 | 1 | indirect | RE-EXPORT | ADVISORY |
| 5 | `game/simulation/components/abilities/launch.py` | 176 | 0 | **NONE** | **0/11 symbols** | **CRITICAL** |
| 6 | `game/simulation/entities/ship_layer_manager.py` | 167 | 2 | `test_ship_layer_manager.py` | PARTIAL (4/5) | MINOR |
| 7 | `game/simulation/physics_constants.py` | 72 | 3 | `test_physics_constants.py` | COVERED (2/2) | — |
| 8 | `game/strategy/__init__.py` | 79 | 0 | **NONE** | **0 symbols (re-exports)** | ADVISORY |
| 9 | `game/strategy/data/container.py` | 352 | 2 | `test_container.py` | PARTIAL (19/22) | MINOR |
| 10 | `game/strategy/data/homeworld_presets.py` | 137 | 2 | `test_homeworld_presets.py` | PARTIAL (4/7) | MINOR |
| 11 | `game/strategy/data/star_generation_config.py` | 200 | 2 | `test_star_generation_config.py` | PARTIAL (2/5) | MINOR |
| 12 | `game/strategy/engine/game_initializer.py` | 446 | 2 | `test_game_initializer.py` | **POOR (4/10)** | **CRITICAL** |
| 13 | `game/strategy/engine/handlers/construction_queue.py` | 341 | 2 | `test_set_build_queue_paused_command.py` | **POOR (5/12)** | **CRITICAL** |
| 14 | `game/strategy/engine/handlers/launch_satellites.py` | 155 | 0 | **NONE** | **0/5 symbols** | **CRITICAL** |
| 15 | `game/strategy/engine/handlers/recover_fighters.py` | 110 | 0 | **NONE** | **0/5 symbols** | **CRITICAL** |
| 16 | `game/strategy/engine/organics_consumption_engine.py` | 126 | 2 | `test_organics_consumption_engine.py` | PARTIAL (3/6) | MAJOR |
| 17 | `game/strategy/engine/session/persistence_adapter.py` | 227 | 3 | `test_persistence_adapter.py` | COVERED (3/3) | — |
| 18 | `game/strategy/generation/loaders/galaxy_layouts_loader.py` | 182 | 2 | `test_layout_loader.py` | PARTIAL (6/7) | MINOR |
| 19 | `game/strategy/interfaces/engines/population.py` | 134 | 0 | **NONE** | **0/6 symbols** | MAJOR |
| 20 | `game/strategy/services/intercept_calculator.py` | 189 | 2 | `test_hybrid_and_intercept.py` | PARTIAL (5/12) | MAJOR |
| 21 | `game/strategy/services/replay_verification_coordinator.py` | 441 | 2 | `test_replay_verification_coordinator.py` | GOOD (11/13) | MINOR |
| 22 | `game/strategy/services/ship_instance_factory.py` | 173 | 3 | `test_ship_instance_factory.py` | COVERED (3/3) | — |
| 23 | `game/strategy/services/strategic_ability_scanner.py` | 423 | 2 | `test_strategic_ability_scanner.py` | PARTIAL (5/8) | MAJOR |
| 24 | `game/strategy/services/system_effects_collector.py` | 411 | 2 | `test_system_effects_collector.py` | GOOD (9/10) | MINOR |
| 25 | `game/ui/colors.py` | 421 | 1 | indirect | CONSTANTS ONLY | ADVISORY |
| 26 | `game/ui/screens/builder/interaction_controller.py` | 132 | 2 | `test_builder_interaction.py` | PARTIAL (4/6) | ADVISORY |
| 27 | `game/ui/screens/event_log_window.py` | 735 | 2 | `test_event_log_window.py` +4 more | PARTIAL (18/23) | MINOR |
| 28 | `game/ui/screens/fleet_data_source.py` | 332 | 2 | `test_fleet_data_source.py` | **POOR (6/24)** | **MAJOR** |
| 29 | `game/ui/screens/per_player_ui_state.py` | 57 | 2 | `test_per_player_ui_state.py` | GOOD (5/6) | MINOR |
| 30 | `game/ui/screens/planet_abilities_controller.py` | 257 | 2 | `test_planet_abilities_controller_scanner.py` | PARTIAL (5/9) | MAJOR |
| 31 | `game/ui/screens/planet_data_source.py` | 100 | 2 | `test_planet_data_source.py` | PARTIAL (2/7) | MAJOR |
| 32 | `game/ui/screens/planet_list_event_router.py` | 301 | 2 | `test_planet_list_components.py` etc. | PARTIAL (5/10) | MINOR |
| 33 | `game/ui/screens/race_setup/renderer.py` | 234 | 2 | `test_race_setup_screen.py` | PARTIAL (6/9) | ADVISORY |
| 34 | `game/ui/screens/race_validator.py` | 96 | 2 | `test_race_validator.py` | PARTIAL (2/3) | MINOR |
| 35 | `game/ui/screens/star_data_source.py` | 71 | 0 | **NONE** | **0/7 symbols** | ADVISORY |
| 36 | `game/ui/screens/strategy_colonization.py` | 273 | 2 | `test_strategy_colonization.py` | **POOR (7/12)** | **MAJOR** |
| 37 | `game/ui/screens/strategy_render/__init__.py` | 9 | 0 | **NONE** | PACKAGE MARKER | ADVISORY |
| 38 | `game/ui/screens/strategy_render/grid.py` | 175 | 2 | `test_grid_and_storms.py` + cache | GOOD (4/6) | ADVISORY |
| 39 | `game/ui/screens/strategy_ui.py` | 567 | 2 | `test_strategy_ui_menu.py` etc. | POOR (12/56) | ADVISORY |
| 40 | `game/ui/screens/test_lab/details/resource_outcomes.py` | 294 | 0 | **NONE** | **0/5 symbols** | ADVISORY |
| 41 | `game/ui/screens/transfer_mass_preview.py` | 209 | 2* | `test_transfer_mass_preview.py` | GOOD (through VM) | MINOR |
| 42 | `game/ui/services/image/__init__.py` | 62 | 1 | indirect | RE-EXPORT | ADVISORY |
| 43 | `game/ui/services/image/null_provider.py` | 62 | 2* | `test_null_provider.py` | GOOD (5/5) | MINOR |
| 44 | `game/ui/services/modifier_icon_service.py` | 87 | 2 | `test_modifier_icon_service.py` | GOOD (3/4) | MINOR |
| 45 | `game/ui/utils/__init__.py` | 57 | 1 | `test_utils.py` | RE-EXPORT | ADVISORY |

**Legend:** `*` = corrected from Phase 1 heuristic; `—` = no severity (adequately covered)

---

## Recommendations

1. **Immediate (CRITICAL):** Write tests for `launch.py` (6 ability classes) — these feed into carrier AI, FMS commands, and battle engine launch paths.
2. **Immediate (CRITICAL):** Write tests for `game_initializer.py` — cover the retry loop, empire creation, galaxy initialization, and homeworld setup.
3. **Immediate (CRITICAL):** Write tests for `construction_queue.py` Add/Remove/Reorder handlers.
4. **Immediate (CRITICAL):** Write tests for `launch_satellites.py` and `recover_fighters.py` command handlers.
5. **High (MAJOR):** Write tests for `strategic_ability_scanner.find_harvest_boosters_for_colony` and `intercept_calculator._evaluate_intercept_candidates`.
6. **High (MAJOR):** Add tests for `fleet_data_source.py` format methods and `planet_abilities_controller.py` toggle/status methods.
7. **Medium (MINOR):** Add coverage for internal helper functions in `transfer_mass_preview.py`, `container.py`, `homeworld_presets.py`, `star_generation_config.py`.
