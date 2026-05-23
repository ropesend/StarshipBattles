# Phase 3: CAT-10 Parametrize

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-480 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Parametrize ~55 verified CAT-10 structurally-identical clusters from review `2026-05-20_210550_test-review`. Each cluster has ≥3 members that differ only in input/output pairs — textbook `@pytest.mark.parametrize` candidates. Clusters with <3 members were rejected during verification; clusters where members exercise different pipeline stages were rejected (e.g., S06-F005 superweapon per-weapon classes). Reclaim ~1,200 LOC of repetition.

---

## Tasks

### Task 3.1: test_build_queue_helpers.py — 6+7 same-pattern tests
**File:** `tests/unit/ui/screens/test_build_queue_helpers.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_helpers.py`

- [ ] Parametrize the 6 `format_empire_resources` tests at lines 42-115 and the 7 `format_resource_cost` tests at lines 118-181.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.2: test_fleet_report_window_multi_select.py — 3 null-guard tests
**File:** `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

- [ ] Parametrize the 3 null-guard tests (lines 241-265).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.3: test_deprecated_code_removed.py — 4+4 deletion guards
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py`

- [ ] Parametrize the 4 identical hasattr-deletion-guard tests at lines 12-34 and the 4 more at lines 45-67.
- [ ] Verify: passes; LOC delta ≈ -30.

### Task 3.4: test_event_bus.py — 3 ValidationException tests
**File:** `tests/unit/systems/test_event_bus.py`
**Tests:** `pytest tests/unit/systems/test_event_bus.py`

- [ ] Parametrize the 3 identical ValidationException tests (lines 43-65).
- [ ] Verify: passes; LOC delta ≈ -12.

### Task 3.5: test_pipeline_unification.py — 6 ability-class tests (NEEDS_REWORK)
**File:** `tests/unit/modifiers/test_pipeline_unification.py`
**Tests:** `pytest tests/unit/modifiers/test_pipeline_unification.py`

- [ ] _(NEEDS_REWORK: keep separate — verification found each test exercises a distinct ability class through unique production path; parametrize would obscure semantic coverage boundaries. See verification_report.md.)_
- [ ] No action — document the semantic distinctness in a comment per the verification adjusted suggestion.

### Task 3.6: test_engine_event_emission.py — 9 event-emission tests
**File:** `tests/unit/strategy/test_engine_event_emission.py`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py`

- [ ] Parametrize the 9 event-emission tests across 3 classes (4 spawn_ship variants + 2 fleet variants + 3 complex variants, lines 108-339) on `(spawn_method, input_params, expected_event_kwargs)`.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.7: test_squadron_characterization.py — 5 roundtrip tests
**File:** `tests/unit/strategy/data/test_squadron_characterization.py`
**Tests:** `pytest tests/unit/strategy/data/test_squadron_characterization.py`

- [ ] Parametrize the 5 `test_round_trip_*` methods (lines 113-172) on `(squadron_kwargs, assert_fn)`.
- [ ] Verify: passes; LOC delta ≈ -45.

### Task 3.8: test_ship_physics.py — 4 heading/velocity tests
**File:** `tests/unit/simulation/entities/test_ship_physics.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_physics.py`

- [ ] Parametrize the 4 velocity-by-angle tests (lines 344-387) on `(angle, expected_x, expected_y)`.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.9: test_cooldowns.py — 5 shield regen tests
**File:** `tests/unit/simulation/ship_combat_engine/test_cooldowns.py`
**Tests:** `pytest tests/unit/simulation/ship_combat_engine/test_cooldowns.py`

- [ ] Parametrize the 5 shield-regen tests (lines 58-140) on `(initial_shields, max, regen_rate, ticks, expected_shields)`.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 3.10: test_formula_exceptions.py — 7 repeated FormulaEvaluator imports
**File:** `tests/unit/simulation/test_formula_exceptions.py`
**Tests:** `pytest tests/unit/simulation/test_formula_exceptions.py`

- [ ] Add module-level `from game.core.formula_evaluator import FormulaEvaluator`; remove the 7 in-method imports (lines 15, 25, 35, 44, 54, 65, 75).
- [ ] Verify: passes; LOC delta ≈ -7.

### Task 3.11: test_invalid_operation_handling.py — 4 multiply/add/set/add_to_mult bodies
**File:** `tests/unit/modifiers/test_invalid_operation_handling.py`
**Tests:** `pytest tests/unit/modifiers/test_invalid_operation_handling.py`

- [ ] Parametrize the 4 identical bodies (lines 77-103) on operation type.
- [ ] Verify: passes; LOC delta ≈ -18.

### Task 3.12: test_system_selection_window.py — 2 cancel/confirm tests
**File:** `tests/unit/ui/screens/test_system_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_system_selection_window.py`

- [ ] Parametrize the 2 cancel/confirm tests with identical setup (lines 12-232).
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.13: test_planet_menu_items.py — 5+ TestPlanetMenuCapabilityMatrix tests
**File:** `tests/unit/ui/screens/test_planet_menu_items.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_menu_items.py`

- [ ] Parametrize 5+ TestPlanetMenuCapabilityMatrix tests (lines 136-198).
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 3.14: test_fleet_menu_items.py — 10+ FMS row tests
**File:** `tests/unit/ui/screens/test_fleet_menu_items.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_menu_items.py`

- [ ] Parametrize the 10+ FMS row tests (lines 400-572) on `(ability, label, condition)`.
- [ ] Verify: passes; LOC delta ≈ -150.

### Task 3.15: test_strategy_input_handler_core.py — 4 escape-returns-to-select tests
**File:** `tests/unit/ui/screens/test_strategy_input_handler_core.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py`

- [ ] Parametrize the 4 escape-returns-to-select tests on `mode` ∈ ["MOVE", "JOIN", "COLONIZE_TARGET", "TRANSFER"] (lines 128-169).
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.16: test_empire_build_queue_window.py — duplicate method name
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Parametrize `test_toggle_column_hides_visible_column` (lines 644-663, 2 defs — first is shadowed by second per Python rules) on `column_id` ∈ ["location", "build_rate"]; rename to `test_toggle_column_hides_any_column`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 3.17: test_ship_fleet_attrs.py — 2 test pairs
**File:** `tests/unit/simulation/entities/test_ship_fleet_attrs.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_fleet_attrs.py`

- [ ] Parametrize the 2 test pairs (lines 16-56) on `(attr_name, expected_value)`.
- [ ] Verify: passes; LOC delta ≈ -18.

### Task 3.18: test_destination_path.py — 3 NavigationState tests
**File:** `tests/unit/strategy/fleet_navigation/test_destination_path.py`
**Tests:** `pytest tests/unit/strategy/fleet_navigation/test_destination_path.py`

- [ ] Extract NavigationState construction (3 identical-except-orders setups, lines 19-78) into a parametrized fixture.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.19: test_design_selector_window.py — 3 ID-sanitization tests
**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py`

- [ ] Extract `_assert_design_row_with_id(design_id, forbidden_chars)` helper for the 3 ID-sanitization tests (lines 482-498, 500-523, 525-546).
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.20: test_superweapon_order_pop_matrix.py — 10 weapon tests (NEEDS_REWORK)
**File:** `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py`

- [ ] _(NEEDS_REWORK: keep separate — verification found per-weapon Order target structures, galaxy scaffolding, and Stellerate's fleet-consumption assertion differ substantially. Document the deliberate per-weapon class organization.)_
- [ ] No action — add a comment explaining the per-weapon class structure is intentional.

### Task 3.21: test_strategy_input_handler_hotkeys.py — 3 hotkey clusters
**File:** `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py`

- [ ] Parametrize the M/J/C/T mode-activation cluster (4 tests, lines 70-101).
- [ ] Parametrize the 4 zoom tests (lines 181-208) on `(key, modifiers, camera_method)`.
- [ ] Parametrize the action tests (lines 214-317, ~14 tests) into 2 sub-clusters: simple-action + fleet-dependent.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.22: test_planet_abilities_controller_scanner.py — 2 instance_label tests
**File:** `tests/unit/ui/screens/test_planet_abilities_controller_scanner.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_abilities_controller_scanner.py`

- [ ] Parametrize the 2 instance_label tests (lines 121-153).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.23: test_setup_screen.py — 3 handle_event/update/draw hasattr tests
**File:** `tests/unit/ui/screens/test_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_setup_screen.py`

- [ ] Parametrize the 3 hasattr+callable tests (lines 389-408) on method name.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.24: test_production_engine_queue.py — 2 resources_consumed tests
**File:** `tests/unit/strategy/engine/test_production_engine_queue.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_queue.py`

- [ ] Parametrize the 2 tests (colony+fleet, lines 125-259) asserting `item["resources_consumed"]["A"] == 0.0` — note setup differs nontrivially; document.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.25: test_planet_energy_engine.py — 4 generator/cap/no-gen/shield-drain
**File:** `tests/unit/strategy/engine/test_planet_energy_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_energy_engine.py`

- [ ] Parametrize the 4 tests at lines 211-269.
- [ ] Verify: passes; LOC delta ≈ -40.

### Task 3.26: test_ship_io.py — 7 round-trip tests
**File:** `tests/unit/ui/services/test_ship_io.py`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [ ] _(coordination note: addressed via DUP-003 in PROJ-479 Phase 5 Task 5.3. After that, parametrize remaining IO-specific properties locally; lines 395-541.)_
- [ ] Verify: passes; LOC delta ≈ -75.

### Task 3.27: test_fleet_dto.py — 2 immutable-tuple tests
**File:** `tests/unit/strategy/facade/test_fleet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/test_fleet_dto.py`

- [ ] Merge the 2 tests (lines 192-269) into one parametrized test covering both construction sources.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.28: test_ship_serialization.py — 5 roundtrip tests
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`

- [ ] Parametrize the 5 roundtrip tests (lines 328-419) on field name. _(coordination note: tied to DUP-003 cross-shard in PROJ-479 Phase 5; do P1's narrowed plan first.)_
- [ ] Verify: passes; LOC delta ≈ -35.

### Task 3.29: test_turn_engine_lazy_properties.py — 18 isinstance tests
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [ ] Parametrize the 18 isinstance + identity test methods (lines 34-178) on engine class.
- [ ] Verify: passes; LOC delta ≈ -130.

### Task 3.30: test_fleet_report_filters.py — warp filter + sort cluster
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [ ] Parametrize the 3 warp filter tests (lines 388-448) and 8+ sort tests (lines 451-628).
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.31: test_deterministic_generation.py — 4 deterministic-gen tests
**File:** `tests/integration/strategy/test_deterministic_generation.py`
**Tests:** `pytest tests/integration/strategy/test_deterministic_generation.py`

- [ ] Parametrize the 4 tests (lines 18-127) on `(galaxy_type, seed, system_count, attribute_getter)`.
- [ ] Verify: passes; LOC delta ≈ -70.

### Task 3.32: test_event_log_data_source.py — 4 category-icon tests
**File:** `tests/unit/ui/screens/test_event_log_data_source.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_data_source.py`

- [ ] Parametrize the 4 category-icon tests (lines 100-118) on `(category, icon_token)`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.33: test_portraits.py — 4 get_ship_class_color tests
**File:** `tests/unit/ui/utils/test_portraits.py`
**Tests:** `pytest tests/unit/ui/utils/test_portraits.py`

- [ ] Parametrize the 4 tests at lines 18-28 on `(class_name, expected)`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 3.34: test_battle_results_screen.py — 6 _hp_color tests
**File:** `tests/unit/ui/screens/test_battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py`

- [ ] Parametrize the 6 _hp_color tests (lines 21-43) on `(hp, expected_color)`.
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.35: test_fleet_pursuer_tracker.py — 3 setup-shared tests
**File:** `tests/unit/strategy/services/test_fleet_pursuer_tracker.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_pursuer_tracker.py`

- [ ] Parametrize the 3 tests (lines 387-445) — same setup, assertion target varies.
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.36: test_battle_screen_simulation.py — 3 clusters
**File:** `tests/unit/ui/screens/test_battle_screen_simulation.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_screen_simulation.py`

- [ ] Parametrize the 4 speed-multiplier-key tests (lines 262-320).
- [ ] Parametrize the 3 battle-over tests (lines 175-222).
- [ ] Parametrize the 3 input-handler tests (lines 444-492).
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 3.37: test_research_renderer.py — 10 + 7 visibility/margin tests
**File:** `tests/unit/ui/screens/test_research_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_research_renderer.py`

- [ ] Parametrize the 10 visibility tests (lines 112-169) on `(pos, expected)`.
- [ ] Parametrize the 7 margin tests (lines 173-238) on `(pos, margin, expected)`.
- [ ] Verify: passes; LOC delta ≈ -100.

### Task 3.38: test_new_game_setup_controller.py — 2 callback tests
**File:** `tests/unit/ui/screens/test_new_game_setup_controller.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_controller.py`

- [ ] Parametrize the 2 tests (lines 174-196) on `(callback_method, player_index, needs_modal_setup)`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.39: test_warp_resources.py — 3 warp_resource_costs tests
**File:** `tests/unit/strategy/fleet/test_warp_resources.py`
**Tests:** `pytest tests/unit/strategy/fleet/test_warp_resources.py`

- [ ] Parametrize the 3 warp_resource_costs tests (lines 41-71) on `(ship_config, expected_costs)`.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.40: test_naming.py — 16 to_roman tests
**File:** `tests/unit/strategy/utility/test_naming.py`
**Tests:** `pytest tests/unit/strategy/utility/test_naming.py`

- [ ] Parametrize the 16 test_one..test_thousand methods (lines 207-269) on `(num, roman)`.
- [ ] Verify: passes; LOC delta ≈ -50.

### Task 3.41: test_event_log_sidebar.py — 4 attribute tests
**File:** `tests/unit/ui/screens/test_event_log_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_sidebar.py`

- [ ] Parametrize the 4 byte-identical-except-attr-name tests (lines 83-103).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.42: test_superweapon_order_processor_gaps.py — 5 TestStabilizerCancellation tests
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py`

- [ ] Parametrize the 5 tests (lines 118-272) on `(processor_method, expected_order_type, target_setup)`.
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 3.43: test_hit_effects.py — 3 early-return tests
**File:** `tests/unit/ui/effects/test_hit_effects.py`
**Tests:** `pytest tests/unit/ui/effects/test_hit_effects.py`

- [ ] _(verification: VERIFIED but test names document branches and serve a discovery purpose — keep structure. No action; retained for traceability.)_

### Task 3.44: test_tick_phases.py — 3 registry read tests
**File:** `tests/unit/simulation/systems/test_tick_phases.py`
**Tests:** `pytest tests/unit/simulation/systems/test_tick_phases.py`

- [ ] Parametrize the 3 structurally identical registry read tests (lines 74-124).
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 3.45: test_empire_treasury_panel.py — 4 _format_value tests
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] Parametrize the 4 _format_value tests (lines 235-284) on `(input_value, expected_output)`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 3.46: test_superweapon_command_handlers.py — 5 handler test cluster
**File:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_command_handlers.py`

- [ ] Parametrize the 5 handler-class `test_execute_adds_correct_order_type` tests (lines 163-331) on `(handler_cls, expected_order_type, expected_target_shape)`.
- [ ] Verify: passes; LOC delta ≈ -60.

### Task 3.47: test_superweapon_validator.py — 5 validator-class clusters
**File:** `tests/unit/strategy/validation/test_superweapon_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/test_superweapon_validator.py`

- [ ] Parametrize the 5 validator-class valid/invalid-no-ability/invalid-bad-location patterns (lines 228-651) on `(validator_method, setup_func, valid_assertion, invalid_assertions)`.
- [ ] Verify: passes; LOC delta ≈ -150.

### Task 3.48: test_empire_validation.py — 3 missing-field tests
**File:** `tests/unit/strategy/empire/test_empire_validation.py`
**Tests:** `pytest tests/unit/strategy/empire/test_empire_validation.py`

- [ ] Parametrize the 3 missing-field PersistenceException tests (lines 41-72) on `missing_key`.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 3.49: test_base_command_handler.py — 2 resolve_fleet tests
**File:** `tests/unit/strategy/engine/test_base_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_base_command_handler.py`

- [ ] Parametrize the 2 tests (lines 18-43) on `(fleet_setup_func, expected_error_substring)`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 3.50: test_superweapons.py — 10 .keys() parametrize matrix
**File:** `tests/unit/strategy/engine/test_superweapons.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapons.py`

- [ ] No restructure needed — already parametrized; just ensure inconsistency at line 113 (Task 1.26 of Phase 1) is resolved.
- [ ] Verify: passes; LOC delta 0.

### Task 3.51: test_boundary.py — protocol-conformance check
**File:** `tests/unit/strategy/regions/test_boundary.py`
**Tests:** `pytest tests/unit/strategy/regions/test_boundary.py`

- [ ] _(verification: OUT_OF_SCOPE intentional_smoke_test — well-suited protocol-conformance check. No action; retained for traceability.)_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4 — CAT-11 Fragile Assertion)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
