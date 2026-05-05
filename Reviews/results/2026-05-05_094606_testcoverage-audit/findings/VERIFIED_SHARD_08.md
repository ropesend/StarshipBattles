# Shard 08 — Verified Coverage Findings

## Summary
- Shard: 08
- Claims reviewed: 28 (4 CRITICAL + 24 MAJOR)
- CONFIRMED: 10 | DISPUTED: 17 | INCONCLUSIVE: 1
- Severity downgrades: 2 (CRITICAL→ADVISORY for planet_gen, CRITICAL→ADVISORY for protocols/ui)
- Severity upgrades (ADVISORY→MAJOR): 0

## CONFIRMED Gaps

### game/assets/asset_manager.py (layer: assets)
- **Location**: `asset_manager.py:132-158`, `160-176`, `178-191`
- **Issue**: `load_star_image`, `get_star_core_info`, `get_star_asset_key_for_type` have zero unit test coverage. Star image resolution fallback chain, metadata lookup, and star-type-to-asset-key mapping are all untested. The existing `test_asset_manager.py` tests only `load_image`/`load_group`/`load_external_image`. The second test file `test_asset_manager_resolutions.py` tests *planet* image resolution (164 lines) but not star images. Two mock references in `test_strategy_screen_assets.py` are test-doubles, not tests of the methods themselves.
- **Suggested tests**: 
  1. `test_load_star_image_resolution_fallback` — mock all resolutions to fail, verify missing texture returned
  2. `test_get_star_core_info_known_star` — known star returns metadata dict
  3. `test_get_star_core_info_unknown_defaults` — unknown star returns default dict with centerX=0.5
  4. `test_get_star_asset_key_for_type` — MAIN_SEQUENCE → 'yellow'
- **Verified status**: CONFIRMED — 3 MAJOR findings accurate

### game/strategy/adapters/simulation_adapter.py (layer: strategy)
- **Location**: `simulation_adapter.py:330-336`
- **Issue**: `_resolve_seed` lazy creation of `_seed_rng` via `random.Random()` when `seed` is None. Zero test references found across entire test suite (grep for `_resolve_seed` in test files returned 0 matches). This path is exercised in production combat but has no deterministic test.
- **Suggested tests**: `test_resolve_seed_random_fallback` — call _resolve_seed with seed=None multiple times, verify different results
- **Verified status**: CONFIRMED — MAJOR finding accurate

### game/strategy/combat/post_battle_hook.py (layer: strategy)
- **Location**: `post_battle_hook.py:72-81`, `line ~129-132`
- **Issue**: Orphan outcome entry path (`apply_outcome_to_fleets` when no ShipInstance matches `instance_id`) is untested. Unknown `ShipStatus` warning path (line 129-132) is untested. Happy paths are thoroughly covered (514-line test file, 10 test methods) but defensive error paths are not.
- **Note**: The `_prune_empty_fleets` exception paths claim is partially disputed — the happy path (empty fleet removed from empire) IS tested in `test_empty_fleet_removed_from_empire_when_provided` and `test_missing_empires_param_does_not_crash`. However, the specific exception branches (empire not in dict, no `fleets` attr, `ValueError` during removal) are not tested.
- **Suggested tests**: `test_apply_outcome_orphan_ship` — outcome with non-existent instance_id → logged and skipped
- **Verified status**: CONFIRMED (orphan path only) — 1 of 2 MAJOR findings partially accurate. Exception paths in `_prune_empty_fleets` confirmed unverified.

### game/strategy/engine/game_session.py (layer: strategy)
- **Location**: `game_session.py:331-454`
- **Issue**: `from_dict` has multiple `PersistenceException` raise paths (missing config key, missing galaxy key, missing empire key) that are untested. The pursuer tracker rebuild (lines 442-448) conditional on `MOVE_TO_FLEET`/`JOIN_FLEET` order types also untested. The happy-path round-trip IS tested in integration tests (`test_game_session.py`, `test_game_session_save_load_registries.py`).
- **Suggested tests**: `test_from_dict_missing_config` — 'config' key missing raises PersistenceException
- **Verified status**: CONFIRMED — MAJOR finding accurate for error recovery paths

### game/strategy/engine/turn_phase_registry.py (layer: strategy)
- **Location**: `turn_phase_registry.py:129-149`
- **Issue**: Individual hook functions `_capture_move_queue`, `_derive_moved_fleet_ids` lack dedicated unit tests. These hooks are exercised only through integration (TurnEngine.process_turn goldentest). The golden order test (`test_default_tick_phase_list.py`) verifies the 15-phase descriptor list ordering but does not test individual hook behavior.
- **Suggested tests**: `test_capture_move_queue_populates_move_queue_and_pre_locations`
- **Verified status**: CONFIRMED — MAJOR finding accurate; hooks only tested via integration

### game/strategy/facade/dto/fleet_dto.py (layer: strategy)
- **Location**: `fleet_dto.py:103-219`
- **Issue**: `FleetInfo.from_fleet` has 6 order-type branches. MOVE (with HexCoord target) is tested at line 369-387. JOIN_FLEET is tested at line 389-411. However, BUILD, TRANSFER (load/unload), MOVE_TO_FLEET, COLONIZE (with Planet target or dict target), and MOVE/COLONIZE with dict target are untested.
- **Suggested tests**:
  1. `test_from_fleet_build_order` — BUILD order shows queue count
  2. `test_from_fleet_transfer_load_order` — TRANSFER load order description
  3. `test_from_fleet_colonize_planet_target` — COLONIZE with Planet target
- **Verified status**: CONFIRMED — MAJOR finding partially accurate; 2 of 6 order types tested, 4 untested

### game/ui/screens/atmosphere_target_editor.py (layer: ui)
- **Location**: `atmosphere_target_editor.py:244-260`
- **Issue**: `_set_species_ideal` has zero test references. PROJ-283 gas factor setpoint resolution from race config preferences is untested. This is testable business logic in a UI file.
- **Suggested tests**: `test_set_species_ideal_resolves_setpoints` — mock race_config preferences, verify slider values set
- **Verified status**: CONFIRMED — MAJOR finding accurate

## Disputed & Inconclusive Claims

| Original Finding | File | Severity | Verdict | Reason |
|---|---|---|---|---|
| Tier 0 — No unit test imports | game/core/protocols/ui.py | CRITICAL | **DISPUTED** → ADVISORY | 50 test matches across 5+ test files. `test_protocols.py` (line 311-360) tests ICamera/is_camera with 5 methods. `test_scene_protocol.py` tests IScene protocol compliance on 7 scene classes. `test_research_scene_di.py` imports ICamera. Protocol conformance IS tested. |
| Tier 0 — Zero test coverage | game/strategy/data/planet_gen.py | CRITICAL | **DISPUTED** → ADVISORY | `test_planet_gen.py` (731 lines, 30+ tests) imports `from game.strategy.data.planet_gen import PlanetGenerator`. Covers mass generation (4 tests), moon generation (7 tests), orbital slots (6 tests), surface flags (4 tests), type determination (10 tests covering ALL PlanetType variants), resource generation (11 tests), and system generation (3 tests). Integration tests in `test_planet_gen.py` (81 lines) also exercise the module. |
| _eval_distance_rule untested | game/ai/target_evaluator.py:41-78 | MAJOR | **DISPUTED** | `test_target_evaluator_rules.py` (1069 lines) has TestDistanceRules with 6 test methods including 4 parametrized tests covering nearest/farthest/distance with all weight/factor combinations, plus distance cache behavior. `test_target_evaluator_edge_cases.py` (523 lines) adds TestEvaluateDistanceCache, TestMigratedDistanceEdgeCases, TestEdgeCaseDefaultsMigrated. All indirectly through evaluate() — thorough coverage. |
| _eval_mass_rule untested | game/ai/target_evaluator.py:81-110 | MAJOR | **DISPUTED** | TestMassRules (test_target_evaluator_rules.py) has 5 test methods with parametrized mass/largest/strongest/smallest/weakest combinations. TestMigratedMassBehaviorEquivalence, TestMigratedStrengthRules confirm behavior. All 5 mass rule types tested. |
| _eval_damage_rule untested | game/ai/target_evaluator.py:137-166 | MAJOR | **DISPUTED** | TestDamageRules has 4 test methods: most_damaged prefers lower HP, least_damaged prefers higher HP, zero-value edge cases. TestEdgeCaseDefaultsMigrated adds default helper tests. TestThreatAssessmentMigrated tests armed+damaged combined scoring. |
| _eval_least_armor_rule untested | game/ai/target_evaluator.py:197-215 | MAJOR | **DISPUTED** | `test_least_armor_rule` (line 524-554) directly tests least_armor with heavy vs light armor comparison using `current_hp` attribute (not `hp` — matches production code fix). Non-combat-ship path tested indirectly via evaluate() with mock targets that have no armor components. |
| _eval_pdc_arc_rule untested | game/ai/target_evaluator.py:218-238 | MAJOR | **DISPUTED** | TestPDCArcRules (6 tests) + TestEvaluateMissileRules (3 tests) + TestMigratedPDCArcRequired (1 test) = 10 distinct PDC arc tests. Cover missile in arc, out of arc, required flag, non-missile pass-through, and missiles_in_pdc_arc alias. |
| _eval_capability_rule untested | game/ai/target_evaluator.py:241-263 | MAJOR | **DISPUTED** | Router function dispatches to sub-evaluators. Each sub-path tested via evaluate() with appropriate rule types: has_weapons (TestCapabilityRules, 5 tests), least_armor (1 test), pdc_arc (10 tests from above). |
| DEACTIVATING phase untested | game/strategy/data/component_activation_state.py:59-67 | MAJOR | **DISPUTED** | `test_tick_completes_deactivation` (line 155-166) directly tests deactivation completion: sets phase=DEACTIVATING, progress=149, required=150, energy_drain_rate=50.0. Runs tick() → asserts phase=INACTIVE, progress=0, energy_drain_rate=0.0. `test_full_activation_cycle` tests full INACTIVE→ACTIVATING→ACTIVE→DEACTIVATING→INACTIVE round-trip (250+150 ticks). |
| get_system_at_location 4-branch lookup untested | game/strategy/data/galaxy_spatial_index.py:108-143 | MAJOR | **DISPUTED** | TestGetSystemAtLocation (342-line test file) has 6 test methods: `test_returns_system_at_direct_location`, `test_returns_system_via_planet_index`, `test_returns_system_via_zone_index`, `test_returns_system_via_warp_point_index`, `test_returns_none_for_deep_space`, `test_priority_direct_system_over_planet`. All 4 branches tested. |
| process_atmosphere pipeline untested | game/strategy/engine/atmosphere_engine.py:40-51 | MAJOR | **DISPUTED** | `test_atmosphere_engine.py` (314 lines, 17 test methods) tests: no target (no change), moves toward target, does not overshoot, small planet changes faster, multiple facilities stack, can reduce gas, can add new gas, skips non-operational, no facility, earth-like rate, non-dict target, non-dict atmosphere, non-positive properties. Proportional distribution and no-overshoot behavior are directly verified. |
| _extract_atmo_modifier list data path | game/strategy/engine/atmosphere_engine.py:140-147 | MAJOR | **DISPUTED** | `test_list_form_atmosphere_modifier_rates_stack` (line 293-307) creates facility with list-form modifier `[{"modification_rate": 100.0}, {"modification_rate": 200.0}]`, verifies atmosphere changes proportional to summed rates (total rate=300, O2=3.0 Pa). Confirms list branch at line 72-73. |
| dump_crash_snapshot error path untested | game/strategy/engine/turn_state_snapshot.py:102-134 | MAJOR | **DISPUTED** | `test_dump_crash_snapshot_logs_oserror_without_raising` (line 182-199) directly patches `os.makedirs` to raise `OSError("disk full")`, calls `dump_crash_snapshot`, and asserts `"Failed to write crash snapshot"` + `"disk full"` appear in error logs. Both OSError and TypeError are caught at line 133. OSError path verified. |
| get_events_for_turn empire_id scoping | game/strategy/events/event_log.py:95-113 | MAJOR | **DISPUTED** | `test_get_events_for_turn_with_empire_id_kwarg` (line 473-483) tests empire_id=None (2 events from both empires) vs empire_id=0 (filters to empire 0 + global events). `test_get_events_for_turn_without_empire_id_unchanged` confirms old callers unaffected. All 3 branches (empire_id=None, empire_id scoped + global broadcast, no-match empty) tested. |
| get_events_by_category empire_id + category branch | game/strategy/events/event_log.py:115-142 | MAJOR | **DISPUTED** | `test_get_events_by_category_with_empire_id_kwarg` (line 494-503) tests 4 combinatorial branches. `test_get_events_by_category_all_with_empire_id_kwarg` tests ALL+empire_id. `test_get_events_by_category_without_empire_id_unchanged` verifies backward compat. Enum coercion path tested via mixed string/enum input (tests at line 171 and 197). |
| LinearPrimitive.evaluate spatial branches | game/strategy/generation/density/primitives/linear.py:37-86 | MAJOR | **DISPUTED** | `test_linear.py` (71 lines, 7 tests) covers: bar center peak density, along-bar density, perpendicular falloff, past-end falloff, output range [0,1] bounds, rotation affects orientation, zero-width edge case (only line has density). All spatial zones verified. |
| scan_abilities data-driven discovery | game/ui/screens/planet_abilities_controller.py:~80-150 | MAJOR | **DISPUTED** | `test_planet_abilities_controller_scanner.py` (11 test references) directly tests `scan_abilities()`: tests activation_time discovery, exclusion of components without activation_time, empty facilities, multi-ability components, and component without component_registry. Data-driven predicate verified. |
| _prune_empty_fleets exception paths | game/strategy/combat/post_battle_hook.py:200-218 | MAJOR | **PARTIALLY DISPUTED** | Happy path IS tested (`test_empty_fleet_removed_from_empire_when_provided`, `test_missing_empires_param_does_not_crash`). Exception branches (empire not in empires dict → continue, no `fleets` attribute → continue, ValueError during removal) are NOT explicitly tested. Downgraded: confirmed gap is minor (defensive branches). |
| _apply_field_state state machine | game/ui/panels/race_description_panel.py:358-418 | MAJOR | **INCONCLUSIVE** | Test file exists at `test_race_description_panel.py` and references `_apply_field_state` (lines 514, 546). Likely tests some states but full 5-branch coverage unverifiable without reading the full test file. Test file not read in this verification pass due to context budget constraints. |

## Discovery Agent Errors

1. **planet_gen.py marked CRITICAL Tier 0**: The Phase 2 discovery agent claimed "No unit test file imports this module. Tier 0." This is factually wrong. `tests/unit/strategy/data/test_planet_gen.py` (731 lines) directly imports `PlanetGenerator` and has 30+ test methods. `tests/integration/strategy/test_planet_gen.py` (81 lines) also exercises the module.

2. **protocols/ui.py marked CRITICAL Tier 0**: Agent claimed "No unit test file imports this module." The `IScene`, `ICamera`, and `is_camera` symbols are imported/used in 5+ test files with 50+ grep hits. Protocol compliance tests exist.

3. **TargetEvaluator methods all marked MAJOR untested**: All 6 evaluator method claims state features are "untested." In reality, the 1592 lines of test code (1069 + 523) exercise every rule type through `evaluate()`, with parametrized weight/factor combinations, edge cases, and combinatorial rule stacking. The methods are all `@staticmethod` and directly called by `evaluate()` — there's no meaningful distinction between "direct" vs "indirect" testing here.

4. **Over-claiming on extensively-tested modules**: The discovery agent marked 12 MAJOR claims on code that has substantial existing coverage (component_activation_state, galaxy_spatial_index, atmosphere_engine, turn_state_snapshot, event_log, linear_primitive, planet_abilities_controller). These modules have dedicated test files that test the exact features flagged. The agent appears to have missed or incompletely read the corresponding test files.

5. **Partial-accuracy findings**: For `post_battle_hook._prune_empty_fleets` and `FleetInfo.from_fleet`, the discovery agent was partially right (exception/edge branches untested) but overstated the gap by implying the happy path was also untested.
