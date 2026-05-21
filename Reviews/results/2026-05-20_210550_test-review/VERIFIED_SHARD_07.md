# Shard 07 — Verified Findings

## Summary
- Shard: 07
- Claims reviewed: 34 (Phase 1: 30, Cross-shard: 4)
- CONFIRMED: 29 | DISPUTED: 5 | INCONCLUSIVE: 0
- Severity downgrades: 0

## Verified Findings (CONFIRMED only)

### tests/unit/simulation/systems/test_tick_phases.py

#### CAT-10: test_same_priority_maintains_insertion_order / test_custom_phase_alongside_others / test_create_default_phases_registers_expected_names_and_priorities [MINOR]
- **Location**: test_tick_phases.py:74-79, 89-95, 114-124
- **Issue**: Three tests verify registry phase ordering with structurally identical bodies — register phases (or call `create_default_phases()`), then check the resulting phase name list. Line 78 uses `[p.name for p in registry.phases]`, line 94 uses the same pattern, and line 117 extends it to `[(phase.name, phase.priority) for phase in registry.phases]`. All three exercise the same registry-read path with different input configurations.
- **Suggestion**: Parameterize into a single test with `@pytest.mark.parametrize` accepting (phase_specs, expected_names).
- **LOC affected**: 25
- **Verified**: CONFIRMED

### tests/integration/ui/test_camera_zoom.py

#### CAT-12: test_zoom_centers_on_mouse_simulation [MINOR]
- **Location**: test_camera_zoom.py:51-97
- **Issue**: Test body contains step-by-step mathematical derivation in comments and code. Computes `world_before` via `screen_to_world`, sets `camera.zoom = 2.0`, computes `new_world_at_mouse`, calculates `diff = world_before - new_world_at_mouse`, applies `camera.position += diff`, then asserts results. The test derives expected values rather than asserting against pre-computed constants. Comment lines walk through the math (lines 63-91).
- **Suggestion**: Split the derivation into a helper function; keep only final invariant assertions in the test with pre-computed expected values.
- **LOC affected**: 47
- **Verified**: CONFIRMED

### tests/unit/simulation/test_battle_outcome_replay_id.py

#### CAT-1: test_battle_outcome_has_replay_id_field_default_none [CRITICAL]
- **Location**: test_battle_outcome_replay_id.py:23-33
- **Issue**: Test creates a `BattleOutcome` without `replay_id` kwarg, then asserts `hasattr(outcome, "replay_id")` and `outcome.replay_id is None`. This cannot fail if the dataclass field exists with a None default — it exercises dataclass attribute-default mechanics, not any business logic. The `hasattr` assertion passes for any field existence; the `is None` assertion only tests the default value.
- **Suggestion**: Replace with an integration-level assertion (e.g., `extract_outcome` with a `NullCaptureSink` that verifies `replay_id` flows through the full pipeline).
- **LOC affected**: 11
- **Verified**: CONFIRMED

### tests/unit/ui/screens/test_event_log_window.py

#### CAT-8: _make_strategy_ui helper [MINOR]
- **Location**: test_event_log_window.py:259-306
- **Issue**: Helper patches `StrategyUI.__init__` with a no-op lambda, then manually sets 25+ individual attributes (scene, facade, width/height, manager, 15 window_manager attributes, etc.) to construct a partial stub. Construction setup dominates test method bodies; tests that use this helper spend >80% of their LOC on setup.
- **Suggestion**: Extract to a shared fixture or builder function at module level to reduce per-test attribute plumbing.
- **LOC affected**: 48
- **Verified**: CONFIRMED

#### CAT-6: _make_window bypasses __init__ [MAJOR]
- **Location**: test_event_log_window.py:44-88
- **Issue**: Patches `EventLogWindow.__init__` with a lambda no-op, then manually wires 10+ attributes (`all_events`, `current_filter`, `on_close_callback`, `ui_manager`, `data_source`, `column_manager`, `virtual_table`, `sidebar`, `_default_view_state`, 5 filter button mocks, `filter_buttons` dict). This mocks the constructor — an internal implementation detail. If `__init__` adds required initialization (e.g., new component tree building), these tests silently miss it.
- **Suggestion**: Use `bypass_init` context manager (already the accepted project pattern, used in `test_orders_window.py:51`) instead of `patch.object(__init__, ...)`.
- **LOC affected**: 45
- **Verified**: CONFIRMED

### tests/unit/strategy/engine/test_superweapon_order_processor.py

#### CAT-6: deep patching of SuperweaponValidator.find_ship_with_ability [MAJOR]
- **Location**: test_superweapon_order_processor.py:131, 166, 201, 622, 669, 708, 748, 909, 1049, 1132
- **Issue**: 10+ tests patch `game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability` — an internal implementation detail of the validator class. The SUT is `SuperweaponOrderProcessor`; these tests shortcut the validator's ship-finding logic entirely. A refactor that changes the validator's method name, signature, or moves find logic to a different module silently breaks these tests.
- **Suggestion**: Use a mock `component_registry` that contains the expected ability so the real `find_ship_with_ability` path is exercised; or test via the processor's public `process_*` methods with a fully-configured mock fleet/ship that the real validator can resolve.
- **LOC affected**: ~200
- **Verified**: CONFIRMED

### tests/unit/core/profiling/test_decorators.py

#### CAT-7: time.sleep(0.02) in test_context_manager_measures_time [MAJOR]
- **Location**: test_decorators.py:135-145
- **Issue**: Uses `time.sleep(0.02)` (line 142) to create measurable elapsed time within a `profile_block` context manager. This is a real blocking latency call in a unit test.
- **Suggestion**: Mock `time.perf_counter` to return incrementing values instead of actually sleeping.
- **LOC affected**: 11
- **Verified**: CONFIRMED

### tests/unit/simulation/combat/test_fleet_aura_cache.py

#### CAT-6: patches _aggregate_ability_groups [MAJOR]
- **Location**: test_fleet_aura_cache.py:83-88
- **Issue**: `test_uses_shared_aggregator` patches `game.simulation.combat.fleet_aura_manager._aggregate_ability_groups` — a module-private function. The patch sets a canned return value and verifies the function was called, but bypasses the actual aggregation logic. A refactor that changes `_aggregate_ability_groups`'s signature would keep the test passing with stale assertions.
- **Suggestion**: Verify aggregation behavior through the public `FleetAuraManager` interface (e.g., check bonus values after `initialize` with known abilities, allowing the real `_aggregate_ability_groups` to execute).
- **LOC affected**: 6
- **Verified**: CONFIRMED

#### CAT-1: test_providers_dirty_flag_exists [CRITICAL]
- **Location**: test_fleet_aura_cache.py:44-47
- **Issue**: Asserts `hasattr(mgr, '_providers_dirty')`. A test that passes if the attribute exists and fails if renamed; cannot verify correctness of the dirty-flag logic. The behavioral tests below (`test_update_with_no_changes_skips_recalculation` at line 49, `test_invalidate_forces_recalculation` at line 67) already validate the caching contract through actual state transitions.
- **Suggestion**: Remove this attribute-existence test; the behavioral tests provide genuine regression protection.
- **LOC affected**: 4
- **Verified**: CONFIRMED

### tests/unit/ui/screens/battle_setup/test_view_model.py

#### CAT-8: 6 identical from...import statements [MINOR]
- **Location**: test_view_model.py:14, 28, 35, 48, 61, 75
- **Issue**: Every test method repeats `from game.ui.screens.battle_setup.view_model import BattleSetupViewModel` inside the method body. The ViewModel is a pure data class with no pygame dependencies — there is no reason for method-level import.
- **Suggestion**: Move the import to module level (once).
- **LOC affected**: 6
- **Verified**: CONFIRMED

### tests/unit/ui/screens/test_lab/test_test_run_card.py

#### CAT-11: test_header_default_path_prioritizes_failed_validation [MINOR]
- **Location**: test_test_run_card.py:135-151
- **Issue**: Asserts exact format substrings in blitted text: `"1P 1F 0W"` at line 150 and `"Failed Metric:"` at line 148. If the summary formatting changes (e.g., commas added, labels reworded), this test fails even though the validation logic is correct.
- **Suggestion**: Assert that the validation summary values are present (e.g., check that "1" pass, "1" fail, and "0" warn are rendered) rather than exact format strings.
- **LOC affected**: 17
- **Verified**: CONFIRMED

### tests/unit/strategy/engine/test_engine_validation.py

#### CAT-9: 12 near-identical engine validation test classes [MINOR]
- **Location**: test_engine_validation.py:39-319
- **Issue**: Twelve classes (`TestHarvestingEngineValidation`, `TestConsumableManagementEngineValidation`, `TestResupplyEngineValidation`, `TestPlanetEnergyEngineValidation`, `TestProductionEngineValidation`, etc.) each with identical structure: `test_valid_empires_pass` (creates engine, calls `_validate_tick_inputs([_empire()])`) + `test_*_raises` (creates engine, calls with invalid input, expects `ValidationException`). The helper functions `_empire()` (line 17) and `_fleet()` (line 26) serve all classes, but the class structure is repeated 12 times across 280 LOC.
- **Suggestion**: Parameterize engine class and failure condition into a single parametrized test that iterates all engine types with expected failure modes.
- **LOC affected**: 280
- **Verified**: CONFIRMED

### tests/unit/ui/screens/test_strategy_input_handler_transfer.py

#### CAT-9: three identical mode-test classes [MINOR]
- **Location**: test_strategy_input_handler_transfer.py:44-275
- **Issue**: Three classes (`TestStrategyInputHandlerTransfer`, `TestDropCargoMode`, `TestLoadCargoMode`) share identical test patterns: key-press-sets-mode, left-click-in-mode-opens-dialog, right-click-cancels, escape-cancels. The same 4-part test structure repeats for each mode.
- **Suggestion**: Parameterize by `(key, mode, direction)` tuple.
- **LOC affected**: 230
- **Verified**: CONFIRMED

### tests/unit/simulation/entities/test_ship_stats.py

#### CAT-8: extensive mock setup for single assertion [MINOR]
- **Location**: test_ship_stats.py:12-55
- **Issue**: The test file defines `_TL_ABILITY` (SimpleNamespace, 3 attrs), `_VS_ABILITY` (SimpleNamespace, 1 attr), a `_HangarComponent` class with 4 methods (`is_active`, `is_operational`, `has_ability`, `get_abilities`), and constructs a 9-attribute MagicMock ship — all for one test function (`test_stats_aggregation_routes_hangar_abilities_to_launch_contributor`) with 4 assertions. Setup is 43 lines; test body is 8 lines.
- **Suggestion**: Extract hangar setup to a fixture if more hangar-component tests are added. Keep inline if this remains the sole test.
- **LOC affected**: 43
- **Verified**: CONFIRMED

### tests/unit/ui/screens/test_planet_abilities_controller_scanner.py

#### CAT-10: test_*_label tests could be parameterized [MINOR]
- **Location**: test_planet_abilities_controller_scanner.py:121-153
- **Issue**: `test_multiple_components_with_same_ability_get_instance_labels` (line 121) and `test_singleton_ability_has_empty_instance_label` (line 142) test the same scanner with different component counts. Both create a facility, create a controller, call `scan_abilities()`, and assert `instance_label` values.
- **Suggestion**: Parameterize component count and expected labels via `@pytest.mark.parametrize`.
- **LOC affected**: 32
- **Verified**: CONFIRMED

### tests/unit/ui/screens/test_strategy_detail_formatter.py

#### CAT-8: 6-level nested with patch() blocks [MINOR]
- **Location**: test_strategy_detail_formatter.py:129-151
- **Issue**: `test_show_detail_with_fleet_shows_fleet_buttons` (line 129) nests 6 `with patch()` context managers to control type-dispatch predicates (`is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment`). The 6-level indentation is a readability and maintainability issue.
- **Suggestion**: Use `patch.multiple` (already used in `test_show_detail_with_star_system` at line 114) to flatten all 6 patches into one context manager.
- **LOC affected**: 30
- **Verified**: CONFIRMED

### tests/integration/ui/test_event_log_replay_e2e.py

#### CAT-5: pygame_init fixture creates real display [MAJOR]
- **Location**: test_event_log_replay_e2e.py:21-25
- **Issue**: The `pygame_init` fixture calls `pygame.init()` and `pygame.display.set_mode((1024, 768), pygame.HIDDEN)` — function-scoped (default), creating a real graphical context per test. `pygame.init()` initializes all pygame modules; `pygame.quit()` tears down everything.
- **Suggestion**: Make the fixture module-scoped since all tests share the same display dimensions and it's read-only (no per-test display state changes). Alternatively, consider `class`-scope if tests modify display state.
- **LOC affected**: 5
- **Verified**: CONFIRMED

### tests/integration/ui/test_build_queue_enhanced_planet_report.py

#### CAT-5: planet_report_panel fixture constructs real pygame_gui elements [MAJOR]
- **Location**: test_build_queue_enhanced_planet_report.py:92-112
- **Issue**: The fixture creates a real `pygame_gui.elements.UIPanel`, `PlanetReportPanel`, and nested `pygame_gui.elements.UIImage` per test function. `PlanetReportPanel.__init__` constructs a full widget tree. This is heavy per-function UI construction.
- **Suggestion**: Use module-scoped fixture with shared panel, or test the logic layer (planet report formatting) separately from the pygame_gui widget tree.
- **LOC affected**: 21
- **Verified**: CONFIRMED

### tests/regression/test_generator_crew_requirement_design.py

#### CAT-12: test_generator_without_crew_is_inactive / test_generator_with_crew_is_active [MINOR]
- **Location**: test_generator_crew_requirement_design.py:32-106
- **Issue**: Both tests contain defensive fallback logic: `if layer_key is None:` branches at lines 45-49 and 80-81. The first test includes a `print(f"DEBUG...")` statement at line 47. These are if/else branches and a debug print inside the test body — both logic-heavy patterns.
- **Suggestion**: Move the layer-key resolution to a helper; remove the debug print from the test.
- **LOC affected**: 75
- **Verified**: CONFIRMED

### tests/unit/strategy/data/test_group_policies.py

#### CAT-4: test_registry_loads_from_data_file duplicate [MAJOR]
- **Location**: test_group_policies.py:20-29
- **Issue**: `test_registry_loads_from_data_file` asserts `len(registry.targeting_policies) > 0` and same for movement/retreat. The parameterized `test_policy_registry_structural_invariants` at line 31 covers the same ground (loads registry, asserts non-zero policies per axis via the param `'targeting'`, `'movement'`, `'retreat'`) with better structural assertions. Two tests verify the same code path.
- **Suggestion**: Remove `test_registry_loads_from_data_file`; the parameterized version is the canonical structural test (PROJ-322 Task 1.11 already consolidated the three-per-axis tests into this one).
- **LOC affected**: 10
- **Verified**: CONFIRMED

### tests/unit/ui/screens/test_orders_window.py

#### CAT-6: _make_window uses bypass_init [MAJOR]
- **Location**: test_orders_window.py:48-59
- **Issue**: Uses `bypass_init(OrdersWindow)` to skip real construction, then passes mocked `pygame.Rect`, `MagicMock(name="ui_manager")`, etc. While `bypass_init` is the accepted project pattern, the `test_window_instance_*` tests all operate on a window whose `__init__` never ran — so they can't catch regressions in constructor behavior (e.g., new widget tree initialization, required attribute defaults not set by the bypass).
- **Suggestion**: Add at least one integration test with a real (bypass_init-free) construction to verify the full two-stage lifecycle.
- **LOC affected**: 12
- **Verified**: CONFIRMED

### tests/unit/ui/screens/builder/test_modifier_utils.py

#### CAT-9: redundant class definitions duplicated in other tests [MINOR]
- **Location**: test_modifier_utils.py:10-17
- **Issue**: `_Modifier` and `_SpecialModifier` classes are defined locally with `definition` and `value` attributes. Similar stub classes serving the modifier/ship-design domain appear in `test_workshop_viewmodel_selection.py` and `test_builder_selection.py` (though with different attribute sets — see DUP-006 for the distinction).
- **Suggestion**: Extract to a shared test fixture/helper module for the builder/workshop test suite.
- **LOC affected**: 8
- **Verified**: CONFIRMED

### tests/unit/strategy/fleet_movement_engine/conftest.py

#### CAT-9: mock_fleet fixture duplicates across test modules [MINOR]
- **Location**: fleet_movement_engine/conftest.py:21-38
- **Issue**: The `mock_fleet` fixture creates a `MagicMock(spec=Fleet)` with 16 attributes (id, owner_id, location, speed, path, orders, get_current_order, pop_order, clear_orders, resources.has_resources_for_movement, resources.has_resources_for_warp, capabilities.can_use_warp, etc.). This is nearly identical to the `mock_fleet` fixture in `test_fleet_order_transfer.py:21-36` — both spec `Fleet` with the same core attributes.
- **Suggestion**: Consolidate into a shared conftest at a higher directory level (e.g., `tests/unit/strategy/conftest.py`).
- **LOC affected**: 18
- **Verified**: CONFIRMED

### tests/unit/research/research_controls/test_reset_state.py

#### CAT-6: binds real method to mock via lambda [MAJOR]
- **Location**: test_reset_state.py:30
- **Issue**: `panel.reset = lambda t, tt: rc.ResearchControlPanel.reset(panel, t, tt)` — binds the unbound production method to a MagicMock instance via a lambda closure. If the production method signature changes (e.g., adds a third parameter), the lambda either raises TypeError (wrong arg count) or silently passes wrong values (if `*args` is used). The closure also shadows the real method, meaning changes to `ResearchControlPanel.reset`'s behavior won't be exercised.
- **Suggestion**: Use `MagicMock(wraps=rc.ResearchControlPanel)` or test through the panel's public interface without reassigning `reset`.
- **LOC affected**: 1
- **Verified**: CONFIRMED

### tests/integration/quickstart/test_quickstart_flow.py

#### CAT-5: full_quickstart_1p / full_quickstart_2p fixtures are heavy [MAJOR]
- **Location**: test_quickstart_flow.py:19-63
- **Issue**: Both fixtures run full `GameSession` construction, `SaveGameService.save_game()` (filesystem I/O), `QuickstartBuilder.copy_quickstart_designs()` (filesystem I/O), `QuickstartBuilder.spawn_initial_complexes()`, and cleanup via `shutil.rmtree()`. All per-test (function-scoped default). This includes multiple disk writes.
- **Suggestion**: Make these fixtures module-scoped to share the expensive setup across all tests in the class.
- **LOC affected**: 45
- **Verified**: CONFIRMED

### tests/unit/strategy/planet_atmosphere/test_generation.py

#### CAT-12: test_greenhouse_warming with for-loop logic [MINOR]
- **Location**: test_generation.py:146-167
- **Issue**: Uses `for _ in range(20)` loop (line 158) with `if "CO2" in composition` branching (line 160) inside the test body. The final assertion at line 166 has conditional logic: `assert warming_found or len(temps) == 0`. The test contains loops, branches, and a derived assertion that depends on stochastic sampling outcomes.
- **Suggestion**: Extract the sampling loop to a helper; assert the helper's output directly. Pre-compute expected values rather than deriving them in the test.
- **LOC affected**: 22
- **Verified**: CONFIRMED

---

### Cross-Shard Duplicates (CONFIRMED)

#### HLP-001: MockGameSession duplicated in test_error_handling.py [MAJOR]
- **Location**: test_error_handling.py:24-51 (Shard 07 copy)
- **Duplicated in**: `conftest.py:12` (Shard 16), `test_save_load_ops.py:24` (Shard 16), `test_save_selection.py:36` (Shard 03), `test_auto_save.py:14` (Shard 15)
- **Issue**: The `MockGameSession` class in `test_error_handling.py` is byte-for-byte identical to the copy in `conftest.py` (same `__init__` signature, same `to_dict()` method, same dict structure with `turn_number`, `save_path`, `config`, `galaxy`, `empires`, `human_player_ids`). The conftest copy is the natural single source of truth for this directory.
- **Suggestion**: Delete the local copy in `test_error_handling.py`. Import from `tests/unit/strategy/save_game_service/conftest.py` (or move to a higher-level shared conftest).
- **LOC affected**: 28
- **Verified**: CONFIRMED

#### HLP-005: setup_tmpdir fixture pattern duplicated in test_error_handling.py [MAJOR]
- **Location**: test_error_handling.py:57-67 (Shard 07 copy)
- **Duplicated in**: `conftest.py:42` (Shard 16), `test_save_load_ops.py:57` (Shard 16), `test_auto_save.py:48` (Shard 15)
- **Issue**: The `setup_tmpdir` fixture in `test_error_handling.py` (autouse function-scoped) creates a tempdir via `tempfile.mkdtemp()`, makes a `saves` subdirectory, patches `Paths.SAVES_DIR`, yields, then cleans up with `shutil.rmtree()`. The conftest fixture (line 42) uses the same pattern with `patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir)`. Identical 10-line pattern across 4 files.
- **Suggestion**: Move to `tests/conftest.py` as a session-scoped fixture or reusable context manager. The save_game_service conftest already has the canonical `setup_tmpdir` at line 42.
- **LOC affected**: 15
- **Verified**: CONFIRMED

#### HLP-006: _make_empire(colonies=None) pattern duplicated in test_empire.py [MINOR]
- **Location**: test_empire.py:17-20 (Shard 07 copy)
- **Duplicated in**: 5 other files across shards 03, 05, 09, 10
- **Issue**: `_make_empire(colonies=None)` creates an `Empire` with `empire_id`, `name`, `color`, and assigns mock colonies. This pattern is duplicated across at least 6 strategy engine test files. The `tests/unit/strategy/engine/` directory has no shared conftest for these helpers.
- **Suggestion**: Extract to `tests/unit/strategy/engine/conftest.py` as a shared fixture factory.
- **LOC affected**: 5
- **Verified**: CONFIRMED

## Disputed & Inconclusive Claims

| Original ID | File | CAT | Original Severity | Verdict | Reason |
|-------------|------|-----|-------------------|---------|--------|
| test_object_without_methods_fails_protocol | test_tick_phases.py:105-108 | CAT-2 | CRITICAL | DISPUTED | Test imports `ITickPhase` from `game.simulation.systems.tick_phase` (line 10) — a real production type. `isinstance(NotAPhase(), ITickPhase)` exercises protocol compliance checking against a production Protocol, not a mocked construct. CAT-2 requires "No imports from game.*" or "never touches production code paths" — both falsified. The test IS trivial (it tests Python's `@runtime_checkable` behavior) but should be CAT-1, not CAT-2. |
| test_transfer_* (3 tests) | test_fleet_order_transfer.py:90-118 | CAT-2 | CRITICAL | DISPUTED | The `processor` fixture creates a REAL `OrderProcessor()` (line 82-83), not a MagicMock. `processor.get_handler(OrderType.TRANSFER)` returns a real handler from the production registry. The handler's `execute_action_order()` runs real guard-clause code. Only the inputs (fleet, empire, galaxy) are mocks — standard boundary isolation. These tests exercise real production guard-clause paths (null order, wrong type, invalid params). They have genuine regression protection value as negative-path tests. |
| test_save_design_writes_file_with_metadata | test_save_design.py:52-65 | CAT-11 | MINOR | DISPUTED | The assertion `"_metadata" in payload` tests a well-defined save-format contract key, not a fragile formatting detail. The save format including `_metadata` is a stable contract — if the key name changes, the test SHOULD fail because the save format changed. This is valid contract testing, not over-assertion. The suggestion to test via the repository's public API is a CAT-9 simplification suggestion, not a CAT-11 fragile-assertion issue. |
| mock_ship fixture | test_ai_controller_interface.py:63-88 | CAT-5 | MINOR | DISPUTED | Setting 22 attributes on a MagicMock is NOT expensive. No file I/O, no pygame init, no registry hydration — just `MagicMock().attr = value` assignments (O(1) each). CAT-5 is about fixtures that "rebuild expensive state" (file I/O, registry hydration, pygame.font.init). This is a CAT-9 duplication issue (the same setup appears in `test_controllable_adapter.py`), not fixture bloat. |
| DUP-006: Stub Modifier classes duplicated | test_modifier_utils.py / test_workshop_viewmodel_selection.py / test_builder_selection.py | DUP | MAJOR | DISPUTED | The stub classes are NOT the same pattern. `_Modifier` in `test_modifier_utils.py:10` has `definition` and `value` attributes. `_Component` in `test_workshop_viewmodel_selection.py:10` has only `id`. `MockComponent` in `test_builder_selection.py:13` has only `id`. These serve different domains (modifier utilities vs component selection) with different attribute structures. The cross-shard report's claim of "identical stub pattern" with "id, name, operation, value, primary_scalar attrs" does not match the actual code. |
