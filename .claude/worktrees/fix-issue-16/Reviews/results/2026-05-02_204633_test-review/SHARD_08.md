# Shard 08 — Test Suite Audit Report

**Reviewer**: Shard 08 Reviewer  
**Files**: 89 files, ~23,566 LOC  
**Date**: 2026-05-02

---

## CRITICAL

### CAT-1: Trivial Pass — Cannot Fail if Imports Succeed

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/ui/screens/test_strategy_menu_panel.py` | 43–79 | 7 tests verify module-level constants (`BUTTON_COUNT == 6`, `len(MENU_BUTTONS) == 6`, exact label lists). These constants are defined in the same module being tested — the test can only fail if someone edits both the constant definitions and the tests simultaneously. |
| `test_unit/strategy/data/test_superweapon_orders.py` | 28–56 | 6 `test_*_order_type_exists` tests that only call `hasattr(OrderType, ...)` and `isinstance(...)`. All pass trivially as long as the enum values are not deleted. |
| `test_unit/strategy/facade/test_strategy_session_facade_public_api.py` | 122–154 | `test_every_public_method_present` + `test_every_public_method_callable` + `test_no_unexpected_public_methods_added` — runtime introspection that can only fail during a deliberate refactor. These are contract/snapshot guards; useful but trivially-passing in normal run. |
| `test_unit/core/test_simulation_constants.py` | 12–21 | `test_constants_exist` — 5 `hasattr` checks. Cannot fail if constants module is importable. |
| `test_unit/ui/screens/test_empire_build_queue_viewmodel.py` | 69–82 | 3 `TestBuildQueueWindowEvents` tests check `hasattr` + truthiness of event string constants. Trivially true. |
| `test_unit/strategy/data/test_fleet_display_name.py` | 129 | `test_two_empires_have_independent_display_numbers` — both empires start at 1, trivial assertion. |

**Downgrade note**: These are contract/presence guards. Blast radius small. Worth keeping as regression smoke but counted as CAT-1.

---

### CAT-2: Tests Nothing Real — No game.* imports, All Mocked/Reimplemented

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/strategy/facade/test_facade_indices.py` | 12–74 | 3 tests, every object (session, planet, system, galaxy, facade) is `MagicMock()`. No real game objects exercised. Tests that `_get_planet_by_id` returns a MagicMock planet and that caching works — purely mock-circuit verification. |
| `test_unit/ui/components/table/test_selection.py` | 6–224 | Entire file tests `SingleSelect`, `MultiSelect`, `NoSelect` strategies — pure in-memory set operations with zero game dependencies. Strong unit test of reusable component; CAT-2 by strict rubric. |
| `test_unit/ai/test_controllable_adapter_edge_cases.py` | 54–365 | Every ship, behavior, etc. is a MagicMock. Tests adapter delegation pattern — `adapter.get_rotation()` returns `mock_ship.angle`. Verifying mock wiring, not game behavior. |

**Downgrade note**: Each tests a real, isolated component (selection strategies, adapter, index caching). Not "dead weight" — just fully mocked. Small blast radius.

---

### CAT-3: Dead Test Code — Removed Functionality, Unused Helpers, Standalone Repros Covered Elsewhere

| File | Lines | Issue |
|------|-------|-------|
| `test_repro_issues/test_bug_12_energy_gen.py` | 32–109 | BUG-12 reproduction. File header states: "WORKING AS DESIGNED - not a code bug." Tests demonstrate expected behavior (generator inactive without crew). Useful as regression guard but classified as CAT-3 — it's a repro for a closed/non-bug, not testing current production code paths. |
| `test_unit/ai/test_controllable_adapter_edge_cases.py` | 339–365 | `TestAttributeDelegationRemoved` — explicitly tests that `__getattr__/__setattr__` delegation was REMOVED (PROJ-24). Tests what is NOT there rather than what is. Regression guard for intentional deletion. |

**Downgrade note**: Both are regression guards with code-movement value. Blast radius small.

---

## MAJOR

### CAT-4: Duplicate Testing

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/simulation/systems/test_battle_engine_end_conditions.py` | 245–287 | `TestExistingModesUnchanged` — `test_tick_limit_condition_works`, `test_team_eliminated_condition_works`, `test_team_incapacitated_condition_works`, `test_never_condition_below_ceiling`. These 4 tests duplicate coverage already provided by existing unit tests for `TickLimitCondition`, `TeamEliminatedCondition`, etc. The "unchanged" assertion is already covered by the individual condition test files. |
| `test_unit/strategy/events/test_event_validation.py` | 26–69 | 5 tests (`test_missing_*_raises_persistence_exception`) share identical structure — delete a key, assert PersistenceException with field name in message. Differ only in field name. |
| `test_unit/simulation/test_battle_state_validation.py` | 39–101 | Similarly, `TestComponentStateValidation` has 6 nearly-identical `test_missing_*_raises_persistence_exception` tests. Identical structure per field. |
| `test_unit/strategy/data/test_colony_species_config.py` | 76–118 | `TestLastFoodRatioAggregation` — 5 tests that set `last_consumption_ratios` and check `last_food_ratio` are conceptually duplicating property behavior testing. Each narrow domain slice but 5 tests with identical pattern. |

---

### CAT-5: Fixture Bloat — Function-Scoped Expensive Fixtures Used 10+ Times

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/simulation/components/test_component_resource_manager.py` | 23–52 | `mock_component` fixture + `mock_resource_consumption_ability` + `mock_constant_consumption_ability` — 3 function-scoped fixtures, each creating MagicMock trees. Used across 9 test classes (~24 test methods). |
| `test_unit/strategy/engine/test_resupply_engine.py` | 20–101 | 6 helper functions (`_make_mock_registries`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_empire`, `_make_mock_ship`, `_make_mock_fleet`, `_make_mock_galaxy`, `_make_planet_with_fuel`) — each creates multi-level mock trees. `_make_mock_ship` builds closures with nonlocal-like mutable state (`_fuel_state` dict). |
| `test_unit/ui/screens/test_fleet_report_filters.py` | 12–75 | `make_mock_ship` helper builds 70+ line MagicMock trees with nested design_data, consumable_levels, get_calculated_stats side effects. Called ~80+ times across 15 test classes. |

---

### CAT-6: Mocking Brittleness — Patching _private, Assert on `call_args_list`

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/engine/collision_edge_cases/test_ccd.py` | 23–376 | Every test constructs MagicMock projectiles with ~15 attributes each (`position`, `velocity`, `radius`, `damage`, `is_alive`, `team_id`, `type`, `source_weapon`, `distance_traveled`, `target`, `status`). ProjectileManager.update() internals must exactly consume these attribute names. Any refactor of projectile attributes breaks all tests silently or noisily. |
| `test_unit/strategy/fleet_movement_engine/test_basics.py` | 77–108 | `test_recalculates_path_if_destination_changed` and `test_move_order_to_destination` patch `fleet_navigation_service.find_hybrid_path` — a deep internal of the engine. |
| `test_unit/ui/screens/test_new_game_setup_extended.py` | 16–49 | `_make_screen()` patches `__init__` with `lambda self, *a, **kw: None`, then manually populates 16+ attributes. Tight coupling to `NewGameSetupScreen.__init__` attribute list. |
| `test_unit/ui/screens/test_strategy_modal_window.py` | 16–37 | `_make_modal_window` patches `pygame_gui.elements.UIWindow.__init__` with lambda, then manually calls base class `__init__`. Fragile to changes in either UIWindow or StrategyModalWindow init signatures. |

---

### CAT-7: Sleep/Latency — `time.sleep`, Delay, Wait (not `get_ticks`/`clock.tick`)

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/strategy/test_auto_save.py` | 124 | `time.sleep(0.01)` — waits for mtime to differ. Legitimate but slows test. |
| `test_unit/strategy/services/test_race_description_llm_controller.py` | 135, 139, 325, 343 | 4 uses of `time.sleep(0.02)` in tests for async cancel/blocking behavior. ~80ms total sleep, and a `_wait_until` spin-loop helper at line 133-140 using `time.sleep(0.01)`. Headless LLM controller tests with real threading — unavoidable but slows suite. |
| `test_unit/strategy/services/test_race_description_llm_controller.py` | 82–91 | `_BlockingProvider.complete` spins in a `while time.monotonic() < end` loop with `time.sleep(0.005)`. Tests may take up to 5 seconds. |

---

## MINOR

### CAT-8: Needless Complexity — 5+ Nested Patches, Setup >50%

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/ui/screens/test_setup_screen.py` | 16–27, 247–256, 319–333 | 3 test classes each have their own `setup_mocks` fixture with 3-deep `with patch(...)` nesting for tkinter. Setup-to-test ratio ~40-50%. |
| `test_unit/ui/screens/test_cargo_quick_dialog_resolution.py` | 30–103 | Tests create live `pygame.Rect`, `pygame_gui.UIManager`, and `CargoQuickDialog` instances. Multi-level side_effect lambdas on `get_planets_at_hex`. |
| `test_unit/strategy/facade/test_colony_demographic_view.py` | 82–103 | `_facade_for()` helper patches 4 internal facade attributes (`_planet_index`, `_race_registry`, `_economy_config`, `session.economy_config`) to bypass normal initialization. |

---

### CAT-9: Simplification — Repeated Imports, Common Setup

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/ui/components/table/test_selection.py` | 9–203 | Delayed import in every single test method: `from game.ui.components.table.selection import SingleSelect` repeated 6 times, `MultiSelect` 7 times, `NoSelect` 6 times. |
| `test_unit/simulation/systems/test_battle_engine_end_conditions.py` | 21–60 | `mock_ship` and `mock_ship_team1` fixtures are nearly identical (differ only in `team_id`). Could be parametrized or merged. |
| `test_unit/strategy/engine/test_organics_consumption_engine.py` | 42–67 | `_colony()` helper exists alongside 5 test classes. Could be a fixture at class scope. |

---

### CAT-10: Parameterize — 3+ Identical-Body Tests

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/ui/screens/test_strategy_menu_panel.py` | 154–194 | 6 tests (`test_save_game_button_calls_callback` through `test_quit_game_button_calls_callback`) differ only in button constant variable. Identical 4-line bodies. Strongly parameterizable with `[(MENU_SAVE_GAME, "MENU_SAVE_GAME"), ...]`. |
| `test_unit/ui/screens/test_fleet_report_filters.py` | 970–1143 | `TestSpecialCapabilityFilter` — 5 tests (`test_filter_hides_ships_with_{ability}`) with identical structure, differing only in ability name and filter key. 150+ lines, parameterizable to ~15. |
| `test_unit/ui/screens/test_fleet_report_filters.py` | 587–665 | `TestFilterShipsSpaceyard` — 3 tests with identical patterns (`NO`/`YES`/`IGNORE`). |
| `test_unit/ui/screens/test_fleet_report_filters.py` | 668–784 | `TestFilterShipsCargo` — 4 tests with identical patterns. |
| `test_unit/strategy/events/test_event_validation.py` | 35–69 | 5 `test_missing_*_raises_persistence_exception` tests — identical body, different field to delete. |
| `test_unit/simulation/test_battle_state_validation.py` | 39–101 | `TestComponentStateValidation` — 6 field-deletion tests. `TestShipStateValidation` lines 145-201 — 8 field-validation tests, near-identical bodies. |
| `test_unit/simulation/systems/test_battle_engine_end_conditions.py` | 115–239 | `TestEscapeBasedMode` — 7 tests with similar fixture setup, could reduce with parametrize. |

---

### CAT-11: Fragile Assertion — Exact Dict/JSON Overassertion

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/strategy/events/test_event_validation.py` | 26, 33 | `assert event.event_type == 'ship_built'` — exact string match on event data after `from_dict`. Tight coupling to serialized form. |
| `test_unit/simulation/test_battle_state_validation.py` | 39–101 | Exact string matching in exception messages: `assert 'component_id' in str(exc_info.value)` — fragile to message wording changes. |
| `test_unit/strategy/data/test_superweapon_orders.py` | 62–123 | Exact dict structure assertions: `data['target']['type'] == 'planet_ref'`, `data['target']['id'] == 42`. Fragile to serialization format changes. |
| `test_unit/strategy/facade/test_facade_dispatch.py` | 36–68 | `DISPATCH_CASES` list with 31 entries of `(method_name, kwargs, expected_cmd_class)` — any command class rename breaks 31 tests simultaneously. |
| `test_unit/ui/screens/test_strategy_menu_panel.py` | 48–78 | Exact label list comparison: `assert labels == ["Save Game", "Load Game", ...]` — any UI string change breaks the test. |

---

### CAT-12: Logic-Heavy — if/else, for with asserts, arithmetic before comparison

| File | Lines | Issue |
|------|-------|-------|
| `test_unit/strategy/engine/test_resupply_engine.py` | 486–527 | `test_fuel_distributed_to_equalize_range` — complex arithmetic: calculates expected fuel distribution based on cost-per-hex ratio, asserts exact `pytest.approx(200.0)` and `pytest.approx(40.0)`. Logic-heavy assertion chain. |
| `test_unit/ui/screens/test_fleet_report_filters.py` | 81–197 | `TestCalculateFleetStats` — 9 tests that each assert on dict keys with arithmetic (e.g., `test_average_hp_calculation: abs(stats['avg_hp_percent'] - 0.7667) < 0.01`). The test itself computes expected values. |
| `test_integration/strategy/test_habitability_on_economy.py` | 250–287 | `test_production_habitability_scales_drain` — calls private `_process_queue_tick_dynamic` with computed magic numbers, then asserts stockpile arithmetic. Multi-step logic in test body. |
| `test_integration/strategy/test_warp_logic_rework.py` | 60–84 | `test_angle_clearance_calculation` — accesses private `galaxy._warp_gen._is_angle_clear` and passes radian values, asserting boolean results against pre-computed expectations. |
| `test_unit/strategy/engine/test_happiness_engine.py` | 130–144 | Multiple tests compute hab values via `score_planet_for_race()` inside test body, then assert against formula-derived expectations. Tests contain production formula calls. |

---

## Summary

| Category | Count | Affected Files |
|----------|-------|----------------|
| CAT-1 (Trivial Pass) | 6 | strategy_menu_panel, superweapon_orders, strategy_session_facade_public_api, simulation_constants, empire_build_queue_viewmodel, fleet_display_name |
| CAT-2 (Tests Nothing Real) | 3 | facade_indices, selection, controllable_adapter_edge_cases |
| CAT-3 (Dead Test Code) | 2 | bug_12_energy_gen, controllable_adapter_edge_cases (partial) |
| CAT-4 (Duplicate Testing) | 4 | battle_engine_end_conditions, event_validation, battle_state_validation, colony_species_config |
| CAT-5 (Fixture Bloat) | 3 | component_resource_manager, resupply_engine, fleet_report_filters |
| CAT-6 (Mocking Brittleness) | 4 | test_ccd, fleet_movement_engine/test_basics, new_game_setup_extended, strategy_modal_window |
| CAT-7 (Sleep/Latency) | 2 | test_auto_save, race_description_llm_controller |
| CAT-8 (Needless Complexity) | 3 | test_setup_screen, cargo_quick_dialog_resolution, colony_demographic_view |
| CAT-9 (Simplification) | 3 | test_selection, battle_engine_end_conditions, organics_consumption_engine |
| CAT-10 (Parameterize) | 7 | strategy_menu_panel, fleet_report_filters (3 classes), event_validation, battle_state_validation, battle_engine_end_conditions |
| CAT-11 (Fragile Assertion) | 5 | event_validation, battle_state_validation, superweapon_orders, facade_dispatch, strategy_menu_panel |
| CAT-12 (Logic-Heavy) | 5 | resupply_engine, fleet_report_filters, habitability_on_economy, warp_logic_rework, happiness_engine |

**Total files with issues**: 34  
**Total files without issues**: 55  
**Top remediation priority**: CAT-10 (parameterize) — ~15 tests across 7 files could collapse to 5–8 parametrized tests, saving ~250 LOC.
