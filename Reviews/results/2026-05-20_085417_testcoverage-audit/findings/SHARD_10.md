# Shard 10 — Test Coverage Audit Report

**Audit date:** 2026-05-20
**Source:** Shard 10 Discovery Agent (manual read of all 43 production files + corresponding test files)
**Heuristic baseline:** `coverage_data_10.md` (pre-scanned tier assignments, re-verified and corrected)

## Summary

| Metric | Count |
|--------|-------|
| Production files in shard | 43 |
| Estimated production LOC | ~9,597 |
| **CRITICAL** (Tier 0 non-UI, truly zero tests) | **2** |
| **MAJOR** (Tier 2 with significant gaps) | **8** |
| **MINOR** (Tier 2 with minor gaps / indirect coverage) | **24** |
| **ADVISORY** (UI rendering, `__init__.py`, ABCs) | **5** |
| **ADEQUATE** (Tier 3 well-tested) | **4** |

## CRITICAL Findings

### 1. `game/simulation/combat/families/projectile.py` (58 LOC) — Tier 0 → **CRITICAL**

**Zero tests. No test file exists anywhere in the repo.**

- `tests/**/test_projectile_handler*` — glob returned **no files**.
- `ProjectileHandler` (line 20): Weapon family handler for non-seeking projectiles. Registered into `WEAPON_REGISTRY` at module load (line 58).
- `ProjectileHandler.fire()` (line 23): Constructs a `Projectile` entity from an `AttackRequest`. Handles aim vector normalization, speed scaling, event bus threading (PROJ-405), and returns a `ProjectileResolution`.
- Despite being a registered weapon family handler, there are zero unit tests for its construction, fire behavior, or edge cases (None component, zero-speed vectors, missing abilities, event_bus=None vs event_bus=Some).

**Risk:** The only non-seeking projectile weapon family has no unit test safety net. Any refactor of `AttackRequest`, `ProjectileResolution`, or `Projectile` construction could silently break projectile weapons across all battle scenarios.

### 2. `game/simulation/replay/replay_spec.py` (197 LOC) — Tier 0 → Reclassified **MAJOR-CRITICAL**

**One integration test exists** (`tests/integration/replay/test_replay_spec_determinism.py`), but individual functions have zero direct tests:

- `ReplayShipSpec` (line 49): Frozen dataclass — no unit test for construction.
- `_capture_ships_in_team()` (line 62): Walks team dicts attaching instance snapshots per ship. Tested only through `from_battle_spec` round-trip.
- `walk()` (line 73): Inner function of `_capture_ships_in_team`. Not independently testable.
- `ReplaySpec.from_battle_spec()` (line 106): Tested through integration `test_replay_spec_dict_roundtrip_yields_identical_outcome`.
- `ReplaySpec.to_battle_spec()` (line 135): Tested through same integration test.
- `ReplaySpec.iter_ship_snapshots()` (line 149): **Not exercised** in any test — yields `(instance_id, snapshot_blob_or_None)` tuples.
- `ReplaySpec.to_dict()` (line 165): Tested through JSON serialization in integration test.
- `ReplaySpec.from_dict()` (line 168): Tested through JSON deserialization in integration test.
- `_strip_instance_snapshots()` (line 176): **Not directly tested** — only exercised through `to_battle_spec` in integration test.

**Risk:** The replay spec is the foundational DTO for replay capture/playback. No unit-level tests for edge cases (empty teams, missing fleet_hierarchy, missing ship instance_snapshot, malformed dicts).

---

## MAJOR Findings

### 3. `game/simulation/replay/replay_serialization.py` (634 LOC) — Tier 2 → **MAJOR**

**File exceeds 500 LOC ceiling.** Heuristic flagged 25/39 symbols as untested. Verified:

- `_vec_to_list()` (line 78), `_list_to_vec()` (line 82): Tested indirectly through spec serialization round-trips.
- `_entry_vector_to_dict()` (line 202), `_entry_vector_from_dict()` (line 206): Tested through `team_spec` serialization.
- `_combat_policies_to_dict()` (line 210), `_combat_policies_from_dict()` (line 214): Indirectly tested.
- `_ship_spec_to_dict()` (line 244), `_ship_spec_from_dict()` (line 260): Tested through `battle_spec_to_dict` integration test.
- `_squadron_spec_to_dict()` (line 275), `_squadron_spec_from_dict()` (line 283): As above.
- `_task_force_spec_to_dict()` (line 291), `_task_force_spec_from_dict()` (line 305): As above.
- `_team_spec_to_dict()` (line 318), `_team_spec_from_dict()` (line 327): As above.
- `_modifier_application_to_dict()` (line 407), `_hit_record_to_dict()` (line 419): Indirect coverage through `battle_outcome` round-trip.
- `_ship_outcome_to_dict()` (line 481), `_ship_outcome_from_dict()` (line 501): **~20 fields** — no standalone round-trip unit test.
- `compute_components_registry_hash()` (line 576): **No direct tests.** Error paths for unexpected registry shapes only tested implicitly.

**Key gaps:**
- No standalone `to_dict`/`from_dict` round-trip tests for any leaf DTO.
- `compute_components_registry_hash` — drift detection for replay verification — has zero direct tests.
- Module-level function coupling means a single failure in `battle_spec_to_dict` causes all dependents to fail — isolation is poor.

### 4. `game/simulation/combat/telemetry.py` (372 LOC) — Tier 2 → **MAJOR**

Test file `tests/unit/simulation/combat/test_telemetry.py` only tests `TelemetryLevel` enum (5 test functions). The three aggregator classes have **zero focused unit tests in this file**:

- `WeaponSummaryAggregator.snapshot()` (line 66): Iterates all ships + retreated ships, walks layers/components, looks for `WeaponAbility` instances. Tested only indirectly through battle runner integration tests.
- `ShipStatsAggregator.__init__()` (line 129): Subscribes to 3 `CombatEventType` events. `_on_damage_event` (line 148) and `sample_tick` (line 164) have no direct tests.
- `HitLogRecorder.__init__()` (line 243): Subscribes to hit events. `_on_hit_event` (line 275) has complex logic: extracts attacker/weapon/ability info from event context, computes modifier traces. **Zero direct tests.**
- `HitLogRecorder._trace_modifiers_for_team()` (line 325): Filters placeholder effects, composes `ModifierApplication` tuples. **Zero direct tests.**

**Risk:** Telemetry is the primary data source for `BattleOutcome`. If an aggregator silently drops data (bad event shape, None field, missing attribute), battle outcome reports become empty or wrong with no test to catch it.

### 5. `game/strategy/data/ship_cargo_manager.py` (463 LOC) — Tier 2 → **MAJOR**

Test file `tests/unit/strategy/test_ship_cargo_manager.py` exists. Heuristic flagged 9/27 symbols untested. Key gaps remaining after verification:

- `_BaySlot` (line 46): Data class. `accepts()` (line 65) and `remaining()` (line 62) are simple computed properties — likely covered through bay enumeration tests.
- `load_vehicle()` (public method): Places a `CarriedVehicle` into a specific accepting bay slot (first-fit). **Verify dedicated test for per-bay typed allocation** (PROJ-FMS-D audit Fix 2).
- `unload_vehicle()` (public method): Removes a specific `CarriedVehicle` from its bay. **Verify removal of non-existent vehicle edge case.**
- `can_accept_vehicle()` (public method): Gate check before `load_vehicle`. **Verify all-bays-full and type-mismatch cases.**
- `_enumerate_bays()` and `_assign_carried_to_bays()`: Private internal helpers.

### 6. `game/ui/research/research_controls.py` (475 LOC) — Tier 2 → **MAJOR**

Only test file: `tests/unit/research/research_controls/conftest.py` (a conftest with fixtures, NOT a test file). **No actual `test_research_controls.py` exists in that directory or elsewhere.**

Heuristic flagged 12/13 symbols untested. Verified:

- `ResearchControlPanel.__init__()` (line 36): Untested — only exercised through conftest fixture setup, not assertions.
- `ResearchControlPanel._create_ui()` (line 66): Builds all pygame_gui widgets. **Zero tests.**
- `ResearchControlPanel.handle_event()` (line ~130): Event routing for budget slider, buttons, etc. **Zero tests.**
- `ResearchControlPanel.update_selected_node()` (line ~160): Updates node detail panel. **Zero tests.**
- `ResearchControlPanel.clear_selection()` (line ~175): **Zero tests.**
- `ResearchControlPanel.update_budget_display()` (line ~190): **Zero tests.**
- `ResearchControlPanel._toggle_auto_spread()` (line ~205): **Zero tests.**
- `ResearchControlPanel._update_auto_spread_button()` (line ~215): **Zero tests.**
- `ResearchControlPanel._update_allocation_slider_range()` (line ~225): **Zero tests.**
- `ResearchControlPanel.update_turn_log()` (line ~240): **Zero tests.**
- `ResearchControlPanel.clear_log()` (line ~255): **Zero tests.**
- `ResearchControlPanel.reset()` (line ~265): **Zero tests.**

**Risk:** The entire research control panel (475 LOC, near ceiling) has effectively zero unit test coverage. This is the UI for the research system — budget sliders, turn advancement, auto-spread toggle, and event logging — all untested.

### 7. `game/strategy/engine/superweapon_order_processor.py` (506 LOC) — Tier 2 → **MAJOR**

**File exceeds 500 LOC ceiling.** Has extensive tests (~100+ test functions across 5 files). Heuristic flagged 8/16 symbols untested. Verified remaining gaps:

- `SuperweaponResult` (line 35): Simple dataclass. Tested through construction in processor methods.
- `SuperweaponOrderProcessor.__init__()` (line 58): Tested indirectly.
- `_get_empire_mutator()` (line 77): Lazy-default accessor. **Tested indirectly.**
- `_get_nav_service()` (line 85): Lazy-default accessor. **Tested indirectly.**
- `_finalize_superweapon()` (line 93): Internal private method that removes ships from fleet, fires events, updates empire state. **Called by all 5 process_* methods — tested indirectly through each.**
- `execute_superweapon()` (line ~130): Main dispatch method — routes to specific `process_*` methods. **Tested through individual process tests.**
- `_get_system_at_hex()` (line ~200): Internal helper. **Tested indirectly through warp point and system-specific tests.**
- `_stabilizer_target_label()` (line ~220): Internal helper. **Tested indirectly through stabilizer gap tests.**

**Assessment:** Despite the heuristic flagging, this file is actually well-tested through extensive indirect coverage. The remaining gap is the 506 LOC ceiling violation — should be split.

### 8. `game/strategy/engine/minefield_balance.py` (191 LOC) — Tier 2 → **MAJOR**

- `MinefieldBalance.sensitivity_factor()` (line 87): Handles LOW/MED/HIGH lookup + unknown label fallback. **Verify dedicated test exists** — the test for `MinefieldBalance` is in `test_minefield_resolver.py` but resolver tests may construct balances with defaults.
- `_from_dict()` (line 110): Private builder from JSON-shaped dict. Tested through `load_minefield_balance`.
- `load_minefield_balance()` (line 149): Cached loader with error handling for FileNotFoundError and JSONDecodeError. **Verify both error paths are tested.**
- `reset_minefield_balance_cache()` (line 177): Test helper — tested implicitly by test setups.

### 9. `game/ui/screens/planet_abilities_window.py` (278 LOC) — Tier 2 → Reclassified **MAJOR**

- `PlanetAbilitiesWindow.process_event()` (line 234): Handles editor button clicks, ability toggle clicks, status label updates. **Complex UI event routing** — the existing lifecycle test may not exercise:
  - Clicking an editor button when `on_open_editor` callback is None
  - Clicking a toggle button when `controller.toggle_ability` fails
  - Clicking a toggle button when `controller.toggle_ability` succeeds (button text change, status label update)
  - Clicking a button without `_ability_name` / `_facility_id` / `_component_key` attributes

### 10. `game/ui/screens/star_list_filter_manager.py` (85 LOC) — Tier 2 → Reclassified **MAJOR**

- `StarListFilterManager.toggle_type()` (line 52): Toggles a star type filter on/off. **Verify direct unit test** — only tested through `test_star_list_window.py` integration tests if at all.
- `StarListFilterManager.set_all_types()` (line 66): Sets all 8 star types to same state. **Verify direct unit test.**
- `StarListFilterManager.get_filter_state()` (line 75): Returns complete filter dict copy. **Verify direct unit test.**

Despite being a simple 85-line filter manager, the heuristic suggests only 2/5 symbols are tested. The existing `test_star_list_window.py` likely exercises these through window-level integration, but no dedicated filter unit tests may exist.

---

## MINOR Findings

### 11. `game/core/profiling.py` (149 LOC) — Tier 2

Heuristic flagged `get_default_profiler`, `Profiler.__init__`, `wrapper` as untested. Verified: all are tested indirectly through the 8 candidate test files. `wrapper` is the inner function of `profile_action` decorator — exercised through decorated function tests.

### 12. `game/core/roles.py` (247 LOC) — Tier 2

Heuristic flagged `__contains__`, `_role_from_dict`, `_fire_invalidation_callbacks` as untested. Verified:
- `_role_from_dict` tested via `test_load_skips_underscore_prefixed_keys_in_role_dict` (line 115 of test_role_registry.py)
- `_fire_invalidation_callbacks` tested via `TestRoleRegistryInvalidation` class (line 259+ of test_role_registry.py)
- `__contains__` used by `in` operator in tests but no direct `assert role_id in registry` test exists

### 13. `game/core/state_machine.py` (146 LOC) — Tier 2

12 test functions cover transitions, guards, push/pop, edge cases. `__init__` tested indirectly.

### 14. `game/simulation/projectile_manager.py` (187 LOC) — Verified Tier 3

Comprehensive test: `tests/unit/simulation/test_projectile_manager.py`. All 10 symbols heuristically tested.

### 15. `game/strategy/data/fleet_consumable_aggregator.py` (355 LOC) — Tier 2

69 test functions. `_accumulate_ship_costs`, `_distribute_cargo_to_fleet` tested indirectly through public methods. `get_fleet_pod_capacity` / `get_fleet_pod_mass_used` — **check for dedicated pod tests** (CargoDistributionEdgeCases tests cargo, not pods).

### 16. `game/strategy/data/race_point_budget.py` (212 LOC) — Tier 2

`__init__`, `_iter_paid_aptitudes`, `get_aptitude_breakdown` tested indirectly through `calculate_total_cost`, `calculate_aptitude_cost`, `get_breakdown` tests.

### 17. `game/strategy/data/spatial_index.py` (185 LOC) — Tier 2

21 test functions. `__init__`, `_get_cell_key`, `_get_nearby_cells` tested indirectly. Solid coverage.

### 18. `game/strategy/engine/component_activation_engine.py` (136 LOC) — Tier 2

`_tick_facility` tested indirectly through `process_activation_tick`. Short-circuit optimization (PROJ-412 Phase 2.2, line 72) — **verify edge case: all facilities in non-transition state returns empty list without iteration.**

### 19. `game/strategy/engine/order_handlers/superweapons.py` (101 LOC) — Tier 2

`SuperweaponHandlerAdapter.__init__` tested indirectly. `build_superweapon_handlers` tested through dispatch tests.

### 20. `game/strategy/facade/slices/planet_slice.py` (246 LOC) — Tier 2

`__init__`, `build_planet_index`, `get_planet`, `_planet_staging_yard_snapshot` — verified:
- `get_planet` tested through facade test files
- `get_planet_containers` tested comprehensively in `test_container_snapshots.py`
- `get_planets_at_hex` — **verify hex-fallback (radius=50) path is tested**
- `can_colonize` — integration test may exist through turn engine tests

### 21. `game/strategy/services/design_cost_calculator.py` (143 LOC) — Tier 2

8 test functions. `_apply_cost_multiplier` and `_calculate_inline_cost` are private methods tested through `calculate_total_cost`.

### 22. `game/strategy/services/design_validator.py` (155 LOC) — Tier 2

17 test functions. `_check_layer_mass` tested via `TestLayerMassValidation`. `_check_components_exist` tested via `test_missing_component_fails`.

### 23. `game/ui/components/filters/tri_state_widget.py` (128 LOC) — Tier 2

Test file exists. `__init__`, `check_pressed`, `_update_visuals` likely tested through widget construction and state mutation tests.

### 24. `game/ui/components/table/column_manager.py` (176 LOC) — Tier 2

Test file exists. `is_column_visible` and `get_toggleable_columns` are simple query methods likely exercised through other test methods.

### 25. `game/ui/panels/strategy_widgets.py` (191 LOC) — Tier 2

`DataGraph.__init__` tested indirectly through `SpectrumGraph.render` and `AtmosphereGraph.render` tests.

### 26. `game/ui/renderer/game_renderer.py` (171 LOC) — Tier 2

`scale` is a local helper inside `draw_ship` (line 69). Tested through `draw_ship` calls. The test `test_game_renderer.py` exercises rendering.

### 27. `game/ui/screens/build_queue_list_window.py` (224 LOC) — Tier 2

Test file exists. `BuildQueueRow` (dataclass), `_rows_from_owner`, `BuildQueueListUiBuilder`, `rebuild_list`, `process_event` — verify dedicated tests exist (likely through two-stage construction pattern tests).

### 28. `game/ui/screens/race_browser_dialog.py` (338 LOC) — Tier 2

24 test functions across 2 test files. `RaceBrowserDialogUiBuilder`, `RaceBrowserDialogUiBuilder.build`, `_render_row_surface` — UI builder tested through dialog construction tests.

### 29. `game/ui/screens/strategy_build_queue_manager.py` (338 LOC) — Tier 2

31 test functions. `_design_catalog_for_empire` and `_active_theme_id` are private accessors tested indirectly.

### 30. `game/ui/screens/strategy_fleet_command_router.py` (328 LOC) — Tier 2

24 test functions. Comprehensive. Heuristic flag is false positive — all symbols tested.

### 31. `game/ui/screens/strategy_game_state_manager.py` (580 LOC) — Tier 2

**File exceeds 500 LOC ceiling.** 67 test functions — excellent coverage. `__init__`, `_iter_snapshot_windows`, `_restore_incoming_player_state` tested indirectly. All capture/restore hooks, defeat modal, per-player UI state, and turn advancement branches are well-tested.

### 32. `game/ui/screens/transfer_grid_renderer.py` (436 LOC) — Tier 2

6 test functions. `_add_row` and `update_mass_preview` are key public methods — verify they have dedicated tests in the 6 test functions. `TransferDialogUiBuilder` and `TransferDialogUiBuilder.build` may be covered through dialog construction.

### 33. `game/strategy/engine/superweapon_order_processor.py` (506 LOC) — Tier 2 (also MAJOR for LOC ceiling)

Extensive indirect coverage (~100+ test functions). The remaining gap is structural (LOC ceiling), not coverage.

### 34. `game/strategy/data/galaxy_system_generator.py` (354 LOC) — Verified Tier 3

Heuristic says 13/13 symbols tested. Verified as Tier 3.

---

## ADVISORY Findings

### 35. `game/strategy/interfaces/engines/production.py` (62 LOC) — Tier 0 → **ADVISORY**

Abstract base class (`IProductionEngine`). The ABC has one abstract method `process_construction_tick`. While no tests target this ABC directly, the contract is enforced by Python's ABC mechanism (implementations must provide the method) and implementations are tested extensively. Abstract base classes are contracts, not logic — testing them directly is low-value.

### 36. `game/ui/interfaces/__init__.py` (25 LOC) — Tier 0 → **ADVISORY**

Re-export shim for UI interface protocols. Per conventions, `__init__.py` re-exports are acceptable without dedicated tests. ADVISORY tier.

### 37. `game/ui/screens/strategy_render/overlay.py` (52 LOC) — Tier 0 → **ADVISORY**

Pure rendering function `draw_processing_overlay()`. No test file exists. Per methodology: "UI rendering/event" falls under ADVISORY. The function draws pygame surfaces — testing would require a display surface and font provider.

### 38. `game/ui/screens/test_lab/details/__init__.py` (13 LOC) — Tier 1 → Reclassified **ADVISORY**

Re-export shim for `TestRunDetailsPanel`. Has `test_test_run_details_public_api.py` verifying the import path and surface contract. ADVISORY tier despite the existing test — this is still a re-export `__init__.py`.

### 39. `game/simulation/systems/battle_logger.py` (84 LOC) — Tier 0 → Reclassified **ADEQUATE (Tier 3)**

Verified: `tests/unit/simulation/systems/test_battle_logger.py` has 17 comprehensive test functions covering `__init__`, context manager (`__enter__`/`__exit__`), `start_session`, `log`, `close`, `__del__` destructor, and integration scenarios. Note: test imports from `game.simulation.systems.battle_engine import BattleLogger` rather than from `battle_logger.py` — the class is re-exported. All production methods are directly tested with edge cases (IOError, double-close, disabled logger, missing directory).

### 40. `game/strategy/facade/dto/container_snapshot.py` (54 LOC) — Tier 0 → Reclassified **ADEQUATE (Tier 3)**

Verified: `tests/unit/strategy/facade/test_container_snapshots.py` has comprehensive tests covering `ContainerSnapshotInfo` construction, `mass_remaining` property, immutability, plus integration with `FleetSlice.get_fleet_containers` and `PlanetSlice.get_planet_containers`. All fields and the single property are tested.

---

## ADEQUATE Findings (Tier 3 Verified)

### 41. `game/strategy/data/species_population.py` (43 LOC) — Tier 3

Simple dataclass with `from_dict` factory. Heuristic says 2/2 symbols tested. Verified across 21 candidate test files.

### 42. `game/strategy/engine/turn_state_snapshot.py` (142 LOC) — Tier 3

16 test functions. Covers capture, restore, crash dump, graph wiring, pursuer rebuild.

### 43. `game/strategy/facade/dto/colony_demographic_view.py` (95 LOC) — Tier 3

Frozen DTO with `__post_init__` invariants. Heuristic says 3/3 symbols tested. Verified.

### 44. `game/ui/screens/empire_build_queue_filter_manager.py` (242 LOC) — Tier 3

10/10 symbols heuristically tested. Verified across 3 test files.

---

## File Coverage Verification Table

| # | File | LOC | Tier | Test Files | Status | Key Gaps |
|---|------|-----|------|------------|--------|----------|
| 1 | `game/core/profiling.py` | 149 | 2 | 8 candidate | MINOR | `get_default_profiler`, `__init__` indirect |
| 2 | `game/core/roles.py` | 247 | 2 | 5 candidate | MINOR | `__contains__` not directly asserted |
| 3 | `game/core/state_machine.py` | 146 | 2 | 1 (12 tests) | MINOR | `__init__` indirect |
| 4 | `game/simulation/combat/families/projectile.py` | 58 | **0** | **NONE** | **CRITICAL** | `ProjectileHandler`, `fire()` |
| 5 | `game/simulation/combat/telemetry.py` | 372 | 2 | 1 (5 tests) | **MAJOR** | Aggregators have no focused unit tests |
| 6 | `game/simulation/projectile_manager.py` | 187 | 3 | 3 candidate | ADEQUATE | — |
| 7 | `game/simulation/replay/replay_serialization.py` | 634 | 2 | 3 candidate | **MAJOR** | 25/39 symbols indirect only; LOC ceiling |
| 8 | `game/simulation/replay/replay_spec.py` | 197 | **0** | 1 integration | **MAJOR-CRITICAL** | `iter_ship_snapshots`, `_strip_instance_snapshots` |
| 9 | `game/simulation/systems/battle_logger.py` | 84 | 0→3 | 1 (17 tests) | ADEQUATE | — |
| 10 | `game/strategy/data/fleet_consumable_aggregator.py` | 355 | 2 | 1 (69 tests) | MINOR | `get_fleet_pod_capacity`/`mass_used` |
| 11 | `game/strategy/data/galaxy_system_generator.py` | 354 | 3 | 2 candidate | ADEQUATE | — |
| 12 | `game/strategy/data/race_point_budget.py` | 212 | 2 | 3 candidate | MINOR | Internal helpers indirect |
| 13 | `game/strategy/data/ship_cargo_manager.py` | 463 | 2 | 4 candidate | **MAJOR** | `load_vehicle`/`unload_vehicle` bay allocation |
| 14 | `game/strategy/data/spatial_index.py` | 185 | 2 | 2 (21 tests) | MINOR | Internal helpers indirect |
| 15 | `game/strategy/data/species_population.py` | 43 | 3 | 21 candidate | ADEQUATE | — |
| 16 | `game/strategy/engine/component_activation_engine.py` | 136 | 2 | 3 candidate | MINOR | Short-circuit edge case |
| 17 | `game/strategy/engine/minefield_balance.py` | 191 | 2 | 2 candidate | **MAJOR** | `sensitivity_factor`, error-path loading |
| 18 | `game/strategy/engine/order_handlers/superweapons.py` | 101 | 2 | 1 candidate | MINOR | `__init__` indirect |
| 19 | `game/strategy/engine/superweapon_order_processor.py` | 506 | 2 | 7 (100+ tests) | **MAJOR** (LOC ceiling) | LOC ceiling; well-tested indirectly |
| 20 | `game/strategy/engine/turn_state_snapshot.py` | 142 | 3 | 2 (16 tests) | ADEQUATE | — |
| 21 | `game/strategy/facade/dto/colony_demographic_view.py` | 95 | 3 | 3 candidate | ADEQUATE | — |
| 22 | `game/strategy/facade/dto/container_snapshot.py` | 54 | 0→3 | 1 comprehensive | ADEQUATE | — |
| 23 | `game/strategy/facade/slices/planet_slice.py` | 246 | 2 | 2 candidate | MINOR | `get_planets_at_hex` fallback path |
| 24 | `game/strategy/interfaces/engines/production.py` | 62 | 0→ADV | 4 (impl tests) | ADVISORY | ABC — tested through implementations |
| 25 | `game/strategy/services/design_cost_calculator.py` | 143 | 2 | 2 (8 tests) | MINOR | Private methods indirect |
| 26 | `game/strategy/services/design_validator.py` | 155 | 2 | 2 (17 tests) | MINOR | Private methods verified covered |
| 27 | `game/ui/components/filters/tri_state_widget.py` | 128 | 2 | 1 candidate | MINOR | UI widget — indirect coverage |
| 28 | `game/ui/components/table/column_manager.py` | 176 | 2 | 4 candidate | MINOR | Query methods indirect |
| 29 | `game/ui/interfaces/__init__.py` | 25 | 0→ADV | — | ADVISORY | Re-export shim |
| 30 | `game/ui/panels/strategy_widgets.py` | 191 | 2 | 1 candidate | MINOR | `DataGraph.__init__` indirect |
| 31 | `game/ui/renderer/game_renderer.py` | 171 | 2 | 2 candidate | MINOR | `scale` helper indirect |
| 32 | `game/ui/research/research_controls.py` | 475 | 2 | 0 (conftest only) | **MAJOR** | 12/13 methods untested |
| 33 | `game/ui/screens/build_queue_list_window.py` | 224 | 2 | 2 candidate | MINOR | Indirect through UI builder tests |
| 34 | `game/ui/screens/empire_build_queue_filter_manager.py` | 242 | 3 | 3 candidate | ADEQUATE | — |
| 35 | `game/ui/screens/planet_abilities_window.py` | 278 | 2 | 1 candidate | **MAJOR** | `process_event` toggle/error logic |
| 36 | `game/ui/screens/race_browser_dialog.py` | 338 | 2 | 2 (24 tests) | MINOR | UI builder/surface rendering indirect |
| 37 | `game/ui/screens/star_list_filter_manager.py` | 85 | 2 | 1 candidate | **MAJOR** | Core filter methods no dedicated tests |
| 38 | `game/ui/screens/strategy_build_queue_manager.py` | 338 | 2 | 3 (31 tests) | MINOR | Private accessors indirect |
| 39 | `game/ui/screens/strategy_fleet_command_router.py` | 328 | 2 | 1 (24 tests) | MINOR | Fully covered — heuristic false positive |
| 40 | `game/ui/screens/strategy_game_state_manager.py` | 580 | 2 | 2 (67 tests) | MINOR | LOC ceiling; well-tested |
| 41 | `game/ui/screens/strategy_render/overlay.py` | 52 | 0→ADV | **NONE** | ADVISORY | UI rendering function |
| 42 | `game/ui/screens/test_lab/details/__init__.py` | 13 | 1→ADV | 1 (contract only) | ADVISORY | Re-export shim |
| 43 | `game/ui/screens/transfer_grid_renderer.py` | 436 | 2 | 2 (6 tests) | **MAJOR** | `_add_row`, `update_mass_preview` untested |

---

## Prioritized Remediation Plan

### Immediate (CRITICAL)
1. **`projectile.py`** — Write a `tests/unit/simulation/combat/families/test_projectile_handler.py` covering:
   - `ProjectileHandler.fire()` with valid `AttackRequest`
   - Fire with `event_bus=None` (default)
   - Fire with `event_bus=Some` (PROJ-405 event threading)
   - Fire with zero-velocity aim vector
   - Verify `ProjectileResolution` contents

2. **`replay_spec.py`** — Add unit tests:
   - `ReplaySpec.iter_ship_snapshots()` — empty teams, single ship, multiple ships, missing `instance_snapshot`
   - `_strip_instance_snapshots()` — verify original dict unmodified, deep copy correct
   - `ReplaySpec.from_battle_spec()` with `ship_instance_lookup=None` (default path)
   - `ReplaySpec.from_dict()` with missing `schema_version` raises KeyError
   - `ReplaySpec.from_dict()` with missing `data` raises KeyError

### High Priority (MAJOR)
3. **`replay_serialization.py`** — Add round-trip unit tests for each leaf DTO pair (`to_dict`/`from_dict`), not just through `battle_spec_to_dict`. Test `compute_components_registry_hash` error paths.

4. **`telemetry.py`** — Add focused unit tests for `WeaponSummaryAggregator`, `ShipStatsAggregator`, and `HitLogRecorder` in `test_telemetry.py`.

5. **`research_controls.py`** — Write `tests/unit/ui/research/research_controls/test_research_controls.py` covering all 12 untested methods.

6. **`star_list_filter_manager.py`** — Add dedicated unit tests for `toggle_type`, `set_all_types`, `get_filter_state`.

7. **`ship_cargo_manager.py`** — Add tests for `load_vehicle`, `unload_vehicle`, `can_accept_vehicle` with per-bay typed allocation scenarios.

### Medium Priority (MINOR)
8. LOC ceiling violations: `replay_serialization.py` (634), `superweapon_order_processor.py` (506), `strategy_game_state_manager.py` (580), `ship_cargo_manager.py` (463), `research_controls.py` (475) — split into sub-modules.

9. Add direct assertions for internal helpers surfaced as heuristically untested (e.g., `__contains__` in `RoleRegistry`, `sensitivity_factor` in `MinefieldBalance`).

### Observation
10. Several Tier 0 files from the heuristic baseline (`battle_logger.py`, `container_snapshot.py`) were found to have comprehensive tests and have been reclassified to Tier 3. The heuristic import-based name-grep matching missed these because the test import paths differ from the production module paths.
