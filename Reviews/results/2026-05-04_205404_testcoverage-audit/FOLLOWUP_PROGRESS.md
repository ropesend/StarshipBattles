# Coverage Follow-up Progress

Source audit: `Reviews/results/2026-05-04_205404_testcoverage-audit/SUMMARY.md` and `SUMMARY.json`.

## Coordination

Five Codex worker agents were started with disjoint ownership:

| Worker | Slice | Primary test paths |
|---|---|---|
| A | Core/simulation protocols and replay DTOs | `tests/unit/core/test_protocols_boundary.py`, `tests/unit/simulation/interfaces/test_ability_protocols.py`, `tests/unit/simulation/replay/` |
| B | Strategy facade slices and DTOs | `tests/unit/strategy/facade/slices/`, `tests/unit/strategy/facade/dto/test_build_queue_dto.py` |
| C | Strategy services/data helpers | `tests/unit/strategy/services/`, `tests/unit/strategy/validation/`, `tests/unit/strategy/data/` |
| D | Simulation components/resources helpers | `tests/unit/simulation/` component, ability, resource-manager tests |
| E | UI pure-Python helpers and one AI helper | `tests/unit/ui/`, `tests/unit/ai/` |

## Completed Locally

| Claim | Result | Notes |
|---|---|---|
| `game/context.py` LLM/Image provider fallback paths lack targeted tests | Covered | Added `ApplicationContext.create_production()` tests for `LLMConfigError` -> `None`, `ImageConfigError` -> `NullImageProvider`, and `create_test()` image fallback. |
| `game/app.py` `_request_shutdown`, `_return_to`, `start_replay` lack unit tests | Covered | Added bootstrap-free `Game.__new__` tests for shutdown, return destinations, and replay config construction. |
| `game/run_loop.py` lacks automated coverage | Partially covered | Added event-routing tests for shutdown, exit dialog Esc/yes/cancel, global exit/profiler hotkeys, menu overlay forwarding, resize plumbing, strategy update/draw, and battle headless draw skip. Full `run()` loop startup/shutdown remains a follow-up. |
| `game/core/roles.py` `_fire_invalidation_callbacks` re-entrance guard untested | Disputed | Existing `tests/unit/core/test_role_registry.py::TestRoleRegistryInvalidation::test_reentrant_add_user_role_in_callback_does_not_recurse` directly covers the guard and nested mutation behavior. |

## Worker Results

| Worker | Result | Notes |
|---|---|---|
| A | Completed | `ability_protocols.py` gap confirmed and covered. `boundary.py` was partial; added missing `IResourceHolder` and `get_resource_names()` coverage. `replay_record.py` and `replay_outcome.py` claims disputed because `tests/unit/simulation/replay/test_serialization.py` already covers round trips. |
| B | Completed | Facade slice/DTO direct coverage gaps confirmed. Added focused tests for `FacadeSessionState`, `PlanetSlice`, `EmpireSlice`, `SystemSlice`, and `BuildQueueSourceDTO`. New DTO test exposed a real nested-shallow-copy bug and fixed it with `deepcopy()`. |
| C | Completed | Added strategy-helper coverage for `StarAbilitySource`, `_facility_has_ability`, `race_resolver.py`, `planet_physics.py`, and `FleetCapabilityCalculator.list_abilities()`. No production changes needed. |
| D | Completed | Added simulation-helper coverage for `BattleConfig`, `get_ability_default_scope`, weapon helper fallbacks, resource ability edges, resource manager edge helpers, and component health facade paths. No production changes needed. |
| E | Completed | Added pure helper coverage for `ListDataSource`, `GameSettings`, builder grouping strategies, stat definitions, and `get_capability_cache_key`. No production changes needed. |

## Test Receipts

| Command | Result |
|---|---|
| `pytest tests/unit/core/test_application_context.py -q` | Passed: 21 tests |
| `pytest tests/unit/test_app_delegators.py -q` | Passed: 6 tests |
| `pytest tests/unit/test_run_loop.py -q` | Passed: 10 tests |
| Worker A targeted protocol/replay suite | Passed: 61 tests |
| Worker B targeted facade slice suite | Passed: 22 tests; broader facade suite passed: 268 tests |
| Worker C targeted strategy-helper suite | Passed: 48 tests |
| Worker D targeted simulation-helper suite | Passed: 257 tests |
| Worker E targeted UI/AI helper suite | Passed: 58 tests |
| Combined targeted suite across all touched files | Passed: 707 tests |

Combined command:

```powershell
pytest tests/unit/core/test_application_context.py tests/unit/core/test_protocols_boundary.py tests/unit/simulation/test_battle_config.py tests/unit/simulation/interfaces/test_ability_protocols.py tests/unit/simulation/components/abilities/test_ability_registry.py tests/unit/simulation/components/abilities/test_resource_consumption.py tests/unit/simulation/components/abilities/test_weapons_isolation.py tests/unit/simulation/components/test_component_health_manager.py tests/unit/simulation/systems/test_resource_manager_edge_cases.py tests/unit/strategy/facade tests/unit/strategy/services/ability_sources/test_star.py tests/unit/strategy/validation/test_planet_order_validator.py tests/unit/strategy/services/test_race_resolver.py tests/unit/strategy/data/test_planet_physics.py tests/unit/strategy/data/test_fleet_capability_calculator.py tests/unit/test_app_delegators.py tests/unit/test_run_loop.py tests/unit/ui/screens/test_list_data_source_base.py tests/unit/ui/services/test_game_settings.py tests/unit/ui/screens/builder/test_grouping_strategies.py tests/unit/ui/screens/builder/test_stat_definitions.py tests/unit/ai/test_combat_utils.py -q -n 0
```

## Production Fixes

| File | Fix |
|---|---|
| `game/strategy/facade/dto/build_queue_dto.py` | `BuildQueueSourceDTO.from_domain()` now deep-copies queue item dictionaries so nested data cannot be mutated through the UI DTO. |

## Pass 2 Results

Second pass started 2026-05-05 with five more worker slices plus two local low-overlap gaps.

| Slice | Result | Notes |
|---|---|---|
| Local | Completed | Added full `RunLoop.run()` one-frame smoke coverage and `normalize_angle()` edge-case coverage. |
| F / command handlers | Completed | Added movement and order-queue handler tests. Found and fixed a `MoveCommandHandler` no-op defect: moving to the current hex now returns success without queueing a `MOVE` order. |
| G / simulation entity helpers | Completed | Added direct coverage for `ShipValidatorHelper`, `ShipResourceManager`, ship stats routing, ship construction branches, and serialization warnings. Found and fixed `_verify_stats` skipping expected zero values. |
| H / app router/dialog | Completed | Added `ScreenRouter` and `exit_dialog` tests for scene callbacks, transitions, dialog rects/clicks/cancel behavior, and load/setup flags. No production changes needed. |
| I / UI builder helpers | Completed | Added `stat_rows_dynamic`, `components`, `stat_getters`, and `workshop_viewmodel_layer_ops` coverage. Found and fixed `ResourceGeneration` tooltip handling, generic ability fallback, resource getter guards, missing-data guards, and a planetary engineering row break bug. |
| J / strategy engine/services | Completed | Added tests for `planet_energy_engine`, `water_engine`, `turn_state_snapshot`, `ability_iterator`, `system_effects_collector`, and `spec_compiler` branches. No production changes needed. |

Pass 2 combined targeted command:

```powershell
pytest tests/unit/core/test_math_vector2.py tests/unit/test_run_loop.py tests/unit/test_screen_router.py tests/unit/test_exit_dialog.py tests/unit/strategy/engine/handlers/test_movement_handlers.py tests/unit/strategy/engine/handlers/test_order_queue_handlers.py tests/unit/simulation/entities/test_ship.py tests/unit/simulation/entities/test_ship_resource_manager.py tests/unit/simulation/entities/test_ship_serialization.py tests/unit/simulation/entities/test_ship_shield_bonus_add.py tests/unit/simulation/entities/test_ship_stats.py tests/unit/simulation/entities/test_ship_validator_helper.py tests/unit/ui/screens/builder/test_stat_rows_dynamic.py tests/unit/ui/screens/builder/test_components.py tests/unit/ui/screens/builder/test_stat_getters.py tests/unit/ui/screens/test_workshop_viewmodel_layer_ops.py tests/unit/strategy/engine/test_planet_energy_engine.py tests/unit/strategy/engine/test_water_engine.py tests/unit/strategy/turn_engine/test_turn_state_snapshot.py tests/unit/strategy/services/test_ability_iterator.py tests/unit/strategy/services/test_system_effects_collector_aggregate_characterization.py tests/unit/strategy/combat/test_spec_compiler.py -q -n 0
```

Pass 2 result: `295 passed`.

## Pass 2 Production Fixes

| File | Fix |
|---|---|
| `game/strategy/engine/handlers/movement.py` | `MoveCommandHandler` now treats current-hex moves as a true no-op instead of queueing a redundant `MOVE` order. |
| `game/simulation/entities/ship_serialization.py` | Expected stat verification now checks present zero-valued expected stats instead of skipping all falsey expected values. |
| `game/ui/screens/builder/components.py` | Component tooltips now recognize `ResourceGeneration` and list generic abilities through `has_ability()` instead of only raw instance keys. |
| `game/ui/screens/builder/stat_getters.py` | Resource getter helpers now tolerate missing `resources`, missing `get_resource_stat`, and non-numeric stat values. |
| `game/ui/screens/builder/stat_rows_dynamic.py` | Dynamic rows now tolerate missing resource/layer APIs and no longer stops planetary engineering row discovery after the first component without a matching ability. |

## Deferred High-Risk/High-Effort Claims

These remain good follow-up candidates if they are not completed by workers:

- `game/ui/screens/transfer_grid_renderer.py`, `orders_window_ctrl.py`, and other pygame_gui registrar/window claims: useful but more brittle than pure helpers.
- `game/ui/screens/test_lab/test_run_card.py` and `screen_input_handler.py`: rect/event dispatch logic remains a good low-to-medium coupling target.
- `game/ui/screens/battle_setup/controller.py`, `event_log_window.py`, `save_selection_window.py`, `species_selector_mixin.py`, and race setup controller/panel factory still have verified UI-layer gaps from the audit.
- P2 simulation projectile/projectile-manager edge cases and strategy randomizer/storm-generator/filter helper gaps remain opportunistic follow-ups.
