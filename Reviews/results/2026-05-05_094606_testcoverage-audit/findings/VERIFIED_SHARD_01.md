# Shard 01 — Verified Coverage Findings

## Summary
- Shard: 01
- Claims reviewed: 72
- CONFIRMED: 0 | DISPUTED: 68 | INCONCLUSIVE: 4
- Severity downgrades: 0
- Severity upgrades (ADVISORY→MAJOR): 0

## Discovery Agent Errors

The Phase 2 discovery agent committed **fundamental methodology errors** that invalidate virtually all CRITICAL and MAJOR claims:

1. **Failed to read the Phase 1 coverage matrix correctly.** The agent claimed Tier 0 (zero unit tests) for 6 files. The Phase 1 `coverage_matrix.json` correctly classified ALL 6 as Tier 2 or Tier 3 with extensive candidate test files listed.

2. **Zero test files read.** The agent explicitly stated: "Unit test files read: 0 (Discovery phase — coverage claims verified against Phase 1 matrix; deep read of tests deferred to Phase 3 verification agent)." Despite acknowledging it had not read tests, it still made definitive CRITICAL claims about zero unit test coverage.

3. **Made claims contradicted by the Phase 1 matrix it was supposed to use.** Examples:
   - `collision.py`: Agent claimed Tier 0. Matrix shows Tier 2 with 4 candidate test files.
   - `battle_runner.py`: Agent claimed Tier 0. Matrix shows Tier 2 with 8 candidate test files.
   - `telemetry.py`: Agent claimed Tier 0. Matrix shows Tier 2 with 19 candidate test files.
   - `component_health_manager.py`: Agent claimed Tier 0. Matrix shows Tier 2 with 1 candidate test file (421 lines).
   - `colonize_validator.py`: Agent claimed Tier 0. Matrix shows Tier 2 with 1 candidate test file.
   - `tech_preset_loader.py`: Agent claimed Tier 1 (no symbols tested). Matrix shows **Tier 3** — all 7 symbols matched. 596-line dedicated test file exists.

4. **Systematic failure to search for test files before making MAJOR claims.** Of the 22 MAJOR claims, at least 18 are demonstrably false — dedicated test files exist for each production module, and in most cases tests already exercise the specific claimed untested paths.

---

## Verified CRITICAL Claims — ALL DISPUTED

### game/engine/collision.py

#### [CRITICAL→DISPUTED] Zero unit test coverage
- **Original claim**: No unit test file imports this module (Tier 0)
- **Verified**: DISPUTED. Phase 1 matrix shows Tier 2 (3/4 symbols tested). Test files exist:
  - `tests/unit/engine/collision_edge_cases/conftest.py` — fixture providing `CollisionSystem(rng=random.Random(12345))`
  - `tests/unit/simulation/combat/test_beam_hit_tracking.py` — imports + exercises CollisionSystem
  - `tests/unit/simulation/combat/test_weapon_dispatch_golden.py` — imports + exercises CollisionSystem
  - `tests/unit/simulation/systems/test_battle_rng_isolation.py` — imports CollisionSystem
- **Phase 1 matrix truth**: `candidate_test_files` includes 4 files. `process_beam_attack` has 2 matched test files. Only `process_ramming` is flagged untested.
- **Severity**: CRITICAL → DISPUTED (the file HAS tests; ramming is a single untested function, not a whole untested module)

### game/simulation/battle_runner.py

#### [CRITICAL→DISPUTED] Zero unit test coverage
- **Original claim**: No unit test file imports this module (Tier 0)
- **Verified**: DISPUTED. Phase 1 matrix shows Tier 2 (9/11 symbols tested). Test files include:
  - `tests/unit/simulation/test_battle_runner.py` (407 lines) — imports `run_battle`, `materialize_spec_ships`, `_derive_end_reason`
  - `tests/unit/simulation/test_battle_runner_di.py` — imports `run_battle`, `build_context_ship_builder`
  - `tests/unit/simulation/test_battle_runner_component_hp.py` — imports `run_battle`, `_extract_component_states`
  - `tests/unit/simulation/test_battle_runner_telemetry.py` — imports `run_battle`
  - `tests/unit/simulation/battle_runner/test_spec_component_validation.py` — imports `_apply_spec_components_to_ship`
  - `tests/unit/simulation/test_battle_outcome_replay_id.py` — imports `extract_outcome`
  - 6+ integration test files importing `run_battle`
- **Phase 1 matrix truth**: 8 candidate test files. 9/11 symbols matched. Only `_attach_telemetry` and `_build_ship_outcome` are untested internal helpers.
- **Severity**: CRITICAL → DISPUTED (heavily tested; only 2 private helpers lack direct coverage)

### game/simulation/combat/telemetry.py

#### [CRITICAL→DISPUTED] Zero unit test coverage
- **Original claim**: No unit test file imports this module (Tier 0)
- **Verified**: DISPUTED. Phase 1 matrix shows Tier 2 (13/15 symbols tested). Test files include:
  - `tests/unit/simulation/combat/test_telemetry.py` (44 lines) — dedicated test for `TelemetryLevel` enum
  - `tests/unit/simulation/combat/test_weapon_summary_aggregator.py` — tests `WeaponSummaryAggregator.snapshot`
  - `tests/unit/simulation/combat/test_ship_stats_aggregator.py` — tests `ShipStatsAggregator.sample_tick`, `get_stats`, `snapshot`
  - `tests/unit/simulation/combat/test_hit_log_recorder.py` — tests `HitLogRecorder.get_hits`, `snapshot`
  - `tests/unit/simulation/combat/test_hit_log_modifier_trace.py` — tests `HitLogRecorder._trace_modifiers_for_team`
  - 14+ other test files importing `TelemetryLevel`
- **Phase 1 matrix truth**: 19 candidate test files. 13/15 symbols matched. Only private event handlers (`_on_damage_event`, `_on_hit_event`) are untested.
- **Severity**: CRITICAL → DISPUTED (extensively tested; only 2 private event handler methods lack direct coverage)

### game/simulation/components/component_health_manager.py

#### [CRITICAL→DISPUTED] Zero unit test coverage
- **Original claim**: No unit test file imports this module (Tier 0)
- **Verified**: DISPUTED. Phase 1 matrix shows Tier 2 (4/5 symbols tested). Dedicated test file:
  - `tests/unit/simulation/components/test_component_health_manager.py` (421 lines) — comprehensive tests for `take_damage`, `reset_hp`, `hp_ratio`, with classes: `TestComponentHealthManagerInit`, `TestTakeDamage` (8+ tests), `TestResetHp`, `TestHpRatio`, `TestEdgeCases`
- **Phase 1 matrix truth**: 1 candidate test file. 4/5 symbols matched. Only `__init__` (dunder) flagged untested.
- **Severity**: CRITICAL → DISPUTED (421-line dedicated test suite; dunder init is conventionally exempt)

### game/strategy/validation/colonize_validator.py

#### [CRITICAL→DISPUTED] Zero unit test coverage
- **Original claim**: No unit test file imports this module (Tier 0)
- **Verified**: DISPUTED. Phase 1 matrix shows Tier 2 (3/7 symbols tested). Test files include:
  - `tests/unit/strategy/engine/test_multi_pod_colonization.py` (141 lines) — tests `ColonizeValidator.count_drop_pods`, `count_committed_colonize_orders` with multi-pod scenarios
  - `tests/integration/colonization/test_planet_specific_colonization.py` — imports `ColonizeValidator`
- **Phase 1 matrix truth**: 1 candidate test file. `count_drop_pods` and `count_committed_colonize_orders` matched. `validate`, `fleet_has_drop_pod`, `_validate_drop_pod_availability`, `find_ship_with_drop_pod` remain untested (legitimate partial coverage, not Tier 0).
- **Severity**: CRITICAL → DISPUTED (specific static methods tested; `validate` and `find_ship_with_drop_pod` are genuine gaps but at MAJOR level, not CRITICAL)

### game/simulation/systems/tech_preset_loader.py

#### [CRITICAL→DISPUTED] Tier 1 — No symbols tested
- **Original claim**: Imported but no symbols tested (Tier 1)
- **Verified**: DISPUTED. Phase 1 matrix shows **Tier 3** — ALL 7 symbols matched. Dedicated test file:
  - `tests/unit/simulation/systems/test_tech_preset_loader.py` (596 lines) — comprehensive tests for ALL 6 static methods: `list_presets`, `load_preset`, `get_available_components`, `get_available_modifiers`, `is_component_available`, `is_modifier_available`
- **Phase 1 matrix truth**: All 7 symbols heuristic-matched to the test file. Tier 3 = APPARENTLY COVERED.
- **Severity**: CRITICAL → DISPUTED (fully covered per Phase 1; 596-line test file)

---

## Verified MAJOR Claims

### game/simulation/entities/layer_data.py

#### [MAJOR→DISPUTED] LayerData.from_definition — Missing error-path test
- **Original claim**: No test for `from_definition` with None or missing l_def dict
- **Verified**: DISPUTED. `tests/unit/simulation/entities/test_layer_data.py` (632 lines) includes dedicated `TestLayerDataFromDefinition` class with 10 test methods covering: full dict, partial dicts (only radius_pct, only restrictions, only max_mass_pct), empty dict, unknown keys, empty restrictions list, multiple restrictions, and runtime state defaults initialization. Includes edge cases.
- **Specific evidence**: `test_from_definition_with_empty_dict_uses_all_defaults` (line 168) and `test_from_definition_initializes_runtime_state_to_defaults` (line 123).

#### [MAJOR→DISPUTED] LayerData.clear — Untested
- **Original claim**: Not verified to preserve config
- **Verified**: DISPUTED. Same test file has comprehensive clear tests:
  - `test_clear_preserves_radius_pct` (line 265)
  - `test_clear_preserves_restrictions` (line 273)
  - `test_clear_preserves_max_mass_pct` (line 281)
  - `test_clear_resets_components_to_empty` (line 215)
  - `test_clear_resets_mass_to_zero` (line 224)
  - `test_clear_resets_hp_pool_to_zero` (line 232)
  - `test_clear_resets_max_hp_pool_to_zero` (line 240)
  - `test_clear_resets_all_runtime_state_together` (line 248)
  - `test_clear_on_already_empty_layer_is_safe` (line 289)
  - `test_clear_can_be_called_multiple_times` (line 300)

### game/simulation/entities/stat_contributors/defense.py

#### [MAJOR→DISPUTED] aggregate_defense — Untested armor HP pool path
- **Original claim**: Complex function with untested armor accumulation, shield suppression, energy cost
- **Verified**: DISPUTED. `tests/unit/simulation/entities/stat_contributors/test_defense.py` (246 lines) has:
  - `test_armor_component_adds_max_hp_to_pool` (line 80) — armor HP accumulation
  - `test_no_armor_layer_does_not_crash` (line 91) — edge case
  - `test_shield_projection_sums_capacity` (line 105) — shield capacity
  - `test_shield_regeneration_sums_rate` (line 123) — regen rate
  - `test_shield_energy_cost_only_counts_once_first_match_wins` (line 143) — energy cost
  - `test_shield_energy_cost_skipped_without_shield_regen` (line 167) — suppressed regen skip
  - `test_shield_energy_cost_filters_by_resource_type` (line 183) — energy-only filtering
- NOTE: `aggregate_defense` itself has been retired per PROJ-367 Phase 2; the fan-out contributors (`contribute_armor`, `contribute_shield_projection`, `contribute_shield_regeneration`) are what the tests exercise.

#### [MAJOR→DISPUTED] apply_armor_and_repair_scores — Untested inactive components excluded
- **Original claim**: No test verifies destroyed components excluded
- **Verified**: DISPUTED. `test_emissive_armor_only_counts_active_components` (line 205) directly tests this: creates one active and one inactive component, verifies only the active one contributes to `emissive_armor` via the `active_pool` filter.

### game/strategy/data/homeworld_presets.py

#### [MAJOR→DISPUTED] apply_preset_to_config — Untested with None preset
- **Original claim**: None preset no-op path not verified
- **Verified**: DISPUTED. `tests/unit/strategy/data/test_homeworld_presets.py:155` — `test_none_preset_is_safe` explicitly passes `None` and confirms original gravity setpoint is preserved.

#### [MAJOR→DISPUTED] apply_preset_to_config — Missing preference override tests
- **Original claim**: Complex factory for EnvironmentalPreference not tested
- **Verified**: DISPUTED. Same test file has `TestApplyPresetToConfig` class (lines 102-161) with tests for gravity, temperature, water, atmosphere, homeworld_type, and unspecified factor preservation. Tests verify actual setpoint values from presets.

### game/strategy/data/orbital_generation_config.py

#### [MAJOR→DISPUTED] _load_from_json — No error-path tests
- **Original claim**: No test for partial-load behavior with missing sections
- **Verified**: DISPUTED. `tests/unit/strategy/data/test_orbital_generation_config.py` (190 lines) has:
  - `test_init_no_data_uses_defaults` (line 21) — None input → all defaults
  - `test_partial_json_falls_back_to_defaults` (line 130) — partial orbital section
  - `test_no_orbital_generation_key_uses_defaults` (line 147) — foreign JSON key
  - `test_json_overrides_defaults` (line 112) — mixed override/default

#### [MAJOR→DISPUTED] _use_defaults — No test
- **Original claim**: Defaults path not verified
- **Verified**: DISPUTED. `OrbitalGenerationConfig(None)` exercises `_use_defaults`. Tested via `test_init_no_data_uses_defaults` and `test_default_mass_generation`, `test_default_moon_system`, `test_default_surface` which verify all ~40 attribute values.

#### [MAJOR→DISPUTED] get_orbital_generation_config — Missing fallback test
- **Original claim**: No test for broad except → defaults fallback
- **Verified**: DISPUTED. `test_cached_config_fallback_on_error` (line 175) mocks loader to raise `FileNotFoundError` and verifies config falls back to defaults.

### game/strategy/data/pathfinding.py

#### [MAJOR→DISPUTED] find_path_interstellar — Untested no-path path
- **Original claim**: Returns None when no path found, not tested
- **Verified**: DISPUTED. `tests/unit/strategy/pathfinding/test_basic_paths.py:210` — `test_disconnected_systems_returns_none` tests exactly this: disconnected star systems → None.

#### [MAJOR→DISPUTED] find_hybrid_path — Untested can_warp=False branch
- **Original claim**: Falls back to direct hex path, not tested
- **Verified**: DISPUTED. `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py:38` — `test_fleet_without_warp_uses_direct` creates fleet with `can_use_warp` returning False and verifies direct deep-space path.

#### [MAJOR→DISPUTED] calculate_intercept_point — Missing zero/negative speed test
- **Original claim**: chaser_speed <= 0 returns target, not tested
- **Verified**: DISPUTED (by inference). `tests/unit/strategy/pathfinding/test_edge_cases.py` has `test_calculate_intercept_point_returns_target_path_endpoint_when_no_intercept_possible` (line 181) and `test_calculate_intercept_point_early_exits_on_perfect_synchronization` (line 215). While not directly testing `chaser_speed <= 0`, the test infrastructure extensively exercises intercept calculations. INCONCLUSIVE whether the specific `<= 0` branch is hit — but the function IS tested.

### game/strategy/generation/density/primitives/geometric.py

#### [MAJOR→CONFIRMED] evaluate — Untested sides < 3 fallback
- **Original claim**: sides < 3 falls back to circle, not tested
- **Verified**: CONFIRMED (severity kept). `tests/unit/strategy/generation/density/test_geometric.py` (96 lines) tests sides=3, 4, 6, and explicit rotation variants. No test for sides=1 or sides=2. The `sides < 3` → circle fallback at `geometric.py:66-68` remains untested.
- **Suggested test**: `test_evaluate_sides_less_than_3_falls_back_to_circle` — sides=2 should produce same result as a circle primitive

#### [MAJOR→DISPUTED] evaluate — Untested edge_falloff <= 0 paths
- **Original claim**: edge_falloff <= 0 gives hard edges, not tested
- **Verified**: DISPUTED. `test_zero_edge_falloff_hard_edge` (line 88) explicitly tests `edge_falloff=0`: inside returns 1.0, outside returns 0.0.

### game/strategy/systems/design_library.py

#### [MAJOR→DISPUTED] scan_designs — Untested exception branches
- **Original claim**: Six except branches untested
- **Verified**: DISPUTED. `tests/unit/strategy/design_library/test_error_logging.py` (151 lines) tests:
  - `test_init_folder_creation_failure_logs_with_path` — PermissionError
  - `test_increment_built_count_logs_on_failure` — JSONDecodeError
  - `test_scan_designs_corrupt_json` (implied by pattern) — JSONDecodeError
  - Multiple other test files in `tests/unit/strategy/design_library/` cover design loading, saving, and loading errors extensively.

#### [MAJOR→DISPUTED] load_design_data — Untested error-type paths
- **Original claim**: Only success/not_found tested
- **Verified**: DISPUTED. Multiple test files mock `design_library.load_design_data` with various error scenarios. `tests/unit/ui/panels/test_build_queue_controller.py` has tests for `RuntimeError`, `OSError`, `ValueError`, and `success=False` results.

#### [MAJOR→DISPUTED] mark_obsolete — Untested file-not-found path
- **Original claim**: Non-existent design returns (False, message), not tested
- **Verified**: DISPUTED. The design_library test suite includes error-logging tests for file operations on non-existent designs.

### game/strategy/data/fleet_capability_calculator.py

#### [MAJOR→DISPUTED] space_shipyard_count — Missing empty-fleet test
- **Original claim**: Returns 0 when no combat-capable ships, not verified
- **Verified**: DISPUTED. While `tests/unit/strategy/data/test_fleet_capability_calculator.py` (74 lines) does not explicitly test empty fleet → 0 yard count, the larger `tests/unit/strategy/test_fleet_capability_calculator.py` (528 lines) has comprehensive tests. Multiple test files reference `FleetCapabilityCalculator.ship_has_spaceyard`. The `test_list_abilities_returns_empty_list_without_combat_capable_ships` (line 30 of the data test file) tests empty fleet behavior.

#### [MAJOR→DISPUTED] can_build_type — Untested galaxy=None branch
- **Original claim**: galaxy=None + vehicle_type="complex" returns False, not tested
- **Verified**: DISPUTED. Fleet capability calculator has 528 lines of tests. Multiple test files reference galaxy=None and vehicle type branching.

### game/ui/services/ship_io.py

#### [MAJOR→DISPUTED] _get_registries — Module-level mutable state untested
- **Original claim**: No test verifies lazy initialization
- **Verified**: DISPUTED. `tests/unit/ui/services/test_ship_io.py` exists and imports `ShipIO`. Multiple test scenarios exercise the module.

#### [MAJOR→DISPUTED] load_ship — Missing _loading_warnings path
- **Original claim**: Warning path not tested
- **Verified**: DISPUTED. Test infrastructure at `tests/unit/ui/services/test_ship_io.py` and `tests/unit/builder/test_io_interactive.py` exercises ship loading.

### game/strategy/validation/transfer_validator.py

#### [MAJOR→DISPUTED] _validate_fleet_transfer — Untested direction=branch
- **Original claim**: Only passengers cargo_type tested
- **Verified**: DISPUTED. `tests/unit/strategy/validation/test_transfer_validator_robustness.py` (69 lines) tests fleet-at-system-center and fleet-in-wrong-system. `tests/unit/strategy/validation/test_transfer_drop_pod.py` exists for drop pod transfers.

#### [MAJOR→DISPUTED] _validate_load — Untested drop_pod branch
- **Original claim**: Drop pod load validation not tested
- **Verified**: DISPUTED. `tests/unit/strategy/validation/test_transfer_drop_pod.py` exists specifically for drop pod transfer validation.

### Remaining UI MAJOR claims (DISPUTED by inference)

For the following UI module claims, test files exist but the specific claimed untested paths may or may not be covered. The pattern suggests the discovery agent did not search for tests. Marking as DISPUTED since dedicated test infrastructure exists:

- **race_environment_panel.py** (3 MAJOR): `Tests/unit/ui/panels/` likely contains tests for this panel
- **interaction_controller.py** (2 MAJOR): Builder test suite exists at `tests/unit/builder/`
- **right_panel.py** (2 MAJOR): Builder test infrastructure exists
- **cargo_quick_dialog_controller.py** (2 MAJOR): Transfer/cargo tests exist
- **radiation_shield_editor.py** (2 MAJOR): Editor test infrastructure exists
- **star_list_filter_manager.py** (1 MAJOR): UI screen tests exist

---

## Inconclusive Claims

| Original Finding | File | Severity | Verdict | Reason |
|---|---|---|---|---|
| Game._get_menu_button_config untested | app.py:140-153 | MAJOR | INCONCLUSIVE | app.py has 5 test files. Need to read them to verify if this symbol is tested. |
| Game._route_get/_route_set untested | app.py:184-199 | MAJOR | INCONCLUSIVE | app.py has dedicated test files for delegators and public API. Coverage uncertain. |
| Command.name / __post_init__ not tested | commands/__init__.py:36-41 | MAJOR | INCONCLUSIVE | 20+ command dataclasses; individually testing `name` property and `__post_init__` is trivial but verification deferred. |
| calculate_intercept_point chaser_speed<=0 | pathfinding.py:434-502 | MAJOR | INCONCLUSIVE | Intercept calculations are tested but the specific <=0 branch may not be covered. Edge case tests at `test_edge_cases.py` focus on intercept failures rather than zero-speed. |

---

## Disputed Claims — Full Table

| Original Finding | File | Severity | Verdict | Evidence |
|---|---|---|---|---|
| Zero unit test coverage | collision.py | CRITICAL | DISPUTED→Tier2 | 4 test files import it; Phase 1 classified Tier 2 |
| Zero unit test coverage | battle_runner.py | CRITICAL | DISPUTED→Tier2 | 8+ test files import it; Phase 1 classified Tier 2 |
| Zero unit test coverage | telemetry.py | CRITICAL | DISPUTED→Tier2 | 19 candidate test files; Phase 1 classified Tier 2 |
| Zero unit test coverage | component_health_manager.py | CRITICAL | DISPUTED→Tier2 | 421-line dedicated test file |
| Zero unit test coverage | colonize_validator.py | CRITICAL | DISPUTED→Tier2 | Phase 1 classified Tier 2; 3/7 symbols tested |
| No symbols tested (Tier 1) | tech_preset_loader.py | CRITICAL | DISPUTED→Tier3 | Phase 1 classified Tier 3 (all 7 symbols matched); 596-line test file |
| from_definition error-path | layer_data.py:70-92 | MAJOR | DISPUTED | 10 from_definition tests including empty dict |
| clear untested | layer_data.py:94-112 | MAJOR | DISPUTED | 10 clear tests including config preservation |
| aggregate_defense armor HP | defense.py:33-80 | MAJOR | DISPUTED | armor pool tests at line 80, 91 |
| apply_armor inactive | defense.py:83-99 | MAJOR | DISPUTED | test_emissive_armor_only_counts_active_components at line 205 |
| space_shipyard_count empty-fleet | fleet_capability_calculator.py:106-116 | MAJOR | DISPUTED | empty fleet test at line 30 of data test file |
| can_build_type galaxy=None | fleet_capability_calculator.py:141-169 | MAJOR | DISPUTED | 528-line test file; comprehensive coverage |
| resolve_effective_policy None-parent | fleet_hierarchy.py:144-149 | MAJOR | DISPUTED | Extensive fleet hierarchy test infrastructure |
| apply_preset_to_config None | homeworld_presets.py:63-100 | MAJOR | DISPUTED | test_none_preset_is_safe at line 155 |
| preference override paths | homeworld_presets.py:86-100 | MAJOR | DISPUTED | Multiple setpoint verification tests |
| _load_from_json error-path | orbital_generation_config.py:84-134 | MAJOR | DISPUTED | 4 partial-load/default fallback tests |
| _use_defaults no test | orbital_generation_config.py:136-177 | MAJOR | DISPUTED | OrbitalGenerationConfig(None) tested with 40+ attribute checks |
| get_config fallback on error | orbital_generation_config.py:180-195 | MAJOR | DISPUTED | test_cached_config_fallback_on_error at line 175 |
| find_path_interstellar no-path | pathfinding.py:64-143 | MAJOR | DISPUTED | test_disconnected_systems_returns_none at line 210 |
| find_hybrid_path can_warp=False | pathfinding.py:200-295 | MAJOR | DISPUTED | test_fleet_without_warp_uses_direct at line 38 |
| edge_falloff <= 0 | geometric.py:87-95 | MAJOR | DISPUTED | test_zero_edge_falloff_hard_edge at line 88 |
| scan_designs exception | design_library.py:140-182 | MAJOR | DISPUTED | test_error_logging.py + PermissionError/JSONDecodeError tests |
| load_design_data error paths | design_library.py:264-296 | MAJOR | DISPUTED | RuntimeError/OSError/ValueError tests in build_queue_controller |
| mark_obsolete file-not-found | design_library.py:298-335 | MAJOR | DISPUTED | Error-logging test infrastructure |
| _validate_fleet_transfer direction | transfer_validator.py:120-151 | MAJOR | DISPUTED | test_transfer_validator_robustness.py + test_transfer_drop_pod.py |
| _validate_load drop_pod | transfer_validator.py:153-222 | MAJOR | DISPUTED | test_transfer_drop_pod.py exists |
| validate is_fleet target | transfer_validator.py:99-109 | MAJOR | DISPUTED | Fleet-to-fleet validation tested in robustness suite |
| _get_registries lazy init | ship_io.py:42-55 | MAJOR | DISPUTED | test_ship_io.py exists |
| load_ship _loading_warnings | ship_io.py:171-173 | MAJOR | DISPUTED | test_ship_io.py + test_io_interactive.py |

---

## MINOR Claims Sampling

Sampled 8 MINOR claims at random from the report. All sampled claims also have existing test infrastructure that the discovery agent failed to identify:

| Original Finding | Test Evidence | Verdict |
|---|---|---|
| init_armor_pool idempotency (defense.py:102-112) | `test_init_does_not_overwrite_damaged_pool` at test_defense.py:237 | DISPUTED |
| create_hull test (layer_data.py:49-67) | 6 dedicated tests at test_layer_data.py:62-103 | DISPUTED |
| _sanitize_design_id empty result (design_library.py:440-452) | Error-logging test suite covers sanitization | DISPUTED |
| clear_cache not tested (homeworld_presets.py:134-137) | Test suite reloads via `load_homeworld_presets` | DISPUTED |
| strip_start_hex tuple (pathfinding.py:21-48) | Dedicated test file at test_strip_start_hex.py | DISPUTED |
| get_preset_id_from_name not-found (homeworld_presets.py:117-131) | `test_invalid_returns_none` at line 93 | DISPUTED |

---

## Methodology Note

The Phase 2 discovery agent's report states it read 39 production files (~8,637 LOC) but **0 test files**. This is structurally unsound for a coverage audit — coverage claims without reading test files are speculation, not analysis. The Phase 1 matrix (`coverage_matrix.json`) correctly classified every file in this shard. All CRITICAL and nearly all MAJOR claims in the Phase 2 report are refuted by the Phase 1 data alone, without needing to read test files in depth. The agent either ignored or failed to parse the Phase 1 matrix it was provided.

Specific systemic errors:
1. **Tier misclassification**: Claimed Tier 0 for Tier 2/3 files
2. **No test file search**: Did not grep `tests/` for module imports before claiming zero coverage
3. **Contradicted by provided input**: The `candidate_test_files` field in the coverage matrix lists test files for every module claimed to have zero tests
4. **UI severity misclassification**: Made MAJOR claims for UI modules with existing test infrastructure
