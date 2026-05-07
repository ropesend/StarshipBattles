# Test Review Report: Simulation Components & Entities

## Scope
- **Source files reviewed** (with statement counts):
  - game/simulation/components/__init__.py (0 stmts, 100%)
  - game/simulation/components/abilities/__init__.py (27 stmts, 100%)
  - game/simulation/components/abilities/base.py (183 stmts, 100%)
  - game/simulation/components/abilities/cargo.py (38 stmts, 100%)
  - game/simulation/components/abilities/colonize.py (24 stmts, 100%)
  - game/simulation/components/abilities/crew.py (39 stmts, 100%)
  - game/simulation/components/abilities/defense.py (44 stmts, 100%)
  - game/simulation/components/abilities/harvester.py (74 stmts, 94.6%)
  - game/simulation/components/abilities/markers.py (65 stmts, 96.9%)
  - game/simulation/components/abilities/planetary.py (150 stmts, 90.0%)
  - game/simulation/components/abilities/propulsion.py (52 stmts, 100%)
  - game/simulation/components/abilities/resources.py (134 stmts, 94.0%)
  - game/simulation/components/abilities/stat_keys.py (80 stmts, 98.8%)
  - game/simulation/components/abilities/superweapons.py (28 stmts, 100%)
  - game/simulation/components/abilities/ui_colors.py (23 stmts, 100%)
  - game/simulation/components/abilities/weapons.py (192 stmts, 92.7%)
  - game/simulation/components/ability_manager.py (128 stmts, 92.2%)
  - game/simulation/components/component.py (150 stmts, 94.7%)
  - game/simulation/components/component_constants.py (30 stmts, 100%)
  - game/simulation/components/component_health_manager.py (36 stmts, 100%)
  - game/simulation/components/component_loader.py (151 stmts, 64.2%) **CRITICAL**
  - game/simulation/components/component_resource_manager.py (36 stmts, 100%)
  - game/simulation/components/component_stats_calculator.py (108 stmts, 97.2%)
  - game/simulation/components/modifier_effects.py (71 stmts, 100%)
  - game/simulation/components/modifier_introspection.py (87 stmts, 100%)
  - game/simulation/components/modifier_manager.py (129 stmts, 76.7%) **LOW**
  - game/simulation/components/modifier_schema.py (96 stmts, 97.9%)
  - game/simulation/components/modifiers.py (56 stmts, 98.2%)
  - game/simulation/entities/ability_aggregator.py (71 stmts, 100%)
  - game/simulation/entities/combat_endurance.py (71 stmts, 100%)
  - game/simulation/entities/layer_data.py (22 stmts, 100%)
  - game/simulation/entities/projectile.py (98 stmts, 98.0%)
  - game/simulation/entities/ship.py (277 stmts, 97.8%)
  - game/simulation/entities/ship_combat_engine.py (70 stmts, 94.3%)
  - game/simulation/entities/ship_combat_manager.py (62 stmts, 93.5%)
  - game/simulation/entities/ship_component_manager.py (115 stmts, 100%)
  - game/simulation/entities/ship_design_stats.py (49 stmts, 89.8%)
  - game/simulation/entities/ship_formation.py (47 stmts, 100%)
  - game/simulation/entities/ship_layer_manager.py (89 stmts, 89.9%)
  - game/simulation/entities/ship_loader.py (68 stmts, 98.5%)
  - game/simulation/entities/ship_physics.py (43 stmts, 90.7%)
  - game/simulation/entities/ship_resource_manager.py (12 stmts, 100%)
  - game/simulation/entities/ship_serialization.py (102 stmts, 95.1%)
  - game/simulation/entities/ship_stat_querier.py (41 stmts, 100%)
  - game/simulation/entities/ship_stats.py (291 stmts, 95.5%)
  - game/simulation/entities/ship_validator_helper.py (18 stmts, 77.8%) **LOW**
  - game/simulation/interfaces/__init__.py (5 stmts, 100%)
  - game/simulation/interfaces/ability_protocols.py (89 stmts, 95.5%)
  - game/simulation/interfaces/ai_controller.py (11 stmts, 100%)
  - game/simulation/interfaces/component_protocols.py (42 stmts, 97.6%)
  - game/simulation/interfaces/entity_protocols.py (140 stmts, 97.9%)
  - game/simulation/validation/__init__.py (3 stmts, 100%)
  - game/simulation/validation/base.py (18 stmts, 94.4%)
  - game/simulation/validation/ship_validator.py (218 stmts, 98.6%)

- **Test files reviewed:**
  - tests/unit/simulation/components/ (19 test files + abilities/ with 19 test files)
  - tests/unit/simulation/entities/ (17 test files)
  - tests/unit/entities/ (13 test files + ship_helpers/ with 2 test files)
  - tests/unit/modifiers/ (23 test files)
  - tests/unit/abilities/ (4 test files)
- Coverage data referenced: yes

## Summary
- Test files reviewed: 78
- Source files reviewed: 54
- Tests flagged for removal: 7 items (estimated LOC: ~157)
- Tests flagged as happy-path-only: 4
- Source files with inadequate coverage: 5

---

## A. Tests Recommended for Removal

### A1. Duplicate TestHullAutoEquip class in test_ship.py
- **File:** tests/unit/entities/test_ship.py
- **Test(s):** `TestHullAutoEquip` (lines 276-291) -- duplicated by `TestHullAutoEquip` (lines 403-441)
- **Reason:** DUPLICATE_OF:tests/unit/entities/test_ship.py:403
- **Confidence:** HIGH
- **Evidence:** Two classes with identical name `TestHullAutoEquip` in the same file. The first (line 276) has 1 test `test_hull_auto_equip` using `registry_with_hull` fixture. The second (line 403) has 3 tests using `fresh_registries` -- `test_init_equips_default_hull`, `test_change_class_equips_new_hull`, `test_no_hull_if_class_has_no_default`. Python silently replaces the first class with the second, meaning the first class's tests never execute.
- **Estimated LOC saved:** 16

### A2. ComponentStatus enum existence tests
- **File:** tests/unit/simulation/components/test_component_constants.py
- **Test(s):** `TestComponentStatusEnum::test_component_status_active`, `test_component_status_damaged`, `test_component_status_no_crew`, `test_component_status_no_power`, `test_component_status_no_fuel`, `test_component_status_no_ammo`
- **Reason:** TRIVIAL_CONSTANT -- tests only assert `hasattr(ComponentStatus, 'ACTIVE')` and `ComponentStatus.ACTIVE is not None`, which merely confirms the enum member exists. Lines 17-49.
- **Confidence:** HIGH
- **Evidence:** Lines 18-19: `assert hasattr(ComponentStatus, 'ACTIVE')` and `assert ComponentStatus.ACTIVE is not None`. These guard against removing an enum variant, but Python enums already enforce this at import time. The only useful test in this class is `test_component_status_all_unique` (line 46) which validates an actual invariant.
- **Estimated LOC saved:** 30

### A3. Deprecated static method tests in ModifierManager
- **File:** tests/unit/simulation/components/test_modifier_manager.py
- **Test(s):** `TestModifierManagerStandalone::test_manager_add_modifier_static`, `test_manager_remove_modifier_static`, `test_manager_get_modifier_static` (lines 141-177)
- **Reason:** DEAD_CODE -- These test `ModifierManager.add_modifier_static`, `remove_modifier_static`, `get_modifier_static` which are explicitly marked "DEPRECATED: Will be removed in Task 1.3" in modifier_manager.py (lines 223-285). The stateful instance methods (tested comprehensively in the same file) are the replacement.
- **Confidence:** MEDIUM -- depends on Task 1.3 timeline. These should be removed together with the deprecated methods.
- **Evidence:** Source modifier_manager.py lines 223, 253, 276: docstrings say "DEPRECATED: Use instance ... instead. Will be removed in Task 1.3."
- **Estimated LOC saved:** 37

### A4. ShipComponentManagerDI source-reading tests
- **File:** tests/unit/simulation/entities/test_ship_component_manager_di.py
- **Test(s):** `TestShipComponentManagerDI::test_no_global_registry_import_in_component_manager`, `test_no_global_registry_import_in_validator_helper`
- **Reason:** TESTS_NOTHING_REAL -- These tests read the source file as text and check that the string `get_default_registry_provider` does not appear. This is an import-checking test that has no functional value. If the import were added, the actual behavior tests would catch the regression.
- **Confidence:** MEDIUM
- **Evidence:** Lines 15-29: Uses `importlib.util.find_spec` to open the source file and do `assert 'get_default_registry_provider' not in content`. This does not exercise any game logic.
- **Estimated LOC saved:** 30

### A5. TestDefaultMaxMass::test_constant_exists
- **File:** tests/unit/entities/test_ship.py
- **Test(s):** `TestDefaultMaxMass::test_constant_exists` (line 491-494)
- **Reason:** TRIVIAL_CONSTANT -- Asserts `DEFAULT_MAX_MASS == 1000`. This is a magic-number check that will break if the constant legitimately changes, providing no regression value.
- **Confidence:** HIGH
- **Evidence:** Line 494: `assert DEFAULT_MAX_MASS == 1000`. The companion test `test_ship_uses_constant_for_unknown_class` (line 496) already validates the same constant is used functionally, making this redundant.
- **Estimated LOC saved:** 4

### A6. Duplicate component operations between old and new entity directories
- **File:** tests/unit/entities/ship_helpers/test_component_getters.py + test_component_operations.py
- **Test(s):** `TestGetAllComponents`, `TestIterComponents`, `TestGetComponentsByAbility`, `TestGetComponentsByLayer`, `TestHasComponents`, `TestFindComponentWithIndex`, `TestClearNonHullComponents`
- **Reason:** DUPLICATE_OF:tests/unit/simulation/entities/test_ship_component_manager.py -- The newer test_ship_component_manager.py covers add/remove/get_all/iter/ability_query/weapon_cache/clear_non_hull/has_components/find_component with fresh_registries, making the older ship_helpers tests redundant.
- **Confidence:** MEDIUM -- The ship_helpers tests are more granular (e.g., test_returns_defensive_copy, test_layer_matches_component_assignment, test_all_returned_components_in_layer) and some may cover edge cases the newer tests don't. However, the core behavior is fully duplicated.
- **Evidence:** Both test suites test the same Ship facade methods: `get_all_components()`, `iter_components()`, `get_components_by_ability()`, `get_components_by_layer()`, `has_components()`, `find_component_with_index()`, `clear_non_hull_components()`. The simulation/ tests were written as part of PROJ-240 (TDD-first), and the entities/ship_helpers/ tests are older. Recommend merging any unique edge-case coverage into the simulation/ tests, then deleting the older files.
- **Estimated LOC saved:** ~40 (after migrating unique edge cases)

### A7. TestShipStatQuerierInitialization trivial tests
- **File:** tests/unit/entities/test_ship_stat_querier.py
- **Test(s):** `TestShipStatQuerierInitialization::test_init_stores_ship_reference`, `test_init_with_different_ships` (lines 263-283)
- **Reason:** TRIVIAL_CONSTANT -- These only verify that `ShipStatQuerier(mock_ship)` stores the ship reference, which is a trivial constructor assignment.
- **Confidence:** MEDIUM -- While trivial, these document the constructor contract. Could be collapsed into a single test.
- **Evidence:** Lines 269-270: `assert querier._ship is mock_ship`. Lines 281-283: Creates two queriers and asserts they reference different ships. Both test a single-line constructor.
- **Estimated LOC saved:** ~20

---

## B. Tests That Are Happy-Path-Only

### B1. component_loader.py -- no tests for error paths
- **File:** (No dedicated test file for component_loader.py)
- **Test(s):** Coverage comes only from integration via fresh_registries fixture
- **What's tested:** Components successfully loaded from data files
- **What's missing:**
  - `load_components_data` with nonexistent file (line 93-99)
  - `load_components_data` with malformed JSON (line 126-128)
  - `load_components_data` with invalid component data (lines 111-116 error handling)
  - `load_components` with `registry_provider=None` raising ValueError (line 146)
  - `load_modifiers_data` with nonexistent file (lines 194-201)
  - `load_modifiers_data` with malformed JSON (lines 227-228)
  - `load_modifiers` with `registry_provider=None` raising ValueError (line 244)
  - `create_component` with `registries=None` raising ValidationException (lines 285-290)
  - `get_all_components` with `registries=None` raising ValidationException (lines 312-317)
  - Cache hit paths in `load_components` (lines 154-157) and `load_modifiers` (lines 253-256)
- **Source method(s) affected:** game/simulation/components/component_loader.py:90-319
- **Priority:** HIGH -- 64.2% coverage is the lowest in the entire domain. 54 missing statements.

### B2. ship_validator_helper.py -- no dedicated unit tests
- **File:** (No dedicated test file)
- **Test(s):** Only tested transitively through test_ship.py and test_bridge_requirement_removal.py
- **What's tested:** `check_validity()` called indirectly via Ship integration tests
- **What's missing:**
  - `check_validity()` when validation passes (line 42-47 full path)
  - `check_validity()` when validation fails with mass errors (line 46)
  - `get_validation_warnings()` (line 49-57) -- never tested directly
  - `get_missing_requirements()` when valid (returns empty list, line 67-68)
  - `get_missing_requirements()` when invalid (returns error list, line 70)
- **Source method(s) affected:** game/simulation/entities/ship_validator_helper.py:33-70
- **Priority:** MEDIUM -- 77.8% coverage. All three methods are thin delegates, so the risk is lower, but the missing lines (42, 44, 46, 47) indicate the methods are exercised but branches within them are not fully covered.

### B3. ship_layer_manager.py -- migrate_components path untested
- **File:** tests/unit/simulation/entities/test_ship_layer_manager.py
- **Test(s):** `TestChangeClass` has 4 tests for change_class
- **What's tested:** Basic class change, layer reinitialization, unknown class rejection
- **What's missing:**
  - `change_class(new_class, migrate_components=True)` with component migration (lines 126-166)
  - Component migration fallback to other layers when original layer doesn't exist (lines 158-163)
  - Warning when component can't fit in any layer (line 166)
  - `equip_default_hull` when `create_component` returns None (line 111)
- **Source method(s) affected:** game/simulation/entities/ship_layer_manager.py:113-168
- **Priority:** MEDIUM -- 89.9% coverage. The migrate_components path (lines 152-166) is untested. Note: tests/unit/entities/test_ship.py::TestShipClassMutation::test_change_class_migration does test this via the Ship facade, but only the success path.

### B4. ship_design_stats.py -- toggle and damage paths untested
- **File:** (No test file found for ship_design_stats.py)
- **Test(s):** None in this review domain
- **What's tested:** (Unknown -- possibly tested from strategy layer)
- **What's missing:**
  - `calculate_design_stats` with `component_toggles` (lines 43-51)
  - `calculate_design_stats` with `component_damage` (lines 58-62)
  - `_lookup_damage` indexed forms (lines 107-113)
  - Resource consumption aggregation (lines 74-87)
- **Source method(s) affected:** game/simulation/entities/ship_design_stats.py:16-114
- **Priority:** MEDIUM -- 89.8% coverage. The toggle filtering and damage application branches are not exercised.

---

## C. Source Code with Inadequate Coverage

### C1. component_loader.py (64.2% -- CRITICAL)
- **Source file:** game/simulation/components/component_loader.py (151 stmts)
- **Coverage:** 64.2% -- 54 missing statements
- **Untested areas:**
  - `load_components_data`: File-not-found fallback path (lines 93-99), JSON parsing error handlers (lines 123-131), component creation error handlers (lines 111-116), warning on partial load failures (lines 118-119)
  - `load_components`: `registry_provider=None` guard (line 146), cache hit path (lines 154-157), empty result early return (line 168)
  - `load_modifiers_data`: File-not-found fallback (lines 194-201), JSON/schema validation paths (lines 210-211, 215-217), error handlers (lines 224-232)
  - `load_modifiers`: `registry_provider=None` guard (line 244), cache hit path (lines 253-256)
  - `create_component`: `registries=None` guard (lines 285-290), component-not-found path (lines 297-298)
  - `get_all_components`: `registries=None` guard (lines 312-317)
- **Risk:** Corrupt or missing data files would hit untested error paths in production. Cache invalidation bugs would be invisible. DI enforcement (registries=None) is untested for some functions.
- **Priority:** HIGH

### C2. modifier_manager.py (76.7% -- LOW)
- **Source file:** game/simulation/components/modifier_manager.py (129 stmts)
- **Coverage:** 76.7% -- 30 missing statements
- **Untested areas:**
  - All deprecated static methods (lines 223-330): `add_modifier_static`, `remove_modifier_static`, `remove_modifier_inplace`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`
  - `get_stat_summary` "set" operation branch (line 217)
- **Risk:** LOW for the deprecated methods (they're scheduled for removal). The "set" operation branch in `get_stat_summary` is a real gap but unlikely to be hit with current modifier data.
- **Priority:** LOW -- Most missing coverage is deprecated code. Remove the deprecated methods to bring coverage near 100%.

### C3. ship_validator_helper.py (77.8%)
- **Source file:** game/simulation/entities/ship_validator_helper.py (18 stmts)
- **Coverage:** 77.8% -- 4 missing statements
- **Untested areas:**
  - `check_validity`: mass_limits_ok update (line 46), full return path (line 47)
  - `get_validation_warnings`: never directly tested (line 42-44 covered transitively but lines 46-47 are not)
  - `get_missing_requirements`: partial path coverage
- **Risk:** LOW -- these are thin delegates to ShipDesignValidator which has 98.6% coverage. The helper just formats outputs.
- **Priority:** LOW

### C4. ship_layer_manager.py (89.9%)
- **Source file:** game/simulation/entities/ship_layer_manager.py (89 stmts)
- **Coverage:** 89.9% -- 9 missing statements
- **Untested areas:**
  - `equip_default_hull` failure path when create_component returns None (line 111)
  - `change_class` with `migrate_components=True`: the entire component migration loop (lines 152-166), including the fallback layer search (lines 158-163) and the warning for components that don't fit (line 166)
- **Risk:** MEDIUM -- class changes with component migration is a user-facing feature. If migration silently drops components, users would lose their ship builds.
- **Priority:** MEDIUM

### C5. ship_physics.py (90.7%)
- **Source file:** game/simulation/entities/ship_physics.py (43 stmts)
- **Coverage:** 90.7% -- 4 missing statements (lines 50-53)
- **Untested areas:**
  - Lines 50-53 appear to be in the `update_physics_movement` method, likely a branch for when total_thrust is calculated from ability values during the movement update
- **Risk:** LOW -- The ShipPhysicsMixin tests in test_ship_physics.py are thorough (acceleration, deceleration, rotation, edge cases). The missing lines may be a rarely-exercised branch.
- **Priority:** LOW

---

## D. Cross-Domain Observations

### D1. Old tests/unit/entities/ directory should be consolidated
The `tests/unit/entities/` directory (3,366 LOC across 15 files) is the **old** test location from before the `tests/unit/simulation/entities/` restructure. Key findings:

- **Not a wholesale duplicate:** The old directory contains unique, valuable tests that are NOT in the simulation/ directory. For example:
  - `test_ship.py`: TestShip (add_component_constraints, mass_calculation, damage_armor_absorption, serialization), TestShipClassMutation (change_class_migration, derelict_status_logic), TestHullAutoEquip, TestComponentAttachment, TestChangeClassInvalidInput, TestTotalDefenseScoreInitialization, TestDefaultMaxMass
  - `test_ship_stat_querier.py`: Comprehensive 775-line test suite with edge cases (non-numeric values, boolean handling, float accumulation, negative values) -- this has NO equivalent in simulation/entities/
  - `test_abilities.py` and `test_ability_interface.py`: Ability creation, factory, polymorphism, PDC detection, get_primary_value interface tests
  - `test_components.py`: Modifier stacking, order independence, turret mount diminishing returns, modifier data methods
  - `test_planetary_complex.py`: Planetary Complex vehicle type acceptance/rejection tests
  - `test_ship_theme_logic.py`: UI asset theme loading -- this belongs in tests/unit/ui/, not entities/

- **Duplicated behavior between directories:**
  - `test_component_getters.py` + `test_component_operations.py` overlap with `test_ship_component_manager.py`
  - `test_component_di.py` overlaps with tests in `test_ship_component_manager.py` and the DI fixture setup
  - `test_component_cache.py` tests ComponentCacheManager which is in component_loader.py (simulation layer)

- **Recommendation:** Migrate unique tests from `tests/unit/entities/` into `tests/unit/simulation/entities/` or `tests/unit/simulation/components/` as appropriate, then delete the old directory. The `test_ship_theme_logic.py` file should move to `tests/unit/ui/`.

### D2. test_ship_theme_logic.py is in the wrong domain
- **File:** tests/unit/entities/test_ship_theme_logic.py (356 lines)
- Tests `game.ui.assets.ShipThemeManager` which is UI layer code
- Should be in `tests/unit/ui/` not `tests/unit/entities/`

### D3. Deprecated static methods in modifier_manager.py inflate missing coverage
The 30 missing statements in modifier_manager.py are almost entirely from deprecated `_static` methods (lines 223-330). These are scheduled for removal in "Task 1.3". Removing them would bring coverage from 76.7% to approximately 97%. The deprecated methods are still tested in test_modifier_manager.py::TestModifierManagerStandalone but those tests should also be removed when the methods are deleted.

### D4. No test file for component_loader.py
Despite being the lowest-coverage file in the domain (64.2%), there is no dedicated `test_component_loader.py` file. The existing coverage comes entirely from integration tests that load real data files via the `fresh_registries` fixture. Error paths, cache behavior, and DI guards are completely untested.

### D5. Duplicate TestHullAutoEquip class (Python silent override)
In `tests/unit/entities/test_ship.py`, the class `TestHullAutoEquip` is defined twice (lines 276 and 403). Python silently replaces the first with the second, so the first class's `test_hull_auto_equip` method never executes. This is a latent bug in the test suite.
