# Pattern Conformance Review: Shard 01
## Summary
- Shard: Shard 01
- Files in Scope: 183
- Files Actually Read: 183
- Total Findings: 5
- Critical: 0 | Major: 0 | Minor: 5

## Layer Dependency Violations

No layer dependency violations reported. The per-shard `layer_violations_01.json` contains zero violations. Manual verification confirms:
- All simulation→strategy imports are TYPE_CHECKING-only
- Strategy→UI imports are absent
- Engine→Simulation imports are absent

## Pattern Bypass Findings

No pattern bypass findings. All critical bypass patterns verified clean:

- **Registry DI (#3)**: No simulation code calls `get_default_registry_provider()`. `VehicleDesignService` requires `registries` via constructor. `BattleEngine` receives AI factory and registries via injection. `ConsumableManagementEngine` enforces `registries is None` guard. `FleetAuraManager` receives `modifier_stack` via `initialize()` call.
- **Facade / Delegate (#5)**: `StrategySessionFacade` properly wraps `GameSession`. UI screens go through facade DTOs for reads and command dispatch for writes. `StrategyScreen` creates `GameSession` only at construction time (see MINOR finding below).
- **CQRS-lite (#6)**: All facade DTOs (`EmpireInfo`, `PlanetInfo`, `FleetInfo`, `SquadronInfo`, `TaskForceInfo`, `ShipInfoExtended`, `ColonyDemographicView`) use `@dataclass(frozen=True)`. `ColonyDemographicView.__post_init__` enforces `MappingProxyType` for `total_upkeep`. No DTO mutation detected.
- **Protocol + TypeGuard (#2)**: `game/core/protocols/strategy_domain.py` defines `@runtime_checkable` protocols with duck-typed TypeGuards (`is_empire`, `is_facility`, `is_ship_instance`). Transfer handler uses `is_planet()` / `is_fleet()` guards rather than `isinstance()` against concrete types.
- **CommandHandlerRegistry (#7)**: `command_handlers.py` is a documented re-export shim. Dispatches through registry via `command_spec` decorator + `register()` function. `superweapon_command_handlers.py` correctly uses `@command_spec` decorator pattern with `register(registry)` module-level function.
- **Two-Phase Ability Aggregation (#14)**: `ability_aggregator.py::_aggregate_ability_groups` implements MAX-within-group / SUM-across-groups. `FleetAuraManager._recalculate()` delegates to it. `calculate_ability_totals()` uses the same shared helper.
- **Scope-Driven Team Routing (#25)**: `compiler_bypass` correctly uses `emit_entries_for_ability()` from the registry. `OPPONENT_SCOPES` is the single source of truth. No duplicated scope sets found. N-team fan-out handled by `_route_team_ids` in the registry.
- **Ability-Stat Registry (#26)**: `ABILITY_STAT_REGISTRY` is the authoritative mapping. `emit_entries_for_ability()` is the documented entry point. `ModifierEntry` objects constructed in only two places: (a) inside `emit_entries_for_ability()` (registry entry point), (b) `replay_serialization.py` (deserialization of previously emitted entries).
- **Strategy Modal Window (#31)**: `StrategyModalWindow` subclassed by `PlanetAbilitiesWindow`, `StarListWindow`, `PlanetSelectionWindow`, `EventLogWindow`, `EmpireBuildQueueWindow`, `BuildQueueListWindow`, `EmpirePanelWindow`, `FleetReportWindow`. Windows using `on_close_callback` are documented legacy slot cleanup (Pattern #30, maintained for existing slots only).
- **Per-Battle RNG (#18)**: `BattleEngine._initialize_start_state()` initializes `self.rng = random.Random(seed)` and injects it into `CollisionSystem`, `DamageCalculator`, and `AIControllerFactory`. No module-level `random.*` calls in simulation/engine/AI.
- **Config Classes (#12)**: Core config (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleTuning`, `LLMConfig`, `ImageConfig`) are all plain classes with class-level attributes. No `@dataclass` decorators. Pattern conforming.

## Naming Collisions

No undocumented naming collisions. `EventBus` appears in both `game/core/event_logging.py` and `game/ui/screens/builder/event_bus.py` — this is **explicitly documented** in the Patterns doc (Critical Naming Reminders section) as two distinct, intentionally separate event buses for different scopes (strategy logging vs. workshop UI).

## Configuration Conventions

#### MINOR: Raw `json.load` instead of `json_utils` in strategy data generators
**ID:** PAT-01-001
**Location:** `game/strategy/data/galaxy_system_generator.py:229`
**Issue:** Uses `json.load(f)` directly instead of `game.core.json_utils` helpers (`load_json`, `load_json_required`, etc.).
**Recommendation:** Replace with `load_json(str(path))` for consistent error handling and atomic save semantics.
**LOC affected:** 1

#### MINOR: Raw `json.load` instead of `json_utils` in warp generator
**ID:** PAT-01-002
**Location:** `game/strategy/data/galaxy_warp_generator.py:368`
**Issue:** Uses `json.load(f)` directly instead of `game.core.json_utils` helpers.
**Recommendation:** Replace with `load_json(str(path))`.
**LOC affected:** 1

#### MINOR: Raw `json.load` instead of `json_utils` in economy config
**ID:** PAT-01-003
**Location:** `game/strategy/config/economy_config.py:106`
**Issue:** Uses `json.load(fh)` directly instead of `game.core.json_utils` helpers. The module explicitly chose the `get_default_* / set_default_*` singleton pattern over `@lru_cache` (noted in its docstring), but the JSON loading still bypasses `json_utils`.
**Recommendation:** Replace with `load_json(resolved)` for consistency with other strategy config loaders (`replay_store.py`, `replay_verification_sidecar.py`).
**LOC affected:** 1

#### MINOR: Facade bypass during construction
**ID:** PAT-01-004
**Location:** `game/ui/screens/strategy_screen.py:81-83`
**Issue:** `StrategyScreen.__init__` creates `GameSession(ai_factory=AIControllerFactory())` directly when no session is passed, then wraps it in `StrategySessionFacade`. Pattern #5 says "UI never touches GameSession directly." This is construction-only (the session is immediately passed to the facade), but still imports and instantiates a strategy-internal class.
**Recommendation:** Move GameSession creation to a factory or composition root. The `strategy_screen_composition.py` Pattern #32 (Compositional Construction) seam already exists for most collaborators; add a `make_game_session()` slot.
**LOC affected:** 3

#### MINOR: Direct GameSession access in lifecycle helpers
**ID:** PAT-01-005
**Location:** `game/ui/screens/strategy_screen_lifecycle.py:32-33`
**Issue:** `on_design_click()` accesses `screen.session.active_empire` and `screen.session` directly rather than going through `screen._facade`. This is utility code that escaped the facade boundary.
**Recommendation:** Replace `screen.session.active_empire` with a facade getter and `screen.session` with facade access.
**LOC affected:** 2

## Undocumented Patterns Found

None. All recurring patterns observed in this shard match documented patterns #1-35 in `docs/02_PATTERNS.md`.

## File Coverage Verification
| File | Status |
|------|--------|
| `game/simulation/services/vehicle_design_service.py` | Read ✓ |
| `game/simulation/components/abilities/markers.py` | Read ✓ |
| `game/ui/panels/race_summary_panel.py` | Read ✓ |
| `game/ui/panels/race_identity_panel.py` | Read ✓ |
| `game/ui/screens/battle_setup/panels/center_panel.py` | Read ✓ |
| `game/strategy/data/planetary_facility.py` | Read ✓ |
| `game/ui/screens/race_setup/input_handler.py` | Read ✓ |
| `game/simulation/systems/battle_engine.py` | Read ✓ |
| `game/strategy/facade/slices/empire_slice.py` | Read ✓ |
| `game/strategy/data/habitability_factors.py` | Read ✓ |
| `game/core/protocols/strategy_domain.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/_draw_helpers.py` | Read ✓ |
| `game/ui/panels/component_modifier_grid_panel.py` | Read ✓ |
| `game/engine/__init__.py` | Read ✓ |
| `game/ui/utils/formatters.py` | Read ✓ |
| `game/core/string_utils.py` | Read ✓ |
| `game/strategy/services/ability_sources/labels.py` | Read ✓ |
| `game/strategy/data/ship_display_formatter.py` | Read ✓ |
| `game/__init__.py` | Read ✓ |
| `game/strategy/engine/superweapon_command_handlers.py` | Read ✓ |
| `game/simulation/combat/weapon_firing_system.py` | Read ✓ |
| `game/ui/screens/strategy_render/dyson_spheres.py` | Read ✓ |
| `game/simulation/components/modifier_introspection.py` | Read ✓ |
| `game/ui/screens/race_setup/controller.py` | Read ✓ |
| `game/services/llm/provider.py` | Read ✓ |
| `game/app.py` | Read ✓ |
| `game/ui/screens/empire_build_queue_viewmodel.py` | Read ✓ |
| `game/simulation/components/ability_manager.py` | Read ✓ |
| `game/ui/screens/cargo_quick_dialog_controller.py` | Read ✓ |
| `game/simulation/components/abilities/harvester.py` | Read ✓ |
| `game/strategy/generation/density/primitives/radial.py` | Read ✓ |
| `game/simulation/services/battle_service.py` | Read ✓ |
| `game/strategy/generation/loaders/system_blueprints_loader.py` | Read ✓ |
| `game/simulation/validation/base.py` | Read ✓ |
| `game/services/llm/__init__.py` | Read ✓ |
| `game/ui/screens/planet_abilities_window.py` | Read ✓ |
| `game/simulation/entities/stat_contributors/command.py` | Read ✓ |
| `game/strategy/data/ship_instance_bridge.py` | Read ✓ |
| `game/simulation/components/modifier_manager.py` | Read ✓ |
| `game/ui/services/image/null_provider.py` | Read ✓ |
| `game/core/return_destination.py` | Read ✓ |
| `game/strategy/services/race_resolver.py` | Read ✓ |
| `game/strategy/facade/dto/colony_demographic_view.py` | Read ✓ |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | Read ✓ |
| `game/services/__init__.py` | Read ✓ |
| `game/ui/screens/strategy_fleet_ops.py` | Read ✓ |
| `game/strategy/engine/game_initializer.py` | Read ✓ |
| `game/ui/screens/battle_ui.py` | Read ✓ |
| `game/ui/screens/galaxy_test/__init__.py` | Read ✓ |
| `game/ui/screens/battle_setup_state.py` | Read ✓ |
| `game/strategy/data/order_serializer.py` | Read ✓ |
| `game/ai/interfaces/__init__.py` | Read ✓ |
| `game/ui/research/research_controls.py` | Read ✓ |
| `game/ui/renderer/sprites.py` | Read ✓ |
| `game/ui/panels/empire_treasury_panel.py` | Read ✓ |
| `game/core/__init__.py` | Read ✓ |
| `game/ui/screens/star_list_window.py` | Read ✓ |
| `game/strategy/data/pathfinding.py` | Read ✓ |
| `game/strategy/services/action_time_resolver.py` | Read ✓ |
| `game/simulation/combat/fleet_aura_manager.py` | Read ✓ |
| `game/strategy/data/galaxy_entity_registry.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/_condition_logic.py` | Read ✓ |
| `game/ui/widgets/column_toggle_section.py` | Read ✓ |
| `game/ui/filters/__init__.py` | Read ✓ |
| `game/ai/group_target_coordinator.py` | Read ✓ |
| `game/ui/screens/strategy_camera_nav.py` | Read ✓ |
| `game/core/spectrum_math.py` | Read ✓ |
| `game/strategy/services/ability_sources/__init__.py` | Read ✓ |
| `game/ui/screens/battle_screen.py` | Read ✓ |
| `game/ui/panels/builder_widgets.py` | Read ✓ |
| `game/simulation/managers/retreat_manager.py` | Read ✓ |
| `game/ai/spatial_behaviors/battle_line.py` | Read ✓ |
| `game/strategy/services/replay_verification_sidecar.py` | Read ✓ |
| `game/ui/screens/star_list_filters.py` | Read ✓ |
| `game/ui/screens/new_game_setup_ui_builder.py` | Read ✓ |
| `game/ui/screens/strategy_renderer.py` | Read ✓ |
| `game/ui/components/__init__.py` | Read ✓ |
| `game/strategy/facade/dto/fleet_hierarchy_dto.py` | Read ✓ |
| `game/ai/protocols.py` | Read ✓ |
| `game/strategy/engine/order_handlers/transfer.py` | Read ✓ |
| `game/ui/panels/race_description_panel.py` | Read ✓ |
| `game/strategy/validation/colonize_validator.py` | Read ✓ |
| `game/simulation/combat/modifier_stack.py` | Read ✓ |
| `game/ui/screens/builder/weapons_viewmodel.py` | Read ✓ |
| `game/core/protocols/persistence.py` | Read ✓ |
| `game/strategy/services/replay_store.py` | Read ✓ |
| `game/ui/screens/strategy_screen.py` | Read ✓ |
| `game/simulation/components/abilities/base.py` | Read ✓ |
| `game/strategy/data/environmental_preference.py` | Read ✓ |
| `game/ui/screens/race_setup/llm_dialog_service.py` | Read ✓ |
| `game/strategy/engine/turn_engine_config.py` | Read ✓ |
| `game/ui/screens/water_target_editor.py` | Read ✓ |
| `game/ui/components/table/column_manager.py` | Read ✓ |
| `game/simulation/combat/families/seeker.py` | Read ✓ |
| `game/ui/utils/__init__.py` | Read ✓ |
| `game/strategy/formulas/habitability.py` | Read ✓ |
| `game/strategy/services/stabilizer_registry.py` | Read ✓ |
| `game/ui/screens/strategy_build_queue_manager.py` | Read ✓ |
| `game/strategy/engine/consumable_management_engine.py` | Read ✓ |
| `game/core/protocols/__init__.py` | Read ✓ |
| `game/simulation/systems/resource_manager.py` | Read ✓ |
| `game/ui/screens/design_image_helper.py` | Read ✓ |
| `game/simulation/components/abilities/planetary.py` | Read ✓ |
| `game/ui/screens/strategy_render/__init__.py` | Read ✓ |
| `game/ui/screens/cargo_quick_dialog.py` | Read ✓ |
| `game/ui/components/filters/__init__.py` | Read ✓ |
| `game/ui/panels/design_stats_panel.py` | Read ✓ |
| `game/simulation/components/abilities/crew.py` | Read ✓ |
| `game/strategy/adapters/__init__.py` | Read ✓ |
| `game/strategy/data/planet_serde.py` | Read ✓ |
| `game/core/formula_evaluator.py` | Read ✓ |
| `game/ui/screens/workshop_viewmodel.py` | Read ✓ |
| `game/simulation/entities/stat_contributors/registry.py` | Read ✓ |
| `game/strategy/data/resource_generation_config.py` | Read ✓ |
| `game/ui/screens/test_lab/data_extractor.py` | Read ✓ |
| `game/strategy/data/planet_physics.py` | Read ✓ |
| `game/strategy/data/ship_instance_serializer.py` | Read ✓ |
| `game/ui/research/research_scene.py` | Read ✓ |
| `game/ui/screens/strategy_screen_lifecycle.py` | Read ✓ |
| `game/simulation/entities/stat_contributors/weapons.py` | Read ✓ |
| `game/ui/screens/strategy_event_router.py` | Read ✓ |
| `game/ui/screens/empire_build_queue_data_source.py` | Read ✓ |
| `game/ui/panels/__init__.py` | Read ✓ |
| `game/simulation/battle_config.py` | Read ✓ |
| `game/strategy/data/fleet_capability_calculator.py` | Read ✓ |
| `game/ui/assets/__init__.py` | Read ✓ |
| `game/strategy/combat/spec_compiler.py` | Read ✓ |
| `game/ui/screens/star_data_source.py` | Read ✓ |
| `game/ui/services/ship_io.py` | Read ✓ |
| `game/strategy/facade/__init__.py` | Read ✓ |
| `game/strategy/data/spectrum.py` | Read ✓ |
| `game/strategy/data/race_point_budget.py` | Read ✓ |
| `game/ui/screens/food_allocation_editor.py` | Read ✓ |
| `game/ui/screens/build_queue_queue_data_source.py` | Read ✓ |
| `game/ai/spatial_behaviors/base.py` | Read ✓ |
| `game/strategy/engine/handlers/construction_queue.py` | Read ✓ |
| `game/ui/screens/new_game_setup_view_model.py` | Read ✓ |
| `game/strategy/engine/order_handlers/transfer_branches.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/orchestrator.py` | Read ✓ |
| `game/ui/screens/battle_setup/input_handler.py` | Read ✓ |
| `game/simulation/validation/__init__.py` | Read ✓ |
| `game/simulation/entities/ship_stat_querier.py` | Read ✓ |
| `game/ui/screens/race_setup/ui_builder.py` | Read ✓ |
| `game/strategy/combat/post_battle_hook.py` | Read ✓ |
| `game/strategy/config/economy_config.py` | Read ✓ |
| `game/simulation/components/abilities/cargo.py` | Read ✓ |
| `game/ui/screens/race_setup_screen.py` | Read ✓ |
| `game/core/patterns/layer_iterator.py` | Read ✓ |
| `game/ui/panels/battle_panels.py` | Read ✓ |
| `game/ui/screens/test_lab/renderer/test_list_panel.py` | Read ✓ |
| `game/ai/policy_manager.py` | Read ✓ |
| `game/simulation/components/component.py` | Read ✓ |
| `game/core/patterns/__init__.py` | Read ✓ |
| `game/ui/panels/build_queue_portraits.py` | Read ✓ |
| `game/ui/screens/test_lab/theme.py` | Read ✓ |
| `game/ui/screens/strategy_render/warp_lanes.py` | Read ✓ |
| `game/strategy/generation/density/primitives/noise.py` | Read ✓ |
| `game/ui/screens/planet_selection_window.py` | Read ✓ |
| `game/strategy/__init__.py` | Read ✓ |
| `game/strategy/facade/slices/planet_slice.py` | Read ✓ |
| `game/strategy/data/fleet.py` | Read ✓ |
| `game/simulation/components/abilities/weapons.py` | Read ✓ |
| `game/simulation/physics_constants.py` | Read ✓ |
| `game/strategy/engine/game_config.py` | Read ✓ |
| `game/simulation/entities/ship_combat_engine.py` | Read ✓ |
| `game/ui/screens/test_lab/test_run_details.py` | Read ✓ |
| `game/strategy/facade/slices/event_slice.py` | Read ✓ |
| `game/ui/screens/setup_screen.py` | Read ✓ |
| `game/strategy/services/effect_ability_display.py` | Read ✓ |
| `game/simulation/battle_spec.py` | Read ✓ |
| `game/ui/screens/race_browser_dialog.py` | Read ✓ |
| `game/ui/screens/build_queue_panel_factory.py` | Read ✓ |
| `game/ui/panels/ship_detail_panel.py` | Read ✓ |
| `game/strategy/data/design_role.py` | Read ✓ |
| `game/strategy/data/species_population.py` | Read ✓ |
| `game/ai/spatial_behaviors/free_maneuver.py` | Read ✓ |
| `game/ui/screens/planet_list_sidebar.py` | Read ✓ |
| `game/strategy/engine/production_spawner.py` | Read ✓ |
| `game/strategy/data/classification_config.py` | Read ✓ |
| `game/ui/services/validation_service.py` | Read ✓ |
| `game/ui/screens/strategy_render/fleets.py` | Read ✓ |
| `game/core/protocols/registry.py` | Read ✓ |
| `game/ui/screens/battle_setup/constants.py` | Read ✓ |

All 183 files read and verified. No critical or major pattern conformance violations found in Shard 01.
