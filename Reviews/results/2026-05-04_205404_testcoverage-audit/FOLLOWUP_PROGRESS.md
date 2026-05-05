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

## Deferred High-Risk/High-Effort Claims

These remain good follow-up candidates if they are not completed by workers:

- `game/run_loop.py`: add an end-to-end `run()` loop smoke with mocked `pygame.event.get`, `pygame.display.flip`, `shutdown_all_calls`, and `pygame.quit`.
- `game/screen_router.py`: critical but likely requires careful pygame/router fakes.
- `game/exit_dialog.py`: module-level pygame globals; should be isolated with surface/rect mocks.
- `game/ui/screens/builder/stat_rows_dynamic.py`: large pure-data surface; likely needs a dedicated batch of focused tests.
- `game/ui/screens/transfer_grid_renderer.py`, `orders_window_ctrl.py`, and other pygame_gui registrar/window claims: useful but more brittle than pure helpers.
