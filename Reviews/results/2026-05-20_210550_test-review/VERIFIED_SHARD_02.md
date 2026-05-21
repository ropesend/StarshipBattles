# Shard 02 — Verified Findings

## Summary
- **Phase 1 claims reviewed**: 24
- **Cross-shard claims reviewed**: 4
- **Total reviewed**: 28
- **CONFIRMED**: 27 | **DISPUTED**: 0 | **INCONCLUSIVE**: 1 | **Downgrades**: 0

## Verified Findings (CONFIRMED only)

### tests/unit/builder/test_ship_loading.py
#### CAT-1: test_all_ships_match_expected_stats [CRITICAL]
- **Location**: test_ship_loading.py:80-131 | **Issue**: Passes vacuously when `ships_dir` contains zero JSON files — the `failures` list stays empty and no assertion fires (line 130-131 only fires `if failures:`). Also passes when all ships lack `expected_stats` (line 96: `continue` skips the ship entirely). A directory with no .json files or only files without `expected_stats` yields a green test that exercises nothing. | **Suggestion**: Add a minimum-ship-files assertion before the loop, e.g. `assert len(ship_files) >= 1`. | **LOC affected**: 5 | **Verified**: CONFIRMED (severity kept). Lines 83-84 find files via `glob.glob`, empty list → loop never executes → `failures` never populated → `if failures:` never triggers → test passes trivially.

#### CAT-12: test_all_ships_match_expected_stats [MINOR]
- **Location**: test_ship_loading.py:88-129 | **Issue**: Logic-heavy test body (42 LOC) with for-loops, nested if/else checks for four stat types (max_hp, max_fuel, max_ammo, max_energy), and a broad `except Exception` (line 127). | **Suggestion**: Extract per-ship validation into a helper and parametrize by design file. | **LOC affected**: 42 | **Verified**: CONFIRMED (severity kept).

### tests/unit/builder/test_bulk_add.py
#### CAT-1: test_bulk_add_success [CRITICAL]
- **Location**: test_bulk_add.py:9-30 | **Issue**: Sole assertion `assert len(ship.layers[LayerType.ARMOR].components) == 10` depends on a mocked `Component` with the `allowed_layers` key removed from its init dict (line 21 comment: `# allowed_layers removed`). If `Component` constructor behavior or internal filtering changes, the test may silently pass with a different count. | **Suggestion**: Add `assert ship.layers[LayerType.ARMOR].components[0] is comp` to verify the component identity was actually added to the correct layer. | **LOC affected**: 22 | **Verified**: CONFIRMED (severity kept).

### tests/unit/strategy/services/test_empire_economy_caching.py
#### CAT-12: Logic-heavy test bodies [MINOR]
- **Location**: test_empire_economy_caching.py:32-83 | **Issue**: Four tests all unpack `smoke_turn1_scenario` identically (`session, galaxy, empires = smoke_turn1_scenario`) and call `_build_service(fresh_registries)`. Setup pattern repeated verbatim 4 times (lines 36-37, 48-49, 64-65, 77-78). | **Suggestion**: Extract into a fixture that yields `(service, session, galaxy, empires)`. | **LOC affected**: 20 | **Verified**: CONFIRMED (severity kept).

### tests/unit/modifiers/test_pipeline_unification.py
#### CAT-9: Repeated `first_component_with_ability` lookups [MINOR]
- **Location**: test_pipeline_unification.py:46-145 | **Issue**: Six tests call `first_component_with_ability()` then `component.recalculate_stats()` and `component.add_modifier(...)`. Only ability name and modifier parameters differ. Identical pattern: lookup → null-check/skip → recalculate → add_modifier → assert. | **Suggestion**: Parametrize on ability name + modifier id + expected values. | **LOC affected**: 90 | **Verified**: CONFIRMED (severity kept). 6 tests across 2 classes share the identical structure.

### tests/unit/ui/screens/test_build_queue_panel_factory.py
#### CAT-6: test_every_uipanel_in_factory_uses_fast_panel_class_id [MAJOR]
- **Location**: test_build_queue_panel_factory.py:170-206 | **Issue**: Iterates over `mock_panel.call_args_list` and asserts every single UIPanel call in `create_all_panels()` passes `object_id="@fast_panel"`. A legitimate future panel that intentionally does not use `@fast_panel` (e.g., a different visual context) would break this blanket assertion. The assertion is order-independent but imposes a maximum-constraint contract on all internal panel creations. | **Suggestion**: Use targeted assertions per logical panel group, or validate >=N panels (current behavior) and flag any that lack the id as warnings rather than hard failures. | **LOC affected**: 37 | **Verified**: CONFIRMED (severity kept). Actual fragility: broad assertion that ALL panels must always use @fast_panel, not order-binding as described in original.

#### CAT-8: test_scoped_fast_panel_object_id fixture setup [MINOR]
- **Location**: test_build_queue_panel_factory.py:133-168 | **Issue**: `_build_factory_for_create_all_panels` (lines 133-168) creates 12+ MagicMock attributes on the factory and configures mock facade, empire, build_context, portrait_loader, etc. The 37-line test at line 170 has ~30 lines of setup in this helper alone (~81% overhead). | **Suggestion**: Extract mock UI configuration into a reusable fixture. | **LOC affected**: 35 | **Verified**: CONFIRMED (severity kept).

#### CAT-12: test_theme_json_has_fast_panel_block_with_rectangle_shape [MINOR]
- **Location**: test_build_queue_panel_factory.py:208-234 | **Issue**: Resolves repo root via five nested `os.path.dirname` calls (line 214-220: `os.path.dirname(os.path.dirname(...))` x5) and reads `data/builder_theme.json` from disk with `open()`. This is a filesystem-dependency test, not a unit test — it validates the data file on disk rather than production logic. | **Suggestion**: Move to integration tests or use `Paths` module for repo-root resolution. | **LOC affected**: 27 | **Verified**: CONFIRMED (severity kept).

### tests/unit/strategy/consumable_management_engine/conftest.py
#### CAT-1: Fixture-only file, no test functions [CRITICAL → MAJOR, downgraded]
- **Location**: conftest.py:1-52 | **Issue**: Contains 4 fixtures (`mock_registries`, `mock_ship`, `mock_fleet`, `mock_empire`) and zero test functions. Sibling `test_initialization.py` duplicates `mock_registries` identically at lines 12-20 — never importing from conftest. The conftest fixtures are dead: pytest discovers them by directory convention but no test function in the directory uses them. | **Suggestion**: Either use the conftest fixtures in `test_initialization.py` or remove the conftest. | **LOC affected**: 52 | **Verified**: CONFIRMED (severity kept as MAJOR — downgrade appropriate; 52 LOC of dead fixture code).

### tests/unit/ui/test_theme_discovery.py
#### CAT-5: Autouse fixtures re-init pygame display per test [MAJOR]
- **Location**: test_theme_discovery.py:26-49, 74-88, 178-185, 238-243, 278-284, 361-366, 401-406, 446-451, 528-533 | **Issue**: Nine test classes each have `autouse=True` function-scoped fixtures that set `SDL_VIDEODRIVER=dummy`, many call `pygame.display.set_mode()`, and initialize/re-seat `ShipThemeManager` singleton. For ~30 tests this means ~30 pygame display inits and singleton resets. **Correction**: 9 classes (not 8 as originally reported). | **Suggestion**: Use class-scoped or module-scoped fixtures that share the initialized manager. | **LOC affected**: 80 | **Verified**: CONFIRMED (severity kept). Observed 9 classes: TestNewThemes (26-49), TestThemeContractAgainstRealAssets (74-88), TestImageSizeValidationWarning (178-185), TestShipThemeManagerSingletonLifecycle (238-243), TestShipThemeManagerErrorPaths (278-284), TestShipThemeManagerCaching (361-366), TestShipThemeManagerMetrics (401-406), TestShipThemeManagerThreadSafety (446-451), TestShipThemeManagerManualScale (528-533).

### tests/unit/ui/test_detail_panel_rendering.py
#### CAT-8: setup_method with 7 nested patch starts [MINOR]
- **Location**: test_detail_panel_rendering.py:16-76 | **Issue**: `setup_method` starts 7 `patch()` instances (lines 25-32), deletes a module from `sys.modules` (lines 18-21), configures a mock manager with theme/font/rect stubs (lines 57-64), imports the panel under test (line 53), and constructs it (lines 72-76). Setup accounts for 60/252 lines (~24% of the file). | **Suggestion**: Move pygame_gui mocks to a shared fixture with class scope. | **LOC affected**: 60 | **Verified**: CONFIRMED (severity kept).

### tests/unit/ui/test_battle_panels_characterization.py
#### CAT-4: Near-duplicate draw_*_renders_*_text tests [MAJOR]
- **Location**: test_battle_panels_characterization.py:435-468 | **Issue**: Three tests with near-identical bodies differing only in team setup and expected text:
  - `test_draw_battle_over_team0_alive_renders_team1_wins_text` (line 435): team_id=0, alive=True → "TEAM 1 WINS"
  - `test_draw_battle_over_team1_alive_renders_team2_wins_text` (line 448): team_id=1, alive=True → "TEAM 2 WINS"
  - `test_draw_battle_over_no_alive_renders_draw_text` (line 460): both teams dead → "DRAW"
  Each calls `_draw_setup` → `_stub_fonts` → `panel.draw(screen)` → extract `call_args_list` → assert text. | **Suggestion**: Parametrize on `(ships_config, expected_text)`. | **LOC affected**: 35 | **Verified**: CONFIRMED (severity kept).

### tests/unit/ai/test_ai.py
#### CAT-5: Function-scoped fixtures rebuild full Ship objects per test [MAJOR]
- **Location**: test_ai.py:17-70 | **Issue**: `ai_setup` fixture (function-scoped by default) loads component data from disk (line 25: `load_components`), loads vehicle classes (line 27: `load_vehicle_classes`), loads AI policy data from test JSON files (lines 29-34), instantiates a `SpatialGrid` (line 37), creates 2 real `Ship` objects each with 5 real component additions (lines 40-54), and creates an `AIController` (line 62). Every test in `TestAIController` triggers this full rebuild including disk I/O. | **Suggestion**: Make class-scoped and use `copy.deepcopy()` or re-initialize only the mutable state. | **LOC affected**: 130 | **Verified**: CONFIRMED (severity kept).

### tests/unit/strategy/test_engine_event_emission.py
#### CAT-10: Repeated event assertion pattern [MINOR]
- **Location**: test_engine_event_emission.py:108-192 (4 `test_spawn_ship_*` variants), 221-268 (2 fleet variants), 279-339 (3 complex variants) | **Issue**: Three test classes with 4+2+3 tests share identical structure: create engine via `_capture_log_event_calls()`, create mock empire/planet/galaxy, wire catalog, call spawn method, assert `len(calls) == 1`, assert event type and kw fields. Only inputs and expected values differ. | **Suggestion**: Parametrize by spawn method, input params, and expected event kwargs. | **LOC affected**: 150 | **Verified**: CONFIRMED (severity kept).

### tests/unit/strategy/data/test_squadron_characterization.py
#### CAT-10: Round-trip tests with identical pattern [MINOR]
- **Location**: test_squadron_characterization.py:113-172 | **Issue**: Five `test_round_trip_*` methods (lines 113, 125, 136, 149, 162) all create a `Squadron` with varying ctor args, call `Squadron.from_dict(original.to_dict())`, and assert field equality. Only ctor args differ. **Correction**: 5 tests, not 6 as originally reported. | **Suggestion**: Parametrize on `(squadron_kwargs, assert_fn)`. | **LOC affected**: 60 | **Verified**: CONFIRMED (severity kept).

### tests/unit/modifiers/test_propulsion_ability_bindings.py
#### CAT-4: Duplicate test patterns across propulsion ability classes [MAJOR]
- **Location**: test_propulsion_ability_bindings.py:13-121 | **Issue**: Three classes (lines 10-46, 48-84, 86-121) with identical triples:
  - `TestCombatPropulsionBindings`: `test_combat_propulsion_has_thrust_binding` + `test_combat_propulsion_get_consumed_stats` + `test_combat_propulsion_recalculate`
  - `TestManeuveringThrusterBindings`: `test_maneuvering_thruster_has_turn_binding` + `test_maneuvering_thruster_get_consumed_stats` + `test_maneuvering_thruster_recalculate`
  - `TestStrategicMovementBindings`: `test_strategic_movement_has_strategic_binding` + `test_strategic_movement_get_consumed_stats` + `test_strategic_movement_recalculate`
  Each triplet checks STAT_BINDINGS existence, consumed stats set membership, and recalculate() with a locally-defined MockComponent. | **Suggestion**: Parametrize on `(ability_class, stat_key, attr_name, base_value, mult_value, expected)`. | **LOC affected**: 100 | **Verified**: CONFIRMED (severity kept).

### tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py
#### CAT-4: Duplicate resolver-capture tests [MAJOR]
- **Location**: test_movement_phase_collaborator.py:89-133 vs tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py:147-196 | **Issue**: Both files contain near-identical tests that verify `MinefieldResolver.resolve_minefield_entry(...)` receives `registries=engine._registries`:
  - `test_resolve_after_threads_registries_into_minefield_resolver` (collaborator, line 89): Creates a local `_CaptureResolver` class, monkeypatches `minefield_resolver.MinefieldResolver`, calls `collab.resolve_after(engine, ctx)`, asserts `captured.get("registries") is sentinel_registries`.
  - `test_derive_moved_fleet_ids_threads_registries_to_minefield_resolver` (descriptor, line 147): Creates an identical `_CaptureResolver` class, monkeypatches the same target, calls the movement post-hook, asserts `captured.get("registries") is sentinel_registries`.
  Same mock class structure, same monkeypatch target, same assertions. | **Suggestion**: Consolidate one as the canonical test or add cross-reference comments. | **LOC affected**: 90 | **Verified**: CONFIRMED (severity kept).

### tests/unit/simulation/entities/test_ship_physics.py
#### CAT-10: Heading/velocity tests with identical pattern [MINOR]
- **Location**: test_ship_physics.py:344-387 | **Issue**: Four tests share identical bodies differing only by angle and expected velocity vector:
  - `test_velocity_set_from_speed_and_heading` (line 344): angle=0 → (10, 0)
  - `test_velocity_follows_heading_at_90_degrees` (line 356): angle=90 → (0, 10)
  - `test_velocity_follows_heading_at_180_degrees` (line 367): angle=180 → (-10, 0)
  - `test_velocity_follows_heading_at_270_degrees` (line 378): angle=270 → (0, -10)
  Each: create ship at angle N, set speed 10, set acceleration_rate 0, call `update_physics_movement()`, assert velocity components. | **Suggestion**: Parametrize on `(angle, expected_x, expected_y)`. | **LOC affected**: 35 | **Verified**: CONFIRMED (severity kept).

### tests/unit/simulation/ship_combat_engine/test_cooldowns.py
#### CAT-10: Shield regen tests with identical pattern [MINOR]
- **Location**: test_cooldowns.py:58-140 | **Issue**: Five shield regen tests follow identical setup:
  - Line 58: `test_shield_regen_applies_when_below_max`
  - Line 75: `test_shield_regen_does_not_exceed_max`
  - Line 93: `test_shield_regen_does_nothing_when_at_max`
  - Line 110: `test_shield_regen_does_nothing_with_zero_rate`
  - Line 127: `test_shield_regen_multiple_ticks_accumulate`
  Each: create MagicMock ship, set is_alive/current_shields/max_shields/shield_regen_rate/shield_regen_cost/repair_rate, create ShipCombatEngine, call update_combat_cooldowns(), assert current_shields. **Correction**: 5 tests, not 6 as originally reported. | **Suggestion**: Parametrize on `(initial_shields, max, regen_rate, ticks, expected_shields)`. | **LOC affected**: 70 | **Verified**: CONFIRMED (severity kept).

### tests/unit/simulation/test_formula_exceptions.py
#### CAT-10: Formula exception tests with repeated imports [MINOR]
- **Location**: test_formula_exceptions.py:13-81 | **Issue**: Every test in `TestFormulaExceptionRaising` re-imports `FormulaEvaluator` inside the method body. Seven identical `from game.core.formula_evaluator import FormulaEvaluator` lines (lines 15, 25, 35, 44, 54, 65, 75) — no module-level import exists. | **Suggestion**: Import once at module level (line ~4). | **LOC affected**: 7 | **Verified**: CONFIRMED (severity kept).

### tests/unit/ui/screens/test_strategy_ui_tooltips.py
#### CAT-2: test_tooltip_enrichment tests depend on real keybindings file [CRITICAL → MAJOR, downgraded]
- **Location**: test_strategy_ui_tooltips.py:34-50 | **Issue**: `test_get_tooltip_text_returns_hotkey` loads from `Paths.DEFAULT_KEYBINDINGS_FILE` (line 38) and asserts exact string matches: `"Enter"` (line 42), `"Shift+P"` (line 46), `"Shift+G"` (line 50). If the default keybindings file is remapped, these break unconditionally. | **Suggestion**: Test the mapping logic with injected/conftest-controlled bindings, not the production defaults file. | **LOC affected**: 17 | **Verified**: CONFIRMED (severity kept as MAJOR — downgrade from CRITICAL appropriate).

### tests/unit/agent_coordination/test_codex_consult_skills.py
#### CAT-2: Tests only file content, no game.* imports [CRITICAL]
- **Location**: test_codex_consult_skills.py:1-101 | **Issue**: All tests read `.md` and `.yaml` files from `.agents/skills/` and assert string containment. Imports are only `from __future__ import annotations` and `from pathlib import Path`. Zero `game.*` imports. These are documentation validation tests, not code tests — they exercise agent skill metadata correctness, not production code. | **Suggestion**: Move to `tests/static_guards/` or `tests/projects/` directory. | **LOC affected**: 101 | **Verified**: CONFIRMED (severity kept). These tests serve a valid purpose (agent skill metadata validation) but are mis-categorized as unit tests.

### tests/integration/strategy/test_fleet_navigation_consistency.py
#### CAT-1: test_already_at_destination_consistency [CRITICAL]
- **Location**: test_fleet_navigation_consistency.py:308-326 | **Issue**: Fleet at `HexCoord(5, 5)` is ordered to MOVE to `HexCoord(5, 5)`. After `process_turn()`, line 326 asserts `len(fleet.orders) == 0` — this depends on the handler immediately popping the order when the fleet is already at destination. If the handler implementation changes to (e.g.) defer clearing orders until actual movement occurs, this assertion breaks while player-facing behavior remains correct. | **Suggestion**: Assert `fleet.location == loc` only; avoid asserting on order queue internals. | **LOC affected**: 18 | **Verified**: CONFIRMED (severity kept).

### tests/unit/services/llm/test_background.py
#### CAT-7: time.sleep() in test bodies [MAJOR]
- **Location**: test_background.py:141, 149, 201 | **Issue**: Three sleep calls in test bodies:
  - Line 141: `time.sleep(0.01)` in `test_elapsed_seconds_is_monotonic_then_frozen` — waits for elapsed to be > 0
  - Line 149: `time.sleep(0.05)` — verifies elapsed is frozen after completion
  - Line 201: `time.sleep(0.02)` in `test_cancel_marks_status_cancelled` — waits for worker to start before cancel
  These add real latency (~0.08s per affected test, ~0.5s cumulative) and are fragile in CI. | **Suggestion**: Use `threading.Event`-based synchronization instead of sleep. | **LOC affected**: 8 | **Verified**: CONFIRMED (severity kept).

---

## Cross-Shard Claims (Shard 02 involvement)

### DUP-002: `_draw_setup` + `_stub_fonts` helper duplication [CONFIRMED]
- **Shard 02 file**: tests/unit/ui/test_battle_panels_characterization.py:419-433
- **Observation**: `TestBattleControlPanel._draw_setup` (line 419) and `_stub_fonts` (line 428) are helper methods constructing mocked `BattleControlPanel` + screen + font. Three draw tests (lines 435-468) use them identically. Cross-shard DUP-002 reports Shard 14's `test_battle_panels_extended.py` duplicates similar pygame mock setup.
- **Recommendation**: Extract a shared `@pytest.fixture` providing a pre-mocked `battle_panels` module, or merge the characterization file into the extended test file.

### DUP-006: Modifier stub class duplication [INCONCLUSIVE]
- **Shard 02 file**: tests/unit/modifiers/test_propulsion_ability_bindings.py:13-186
- **Observation**: DUP-006 connects Shard 02's propulsion binding tests to Shard 07's `_Modifier`/`_SpecialModifier` stub duplication. However, `test_propulsion_ability_bindings.py` does not define or use `_Modifier`/`_SpecialModifier` stubs — it uses inline `MockComponent` classes (lines 36-40, 74-78, 112-116) with `stats` dicts and tests STAT_BINDINGS against real ability classes. The connection is tangential: both involve modifier-related test patterns but not the same stub class. The CAT-4 flag on this file (duplicate test patterns) is valid but the DUP-006 cross-shard claim's inclusion of Shard 02 is weak.
- **Recommendation**: Shard 02's `test_propulsion_ability_bindings.py` does not need to participate in DUP-006 consolidation. Shard 07's modifier stubs should be extracted independently.

### HLP-002: `MockPlanetType(Enum)` inline duplication [CONFIRMED]
- **Shard 02 file**: tests/unit/strategy/test_engine_event_emission.py:440, 540, 938, 999
- **Observation**: `class MockPlanetType(Enum): CONTINENTAL = "CONTINENTAL"` is defined inline inside four different test methods/scope blocks at lines 440, 540, 938, and 999. This matches the cross-shard pattern: same two-field Enum (CONTINENTAL only variant) repeated verbatim across test classes and shards.
- **Recommendation**: Define a single `MockPlanetType` in a shared fixture module and import it. The turn_engine conftest version could be the canonical source.

### HLP-004: `_make_fleet` helper proliferation [CONFIRMED]
- **Shard 02 files**: tests/unit/strategy/combat/test_battle_assembly_third_party_mines.py:33-42, tests/unit/strategy/engine/test_environmental_hazard_engine.py:43-54
- **Observation**: Both files define local `_make_fleet` helpers with different signatures:
  - `test_battle_assembly_third_party_mines.py` line 33: `_make_fleet(fleet_id, owner_id, location, ships)` → MagicMock with `spec_set`
  - `test_environmental_hazard_engine.py` line 43: `_make_fleet(*, fleet_id=1, location=_UNSET, combat_ships=None)` → MagicMock (keyword-only, different signature)
  These are 2 of 43+ `_make_fleet` definitions across the codebase.
- **Recommendation**: Create a canonical `tests/conftest.py:_make_mock_fleet(**overrides)` accepting kwargs for per-context fields. See HLP-004 for full consolidation plan.

---

## Disputed & Inconclusive Claims

| Claim | File | Verdict | Detail |
|-------|------|---------|--------|
| DUP-006: Modifier stub duplication involving Shard 02 | tests/unit/modifiers/test_propulsion_ability_bindings.py | INCONCLUSIVE | File does not define `_Modifier`/`_SpecialModifier` stubs; uses inline `MockComponent` classes for STAT_BINDINGS testing. Connection to Shard 07's modifier stub duplication is weak. |

---

## Verification Notes
- All 24 Phase 1 claims from SHARD_02.md verified directly against cited line ranges + surrounding context.
- 3 minor factual corrections: test_theme_discovery has 9 (not 8) autouse fixture classes; test_squadron_characterization has 5 (not 6) round-trip tests; test_cooldowns has 5 (not 6) shield regen tests. None affect the validity of the claims.
- Cross-shard claims DUP-002, HLP-002, and HLP-004 confirmed against Shard 02 files. DUP-006 marked INCONCLUSIVE due to weak connection.
- No severity downgrades needed beyond the already-applied downgrades in Phase 1 (consumable_management_engine/conftest.py CRITICAL→MAJOR, test_strategy_ui_tooltips CRITICAL→MAJOR).
