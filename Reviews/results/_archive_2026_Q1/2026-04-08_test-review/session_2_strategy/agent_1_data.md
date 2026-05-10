# Test Review Report: Agent 1 -- Strategy Data

## Scope
- **Source files reviewed:** 41 files in `game/strategy/data/` (10,356 LOC total)
- **Test files reviewed:** 67 files across `tests/unit/strategy/data/` (42 files), `tests/unit/strategy/ship_instance/` (9 files), `tests/unit/strategy/ship_stats/` (6 files), `tests/unit/strategy/empire/` (1 file), `tests/unit/strategy/stars/` (2 files), `tests/unit/strategy/planet_atmosphere/` (2 files), `tests/unit/strategy/galaxy/` (3 files) -- 19,404 LOC total
- **Coverage data referenced:** Yes, from coverage.json. Range: 0.0% (build_context.py) to 100.0% (6 files). Median ~85%.

## Summary
- Test files reviewed: 67
- Source files reviewed: 41
- Tests flagged for removal: 3 (estimated LOC: 126)
- Tests flagged as happy-path-only: 11
- Source files with inadequate coverage: 10

---

## A. Tests Recommended for Removal

### A1. test_ship_pod_storage.py -- OVER_MOCKED / TESTS_NOTHING_REAL
- **File:** `tests/unit/strategy/data/test_ship_pod_storage.py`
- **Test(s):** All 7 tests in `TestShipPodStorage`
- **Reason:** OVER_MOCKED
- **Confidence:** HIGH
- **Evidence:** The test file creates `MagicMock(spec=ShipInstance)` at line 12, then manually re-implements `get_pod_storage_capacity`, `get_pod_storage_used`, and `can_carry_pod` as lambdas (lines 16-20). These lambda re-implementations are what get tested, NOT the actual `ShipInstance` methods. Zero real game code executes. This is testing a hand-written mock, not production behavior. If the real methods diverge from these lambdas, the tests would still pass.
- **Estimated LOC saved:** 74

### A2. test_production_rates.py -- TRIVIAL_CONSTANT
- **File:** `tests/unit/strategy/data/test_production_rates.py`
- **Test(s):** `TestProductionRatesJson` (all 7 tests)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Lines 39-47 assert that `planetary_yard` rates are exactly 2000 and `space_shipyard` rates are exactly 30000. These are pure data file assertions -- they verify a JSON file contains specific magic numbers. These exact same values are also asserted in `test_build_queue_source.py` lines 25-36 (EXPECTED_PLANETARY_RATES, EXPECTED_SHIPYARD_RATES) which tests them through actual code paths. The structural tests (keys present, values positive) have marginal value since load failures would crash downstream tests immediately.
- **Estimated LOC saved:** 54 (but keep if data file validation is desired as a standalone concern)

### A3. test_data_layer_boundaries.py -- Architectural guard, but recommend KEEP
- **File:** `tests/unit/strategy/data/test_data_layer_boundaries.py`
- **Test(s):** `TestDataLayerDoesNotImportEngine`, `TestNoSingletonAccessInData`
- **Reason:** N/A -- recommending KEEP despite being non-behavioral
- **Confidence:** N/A
- **Evidence:** These are architectural boundary tests (lines 13-42, 46-67) that walk the AST of all data/ files to detect forbidden imports. They enforce documented architecture constraints. Although they don't test game behavior, they prevent layer violations. **Keep.**

---

## B. Tests That Are Happy-Path-Only

### B1. test_homeworld_presets.py -- Missing error paths
- **File:** `tests/unit/strategy/data/test_homeworld_presets.py`
- **Test(s):** `TestLoadHomeworldPresets`, `TestApplyPresetToConfig`, `TestGetAvailableHomeworldNames`
- **What's tested:** Loading presets from JSON, applying them to RaceConfig, getting display names
- **What's missing:**
  - `apply_preset_to_config(None, config)` -- None preset guard (line 71 of source, 0% covered)
  - `get_preset_id_from_name()` -- entire function untested (lines 119-123, 0% covered)
  - `clear_cache()` -- untested (line 129, 0% covered)
  - Cache behavior: no test for the `_presets_cache is not None` early return (line 34)
  - Error handling: no test for `load_json` returning None or missing "presets" key (line 38-39)
- **Source method(s) affected:** `homeworld_presets.py:39,71-72,75-95,119-123,129`
- **Priority:** MEDIUM

### B2. test_build_context.py -- Missing error paths for can_build_type
- **File:** `tests/unit/strategy/data/test_build_context.py`
- **Test(s):** `TestPlanetCanBuildType`, `TestFleetContextType`
- **What's tested:** Protocol compliance and basic can_build_type behavior
- **What's missing:**
  - Edge: empty string input to `can_build_type("")`
  - The BuildContext Protocol itself (build_context.py) has 0% coverage because Protocol bodies are never executed. This is expected/correct -- the tests verify protocol compliance via isinstance checks and real method calls on Planet/Fleet.
- **Source method(s) affected:** `build_context.py` (0% is acceptable for Protocol-only file)
- **Priority:** LOW

### B3. test_classification_config.py -- Missing _use_defaults and cached config paths
- **File:** `tests/unit/strategy/data/test_classification_config.py`
- **Test(s):** `TestClassificationConfigDefaults`, `TestClassificationConfigFromJson`
- **What's tested:** Default values, JSON override, partial JSON fallback, cached config
- **What's missing:**
  - `_use_defaults()` method never directly covered (lines 127-154). Tests verify defaults via `ClassificationConfig(None)` which calls `_use_defaults`, but the coverage report shows lines 128-154 as uncovered, suggesting the `_load_from_json` path is what's actually hit from the cached `get_classification_config()` call in the test suite
  - Chthonian stripping config values (lines 112-123) not asserted in tests
  - `get_classification_config()` error path: only FileNotFoundError tested, not other exception types (OSError, TypeError, etc.)
- **Source method(s) affected:** `classification_config.py:128-154,170-173`
- **Priority:** LOW (config loading is low-risk)

### B4. test_orbital_generation_config.py -- Missing _use_defaults path
- **File:** `tests/unit/strategy/data/test_orbital_generation_config.py`
- **Test(s):** `TestOrbitalGenerationConfigDefaults`, `TestOrbitalGenerationConfigFromJson`
- **What's tested:** Defaults, JSON loading, cached config
- **What's missing:**
  - `_use_defaults()` is called by `OrbitalGenerationConfig(None)` but coverage shows lines 138-177 as uncovered. This means the `_load_from_json()` path runs when loading from the actual astrophysics.json, and `_use_defaults()` never gets covered by the cached function path.
  - `get_orbital_generation_config()` error path with warning log (lines 193-195)
- **Source method(s) affected:** `orbital_generation_config.py:138-177,193-195`
- **Priority:** LOW

### B5. test_star_generation_config.py -- Missing _use_defaults path
- **File:** `tests/unit/strategy/data/test_star_generation_config.py`
- **Test(s):** Same pattern as B3/B4
- **What's tested:** Defaults, JSON loading, cached config
- **What's missing:**
  - `_use_defaults()` method lines 155-176 uncovered (same pattern as classification and orbital config)
  - Stefan-Boltzmann types from JSON loading untested (line 151 -- always uses defaults for complex nested structure)
- **Source method(s) affected:** `star_generation_config.py:155-176,192-194`
- **Priority:** LOW

### B6. test_order_serializer.py -- Missing colonize_params and dict format
- **File:** `tests/unit/strategy/data/test_order_serializer.py`
- **Test(s):** `TestDeserializeTarget*`, `TestResolveOrderReferences`
- **What's tested:** 7 of 8 target formats, fleet/planet ref resolution, corrupt entry handling
- **What's missing:**
  - Format 3b: `colonize_params` deserialization (lines 128-133 of source) -- completely untested
  - `_colonize_planet_ref` resolution in `resolve_order_references` (lines 214-227) -- untested
  - `dict` format wrapping in `Order.to_dict()` (order_types.py:130-132) -- untested
  - Colonize with population/cargo amounts (order_types.py:121-129) -- untested
- **Source method(s) affected:** `order_serializer.py:128-133,214-227`, `order_types.py:121-134`
- **Priority:** HIGH (colonize is a core gameplay feature, untested serialization path)

### B7. test_race_point_budget.py -- Missing get_tolerance_breakdown atmosphere detail
- **File:** `tests/unit/strategy/data/test_race_point_budget.py`
- **Test(s):** `TestRacePointBudgetCostBreakdown.test_get_tolerance_breakdown`
- **What's tested:** Gravity, temperature, water breakdown; atmosphere as aggregate
- **What's missing:**
  - `get_tolerance_breakdown()` returns an aggregate "atmosphere" cost but individual gas breakdowns are not verified
  - No test for `get_tolerance_breakdown` with mixed positive/negative atmosphere values
  - Lines 209-234 of source show the breakdown method duplicates logic from `calculate_tolerance_cost` -- no test verifies they stay in sync
- **Source method(s) affected:** `race_point_budget.py:209-234`
- **Priority:** LOW

### B8. test_galaxy_entity_registry.py -- Missing update_next_planet_id path
- **File:** `tests/unit/strategy/data/test_galaxy_entity_registry.py`
- **Test(s):** `TestPlanetRestore`
- **What's tested:** restore_planet preserves ID, doesn't advance next_id
- **What's missing:**
  - Source line 109: `restore_planet` doesn't call `_update_next_planet_id`. The Galaxy-level method that tracks max_id after restore is not in this file, but the entity_registry's `restore_planet` is thin. No real gap here.
  - Missing: concurrent registration while restore is happening (edge case)
  - Lines 159, 177-188 (unregister_zone cleanup when zone has multiple hexes with some already cleaned)
- **Source method(s) affected:** `galaxy_entity_registry.py:159,177-188`
- **Priority:** LOW

### B9. test_fleet_consumable_aggregator.py -- Missing cargo and pod methods
- **File:** `tests/unit/strategy/data/test_fleet_consumable_aggregator.py`
- **Test(s):** Various classes
- **What's tested:** Movement resources, warp resources, atomic consumption, fuel endurance
- **What's missing:**
  - `load_cargo_to_fleet()` -- untested (lines 291-315 of source, 0% covered)
  - `unload_cargo_from_fleet()` -- untested (lines 317-341 of source, 0% covered)
  - `get_capability_summary()` -- untested (lines 232-247 of source, 0% covered)
  - `get_fleet_pod_capacity()` and `get_fleet_pod_mass_used()` -- untested (lines 251-257)
  - `warp_jumps_remaining()` with multi-resource cost -- only single-resource tested
- **Source method(s) affected:** `fleet_consumable_aggregator.py:199-201,217-230,239,303,310,329`
- **Priority:** MEDIUM (cargo operations are gameplay-critical)

### B10. test_component_activation_state.py -- Missing start_deactivating from DEACTIVATING
- **File:** `tests/unit/strategy/data/test_component_activation_state.py`
- **Test(s):** `TestStartDeactivating`
- **What's tested:** Deactivating from ACTIVE, error from INACTIVE
- **What's missing:**
  - No test for `start_deactivating` from ACTIVATING phase (should raise ValueError)
  - No test for `start_deactivating` from DEACTIVATING phase (should raise ValueError)
  - Lines 67, 69 of source: tick returning False from non-transitional phases -- partially covered
- **Source method(s) affected:** `component_activation_state.py:77-78,82-85,94`
- **Priority:** LOW (edge case, covered by cancel tests)

### B11. test_spatial_index.py -- Missing get_k_nearest max_radius and expansion
- **File:** `tests/unit/strategy/data/test_spatial_index.py`
- **Test(s):** `TestSpatialIndexNeighborQuery.test_get_k_nearest`
- **What's tested:** Basic k-nearest, exclude_self
- **What's missing:**
  - `max_radius` parameter never tested (line 117 of source)
  - Search radius expansion loop (lines 136-162) -- the iterative doubling behavior untested
  - `get_k_nearest` when k > total points (should return all available)
  - Lines 98-99, 101-108 of source: the candidate count stagnation termination condition untested
- **Source method(s) affected:** `spatial_index.py:98-99,101-108,150-162`
- **Priority:** MEDIUM (spatial queries affect galaxy generation correctness)

---

## C. Source Code with Inadequate Coverage

### C1. build_context.py -- 0.0% (14 stmts)
- **Source file:** `game/strategy/data/build_context.py` (62 LOC)
- **Coverage:** 0.0% -- but this is a Protocol class (abstract interface)
- **Untested areas:** All property/method bodies are `...` (ellipsis). Protocol bodies are never executed at runtime.
- **Risk:** None. The Protocol is tested via isinstance checks and real implementations in test_build_context.py.
- **Priority:** LOW (non-issue; Protocol bodies are inherently uncoverable)

### C2. homeworld_presets.py -- 53.5% (43 stmts, 20 missing)
- **Source file:** `game/strategy/data/homeworld_presets.py` (130 LOC)
- **Coverage:** 53.5% qualitatively -- `apply_preset_to_config` body (lines 71-95) and helper functions (119-129) are uncovered
- **Untested areas:**
  - `apply_preset_to_config()` -- entire body (lines 71-95): setting gravity, temperature, water, radiation, atmosphere on RaceConfig
  - `get_preset_id_from_name()` -- entire function (lines 119-123)
  - `clear_cache()` (line 129)
  - None preset guard (line 39)
- **Risk:** `apply_preset_to_config` is called during race creation UI. If it silently fails to set fields, race configs would have wrong environmental preferences. Medium risk.
- **Priority:** HIGH

### C3. orbital_generation_config.py -- 60.2% (103 stmts, 41 missing)
- **Source file:** `game/strategy/data/orbital_generation_config.py` (196 LOC)
- **Coverage:** 60.2% -- `_use_defaults()` method entirely uncovered (lines 137-177)
- **Untested areas:** The `_use_defaults()` method (40 lines) sets 30 attributes. It runs when data is None. Tests create `OrbitalGenerationConfig(None)` which should call it, but coverage says these lines are missed. This may be a coverage collection artifact where the defaults test calls `OrbitalGenerationConfig(None)` at import time before coverage starts.
- **Risk:** Low -- `_use_defaults` is a mirror of the DEFAULT_* class attrs already tested.
- **Priority:** LOW

### C4. build_queue_source.py -- 64.7% (167 stmts, 59 missing)
- **Source file:** `game/strategy/data/build_queue_source.py` (440 LOC)
- **Coverage:** 64.7% -- significant methods uncovered
- **Untested areas:**
  - `_get_planetary_yard_size_multiplier()` (lines 194-226) -- entire function
  - `get_build_rate_booster_mult()` (lines 83-113) -- tested only via collect path with galaxy=None/empire=None early return
  - `colony_has_planetary_yard()` string component path (line 150-155) -- when comp is a string ID
  - `_collect_planet_sources` with build boosters (line 317 -- build_booster calculation)
  - `get_production_rate_for_queue` with yard_size_mult scaling (line 294)
- **Risk:** Build rate calculations affect turn estimation and production speeds. Incorrect multipliers would cause ships to take wrong number of turns to build.
- **Priority:** HIGH

### C5. classification_config.py -- 65.8% (76 stmts, 26 missing)
- **Source file:** `game/strategy/data/classification_config.py` (174 LOC)
- **Coverage:** 65.8% -- `_use_defaults()` and `get_classification_config()` error path uncovered
- **Untested areas:**
  - `_use_defaults()` lines 128-154 (same pattern as C3)
  - `get_classification_config()` fallback path with warning log (lines 170-173)
  - Chthonian stripping defaults (lines 151-154)
- **Risk:** Low -- defaults are tested indirectly via `ClassificationConfig(None)` in test suite.
- **Priority:** LOW

### C6. star_generation_config.py -- 68.3% (63 stmts, 20 missing)
- **Source file:** `game/strategy/data/star_generation_config.py` (195 LOC)
- **Coverage:** 68.3% -- `_use_defaults()` uncovered (lines 155-176)
- **Untested areas:** Same pattern as C3/C5. `_use_defaults()` sets 15+ attributes from class-level defaults.
- **Risk:** Low.
- **Priority:** LOW

### C7. galaxy_spatial_index.py -- 72.9% (59 stmts, 16 missing)
- **Source file:** `game/strategy/data/galaxy_spatial_index.py` (193 LOC)
- **Coverage:** 72.9%
- **Untested areas:**
  - `get_system_of_object()` lines 47-49: auto-routing for Planet isinstance check (partially tested with real Planet in test_galaxy_spatial_index.py line 197-209)
  - `get_all_fleets_in_system()` lines 163-179: planet zone hex calculation (radius_hexes > 0 path)
  - `get_system_at_location()` zone-to-system resolution when zone is found (line 136)
- **Risk:** Spatial queries drive fleet movement, battle detection, and system identification. Missed hexes could cause fleets to "disappear" from system views.
- **Priority:** MEDIUM

### C8. ship_instance.py -- 83.0% (223 stmts, 38 missing)
- **Source file:** `game/strategy/data/ship_instance.py` (616 LOC)
- **Coverage:** 83.0%
- **Untested areas:**
  - `repair()` method (lines 536-557): repair amount calculation, clearing damage at full HP
  - `resupply()` method (line 565)
  - `clone()`, `to_json()`, `from_json()` methods (lines 596-610)
  - `__repr__()` (lines 612-615)
  - `get_hp_percentage()` edge case when max_hp <= 0 (line 287)
  - `is_damaged()` when only `component_damage` is set (line 217)
  - Error path in `get_calculated_stats()` when registries is None (lines 257-262)
- **Risk:** `repair()` is called by repair bay processing. If repair clears damage state incorrectly, ships could become unrepairably bugged. Medium risk.
- **Priority:** MEDIUM

### C9. planet.py -- 85.2% (189 stmts, 28 missing)
- **Source file:** `game/strategy/data/planet.py` (540+ LOC)
- **Coverage:** 85.2%
- **Untested areas:**
  - Lines 150-153, 158: some property accessors
  - Lines 282-296: `get_active_abilities()` or similar method
  - Lines 315-340: Planet serialization/deserialization edge cases
  - Lines 534-537: some helper method
- **Risk:** Planet is a core data class. Missing coverage on serialization could cause save/load bugs.
- **Priority:** MEDIUM

### C10. planet_gen.py -- 82.5% (257 stmts, 45 missing)
- **Source file:** `game/strategy/data/planet_gen.py` (580+ LOC)
- **Coverage:** 82.5%
- **Untested areas:**
  - Lines 67-77: Early initialization/setup code
  - Lines 113-128: Planet generation configuration loading
  - Lines 154-172: Some generation helper methods
  - Lines 220-224, 238: Edge cases in physical parameter generation
  - Lines 266-272: Water/atmosphere generation
  - Lines 530-533, 581: Edge cases in classification
- **Risk:** Planet generation is a complex stochastic process. Missing coverage on edge cases could produce invalid planets that crash downstream code.
- **Priority:** MEDIUM

---

## D. Cross-Domain Observations

### D1. Config classes share identical `_use_defaults` coverage gap
Three configuration classes follow the same pattern and all have the same coverage gap:
- `classification_config.py` (65.8%)
- `orbital_generation_config.py` (60.2%)
- `star_generation_config.py` (68.3%)

Each has `_load_from_json()` and `_use_defaults()`. The `_use_defaults()` path is never covered despite tests calling `Config(None)`. This likely means pytest-cov collection starts AFTER module-level imports, and the `get_*_config()` cached functions are called during import of other modules, covering `_load_from_json()` but leaving `_use_defaults()` unreachable in subsequent test runs. This is a coverage measurement artifact, not a real testing gap. All three should be treated as LOW priority.

### D2. Order serialization has untested colonize_params format
The `colonize_params` target format (order_serializer.py lines 128-133, order_types.py lines 121-129) is completely untested. This is a **cross-domain concern** because:
- The colonize flow involves UI (session 3) -> strategy engine -> data layer
- If colonize serialization breaks, colony establishment would fail on save/load
- This should be flagged for the strategy engine session as well

### D3. FleetConsumableAggregator cargo methods untested
`load_cargo_to_fleet()` and `unload_cargo_from_fleet()` in fleet_consumable_aggregator.py (lines 291-341) are 0% covered. These are called by the strategy transfer order system. If the cargo distribution across ships has bugs, resource transfers at planets would silently fail or produce incorrect results.

### D4. test_ship_pod_storage.py tests mock lambdas, not real code
This file (74 LOC) tests hand-written lambda re-implementations of ShipInstance methods. If the real ShipInstance.get_pod_storage_capacity / can_carry_pod methods change, these tests would still pass. This is a cross-domain risk for ship_instance testing (session 2 ship_instance scope).

### D5. BuildQueueSource size_multiplier and build_rate_booster paths untested
The `_get_planetary_yard_size_multiplier()` function (build_queue_source.py lines 194-226) and the full `get_build_rate_booster_mult()` function (lines 83-113) are not exercised by any test. These functions scan facility components for abilities and aggregate multipliers. The build rate booster involves cross-system strategic ability scanning, which may also affect the strategy services session scope.
