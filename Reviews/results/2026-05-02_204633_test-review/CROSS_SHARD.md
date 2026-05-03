# Cross-Shard Duplicate Report

## Summary
- Shard reports analyzed: 12
- Cross-shard duplicates found: 3
- Helper duplications found: 4
- Anti-pattern clusters found: 3

## Cross-Shard Duplicates

### DUP-001: Identical superweapon handler 3-test pattern across engine test files
- **SUT**: `game.strategy.engine.superweapon_command_handlers.*CommandHandler.execute`
- **Shard 03**: `tests/unit/strategy/engine/test_superweapon_command_handlers.py` — ~200 LOC covering 6 handler classes, each with 3 identical-pattern tests: (1) validation passes, (2) correct order type added, (3) fleet-not-found
- **Shard 07**: `tests/unit/strategy/engine/test_superweapon_handler_validation.py` — ~300 LOC covering 5+5 handler classes (direct + mission), each with 2 identical-pattern tests: (1) validator called with component_registry, (2) ability-rejection returned
- **Similarity**: Near-identical structural pattern (one test class per superweapon handler class, same mock_session/mock_fleet/mock_planet fixture chain, same `with patch('...SuperweaponValidator')` pattern). SHARD_03 tests execute path; SHARD_07 tests DI validation path. Different assertions but identical structural template and handler class iteration.
- **Recommendation**: Merge the DI validation tests (SHARD_07) into SHARD_03's test classes as additional test methods per handler class, eliminating the duplicated fixture/import/mock boilerplate. Alternatively, create a single parametrized test class that covers all 6 handlers, combining both the execution and DI-validation assertions.
- **Estimated LOC savings**: 200 (consolidated fixtures, imports, and class scaffolding)

### DUP-002: Fleet-not-found test pattern duplicated across command handler test files
- **SUT**: `game.strategy.engine.*CommandHandler.execute` (generic handler `_get_fleet_by_id` path)
- **Shard 03**: `tests/unit/strategy/engine/test_superweapon_command_handlers.py:105-312` — 6 `test_execute_fails_when_fleet_not_found` tests, each: `mock_session._get_fleet_by_id.return_value = None`, create command, execute, `assert not result.is_valid`, `assert "Fleet not found" in result.message`
- **Shard 12**: `tests/unit/strategy/test_command_handlers.py:93-290` — 8+ `test_fleet_not_found` tests across ColonizeCommandHandler, MoveCommandHandler, InterceptCommandHandler, JoinCommandHandler, ClearOrdersCommandHandler, TransferCommandHandler, SplitFleetCommandHandler, DeleteOrderCommandHandler. Identical pattern: `mock_session._get_fleet_by_id.return_value = None`, execute, assert invalid with "Fleet not found"
- **Similarity**: Identical assertion pattern (`mock_session._get_fleet_by_id.return_value = None` → execute → `assert not result.is_valid` → check message for "Fleet not found"). Tests different handler classes but the same `_get_fleet_by_id → None` code path with identical assertions.
- **Recommendation**: Extract a parametrized test: `@pytest.mark.parametrize("handler_cls,cmd_kwargs", [(ColonizeCommandHandler, {"fleet_id": 999}), (MoveCommandHandler, {"fleet_id": 999}), ...])`. This is the SAME recommendation issued independently by both SHARD_03 and SHARD_12 agents — confirming the duplication.
- **Estimated LOC savings**: 180

### DUP-003: Mock ship/fleet factory helpers with overlapping cargo capacity logic
- **SUT**: N/A (test infrastructure)
- **Shard 06**: `tests/unit/strategy/data/test_fleet_cargo_resources.py:14-45` — `_make_ship(cargo_capacity, cargo_contents)` creates MagicMock ship with `get_cargo_capacity`, `get_current_cargo`, `load_cargo`, `unload_cargo` as lambda closures over mutable dict state
- **Shard 08**: `tests/unit/strategy/engine/test_resupply_engine.py:20-101` — `_make_mock_ship()` creates MagicMock ship with closure-based mutable `_fuel_state` dict and `get_cargo_capacity`/`get_current_cargo` lambdas
- **Similarity**: Both define closure-based cargo mock ships using `dict()` mutable state captured in lambdas (`get_cargo_capacity`, `get_current_cargo`, `load_cargo`, `unload_cargo`). test_resupply_engine.py's version additionally models fuel state but the cargo pattern is identical.
- **Recommendation**: Extract a shared `make_cargo_mock_ship(cargo_capacity=None, cargo_contents=None)` to `tests/fixtures/` or a shared `conftest.py`.
- **Estimated LOC savings**: 50

## Cross-Shard Helper Duplication

### HLP-001: make_mock_ship() with design_data and calculated_stats
- **Defined in**:
  - `tests/unit/ui/screens/test_fleet_report_filters.py:12-75` — 63-line helper, 20+ parameters, `design_data` dict with nested `expected_stats`, `get_calculated_stats` return_value, consumable_levels, HP percentage logic
  - `tests/unit/strategy/data/test_fleet_cargo_resources.py:14-45` — 31-line helper, cargo-focused with closure lambdas
  - `tests/unit/strategy/engine/test_resupply_engine.py:20-101` — `_make_mock_ship`, `_make_mock_fleet`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_empire` — 6 helper functions creating multi-level mock trees
  - `tests/unit/strategy/facade/test_strategy_session_facade.py:19-39, 168-181, 252-261, 333-363, 484-520` — 4 test classes each redefine `_make_mock_fleet`, `_make_mock_empire`, `_make_mock_planet` (12+ helper methods, 80 LOC)
- **Recommendation**: Create shared fixtures in `tests/fixtures/test_entities.py` or a shared `conftest.py` with `make_mock_ship(**overrides)`, `make_mock_fleet(**overrides)`, `make_mock_empire(**overrides)`. Use `@pytest.fixture` with `scope="function"` and keyword-arg overrides for test-specific configuration.

### HLP-002: BattleRunner test helpers (make_ship_spec, make_team, minimal_spec)
- **Defined in**:
  - `tests/unit/simulation/test_battle_runner.py:46-105` — `_make_ship_spec()`, `_make_team()`, `_minimal_spec`, `ship_builder` fixture
  - `tests/unit/simulation/test_battle_runner_di.py:52-100` — near-exact copies of the same helpers
- **Recommendation**: Extract to `tests/unit/simulation/conftest.py` with `scope="class"`. The DI file should import the helpers from the shared location.

### HLP-003: Yard facility factory helpers
- **Defined in**:
  - `tests/unit/strategy/engine/test_planetary_yard_requirement.py:15-25` — `_make_yard_facility()`
  - `tests/unit/strategy/production_engine/test_tick_consumption.py:25` — `_make_planetary_yard_facility()`
  - `tests/unit/strategy/fleet/test_space_yard.py:91-123, 195-226` — `make_ship_with_yard` defined twice within the same file
- **Recommendation**: Move to a shared fixture in `tests/fixtures/` or a common conftest under `tests/unit/strategy/`.

### HLP-004: make_planet helper triplicated in colonize validator tests
- **Defined in**:
  - `tests/unit/strategy/validation/test_colonize_validator.py:753-774` — `TestColonizeValidatorAnyPlanetPods._make_planet`
  - `tests/unit/strategy/validation/test_colonize_validator.py:890-913` — `TestColonizeValidatorAdvancedEdgeCases._make_planet`
  - `tests/unit/strategy/validation/test_colonize_validator.py:620-635` — inline planet construction in `TestColonizeValidatorZoneColonization`
- **Note**: All three in same file (Shard 05), but the pattern of duplicated planet factory helpers also appears in Shard 08 (`test_resupply_engine.py:_make_planet_with_fuel`) and Shard 11 (`test_planet_specific_colonization.py:196-244` — 4 galaxy fixtures with identical structure). This represents a broader cross-shard pattern.
- **Recommendation**: Create a shared `make_mock_planet(**overrides)` factory in `tests/fixtures/`.

## Anti-Pattern Clusters (tests with same structural issues across shards)

### APC-001: `__new__` bypass-init pattern — 16 files across 10 shards
- **Pattern**: `patch.object(ClassName, '__init__', lambda self, *a, **kw: None)` + `ClassName.__new__(ClassName)` + manual attribute wiring of ALL internal state
- **Shards affected**: 01, 03, 04, 06, 07, 08, 09, 11, 12
- **Files**:
  - `tests/unit/ui/test_race_portrait_gallery.py` (Shard 01, 240 LOC affected)
  - `tests/unit/ui/test_race_description_panel.py` (Shard 01, 230 LOC affected)
  - `tests/unit/ui/panels/test_race_identity_panel.py` (Shard 03, 200 LOC affected)
  - `tests/unit/ui/panels/test_component_modifier_grid_panel.py` (Shard 03, 200 LOC affected)
  - `tests/unit/ui/test_race_flag_gallery.py` (Shard 03, 200 LOC affected)
  - `tests/unit/ui/screens/test_fleet_report_window.py` (Shard 03, 98 LOC helper)
  - `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` (Shard 03, 150 LOC)
  - `tests/unit/ui/panels/test_system_tree_panel.py` (Shard 04, 400 LOC affected)
  - `tests/unit/ui/panels/test_design_report_panel.py` (Shard 06, 336 LOC affected)
  - `tests/unit/ui/screens/test_workshop_screen.py` (Shard 06, 450 LOC affected)
  - `tests/unit/ui/screens/test_race_setup_screen.py` (Shard 07, 118 LOC helper)
  - `tests/unit/ui/screens/test_new_game_setup_extended.py` (Shard 08, 16-49 LOC)
  - `tests/unit/ui/test_race_theme_gallery.py` (Shard 09, 200 LOC affected)
  - `tests/unit/ui/test_race_summary_panel.py` (Shard 11, 47 LOC helper)
  - `tests/unit/ui/screens/test_build_queue_screen.py` (Shard 12, 580 LOC affected)
  - `tests/unit/ui/screens/test_sub_window_hotkeys.py` (Shard 12, 350 LOC affected)
- **Estimated total LOC affected**: ~4,000
- **Impact**: Zero regression protection for any UI class constructor or pygame_gui element lifecycle. Every test manually assigns attributes and asserts they were assigned — tests verify Python attribute assignment, not production behavior. Any bug in `__init__`, `_create_content`, or pygame_gui widget construction passes these tests unnoticed.
- **Recommendation**: Create a shared `make_ui_widget(Cls, **kwargs)` test helper in `tests/fixtures/` that constructs real widgets with a pre-configured mock `pygame_gui.UIManager`. Apply consistently across all UI test files. Alternatively, if full pygame_gui mocking is too heavy, consolidate bypass-init files into integration tests that exercise the real widget with a headless pygame_gui setup (as `test_build_queue_screen.py` integration tests already do in `tests/integration/ui/build_queue_screen/`).

### APC-002: `inspect.getsource()` / `inspect.signature()` source inspection — 11 files across 6 shards
- **Pattern**: Using `inspect.getsource()`, `inspect.signature()`, or `ast.parse()` to inspect source code as assertions, rather than testing runtime behavior
- **Shards affected**: 01, 04, 05, 06, 07, 12
- **Files**:
  - `tests/unit/modifiers/test_seeker_multi_ability.py:66-82` (Shard 01) — `inspect.getsource(SeekerWeaponAbility.recalculate)`, asserts string patterns absent
  - `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py:175-186` (Shard 01) — `inspect.signature()` to verify parameter default
  - `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py:13-53` (Shard 04) — signature + getsource, 3 tests
  - `tests/integration/test_app_integration.py:160-239` (Shard 04) — getsource + signature, 3 tests
  - `tests/unit/ui/screens/battle_setup/test_view_model.py:24-39` (Shard 04) — getsource + AST parse
  - `tests/unit/ui/screens/test_strategy_renderer_public_api.py:16-92` (Shard 05) — entire file, 7 tests using `inspect.signature()` and `isinstance(getattr(...), property)`
  - `tests/unit/research/test_research_scene_di.py:88-97` (Shard 06) — `open(module.__file__).read()` to find import string
  - `tests/unit/ui/screens/battle_setup/test_renderer.py:54-64` (Shard 07) — `inspect.getsource(FleetBattleSetupScreen._rebuild_ui)`
  - `tests/unit/ui/screens/test_planet_selection_window.py:28-62` (Shard 07) — `inspect.signature()` only, 2 tests
  - `tests/unit/ui/test_new_game_setup.py:103-117` (Shard 09) — `inspect.signature()` + `inspect.getsource()` to verify parameter default
  - `tests/unit/ui/screens/test_strategy_window_manager_public_api.py:417-423` (Shard 12) — `inspect.getsource(registrar_cls.open)`, asserts string present
- **Estimated total LOC affected**: ~400
- **Recommendation**: Replace source-inspection tests with behavioral tests. For contract/API stability, use `@pytest.mark.parametrize` behavioral tests that call the actual methods. For invariant enforcement (e.g., "no pygame imports in view model"), use a pre-commit lint rule or CI step rather than a runtime test. For the intentional contract-pin file (`test_strategy_renderer_public_api.py`, PROJ-309), keep as-is but add a file-level docstring explaining why source inspection is used.

### APC-003: Patching private `_methods` instead of testing through public API — 8 files across 5 shards
- **Pattern**: Tests call or patch `SUT._private_method()`, `SUT._private_attribute`, or `patch.object(SUT, '_private_internal')` rather than exercising the SUT through its public interface
- **Shards affected**: 02, 05, 06, 08, 11
- **Files**:
  - `tests/unit/ui/screens/builder/test_modifier_logic_service.py:47-84` (Shard 02) — 5 tests directly call `service._get_base_firing_arc(comp)` (private method)
  - `tests/unit/simulation/systems/test_battle_engine_init_ship.py:65-93` (Shard 02) — 4 tests call `battle_engine._initialize_ship(ship)` (private helper)
  - `tests/unit/ui/screens/test_build_queue_list_window.py:28` (Shard 05) — `patch.object(BuildQueueListWindow, '_build_list')` on all 11 tests
  - `tests/unit/strategy/turn_engine/test_tick_mechanics.py:149, 177` (Shard 05) — `patch.object(turn_engine.movement_engine, 'calculate_next_hex')`
  - `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py:69-107` (Shard 06) — access `engine._fleets_destroyed`, `engine._empires`, `engine._combats_resolved`
  - `tests/unit/strategy/engine/test_build_order_command_handler.py:183-203` (Shard 06) — access `registry._handlers` dict
  - `tests/unit/strategy/fleet_movement_engine/test_basics.py:77-108` (Shard 08) — `patch('fleet_navigation_service.find_hybrid_path')`
  - `tests/unit/builder/test_builder_drag_drop_real.py:29` (Shard 11) — `patch.object(Builder, '_create_ui')` (private method)
- **Estimated total LOC affected**: ~400
- **Recommendation**: Refactor tests to exercise the SUT through its public API. If a private method has independently critical logic, promote it to a public standalone function (or `_protected` method of a public helper class) so it can be unit-tested legitimately. When patching is necessary for isolation, patch at the service boundary (the dependency injected into the SUT) rather than at the internal call chain level.

## Recommendations Summary

| Priority | Action | LOC Savings | Shards Affected |
|----------|--------|-------------|-----------------|
| 1 | Consolidate `__new__` bypass-init UI tests with shared `make_ui_widget()` factory | ~4,000 affected (quality, not deletion) | 01, 03, 04, 06, 07, 08, 09, 11, 12 |
| 2 | Create shared mock ship/fleet/planet/empire fixtures in `tests/fixtures/` | ~300 deduplication | 06, 08, 09, 10, 11 |
| 3 | Replace `inspect.getsource()`/`inspect.signature()` with behavioral tests | ~400 | 01, 04, 05, 06, 07, 12 |
| 4 | Parametrize fleet-not-found tests across command handler files | ~180 | 03, 12 |
| 5 | Merge superweapon handler DI tests into execution test file | ~200 | 03, 07 |
| 6 | Refactor private-method-patching tests to public API | ~400 (quality) | 02, 05, 06, 08, 11 |
