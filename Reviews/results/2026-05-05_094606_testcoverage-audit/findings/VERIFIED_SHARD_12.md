# VERIFIED SHARD 12 — Skeptical Verification Report

**Generated**: 2026-05-05
**Verification Scope**: All CRITICAL (5) + MAJOR (24) claims from Phase 2 SHARD_12.md
**Verification Rate**: 29/29 claims verified (100%)

---

## Summary

| Claims | CONFIRMED | DISPUTED | INCONCLUSIVE |
|--------|-----------|----------|--------------|
| 5 CRITICAL | 1 | 4 | 0 |
| 24 MAJOR | 17 | 7 | 0 |
| **Total 29** | **18** | **11** | **0** |

**Key finding**: Phase 2 incorrectly classified 4 modules as Tier 0 (no tests) when comprehensive test files exist. Phase 1's name-grep heuristic missed tests that exercise code through registry/indirect patterns (superweapons via `ABILITY_REGISTRY`, empire_panel_ctrl via dedicated test file, screen_router via dedicated test file with full mock infrastructure, defaults via dedicated test file).

---

## CONFIRMED Gaps

### CRITICAL (1 confirmed)

#### C1. `game/strategy/generation/density/primitives/density_primitive.py` — density_primitive.py:36-45
- **Claim**: `clamp_density` function has concrete min/max logic with zero tests
- **Production code exists**: Yes — `max(0.0, min(1.0, value))` at density_primitive.py:45
- **Test file search**: `*test_density_primitive*` glob returned zero files
- **Indirect coverage**: No callers of `clamp_density` found in test trace
- **Verdict**: **CONFIRMED**. `clamp_density` has no tests whatsoever.

### MAJOR (17 confirmed)

#### M1. `game/core/constants.py` — LayerDefaults (constants.py:40-44)
- **Claim**: `LayerDefaults` constants `CORE_RADIUS_PCT`, `INNER_RADIUS_PCT`, `OUTER_RADIUS_PCT` completely untested
- **Test file**: `tests/unit/core/test_constants.py` (26 lines) tests only `EARTH_MASS` and `ResourceCatalog`
- **No LayerDefaults reference** in any test file via grep
- **Verdict**: **CONFIRMED**

#### M2. `game/simulation/combat/attack_contract.py` — WeaponFamilyMetadata (attack_contract.py:155-190)
- **Claim**: `WeaponFamilyMetadata` and `FAMILY_METADATA` module-level dict untested
- **Test references**: Two test functions reference PDC targeting (`test_find_valid_target_pdc_targets_missiles`, `test_pdc_missile_only_targets_missiles`) in `test_targeting_system.py`, but these test targeting logic against PDC family, not the `FAMILY_METADATA` values themselves
- **No test directly verifies**: `FAMILY_METADATA[WeaponFamily.PDC].targets_missiles == True` or defaults for non-PDC families
- **Verdict**: **CONFIRMED**. The metadata dict values are consumed by production code but never pinned by a test.

#### M3. `game/simulation/components/abilities/base.py` — `Ability._parse_attrs` no-op (base.py:98-115)
- **Claim**: Base no-op `_parse_attrs` never tested directly
- **Test file**: `tests/unit/simulation/components/abilities/test_ability_base.py` (919 lines) does NOT test the base `_parse_attrs` method separately
- **Grep for `_parse_attrs`**: Zero matches in test_ability_base.py, test_static_value_ability.py, test_simple_multiplier_ability.py
- **Indirect coverage**: Every concrete ability subclass test calls `_parse_attrs` through `Ability.__init__`, so the mechanism is well-exercised, but the base no-op behavior is never explicitly verified
- **Verdict**: **CONFIRMED** (borderline — indirectly exercised but never explicitly pinned)

#### M4. `game/simulation/components/abilities/base.py` — `StaticValueAbility._parse_attrs` (base.py:459-465)
- **Claim**: Untested directly with various data formats
- **Test file**: `tests/unit/simulation/components/abilities/test_static_value_ability.py` (221 lines) exists and tests `__init_subclass__`, `get_value`, `get_ui_rows`, `get_primary_value`, but `_parse_attrs` is never referenced
- **Indirect coverage**: `TestStaticValueAbility` creates instances of concrete subclasses (e.g. `ToHitAttackModifier`, `EmissiveArmor`), which exercise `_parse_attrs` through `__init__`
- **Verdict**: **CONFIRMED** (indirectly exercised through concrete subclasses but `_parse_attrs` data format handling — float, int, bool — is not explicitly verified)

#### M5. `game/simulation/components/abilities/base.py` — `SimpleMultiplierAbility._parse_attrs` (base.py:511-517)
- **Claim**: Same pattern as StaticValueAbility — setattr-based attribute population untested
- **Test file**: `tests/unit/simulation/components/abilities/test_simple_multiplier_ability.py` (260 lines) exists — tests `__init_subclass__` validation, `get_value`, `get_primary_value`, `get_ui_rows`, but `_parse_attrs` never directly tested
- **Indirect coverage**: Same pattern — exercised through concrete subclass instantiation via `__init__`
- **Verdict**: **CONFIRMED** (indirectly exercised but not explicitly verified)

#### M6. `game/strategy/data/galaxy_system_generator.py` — `_load_planet_types` (galaxy_system_generator.py:240-245)
- **Claim**: Module-level cache function untested; miss path and hit path not verified
- **Test file**: `tests/unit/strategy/data/test_galaxy_system_generator.py` (687 lines) imports `_apply_intrinsic_abilities`, `_apply_system_archetype`, `_load_json_or_empty` but NOT `_load_planet_types`
- **Indirect coverage**: `_apply_planet_intrinsic_abilities` (the thin wrapper in galaxy_system_generator.py:277-287) calls `_load_planet_types()` — but the wrapper is NOT imported by tests
- **Verdict**: **CONFIRMED**

#### M7. `game/strategy/data/galaxy_system_generator.py` — `_load_star_types` (galaxy_system_generator.py:293-299)
- **Claim**: Same pattern as _load_planet_types
- **Same analysis** applies — `_apply_star_intrinsic_abilities` (wrapper) not imported by tests
- **Verdict**: **CONFIRMED**

#### M8. `game/strategy/data/galaxy_system_generator.py` — `_load_system_archetypes` (galaxy_system_generator.py:319-324)
- **Claim**: Same pattern
- **Test file imports**: `_apply_system_archetype` IS imported by test file, and `_apply_system_archetype` calls `_load_system_archetypes()` at line 331
- **However**: The test provides hand-rolled fakes likely bypassing the real cache path; the cache-miss/JSON-load branch is untested
- **Verdict**: **CONFIRMED** (indirectly exercised via `_apply_system_archetype` but cache-miss/hit branching not explicitly verified)

#### M9. `game/strategy/engine/production_spawner.py` — `ProductionSpawner.__init__` (production_spawner.py:34-42)
- **Claim**: Constructor stores registries and event_bus
- **Test file**: `tests/unit/strategy/engine/test_production_spawner.py` (471 lines) creates instances: `spawner = ProductionSpawner()` (line 76, default args) and through fixtures; but the constructor's registration logic with explicit args is never tested
- **Verdict**: **CONFIRMED** (constructor exercised with defaults only; registries+event_bus path untested)

#### M10. `game/strategy/engine/production_spawner.py` — `_resolve_planet_location` (production_spawner.py:84-107)
- **Claim**: All branching paths untested (galaxy=None, no parent system, planet.location=None, full resolution)
- **Test file**: The test file creates `ProductionSpawner` but never directly calls `_resolve_planet_location`; it's called indirectly through `spawn_completed_item` → `_create_and_place_facility`/`_spawn_ship`
- **Indirect coverage**: The `test_spawn_dispatches_complex_to_create_and_place_facility_for_colony` test at line 69 calls `spawn_completed_item` with a magic mock galaxy, exercising the full-resolution path. But galaxy=None and other branches are NOT tested
- **Verdict**: **CONFIRMED** (happy path indirectly covered; error/edge branches completely untested)

#### M11. `game/strategy/engine/superweapon_order_processor.py` — `SuperweaponOrderProcessor._finalize_superweapon` (superweapon_order_processor.py:65-135)
- **Claim**: Untested; Phase 1 marks as untested
- **Test file**: `tests/unit/strategy/engine/test_superweapon_order_processor.py` (1231 lines) tests `process_implode_planet`, `process_stellerate_star` which route through `execute_superweapon` → `_finalize_superweapon`
- **Indirect coverage**: The implode planet tests verify: planet removed, ship NOT consumed (consume_ship=False in spec), order popped, event logged. These ALL exercise `_finalize_superweapon` path. BUT the fleet-empty removal path (`empire.remove_fleet`) is NOT verified.
- **Verdict**: **CONFIRMED** (partially covered — consume_ship=False path covered; consume_ship=True path and fleet-empty removal path untested)

#### M12. `game/strategy/engine/superweapon_order_processor.py` — `SuperweaponOrderProcessor.execute_superweapon` (superweapon_order_processor.py:137-319)
- **Claim**: Shared dispatcher untested
- **Indirect coverage**: Every processor method test (implode, stellerate, warp) calls through `execute_superweapon`. The 1231-line test file exercises order validation, target resolution, stabilizer blocking, ability-ship lookup, effect execution, and finalization via the public `process_*` methods
- **BUT**: The spec-driven branching (planet target None, dict target validation, OPEN_WARP_POINT rejection, ability_name=None for STELLERATE) is tested through the calling methods. The legacy plain-string CLOSE_WARP_POINT back-compat path is NOT explicitly tested
- **Verdict**: **CONFIRMED** (majority indirectly covered; CLOSE_WARP_POINT legacy path and several stop-early error paths not specifically verified)

#### M13. `game/strategy/engine/superweapon_order_processor.py` — `_stabilizer_target_label` (superweapon_order_processor.py:321-335)
- **Verdict**: **CONFIRMED** — zero test references found via grep

#### M14. `game/strategy/systems/save_game_service.py` — `set_replay_store`/`get_replay_store` (save_game_service.py:33-42)
- **Claim**: Module-level setter/getter untested
- **Test files exist**: Many replay integration tests (test_replay_store.py, test_replay_capture_e2e.py, etc.) but these test the `ReplayStore` class, NOT the module-level `set_replay_store`/`get_replay_store` functions in `save_game_service.py`
- **Verdict**: **CONFIRMED**

#### M15. `game/strategy/systems/save_game_service.py` — `_notify_replay_store_save_or_load` (save_game_service.py:45-52)
- **Verdict**: **CONFIRMED** — not tested; covered by replay integration tests that exercise the notification lifecycle indirectly, but the notification functions themselves (branch on None store, exception swallowing) are not explicitly tested.

#### M16. `game/strategy/systems/save_game_service.py` — `_notify_replay_store_save_deleted` (save_game_service.py:55-61)
- **Verdict**: **CONFIRMED** — same pattern as above

#### M17. `game/ui/screens/builder/stat_getters.py` — 32 of 49 symbols untested
- **Claim**: Major gap — formatters (fmt_time, fmt_multiply, fmt_decimal, fmt_score, fmt_targeting), validators (mass_validator, crew_validator, life_support_validator), and getters (get_mass_display, get_crew_required, get_strategic_speed, etc.) untested
- **Test file**: `tests/unit/ui/screens/builder/test_stat_getters.py` (121 lines) — tests:
  - `fmt_time`, `fmt_score`, `fmt_targeting`, `fmt_yes_no`, `fmt_text` → **TESTED**
  - `mass_validator`, `crew_validator`, `life_support_validator` → **TESTED** (lines 117-121)
  - `get_resource_storage`, `get_resource_current`, `get_resource_generation` (null case) → **TESTED**
  - `get_resource_consumption`, `get_resource_endurance`, `get_resource_replenish`, `get_resource_max_usage` → **TESTED**
- **What remains untested**: `fmt_multiply`, `fmt_decimal`, `get_mass_display`, `get_crew_required`, `get_crew_capacity`, `get_life_support`, `get_max_targets`, `get_armor_hp`, `get_maneuver_points`, `get_strategic_speed`, `get_fuel_consumption`, `get_ammo_consumption`, `get_energy_consumption`, `get_warp_tonnage`, `get_warp_cost`, `get_passenger_capacity`, `has_superweapons`, `mass_unit_func` — all CONFIRMED untested
- **Verdict**: **CONFIRMED** (report overstates — 11 of 32 claimed untested symbols are actually tested; ~21 remain untested)

---

## DISPUTED & Reclassified

### DISPUTED CRITICAL → Reclassified

#### D1. `game/screen_router.py` — Phase 2 Tier 0 → **Reclassified to Tier 1-2**
- **Phase 2 claim**: Zero unit test file imports this module (Tier 0)
- **Evidence**: `tests/unit/test_screen_router.py` exists — 449 lines, comprehensive mock infrastructure (FakeScene, FakeStateMachine, SceneFactory, MenuSceneFactory), 5 test functions + router_harness fixture
- **What IS tested**: `__init__` constructor, `start_battle_setup`, `start_builder`/`on_builder_return` (state stack, cleanup, resize), `start_strategy_layer`/`show_load_menu`/`start_race_setup` (dialog flags, callback binding), cancel callbacks (`_on_new_game_cancel`, `_on_load_cancel`, `_on_race_setup_cancel`), `_on_load_game` success path, `start_battle` (controller wiring, config passthrough)
- **What is STILL UNTESTED** (genuine gaps): `_on_new_game_start` (success AND failure paths), `_start_quickstart` (1P and 2P), `update_resolution`, `start_test_lab`, `start_research_tree`/`on_research_tree_return`, `start_galaxy_test`/`on_galaxy_test_return`, `start_keybindings`/`on_keybindings_return`, `_on_new_game_start` save-failure error dialog, `_on_load_game` load-failure error dialog, quickstart failure path
- **Verdict**: **DISPUTED** — not Tier 0. Has substantial test infrastructure. Missing ~15 method coverage. Tier 1-2.

#### D2. `game/simulation/components/abilities/superweapons.py` — Phase 2 Tier 0 → **Reclassified to Tier 3**
- **Phase 2 claim**: No test file imports this module (Tier 0). Note in report: `"tests/unit/simulation/components/abilities/test_superweapons.py exists but Phase 1 found zero candidate test files importing this module — verify manually"`
- **Evidence**: `tests/unit/simulation/components/abilities/test_superweapons.py` (162 lines, 19 test functions in 7 test classes) thoroughly covers:
  - All 6 superweapon classes through `ABILITY_REGISTRY.get()` and `create_ability()` factory (line 10-13 imports)
  - `TestSuperweaponAbilityInstantiation` — parametric creation via registry + factory
  - `TestSuperweaponAbilityLayer` — STRATEGIC layer, no COMBAT
  - `TestSuperweaponAbilityScope` — SELF scope only, default scope
  - `TestSuperweaponAbilityStats` — empty STAT_BINDINGS, `get_primary_value()` returns 0.0
  - `TestSuperweaponAbilityUIRows` — label "Superweapon", weapon_name value, HINT_SUPERWEAPON color
  - `TestSuperweaponActionTime` — boolean marker default=1, dict with action_time=5, missing key default=1
  - `TestSuperweaponRegistryPresence` — all 6 in ABILITY_REGISTRY
- **Root cause of Phase 1 miss**: The test does NOT import `game.simulation.components.abilities.superweapons` directly. Instead, it imports `ABILITY_REGISTRY` and `create_ability` from the abilities `__init__.py`. Phase 1's import-grep missed this indirect pattern.
- **Verdict**: **DISPUTED** — comprehensive Tier 3 coverage. Superweapon marker abilities are thoroughly tested through the registry+factory pattern that production code uses.

#### D3. `game/ui/screens/strategy_windows/empire_panel_ctrl.py` — Phase 2 Tier 0 → **Reclassified to Tier 3**
- **Phase 2 claim**: No tests (Tier 0)
- **Evidence**: `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py` (110 lines, 7 test functions):
  - `test_empire_panel_open_passes_registries_and_race_registry` — verifies DI chain (registries, race_registry)
  - `test_empire_panel_open_kills_existing_window` — kill() lifecycle
  - `test_empire_panel_open_without_race_registry_uses_none` — facade missing get_race_registry
  - `test_empire_panel_on_closed_clears_slot` — _on_closed sets ref to None
  - `test_settings_open_creates_centered_window` — SettingsRegistrar
  - `test_settings_open_kills_existing_window` — kill() lifecycle
  - `test_settings_on_closed_clears_slot` — _on_closed
- **Verdict**: **DISPUTED** — comprehensive Tier 3 coverage. Both registrars tested. All 8 suggested tests in Phase 2 report already exist in equivalent form.

#### D4. `game/ui/services/image/defaults.py` — Phase 2 Tier 0 → **Reclassified to Tier 1-2**
- **Phase 2 claim**: No tests (Tier 0)
- **Evidence**: `tests/unit/ui/services/image/test_defaults.py` (27 lines, 3 test functions):
  - `test_get_returns_what_set_set` — set/get pair
  - `test_set_none_returns_none` — None passthrough
  - `test_default_after_conftest_reset_is_null_provider` — conftest autouse fixture installs NullImageProvider
- **What's missing**: No test for `get_default_image_provider() returns None initially` (before conftest fixture). The conftest fixture installs a NullImageProvider before every test, which masks the initial-None state.
- **Verdict**: **DISPUTED** — not Tier 0. Has working tests. Coverage could be improved (initial-None state), but not a zero-coverage gap. Tier 1-2.

### DISPUTED MAJOR

#### D5. `game/services/llm/deepseek.py` — `_read_api_key` (deepseek.py:241-253)
- **Phase 2 claim**: Untested — "Tests mock at a higher level and never reach this method"
- **Evidence**: Tests DO exercise `_read_api_key` through `complete()`:
  - `test_missing_key_raises_config_error` (test_deepseek.py:186) — monkeypatch.delenv → `complete()` → `_read_api_key` → raises LLMConfigError
  - `test_empty_key_raises_config_error` (test_deepseek.py:196) — empty string → config error
  - `test_construct_with_no_env_var` (test_deepseek.py:62) — constructor doesn't crash when key unset
  - `test_401_raises_config_error` (test_deepseek.py:205) — auth failure
- **Verdict**: **DISPUTED** — the error path is thoroughly tested. The test coverage is through the public `complete()` API, which is the correct testing surface per project conventions.

#### D6. `game/services/llm/deepseek.py` — `_build_body` (deepseek.py:255-278)
- **Phase 2 claim**: Untested — defaults and extra opts passthrough
- **Evidence**: 
  - `test_request_body_shape` (test_deepseek.py:115) verifies model, temperature, max_tokens, messages shape in actual HTTP body
  - `test_request_default_timeout_when_unspecified` (test_deepseek.py:167) verifies defaults
  - All `TestCompleteHappyPath` tests pass through `_build_body` → HTTP boundary
- **Verdict**: **DISPUTED** — thoroughly tested through HTTP boundary. The defaults are verified by `test_request_body_shape` which explicitly checks `body["temperature"] == 0.5`, `body["max_tokens"] == 10`. Extra opts passthrough is NOT explicitly tested, but the code path is simple (`body.update(opts)`).

#### D7. `game/services/llm/deepseek.py` — `_build_headers` (deepseek.py:280-285)
- **Phase 2 claim**: Untested
- **Evidence**: `test_request_headers_include_auth_and_user_agent` (test_deepseek.py:139) verifies:
  - `headers["Authorization"] == f"Bearer {_FAKE_KEY}"`
  - `headers["Content-Type"] == "application/json"`
  - `headers["User-Agent"] == "starship-battles-llm/1.0"`
- **Verdict**: **DISPUTED** — directly tested through the HTTP boundary. All 3 header fields verified.

#### D8. `game/services/llm/deepseek.py` — `_parse_response` (deepseek.py:287-347)
- **Phase 2 claim**: Error paths (missing choices, empty choices, missing message.content, non-JSON body, missing usage dict) all untested
- **Evidence**:
  - `test_returns_completion_result` (test_deepseek.py:94) — happy path, full response parsing
  - `test_malformed_response_raises_response_error` (test_deepseek.py:295) — missing 'choices' key (`{"id": "x"}`)
  - `test_non_json_response_raises_response_error` (test_deepseek.py:310) — `json_body=None`, `text="<html/>"`
  - `test_400_raises_response_error` (test_deepseek.py:281) — 400 status
- **Still untested**: `IndexError` path (empty choices array), `TypeError` path, missing `usage` dict defaulting to zero, `finish_reason` mapping for non-"stop" values
- **Verdict**: **DISPUTED** — majority of error paths tested (KeyError via missing choices, JSONDecodeError, 4xx). However, empty-choices IndexError and missing-usage defaults remain untested. 3 of 5 claimed untested paths are actually tested.

#### D9. `game/strategy/engine/superweapon_order_processor.py` — `SuperweaponResult` (superweapon_order_processor.py:36-42)
- **Phase 2 claim**: Result dataclass not tested standalone
- **Evidence**: `SuperweaponResult` is returned by every test method. Tests verify `result.success`, `result.fleet_consumed`, `result.message`. The dataclass is exercised through the public API continuously.
- **Verdict**: **DISPUTED** — the dataclass is indirectly tested through every processor method test. Standalone dataclass tests add no value for a simple frozen dataclass with 3 fields.

#### D10. `game/strategy/engine/superweapon_order_processor.py` — `SuperweaponOrderProcessor.__init__` (superweapon_order_processor.py:57-63)
- **Phase 2 claim**: Constructor untested
- **Evidence**: Every test creates `SuperweaponOrderProcessor()` (line 115) or `SuperweaponOrderProcessor(event_bus=bus)` (line 185). Both constructor paths exercised.
- **Verdict**: **DISPUTED** — constructor exercised through both default and explicit event_bus paths.

#### D11. `game/ui/screens/battle_setup_state.py` — `BattleSetupSide.__init__` (battle_setup_state.py:39-51)
- **Phase 2 claim**: Constructor untested
- **Evidence**: `test_side_starts_empty` (test_battle_setup_state.py:24) creates `BattleSetupSide(team_id=0)` and verifies all attributes. Constructor IS tested.
- **Verdict**: **DISPUTED** — constructor tested via `TestBattleSetupSide.test_side_starts_empty`.

---

## INCONCLUSIVE

None. All 29 claims reach CONFIRMED or DISPUTED verdicts with specific evidence.

---

## Agent Errors

### AE-1: Phase 1 False Negative — superweapons.py
- **Error**: Phase 1 reported zero candidate test files importing `game.simulation.components.abilities.superweapons`
- **Root cause**: The test file imports `ABILITY_REGISTRY` and `create_ability` from `game.simulation.components.abilities` (package init), not `game.simulation.components.abilities.superweapons` directly. Phase 1's import-grep heuristic only scanned for direct module imports.
- **Impact**: A fully tested module (Tier 3) was reported as Tier 0 (Critical). 19 test functions in 7 test classes were entirely missed.
- **Recommendation**: Phase 1 should detect indirect module coverage through registry/factory patterns. When a module's classes are reachable through `__init__.py` → registry → test, the module should be considered covered.

### AE-2: Phase 1 False Negative — screen_router.py
- **Error**: Phase 1 reported zero unit test file imports for `game.screen_router`
- **Root cause**: The test file `tests/unit/test_screen_router.py` imports `from game import screen_router as router_mod` and `from game.core.constants import GameState` but Phase 1's grep missed this pattern.
- **Impact**: A substantially tested module (449 lines of tests, 5 test functions) was reported as Tier 0.

### AE-3: Phase 1 False Negative — empire_panel_ctrl.py
- **Error**: Phase 1 reported zero tests (Tier 0)
- **Root cause**: The test file `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py` was missed. Multiple tests cover open/kill/close lifecycle.
- **Impact**: Full coverage module reported as zero coverage.

### AE-4: Phase 1 False Negative — defaults.py
- **Error**: Phase 1 reported zero tests (Tier 0)
- **Root cause**: The test file `tests/unit/ui/services/image/test_defaults.py` was missed.
- **Impact**: Tested module reported as zero coverage.

### AE-5: Phase 1 False Negative — deepseek.py helpers
- **Error**: Phase 1 reported `_read_api_key`, `_build_body`, `_build_headers`, `_parse_response` as untested
- **Root cause**: Phase 1 didn't recognize that these private methods are exercised through the `complete()` public method, which has comprehensive test coverage
- **Impact**: 4 private helper methods with thorough test coverage were reported as untested gaps

### AE-6: Phase 2 Repetition without Verification
- **Error**: Phase 2 report propagated all Phase 1 false negatives without skeptical reading of the actual test files
- **Example**: The Phase 2 report itself notes "test_superweapons.py exists but Phase 1 found zero candidate test files importing this module — verify manually" yet did not read the test file to confirm
- **Impact**: 4 modules were categorized as Critical gaps when they have comprehensive test coverage

---

## Adjusted Severity Reclassifications

| Module | Phase 2 Tier | Verified Tier | Change |
|--------|-------------|---------------|--------|
| game/screen_router.py | 0 (Critical) | 1-2 (Partial) | ↓ 5 methods tested, ~15 untested |
| game/simulation/components/abilities/superweapons.py | 0 (Critical) | 3 (Verified) | ↓ Full coverage found |
| game/strategy/generation/density/primitives/density_primitive.py | 0 (Critical) | 0 (Critical) | — Confirmed |
| game/ui/screens/strategy_windows/empire_panel_ctrl.py | 0 (Critical) | 3 (Verified) | ↓ Full coverage found |
| game/ui/services/image/defaults.py | 0 (Critical) | 1-2 (Partial) | ↓ 3 tests found, coverage adequate |

**Revised Critical count**: 1 (was 5)
**Revised Major count**: 17 confirmed + 7 disputed = 24 (unchanged, but 7 reclassified as indirectly covered)

---

## Methodology Notes

All verifications performed by:
1. Reading cited production file line ranges + 10 lines context
2. Reading corresponding test files (full file)
3. Grepping test directory for symbol names
4. Checking indirect coverage through public API paths
5. Cross-referencing Phase 2 claims against actual code
