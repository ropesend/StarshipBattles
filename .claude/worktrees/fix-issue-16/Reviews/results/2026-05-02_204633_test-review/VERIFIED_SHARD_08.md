# Shard 08 — Verified Findings Report

**Verifier**: Skeptical Verifier  
**Phase 1 Report**: SHARD_08.md  
**Cross-Shard Report**: CROSS_SHARD.md  
**Verification Date**: 2026-05-02  
**Methodology**: Read cited line ranges + 10 lines context above/below for every claim. Cross-referenced with cross-shard report. Category validated, severity only downgraded.

---

## CRITICAL

### CAT-1: Trivial Pass — Cannot Fail if Imports Succeed

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_strategy_menu_panel.py` | 43–79 | **CONFIRMED** | 7 tests in `TestMenuPanelConstants` verify `BUTTON_COUNT == 6`, `len(MENU_BUTTONS) == 6`, exact label/option-id lists, arithmetic-derived dimensions. All constants defined in the same module — tests can only fail if both constant definitions and tests are edited simultaneously. Panel width/height checks at lines 62-75 do test arithmetic consistency (`PANEL_WIDTH == BUTTON_WIDTH + 2 * PANEL_PADDING`, `PANEL_HEIGHT` formula) — these are slightly more meaningful but still can't break alone. |
| `test_superweapon_orders.py` | 28–56 | **CONFIRMED** | 6 `test_*_order_type_exists` tests: `hasattr(OrderType, 'IMPLODE_PLANET')` + `isinstance(...)`. All assert trivial enum presence. Cannot fail without deliberate enum value deletion. |
| `test_strategy_session_facade_public_api.py` | 122–154 | **CONFIRMED** | `test_every_public_method_present` (hasattr checks against frozen `PUBLIC_METHODS` set), `test_every_public_method_callable` (callable check), `test_no_unexpected_public_methods_added` (inspect.getmembers diff). Runtime introspection — can only fail during intentional refactoring. These are API contract guards. |
| `test_simulation_constants.py` | 12–21 | **CONFIRMED** | `test_constants_exist` — 5 `hasattr` checks against `SimulationConstants`. **Note**: This file has 7 test methods total; the remaining 6 test meaningful behavior (warp timing, map defaults, tick rate inverse, absolute max ticks). The CAT-1 claim correctly scopes only lines 12–21. |
| `test_empire_build_queue_viewmodel.py` | 69–82 | **CONFIRMED** | 3 `TestBuildQueueWindowEvents` tests: `hasattr(BuildQueueWindowEvents, 'SOURCES_CHANGED')` + truthiness check. Trivial presence guards. |
| `test_fleet_display_name.py` | 129 | **CONFIRMED** (weak) | `test_two_empires_have_independent_display_numbers` — both `Empire` objects start at 1, trivial assertions. However, this **does** test a non-trivial invariant (per-empire counter independence), so its CAT-1 classification is borderline. A globalized counter would break it. |

---

### CAT-2: Tests Nothing Real — No game.* imports, All Mocked/Reimplemented

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_facade_indices.py` | 12–74 | **DISPUTED** | **The "No game.* imports" descriptor is incorrect.** Line 14 imports `StrategySessionFacade` from `game.strategy.facade.strategy_session_facade` — this is the real production class being tested. The session, planet, system, and galaxy are MagicMock dependencies, but the SUT is real. The facade's `_get_planet_by_id` method is exercised through its real code path; only its environment is mocked. Reclassify as "fully mocked dependencies" (not all-mocked, not "tests nothing real"). Downgrade to **MINOR or remove CAT-2**. |
| `test_selection.py` | 6–224 | **DISPUTED** | **Every test imports the real production classes** from `game.ui.components.table.selection` (e.g., `SingleSelect`, `MultiSelect`, `NoSelect` are imported at lines 11, 71, 137, etc.). These are pure-in-memory strategy objects with zero dependencies — the tests exercise them directly with no mocking at all. The importing style (per-test delayed import) is CAT-9, but the claims "No game.* imports" and "all mocked" are **factually false**. These are strong unit tests of reusable components. Downgrade to **MINOR or remove CAT-2 entirely**. |
| `test_controllable_adapter_edge_cases.py` | 54–365 | **DISPUTED** | **Imports real `ShipControllableAdapter`, `IControllable`, and `CombatConstants`** from `game.ai.interfaces.controllable` and `game.core.constants` (lines 12–13). The `mock_ship` fixture is a MagicMock, but the adapter itself is the real production class being tested. Tests verify adapter method delegation, initialization, and attribute-forwarding behavior. The "No game.* imports" claim is incorrect. The mock ship is a dependency, not the SUT. Downgrade to **MAJOR (mock brittleness)** or reclassify — these tests exercise real adapter logic through mocks. |

---

### CAT-3: Dead Test Code — Removed Functionality, Unused Helpers

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_bug_12_energy_gen.py` | 32–109 | **CONFIRMED** | File header (lines 10–11) states: "WORKING AS DESIGNED - not a code bug." The test demonstrates that a Generator without Crew Quarters/Life Support is inactive — expected behavior. Uses real game objects (`Ship`, `Component`, `fresh_registries` fixture). Valid regression guard for a closed/non-bug. **Filepath correction**: the report cites `test_repro_issues/`; actual path is `tests/repro_issues/`. |
| `test_controllable_adapter_edge_cases.py` | 339–365 | **CONFIRMED** | `TestAttributeDelegationRemoved` explicitly tests that `__getattr__`/`__setattr__` delegation was **removed** (PROJ-24). Tests what is NOT present rather than functional behavior — but serves as deliberate regression guard for an intentional deletion. **Note**: This is a meaningful guard; accidentally re-adding delegation would break the interface contract. |

---

## MAJOR

### CAT-4: Duplicate Testing

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_battle_engine_end_conditions.py` | 245–287 | **INCONCLUSIVE** | `TestExistingModesUnchanged` has 4 tests that test `TickLimitCondition`, `TeamEliminatedCondition`, `TeamIncapacitatedCondition`, and `NeverCondition` within the battle engine's `is_battle_over()` integration. The report claims individual condition test files provide duplicate coverage. **Cannot verify without reading the individual condition unit test files.** These tests serve as integration-level smoke verifying the conditions work correctly in the engine context — arguably a different testing concern. |
| `test_event_validation.py` | 26–69 | **CONFIRMED** (CAT-10 overlap) | 5 `test_missing_*_raises_persistence_exception` tests (lines 35–69) share identical structure: delete key, assert `PersistenceException` with field name. **More CAT-10 (parameterize) than CAT-4 (duplicate)** — each tests a distinct field validation requirement, but the body is fully parametrizable. |
| `test_battle_state_validation.py` | 39–101 | **CONFIRMED** (CAT-10 overlap) | `TestComponentStateValidation` — 6 nearly-identical field-deletion tests. Same pattern as event_validation. More CAT-10 than CAT-4. |
| `test_colony_species_config.py` | 76–118 | **DISPUTED** | `TestLastFoodRatioAggregation` has 5 tests, each testing **distinct behavioral cases** of the MIN aggregation property: single-resource pass-through, multi-resource min, zero-collapses, all-ones, empty-dict-returns-1. These are NOT duplicate tests — each exercises a different edge case of the `last_food_ratio` property logic. The tests have identical *structural patterns* (set `last_consumption_ratios`, assert `last_food_ratio`) but verify **fundamentally different behavioral assertions**. Downgrade to **MINOR or remove from CAT-4**. |

---

### CAT-5: Fixture Bloat — Function-Scoped Expensive Fixtures Used 10+ Times

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_component_resource_manager.py` | 23–52 | **CONFIRMED** | 3 function-scoped fixtures (`mock_component`, `mock_resource_consumption_ability`, `mock_constant_consumption_ability`) creating MagicMock trees, used across 9 test classes (~24 test methods). |
| `test_resupply_engine.py` | 20–101 | **CONFIRMED** (line range incomplete) | 6 helper functions at lines 20–101: `_make_mock_registries`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_empire`. **Additional 4 helpers** at lines 306–379: `_make_mock_ship`, `_make_mock_fleet`, `_make_mock_galaxy`, `_make_planet_with_fuel`. Total: 10 helper functions creating multi-level mock trees. The report's line range (20–101) only captures 6 of 10. `_make_mock_ship` uses closure-based mutable `_fuel_state` dict (line 319). |
| `test_fleet_report_filters.py` | 12–75 | **CONFIRMED** | `make_mock_ship` helper: 63 lines, 20+ parameters, `design_data` dict with nested `expected_stats`, `get_calculated_stats` return_value, consumable_levels, HP percentage logic. Called ~80+ times across 15 test classes. |

---

### CAT-6: Mocking Brittleness — Patching _private, Assert on `call_args_list`

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_ccd.py` | 23–376 | **CONFIRMED** | Every test constructs MagicMock projectiles with ~15 attributes (position, velocity, radius, damage, is_alive, team_id, type, source_weapon, distance_traveled, target, status — verified lines 28–39). Tight coupling to `ProjectileManager.update()` internal attribute consumption. |
| `test_basics.py` | 77–108 | **CONFIRMED** | `test_recalculates_path_if_destination_changed` (lines 89–108) patches `game.strategy.services.fleet_navigation_service.find_hybrid_path` — a deep internal of the engine. Also matches cross-shard **APC-003** (patching private `_methods`). |
| `test_new_game_setup_extended.py` | 16–49 | **CONFIRMED** | `_make_screen()` (lines 16–49) patches `__init__` with `lambda self, *a, **kw: None`, then manually populates 16+ attributes. Tight coupling to `NewGameSetupScreen.__init__` attribute list. **Also matches cross-shard APC-001** (`__new__` bypass-init pattern). |
| `test_strategy_modal_window.py` | 16–37 | **CONFIRMED** | `_make_modal_window` (lines 16–37) patches `pygame_gui.elements.UIWindow.__init__` with lambda, manually calls base class `__init__`. Fragile to changes in UIWindow or StrategyModalWindow init signatures. |

---

### CAT-7: Sleep/Latency — `time.sleep`, Delay, Wait

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_auto_save.py` | 124 | **CONFIRMED** | `time.sleep(0.01)` at line 124 — waits for mtime to differ for save-file immutability verification. Legitimate but measurable overhead. |
| `test_race_description_llm_controller.py` | 135, 139, 325, 343 | **CONFIRMED** | 4 uses of `time.sleep(0.02)`. `_wait_until` spin-loop at lines 133–140 uses `time.sleep(0.01)`. Headless LLM controller tests. |
| `test_race_description_llm_controller.py` | 82–91 | **CONFIRMED** | `_BlockingProvider.complete` (lines 82–91): `while time.monotonic() < end` loop with `time.sleep(0.005)`. Tests may take up to 5 seconds. Verified at lines 82–86. |

---

## MINOR

### CAT-8: Needless Complexity — 5+ Nested Patches, Setup >50%

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_setup_screen.py` | 16–27, 247–256, 319–333 | **CONFIRMED** | `TestBattleSetupScreen.setup_mocks` (lines 16–27): 3-deep `with patch(...)` nesting for tkinter. Each of the 3 test classes has its own `setup_mocks` fixture. |
| `test_cargo_quick_dialog_resolution.py` | 30–103 | **CONFIRMED** | Tests create live `pygame.Rect` (line 63), `pygame_gui.UIManager` (fixture line 13), real `CargoQuickDialog` instances (lines 64–66). Multi-level `side_effect` lambdas on `get_planets_at_hex` (lines 55–58). |
| `test_colony_demographic_view.py` | 82–103 | **CONFIRMED** | `_facade_for()` helper (lines 82–103) patches 4 internal facade attributes: `_planet_index` (line 95), `_race_registry` (line 98), `_economy_config` (line 101), and `session.economy_config` (line 102). Bypasses normal init. |

---

### CAT-9: Simplification — Repeated Imports, Common Setup

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_selection.py` | 9–203 | **CONFIRMED** | Delayed imports in every test method: `SingleSelect` imported at lines 11, 21, 33, 45, 60, 70 — 6 times. `MultiSelect` at lines 80, 91, 101, 112, 123, 134, 144 — 7 times. `NoSelect` at lines 156, 166, 176, 187, 197, 200 — 6 times. Every test has `from game.ui.components.table.selection import ...`. |
| `test_battle_engine_end_conditions.py` | 21–60 | **CONFIRMED** | `mock_ship` (lines 23–34) and `mock_ship_team1` (lines 37–48) are nearly identical — differ only in `team_id` (0 vs 1) and `is_derelict` (present in mock_ship, absent in mock_ship_team1). Could be parametrized. |
| `test_organics_consumption_engine.py` | 42–67 | **CONFIRMED** | `_colony()` helper (lines 42–66) exists alongside 5 test classes. Could be a class-scoped fixture. |

---

### CAT-10: Parameterize — 3+ Identical-Body Tests

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_strategy_menu_panel.py` | 154–194 | **CONFIRMED** | 6 tests (lines 154–194): `test_save_game_button_calls_callback` through `test_quit_game_button_calls_callback`. Identical 4-line bodies, differ only in `buttons[MENU_*]` constant. Strongly parameterizable with `[(MENU_SAVE_GAME, "MENU_SAVE_GAME"), ...]`. |
| `test_fleet_report_filters.py` | 970–1143 | **CONFIRMED** | `TestSpecialCapabilityFilter` — 5 tests (lines 973–1143): `test_filter_hides_ships_with_{ability}` with identical structure, differing in ability name + filter key. ~170 lines, parameterizable to ~15. Verified: `test_filter_hides_ships_with_ability` (973), `test_filter_hides_ships_without_ability` (999), `test_filter_default_shows_all` (1025), `test_filter_hides_ships_with_open_warp_ability` (1042), `test_filter_hides_ships_with_close_warp_ability` (1068), `test_filter_hides_ships_with_destroy_star_ability` (1094), `test_filter_hides_ships_with_create_sphere_ability` (1120). **Actually 7 tests, not 5** — and `test_filter_hides_ships_without_ability` (999) tests the inverse (YES filter), which is a genuinely different assertion direction. Subtle but not a duplicate of the NO filter tests. |
| `test_fleet_report_filters.py` | 587–665 | **CONFIRMED** | `TestFilterShipsSpaceyard` — 3 tests (lines 587–665): `test_filter_hide_has_spaceyard` (NO), `test_filter_hide_no_spaceyard` (YES), `test_filter_show_all_spaceyard_states` (IGNORE). Identical patterns for tri-state FilterState. Parameterizable. |
| `test_fleet_report_filters.py` | 668–784 | **CONFIRMED** | `TestFilterShipsCargo` — 4 tests with identical patterns for tri-state cargo filtering. |
| `test_event_validation.py` | 35–69 | **CONFIRMED** | 5 `test_missing_*_raises_persistence_exception` tests — identical body, different field to delete. |
| `test_battle_state_validation.py` | 39–101, 145–201 | **CONFIRMED** | `TestComponentStateValidation` — 6 field-deletion tests (lines 39–101). `TestShipStateValidation` — 8 field-validation tests (lines 145–201 in file but 108+ context), near-identical bodies. |
| `test_battle_engine_end_conditions.py` | 115–239 | **CONFIRMED** | `TestEscapeBasedMode` — 7 tests (lines 119–239) with similar fixture setup: each creates `EscapeCondition(escape_radius=5000.0, ...)`, sets ship positions, asserts `is_battle_over()`. Distinct behavioral tests (escape radius, dead ship ignoring, team-specific, all-ships, Euclidean distance), **not identical bodies** — but the pattern of "set position, set condition, assert" is uniform. Low-priority CAT-10. |

---

### CAT-11: Fragile Assertion — Exact Dict/JSON Overassertion

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_event_validation.py` | 26, 33 | **CONFIRMED** | Line 29: `assert event.event_type == 'ship_built'` — exact string match on event data after `from_dict`. Also line 33: `assert event.message == 'Cruiser completed at Alpha Centauri'`. Tight coupling to fixture data. |
| `test_battle_state_validation.py` | 39–101 | **CONFIRMED** | Lines 44, 48, 52, etc.: `assert 'component_id' in str(exc_info.value)` — exact substring matching in exception messages. Fragile to message wording changes. |
| `test_superweapon_orders.py` | 62–123 | **CONFIRMED** | Lines 73–75: `assert data['target']['type'] == 'planet_ref'`, `assert data['target']['id'] == 42`. Exact dict structure assertions. Lines 83–84, 93–94, etc. Fragile to serialization format changes. |
| `test_facade_dispatch.py` | 36–68 | **CONFIRMED** | `DISPATCH_CASES` list (lines 36–68) with 31 entries of `(method_name, kwargs, expected_cmd_class)`. Any command class rename breaks all 31 parametrized test cases. **Note**: This IS parametrized (uses `@pytest.mark.parametrize` at line 74) — the fragility is the hardcoded class name strings in the data table, not the test structure. |
| `test_strategy_menu_panel.py` | 48–78 | **CONFIRMED** | `test_menu_buttons_labels` (lines 48–52): `assert labels == ["Save Game", "Load Game", "Settings", "Controls", "Quit to Menu", "Quit Game"]`. Any UI string change breaks the test. Also `test_menu_buttons_option_ids` (lines 55–59): exact option_id ordering. |

---

### CAT-12: Logic-Heavy — if/else, for with asserts, arithmetic before comparison

| File | Lines | Verdict | Notes |
|------|-------|---------|-------|
| `test_resupply_engine.py` | 486–527 | **CONFIRMED** | `test_fuel_distributed_to_equalize_range` (lines 486–527): calculates expected fuel distribution based on cost-per-hex ratio (10/hex for ship A, 2/hex for ship B), asserts `pytest.approx(200.0)` and `pytest.approx(40.0)`. The test body computes its own expected values from the same formula the SUT uses. |
| `test_fleet_report_filters.py` | 81–197 | **CONFIRMED** | `TestCalculateFleetStats` — 9 tests (lines 81–197). `test_average_hp_calculation` (lines 117–129): `abs(stats['avg_hp_percent'] - 0.7667) < 0.01` — test computes expected value. The suite tests stat aggregation logic where expected values require arithmetic. |
| `test_habitability_on_economy.py` | 250–287 | **CONFIRMED** | `test_production_habitability_scales_drain` (lines 250–287): calls private `_process_queue_tick_dynamic` on two engines, computes `ideal_drain = 1e6 - ideal.stockpile["metals"]`, asserts relative ratios (`hostile_drain < ideal_drain * 0.05`). Multi-step logic including pre-seeding stockpiles to 1e6. |
| `test_warp_logic_rework.py` | 60–84 | **CONFIRMED** | `test_angle_clearance_calculation` (lines 60–84): accesses private `galaxy._warp_gen._is_angle_clear` (line 80), passes radian values (`0.1`, `math.pi / 2`), asserts boolean results. Also tests `hex_distance()` arithmetic (lines 49–54). |
| `test_happiness_engine.py` | 130–144 | **CONFIRMED** | `test_ideal_planet_food_ratio_one_base_half` (lines 131–144): computes `score_planet_for_race(planet, race)` inside test body, then asserts `pop.happiness == pytest.approx(0.5 * 1.0 * hab)`. Test reproduces the production formula in its assertion. Verified imports at line 29: `from game.strategy.formulas.habitability import score_planet_for_race`. |

---

## Cross-Shard Claims Involving Shard 08

### DUP-003: Mock ship/fleet factory helpers (Shard 06 + Shard 08)

| Claim | Verdict | Notes |
|-------|---------|-------|
| `test_resupply_engine.py:_make_mock_ship()` (Shard 08) vs `test_fleet_cargo_resources.py:_make_ship()` (Shard 06) share closure-based cargo mock pattern | **CONFIRMED** | Shard 08 `_make_mock_ship` (lines 306–337) uses closure-based mutable `_fuel_state` dict in `_get_current_resource` and `_resupply` lambdas. Both patterns use `dict()` mutable state captured in closures for cargo-like behavior. Recommended shared `make_cargo_mock_ship()` in `tests/fixtures/`. |

### HLP-001: make_mock_ship() with design_data and calculated_stats

| Claim | Verdict | Notes |
|-------|---------|-------|
| `test_fleet_report_filters.py:12-75` (Shard 08) has 63-line `make_mock_ship` duplicated with Shard 06 and other files | **CONFIRMED** | Verified the 63-line helper at lines 12–75. `test_resupply_engine.py` has its own `_make_mock_ship` (lines 306–337) and `_make_mock_fleet` (lines 340–347). The report correctly identifies the broader pattern. |
| `test_strategy_session_facade.py` has 4 test classes redefining `_make_mock_fleet`, `_make_mock_empire`, `_make_mock_planet` | **CONFIRMED** (no Shard 08 impact) | The report mentions this pattern exists but this specific file is not in Shard 08's scope. Shard 08's `test_resupply_engine.py` contributes to the same duplication family. |

### HLP-004: make_planet helper triplication — Shard 08 mention

| Claim | Verdict | Notes |
|-------|---------|-------|
| `test_resupply_engine.py:_make_planet_with_fuel` (Shard 08) part of broader make_planet duplication | **CONFIRMED** | `_make_planet_with_fuel` at lines 362–379 creates a mock Planet+facility+registries tuple. Part of a cross-shard pattern of duplicated planet factory helpers. The specific helper in Shard 08 adds fuel-specific behavior (fuel storage, fuel generator) beyond plain planet creation. |

### APC-001: `__new__` bypass-init pattern — Shard 08

| Claim | Verdict | Notes |
|-------|---------|-------|
| `test_new_game_setup_extended.py:16-49` (Shard 08) uses bypass-init pattern | **CONFIRMED** | `_make_screen()` at lines 16–49: `patch.object(NewGameSetupScreen, '__init__', lambda self, *a, **kw: None)` + `.__new__()` + manual attribute wiring of 8 UI element arrays (4x per player), `save_name_input`, `kill`, etc. Zero regression protection for actual `__init__` or pygame_gui lifecycle. |

### APC-003: Patching private `_methods` — Shard 08

| Claim | Verdict | Notes |
|-------|---------|-------|
| `test_basics.py:77-108` (Shard 08) patches `fleet_navigation_service.find_hybrid_path` | **CONFIRMED** | Lines 101–108: `with patch('game.strategy.services.fleet_navigation_service.find_hybrid_path')` — patches a deep internal of the engine rather than exercising through public API. |

---

## Summary

| Category | Phase 1 Count | CONFIRMED | DISPUTED | INCONCLUSIVE |
|----------|---------------|-----------|----------|--------------|
| CAT-1 (Trivial Pass) | 6 | 6 (1 weak) | 0 | 0 |
| CAT-2 (Tests Nothing Real) | 3 | 0 | 3 | 0 |
| CAT-3 (Dead Test Code) | 2 | 2¹ | 0 | 0 |
| CAT-4 (Duplicate Testing) | 4 | 2 | 1 | 1 |
| CAT-5 (Fixture Bloat) | 3 | 3² | 0 | 0 |
| CAT-6 (Mocking Brittleness) | 4 | 4 | 0 | 0 |
| CAT-7 (Sleep/Latency) | 3 | 3 | 0 | 0 |
| CAT-8 (Needless Complexity) | 3 | 3 | 0 | 0 |
| CAT-9 (Simplification) | 3 | 3 | 0 | 0 |
| CAT-10 (Parameterize) | 7 | 7³ | 0 | 0 |
| CAT-11 (Fragile Assertion) | 5 | 5 | 0 | 0 |
| CAT-12 (Logic-Heavy) | 5 | 5 | 0 | 0 |
| Cross-Shard | 5 | 5 | 0 | 0 |

¹ Filepath correction: `test_repro_issues/` → `tests/repro_issues/`  
² Line range incomplete for `test_resupply_engine.py` (20–101 captures 6 of 10 helpers)  
³ `TestSpecialCapabilityFilter` has 7 tests, not 5 as reported  

### Dispute Details

**DISPUTED CAT-2 #1** (`test_facade_indices.py`): The test imports and exercises the real `StrategySessionFacade` class. Only dependencies are mocked. Remove "No game.* imports" descriptor.

**DISPUTED CAT-2 #2** (`test_selection.py`): The test imports and exercises real production `SingleSelect`/`MultiSelect`/`NoSelect` classes with **zero mocking**. These are strong unit tests. Remove CAT-2 entirely.

**DISPUTED CAT-2 #3** (`test_controllable_adapter_edge_cases.py`): Imports real `ShipControllableAdapter`, `IControllable`, `CombatConstants`. The mock ship is a dependency, not the SUT. Reclassify or downgrade.

**DISPUTED CAT-4** (`test_colony_species_config.py:76-118`): The 5 `TestLastFoodRatioAggregation` tests each verify distinct behavioral edge cases of the MIN aggregation property. Not duplicate tests — different logical assertions. Downgrade to MINOR or remove.

### Cross-Shard Verdicts

All 5 cross-shard claims involving Shard 08 files are **CONFIRMED**. The DUP-003 closure-based mock pattern, HLP-001/HLP-004 helper duplication, APC-001 bypass-init pattern, and APC-003 private-method patching are all verified against the actual code.
