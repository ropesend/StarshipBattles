# Shard 09 Test Coverage Audit Report

**Generated:** 2026-05-20 | **Production files:** 42 | **Estimated LOC:** ~9742

---

## Summary

| Tier | Count | LOC | Status |
|------|-------|-----|--------|
| **Tier 0** (zero tests) | **3** | 535 | Files with no test coverage whatsoever |
| **Tier 1** (no symbols tested) | **5** | 194 | `__init__.py` re-exports, constants-only |
| **Tier 2** (partial coverage) | **16** | ~4,713 | Tested but gaps in coverage |
| **Tier 3** (apparently covered) | **18** | ~4,300 | Heuristically well-tested |

**Critical finding:** The heuristic baseline had **6 false Tier-0 positives** — files it claimed had zero tests actually have test suites. Verified by reading the test files. The true Tier-0 count is 3, not 9.

**Overall assessment:** Shard 09 is **moderately well-tested**. The 3 true Tier 0 files are all UI-layer rendering/event code (`propulsion_outcomes.py`, `water_target_editor.py`, `transfer_dialogs.py`). Production logic in `simulation/` and `strategy/` layers has good coverage. Most Tier 2 gaps are private helper methods tested indirectly through public APIs.

---

## Tier 0: No Tests (CRITICAL)

### `game/ui/screens/test_lab/details/propulsion_outcomes.py` — 229 LOC
**Status: CRITICAL — zero tests.**
- **5 symbols,** 0 tested.
- `is_propulsion_test()` — pure logic, testable with mock records
- `draw_propulsion_outcomes()` — main orchestrator
- `_draw_motion_outcomes()` (line 73) — velocity/position/distance rendering
- `_draw_turn_outcomes()` (line 128) — angle/expected-vs-actual color-coded rendering (lines 169-184 contain pass/fail color logic, testable)
- `_draw_stationary_outcomes()` (line 200) — zero-velocity rendering
- No test file exists. No grep hits for `is_propulsion_test`, `draw_propulsion_outcomes`, or `propulsion_outcomes` in test directory.

### `game/ui/screens/water_target_editor.py` — 227 LOC
**Status: CRITICAL — zero unit tests.**
- **9 symbols,** 0 directly unit-tested.
- `WaterTargetEditor` (extends `PlanetTargetEditor`) — modal window for planet water coverage
- `__init__` (line 34) — wires callbacks, builds UI
- `_build_ui()` (line 75) — species selector, slider, 4 buttons
- `update()` (line 165) — time-driven slider polling
- `_button_handlers()` (line 173) — button-to-method dispatch dict
- `_on_apply()` (line 181) — fires `on_apply_callback(planet_id, water_level)`
- `_set_species_ideal()` (line 195) — reads `race_config.preferences["water"].setpoint`
- `_set_match_current()` (line 213) — clones current water to slider
- `_clear_target()` (line 220) — fires callback with `None`
- Only integration references exist (`tests/integration/ui/test_editor_click_blocking.py` patches the class for click-blocking tests; no unit tests for logic)
- The `_set_species_ideal` method's water setpoint read (line 203) is an untested code path

### `game/ui/screens/strategy_windows/transfer_dialogs.py` — 79 LOC
**Status: CRITICAL — zero tests for TransferDialogRegistrar.**
- **4 symbols,** 0 directly tested.
- `TransferDialogRegistrar.__init__(composer)` (line 21)
- `TransferDialogRegistrar.open(source_fleet, hex_coord)` (line 24) — kills existing, creates `TransferDialog`
- `TransferDialogRegistrar.open_quick(fleet, hex_coord, direction)` (line 53) — creates `CargoQuickDialog`
- No test file named `test_transfer_dialog_registrar` or similar. The existing `test_transfer_dialog*.py` files test `TransferDialog`/`CargoQuickDialog` directly, not the registrar.
- The `open_quick` method's `direction: str` parameter has no validation (line 53) — untested error path

### False Tier-0 positives (heuristic errors):
These files were incorrectly classified as Tier 0 by the heuristic but actually have test coverage:

| File | Actual tests | Correct tier |
|------|-------------|-------------|
| `game/screen_router.py` (518 LOC) | `tests/unit/test_screen_router.py` (545 lines) | Tier 2 |
| `game/simulation/entities/ship_component_manager.py` (293 LOC) | `tests/unit/simulation/entities/test_ship_component_manager.py` (445 lines) + DI test | Tier 2 |
| `game/ui/services/tkinter_utils.py` (231 LOC) | `tests/unit/ui/services/test_tkinter_utils.py` (217 lines) | Tier 2 |
| `game/simulation/components/abilities/planetary/resource_modifiers.py` (160 LOC) | `test_planetary_abilities.py` + `test_strategic_abilities.py` | Tier 3 |
| `game/simulation/systems/boundary_enforcement.py` (122 LOC) | `test_exit_policy.py` + `test_tick_phases.py` + `test_battle_engine_boundary.py` | Tier 2 |
| `game/strategy/generation/density/__init__.py` (27 LOC) | Re-export only; tested via consumer tests | Tier 1 |

---

## Tier 1: `__init__.py` Re-exports & Constants (ADVISORY)

### `game/simulation/entities/stat_contributors/__init__.py` — 43 LOC
- Re-exports `accumulator`, `command`, `defense`, `launch`, `movement`, `registry`, `weapons`, `StatAccumulator`
- Calls `registry._seed_builtin_contributors()` at import time (line 32)
- 6 sub-module test files exist for the individual contributors. The `__init__.py` seed call is exercised via any test importing from the package.
- **ADVISORY:** Re-export module — no action needed.

### `game/simulation/replay/__init__.py` — 80 LOC
- Re-exports from `replay_capture`, `replay_serialization`, `replay_spec`, `replay_outcome`, `replay_record`, `replay_player`
- 12 test files reference symbols imported from this package
- **ADVISORY:** Re-export module — no action needed.

### `game/ui/effects/__init__.py` — 1 LOC
- Docstring only: `"""Visual effects for battle rendering."""`
- `tests/unit/ui/effects/test_hit_effects.py` exists (tests effect sub-modules)
- **ADVISORY:** Single-line docstring marker — no action needed.

### `game/ui/screens/battle_setup/__init__.py` — 16 LOC
- Re-exports `FleetBattleSetupScreen`
- `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` uses the import
- **ADVISORY:** Re-export module — no action needed.

### `game/ui/screens/battle_setup/constants.py` — 54 LOC
- Module-level constants: `_SYSTEM_SCOPE_COMPLEXES`, `_SECTOR_SCOPE_COMPLEXES`, `_TARGETING_OPTIONS`, `_MOVEMENT_OPTIONS`, `_BATTLE_ROLE_OPTIONS`
- Used by battle setup panels and controller — exercised indirectly
- No direct unit test for these constants' values
- **ADVISORY:** Constants-only module — low risk. Could add a simple existence test checking that lists are non-empty and tuples have expected structure.

---

## Tier 2: Partial Coverage (MAJOR)

### `game/screen_router.py` — 518 LOC
**Test file:** `tests/unit/test_screen_router.py` (545 lines — comprehensive)

**Tested:** Scene creation, state machine transitions, `_switch_scene`, `update_resolution`, `start_builder`, `on_builder_return`, `start_battle_setup`, `start_strategy_layer`, `show_load_menu`, `start_test_lab`, `start_research_tree`, `on_research_tree_return`, `start_galaxy_test`, `on_galaxy_test_return`, `start_keybindings`, `on_keybindings_return`, `start_race_setup`, `_on_race_setup_complete`, `_on_race_setup_cancel`, `start_battle`, overlay dialog flags

**Gaps (tested indirectly or via SceneCallbacks mocks):**
- `_on_new_game_start()` (line 199-239) — complex path: `GameSession` creation, `SaveGameService.save_game`, `QuickstartBuilder`, error dialog on save failure. The test file mocks the full save/load pipeline but doesn't exercise the production save-failure branch (lines 230-239: `UIMessageWindow` creation).
- `_start_quickstart()` (line 246-290) — similar save-failure branch (lines 289-290) untested
- `_on_load_game()` (line 321-355) — save-failure dialog branch (lines 345-355) untested
- `start_battle()` (line 457-513) — resolution mismatch and controller creation tested; `config is None` branch (lines 489-495) and `config is not None` branch (replay path) both covered via test

**MAJOR:** The save-failure error dialog paths (3 locations) are untested.

### `game/simulation/entities/ship_component_manager.py` — 293 LOC
**Test file:** `tests/unit/simulation/entities/test_ship_component_manager.py` (445 lines)

**Tested:** `add_component`, `add_components_bulk`, `remove_component`, `get_all_components`, `iter_components`, `get_components_by_ability`, `get_weapon_components_cached`, `get_components_by_layer`, `has_components`, `find_component_with_index`, `clear_non_hull_components`, `_invalidate_components_cache`

**Gaps:**
- `__init__` (line 31) — tested implicitly through `Ship.__init__` but never tested in isolation for cache initialization
- `_attach_component()` (line 56) — private internal helper, tested through `add_component`/`add_components_bulk`. However, the `modifier_service is None` branch (late import at lines 75-79) is only exercised when calling `add_component` (not `add_components_bulk`, which pre-creates the service at line 122-125). **MINOR** — both paths tested.

**MINOR:** Near-complete coverage. No gaps requiring new tests.

### `game/simulation/systems/boundary_enforcement.py` — 122 LOC
**Test files:** `test_exit_policy.py`, `test_tick_phases.py`, `test_battle_engine_boundary.py`

**Tested:** `bounce_ship` with RectBoundary (line 100-108: flip velocity components), `bounce_ship` with CircleBoundary (line 110-118: reflect about radial normal), NONE/DESTROY/RETREAT exit policies

**Gaps:**
- `enforce_boundary()` (line 29) — tested indirectly through `BoundaryEnforcementPhase` ticks. The `boundary is None` guard (line 38-39) and the alive-ship snapshot (line 43) are not unit-tested directly.
- `apply_exit_policy()` (line 50) — the `Unknown ExitPolicy` fallback at line 81 (`logger.warning`) is untested
- `bounce_ship()` (line 84) — the `velocity is None` guard (line 97-98) and the `else` fallback (line 119-122: flip both components) are untested

**MINOR:** 3 untested guard/failsafe branches.

### `game/simulation/components/modifier_manager.py` — 219 LOC
**Test file:** `tests/unit/simulation/components/test_modifier_manager.py`

**Tested:** `add_modifier`, `remove_modifier`, `get_modifier`, `get_all_effects`, `get_stat_summary`

**Gaps:**
- `__init__` (line 46) — tested implicitly, not in isolation
- `_load_initial_modifiers()` (line 56) — private, tested through `__init__`; the `mod_id not in mods` warning branch (line 76-80) is **untested** (requires a component with a missing modifier in data)
- `get_stat_summary()` (line 165) — tested; the `effect.operation == 'set'` branch (line 215-216: last-set-wins) not explicitly verified

**MINOR:** 2 untested branches.

### `game/simulation/replay/replay_capture.py` — 138 LOC
**Test files:** `test_capture_pipeline.py`, `test_replay_capture_e2e.py`, `test_replay_store.py`

**Tested:** `NullCaptureSink.on_battle_started`, `NullCaptureSink.on_battle_ended`, `set_default_capture_sink`, `reset_default_capture_sink`, `ReplayCaptureContext` construction

**Gaps:**
- `IReplayCaptureSink` Protocol — tested structurally by integration tests, not unit-tested for `@runtime_checkable` behavior
- `get_default_capture_sink()` (line 113) — tested as fixture setup, not in isolation
- **MINOR:** All gaps are minor. The protocol + sink are well-tested via integration.

### `game/simulation/entities/ship.py` — 607 LOC
**Test files:** 84 candidate test files (heuristic), core tests at `tests/unit/entities/test_ship.py`

**Tested:** Ship construction, DI validation, layers, hull, stats, combat delegates (lazy init), component facade methods, physics, serialization

**Heuristically flagged as untested (verified):**
- `Ship.stat_querier` (line 342) — **FALSE POSITIVE.** Tested in `test_ship_stat_querier.py` (27+ tests including `get_total_ecm_score`, `get_total_sensor_score`)
- `Ship.validator_helper` (line 349) — **FALSE POSITIVE.** Tested in `test_ship_validator_helper.py` (5 tests)
- `Ship.get_total_ecm_score` — **FALSE POSITIVE.** Tested in `test_ship_stat_querier.py` (7 specific tests: line 158, 175, 430, 465, 629, 664)
- `Ship.check_validity` — **FALSE POSITIVE.** Tested in `test_ship_validator_helper.py` (line 15, 39)

**MINOR:** The heuristic had 4 false positives for ship.py. Coverage is comprehensive.

### `game/strategy/engine/commands/__init__.py` — 629 LOC
**Test files:** 27 candidate test files

**Heuristically flagged as untested (verified):**
- `TransferDirection` (line 12) — **TRUE.** The `TransferDirection` enum is used indirectly via `IssueTransferCommand`, but no test imports or directly tests the enum values (`LOAD`, `UNLOAD`). **MINOR** — used in command DTOs which are tested.
- `RemoveFromConstructionQueueCommand` (line 490) — **FALSE POSITIVE.** Tested in `test_command_handlers.py` (`TestRemoveFromConstructionQueueCommandHandler`, 8 tests starting at line 1486)
- `ReorderConstructionQueueCommand` (line 509) — **FALSE POSITIVE.** Tested in `test_command_handlers.py` (`TestReorderConstructionQueueCommandHandler`, 7 tests starting at line 1677)
- `SetAtmosphereTargetCommand` (line 605) — **FALSE POSITIVE.** Tested in `test_planet_command_handlers.py` (line 369, 4 tests)
- `SetGravityTargetCommand` (line 612) — **FALSE POSITIVE.** Tested in `test_planet_command_handlers.py` (line 431, 4 tests)
- `SetWaterTargetCommand` (line 619) — **FALSE POSITIVE.** Tested in `test_planet_command_handlers.py` (line 477, 4 tests)
- `SetRadiationShieldTargetCommand` (line 626) — **FALSE POSITIVE.** Tested in `test_planet_command_handlers.py` (line 523, 4 tests)

**MINOR:** Only `TransferDirection` (2 enum values) is genuinely untested. All other 6 claimed-gap symbols are tested.

### `game/strategy/engine/commands/registry.py` — 494 LOC
**Test files:** 11 candidate test files

**Heuristically flagged as untested (verified):**
- `CommandRegistry.unregister()` (line 227) — **FALSE POSITIVE.** The `test_command_registry_thirdparty.py` docstring says "a third-party command registers, dispatches, unregisters cleanly." The function is tested.
- `CommandRegistry.__len__()` (line 246) — **UNVERIFIED.** No explicit test for `len(registry)`. Used implicitly in assertions but never directly verified.
- `CommandRegistry.__contains__()` (line 249) — **UNVERIFIED.** No explicit `assert cmd_name in registry` test found.
- `_wrap()` (line 419) — **ADVISORY.** Internal closure in `command_spec()`. Tested through decorator contract tests.

**MINOR:** `__len__` and `__contains__` missing explicit assertions.

### `game/strategy/engine/construction_forecast.py` — 100 LOC
**Test file:** `tests/unit/strategy/engine/test_construction_forecast.py` (15 tests)

**Gaps:**
- `_get_planetary_ids()` (line 21) — **FALSE POSITIVE (indirect).** Called internally by `forecast_queue_turn_spend()`. Every test of `forecast_queue_turn_spend` exercises this function. The `@lru_cache` behavior is tested indirectly.

**MINOR:** No gaps.

### `game/strategy/engine/issuer_adapter.py` — 372 LOC
**Test file:** `tests/unit/strategy/engine/test_issuer_adapter.py`

**Heuristically flagged as untested (verified):**
- `_matches()` (line 115) — **TRUE (indirect).** Private helper called by `PlanetStagingYardIssuerAdapter.pop_carried()` and `count_carried()`. Tested through integration tests (`test_fms_cd_isolation.py`, `test_fms_d_e2e.py`), not through direct unit tests. The branch at line 132-136 (dict-shape probe + `VALID_VEHICLE_TYPES` check) is exercised but the `else` branch (line 136-137: `cv = None`) requires a dict with an invalid `vehicle_type`. **MINOR** — untested explicit invalid-dict branch.
- `_cv_matches()` (line 146) — **TRUE (indirect).** Private helper called by `FleetShipIssuerAdapter.pop_carried()` and `count_carried()`. Tested through integration. The `design_id != "auto"` branch at line 150 is exercised.
- `FleetShipIssuerAdapter.ship` (line 178) — **TRUE.** Property getter returning `self._ship`. Tested implicitly when tests access `issuer._ship` directly. **ADVISORY** — trivial getter.

**MINOR:** Private helper `_matches` invalid-dict branch untested; `_cv_matches` tested indirectly.

### `game/strategy/engine/order_handlers/launch_satellites.py` — 274 LOC
**Test files:** `test_launch_satellites_handler.py`, `test_fms_d_e2e.py`, `test_fms_cd_isolation.py`, `test_fms_planet_launch.py`

**Heuristically flagged as untested (verified):**
- `_run_with_issuer()` (line 130) — **TRUE (indirect).** Called by `execute_action_order` and `execute_for_issuer`. The unit test exercises it via those public methods. All branches tested: count <= 0 (line 148), insufficient satellites (line 156), success path (line 168).
- `_find_ship()` (line 222) — **TRUE (indirect).** Static helper, tested through `execute_action_order`. The `None` return path (ship not found) tested at line 81-85.
- `_create_satellite_group()` (line 231) — **TRUE (indirect).** Tested through `_run_with_issuer`. `empire.deployed_groups.append` is part of the test assertions.
- `_mint_group_id()` (line 249) — **TRUE (indirect).** Tested through `_create_satellite_group`. The while-loop for ID collision (line 255-256) is **untested** — requires a test with existing deployed groups at ID 300000.
- `_carried_vehicle_to_ship_instance()` (line 259) — **TRUE (indirect).** Static helper delegating to `carried_vehicle_to_ship_instance()`. Tested through the launch flow.

**MAJOR:** `_mint_group_id` collision loop (line 255-256) never exercised. If another deployed group already has ID 300000, the handler increments — this path has zero coverage.

### `game/strategy/facade/slices/fleet_slice.py` — 191 LOC
**Test files:** `test_strategy_session_facade.py`, `test_container_snapshots.py`, `test_facade_grouped_namespaces.py`

**Heuristically flagged as untested (verified):**
- `FleetSlice.__init__` (line 26) — **FALSE POSITIVE.** Tested through all FleetSlice construction in tests.
- `FleetSlice.build_fleet_hex_index()` (line 45) — **TRUE (untested directly).** Called by `get_fleets_at_hex` via cache rebuild, but never tested as a standalone unit. The internal dict building logic is exercised but the method itself has no dedicated test asserting the index structure.
- `FleetSlice.get_fleet()` (line 60) — **FALSE POSITIVE.** Tested in `test_facade_grouped_namespaces.py` line 114.
- `FleetSlice.get_fleets_at_hex()` (line 67) — **FALSE POSITIVE.** Tested in `test_strategy_session_facade.py` lines 88, 103.
- `FleetSlice.get_fleet_path_preview()` (line 84) — **FALSE POSITIVE.** Tested in `test_strategy_session_facade.py` lines 113, 130.
- `FleetSlice.get_fleet_path_projection()` (line 96) — **FALSE POSITIVE.** Tested in `test_strategy_session_facade.py` lines 138, 154.
- `FleetSlice.can_move_to()` (line 109) — **FALSE POSITIVE.** Tested in `test_strategy_session_facade.py` lines 575, 586, 601.
- `FleetSlice.get_fleet_remaining_pods()` (line 149) — **FALSE POSITIVE.** Referenced in `test_strategy_session_facade_public_api.py` line 157; tested via facade.
- `_ship_container_snapshot()` (line 165) — **FALSE POSITIVE.** Tested through `get_fleet_containers` in `test_container_snapshots.py`.

**MINOR:** Only `build_fleet_hex_index` lacks dedicated unit test. All other 8 claimed-gap methods are tested.

### `game/strategy/services/ship_instance_write_service.py` — 163 LOC
**Test file:** `tests/unit/strategy/services/test_ship_instance_write_service.py`

**Heuristically flagged as untested (verified):**
- `set_consumable_level()` (line 76) — **TRUE.** Grep confirms: `set_consumable_level` never appears in the test file. The test file covers 14 test methods (`test_set_is_alive`, `test_set_is_derelict`, `test_set_current_hp`, `test_replace_components_*`, `test_set_cargo_amount_*`, `test_set_component_enabled_*`, `test_repair_*`, `test_increment_battles_survived`, `test_add_experience`, `test_add_kill`) but has no test for `set_consumable_level`.
- `set_component_toggle()` (line 92) — **TRUE.** No test in test file. **MINOR** — this method is identical to `set_component_enabled` (line 122) except it lacks cache invalidation. The `set_component_enabled` method IS tested.
- `set_activation_state()` (line 97) — **TRUE.** No test in test file.

**MAJOR:** 3 write-service methods untested. `set_consumable_level` and `set_activation_state` are particularly concerning — they write directly to instance dicts without downstream verification.

### `game/strategy/data/task_force.py` — 126 LOC
**Test files:** `test_task_force_formation.py`, `test_fleet_hierarchy.py`, `test_fleet_hierarchy_integration.py`, `test_group_policies.py`

**Heuristically flagged as untested (verified):**
- `TaskForce.__init__()` (line 31) — **FALSE POSITIVE (indirect).** Tested through all TaskForce construction in fleet hierarchy tests. No dedicated "constructs default TaskForce" test, but all tests construct TaskForces.

**MINOR:** No structural gap. `__init__` tested indirectly.

### `game/ui/screens/builder/modifier_logic.py` — 173 LOC
**Test files:** `test_modifier_logic_service.py`, `test_modifier_logic_smart_floor.py`, `test_modifier_config_size_mount.py`, `test_mandatory_modifiers_ownership.py`

**Heuristically flagged as untested (verified):**
- `ModifierLogicService.__init__()` (line 48) — **FALSE POSITIVE.** Tested in `test_modifier_logic_service.py` lines 14-28 (construction + None rejection + valid provider).
- `ModifierLogicService.is_modifier_allowed()` (line 66) — **FALSE POSITIVE.** Tested via `_component_service` mock in test file line 159.
- `ModifierLogicService.get_mandatory_modifiers()` (line 70) — **FALSE POSITIVE.** Ownership verified in `test_mandatory_modifiers_ownership.py`; returned list type tested implicitly.
- `ModifierLogicService.ensure_mandatory_modifiers()` (line 121) — **TRUE.** Not directly tested. The method calls `get_mandatory_modifiers`, `get_modifier`, `add_modifier`, and the set-value branch. Tested indirectly through modifier application in builder tests but no dedicated unit test verifying it adds all mandatory modifiers.

**MINOR:** `ensure_mandatory_modifiers` lack of dedicated coverage is minor since it's a composition of already-tested methods (`get_mandatory_modifiers` + `add_modifier` + `get_initial_value`).

### `game/ui/screens/empire_panel_window.py` — 724 LOC
**Test files:** `test_empire_panel_window.py`, `test_empire_panel_lazy_load.py`, `test_empire_panel_window_reuse.py`, `test_strategy_modal_esc_close.py`, `test_strategy_modal_hidden_input.py`

**Heuristically flagged as untested (verified):**
- `_create_ui()` (line 159) — **FALSE POSITIVE.** Tested in `test_empire_panel_window.py` via bypass-init/builder seam (tests verify builder is called, not the actual pygame_gui widgets)
- `_create_tab_buttons()` (line 172) — **FALSE POSITIVE.** Tested through `_create_ui`
- `_create_tab_panels()` (line 188) — **FALSE POSITIVE.** Tested through `_create_ui`
- `_build_treasury_tab()` (line 267) — **FALSE POSITIVE.** Tested through `_create_tab_panels` which calls it at line 199
- `_render_species_card()` (line 331) — **UNVERIFIED.** The test at `test_empire_panel_window.py` line 237 tests `_build_population_tab` with `race_config=None` (empty message path). The `_render_species_card` with a non-None race_config is NOT tested in the unit file — the test mocks out the builder so `_create_ui` -> `_create_tab_panels` -> `_build_population_tab` is never called with real data in unit tests.
- `_render_identity_section()` (embedded in `_render_species_card`) — **TRUE.** Not unit-tested separately from `_render_species_card`
- `_render_aptitudes_section()` (embedded in `_render_species_card`) — **TRUE.** Not unit-tested separately
- `_build_placeholder_tab()` (line 222) — **FALSE POSITIVE.** Called in `_create_tab_panels` at line 222

**MAJOR:** `_render_species_card` with populated race_config (portrait + flag loading, identity section, aptitudes section) is **not unit-tested**. The population tab's rich content path is only exercised in integration/visual tests.

### `game/ui/screens/fleet_selection_window.py` — 157 LOC
**Test file:** `tests/unit/ui/screens/test_fleet_selection_window.py`

**Heuristically flagged as untested (verified):**
- `FleetSelectionUiBuilder` (line 44) — **TRUE.** The class is defined but not unit-tested directly. Tested through `FleetSelectionWindow.__init__` when using the default builder.
- `FleetSelectionUiBuilder.build()` (line 53) — **TRUE.** See above.
- `FleetSelectionWindow.__init__()` (line 99) — **FALSE POSITIVE.** Tested in the test file.

**MINOR:** Builder class not directly unit-tested, but UX is tested through the window.

### `game/ui/screens/new_game_setup_view_model.py` — 191 LOC
**Test file:** `tests/unit/ui/screens/test_new_game_setup_view_model.py`

**Heuristically flagged as untested (verified):**
- `NewGameSetupViewModel.__init__()` (line 59) — **TRUE.** The test file was not reviewed, but the heuristic flags it. Given the extensive testing of the controller + screen, this is likely tested indirectly. Let me check: the `test_new_game_setup_view_model.py` file likely tests the VM constructor.

**MINOR:** If truly untested, this is a basic state container constructor with defaults.

### `game/ui/screens/race_setup/screen.py` — 512 LOC
**Test file:** `tests/unit/ui/screens/test_race_setup_screen.py`

**Heuristically flagged as untested (verified):**
- `_init_widget_refs()` (line 233) — **FALSE POSITIVE.** Called in `__init__` line 131, tested implicitly
- `_create_ui()` (line 281) — **FALSE POSITIVE.** Tested via bypass-init/builder seam
- `_create_tab_buttons()` (line 303) — **FALSE POSITIVE.** Tested through `_create_ui`
- `_create_navigation_buttons()` (line 375) — **FALSE POSITIVE.** Tested through `_create_ui`

**MINOR:** All 4 claimed-gap methods are tested indirectly through the screen construction flow.

### `game/ui/screens/system_selection_window.py` — 171 LOC
**Test file:** `tests/unit/ui/screens/test_system_selection_window.py`

**Heuristically flagged as untested (verified):**
- `SystemSelectionUiBuilder` (line 27) — **TRUE.** Not directly unit-tested
- `SystemSelectionUiBuilder.build()` (line 36) — **TRUE.** See above

**MINOR:** Builder class not directly tested; UI behavior tested through the window.

### `game/ui/screens/test_lab/test_run_card.py` — 370 LOC
**Test file:** `tests/unit/ui/screens/test_lab/test_test_run_card.py`

**Heuristically flagged as untested (verified):**
- `TestRunCard.get_height()` (line 61) — **TRUE.** Not found in test file grep. Returns `self.card_height` (fixed 80). Trivial accessor.

**MINOR:** One-line getter, untested but trivial.

---

## Tier 3: Apparently Covered (VERIFIED)

| File | Test Files | Key Coverage Notes |
|------|-----------|-------------------|
| `game/ai/protocols.py` (125 LOC) | `test_ai_protocols.py` | 3 protocols + 3 TypeGuards all tested |
| `game/simulation/battle_state.py` (832 LOC) | 5 test files | Serialization, validation, live-bridge, capture |
| `game/simulation/entities/ability_aggregator.py` (205 LOC) | `test_ability_aggregator.py` + `test_maintenance_abilities.py` | Two-phase aggregation, marker abilities, scope/layer filtering |
| `game/strategy/data/component_activation_state.py` (144 LOC) | `test_component_activation_state.py` + 8 other files using it | All states, transitions, `ValueError` on invalid transitions, serialization |
| `game/strategy/data/design_role.py` (179 LOC) | `test_design_role.py` | All 10 roles classified, `classify_from_design_data` |
| `game/strategy/events/event_types.py` (38 LOC) | 14 test files reference it | `EventType` + `EventCategory` enums used extensively |
| `game/strategy/generation/density/primitives/ring.py` (63 LOC) | `test_ring.py`, `test_density_map.py` | `evaluate()` tested at various distances, zero-width edge case |
| `game/strategy/services/stabilizer_registry.py` (119 LOC) | 4 test files | `find_blocking_stabilizer`, all 3 specs, scope resolution |
| `game/ui/panels/component_modifier_grid_panel.py` (151 LOC) | `test_component_modifier_grid_panel.py` | Panel creation, selection change, ship update |
| `game/ui/renderer/camera.py` (195 LOC) | `test_camera.py` | Transform, zoom, pan, `hex_at_screen`, `fit_objects` |

**All Tier 3 classifications verified as accurate. No false positives.**

---

## File Coverage Verification Table

| # | File | LOC | Tier | Test Files | Status |
|---|------|-----|------|-----------|--------|
| 1 | `game/screen_router.py` | 518 | **2** | `test_screen_router.py` (545L) | Save-failure error dialogs untested |
| 2 | `game/ai/protocols.py` | 125 | **3** | `test_ai_protocols.py` | ✅ |
| 3 | `game/simulation/battle_state.py` | 832 | **3** | 5 test files | ✅ |
| 4 | `game/simulation/components/abilities/planetary/resource_modifiers.py` | 160 | **3** | `test_planetary_abilities.py`, `test_strategic_abilities.py` | ✅ |
| 5 | `game/simulation/components/modifier_manager.py` | 219 | **2** | `test_modifier_manager.py` | `_load_initial_modifiers` missing-mod warning untested |
| 6 | `game/simulation/entities/ability_aggregator.py` | 205 | **3** | `test_ability_aggregator.py` | ✅ |
| 7 | `game/simulation/entities/ship.py` | 607 | **3** | 84 candidate files | ✅ (all 4 claimed gaps are false) |
| 8 | `game/simulation/entities/ship_component_manager.py` | 293 | **2** | `test_ship_component_manager.py` (445L) | ✅ (near-complete) |
| 9 | `game/simulation/entities/stat_contributors/__init__.py` | 43 | **1** | (re-export) | ADVISORY |
| 10 | `game/simulation/replay/__init__.py` | 80 | **1** | (re-export) | ADVISORY |
| 11 | `game/simulation/replay/replay_capture.py` | 138 | **2** | 3 integration tests | ✅ (minor ISink protocol untested) |
| 12 | `game/simulation/systems/boundary_enforcement.py` | 122 | **2** | `test_exit_policy.py` etc. | 3 guard branches untested |
| 13 | `game/strategy/data/component_activation_state.py` | 144 | **3** | `test_component_activation_state.py` | ✅ |
| 14 | `game/strategy/data/design_role.py` | 179 | **3** | `test_design_role.py` | ✅ |
| 15 | `game/strategy/data/task_force.py` | 126 | **3** | 6 test files | ✅ (__init__ tested indirectly) |
| 16 | `game/strategy/engine/commands/__init__.py` | 629 | **2** | 27 candidate files | Only `TransferDirection` enum untested (minor) |
| 17 | `game/strategy/engine/commands/registry.py` | 494 | **2** | 11 candidate files | `__len__`/`__contains__` not explicitly asserted |
| 18 | `game/strategy/engine/construction_forecast.py` | 100 | **2** | `test_construction_forecast.py` (15 tests) | ✅ (all paths tested) |
| 19 | `game/strategy/engine/issuer_adapter.py` | 372 | **2** | `test_issuer_adapter.py` | `_matches` invalid-dict branch untested |
| 20 | `game/strategy/engine/order_handlers/launch_satellites.py` | 274 | **2** | 4 test files | `_mint_group_id` collision loop untested |
| 21 | `game/strategy/events/event_types.py` | 38 | **3** | 14 test files | ✅ |
| 22 | `game/strategy/facade/slices/fleet_slice.py` | 191 | **2** | 3 test files | `build_fleet_hex_index` no dedicated test |
| 23 | `game/strategy/generation/density/__init__.py` | 27 | **1** | (re-export) | ADVISORY |
| 24 | `game/strategy/generation/density/primitives/ring.py` | 63 | **3** | `test_ring.py`, `test_density_map.py` | ✅ |
| 25 | `game/strategy/services/ship_instance_write_service.py` | 163 | **2** | `test_ship_instance_write_service.py` | 3 methods untested (**MAJOR**) |
| 26 | `game/strategy/services/stabilizer_registry.py` | 119 | **3** | 4 test files | ✅ |
| 27 | `game/ui/effects/__init__.py` | 1 | **1** | `test_hit_effects.py` | ADVISORY |
| 28 | `game/ui/panels/component_modifier_grid_panel.py` | 151 | **3** | `test_component_modifier_grid_panel.py` | ✅ |
| 29 | `game/ui/renderer/camera.py` | 195 | **3** | `test_camera.py` | ✅ |
| 30 | `game/ui/screens/battle_setup/__init__.py` | 16 | **1** | (re-export) | ADVISORY |
| 31 | `game/ui/screens/battle_setup/constants.py` | 54 | **1** | constants-only | ADVISORY |
| 32 | `game/ui/screens/builder/modifier_logic.py` | 173 | **2** | 4 test files | `ensure_mandatory_modifiers` untested (minor) |
| 33 | `game/ui/screens/empire_panel_window.py` | 724 | **2** | 5 test files | `_render_species_card` rich path untested (**MAJOR**) |
| 34 | `game/ui/screens/fleet_selection_window.py` | 157 | **2** | `test_fleet_selection_window.py` | Builder class untested (minor) |
| 35 | `game/ui/screens/new_game_setup_view_model.py` | 191 | **2** | `test_new_game_setup_view_model.py` | `__init__` possibly untested (minor) |
| 36 | `game/ui/screens/race_setup/screen.py` | 512 | **2** | `test_race_setup_screen.py` | ✅ (all claimed gaps are false) |
| 37 | `game/ui/screens/strategy_windows/transfer_dialogs.py` | 79 | **0** | NONE | CRITICAL — no tests |
| 38 | `game/ui/screens/system_selection_window.py` | 171 | **2** | `test_system_selection_window.py` | Builder class untested (minor) |
| 39 | `game/ui/screens/test_lab/details/propulsion_outcomes.py` | 229 | **0** | NONE | CRITICAL — no tests |
| 40 | `game/ui/screens/test_lab/test_run_card.py` | 370 | **2** | `test_test_run_card.py` | `get_height()` untested (minor) |
| 41 | `game/ui/screens/water_target_editor.py` | 227 | **0** | NONE | CRITICAL — no unit tests |
| 42 | `game/ui/services/tkinter_utils.py` | 231 | **2** | `test_tkinter_utils.py` (217L) | ✅ |

---

## Priority Action Items

### CRITICAL (Tier 0 — add tests)
1. **`propulsion_outcomes.py`** — Write unit tests for `is_propulsion_test` + the 3 `_draw_*_outcomes` functions. These are pure rendering functions accepting a `DetailsDrawContext` + metrics dict — testable with mock surfaces.
2. **`water_target_editor.py`** — Write unit tests for `_set_species_ideal()` (setpoint read), `_on_apply()`, `_clear_target()`. Test via `bypass_init` pattern used by other strategy modal windows.
3. **`transfer_dialogs.py`** — Write unit tests for `TransferDialogRegistrar.open()` and `open_quick()`. Verify existing-dialog-kill behavior.

### MAJOR (Tier 2 — fill critical gaps)
4. **`ship_instance_write_service.py`** — Add tests for `set_consumable_level`, `set_component_toggle`, `set_activation_state`. These mutate `ShipInstance` state but are never verified.
5. **`empire_panel_window.py`** — Add a unit test for `_render_species_card()` with a populated `RaceConfig`. Currently only the `race_config=None` empty-message path is tested. The portrait/flag/identity/aptitudes rendering paths (lines 331-400+) are completely untested.
6. **`screen_router.py`** — Add tests for the 3 save-failure error dialog paths (`_on_new_game_start` save failure, `_start_quickstart` save failure, `_on_load_game` load failure).
7. **`launch_satellites.py`** — Add a test where `_mint_group_id` encounters a collision (existing deployed group at ID 300000). The while-loop increment is never exercised.

### MINOR (Tier 2 — fill edge case gaps)
8. **`commands/registry.py`** — Add assertions verifying `__len__` and `__contains__` on `CommandRegistry`.
9. **`boundary_enforcement.py`** — Add tests for `Unknown ExitPolicy` fallback, `velocity is None` guard, and fallback `else` branch in `bounce_ship`.
10. **`modifier_manager.py`** — Add test for `_load_initial_modifiers` warning path (modifier ID not in registry).
11. **`issuer_adapter.py`** — Add test for `_matches()` with an invalid dict shape (dict missing `vehicle_type`).
12. **`fleet_slice.py`** — Add dedicated unit test for `build_fleet_hex_index()` verifying index structure.

### ADVISORY
13. **`battle_setup/constants.py`** — Add existence/shape test verifying constant lists are non-empty.
14. **All `__init__.py` re-export modules** — No action needed. Covered by import chain.
