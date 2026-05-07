# Test Review Report: AI Domain

## Scope
- Source files reviewed:
  - `game/ai/__init__.py` (6 stmts, 100.0%)
  - `game/ai/ai_factory.py` (18 stmts, 100.0%)
  - `game/ai/behaviors.py` (219 stmts, 93.2%, 15 missing)
  - `game/ai/combat_utils.py` (82 stmts, 85.4%, 12 missing)
  - `game/ai/controller.py` (235 stmts, 97.9%, 5 missing)
  - `game/ai/interfaces/controllable.py` (205 stmts, 81.5%, 38 missing)
  - `game/ai/protocols.py` (52 stmts, 100.0%)
  - `game/ai/strategy_manager.py` (57 stmts, 98.2%, 1 missing)
  - `game/ai/target_evaluator.py` (126 stmts, 99.2%, 1 missing)
- Test files reviewed:
  - `tests/unit/ai/test_ai.py` (317 lines)
  - `tests/unit/ai/test_ai_controller_unit.py` (1152 lines)
  - `tests/unit/ai/test_ai_controller_edge_cases.py` (413 lines)
  - `tests/unit/ai/test_ai_controller_interface.py` (469 lines)
  - `tests/unit/ai/test_ai_protocols.py` (296 lines)
  - `tests/unit/ai/test_advanced_behaviors.py` (177 lines)
  - `tests/unit/ai/test_behavior_units.py` (946 lines)
  - `tests/unit/ai/test_combat_utils.py` (559 lines)
  - `tests/unit/ai/test_controllable_adapter.py` (246 lines)
  - `tests/unit/ai/test_controllable_adapter_edge_cases.py` (484 lines)
  - `tests/unit/ai/test_movement_and_ai.py` (140 lines)
  - `tests/unit/ai/test_strategy_manager_singleton.py` (291 lines)
  - `tests/unit/ai/test_strategy_system.py` (237 lines)
  - `tests/unit/ai/test_targeting_rules.py` (224 lines)
  - `tests/unit/ai/test_target_evaluator_edge_cases.py` (523 lines)
  - `tests/unit/ai/test_target_evaluator_rules.py` (1069 lines)
  - `tests/unit/ai/test_ai_capabilities_cache.py` (234 lines)
  - `tests/unit/ai/target_evaluator/test_capabilities_cache.py` (234 lines)
  - `tests/unit/ai/formation_prediction/test_formation_behavior.py` (387 lines)
  - `tests/unit/ai/formation_prediction/conftest.py` (101 lines)
  - `tests/integration/ai_strategy/conftest.py` (60 lines)
  - `tests/integration/ai_strategy/test_commands.py` (81 lines)
  - `tests/integration/ai_strategy/test_evaluation.py` (284 lines)
  - `tests/integration/ai_strategy/test_response.py` (204 lines)
- Coverage data referenced: yes

## Summary
- Test files reviewed: 24 (including 2 conftest files)
- Source files reviewed: 9
- Tests flagged for removal: 9 (estimated LOC: 310)
- Tests flagged as happy-path-only: 5
- Source files with inadequate coverage: 2

## A. Tests Recommended for Removal

### A1. Duplicate engage distance tests across 3 files

- **File:** `tests/unit/ai/test_ai_controller_edge_cases.py`
- **Test(s):** `TestAIControllerEngageDistance` (lines 332-375, 6 tests: `test_engage_distance_max_range`, `test_engage_distance_ram`, `test_engage_distance_numeric_value`, `test_engage_distance_integer_value`, `test_engage_distance_unknown_value`, `test_engage_distance_missing_key`)
- **Reason:** DUPLICATE_OF:`tests/unit/ai/test_ai_controller_unit.py:TestGetEngageDistanceMultiplier` (lines 74-100)
- **Confidence:** HIGH
- **Evidence:** Both test classes call `controller.get_engage_distance_multiplier()` with identical inputs (`'max_range'`, `'ram'`, numeric, `'unknown'`, empty dict) and assert identical expected outputs (1.0, 0.0, float, 1.0, 1.0). The edge_cases version uses a fully mocked ship while the unit version patches StrategyManager, but the function under test is a pure helper with no dependencies on either, making these exact duplicates. Additionally, `tests/integration/ai_strategy/test_response.py:TestStrategyResolution:test_engage_distance_multiplier` (line 133-144) tests the same 3 cases again with real ships.
- **Estimated LOC saved:** 50 (removing edge_cases version)

### A2. Duplicate capabilities cache tests

- **File:** `tests/unit/ai/test_ai_controller_edge_cases.py`
- **Test(s):** `TestAIControllerCapabilitiesCache` (lines 273-329, 4 tests: `test_build_capabilities_cache_empty_ships`, `test_build_capabilities_cache_ship_without_id`, `test_build_capabilities_cache_with_weapons`, `test_build_capabilities_cache_with_pdc`)
- **Reason:** DUPLICATE_OF:`tests/unit/ai/test_ai_capabilities_cache.py:TestBuildCapabilitiesCache` (lines 80-168)
- **Confidence:** HIGH
- **Evidence:** `test_ai_capabilities_cache.py` provides a superset: 8 tests covering structure, armed/unarmed, PDC/no-PDC, multiple ships, and duplicate name handling. The 4 tests in edge_cases test exactly the same things (empty list returns `{}`, ship without ID skipped, weapons detected, PDC detected) with identical mock setups. The edge_cases versions add no additional value.
- **Estimated LOC saved:** 60

### A3. Duplicate score_and_sort tests

- **File:** `tests/unit/ai/test_ai_controller_edge_cases.py`
- **Test(s):** `TestAIControllerScoreAndSort` (lines 378-413, 2 tests)
- **Reason:** DUPLICATE_OF:`tests/unit/ai/test_ai.py:TestTargetingHelpers` (lines 289-317)
- **Confidence:** HIGH
- **Evidence:** `test_ai.py:test_score_and_sort_enemies_returns_sorted_list` (line 289) and `test_ai.py:test_score_and_sort_enemies_excludes_negative_infinity` (line 298) test the exact same two behaviors: sorted output with empty rules, and exclusion of -inf scores. The edge_cases versions at lines 381 and 407 duplicate these with mocked ships instead of real ships, but add no new scenarios. Additionally, `test_ai_capabilities_cache.py:TestScoreAndSortEnemiesWithCache` (line 170) covers more advanced cache-integrated sorting.
- **Estimated LOC saved:** 40

### A4. Controllable adapter contract tests are superseded

- **File:** `tests/unit/ai/test_controllable_adapter.py`
- **Test(s):** `TestIControllableAbstractContract` (lines 13-65, 3 tests), `TestMockImplementation` (lines 68-246, 2 tests with ~180 LOC of mock class boilerplate)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** MEDIUM
- **Evidence:** `test_cannot_instantiate_icontrollable` (line 18) and `test_concrete_subclass_must_implement_all` (line 48) only verify Python ABC mechanics, not game logic. `test_all_abstract_methods_present` (line 26) asserts a frozen list of method names which is fragile and couples the test to Python internal implementation. `TestMockImplementation` (lines 68-246) creates a 170-line mock implementation just to verify `isinstance` and that `get_position()` returns hardcoded values. These are testing Python's `ABC` class, not the game. However, `test_all_abstract_methods_present` does serve as a guard against accidentally removing abstract methods from the interface, so it could be kept as a contract test.
- **Estimated LOC saved:** 100 (conservative: remove TestMockImplementation, keep contract test)

### A5. Overlapping formation integrity tests across 3 files

- **File:** `tests/unit/ai/test_ai_controller_interface.py`
- **Test(s):** `TestFormationIntegrityWithAdapter` (lines 387-469, 2 tests: `test_formation_member_removed_when_ship_damaged`, `test_formation_member_not_removed_when_undamaged`)
- **Reason:** DUPLICATE_OF:`tests/unit/ai/test_ai_controller_unit.py:TestCheckFormationIntegrity` (lines 704-788) and `tests/unit/ai/formation_prediction/test_formation_behavior.py:TestFormationIntegrity` (lines 341-383)
- **Confidence:** MEDIUM
- **Evidence:** Three separate test files all test `_check_formation_integrity()` with identical scenarios: damaged propulsion triggers dropout, undamaged propulsion stays in formation. The `test_ai_controller_unit.py` version (lines 704-788) is the most thorough with 5 tests including edge cases (no propulsion components, mixed components). The `test_ai_controller_interface.py` version and `formation_prediction/test_formation_behavior.py:TestFormationIntegrity` version both duplicate the damaged/undamaged tests with slightly different mock setups. The interface version also duplicates the adapter-unwrapping test from `test_advanced_behaviors.py:test_formation_integrity__ability_check` (line 146).
- **Estimated LOC saved:** 60 (remove interface and formation_prediction duplicates, keep controller_unit version)

## B. Tests That Are Happy-Path-Only

### B1. combat_utils: IControllable-path code paths untested

- **File:** `tests/unit/ai/test_combat_utils.py`
- **Test(s):** `TestGetPosition`, `TestGetRotation`, `TestGetAllComponents`
- **What's tested:** Direct attribute access path (entity with `.position`, `.angle`, `get_all_components()`)
- **What's missing:** The `IControllable` branch in `get_position()` (lines 103-107), `get_rotation()` (lines 123-124), and `get_all_components()` (lines 139-140) are never tested. These branches check `isinstance(entity, IControllable)` and call interface methods. The tests only exercise the direct-attribute fallback path. This accounts for most of the 12 missing lines in combat_utils.py coverage.
- **Source method(s) affected:** `game/ai/combat_utils.py:103-107`, `game/ai/combat_utils.py:123-124`, `game/ai/combat_utils.py:139-140`
- **Priority:** MEDIUM

### B2. combat_utils: safe_distance exception path untested

- **File:** `tests/unit/ai/test_combat_utils.py`
- **Test(s):** `TestSafeDistance`
- **What's tested:** Valid positions (3-4-5 triangle) and None positions
- **What's missing:** The `except (AttributeError, TypeError)` branch at `game/ai/combat_utils.py:169-171` is never triggered. A test where `position.distance_to()` raises `AttributeError` or `TypeError` would cover this defensive path.
- **Source method(s) affected:** `game/ai/combat_utils.py:169-171`
- **Priority:** LOW

### B3. combat_utils: is_in_pdc_arc IControllable branch untested

- **File:** `tests/unit/ai/test_combat_utils.py`
- **Test(s):** `TestIsInPdcArc`, `TestIsInPdcArcEdgeCases`
- **What's tested:** Ships with direct `.position` and `.get_components_by_ability` attributes
- **What's missing:** The `IControllable` isinstance branch at `game/ai/combat_utils.py:215-216` is never exercised. All tests use `Mock(spec=[...])` with direct attributes. A test passing a `ShipControllableAdapter` or `IControllable` mock would cover this. Also, the raw-ship fallback where `getattr(ship, 'get_components_by_ability', None)` is not callable (lines 219-221) is untested.
- **Source method(s) affected:** `game/ai/combat_utils.py:215-221`, `game/ai/combat_utils.py:234`, `game/ai/combat_utils.py:238`
- **Priority:** MEDIUM

### B4. behaviors.py: ErraticBehavior leash path and FormationBehavior correction cap untested

- **File:** `tests/unit/ai/test_behavior_units.py`
- **Test(s):** No ErraticBehavior tests exist in `test_behavior_units.py` at all
- **What's tested:** Nothing for ErraticBehavior
- **What's missing:** The entire `ErraticBehavior` class (lines 401-467 of `behaviors.py`) has no unit tests. The leash constraint code path (lines 432-447, which accounts for all 15 missing coverage lines in behaviors.py) is completely untested. The leash overshoot steering logic, the dead band jitter prevention (line 444), and the timer-based direction changes are all uncovered. Additionally, `FormationBehavior._correct_position()` line 342 (`correction.scale_to_length(MAX_CORRECTION_FORCE)`) is unreached, meaning the cap on correction force magnitude is untested.
- **Source method(s) affected:** `game/ai/behaviors.py:401-467` (ErraticBehavior), `game/ai/behaviors.py:342` (FormationBehavior correction cap)
- **Priority:** HIGH - ErraticBehavior is used in simulation tests for erratic targets, and the leash constraint is critical for preventing targets from flying off the map

### B5. controller.py: Dead code paths in formation and targeting

- **File:** `tests/unit/ai/test_ai_controller_unit.py`
- **Test(s):** Various
- **What's tested:** Primary targeting, formation master handling, behavior selection
- **What's missing:** Line 235-236 (`slow_down` branch for dead/inactive formation members in `_handle_formation_master`), line 264 (an unreachable return or branch in update), line 278 (similarly unreachable), line 421 (the `not member.is_alive or not member.formation.active` continue in the second formation loop). These are defensive guard clauses that current tests don't trigger because mocks always have alive active members.
- **Source method(s) affected:** `game/ai/controller.py:235-236`, `game/ai/controller.py:264`, `game/ai/controller.py:278`, `game/ai/controller.py:421`
- **Priority:** LOW - these are defensive guards, not primary logic

## C. Source Code with Inadequate Coverage

### C1. `game/ai/interfaces/controllable.py` (205 stmts, 81.5%)

- **Coverage:** 81.5% with 38 missing lines
- **Qualitative assessment:** The 38 missing lines are all the abstract method `pass` bodies in `IControllable` (lines 43, 48, 53, 58, 63, 68, 73, 78, 83, 92, 97, 102, 112, 117, 122, 127, 136, 148, 157, 162, etc.). This is a **false positive**: abstract methods with `pass` bodies are never executed (the concrete `ShipControllableAdapter` overrides them all). Python's coverage tool counts these as "uncovered" but they are unreachable by design.
- **Untested areas:** None in practice. The `ShipControllableAdapter` implementation has thorough tests in `test_controllable_adapter_edge_cases.py` covering all 30+ methods, formation edge cases, and the leave_formation error handling.
- **Risk:** Very low. The adapter is a thin delegation layer and is well tested.
- **Priority:** LOW - This is a coverage tool artifact, not a real coverage gap.

### C2. `game/ai/combat_utils.py` (82 stmts, 85.4%)

- **Coverage:** 85.4% with 12 missing lines
- **Qualitative assessment:** Real coverage gaps exist. The missing lines fall into three categories:
  1. **IControllable isinstance branches** (lines 85, 104, 106, 107, 124): Never triggered because all tests use raw mocks with direct attributes rather than `IControllable` instances. These branches are exercised in production when `ShipControllableAdapter` is passed.
  2. **Error/fallback paths** (lines 169-171, 216, 221): The `except` clause in `safe_distance` and the raw-ship fallback in `is_in_pdc_arc` where `getattr` returns a non-callable. These are defensive paths.
  3. **Weapon ability None guard** (lines 234, 238): The path where `comp.get_ability('WeaponAbility')` returns `None` or where the raw ship's `get_components_by_ability` method is not callable.
- **Untested areas:** IControllable code paths in `get_position`, `get_rotation`, `get_all_components`, and `is_in_pdc_arc`; exception handling in `safe_distance`; None guard in `is_in_pdc_arc` weapon iteration.
- **Risk:** Medium. The IControllable paths are exercised in production via the adapter, but a regression in the isinstance check would not be caught by unit tests. The defensive error paths protect against combat crashes.
- **Priority:** MEDIUM

## D. Cross-Domain Observations

### D1. test_ai_controller_unit.py at 1152 lines is proportionate

The file tests 12 distinct functional areas of `controller.py` (235 stmts): engage distance (5 tests), behavior selection (3 tests), satellite exception (1 test), dead ship (1 test), find target (4 tests), behavior context merging (2 tests), formation target sync (2 tests), secondary targets (2 tests), formation master handling (4 tests), formation integrity (5 tests), collision avoidance (8 tests), and navigation (10 tests). This is roughly 5:1 test-LOC to source-LOC, which is typical for AI decision-making logic with many branches and edge cases. The tests are well-organized into focused test classes. No over-testing detected.

### D2. `test_ai_controller_edge_cases.py` is largely redundant

This file (413 lines) was created separately from `test_ai_controller_unit.py` and appears to be an earlier, less thorough testing effort. Of its 5 test classes (22 tests), 3 classes (12 tests, ~150 LOC) are exact duplicates of tests in other files (as detailed in A1, A2, A3). The remaining 2 classes (`TestAIControllerStrategyResolution` with 3 tests and `TestAIControllerUpdateEdgeCases` with 3 tests) provide unique value testing mock-based edge cases for strategy resolution and dead targets, but these could be merged into `test_ai_controller_unit.py` for consolidation.

### D3. Integration tests are valuable and well-scoped

The `tests/integration/ai_strategy/` suite (4 files, 629 lines including conftest) provides genuine cross-layer integration testing with real Ship objects, real SpatialGrid, real component loading, and real StrategyManager data. The `TestAIControllerWithProductionData` class in `test_evaluation.py` (lines 166-284) is particularly valuable -- it loads actual `combat_strategies.json` and verifies all production strategies are resolvable and functional. These should be kept.

### D4. get_capability_cache_key fallback logic may need simulation-layer testing

`combat_utils.py:get_capability_cache_key()` (lines 73-87) falls back from `entity.id` to `entity.name` to `None`. The `entity.id` path is used in production (PROJ-247 gave all ships UUID4 ids), and the `name` fallback exists for older test mocks. Line 85 (`entity_name` fallback) is covered but line 85 is actually the `entity_id is not None` early return. The concern is that if a simulation entity ever has `id=None`, the cache key falls to `.name`, which is not unique across ships. This is a latent bug risk that spans AI and simulation domains.

### D5. ErraticBehavior is used by simulation test framework

`ErraticBehavior` (behaviors.py lines 401-467) is heavily used by the Combat Lab simulation test framework for erratic targets. Despite having zero dedicated unit tests, it is indirectly exercised through simulation tests. However, the leash constraint (lines 432-447) is a critical safety mechanism that should have focused unit tests -- a regression there would cause erratic targets to fly off the map, breaking many simulation tests silently rather than with clear failures.
