# Validation Report: Core + Sim + AI

## Claims Reviewed: 25
## Confirmed: 16 | Downgraded: 7 | Rejected: 2

---

## Detailed Verdicts

### [Claim 1] test_import_path (test_combat_types.py:33-35)
- **Original claim:** SCAFFOLD_ONLY, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** The test imports `DamageContext` via a second path and asserts identity with the already-imported symbol. Line 6 already imports it. This test proves nothing -- if the import failed, the module wouldn't load at all. Pure scaffold.
- **Validated confidence:** HIGH

### [Claim 2] test_slots (test_combat_types.py:29-31)
- **Original claim:** TRIVIAL_CONSTANT, MEDIUM
- **Verdict:** CONFIRMED
- **Evidence:** `hasattr(ctx, "__slots__")` -- this checks the dataclass has `__slots__` but doesn't verify its contents or that it actually prevents `__dict__` creation. The frozen+immutability test (line 24-27) is far more meaningful. This is trivial.
- **Validated confidence:** MEDIUM

### [Claim 3] test_config.py 6 tests (lines 13-80)
- **Original claim:** TRIVIAL_CONSTANT, HIGH
- **Verdict:** DOWNGRADED
- **Evidence:** I read both `test_config.py` and `test_config_edge_cases.py`. The edge cases file tests *invariants* (e.g., `FLEE_DISTANCE > DEFAULT_ORBIT_DISTANCE`, `TICK_RATE < 1.0`, `ERRATIC_TURN_INTERVAL_MIN < MAX`). The original `test_config.py` tests exact values like `DEFAULT_WIDTH == 3840`, `TICK_RATE == 0.01`, `TARGET_QUERY_RADIUS == 200000`. These are brittle pin-down tests that will break on any intentional change, but they DO serve as a change-detection alarm for config values that many systems depend on. The edge cases file does NOT cover the same ground -- it only tests relationships, not specific values. Removing ALL 6 tests would leave no alert for accidental config value changes. The `test_default_resolution_tuple` and `test_test_resolution_tuple` tests (lines 27-40) are more valuable since they test the *methods* `default_resolution()` and `test_resolution()`, not just raw attributes.
- **Validated confidence:** MEDIUM -- Remove the 4 pure attribute equality tests (test_default_resolution_values, test_test_resolution_values, test_spacing_values, test_tick_rate) but KEEP the 2 tuple method tests (test_default_resolution_tuple, test_test_resolution_tuple). Alternatively, remove all 6 if the edge cases file is expanded to pin exact values.

### [Claim 4] test_earth_mass_importable + test_earth_mass_is_float (test_constants.py:48-61)
- **Original claim:** SCAFFOLD_ONLY, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** `test_earth_mass_value` (line 53-56) already imports the constant, asserts it's in a numeric range (implicitly proving it's importable and a float), and checks the actual value. The other two tests are strictly subsumed.
- **Validated confidence:** HIGH

### [Claim 5] 3 PlanetaryResources tests (test_constants.py:17-42)
- **Original claim:** DUPLICATE_OF test_planetary_resources_has_expected_values, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** `test_planetary_resources_has_expected_values` (line 24-29) asserts `ids == ["metals", "organics", "vapors", "radioactives", "exotics"]` which implicitly proves: (a) it's a list (test at line 20), (b) has 5 elements (test at line 35), (c) elements are strings (test at line 40), and (d) is not None (test at line 17). All 4 other tests are strictly subsumed by the exact equality check.
- **Validated confidence:** HIGH -- but note: remove only 4 tests (lines 12-22, 32-42), keep test_planetary_resources_has_expected_values.

### [Claim 6] TestProtocolExistence (test_protocols.py:12-75)
- **Original claim:** SCAFFOLD_ONLY, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** TestProtocolsWithRealClasses (line 78+) imports and uses every protocol with real game objects. TestTypeGuardFunctions (line 165+) imports and calls every typeguard. TestPROJ193ProtocolSatisfaction (line 523+) covers the PROJ-193 protocols with real classes. All imports in TestProtocolExistence are subsumed. The `assert callable(is_fleet)` checks are also subsumed by the tests that actually call them.
- **Validated confidence:** HIGH

### [Claim 7] TestPROJ193ProtocolImports (test_protocols.py:493-520)
- **Original claim:** SCAFFOLD_ONLY, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** TestPROJ193ProtocolSatisfaction (line 523-582) imports and uses IEmpire, IFacility, IShipInstance, ICombatShip with real game classes AND calls is_empire, is_facility, is_ship_instance, is_combat_ship. Every import in TestPROJ193ProtocolImports is strictly subsumed.
- **Validated confidence:** HIGH

### [Claim 8] TestErrorCodeCategories (test_error_codes.py:84-120)
- **Original claim:** DUPLICATE_OF TestErrorCodeNamingConvention, MEDIUM
- **Verdict:** DOWNGRADED
- **Evidence:** These test DIFFERENT things. TestErrorCodeNamingConvention (line 30-82) tests that specific *named* codes follow the right prefix convention (e.g., codes named VALIDATION_* start with 'V'). TestErrorCodeCategories (line 84-120) tests that at least one code *exists* for each category prefix (at least one 'V' code, one 'S' code, etc.). These are complementary: the naming convention tests could all pass even if an entire category was accidentally deleted, because they only check existing members. The categories tests catch "entire category accidentally removed." However, the categories tests are extremely weak -- they only check `len > 0`. TestErrorCodeMinimumSet (line 148-178) already pins specific codes per category (e.g., VALIDATION_FAILED=V001, STATE_FROZEN=S001), which implicitly proves each category has at least one member.
- **Validated confidence:** LOW -- TestErrorCodeMinimumSet already proves categories exist. Remove TestErrorCodeCategories, but note this is because of MinimumSet, NOT NamingConvention.

### [Claim 9] First TestHullAutoEquip shadowed by second (test_ship.py:276-291 vs 403+)
- **Original claim:** HIGH, Python silently replaces the class
- **Verdict:** CONFIRMED
- **Evidence:** Python class definition at line 276 `class TestHullAutoEquip:` is silently replaced by the second definition at line 403 `class TestHullAutoEquip:`. Only the second class's tests run. The first class's `test_hull_auto_equip` method (line 279) never executes. This is a genuine bug in the test suite. The fix is to either rename the first class or merge its test into the second.
- **Validated confidence:** HIGH -- but this is a BUG to fix, not just dead code to remove. The first class tests `registry_with_hull` fixture behavior (hull_escort auto-equip + base_mass shadowing). The second class tests the PROJ-225 extracted `_equip_default_hull`. Recommend RENAMING the first class (e.g., `TestHullAutoEquipLegacy`) so its test actually runs, rather than deleting it.

### [Claim 10] ComponentStatus enum tests (test_component_constants.py:17-49)
- **Original claim:** TRIVIAL_CONSTANT, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** Lines 17-45 are 6 individual `assert hasattr(ComponentStatus, 'ACTIVE')` / `assert ComponentStatus.ACTIVE is not None` tests. The test at line 46-49 `test_component_status_all_unique` is the only non-trivial one -- it checks all values are distinct. The hasattr tests are pure scaffold; any code that references `ComponentStatus.ACTIVE` would immediately fail with an AttributeError if it didn't exist. The same file has substantial Modifier/ApplicationModifier tests (lines 52+) that should be kept.
- **Validated confidence:** HIGH -- remove only lines 16-45 (the 6 hasattr tests). Keep test_component_status_all_unique and everything below.

### [Claim 11] 3 deprecated static method tests (test_modifier_manager.py:141-177)
- **Original claim:** DEAD_CODE, MEDIUM
- **Verdict:** DOWNGRADED
- **Evidence:** The methods `add_modifier_static`, `remove_modifier_static`, `get_modifier_static` are marked DEPRECATED in source but still exist in `game/simulation/components/modifier_manager.py`. Grep shows NO production callers (only the test file and coverage.json reference them). These tests exercise dead code that nobody calls. However, removing the tests without also removing the dead production code would leave untested deprecated methods in the codebase. The right action is to remove BOTH the deprecated static methods AND their tests simultaneously.
- **Validated confidence:** MEDIUM -- but recommend removing the deprecated methods from production code at the same time, otherwise you have dead untested code.

### [Claim 12] Source-reading tests (test_ship_component_manager_di.py:15-29)
- **Original claim:** TESTS_NOTHING_REAL, MEDIUM
- **Verdict:** DOWNGRADED
- **Evidence:** These tests read Python source files and assert `'get_default_registry_provider' not in content`. This is a legitimate architectural constraint enforcement (DI compliance). If someone adds a global registry import to `ship_component_manager.py`, this test catches it. This is an *architecture guard test*, similar to import-order enforcement. It tests a real invariant that matters for the DI migration. However, it's fragile (string matching on source) and could be replaced by a proper import analysis tool. I'd keep these unless a better mechanism is in place.
- **Validated confidence:** KEEP -- these guard a real architectural constraint (PROJ-252 DI compliance). Not a duplicate, not trivial, not dead code. The claim is wrong.

### [Claim 13] TestDefaultMaxMass::test_constant_exists (test_ship.py:491-494)
- **Original claim:** TRIVIAL_CONSTANT, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** `test_constant_exists` asserts `DEFAULT_MAX_MASS == 1000`. The next test `test_ship_uses_constant_for_unknown_class` (line 496-503) imports the same constant and tests that a ship actually uses it. The behavioral test is far more valuable and implicitly proves the constant exists with the right value.
- **Validated confidence:** HIGH

### [Claim 14] test_component_getters.py + test_component_operations.py vs test_ship_component_manager.py
- **Original claim:** DUPLICATE_OF test_ship_component_manager.py, MEDIUM
- **Verdict:** REJECTED
- **Evidence:** I carefully compared all three files. The ship_helpers tests use a CUSTOM conftest with manually constructed components (no real data loading). test_ship_component_manager.py uses `fresh_registries` with `create_component()` from the real factory. More importantly:
  - `test_component_getters.py` has 30 tests covering `get_all_components`, `iter_components`, `get_components_by_ability` (with operational_only filtering, default behavior), and `get_components_by_layer` with extensive edge cases (nonexistent layer, defensive copy, layer-assignment verification).
  - `test_component_operations.py` has 19 tests covering `has_components`, `find_component_with_index` (predicate-based search with layer tracking, index validity for removal), and `clear_non_hull_components`.
  - `test_ship_component_manager.py` covers `add_component`, `remove_component`, `add_components_bulk`, `get_all_components` cache, `iter_components`, `get_components_by_ability`, and `get_weapon_components_cached`.
  
  There is SOME overlap in `get_all_components` and `iter_components`, but the helper tests cover `find_component_with_index`, `has_components`, `clear_non_hull_components`, and `get_components_by_layer` which are NOT tested in test_ship_component_manager.py. Removing the helper tests would leave significant API surface untested.
- **Validated confidence:** KEEP -- partial overlap exists but unique coverage is substantial. At most, a handful of individual test methods could be deduplicated, but blanket removal is wrong.

### [Claim 15] TestShipStatQuerierInitialization (test_ship_stat_querier.py:263-283)
- **Original claim:** TRIVIAL_CONSTANT, MEDIUM
- **Verdict:** CONFIRMED
- **Evidence:** The two tests check that `querier._ship` stores a reference to the mock ship passed to the constructor, and that two queriers have independent ship references. This is testing basic Python attribute assignment. The rest of the file (TestGetAbilityTotalEdgeCases at line 286+, etc.) tests actual behavior. These init tests are trivial.
- **Validated confidence:** MEDIUM

### [Claim 16] test_combat_ops.py vs test_damage_calculator.py + test_weapon_firing_system.py
- **Original claim:** DUPLICATE_OF subsystem tests, HIGH
- **Verdict:** DOWNGRADED
- **Evidence:** ShipCombatEngine.fire_weapons() delegates to `self._weapon_firing_system.fire_weapons(self._ship, context)` and ShipCombatEngine.take_damage() delegates to `self._damage_calculator.apply_damage(self._ship, damage_amount, context, self._event_bus)`. The test_combat_ops.py tests exercise these through the ShipCombatEngine facade, while test_damage_calculator.py and test_weapon_firing_system.py test the subsystems directly. The facade tests verify:
  1. The delegation wiring is correct (facade -> subsystem)
  2. The facade adds its own guards (dead/derelict checks in fire_weapons)
  3. The emissive armor test creates the engine and calls `engine.take_damage(10)` which goes through the facade
  
  However, the dead/derelict guard tests ARE duplicated: `test_combat_ops.py::test_fire_weapons_returns_empty_when_dead` is identical in logic to `test_weapon_firing_system.py::test_fire_weapons_returns_empty_when_dead`. The damage tests are also near-duplicates. The ONLY unique value in test_combat_ops.py is the TestCombatEngineIntegration class (lines 238-257) which tests with real Ship objects.
- **Validated confidence:** MEDIUM -- The integration tests (TestCombatEngineIntegration) should be kept. The unit-level facade tests (TestFireWeapons and TestDamageApplication) are genuine duplicates and can be removed. This is a partial removal, not wholesale file deletion.

### [Claim 17] test_ship_stats_phase_ordering.py 2 tests (lines 14-22)
- **Original claim:** SCAFFOLD_ONLY, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** `test_ship_stats_calculator_exists` asserts `ShipStatsCalculator is not None` after importing it. `test_calculator_has_calculate_method` asserts `hasattr(ShipStatsCalculator, 'calculate')`. These are pure import/existence scaffold. The actual ShipStatsCalculator has extensive tests in test_ship_stats_calculator_phases.py. The entire file is only these 2 tests.
- **Validated confidence:** HIGH -- entire file can be removed.

### [Claim 18] test_ship_stats_calculator_phases.py 5 hasattr tests (lines 381-404)
- **Original claim:** SCAFFOLD_ONLY, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** Five tests checking `hasattr(calculator, '_priority_sort_key')`, `hasattr(calculator, '_check_mass_limits')`, etc. These check that private helper methods exist after a refactor. The same file has TestShipStatsCalculatorPhases (line 19+) that actually calls `calculator.calculate(ship)` which exercises all these methods. Pure existence checks for private methods are scaffold.
- **Validated confidence:** HIGH

### [Claim 19] TestModeCharacteristics (test_battle_mode_handlers.py:260-293)
- **Original claim:** DUPLICATE_OF individual handler tests, MEDIUM
- **Verdict:** CONFIRMED
- **Evidence:** TestModeCharacteristics has 4 tests that each check all 4 properties of a handler. E.g., `test_manual_mode_characteristics` checks `is_headless_default() is False`, `can_retreat() is False`, `can_reinforce() is False`, `should_clone_ships() is False`. These exact same assertions appear individually in TestManualBattleModeHandler: `test_can_retreat_returns_false`, `test_can_reinforce_returns_false`, `test_should_clone_ships_returns_false`, `test_is_headless_default_returns_false`. Every assertion in TestModeCharacteristics is duplicated in the per-handler test classes. The per-handler tests also include `test_is_battle_mode_handler` and `test_configure_does_nothing` which are not in the summary class.
- **Validated confidence:** MEDIUM

### [Claim 20] 6 interface-existence tests (test_battle_mode_handlers.py:38-61)
- **Original claim:** SCAFFOLD_ONLY, MEDIUM
- **Verdict:** CONFIRMED
- **Evidence:** Tests check `hasattr(BattleModeHandler, 'configure')`, `hasattr(BattleModeHandler, 'can_retreat')`, etc. The individual handler tests (TestManualBattleModeHandler, etc.) actually CALL these methods, proving they exist. The `test_is_abstract_class` and `test_cannot_instantiate_directly` tests (lines 29-36) are worth keeping as they verify the ABC contract. The 6 hasattr tests (lines 38-61) are scaffold.
- **Validated confidence:** MEDIUM

### [Claim 21] TestAIControllerEngageDistance (test_ai_controller_edge_cases.py:332-375)
- **Original claim:** DUPLICATE_OF test_ai_controller_unit.py:TestGetEngageDistanceMultiplier, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** I compared both test classes side by side:
  - edge_cases: `max_range` -> 1.0, `ram` -> 0.0, numeric 0.75 -> 0.75, integer 2 -> 2.0, unknown -> 1.0, missing key -> 1.0
  - unit: `max_range` -> 1.0, `ram` -> 0.0, numeric 0.8 -> 0.8, unknown -> 1.0, missing key -> 1.0
  
  The edge_cases file has one extra test (integer conversion: `2 -> 2.0`) not in the unit file. Otherwise identical logic. The integer test is marginal value since Python's float() handles integers trivially.
- **Validated confidence:** HIGH -- the one extra integer test is not worth keeping a duplicate class for.

### [Claim 22] TestAIControllerCapabilitiesCache (test_ai_controller_edge_cases.py:273-329)
- **Original claim:** DUPLICATE_OF test_ai_capabilities_cache.py, HIGH
- **Verdict:** CONFIRMED
- **Evidence:** test_ai_capabilities_cache.py has a dedicated TestBuildCapabilitiesCache class (lines 80-168) with 8 tests covering: returns dict, includes all ships, has_weapons true/false, has_pdc true/false, cache structure verification, and duplicate name handling. The edge_cases version (lines 273-329) has 4 tests: empty ships, ships without id, ships with weapons, ships with PDC. The "empty ships" and "ship without id" edge cases are NOT in test_ai_capabilities_cache.py. However, these are minor edge cases that could be moved to the dedicated file if needed.
- **Validated confidence:** MEDIUM -- 2 of 4 tests have unique coverage (empty list, missing id). Recommend moving those 2 tests to test_ai_capabilities_cache.py rather than deleting them. Downgrade the "just delete" recommendation.

### [Claim 23] TestAIControllerScoreAndSort (test_ai_controller_edge_cases.py:378-413)
- **Original claim:** DUPLICATE_OF test_ai.py:TestTargetingHelpers, HIGH
- **Verdict:** DOWNGRADED
- **Evidence:** TestTargetingHelpers in test_ai.py tests `_find_enemies_in_radius` and `_score_and_sort_enemies` with real pygame Ship-like objects in a SpatialGrid. The edge_cases TestAIControllerScoreAndSort tests (a) handling of evaluation failures (enemy with position=None) and (b) empty enemy list. These are genuine edge cases. The "empty list" test is likely covered somewhere else, but the "evaluation failure handling" test (lines 381-405) is unique -- it tests that a bad enemy doesn't crash the scoring and is skipped gracefully. This isn't just a duplicate.
- **Validated confidence:** LOW -- the evaluation failure test is unique. Keep at least that test. Move it to test_ai.py or test_ai_controller_unit.py if consolidating.

### [Claim 24] TestIControllableAbstractContract + TestMockImplementation (test_controllable_adapter.py:13-246)
- **Original claim:** TESTS_NOTHING_REAL, MEDIUM
- **Verdict:** DOWNGRADED
- **Evidence:** TestIControllableAbstractContract (lines 13-65) tests that IControllable is a proper ABC: cannot instantiate, has expected abstract methods, partial implementation raises TypeError. TestMockImplementation (lines 68-246) creates a complete mock implementation to prove the interface is satisfiable. These are interface contract tests. The `test_all_abstract_methods_present` test (lines 25-46) is genuinely valuable -- it documents the FULL set of required abstract methods and would catch if someone accidentally removed a required method from the interface. However, the full MockControllable implementation (lines 74-192) is excessive -- it's 120 lines of boilerplate that proves you can implement an ABC. The isinstance check test is trivial.
- **Validated confidence:** MEDIUM -- keep TestIControllableAbstractContract (it guards the interface contract). Remove TestMockImplementation (the mock is not used anywhere else, and isinstance of a manually-constructed mock is not meaningful).

### [Claim 25] TestFormationIntegrityWithAdapter (test_ai_controller_interface.py:387-469)
- **Original claim:** DUPLICATE_OF test_ai_controller_unit.py:TestCheckFormationIntegrity, MEDIUM
- **Verdict:** DOWNGRADED
- **Evidence:** The unit test TestCheckFormationIntegrity (test_ai_controller_unit.py:704+) uses mock_ship directly (IControllable mock). The interface test TestFormationIntegrityWithAdapter wraps mock_ship in `ShipControllableAdapter` first, then tests formation integrity. This tests a DIFFERENT code path: the adapter's `get_components_by_ability` delegates to the wrapped ship, and the formation member list contains RAW ships (not adapters). The test at line 395 explicitly documents "Fix 10.1" for a bug where formation_members contains raw Ships but the controller's ship is an adapter. The damaged/undamaged tests verify the adapter-to-raw-ship interaction works. This is NOT a pure duplicate -- it tests the adapter layer specifically.
- **Validated confidence:** KEEP -- this tests a real adapter-layer integration concern documented as a specific bug fix. Removing it could allow the adapter-related bug to regress.

---

## Summary Table

| # | Test | Original | Verdict | Final Confidence |
|---|------|----------|---------|-----------------|
| 1 | test_import_path | HIGH | CONFIRMED | HIGH |
| 2 | test_slots | MEDIUM | CONFIRMED | MEDIUM |
| 3 | test_config.py 6 tests | HIGH | DOWNGRADED | MEDIUM (partial) |
| 4 | test_earth_mass_importable+is_float | HIGH | CONFIRMED | HIGH |
| 5 | 3 PlanetaryResources tests | HIGH | CONFIRMED | HIGH |
| 6 | TestProtocolExistence | HIGH | CONFIRMED | HIGH |
| 7 | TestPROJ193ProtocolImports | HIGH | CONFIRMED | HIGH |
| 8 | TestErrorCodeCategories | MEDIUM | DOWNGRADED | LOW (subsumed by MinimumSet, not NamingConvention) |
| 9 | First TestHullAutoEquip (shadowed) | HIGH | CONFIRMED | HIGH (but rename, don't delete) |
| 10 | ComponentStatus 6 hasattr tests | HIGH | CONFIRMED | HIGH |
| 11 | 3 deprecated static method tests | MEDIUM | DOWNGRADED | MEDIUM (remove with production code) |
| 12 | Source-reading DI tests | MEDIUM | REJECTED | KEEP |
| 13 | test_constant_exists | HIGH | CONFIRMED | HIGH |
| 14 | test_component_getters + operations | MEDIUM | REJECTED | KEEP |
| 15 | TestShipStatQuerierInitialization | MEDIUM | CONFIRMED | MEDIUM |
| 16 | test_combat_ops.py | HIGH | DOWNGRADED | MEDIUM (partial removal only) |
| 17 | test_ship_stats_phase_ordering 2 tests | HIGH | CONFIRMED | HIGH |
| 18 | 5 hasattr tests in phases file | HIGH | CONFIRMED | HIGH |
| 19 | TestModeCharacteristics | MEDIUM | CONFIRMED | MEDIUM |
| 20 | 6 interface-existence tests | MEDIUM | CONFIRMED | MEDIUM |
| 21 | TestAIControllerEngageDistance | HIGH | CONFIRMED | HIGH |
| 22 | TestAIControllerCapabilitiesCache | HIGH | DOWNGRADED | MEDIUM (2 unique edge cases) |
| 23 | TestAIControllerScoreAndSort | HIGH | DOWNGRADED | LOW (evaluation failure test unique) |
| 24 | TestIControllableAbstractContract+Mock | MEDIUM | DOWNGRADED | MEDIUM (keep contract, remove mock) |
| 25 | TestFormationIntegrityWithAdapter | MEDIUM | REJECTED (KEEP) | KEEP |

## Key Findings

1. **Claim 9 (shadowed TestHullAutoEquip) is a real bug** -- the first class's test never runs. Fix by renaming, not deleting.
2. **Claim 12 (DI source-reading tests) is incorrectly classified** -- these are architecture guard tests with real value.
3. **Claim 14 (component helpers) is wrong** -- substantial unique coverage exists in the helper files.
4. **Claim 25 (adapter formation test) is wrong** -- tests a documented bug fix with distinct code path.
5. **Several "HIGH" claims should be MEDIUM** because the removal requires additional action (moving tests, removing production code) to be safe.
