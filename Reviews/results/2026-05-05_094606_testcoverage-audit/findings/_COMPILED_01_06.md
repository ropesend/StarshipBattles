# Compiled Confirmed Gaps — Shards 01-06

**Compiled:** 2026-05-05  
**Source:** VERIFIED_SHARD_01.md through VERIFIED_SHARD_06.md (Phase 3 — Skeptical Verification)  
**Scope:** Only CONFIRMED coverage gaps. DISPUTED and INCONCLUSIVE claims excluded.

---

## Per-Shard Statistics

| Shard | Reviewed | Confirmed | Disputed | Inconclusive | Downgrades | Upgrades |
|---|---|---|---|---|---|---|
| 01 | 72 | 1 | 68 | 4 | 6 (CRIT→DISPUTED) | 0 |
| 02 | 23 | 5 (CRIT+MAJ) / 14 (all) | 6 | 0 | 3 (CRIT→MAJ/MIN) | 0 |
| 03 | 17 | 6 | 1 | 0 | 1 (MAJ→MIN) | 4 (T2→T3) |
| 04 | 18 | 4 | 4 | 0 | 5 | 0 |
| 05 | 27 | 12 | 2 | 0 | 2 (MAJ→MIN) | 2 (T0→T3) |
| 06 | 7 | 5 (incl. 3 FP neg.) | 1 | 0 | 2 (MAJ→MIN) | 3 (T0→T3) |

**Notes on Shard 02 column:** The Phase 2 report filed 34 claims (4 CRIT + 4 MAJ + 8 MIN + 18 ADVISORY). The verifier sampled 23. "Confirmed 5" counts CRITICAL+MAJOR gaps that were independently confirmed by reading test files; the remaining 9 MINOR gaps were partially extrapolated from Phase 2 (only 5/8 MINOR claims sampled directly) but accepted into the Final Corrected Tiers by the verifier.

**Notes on Shard 06:** 3 confirmed gaps are Phase 1 false negatives (files reclassified Tier 0→Tier 3). The remaining 2 are genuine MAJOR gaps (battle_ui.py, ship_combat_engine.py).

---

## All CONFIRMED Gaps

---

### [MAJOR] `game/strategy/generation/density/primitives/geometric.py` — `evaluate`
- **Shard**: 01
- **Location**: geometric.py:66-68
- **Untested**: `sides < 3` fallback to circle. Tests cover sides=3, 4, 6. No test for sides=1 or sides=2.
- **Suggested test**: `test_evaluate_sides_less_than_3_falls_back_to_circle` — sides=2 should produce identical result to circle primitive.

---

### [CRITICAL] `game/ui/screens/workshop_data_reloader.py` — All 11 symbols
- **Shard**: 02
- **Location**: workshop_data_reloader.py:1-197 (entire file)
- **Untested**: Entire class `WorkshopDataReloader` (197 LOC, 11 symbols). Zero test coverage at any level. No test file imports, references, or exercises this class. The `reload_data()` error-handling path (line 158-160) catches `OSError`, `ValueError`, `KeyError` but could leave UI in inconsistent state on silent failure.
- **Suggested test**: `tests/unit/ui/screens/test_workshop_data_reloader.py` — cover `reload_data` success path, `reload_data` error-path (OSError/ValueError/KeyError → UI state consistency), `_load_all_data` orchestration chain.

---

### [MAJOR] `game/strategy/services/replay_verification_coordinator.py` — `_json_safe`
- **Shard**: 02
- **Location**: replay_verification_coordinator.py:104-133
- **Untested**: 4 of 5 distinct branches: Enum branch (line 126-127, `isinstance(value, Enum)` → recursive), dict recursive walk with non-primitive values (lines 128-129), tuple→list conversion (lines 130-131), fallback `repr(value)` for unknown types (line 133). Currently low risk because `battle_outcome_to_dict` only produces JSON-primitives, but future Enum/datetime/Vector2 additions would engage untested code.
- **Suggested test**: Parametrized tests for `_json_safe` with Enum value, dict containing Enum, tuple, and unknown-type input. Verify each branch's output shape.

---

### [MAJOR] `game/ui/screens/test_lab/data_extractor.py` — `extract_ships`, `load_component`, `get_components_cache`
- **Shard**: 02
- **Location**: data_extractor.py:121-226
- **Untested**: ~40% of branches: scenario-class attribute fallback (lines 121-139, when `metadata.conditions` has no JSON filename but `scenario_cls` has `ship_file`), PROP-002 hardcoded multi-ship list (lines 142-165, `"Test 3 ships"` condition), condition with mass annotation (e.g. `"Ship: Test_Engine_1x_LowMass.json (mass=40)"`), `load_component()` cache-miss on first call (lines 198-211, tested only indirectly via patched `load_json`), `get_components_cache()` lazy cache population trigger (lines 224-226).
- **Suggested test**: Test scenario-class fallback with minimal `ScenarioClass`, PROP-002 multi-ship extraction, mass-annotated ship condition parsing, and direct cache-population verification.

---

### [MAJOR] `game/ui/screens/transfer_controller.py` — `collect_sources_and_targets`, `discover_pod_designs`
- **Shard**: 02
- **Location**: transfer_controller.py:71-147
- **Untested**: `collect_sources_and_targets` (lines 71-128, projected position fallback, colony vs uncolonized labeling) and `discover_pod_designs` (lines 130-147, Exception fallback handling). Dialog tests mock `get_fleets_at_hex` at facade level and patch `_all_pod_names` directly, bypassing these methods. ~60% of controller logic is exercised through 4 dialog test files.
- **Suggested test**: Direct unit tests for `collect_sources_and_targets` with fleet-fleet, fleet-colony, and uncolonized planet scenarios. Test `discover_pod_designs` Exception fallback path.

---

### [MAJOR] `game/ui/screens/workshop_viewmodel_ship_ops.py` — 8 untested methods
- **Shard**: 02
- **Location**: workshop_viewmodel_ship_ops.py:101-330
- **Untested**: 8 of 18 methods: `add_component_bulk` (lines 101-122), `add_component_instance` (lines 124-140), `change_ship_class` (lines 177-205), `validate_design` (lines 207-216), `get_available_components_for_layer` (lines 218-223), `get_ship_summary` (lines 225-230), `set_ship_targeting_policy` (lines 300-314), `set_ship_design_role` (lines 316-330). 10/18 methods are exercised through ViewModel tests.
- **Suggested test**: `tests/unit/ui/screens/test_workshop_viewmodel_ship_ops.py` covering each untested method with edge cases.

---

### [MINOR] `game/strategy/services/ability_sources/facility.py` — `get_activation_state`
- **Shard**: 02
- **Location**: facility.py:74-87
- **Untested**: 3 branches (found match, no match, missing callable). 8/11 paths covered by `test_facility.py`. `affects_hex()` and `affects_system()` are trivial (always return True).
- **Suggested test**: Test `get_activation_state` with matching facility, non-matching name, and None/unset activation_function.

---

### [MINOR] `game/simulation/components/abilities/stat_keys.py` — `__post_init__` error path
- **Shard**: 02
- **Location**: stat_keys.py:36-41
- **Untested**: `operation not in {'multiply', 'add', 'set'}` defensive guard at construction time. Low blast radius — enum-like known set.
- **Suggested test**: Parametrized test constructing `StatModifier` with invalid operation value.

---

### [MINOR] `game/simulation/components/component_loader.py` — `__init__`
- **Shard**: 02
- **Location**: component_loader.py (dunder __init__)
- **Untested**: Sets 4 fields to None. Tested indirectly through `get_default_cache_manager()`.
- **Suggested test**: Direct construction + field verification for defensive regression.

---

### [MINOR] `game/simulation/systems/battle_end_conditions.py` — 9 `__repr__` methods
- **Shard**: 02
- **Location**: battle_end_conditions.py (9 dataclass __repr__ methods)
- **Untested**: 9 debugging `__repr__` methods (corrected from Phase 2 claim of 10). All are `f"ClassName(params)"` patterns.
- **Suggested test**: Single parametrized test verifying `__repr__` contains class name and key fields.

---

### [MINOR] `game/strategy/engine/game_config.py` — 2 module-level helpers
- **Shard**: 02
- **Location**: game_config.py (module-level helpers)
- **Untested**: 2 module-level helper functions with no direct tests. Tested indirectly through their callers.
- **Suggested test**: Add direct unit tests for the 2 helper functions.

---

### [MINOR] `game/strategy/facade/strategy_session_facade.py` — Property shims
- **Shard**: 02
- **Location**: strategy_session_facade.py (property shim methods)
- **Untested**: Property shim methods with zero direct tests. Tested indirectly through facade integration.
- **Suggested test**: Verify property forwarders return correct types.

---

### [MINOR] `game/ui/screens/build_queue_queue_data_source.py` — `_format_int`, `__init__`
- **Shard**: 02
- **Location**: build_queue_queue_data_source.py:57-62
- **Untested**: `_format_int` 3 branches (zero, non-zero, float rounding). Zero-value tested implicitly.
- **Suggested test**: Parametrized test for `_format_int` with 0, positive, large, float values.

---

### [MINOR] `game/ui/services/modifier_icon_service.py` — `__init__`
- **Shard**: 02
- **Location**: modifier_icon_service.py (dunder __init__)
- **Untested**: Stores icon_size/base_path. Tested via `get_icon()`.
- **Suggested test**: Direct construction + attribute check.

---

### [MINOR] `game/simulation/components/component.py` — `mark_hp_cache_dirty`
- **Shard**: 02
- **Location**: component.py (dunder method)
- **Untested**: Dunder method for cache invalidation. Tested indirectly through damage paths.
- **Suggested test**: Verify cache state before/after `mark_hp_cache_dirty` call.

---

### [ADVISORY] `game/ui/screens/galaxy_test/galaxy_mode.py` — Pure UI rendering
- **Shard**: 02
- **Location**: galaxy_mode.py (427 LOC)
- **Untested**: pygame_gui rendering, galaxy generation, camera manipulation. No business logic.
- **Suggested test**: N/A — low value for pure rendering code.

---

### [ADVISORY] `game/ui/screens/fleet_report_window.py` — UI event handlers
- **Shard**: 02
- **Location**: fleet_report_window.py (430 LOC)
- **Untested**: `process_event`, `_handle_row_click`, private mutators (`_swap_columns`, `_toggle_filter`, `_apply_tri_state_filter`). Tested indirectly through integration tests. No business logic.
- **Suggested test**: N/A.

---

### [ADVISORY] `game/core/protocols/registry.py` — Protocol definition
- **Shard**: 02
- **Location**: registry.py (38 lines)
- **Untested**: `IRegistryProvider` protocol with 4 abstract methods. Used by 75+ test files.
- **Suggested test**: N/A — abstract protocol, exercised by all implementations.

---

### [MINOR] `game/strategy/data/race_caption_loader.py` — `_load` non-dict data branch
- **Shard**: 03
- **Location**: race_caption_loader.py:96-101
- **Untested**: `not isinstance(data, dict)` guard when JSON parses to array or scalar. 4/5 error paths tested (missing file, malformed JSON, wrong schema_version, valid data). No test submits a JSON array `[1,2,3]` or JSON scalar.
- **Suggested test**: Test `_load` with JSON array input and JSON string scalar input.

---

### [MINOR] `game/strategy/data/race_description_prompt_builder.py` — `_render_preferences` unknown factor skip
- **Shard**: 03
- **Location**: race_description_prompt_builder.py:237-238
- **Untested**: `if factor is None: continue` guard when `factor_id` is in `race_config.preferences` but missing from `FACTOR_REGISTRY`. Normal path (factors present) tested via `test_user_prompt_includes_environmental_preferences`.
- **Suggested test**: Construct race config with an unknown `factor_id` in preferences and verify it is silently skipped.

---

### [MINOR] `game/simulation/combat/formations/battle_line.py` — `leader=None`, `total==0`, `wall` shape
- **Shard**: 03
- **Location**: battle_line.py:47-48, 50-52, 74-90
- **Untested**: (1) `leader is None` → returns None early return (line 47-48). (2) Empty `group_ships` list (`total == 0`) fallback to `total = 1` (lines 50-52). (3) "wall" shape — documented supported shape but never tested (lines 74-90). Shapes "line", "wedge", "echelon_left", "echelon_right" are all tested.
- **Suggested test**: `test_leader_none_returns_none`, `test_empty_group_ships_fallback`, `test_wall_shape_positions`.

---

### [MINOR] `game/strategy/services/ability_sources/warp_point.py` — 5 edge-case gaps
- **Shard**: 03
- **Location**: warp_point.py:27, 43, 53-58
- **Untested**: (1) `source_label` fallback when `destination_id` is absent (line 27). (2) `get_abilities` when `intrinsic_abilities` is None (line 43). (3) `affects_hex` when `global_location` is None (line 53). (4) `affects_hex` with `location` as None (line 53). (5) `affects_hex` with `TypeError` from hex coordinate addition (lines 56-58). The file has 8 comprehensive tests; these are remaining edge cases.
- **Suggested test**: Add 5 edge-case tests to `test_warp_point.py` covering each path.

---

### [CRITICAL] `game/strategy/services/ability_sources/fleet.py` — All 12 symbols
- **Shard**: 04
- **Location**: fleet.py:1-148 (entire file)
- **Untested**: `FleetAbilitySource` has zero behavioral tests. `get_abilities()`, `affects_hex()`, `source_label`, `_is_combat_capable()`, `_is_hidden()`, `_walk_strategic_abilities()` — all untested. The only test file referencing this module (67 LOC) performs an AST scan for global registry access; it does not test business logic. No other test file imports from this module.
- **Suggested test**: `tests/unit/strategy/services/ability_sources/test_fleet_ability_source.py` covering all 12 symbols: memoization cache, strategic scope filtering, cloaked fleet empty-result, affects_hex matching/non-matching, source_label formatting, _is_combat_capable error tolerance, _walk_strategic_abilities scope filtering.

---

### [MAJOR] `game/simulation/components/abilities/__init__.py` — `_contains_unevaluated_formula`
- **Shard**: 04
- **Location**: abilities/__init__.py:159
- **Untested**: `_contains_unevaluated_formula` has zero unit tests. Called internally by `create_ability()` (line 193) but no test verifies its recursive logic for nested dicts, lists, mixed types, empty data, or `=`-prefixed strings.
- **Suggested test**: Parametrized tests for `_contains_unevaluated_formula` with: flat `=`-string, non-formula string, nested dict with formula, list containing formula, empty data, int/float/bool, mixed nested structures.

---

### [MAJOR] `game/ui/screens/workshop_viewmodel_selection.py` — All 3 pure functions
- **Shard**: 04
- **Location**: workshop_viewmodel_selection.py:21-138 (entire file)
- **Untested**: `normalize_selection()` (line 21), `apply_append_selection()` (line 62), `sync_modifiers_to_selection()` (line 117) — all three pure functions have zero test coverage. The similar-sounding `test_builder_selection.py` tests a DIFFERENT module (`game.ui.screens.builder_selection`). The only test-suite reference to `_sync_modifiers_to_selection` is a string literal in a public API symbol list.
- **Suggested test**: `tests/unit/ui/screens/test_workshop_viewmodel_selection.py` covering: tuple-pass-through, component-lookup in ship layers, component-not-found (None, -1) path, append/toggle with empty current/empty incoming, homogeneity enforcement, toggle-add, toggle-remove, modifier copy to siblings (skip primary), no-selection/no-primary edge cases.

---

### [MINOR] `game/strategy/engine/happiness_engine.py` — `_validate_tick_inputs` error path
- **Shard**: 04
- **Location**: happiness_engine.py:90-96
- **Untested**: `_validate_tick_inputs()` raises `ValidationException` when colony list contains None (line 96). The method is exercised indirectly through `process_happiness()` for the non-error path, but no test passes a colony list with None to trigger the exception.
- **Suggested test**: `test_none_colony_in_list_raises_validation_exception` — pass a colony list containing None and assert `ValidationException` is raised.

---

### [CRITICAL] `game/ui/services/image/background.py` — All symbols
- **Shard**: 05
- **Location**: background.py:1-230 (entire file)
- **Untested**: Threaded image-generation with module-level mutable state (`_in_flight_calls`, `_active_workers`, `_in_flight_lock`). `start()` has concurrency gating (lines 109-119) with check-then-increment race condition. `_run()` has cancellation race handling (lines 166-201). `shutdown_all_image_calls()` (line 209) with partial timeout logic. Zero test coverage — no test file references `ImageBackgroundCall`. Parallels `LLMBackgroundCall` (which has dedicated tests) but has none of its own.
- **Suggested test**: `tests/unit/ui/services/image/test_background.py` — test `start()` concurrency gating, `_run()` cancellation, `shutdown_all_image_calls()` timeout logic. Race condition verification with concurrent start/shutdown calls.

---

### [MAJOR] `game/simulation/entities/ship_stats.py` — `_aggregate_resource_abilities`, `_apply_aggregated_stats`
- **Shard**: 05
- **Location**: ship_stats.py:274-366
- **Untested**: Both methods only tested indirectly via `calculate()` → snapshots. No direct unit tests. Gaps: unknown resource type classification, empty `ability_instances`, `ability.trigger == "warp_jump"` path in `_aggregate_resource_abilities`. `external_stats` dict guard (line 348-357), `shield_capacity_mult` from external_stats (line 356) in `_apply_aggregated_stats`. Test file `test_ship_stats.py` (54 lines) only covers hangar aggregation routing.
- **Suggested test**: Direct unit tests for `_aggregate_resource_abilities` with unknown/empty/warp_jump inputs. Direct tests for `_apply_aggregated_stats` with real dict external_stats (shield bonus path) and MagicMock (guard path).

---

### [MAJOR] `game/simulation/replay/replay_serialization.py` — 4 specific gaps
- **Shard**: 05
- **Location**: replay_serialization.py:83-84, 115, 191-203, 586-628
- **Untested**:
  1. `_list_to_vec` Vector2 passthrough (line 83-84): `isinstance(data, Vector2)` branch never hit in tests (JSON roundtrip always produces lists).
  2. `boundary_to_dict` TypeError branch (line 115): reached only if boundary is not None/RectBoundary/CircleBoundary/UnboundedRegion. Never hit.
  3. `_formation_to_dict` fallback (lines 191-203): non-`FormationSpec` input path returns default LINE_ASTERN formation. Never hit.
  4. `compute_components_registry_hash` (lines 586-628): zero tests for entire function. Two broad `except Exception` catches (registry shape drift → `"sha256:unknown"`, bad `to_dict` → `str(entry)` fallback). Dict vs hasattr branching.
- **Suggested test**: Direct parametrized tests for each of the 4 gaps. For `compute_components_registry_hash`: test with valid component registry, invalid entries (missing to_dict), and exception-inducing entries.

---

### [MAJOR] `game/strategy/services/ability_iterator.py` — `_fleet_provider` system-scope, `_planet_global_hex` TypeError
- **Shard**: 05
- **Location**: ability_iterator.py:166-179, 254-259
- **Untested**: (1) `_fleet_provider` system-scope path (when `hex_coord is None`, using `_FLEETS_IN_SYSTEM_LOOKUP`): only hex-query path tested. (2) `_planet_global_hex` TypeError catch (lines 166-179): `system_loc + planet_loc` expects `HexCoord.__add__`; TypeError when non-HexCoord values are present is untested.
- **Suggested test**: Test `iter_ability_sources_in_system` with fleet lookups configured. Test `_planet_global_hex` with a non-HexCoord location.

---

### [MAJOR] `game/strategy/services/component_inspector.py` — 3 untested symbols
- **Shard**: 05
- **Location**: component_inspector.py:48-299
- **Untested**: `extract_abilities_from_component` (lines 48-78, registry lookup by comp_id + string comp path), `list_ship_abilities` (lines 253-273, entire function — unique ability name extraction), `get_ability_list` (lines 276-299, scalar-to-list path at line 299: `return [{'value': val}]`). Test file `test_component_inspector.py` (259 lines) only tests `get_component_abilities`. Zero direct tests for these 3 symbols.
- **Suggested test**: Direct tests for each symbol: registry-lookup path vs string-comp path for `extract_abilities_from_component`, unique sub-string matching for `list_ship_abilities`, scalar and list inputs for `get_ability_list`.

---

### [MAJOR] `game/ui/screens/builder/weapons_viewmodel.py` — `calculate_tooltip_data`
- **Shard**: 05
- **Location**: weapons_viewmodel.py:443-494
- **Untested**: `calculate_tooltip_data` is MOCKED in tests (`vm.calculate_tooltip_data = Mock(return_value={...})`). The mock is never configured to call the real implementation. Untested edge cases: `weapon.get_ability('WeaponAbility')` returning None → `return None` (line 456-457), non-beam weapon path `acc_text = "N/A"` (line 486), `hover_range` clamping to `[0, weapon_range]` (line 460), `net_score` clamping to `[-20.0, 20.0]` (line 474), sigmoid `1.0 / (1.0 + math.exp(-clamped))` correctness (line 475), `_target_defense_mod` attribute usage (line 470).
- **Suggested test**: Direct parametrized tests for `calculate_tooltip_data` covering all 6 edge cases. Remove mock-based test setup or add real-implementation variant.

---

### [MAJOR] `game/strategy/data/planet.py` — `_deserialize_planet_orders`
- **Shard**: 05
- **Location**: planet.py:626-642
- **Untested**: `_deserialize_planet_orders` has zero direct tests. Tested indirectly through `Planet.from_dict` (37+ test files). Silent-skip of malformed entries (lines 640-641, `pass` on KeyError/TypeError/ValueError) is untested — no test verifies corrupt order data is silently dropped vs raising an error.
- **Suggested test**: Test `_deserialize_planet_orders` directly with valid orders, missing-key orders, and corrupt orders. Verify silent-drop behavior.

---

### [MINOR] `game/simulation/battle_controller.py` — `reset` missing `_initial_state` assertion
- **Shard**: 05
- **Location**: battle_controller.py:823
- **Untested**: `self._initial_state = None` in `reset()` is never asserted in any test. 4 other reset operations (service reset, config clear, state flags clear, tracking dicts clear) are verified.
- **Suggested test**: Add assertion `assert controller._initial_state is None` to existing reset tests.

---

### [MINOR] `game/strategy/data/classification_config.py` — Partial load failure paths
- **Shard**: 05
- **Location**: classification_config.py:157-173
- **Untested**: `get_classification_config()` fallback is tested for `FileNotFoundError`, but `KeyError`, `TypeError`, `ValueError` paths in the except clause (line 170) are untested. These represent corrupted JSON or missing keys in partial load.
- **Suggested test**: Parametrized test with mocked loader raising KeyError, TypeError, ValueError — verify fallback to defaults.

---

### [MINOR] `game/strategy/data/planet.py` — `get_staging_mass`
- **Shard**: 05
- **Location**: planet.py:342-344
- **Untested**: One-liner sum function with `.get('mass', 0.0)` fallback. Tested indirectly through staging yard operations. The edge case "items missing 'mass' key" is handled by the default. Low risk.
- **Suggested test**: Direct test with items missing 'mass' key, empty staging yard, and mixed keys.

---

### [MINOR] `game/strategy/engine/resupply_engine.py` — `_transfer_fuel`
- **Shard**: 05
- **Location**: resupply_engine.py:270-294
- **Untested**: `_transfer_fuel` has zero direct tests. Tested only indirectly through `process_fleet_resupply()` integration tests. The overflow guard at line 288 (`if actual <= 0: break`) is never directly triggered. Note: `_calculate_fuel_distribution` was claimed untested but HAS 5 direct tests (Phase 2 error).
- **Suggested test**: Direct test for `_transfer_fuel` with edge cases: zero available fuel, overflow triggering `break` guard, partial fill.

---

### [MINOR] `game/strategy/services/ability_sources/labels.py` — `format_intrinsic_source_label`
- **Shard**: 05
- **Location**: labels.py (23 LOC, single function)
- **Untested**: Returns f-string `f"{entity_name} ({ability_type})"`. Format contract unenforced.
- **Suggested test**: Verify format string output for given entity_name + ability_type inputs.

---

### [MINOR] `game/ui/screens/setup_data_io.py` — `_get_ship_factory` lazy init
- **Shard**: 05
- **Location**: setup_data_io.py:26-44
- **Untested**: `_get_ship_factory()` lazy initialization logic. Tests patch `_ship_factory` global directly, bypassing `_get_ship_factory()`. The lazy singleton cache guard is not directly unit tested. Reclassified from MAJOR to ADVISORY by verifier.
- **Suggested test**: Test `_get_ship_factory()` first-call (creates factory) and second-call (returns cached factory) behavior.

---

### [ADVISORY] `game/ui/screens/battle_setup/panels/center_panel.py` — pygame_gui construction
- **Shard**: 05
- **Location**: center_panel.py (299 LOC)
- **Untested**: pygame_gui elements constructed in `build()` and `_build_policy_controls()`. Impractical to unit test without pygame_gui harness.
- **Suggested test**: N/A — pure UI construction.

---

### [MAJOR] `game/ui/screens/battle_ui.py` — All 9 symbols
- **Shard**: 06
- **Location**: battle_ui.py:25-209 (entire file)
- **Untested**: `BattleUI` class — 209 LOC, 9 symbols, zero dedicated test coverage. Methods: `__init__`, `track_projectile`, `handle_resize`, `draw`, `handle_click`, `handle_scroll`, `draw_grid`, `draw_debug_overlay`. Test files `test_battle_ui_service.py` (tests `BattleUIService` — different class) and `test_battle_ui.py` (tests `IBattleUI` protocol — not the class). `handle_click` (dispatches to panels) and `handle_resize` (layout logic) are testable without pygame.
- **Suggested test**: `tests/unit/ui/screens/test_battle_ui.py` — minimum: `handle_click` dispatch to panels, `handle_resize` layout calculations, `track_projectile` filtering.

---

### [MAJOR] `game/simulation/entities/ship_combat_engine.py` — `select_target`, `calculate_firing_solution`
- **Shard**: 06
- **Location**: ship_combat_engine.py:99-126
- **Untested**: Both delegation methods are single-line pass-through to `TargetingSystem`, but no test verifies the delegation at the engine-facade level: `select_target(self, candidates)` → `self._targeting_system.select_target(self._ship, candidates)` and `calculate_firing_solution(self, comp, target)` → `self._targeting_system.calculate_firing_solution(self._ship, comp, target)`. The underlying `TargetingSystem` IS tested directly, but no smoke test verifies `self._ship` is correctly passed as the first argument through the engine facade.
- **Suggested test**: Smoke tests for `ShipCombatEngine.select_target` and `ShipCombatEngine.calculate_firing_solution` verifying correct `self._ship` argument forwarding to `TargetingSystem`.

---

### [MINOR] `game/simulation/replay/replay_player.py` — `run_replay_headless` unit test
- **Shard**: 06
- **Location**: replay_player.py:50
- **Untested**: Missing dedicated unit test. Function IS tested at integration level via `test_headless_visual_equivalence.py:122` (spec reconstruction, parameter forwarding, `capture_context=None`). 26-line function body. Downgraded from MAJOR to MINOR — low priority due to existing integration coverage.
- **Suggested test**: Consider dedicated unit test for `run_replay_headless` parameter-forwarding contract (low priority).

---

### [MINOR] `game/ui/panels/system_tree_panel.py` — `process_event`, `set_dimensions`
- **Shard**: 06
- **Location**: system_tree_panel.py:671, 708
- **Untested**: Only 2 genuinely untested symbols (not 10 as Phase 2 claimed). `process_event` (line 671, 8 lines of event-routing logic — no test sends `pygame_gui.UI_BUTTON_PRESSED` to panel) and `set_dimensions` (line 708, 3 lines of trivial delegation). 975+ LOC of test code exists across 3 test files for the 711 LOC production file. 4 other claimed-untested symbols (`set_position`, `show`, `hide`, `layout`) are implicitly tested through `set_items` → `layout` chain.
- **Suggested test**: Test `process_event` with `UI_BUTTON_PRESSED` event routing to `on_click`. Test `set_dimensions` resize delegation.

---

### [Tier 3 — Phase 1 FN] `game/simulation/replay/replay_record.py` — Fully covered (93 LOC)
- **Shard**: 05 (reclassified Tier 0→Tier 3)
- **Verified**: `TestReplayRecord` with roundtrip + mismatch + optional-None-field tests. `is_current_schema()` tested. Additional coverage in 4 other test files. No remaining gap.

---

### [Tier 3 — Phase 1 FN] `game/simulation/replay/replay_spec.py` — Public API covered (197 LOC)
- **Shard**: 05 (reclassified Tier 0→Tier 2)
- **Verified**: `from_battle_spec` both lookup paths, `to_battle_spec` strips snapshots, `to_dict` → `from_dict` roundtrip. Internal helpers `_capture_ships_in_team` and `_strip_instance_snapshots` tested indirectly. No remaining gap.

---

### [Tier 3 — Phase 1 FN] `game/simulation/entities/intrinsic_roll.py` — Fully covered (79 LOC)
- **Shard**: 06 (Phase 1 false negative → Tier 3)
- **Verified**: `test_intrinsic_roll.py` (157 LOC, 10+ test methods). FEAT-15 chance gates, rolling, pass-through. No remaining gap.

---

### [Tier 3 — Phase 1 FN] `game/strategy/generation/star.py` — Fully covered (69 LOC)
- **Shard**: 06 (Phase 1 false negative → Tier 3)
- **Verified**: `test_star.py` (136 LOC, 12+ test methods). Protocol conformance, edge cases. No remaining gap.

---

### [Tier 3 — Phase 1 FN] `game/strategy/generation/system_archetype.py` — Fully covered (53 LOC)
- **Shard**: 06 (Phase 1 false negative → Tier 3)
- **Verified**: `test_system_archetype.py` (68 LOC, 6 test methods). Round-trip serialization, protocol. No remaining gap.

---

## Summary by Severity

| Severity | Count | Shards |
|---|---|---|
| **CRITICAL** | 3 | 02 (workshop_data_reloader), 04 (fleet.py), 05 (background.py) |
| **MAJOR** | 13 | 01 (geometric), 02 (4), 04 (2), 05 (4), 06 (2) |
| **MINOR** | 18 | 02 (9), 03 (6), 04 (1), 05 (4), 06 (2) — Shard 05 has some overlap/cross-shard |
| **ADVISORY** | 4 | 02 (galaxy_mode, fleet_report_window, registry), 05 (center_panel) |
| **Tier 3 FN (no gap)** | 5 | 05 (replay_record, replay_spec), 06 (intrinsic_roll, star, system_archetype) |

**Total CONFIRMED gaps requiring action: 38** (3 CRITICAL + 13 MAJOR + 18 MINOR + 4 ADVISORY)

**Phase 1 false negatives resolved (already covered): 5**

## Discovery Agent Systemic Errors (Cross-Shard)

| Error Pattern | Affected Shards | Description |
|---|---|---|
| **Missed test files** | 01, 02, 03, 05 | Agent claimed Tier 0 for files with dedicated test suites. Root cause: searched by filename not class name; missed indirect test coverage through callers. |
| **Zero test files read** | 01, 03 | Phase 2 agent self-admitted reading 0 test files in some shards. Coverage claims without reading tests. |
| **Re-export chain blindness** | 04 | Phase 1 AST scanner couldn't resolve `command_handlers.py` → `handlers/` re-exports. Caused false CRITICAL/MAJOR claims for `build.py` and `construction_queue.py`. |
| **Indirect-call blind spot** | 04 | Scanner marked private `_validate_*` helpers as untested when called only through public `validate()`. |
| **Module confusion** | 02, 04 | Agent conflated similarly-named modules (e.g., `workshop_viewmodel_selection` vs `builder_selection`, `BattleUIService` vs `BattleUI`). |
| **Overstated coverage gap** | 02, 03, 05, 06 | Agent claimed untested branches that were tested (e.g., `get_tick_count`, `_calculate_fuel_distribution`, `system_tree_panel` symbol count). |
| **Wrong integration test cited** | 06 | Agent cited `test_battle_determinism.py` instead of `test_headless_visual_equivalence.py` for `run_replay_headless`. |
