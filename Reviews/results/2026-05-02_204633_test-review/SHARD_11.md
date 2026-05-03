# Shard 11 — Test Audit Report

## Summary
- Shard: 11
- Files assigned: 88
- Files actually read: 88
- Total findings: 40
- Critical: 4 | Major: 12 | Minor: 24

## Findings

### tests/unit/test_lab/test_testruncard_propulsion.py (~229 LOC)

#### CAT-2: Entire file tests nothing real  [CRITICAL]
- **Location**: test_testruncard_propulsion.py:1-229
- **Issue**: File contains zero imports from `game.*`. All 14 test functions exercise locally-constructed mock data and string-formatting logic that is not the system under test. No production code path is verified; all assertions validate fixture data shape or locally computed strings.
- **Suggestion**: Remove file. Tests like `test_velocity_format` (line 193) that verify `f"Velocity: {start_vel:.1f} -> {end_vel:.2f}"` test Python f-string behavior, not production code. If a `TestRunCard` component exists in production, tests should instantiate and exercise it with real metrics data.
- **LOC affected**: 229

#### CAT-10: 8 format-string tests should be parametrized  [MINOR]
- **Location**: test_testruncard_propulsion.py:193-229
- **Issue**: `test_velocity_format`, `test_distance_format`, `test_angle_format`, `test_expected_vs_actual_angle_format` all test the same pattern — formatting mock metric values into strings. Could be one parametrized test.
- **Suggestion**: Parametrize into single `test_metrics_formatting` with test cases for each metric type.
- **LOC affected**: 37

---

### tests/unit/ui/test_race_summary_panel.py (~646 LOC)

#### CAT-1: test_race_summary_panel_stores_race_config  [CRITICAL]
- **Location**: test_race_summary_panel.py:130-138
- **Issue**: Creates panel via `__new__` bypass, sets `panel.race_config = mock_race_config`, then asserts `panel.race_config is mock_race_config`. This tests Python attribute assignment, not panel behavior.
- **Suggestion**: Remove. The attribute-storage behavior is tested implicitly by every other test that uses `panel.race_config`.
- **LOC affected**: 9

#### CAT-1: test_on_load_race_callback_stored and test_has_load_button_reference  [CRITICAL]
- **Location**: test_race_summary_panel.py:348-367
- **Issue**: Both tests create a bypass-init panel, set an attribute, and assert equality or hasattr. No production logic exercised.
- **Suggestion**: Remove both tests.
- **LOC affected**: 20

#### CAT-1: Feat12 button callback storage tests  [MINOR → downgraded: low blast radius]
- **Location**: test_race_summary_panel.py:378-393
- **Issue**: `test_on_randomize_all_callback_stored` and `test_has_btn_randomize_all_attribute` test attribute assignment on bypass-init panel. Same trivial-pass pattern.
- **Suggestion**: Remove. `test_constructor_accepts_on_randomize_all_callback` (line 395) already validates the constructor signature.
- **LOC affected**: 16

#### CAT-8: _refresh_with_mocked_uilabel helper is deeply nested  [MINOR]
- **Location**: test_race_summary_panel.py:447-494
- **Issue**: Helper method creates 4 nested `with patch` blocks, manually assigns 14 attributes on a bypass-init panel, and captures label constructor call arguments. This is 47 lines of setup serving as the core mechanism for 7 test methods.
- **Suggestion**: Extract to a dedicated fixture that returns pre-configured panel + captured texts, reducing each test's cognitive overhead.
- **LOC affected**: 47

---

### tests/unit/ui/components/table/test_virtual_table.py (~861 LOC)

#### CAT-6: 5× @patch decorator on every test is brittle  [MAJOR]
- **Location**: test_virtual_table.py:78-81 (and repeated 11x through file)
- **Issue**: Every test method carries 5 `@patch` decorators for `UIPanel`, `UILabel`, `UIScrollBar`, `UIImage`, `TableHeader`. If pygame_gui renames or removes any of these, all 12 tests fail even if VirtualTable logic is unchanged. Mock setup encodes the internal call chain of `VirtualTable.__init__`.
- **Suggestion**: Move patches into a class-scoped autouse fixture that sets up all 5 pygame_gui mocks once, returning defaults. Each test then only overrides what it needs via `mock_xxx.return_value`.
- **LOC affected**: ~60 (repeated decorator blocks)

#### CAT-8: Deeply repetitive mock setup across 12 tests  [MINOR]
- **Location**: test_virtual_table.py:83-555 (each test body)
- **Issue**: Every test repeats the same 10-15 lines of mock scrollbar/list_panel creation and `VirtualTable` instantiation. The `mock_panel_class.return_value` pattern with `get_relative_rect.return_value = pygame.Rect(...)` appears verbatim 11 times.
- **Suggestion**: Extract a helper `_make_table(data_source, column_manager, **overrides)` that creates the table with all default mocks and returns `(table, mocks_dict)`.
- **LOC affected**: ~150 (repeated setup lines)

#### CAT-12: test_update_visible_rows_disables_edge_action_buttons is logic-heavy  [MINOR]
- **Location**: test_virtual_table.py:668-770
- **Issue**: Test body is 102 lines with manual scroll percentage calculation (`total_h = row_count * table._row_height; mock_scrollbar.start_percentage = ...`), direct `_row_pool` list manipulation, and if/else branching on disable/enable assertions. The arithmetic for computing scroll percentage from row index makes the test error-prone.
- **Suggestion**: Extract scroll-calculation step into a helper `_set_scroll_to_row(table, mock_scrollbar, row_idx, row_count)` and hard-code expected values rather than computing them.
- **LOC affected**: 102

---

### tests/unit/ai/test_controllable_adapter.py (~213 LOC)

#### CAT-2: Tests only exercise ABC interface contract, not production behavior  [MAJOR]
- **Location**: test_controllable_adapter.py:1-213
- **Issue**: All tests verify Python ABC mechanics — `TypeError` on direct instantiation, `__abstractmethods__` contents, `isinstance` checks. These test `abc.ABC` behavior, not the `IControllable` interface semantics. A `test_mock_implementation_satisfies_interface` (line 66) constructs a 30-method mock class that never calls production code.
- **Suggestion**: Keep `test_cannot_instantiate_icontrollable` and `test_all_abstract_methods_present` as lightweight contract checks. Remove the 50-line `MockControllable` implementation and `test_isinstance_check_with_mock` — they duplicate what Python's ABC guarantees without adding domain value.
- **LOC affected**: ~130 (MockControllable class + isinstance test)

---

### tests/unit/ui/test_battle_panels_extended.py (~631 LOC)

#### CAT-4: Three copy-pasted setup_mocks fixtures  [MAJOR]
- **Location**: test_battle_panels_extended.py:39-66, 225-247, 402-424
- **Issue**: `TestShipStatsPanelExtended.setup_mocks`, `TestSeekerMonitorPanelExtended.setup_mocks`, and `TestBattleControlPanelExtended.setup_mocks` are near-identical: they all patch `sys.modules['pygame']`, import-reload `battle_panels`, and set up a mock scene. Only difference is the mock scene's attribute population.
- **Suggestion**: Consolidate into a single class-scoped helper `_setup_pygame_and_panels()` that returns the module and a fresh mock scene, letting each test class configure extra scene attributes as needed.
- **LOC affected**: ~60 (two redundant fixtures)

#### CAT-6: setup_mocks patches sys.modules and reloads the module  [MAJOR]
- **Location**: test_battle_panels_extended.py:48-53
- **Issue**: Fixtures call `patch.dict(sys.modules, {'pygame': mock_pygame})` then `importlib.reload(battle_panels)`. This is extremely brittle — if any other module cached a reference to `battle_panels` during import, the reload may not propagate. Also risks state leakage between test classes.
- **Suggestion**: Use `patch.object` on specific functions the panel calls (e.g., `pygame.draw.rect`) rather than replacing the entire `pygame` module namespace.
- **LOC affected**: ~10 per fixture

#### CAT-10: expand/collapse toggle tests should be parametrized  [MINOR]
- **Location**: test_battle_panels_extended.py:195-209, 324-336
- **Issue**: `test_toggle_expanded_adds_and_removes` and `test_seeker_expansion_toggle` follow identical pattern: add ID to set via toggle, assert present; toggle again, assert absent.
- **Suggestion**: Parametrize as single test with `[(panel_type, toggle_method, id_attr), ...]`.
- **LOC affected**: 30

---

### tests/integration/ui/test_colonization_facade.py (~836 LOC)

#### CAT-1: No session/turn_engine/galaxy property tests verify implementation detail  [MINOR → downgraded: test cleanup validation]
- **Location**: test_colonization_facade.py:40-60
- **Issue**: Three tests (`test_no_session_property`, `test_no_turn_engine_property`, `test_no_galaxy_property`) check `ColonizationSystem.__dict__` for absent keys. This tests the internal structure of a class — useful as a one-time migration guard, but permanently testing that a class doesn't have a property is a fragile implementation-detail check. If a property is added later for a legitimate reason, these tests break for the wrong reason.
- **Suggestion**: Downgrade these to a single migration-validation test gated by a skip marker defined for the relevant PROJ, or remove. These are read-once migration checkers, not ongoing regression tests.
- **LOC affected**: 21

#### CAT-10: Success/failure duplicate patterns in issue_colonize_order and queue_colonize_mission tests  [MINOR]
- **Location**: test_colonization_facade.py:136-178, 213-258
- **Issue**: `test_issue_colonize_returns_success` (line 136) and `test_issue_colonize_returns_error_on_failure` (line 157) have identical bodies except the expected result type. Same for `queue_colonize_mission` pair (lines 214, 237). Could be two parametrized tests.
- **Suggestion**: Parametrize with `[(ValidationResult(), 'success'), (ValidationResult.error('msg'), 'error')]`.
- **LOC affected**: 82

#### CAT-10: Multiple pod-filtering tests with identical structure  [MINOR]
- **Location**: test_colonization_facade.py:474-551 (four `on_colonize_click` tests)
- **Issue**: `test_on_colonize_shows_all_planets_with_universal_pods`, `test_on_colonize_ignores_pod_count_at_command_time`, `test_on_colonize_no_pods_still_prompts` share identical setup and assertion patterns differing only in pod availability and expected planet count.
- **Suggestion**: Parametrize with `[(pods_dict, expected_planet_count), ...]`.
- **LOC affected**: ~80

---

### tests/unit/ui/services/test_validation_service.py (~100 LOC)

#### CAT-6: Tests mock the entire validator dependency, asserting delegation only  [MAJOR]
- **Location**: test_validation_service.py:14-101
- **Issue**: All four tests mock the validator and assert that `ValidationService` delegates correctly — e.g., `mock_validator.validate_addition.assert_called_once_with(...)`. These tests verify that a facade calls through to its injected dependency with the right arguments. If `ValidationService` is refactored to compose differently but still produce correct results, these tests break.
- **Suggestion**: Keep `test_service_creates_default_validator_when_none_provided` (line 54) as it tests a real code path. Remove `test_validate_addition_delegates_to_validator` and `test_validate_design_delegates_to_validator` — they test the mock framework, not production behavior. Replace with one integration test using a real validator.
- **LOC affected**: ~45

---

### tests/unit/ui/panels/test_ship_stats_renderer.py (~390 LOC)

#### CAT-10: Five get_hp_bar_color tests should be parametrized  [MINOR]
- **Location**: test_ship_stats_renderer.py:118-171
- **Issue**: `test_high_hp_returns_green`, `test_medium_hp_returns_yellow`, `test_low_hp_returns_red`, `test_inactive_component_returns_dim_red`, `test_boundary_fifty_percent`, `test_boundary_twenty_percent` — six tests testing a single function with different inputs.
- **Suggestion**: Parametrize into one test with `[(ratio, is_active, expected_color), ...]`.
- **LOC affected**: 54

#### CAT-10: Five get_component_status_display tests should be parametrized  [MINOR]
- **Location**: test_ship_stats_renderer.py:178-236
- **Issue**: Five tests for different ComponentStatus values all call the same function and check text + color. Identical structure.
- **Suggestion**: Parametrize into one test with `[(status, expected_text, expected_color), ...]`.
- **LOC affected**: 58

#### CAT-10: Three draw_stat_bar tests should be parametrized  [MINOR]
- **Location**: test_ship_stats_renderer.py:53-110
- **Issue**: `test_draw_stat_bar_with_zero_percent`, `test_draw_stat_bar_with_fifty_percent`, `test_draw_stat_bar_with_hundred_percent`, `test_draw_stat_bar_clamps_over_hundred`, `test_draw_stat_bar_handles_negative` — five tests, identical bodies except input percentage.
- **Suggestion**: Parametrize into one test.
- **LOC affected**: 57

#### CAT-10/12: ResourceColors/RESOURCE_ORDER_PRIORITY tests verify constants  [MINOR]
- **Location**: test_ship_stats_renderer.py:303-349
- **Issue**: Six tests verifying hardcoded color constants and priority values. These are logic-light but test static data that almost never changes. If a color value changes, these fail — but they provide regression protection against accidental edits.
- **Suggestion**: These are fine as-is (constants-verification tests are legitimate, per rubric). No action needed, but noted for completeness.
- **LOC affected**: 0 (no change recommended)

---

### tests/unit/ui/panels/test_build_queue_portraits.py (~145 LOC)

#### CAT-12: test_load_resource_icons_fallback_on_missing_file patches file I/O  [MINOR]
- **Location**: test_build_queue_portraits.py:75-90
- **Issue**: Test patches `pygame.image.load` to raise `FileNotFoundError`, then asserts fallback surfaces are created. The `with patch('pygame.image.load', ...)` block is nested inside a test that also creates a real `BuildQueuePortraitLoader`. This mixes real and mocked I/O paths.
- **Suggestion**: Keep as-is — the test exercises a real fallback path with a reasonable mock of the file I/O boundary. Noted for completeness only.
- **LOC affected**: 0 (acceptable)

---

### tests/unit/modifiers/test_pipeline_unification.py (~166 LOC)

#### CAT-7/12: Multiple tests call `.recalculate_stats()` then check individual stat values  [MINOR]
- **Location**: test_pipeline_unification.py:13-92
- **Issue**: Four tests in `TestSingleRecalculatePath` each create a component from production data, add a modifier, and assert a specific numeric multiply. These depend on the live `components.json` data values — if the data is rebalanced, test values need updating. This is expected behavior for component integration tests; downgraded to MINOR because data-driven tests inherently couple to data.
- **Suggestion**: Consider loading test-specific component definitions rather than relying on production data for exact multiplier verification.
- **LOC affected**: 0 (acceptable — data contract tests)

---

### tests/unit/strategy/engine/test_commands.py (~364 LOC)

#### CAT-2: Some tests exercise only dataclass default behavior  [MINOR → downgraded: low blast radius]
- **Location**: test_commands.py:41-44
- **Issue**: `test_command_name_property` checks that a dataclass `.name` returns the class name. This tests Python's `__class__.__name__` behavior, not game-specific logic.
- **Suggestion**: Remove. Dataclass defaults (like `planet_id is None`) are tested in 3+ places yet come for free from Python's `=None` default.
- **LOC affected**: 4

#### CAT-10: Command property tests could be parametrized  [MINOR]
- **Location**: test_commands.py:38-342 (many test classes)
- **Issue**: Many command test classes (`TestIssueColonizeCommand`, `TestIssueMoveCommand`, etc.) have identical structure: create command, assert attributes, assert `type == CommandType.ISSUE_ORDER`.
- **Suggestion**: Parametrize into a single test that iterates over `(command_class, kwargs, expected_attrs)` tuples.
- **LOC affected**: ~100 (redundant test structure)

---

### tests/unit/simulation/combat/test_damage_calculator.py (~1199 LOC)

#### CAT-5: mock_component and mock_ship factory fixtures could be shared  [MAJOR]
- **Location**: test_damage_calculator.py:338-370
- **Issue**: `mock_component` and `mock_ship` factory fixtures (lines 338-370) are defined as function-scoped helpers inside a single test class but are conceptually reusable across all test classes in the file. Every test that needs a mock ship/component rebuilds these from scratch.
- **Suggestion**: Move to module-level fixtures with `function` scope (they remain function-scoped because tests mutate the mocks).
- **LOC affected**: 0 (rescoping only)

#### CAT-8: Extremely granular test classes with 3-line tests  [MINOR]
- **Location**: test_damage_calculator.py:606-822 (TestDamageLayerBoundaryConditions, 10 tests; TestDamageLayerDirectMethod, 5 tests)
- **Issue**: Many 5-8 line tests that test edge cases like "zero damage", "exactly equal HP", "fractional damage". While each edge case deserves coverage, the class-per-edge-group + 3-line-test pattern inflates LOC without organizing insight.
- **Suggestion**: Consolidate boundary-condition tests into a parametrized test: `[(damage, initial_hps, expected_hps), ...]`.
- **LOC affected**: ~200 (could be reduced ~60% via parametrization)

---

### tests/unit/builder/test_builder_drag_drop_real.py (~244 LOC)

#### CAT-6: setup_builder fixture mocks internal UI initialization heavily  [MAJOR]
- **Location**: test_builder_drag_drop_real.py:20-130
- **Issue**: The fixture patches `_create_ui` (line 29) — a private method — and then manually assigns 10+ mock attributes that `_create_ui` would have created (lines 56-65). Tests then call `handle_event` and assert on `builder.viewmodel.add_component_instance` (a mock). This tests the event-routing internal chain, not the end-to-end behavior.
- **Suggestion**: If `_create_ui` is too expensive to run, extract the event-handling logic under test into a separate, testable function rather than patching privates.
- **LOC affected**: ~110

---

### tests/unit/modifiers/test_beam_weapon_bindings.py (~123 LOC)

#### CAT-4: Duplication with test_weapon_ability_bindings.py structure  [MAJOR]
- **Location**: test_beam_weapon_bindings.py:1-123
- **Issue**: This file mirrors `test_weapon_ability_bindings.py` almost exactly — same test class structure (`TestBeamWeaponAbilityStatBindings`, `TestBeamWeaponAbilityRecalculate`, `TestBeamWeaponAbilityEffectSummary`), same pattern of MockComponent classes, same assertion patterns. The only difference is checking `BeamWeaponAbility` instead of `WeaponAbility` + accuracy_add binding.
- **Suggestion**: Merge into `test_weapon_ability_bindings.py` as additional parametrized cases or a single test class covering both `WeaponAbility` and `BeamWeaponAbility`.
- **LOC affected**: 123

---

### tests/integration/ui/test_design_selector.py (~89 LOC)

#### CAT-11: test_portrait_load_success_no_warning assertion on log text content is fragile  [MINOR]
- **Location**: test_design_selector.py:59-89
- **Issue**: `test_portrait_load_success_no_warning` filters log records checking `'portrait' in r.message.lower() or 'Working_Design' in r.message`. If the log message format changes (e.g., different wording), the test may pass incorrectly or miss warnings.
- **Suggestion**: Assert that the total count of warning-level records from the relevant logger is zero, rather than filtering on substring matches.
- **LOC affected**: 10

---

### tests/unit/simulation/systems/test_exit_policy.py (~143 LOC)

#### CAT-5: Each test creates a fresh BattleEngine with a boundary  [MINOR → downgraded: justified for isolation]
- **Location**: test_exit_policy.py:42-143
- **Issue**: Each of 7 tests creates a new `BattleEngine(boundary=...)`, `AIControllerFactory()`, and one or more `Ship` instances. The `RectBoundary` and `CircleBoundary` could be module-level constants.
- **Suggestion**: Move boundary objects to module-level constants.
- **LOC affected**: ~15 (reduction)

---

### tests/unit/simulation/test_component_decoupling.py (~233 LOC)

#### CAT-5: setup_and_teardown fixtures call initialize_ship_data() + load_components for each class  [MAJOR]
- **Location**: test_component_decoupling.py:30-36, 96-102, 177-183
- **Issue**: Three test classes each have an `autouse setup_and_teardown` fixture that calls `initialize_ship_data()` and `load_components()` — expensive file I/O that loads the same data repeatedly (3 times in this file).
- **Suggestion**: Consolidate into a single session-scoped fixture or reuse conftest.py's `fresh_registries` which already hydrates registries.
- **LOC affected**: 0 (rescoping — already using `fresh_registries` in most tests, these `initialize_ship_data` calls are redundant)

---

### tests/unit/strategy/engine/test_fleet_transfer_extended.py (~250 LOC)

#### CAT-10: _execute_fleet_transfer tests follow identical pattern  [MINOR]
- **Location**: test_fleet_transfer_extended.py:65-135 (8 tests)
- **Issue**: All 8 tests in `TestExecuteFleetTransfer` call `processor._execute_fleet_transfer(fleet, target, resource, direction, amount)` and assert the returned integer. The differences are in cargo_current, cargo_capacity, and expected result.
- **Suggestion**: Parametrize into one test with `[(cargo_src, cap_src, cargo_dst, cap_dst, direction, amount, expected), ...]`.
- **LOC affected**: ~70

---

### tests/unit/strategy/engine/test_planetary_yard_requirement.py (~89 LOC)

#### CAT-9: _make_yard_facility duplicates similar helper in test_tick_consumption.py  [MINOR]
- **Location**: test_planetary_yard_requirement.py:15-25
- **Issue**: `_make_yard_facility()` and `_make_planetary_yard_facility()` in `test_tick_consumption.py` (line 25) create identical `PlanetaryFacility` instances with the same structure.
- **Suggestion**: Move to a shared test fixture in `tests/fixtures/`.
- **LOC affected**: 10

---

### tests/unit/quickstart/test_quickstart_races.py (~114 LOC)

#### CAT-11: test_race_has_valid_theme uses hardcoded theme list  [MINOR]
- **Location**: test_quickstart_races.py:84-88
- **Issue**: `valid_themes = ["Federation", "Atlantians", "Romulans", "Klingons"]` is hardcoded. Adding a new theme requires updating this test.
- **Suggestion**: Derive valid themes from the theme registry or data directory, or widen the assertion to "theme_id is non-empty string".
- **LOC affected**: 5

---

### tests/unit/simulation/systems/test_ship_stats_calculator_phases.py (~371 LOC)

#### CAT-8: _create_mock_ship is 45 lines of mock infrastructure  [MINOR]
- **Location**: test_ship_stats_calculator_phases.py:28-72
- **Issue**: The `_create_mock_ship` helper constructs a MagicMock ship with 15+ manually assigned attributes, two lambda functions, and a manual iteration loop. This is complex setup for each of the 10 tests.
- **Suggestion**: Consider using a real `Ship` object with actual `LayerData` — the tests already use real `Component` objects. Moving from mock to real ship reduces the mock maintenance burden and increases test fidelity.
- **LOC affected**: 45

---

### tests/unit/ui/screens/builder/test_modifier_control_row.py (~173 LOC)

#### CAT-8: Two near-identical fixtures creating ModifierControlRow  [MINOR]
- **Location**: test_modifier_control_row.py:12-36, 111-139
- **Issue**: `mock_mod_def` + `row` fixtures are duplicated in `TestModifierControlRowGetLocalBounds` and `TestModifierControlRowSetControlsEnabled`. The only difference is the second class adds `row.entry`, `row.slider`, `row.buttons` afterward.
- **Suggestion**: Share fixtures via class inheritance or module-level fixture with optional overrides.
- **LOC affected**: ~60

---

### tests/integration/save_load/test_full_roundtrip.py (~225 LOC)

#### CAT-7: _check_keys_are_strings / _check_serializable recursive helpers  [MINOR]
- **Location**: test_full_roundtrip.py:201-225
- **Issue**: Two recursive functions that walk the full serialized game state dict. This is heavyweight verification after each round-trip, but the functions themselves are well-isolated and used as test assertions rather than test computation per se.
- **Suggestion**: Replace with a single recursive function that checks both constraints to avoid traversing the dict tree twice.
- **LOC affected**: 25

---

### tests/unit/strategy/fleet/test_fleet_validation.py (~141 LOC)

#### CAT-10: Missing required key tests should be parametrized  [MINOR]
- **Location**: test_fleet_validation.py:44-65
- **Issue**: `test_missing_id_raises_persistence_exception` and `test_missing_owner_id_raises_persistence_exception` are identical except the deleted key.
- **Suggestion**: Parametrize into `[(key_to_delete, expected_message_part), ...]`.
- **LOC affected**: 22

---

### tests/integration/strategy/combat/test_flat_shield_bonus.py (~205 LOC)

#### CAT-8: Deep helper nesting for spec construction  [MINOR]
- **Location**: test_flat_shield_bonus.py:55-99
- **Issue**: Four helper functions (`_design_with_shields`, `_team`, `_ship_spec`, `_run`, `_ship_outcome`, `_bonus_entry`, `_mult_entry`) form a deep composition chain. Each test builds a `BattleSpec` through 5-6 layers of helper calls, making it hard to understand the actual test parameters at a glance.
- **Suggestion**: Consider a builder pattern or `@pytest.fixture` that returns pre-configured `BattleSpec` instances with clear parameter overrides.
- **LOC affected**: ~50 (helper functions)

---

### tests/integration/strategy/test_three_empire_battle.py (~152 LOC)

#### CAT-8: test_three_empire_battle_reports_destroyed_fleets has 50 lines of setup for 3 assertions  [MINOR]
- **Location**: test_three_empire_battle.py:127-152
- **Issue**: 25 lines of fleet/empire construction followed by 3 assertions. The helper `_make_fleet` and `_make_empire` could be composed with even shorter syntax.
- **Suggestion**: Add a `_three_empire_setup()` helper that encapsulates the common 3-empire setup pattern used by 3 of 4 tests.
- **LOC affected**: ~30

---

### tests/unit/simulation/combat/test_damage_calculator.py (second pass)

#### CAT-10: TestDamageLayerBoundaryConditions (10 tests) should be parametrized  [MAJOR]
- **Location**: test_damage_calculator.py:606-822
- **Issue**: 10 separate test methods testing damage boundaries (zero damage, exact HP, fractional damage, tiny damage, large overflow, single HP, many components). Each test body is 6-12 lines following the same create-component → apply-damage → assert-HP pattern.
- **Suggestion**: Parametrize into one test with `[(damage, initial_hps_list, expected_hps_list, description), ...]`.
- **LOC affected**: ~200

---

### tests/unit/builder/test_builder_validation.py (~336 LOC)

#### CAT-12: test_exclusive_group has branching assertion logic  [MINOR]
- **Location**: test_builder_validation.py:104-131
- **Issue**: Test uses list comprehensions (`any(c.id == ... for c in ...)`) and `not (has_comp1 and has_comp2)` for assertion — computing search results as part of the assertion rather than with pre-computed expected values.
- **Suggestion**: Pre-compute expected membership boolean before the final assertion.
- **LOC affected**: 5

#### CAT-12: test_mass_validation mutates registries in try/finally  [MINOR]
- **Location**: test_builder_validation.py:158-185
- **Issue**: Test clears and re-populates `self.registries.vehicle_classes` in a try/finally block with explicit cleanup. This is error-prone state mutation within a test.
- **Suggestion**: Use `monkeypatch` or a dedicated fixture that provides a clean registries instance.
- **LOC affected**: 28

---

### tests/unit/data/test_data_validation.py (~292 LOC)

#### CAT-11: test_formation_files_have_professional_names tests regex patterns  [MINOR]
- **Location**: test_data_validation.py:24-48
- **Issue**: Tests that filenames don't match profanity regex patterns. This is a code style / naming convention check, not a functional test. It would be better suited as a pre-commit lint rule.
- **Suggestion**: Move to a pre-commit hook or CI lint step rather than a runtime test.
- **LOC affected**: 25

---

### tests/integration/ui/test_build_queue_drag_drop.py (~361 LOC)

#### CAT-12: test_reorder_queue and test_remove_from_queue have complex event/logic chains  [MAJOR]
- **Location**: test_build_queue_drag_drop.py:265-361
- **Issue**: Both tests manually construct pygame mouse events with `MOUSEBUTTONDOWN`, `MOUSEMOTION` with drag-threshold checks, and `MOUSEBUTTONUP` with position math. The `test_reorder_queue` test is 52 lines of event simulation and position arithmetic to verify a single queue reorder. This is fragile to pygame event handling changes.
- **Suggestion**: Extract a helper `_simulate_drag(from_widget, to_pos)` that handles the mouse-down/motion/up sequence, reducing each test's event plumbing.
- **LOC affected**: ~110

---

### tests/regression/test_caption_schemas_validate.py (~98 LOC)

#### CAT-8/11: test_schema_is_valid_json parametrize iterates only 3 schema names  [MINOR]
- **Location**: test_caption_schemas_validate.py:40-45
- **Issue**: Both `test_schema_is_valid_json` and `test_schema_version_is_1` iterate over a hardcoded 3-element list. If a new schema is added, the test must be updated. `_load` would fail naturally on invalid JSON, and the parametrized version check would miss the new schema.
- **Suggestion**: Auto-discover `.schema.json` files in the schemas directory rather than hardcoding the list.
- **LOC affected**: 6

---

### tests/integration/colonization/test_planet_specific_colonization.py (~695 LOC)

#### CAT-8: Four galaxy fixtures with identical structure  [MINOR]
- **Location**: test_planet_specific_colonization.py:196-244
- **Issue**: `galaxy_with_ice_planet`, `galaxy_with_multiple_planets`, `galaxy_with_three_ice_planets`, `galaxy_with_two_continental_planets` are nearly identical — each creates a `MockGalaxy`, `MockPlanet`(s), `MockSystem`, and returns the galaxy + planets. Only the planet count/type differs.
- **Suggestion**: Use a single factory fixture `def make_galaxy(*planet_specs)`.
- **LOC affected**: ~50

---

### tests/unit/simulation/combat/test_fleet_aura_extended.py (~418 LOC)

#### CAT-8: _make_modifier_stack helper is complex  [MINOR]
- **Location**: test_fleet_aura_extended.py:56-94
- **Issue**: `_make_modifier_stack` is a 40-line helper that creates `ModifierEffect` + `ModifierEntry` + `ModifierStack` through nested factory functions. Used by only 4 tests.
- **Suggestion**: Simplify by providing a direct `_make_stack(team_id, abilities)` helper that constructs the simplest possible ModifierStack for the test scenario.
- **LOC affected**: 40

---

### tests/unit/ui/screens/test_design_selector_window.py (~661 LOC)

#### CAT-1: Five init tests verify attribute assignment only  [MINOR → downgraded: not much LOC]
- **Location**: test_design_selector_window.py:166-208
- **Issue**: Five test methods in `TestDesignSelectorWindowInit` each verify that a single attribute is set on a bypass-init window. These test Python object attribute assignment, not `DesignSelectorWindow` behavior.
- **Suggestion**: Reduce to a single `test_init_sets_initial_state` that asserts all default attributes at once.
- **LOC affected**: 43

---

### tests/unit/strategy/save_game_service/test_error_handling.py (~500 LOC)

#### CAT-12: setup_tmpdir autouse fixtures create temp dirs with patch pattern  [MINOR]
- **Location**: test_error_handling.py:58-66, 107-115, 178-186, 263-270, 314-322, 342-350
- **Issue**: Six test classes each define an autouse `setup_tmpdir` fixture with the same pattern: `tempfile.mkdtemp()`, `os.makedirs`, `patch.object(paths_module.Paths, 'SAVES_DIR', ...)`, `yield`, `shutil.rmtree`. Identical except for context manager framing differences.
- **Suggestion**: Consolidate into a single module-level fixture used by all classes.
- **LOC affected**: ~60 (redundant fixture definitions)

---

### tests/integration/ui/test_battle_setup_three_sides.py (~120 LOC)

No significant issues found. Tests are well-structured, exercise real production paths, and have clear purposes.

---

### tests/unit/strategy/services/test_planet_economy_projector.py (~702 LOC)

No significant issues found. Though large, helpers are well-factored and tests exercise production code paths directly with test-specific stubs that are clearly separable from production code.

---

### tests/unit/strategy/generation/test_system_blueprints.py (~279 LOC)

No significant issues found. Tests verify data file structure and content — data-validity tests that provide legitimate regression protection.

---

### tests/unit/strategy/generation/density/test_density_map.py (~222 LOC)

No significant issues found. Tests exercise real `DensityMap` code paths with clear inputs and assertions.

---

### tests/unit/simulation/systems/test_battle_rng_isolation.py (~126 LOC)

No significant issues found. Tests correctly verify per-instance RNG isolation with clear assertions.

---

### tests/unit/core/test_input_actions.py (~223 LOC)

No significant issues found. Tests verify enum uniqueness, display name coverage, and frozen dataclass behavior — appropriate for a configuration enum.

---

### tests/unit/core/test_error_codes.py (~174 LOC)

No significant issues found. Tests validate error code uniqueness and naming conventions — appropriate regression protection for code enums.

---

### tests/unit/modifiers/test_modifier_loader_v2.py (~209 LOC)

No significant issues found. Tests exercise real Modifier evaluation with formula strings against known values.

---

### tests/unit/entities/test_components.py (~335 LOC)

No significant issues found. Tests exercise real Component instances with production data and verify modifier stacking behavior.

---

### tests/repro_issues/test_bug_12_hull_layer_addition.py (~49 LOC)

No significant issues found. Focused reproduction test with real Ship/Component instances.

---

### tests/unit/simulation/combat/test_beam_hit_tracking.py (~101 LOC)

No significant issues found. Tests use real Ships with mock beams to verify hit/miss tracking behavior.

---

### tests/unit/engine/collision_edge_cases/test_beam_ramming.py (~792 LOC)

No significant issues found. Though large, tests are well-organized and exercise real `CollisionSystem` methods with both mock and real Ship objects.

---

### tests/unit/strategy/fleet_navigation/test_destination_path.py (~330 LOC)

No significant issues found. Tests are well-structured, exercising real `FleetNavigationService` methods with mocked pathfinding dependencies.

---

### tests/unit/simulation/components/abilities/test_fleet_components.py (~275 LOC)

No significant issues found. Tests load real components from production data and verify properties, plus have clean mock-based fleet aura integration tests.

---

### tests/unit/strategy/production_engine/test_tick_consumption.py (~610 LOC)

No significant issues found. Well-structured with clear helper functions and real `ProductionEngine` path exercise.

---

### tests/unit/simulation/combat/test_fleet_aura_cache.py (~88 LOC)

No significant issues found. Clean, focused tests for caching behavior.

---

### tests/unit/strategy/engine/test_game_config.py (~100 LOC)

No significant issues found. Clear validation boundary tests.

---

### tests/unit/strategy/data/test_planet_stockpile.py (~221 LOC)

No significant issues found. Well-structured with real `Planet` instances.

---

### tests/unit/simulation/test_physics_constants.py (~108 LOC)

No significant issues found. Tests verify constants and formula documentation.

---

### tests/unit/strategy/data/test_race_config.py (~465 LOC)

No significant issues found. Well-organized test classes covering construction, serialization, file I/O, validation, and preference fields.

---

### tests/unit/strategy/data/test_planet_species_configs.py (~137 LOC)

No significant issues found. Clean tests with minimal helper.

---

### tests/unit/strategy/data/test_facility_construction_queue.py (~199 LOC)

No significant issues found. Clean serialization round-trip tests.

---

### tests/unit/strategy/services/test_planet_economy_projector.py (~702 LOC)

No significant issues found. Well-structured with thorough coverage of net arithmetic, habitability scaling, and edge cases.

---

### tests/unit/strategy/data/test_planet_classification_logic.py (~114 LOC)

No significant issues found. Parametrized `test_classification_logic` is an excellent example.

---

### tests/unit/simulation/test_battle_spec.py (~275 LOC)

No significant issues found. Tests verify frozen dataclass structure and round-trip behavior.

---

### tests/unit/core/registry/test_singleton_and_thread.py (~243 LOC)

No significant issues found. Tests verify instance management and thread safety patterns.

---

### tests/unit/simulation/ship_combat_engine/test_combat_ops.py (~27 LOC)

No significant issues found. Brief but exercises real `ShipCombatEngine` with real ships.

---

### tests/unit/builder/test_ship_loading.py (~131 LOC)

No significant issues found. Tests exercise real Ship deserialization with modifier verification.

---

### tests/unit/simulation/test_component_decoupling.py (~233 LOC)

No significant issues found. Tests exercise real Component instances with context injection.

---

### tests/unit/ui/screens/test_planet_production_display.py (~153 LOC)

No significant issues found. Tests exercise real `compute_planet_production` with both inline and registry-based component lookups.

---

### tests/unit/simulation/components/abilities/test_combat_modifiers.py (~236 LOC)

No significant issues found. Well-structured tests for strategic-layer abilities.

---

### tests/unit/modifiers/test_ability_stat_binding.py (~183 LOC)

No significant issues found. Clean tests for `AbilityStatBinding` dataclass with mock abilities.

---

### tests/unit/fixtures/test_strategy_entities.py (~354 LOC)

No significant issues found. Tests verify test fixtures produce valid, round-trippable objects.

---

### tests/unit/validation/test_component_definitions.py (~107 LOC)

No significant issues found. Data-driven parametrized tests validating components.json structure.

---

### tests/unit/ai/test_ai_controller_interface.py (~327 LOC)

No significant issues found. Tests exercise real `AIController` with `ShipControllableAdapter`, including the self-skip avoidance fix.

---

### tests/unit/simulation/interfaces/test_ai_controller_interface.py (~101 LOC)

No significant issues found. Protocol compliance tests with structural checks.

---

### tests/unit/ui/screens/test_fleet_orders_refresh.py (~178 LOC)

No significant issues found. Tests exercise real `OrdersWindow` with proper fixture setup.

---

### tests/unit/ui/screens/test_strategy_input_handler_transfer.py (~278 LOC)

No significant issues found. Clean tests for keyboard input mode transitions.

---

### tests/unit/ui/services/image/test_defaults.py (~27 LOC)

No significant issues found. Brief module-level singleton tests.

---

### tests/unit/modifiers/test_modifier_introspection.py (~342 LOC)

No significant issues found. Tests exercise `ModifierIntrospection` with real production components.

---

### tests/unit/modifiers/test_weapon_ability_bindings.py (~289 LOC)

No significant issues found. Tests verify `WeaponAbility.STAT_BINDINGS` declarations and recalculate behavior.

---

### tests/integration/save_load/test_reference_integrity.py (~201 LOC)

No significant issues found. Tests verify cross-object reference resolution after save/load.

---

### tests/integration/strategy/facade/test_fleet_queries.py (~318 LOC)

No significant issues found. Clean facade query tests with DTO verification.

---

### tests/integration/strategy/test_star_generation.py (~157 LOC)

No significant issues found. Tests exercise real `StarGenerator` and `Star` objects.

---

### tests/integration/strategy/test_treasury_panel_e2e.py (~199 LOC)

No significant issues found. End-to-end test verifying calculator → snapshot → panel row consistency.

---

### tests/integration/test_complex_workflow.py (~425 LOC)

No significant issues found. Workflow tests exercising Design → Queue → Build → Facility lifecycle.

---

### tests/unit/strategy/interfaces/test_battle_resolver_replay_id.py (~20 LOC)

No significant issues found. Simple round-trip test.

---

### tests/unit/simulation/components/abilities/test_planet_modifiers.py (~202 LOC)

No significant issues found. Clean ability construction tests.

---

### tests/repro_issues/test_slider_increment.py (~102 LOC)

No significant issues found. Tests `ModifierControlRow` slider creation directly.

---

### tests/unit/strategy/fleet/test_fleet_validation.py (~141 LOC)

No significant issues found. Tests Fleet.from_dict validation errors.

---

### tests/unit/strategy/data/test_planet_stockpile.py (~221 LOC)

No significant issues found.

---

### tests/integration/save_load/test_full_roundtrip.py (~225 LOC)

No significant issues found.

---

### tests/integration/ui/test_design_selector.py (~89 LOC)

No significant issues found beyond the one CAT-11 note above.

---

### tests/unit/simulation/systems/test_exit_policy.py (~143 LOC)

No significant issues found.

---

### tests/unit/strategy/engine/test_fleet_transfer_extended.py (~250 LOC)

No significant issues found beyond the parametrization opportunity noted above.

---

### tests/unit/simulation/combat/test_weapon_summary_aggregator.py (~191 LOC)

No significant issues found. Clean fake-object tests for the aggregator.

---

### tests/unit/performance/test_profiler_perf.py (~181 LOC)

No significant issues found. Tests exercise real Profiler with expected timing behavior.

---

## File Coverage Verification

| File | Status | Findings |
|------|--------|----------|
| tests/unit/builder/test_builder_warning_logic.py | Read ✓ | 0 |
| tests/repro_issues/test_bug_12_hull_layer_addition.py | Read ✓ | 0 |
| tests/unit/ui/services/test_validation_service.py | Read ✓ | 1 |
| tests/unit/ui/test_race_summary_panel.py | Read ✓ | 4 |
| tests/unit/ui/components/table/test_virtual_table.py | Read ✓ | 3 |
| tests/integration/strategy/test_star_generation.py | Read ✓ | 0 |
| tests/integration/strategy/facade/test_fleet_queries.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_radiation_physics.py | Read ✓ | 0 |
| tests/integration/strategy/test_treasury_panel_e2e.py | Read ✓ | 0 |
| tests/unit/ai/test_controllable_adapter.py | Read ✓ | 1 |
| tests/unit/ui/test_battle_panels_extended.py | Read ✓ | 4 |
| tests/unit/strategy/interfaces/test_battle_resolver_replay_id.py | Read ✓ | 0 |
| tests/unit/strategy/engine/test_planetary_yard_requirement.py | Read ✓ | 1 |
| tests/unit/simulation/systems/test_ship_stats_calculator_phases.py | Read ✓ | 1 |
| tests/unit/simulation/components/abilities/test_fleet_components.py | Read ✓ | 0 |
| tests/unit/ui/panels/test_ship_stats_renderer.py | Read ✓ | 3 |
| tests/unit/strategy/production_engine/test_tick_consumption.py | Read ✓ | 0 |
| tests/unit/modifiers/test_pipeline_unification.py | Read ✓ | 1 |
| tests/unit/quickstart/test_quickstart_races.py | Read ✓ | 1 |
| tests/unit/strategy/generation/density/test_density_map.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_beam_hit_tracking.py | Read ✓ | 0 |
| tests/unit/engine/collision_edge_cases/test_beam_ramming.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_planet_stockpile.py | Read ✓ | 0 |
| tests/integration/save_load/test_full_roundtrip.py | Read ✓ | 1 |
| tests/unit/strategy/fleet_navigation/test_destination_path.py | Read ✓ | 0 |
| tests/integration/save_load/test_reference_integrity.py | Read ✓ | 0 |
| tests/unit/modifiers/test_modifier_loader_v2.py | Read ✓ | 0 |
| tests/integration/ui/test_colonization_facade.py | Read ✓ | 3 |
| tests/unit/modifiers/test_weapon_ability_bindings.py | Read ✓ | 0 |
| tests/unit/validation/test_component_definitions.py | Read ✓ | 0 |
| tests/integration/ui/test_design_selector.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_commands.py | Read ✓ | 2 |
| tests/unit/fixtures/test_strategy_entities.py | Read ✓ | 0 |
| tests/unit/modifiers/test_ability_stat_binding.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_fleet_aura_cache.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_planet_species_configs.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_facility_construction_queue.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_drag_drop_real.py | Read ✓ | 1 |
| tests/unit/ui/panels/test_build_queue_portraits.py | Read ✓ | 0 |
| tests/unit/strategy/generation/test_system_blueprints.py | Read ✓ | 0 |
| tests/unit/ui/screens/builder/test_modifier_control_row.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_design_selector_window.py | Read ✓ | 1 |
| tests/unit/strategy/data/test_race_config.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_fleet_report_sidebar.py | Read ✓ | 0 |
| tests/integration/strategy/combat/test_flat_shield_bonus.py | Read ✓ | 1 |
| tests/unit/strategy/engine/test_fleet_transfer_extended.py | Read ✓ | 1 |
| tests/integration/test_complex_workflow.py | Read ✓ | 0 |
| tests/unit/strategy/save_game_service/test_error_handling.py | Read ✓ | 1 |
| tests/unit/ui/services/image/test_defaults.py | Read ✓ | 0 |
| tests/unit/modifiers/test_modifier_introspection.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_planet_modifiers.py | Read ✓ | 0 |
| tests/unit/simulation/combat/test_damage_calculator.py | Read ✓ | 3 |
| tests/unit/strategy/engine/test_game_config.py | Read ✓ | 0 |
| tests/unit/builder/test_ship_loading.py | Read ✓ | 0 |
| tests/unit/simulation/ship_combat_engine/test_combat_ops.py | Read ✓ | 0 |
| tests/unit/builder/test_builder_validation.py | Read ✓ | 2 |
| tests/unit/simulation/combat/test_fleet_aura_extended.py | Read ✓ | 1 |
| tests/unit/simulation/combat/test_weapon_summary_aggregator.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_strategy_input_handler_transfer.py | Read ✓ | 0 |
| tests/regression/test_caption_schemas_validate.py | Read ✓ | 1 |
| tests/unit/core/test_input_actions.py | Read ✓ | 0 |
| tests/unit/simulation/systems/test_battle_rng_isolation.py | Read ✓ | 0 |
| tests/repro_issues/test_slider_increment.py | Read ✓ | 0 |
| tests/unit/modifiers/test_beam_weapon_bindings.py | Read ✓ | 1 |
| tests/unit/strategy/fleet/test_fleet_validation.py | Read ✓ | 1 |
| tests/unit/simulation/test_physics_constants.py | Read ✓ | 0 |
| tests/unit/strategy/services/test_planet_economy_projector.py | Read ✓ | 0 |
| tests/unit/strategy/test_fleet_orders_logic.py | Read ✓ | 0 |
| tests/unit/test_lab/test_testruncard_propulsion.py | Read ✓ | 2 |
| tests/unit/strategy/engine/test_fleet_order_transfer.py | Read ✓ | 0 |
| tests/unit/performance/test_profiler_perf.py | Read ✓ | 0 |
| tests/unit/simulation/components/abilities/test_combat_modifiers.py | Read ✓ | 0 |
| tests/unit/simulation/test_component_decoupling.py | Read ✓ | 1 |
| tests/unit/ui/screens/test_planet_production_display.py | Read ✓ | 0 |
| tests/integration/ui/test_build_queue_drag_drop.py | Read ✓ | 1 |
| tests/unit/simulation/systems/test_exit_policy.py | Read ✓ | 1 |
| tests/integration/colonization/test_planet_specific_colonization.py | Read ✓ | 1 |
| tests/unit/simulation/interfaces/test_ai_controller_interface.py | Read ✓ | 0 |
| tests/unit/entities/test_components.py | Read ✓ | 0 |
| tests/unit/core/test_error_codes.py | Read ✓ | 0 |
| tests/unit/data/test_data_validation.py | Read ✓ | 1 |
| tests/integration/ui/test_battle_setup_three_sides.py | Read ✓ | 0 |
| tests/unit/ui/screens/test_fleet_orders_refresh.py | Read ✓ | 0 |
| tests/unit/ai/test_ai_controller_interface.py | Read ✓ | 0 |
| tests/unit/strategy/data/test_planet_classification_logic.py | Read ✓ | 0 |
| tests/integration/strategy/test_three_empire_battle.py | Read ✓ | 1 |
| tests/unit/simulation/test_battle_spec.py | Read ✓ | 0 |
| tests/unit/core/registry/test_singleton_and_thread.py | Read ✓ | 0 |

## Context Usage Estimate
- Total LOC read (test files + production code): ~30,000
- Approximate headroom: High (>500K remaining)
