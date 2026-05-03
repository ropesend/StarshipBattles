# Shard 02 — Verified Findings

## Summary
- Shard: 02
- Claims reviewed: 24 (Phase 1: 22, Cross-shard: 2)
- CONFIRMED: 24 | DISPUTED: 0 | INCONCLUSIVE: 0
- Severity downgrades: 0

## Verified Findings (CONFIRMED only)

### tests/unit/services/llm/test_package_imports.py

#### CAT-1: test_services_package_importable  [CRITICAL]
- **Location**: test_package_imports.py:4-5
- **Issue**: Test body is `import game.services  # noqa: F401` — zero explicit assertions. The only failure mode is import error, which is already exercised by every other test that imports from `game.services`. No unique regression signal.
- **Suggestion**: Remove — package importability is already validated by `test_llm_package_exports_phase_2_symbols` and all other tests that import from `game.services`.
- **LOC affected**: 3
- **Verified**: CONFIRMED (severity kept)

#### CAT-1: test_llm_package_importable  [CRITICAL]
- **Location**: test_package_imports.py:8-9
- **Issue**: Test body is `import game.services.llm  # noqa: F401` — zero explicit assertions. Redundant with explicit symbol-export tests (`test_llm_package_exports_phase_2_symbols`, etc.) in the same file.
- **Suggestion**: Remove.
- **LOC affected**: 2
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/test_modifier_logic.py

#### CAT-2: Entire file — Tests Nothing Real  [CRITICAL]
- **Location**: test_modifier_logic.py:1-103
- **Issue**: Verified by full file read. Every test method reimplements `calculate_snap_decrement`, `calculate_snap_increment`, and `calculate_size_decrement` locally in the class (lines 5-34) and exercises ONLY those local reimplementations. Zero imports from `game.*`. The production `ModifierLogicService.calculate_snap_value` is covered by `tests/unit/ui/screens/builder/test_modifier_logic_service.py:198-218`.
- **Suggestion**: Remove entire file.
- **LOC affected**: 103
- **Verified**: CONFIRMED (severity kept)

---

### tests/regression/test_deprecated_code_removed.py

#### CAT-3: test_fleet_movement_simulator_import_fails  [CRITICAL]
- **Location**: test_deprecated_code_removed.py:13-16
- **Issue**: Uses `pytest.raises(ImportError): from game.strategy.engine.fleet_movement import FleetMovementSimulator` to verify a class that was already deleted stays deleted. This is a dead-code-guard pattern — the test asserts on a negative (that an import fails) rather than on behavior. The `hasattr` guards in the same file (lines 22-77) serve the same regression purpose with cleaner patterns.
- **Suggestion**: Remove this test. The removed module has been gone long enough that regression risk is negligible.
- **LOC affected**: 4
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/simulation/components/test_modifier_manager.py

#### CAT-4: Standalone static method tests duplicate instance method coverage  [MAJOR]
- **Location**: test_modifier_manager.py:140-177
- **Issue**: `TestModifierManagerStandalone` tests `add_modifier_static` (line 143), `remove_modifier_static` (line 158), and `get_modifier_static` (line 168) — deprecated static methods that are thin wrappers. The same add/remove/query operations are tested on instance methods in preceding classes (`TestModifierManagerAddRemove`, `TestModifierManagerQuery`, etc.).
- **Suggestion**: Remove `TestModifierManagerStandalone` class.
- **LOC affected**: 38
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/ui/test_camera.py

#### CAT-5: pygame.init() autouse fixtures repeated across 8 classes  [MAJOR]
- **Location**: test_camera.py:22-26, 48-51, 115-118, 164-167, 237-240, 259-262, 305-308, 355-361
- **Issue**: **Correction to Phase 1 count**: 8 (not 7) test classes repeat `@pytest.fixture(autouse=True)` with `pygame.init()` and `os.environ['SDL_VIDEODRIVER'] = 'dummy'`. The 8th class is `TestCameraUpdateInput` at line 355. `pygame.init()` is a heavyweight call that only needs to happen once per session. The SDL_VIDEODRIVER env var is already set by the repo's top-level `conftest.py`.
- **Suggestion**: Move pygame init to a single `module`-scoped fixture.
- **LOC affected**: ~55 (8 fixture definitions)
- **Verified**: CONFIRMED (severity kept; Phase 1 count understated by 1 class)

---

### tests/unit/ui/services/test_ship_io.py

#### CAT-5: Ship-creation fixtures are function-scoped but used across multiple test classes  [MAJOR]
- **Location**: test_ship_io.py:27-55
- **Issue**: `mock_ship` (line 27), `mock_ship_with_special_chars` (line 39), and `minimal_ship` (line 49) call `create_test_ship()` with `registries=fresh_registries` — creating real Ship objects with full component instantiation. These are function-scoped (default). Used across 14 test classes (Phase 1 reported 13; verified 14 via grep: `TestShipIOSaveOperations`, `TestShipIOLoadOperations`, `TestShipIORoundTrip`, `TestShipIODataFormat`, `TestShipIOEdgeCases`, `TestShipIOErrorLogging`, `TestShipIOStatMismatchWarnings`, `TestShipIOComponentIntegration`, `TestShipIOFormatVersioning`, `TestShipIOResourceSerialization`, `TestShipIOSpecialCharacters`, `TestShipIOLargeShips`, `TestShipIOConcurrency`, `TestShipIODefaultValues`). Each test that uses them re-creates the same Ship.
- **Suggestion**: Rescope to `class` or `module` level.
- **LOC affected**: 30
- **Verified**: CONFIRMED (severity kept; Phase 1 class count understated by 1)

---

### tests/unit/ui/screens/builder/test_modifier_logic_service.py

#### CAT-6: Tests call private _get_base_firing_arc method  [MAJOR]
- **Location**: test_modifier_logic_service.py:47, 57, 67, 73, 84
- **Issue**: All 5 tests in `TestGetBaseFiringArc` directly call `service._get_base_firing_arc(comp)`. Verified the method is indeed private: `game/ui/screens/builder/modifier_logic.py:131` — `def _get_base_firing_arc(self, component) -> Optional[float]:`. Tests are tightly coupled to internal implementation. Also cited in cross-shard APC-003.
- **Suggestion**: Test through public API (`get_initial_value('turret_mount', comp)`, `get_local_min_max`), or promote `_get_base_firing_arc` to a public static helper if it requires independent testing.
- **LOC affected**: 42
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/simulation/systems/test_battle_engine_init_ship.py

#### CAT-6: Tests call private _initialize_ship method  [MAJOR]
- **Location**: test_battle_engine_init_ship.py:65, 73, 82, 90
- **Issue**: All 4 tests call `battle_engine._initialize_ship(ship)` directly. Verified the method is private: `game/simulation/systems/battle_engine.py:425` — `def _initialize_ship(self, ship: 'Ship') -> None:`. Tests assert internal effects (event bus wiring, component update calls, stat recalculation) rather than observable outcomes. Also cited in cross-shard APC-003.
- **Suggestion**: Test through `engine.start(...)` or `engine.start_teams(...)` public APIs, verifying observable outcomes (ship is in `engine.ships`, has correct team_id).
- **LOC affected**: 31
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/ui/screens/test_strategy_screen.py

#### CAT-6: Mocks internal sub-object delegates  [MAJOR]
- **Location**: test_strategy_screen.py:66-74 (setup), used across ~50 tests
- **Issue**: The `_make_strategy_screen()` helper (lines 14-79) uses the `__new__` bypass-init pattern to inject MagicMock replacements for 8 internal sub-objects (`_renderer`, `_camera_nav`, `_fleet_ops`, `_colonization`, `_superweapons`, `_build_queue`, `_game_state`, `_input`). Tests then assert these mocks were called with specific arguments, encoding the exact delegation chain. Matches cross-shard APC-001 (`__new__` pattern) and APC-003 (patching private implementation details).
- **Suggestion**: Reduce to testing the public API surface (update, draw, handle_event, handle_resize, handle_click) with observable outcomes.
- **LOC affected**: ~400
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/ai/test_ai_controller_unit.py

#### CAT-8: Nesting + nonlocal capture for single assertion  [MAJOR]
- **Location**: test_ai_controller_unit.py:284-362
- **Issue**: `test_behavior_context_includes_movement_policy` (line 284) and `test_behavior_context_uses_movement_policy_values` (line 327) use 5+ levels of `with patch()` nesting (lines 289, 293, 318-319 for the first; lines 331, 338, 356-357 for the second), plus `nonlocal` variable capture (lines 314, 348) and `patch.object` side-effect to intercept behavior calls — all to assert single key-value pairs (`approach_distance` == 0.5 at line 324, `engage_distance` == 0.9 at line 361). Setup is ~50%+ of test body.
- **Suggestion**: Simplify by calling `controller._build_behavior_context(policy={...})` if promoted, or restructure controller for separable context construction.
- **LOC affected**: 78
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/strategy/test_fleet_speed_calculator.py

#### CAT-9: Repeated mock construction across 7 ship-speed tests  [MINOR]
- **Location**: test_fleet_speed_calculator.py:13-131
- **Issue**: Every test in `TestFleetSpeedCalculatorShipSpeed` duplicates the pattern: `ship_instance = MagicMock()`, set `design_data`, set `get_calculated_stats.return_value`, call `calculate_ship_speed`, assert. A helper factory would eliminate ~50 lines.
- **Suggestion**: Extract a `_make_mock_ship_with_stats(mass, speed)` helper.
- **LOC affected**: 50
- **Verified**: CONFIRMED (severity kept)

#### CAT-10: 7 calculate_ship_speed tests are parametrizable  [MINOR]
- **Location**: test_fleet_speed_calculator.py:13-116
- **Issue**: Tests `test_calculate_ship_speed_formula` (line 13), `test_calculate_ship_speed_higher_movement` (line 32), `test_calculate_ship_speed_clamped_to_max` (line 50), `test_calculate_ship_speed_zero_for_fighters` (line 67), `test_calculate_ship_speed_zero_for_complexes` (line 84), `test_calculate_ship_speed_zero_for_no_movement` (line 101), `test_calculate_ship_speed_handles_missing_stats` (line 117) all follow the identical pattern: define (vehicle_type, mass, strategic_movement, expected_speed), mock, call, assert.
- **Suggestion**: Parametrize to one `@pytest.mark.parametrize` test.
- **LOC affected**: 103
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/strategy/services/test_modifier_resolver.py

#### CAT-10: 7 tests have identical structure, differ only in input data  [MINOR]
- **Location**: test_modifier_resolver.py:15-69
- **Issue**: `test_component_with_size_mount_0_2` (line 15), `test_component_with_size_mount_1_0` (line 24), `test_component_without_modifiers` (line 33), `test_component_with_empty_modifiers` (line 39), `test_component_with_other_modifiers_only` (line 45), `test_string_component_entry` (line 54), `test_component_with_multiple_modifiers` (line 59) all create a comp_entry dict, call `resolve_size_multiplier`, and assert a specific float. Only the dict and expected value differ.
- **Suggestion**: Parametrize: `@pytest.mark.parametrize("entry,expected", [...])`.
- **LOC affected**: 55
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/ui/screens/test_planet_data_source.py

#### CAT-10: Attr-value extraction tests are parametrizable  [MINOR]
- **Location**: test_planet_data_source.py:150-208
- **Issue**: `test_attr_simple_attribute` (line 150), `test_attr_dotted_path` (line 165), `test_attr_missing_returns_question_mark` (line 181), `test_attr_dotted_path_missing_intermediate` (line 195) all follow identical structure: create planet mock, create column, call `get_cell_value`, assert result.
- **Suggestion**: Parametrize to a single test.
- **LOC affected**: 59
- **Verified**: CONFIRMED (severity kept)

---

### tests/regression/test_deprecated_code_removed.py

#### CAT-11: Hardcoded EXPECTED_GAME_COUNT magic number  [MINOR]
- **Location**: test_deprecated_code_removed.py:152-153
- **Issue**: `EXPECTED_GAME_COUNT = 0` and `EXPECTED_TESTS_COUNT = 13` are hardcoded file-search counts. Tests `test_singleton_usage_count_game` (line 155) and `test_singleton_usage_count_tests` (line 178) walk the entire filesystem with `os.walk` to count string occurrences of `RegistryManager.instance()`. Any legitimate addition requires updating the constant. This is a fragile snapshot rather than a behavioral test.
- **Suggestion**: Remove the count-based tests (lines 155-199) or make them advisory-only (non-blocking warnings). The `hasattr` checks in the rest of the file (lines 19-136) already guard against reintroduced code.
- **LOC affected**: 48
- **Verified**: CONFIRMED (severity kept)

---

### tests/integration/ui/test_race_setup_ships_smoke.py

#### CAT-12: Logic-heavy test with if/else branches  [MINOR]
- **Location**: test_race_setup_ships_smoke.py:124-154
- **Issue**: `test_every_portrait_is_2048x2048_or_in_allowlist` (line 124) has if/elif/else branches in the test body: `if pair in EXPECTED_PORTRAIT_GAPS: continue` (line 131), `if pair in EXPECTED_PORTRAIT_SIZE_MISMATCHES: assert !=` (line 141) else `assert ==` (line 147). Conditional branching and different comparison operators (== vs !=) in a single test body.
- **Suggestion**: Split into two tests: one for allowlisted gaps and one for target-sized portraits.
- **LOC affected**: 31
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/ai/test_ai_controller_unit.py

#### CAT-8: Complex mock chain for avoidance tests  [MINOR]
- **Location**: test_ai_controller_unit.py:448-621
- **Issue**: The `TestCheckAvoidance` class (line 448) repeats identical mock setup across 8 tests: mock_ship positioning (`get_position.return_value`, `get_radius.return_value`), mock_grid query returns (`query_radius.return_value`, `query_radius_exact.return_value`), and `patch('game.ai.controller.is_combatant', ...)`. Each test has ~10 lines of repeated setup.
- **Suggestion**: Extract mock setup: `_setup_avoidance_test(threats, ship_pos=(100,100), ship_radius=10.0)`.
- **LOC affected**: 80
- **Verified**: CONFIRMED (severity kept)

---

### tests/integration/fleet_combat/test_combat_resource_consumption.py

#### CAT-12: Logic-heavy tests with loops and conditionals  [MINOR]
- **Location**: test_combat_resource_consumption.py:276-313
- **Issue**: `test_fuel_depletes_during_continuous_movement` (line 269) contains a for-loop (100 iterations) with conditional break at line 283-287 and calculation before the assertion at line 291. `test_ammo_depletes_during_weapon_firing` (line 294) contains a for-loop (10 iterations) with conditional if at line 308-310. The test body encodes production-like simulation logic.
- **Suggestion**: Extract the resource consumption loop into a test helper. Test at the ResourceState level directly (already covered by `TestResourceStateBasics`) and keep one integration scenario.
- **LOC affected**: 38
- **Verified**: CONFIRMED (severity kept)

---

### tests/unit/builder/test_multi_selection_logic.py

#### CAT-6: Autouse fixture uses self for state sharing  [MINOR]
- **Location**: test_multi_selection_logic.py:10-50
- **Issue**: The `setup` fixture (line 10, `@pytest.fixture(autouse=True)`) sets attributes on `self` (`self.builder`, `self.comp_a1`, `self.comp_a2`, etc.) instead of returning test objects or using fixture injection. This couples all tests to the class instance and makes test isolation fragile if tests run in parallel. **Note**: The CAT-6 classification is borderline — this is a fixture design pattern issue (coupling via `self`), not a "calling private methods" issue. The structural concern is valid at MINOR severity.
- **Suggestion**: Convert to standard pytest fixtures that return values, or use a helper function instead of autouse.
- **LOC affected**: 40
- **Verified**: CONFIRMED (severity kept; CAT-6 classification noted as imprecise — this is fixture coupling, not private-method access)

---

### tests/repro_issues/repro_load_cargo_bug.py

#### CAT-3: Standalone repro script covered by proper tests elsewhere  [MINOR]
- **Location**: repro_load_cargo_bug.py:1-244
- **Issue**: This is a standalone diagnostic repro script using `unittest.TestCase` (line 18), with `print()` diagnostics (lines 99-104, 127-130, 230-237), and ends with `if __name__ == '__main__': unittest.main(verbosity=2)` (line 243-244). It exercises `TransferCommandHandler` and `TransferValidator` paths that are covered by proper unit tests in `tests/unit/strategy/` and `tests/integration/strategy/`. The file imports real production types (line 10-15: `IssueTransferCommand`, `TransferCommandHandler`, `TransferValidator`, `Planet`, `Fleet`, `ValidationResult`).
- **Suggestion**: Review whether the bug this reproduces is still present. If fixed, remove the file. If still present, convert to a focused pytest test in the appropriate integration test dir.
- **LOC affected**: 244
- **Verified**: CONFIRMED (severity kept; CAT-3 classification is a reasonable fit — this is a maintenance burden)

---

### tests/unit/strategy/services/ability_sources/test_system_archetype.py

#### CAT-9: Repeated _MockSystem construction  [MINOR]
- **Location**: test_system_archetype.py:16, 21, 26, 32, 41, 46
- **Issue**: Six module-level tests construct `_MockSystem(name=..., archetype=..., intrinsic_abilities=...)` inline. A fixture with parameterization would eliminate ~20 lines of duplication.
- **Suggestion**: Create a `@pytest.fixture` for `_MockSystem` and parametrize the archetype/abilities.
- **LOC affected**: 20
- **Verified**: CONFIRMED (severity kept)

---

## Cross-Shard Verified Findings

### APC-003: Private-method patching (Shard 02 files)

#### tests/unit/ui/screens/builder/test_modifier_logic_service.py:47-84
- **Verified**: 5 tests call `service._get_base_firing_arc(comp)` — a single-underscore private method at `game/ui/screens/builder/modifier_logic.py:131`. Confirmed as APC-003 instance.

#### tests/unit/simulation/systems/test_battle_engine_init_ship.py:65-93
- **Verified**: 4 tests call `battle_engine._initialize_ship(ship)` — a single-underscore private method at `game/simulation/systems/battle_engine.py:425`. Confirmed as APC-003 instance.

---

## Disputed & Inconclusive Claims

None. All 24 claims verified as substantiated by source code.

---

## Verification Notes

1. **test_camera.py fixture count**: Phase 1 reported 7 autouse `pygame.init()` fixtures. Verified 8 (includes `TestCameraUpdateInput` at line 355). Structural finding unchanged.
2. **test_ship_io.py class count**: Phase 1 reported 13 test classes. Verified 14 via grep. Structural finding unchanged.
3. **test_multi_selection_logic.py CAT-6**: The classification is imprecise — the issue is fixture design coupling (autouse fixture using `self`), not calling private methods. The structural concern is real; category labeling is noted as a minor mismatch.
4. **repro_load_cargo_bug.py CAT-3**: The report classifies this as "dead code guard" (CAT-3). The file is more accurately described as a redundant standalone repro script than a dead-code guard. Both classifications are reasonable.
