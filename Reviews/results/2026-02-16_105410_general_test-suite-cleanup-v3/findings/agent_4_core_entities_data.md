# Agent 4: Core + Entities + Data Tests Analysis

## Summary
- Files analyzed: 95 (47 core + 46 entities + 2 data)
- Removal candidates found: 14
- HIGH confidence: 10
- MEDIUM confidence: 4
- LOW confidence: 2
- Estimated removable lines: ~1,300 (duplicates/trivial)

---

## tests/unit/core/ Analysis

### HIGH Confidence Removal Candidates

#### test_error_codes_coverage.py
- **Location:** `tests/unit/core/test_error_codes_coverage.py`
- **Category:** Duplicate
- **Reason:** Almost entirely duplicates `test_error_codes.py`. Both test uniqueness (TestErrorCodeUniqueness), naming conventions (TestErrorCodeNamingConvention), and category-specific checks. The "coverage" file tests the exact same behaviors -- uniqueness, X### format, category prefix letters -- with slightly different organization. The original `test_error_codes.py` is more comprehensive (155 lines vs 150 lines) and also covers access patterns and minimum set existence.
- **Lines:** ~150 lines that could be removed

#### test_json_utils_edge_cases.py
- **Location:** `tests/unit/core/test_json_utils_edge_cases.py`
- **Category:** Duplicate
- **Reason:** Significantly overlaps with `test_json_utils.py`. Both files test: load_json with missing files returning defaults, load_json with invalid JSON returning defaults, save_json creating parent directories, save_json success returning True, load_json_required raising FileNotFoundError and JSONDecodeError. The edge cases file adds one unique test (save_json_io_error_returns_false via mock and save_json_type_error_returns_false), but these are minor additions that could be merged into the primary file. The overlap is about 80%.
- **Lines:** ~127 lines, of which ~100 are duplicates

#### test_validation_edge_cases.py
- **Location:** `tests/unit/core/test_validation_edge_cases.py`
- **Category:** Duplicate
- **Reason:** Heavy overlap with `test_validation.py`. Both files test: ValidationResult default initialization, message property returning first error/empty string, add_error setting is_valid to False, add_error with codes (first wins), merge behavior (valid into invalid, invalid into valid, combining errors/warnings). The edge cases file adds a few unique tests (init with None errors/warnings, add_error with ErrorCode enum), but the merge and creation tests are mostly duplicated.
- **Lines:** ~165 lines, of which ~120 are duplicates

#### test_config_edge_cases.py
- **Location:** `tests/unit/core/test_config_edge_cases.py`
- **Category:** Duplicate
- **Reason:** Overlaps with `test_config.py`. Both files test: DisplayConfig resolution tuples (default, test), AIConfig values. The edge cases file adds windowed resolution, boundary value checks, and PhysicsConfig constraints, but the resolution tuple tests are direct duplicates. The unique tests (boundary values, constraints) are worth keeping but the duplicate resolution tests are ~20 lines of waste.
- **Lines:** ~104 lines total, ~25 lines of direct duplication

#### logger/test_events.py (in logger subdirectory)
- **Location:** `tests/unit/core/logger/test_events.py`
- **Category:** Duplicate
- **Reason:** Duplicates the TestEventHandler class in `test_logger.py`. Both test: setting event handler, log_event calling handler, log_event doing nothing without handler, handler replacement, clearing handler. The `test_logger.py` version additionally tests exception handling in the handler. The subdirectory version adds tests for log_event with no kwargs and many kwargs, which are marginally useful.
- **Lines:** ~104 lines, of which ~60 are duplicates

#### logger/test_singleton.py (in logger subdirectory)
- **Location:** `tests/unit/core/logger/test_singleton.py`
- **Category:** Duplicate
- **Reason:** Duplicates TestLoggerSingleton and TestModuleLevelFunctions from `test_logger.py`. Both test: singleton same instance, reset creates new instance, log_debug/log_info/log_warning/log_error delegation, set_logging sets enabled. The edge cases in this file (None message, empty string, complex objects, unicode, long messages) are the only unique additions.
- **Lines:** ~175 lines, of which ~100 are duplicates

#### logger/test_warning.py (in logger subdirectory)
- **Location:** `tests/unit/core/logger/test_warning.py`
- **Category:** Duplicate
- **Reason:** Duplicates warning tests already covered in `test_logger.py` (TestLoggerEnabledFlag and TestModuleLevelFunctions both test warning behavior). Tests that log_warning exists, runs when enabled, is suppressed when disabled, and delegates to Logger.warning are all covered in the main logger test file.
- **Lines:** ~56 lines, all duplicated

#### logger/test_levels.py (in logger subdirectory)
- **Location:** `tests/unit/core/logger/test_levels.py`
- **Category:** Duplicate
- **Reason:** Tests log levels and enabled flag behavior already covered by `test_logger.py` TestLoggerEnabledFlag class. Both test that all log methods respect the enabled flag. The setup/formatter tests in test_levels.py are somewhat unique but overlap with what test_logger.py covers for the Logger's basic configuration.
- **Lines:** ~119 lines, of which ~40 are duplicates

### MEDIUM Confidence Removal Candidates

#### test_constants.py
- **Location:** `tests/unit/core/test_constants.py`
- **Category:** Trivial
- **Reason:** Tests that PLANET_RESOURCES is a list with 5 specific string elements. These are trivially obvious checks on a static constant. The entire test class just verifies that a constant list equals `["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]`. If the constant changes, the test would need manual updating anyway, and the constant is unlikely to be accidentally corrupted. The assertion `PLANET_RESOURCES == expected` in test_planet_resources_has_expected_values already covers all other tests.
- **Lines:** ~40 lines

#### test_superweapon_input_actions.py
- **Location:** `tests/unit/core/test_superweapon_input_actions.py`
- **Category:** Trivial / Redundant with test_input_actions.py
- **Reason:** Tests that specific InputAction enum values exist and have correct display names/groups. However, `test_input_actions.py` already has comprehensive tests: `test_all_values_are_unique`, `test_covers_all_actions` (display names cover ALL actions), `test_covers_all_actions` (groups cover ALL actions). These generic tests already catch any missing action, display name, or group membership. The superweapon file just spot-checks 6 specific enum values that are already guaranteed by the exhaustive tests.
- **Lines:** ~93 lines

#### test_resource_loading.py
- **Location:** `tests/unit/core/test_resource_loading.py`
- **Category:** Duplicate
- **Reason:** Has a DUPLICATE `TestLoadResourcesData` class (same name appears twice in the file, lines 60 and 144). The second class (lines 144-184) duplicates tests from the first class. Additionally, the entire file significantly overlaps with `test_resources.py` which tests `load_resources_data`, `_get_default_resources`, and `_resolve_resource_path` with better coverage and additional edge cases. The `test_resources.py` file is more thorough (310 lines with edge cases for None IDs, empty string IDs, duplicate IDs).
- **Lines:** ~185 lines, of which ~80 are duplicates of tests within the same file, and ~100 overlap with test_resources.py

#### test_profiling_edge_cases.py
- **Location:** `tests/unit/core/test_profiling_edge_cases.py`
- **Category:** Partial overlap with profiling subdirectory
- **Reason:** Tests profile_action, profile_block, save_history, record, toggle, clear. Some of these overlap with the profiling subdirectory tests (profiling/test_decorators.py, profiling/test_persistence.py, profiling/test_recording.py). The overlap is moderate -- the edge cases file is more comprehensive in some areas. Consider consolidating.
- **Lines:** ~361 lines, moderate overlap

### LOW Confidence Removal Candidates

#### test_singleton.py
- **Location:** `tests/unit/core/test_singleton.py`
- **Category:** Possibly over-tested
- **Reason:** 313 lines testing SingletonMeta metaclass with 12 test classes. Tests are thorough but possibly excessive for a simple metaclass (basic behavior, independence, thread safety, subclass features, direct construction, edge cases, rapid creation). The thread safety tests with 20 threads and 100 concurrent operations seem like overkill for a simple lock-based singleton. Could be reduced by ~50% while retaining meaningful coverage.
- **Lines:** ~313 lines, could be reduced to ~150

#### test_isolation.py
- **Location:** `tests/unit/core/test_isolation.py`
- **Category:** Infrastructure test / order-dependent
- **Reason:** Tests require sequential execution (part1 then part2) to verify isolation. With pytest-xdist parallel execution, these tests may not run in order. The isolation is already guaranteed by the conftest reset_game_state fixture which is separately tested. These tests essentially re-verify that the fixture works.
- **Lines:** ~119 lines

### Core Files Analyzed and Kept (No Issues Found)

The following 33 files were analyzed and found to be legitimate, non-duplicate, and worth keeping:
- `test_error_codes.py` - ErrorCode enum uniqueness, naming, categories, access, minimum set
- `test_exceptions.py` - Exception hierarchy and inheritance
- `test_input_actions.py` - InputAction enum exhaustive coverage
- `test_config.py` - Config dataclass defaults and values
- `test_json_utils.py` - JSON load/save utilities (primary file)
- `test_logger.py` - Logger singleton, enabled flag, module functions, events (primary file)
- `test_math_vector2.py` - Vector2 edge cases (infinity, NaN, zero-length)
- `test_protocols.py` - Protocol definitions (IRegistryProvider, IResourceProvider)
- `test_protocols_boundary.py` - Boundary protocol tests (MutableMapping, ABC compliance)
- `test_validation.py` - ValidationResult dataclass (primary file)
- `test_hex_math_core.py` - HexCoord coordinate system and neighbors
- `test_paths_config.py` - Paths constants existence and types
- `test_asset_manager.py` - AssetManager resource loading
- `test_pure_loaders.py` - Pure loading function tests
- `test_resources.py` - Resource loading (primary, comprehensive file)
- `test_registry_fixtures.py` - DI fixture tests (fresh_registries, minimal_registries)
- `test_simulation_constants.py` - SimulationConstants class attributes
- `test_strategy_metadata.py` - StrategyMetadataService singleton, data, queries
- `test_service_injection.py` - Service DI patterns
- `test_registry_manager_reload.py` - Registry reload behavior
- `test_registry_provider.py` - IRegistryProvider protocol compliance
- `profiling/test_decorators.py` - Profiling decorator tests
- `profiling/test_persistence.py` - Profiling persistence tests
- `profiling/test_recording.py` - Profiling recording tests
- Plus additional conftest.py and __init__.py files

---

## tests/unit/core/ Subdirectory Analysis Notes

The core test directory has a significant duplication problem where "edge cases" files duplicate the primary test files. The pattern is:
- `test_X.py` (primary tests)
- `test_X_edge_cases.py` (duplicates most of test_X.py, adds a few edge cases)

The logger subdirectory also duplicates `test_logger.py`:
- `logger/test_events.py` duplicates TestEventHandler
- `logger/test_singleton.py` duplicates TestLoggerSingleton + TestModuleLevelFunctions
- `logger/test_warning.py` duplicates warning tests
- `logger/test_levels.py` duplicates enabled flag tests

**Recommendation:** Merge unique edge case tests into the primary files, then delete the edge case and subdirectory duplicate files.

---

## tests/unit/entities/ Analysis

### HIGH Confidence Removal Candidates

#### test_ship_formation_edge_cases.py
- **Location:** `tests/unit/entities/test_ship_formation_edge_cases.py`
- **Category:** Trivial / Scaffold
- **Reason:** Contains only 2 trivial import-existence checks (~22 lines total). Tests that `ShipFormation` can be imported and that `FormationPosition` can be imported. The real, comprehensive formation tests are in `test_ship_formation.py` (which tests actual formation logic, positions, assignments, edge cases). These import checks add zero value since any test in the primary file would fail if imports were broken.
- **Lines:** ~22 lines, all trivial

#### test_projectile_edge_cases.py
- **Location:** `tests/unit/entities/test_projectile_edge_cases.py`
- **Category:** Trivial / Scaffold
- **Reason:** Contains only 2 trivial import-existence checks (~22 lines total). Tests that `Projectile` class can be imported and that `ProjectileState` enum can be imported. These are pure scaffold tests that verify nothing beyond module importability. Any real test of projectile behavior would catch import failures.
- **Lines:** ~22 lines, all trivial

### MEDIUM Confidence Removal Candidates

#### test_ability_aggregator_scope.py
- **Location:** `tests/unit/entities/test_ability_aggregator_scope.py`
- **Category:** Trivial / Scaffold
- **Reason:** Contains only 5 trivial import-existence checks (~37 lines total). Tests that `ability_aggregator` module exists, that `AbilityLayer` enum exists, that `AbilityScope` enum exists, that `calculate_ability_totals` function exists, and that `get_ability_total` function exists. The comprehensive layer-scope tests are already in `test_ability_aggregator_layers.py` (which tests actual COMBAT/STRATEGIC/BOTH filtering, scope filtering, aggregation, stack groups -- 285 lines of real tests). These import checks provide no value beyond what the comprehensive file already validates.
- **Lines:** ~37 lines, all trivial

### Entities Files Analyzed and Kept (No Issues Found)

The following 43 files were analyzed and found to be legitimate, non-duplicate, and worth keeping:
- `conftest.py` - Fixtures for entities tests
- `test_abilities.py` - Ability creation and basic behavior
- `test_abilities_advanced.py` - Advanced ability features
- `test_ability_interface.py` - get_primary_value() polymorphic interface
- `test_ability_aggregator_layers.py` - Layer-aware ability aggregation (comprehensive)
- `test_bridge_requirement_removal.py` - Bridge validation removal
- `test_bridge_scaling.py` - Bridge scaling with ship class mass
- `test_component_cache.py` - ComponentCacheManager thread safety
- `test_component_composition.py` - Component ability composition (engine, weapon, UI rows)
- `test_component_di.py` - Component DI (fresh_registries)
- `test_component_formulas.py` - Formula-based mass/HP calculation
- `test_component_modifiers_extended.py` - Modifier stacking integration
- `test_component_resources.py` - Component resource abilities
- `test_components.py` - Component loading, modifier stacking, turret mount, modifier data methods
- `test_crystalline_armor.py` - Crystalline armor damage absorption, regen, stacking
- `test_emissive_armor.py` - Emissive armor damage reduction
- `test_hull_layer.py` - Hull layer initialization, auto-equip, serialization, class change
- `test_layer_data.py` - LayerData dataclass construction, factories, clear, isolation
- `test_mandatory_modifiers.py` - ModifierEditorPanel auto-apply, constraints
- `test_mandatory_updates.py` - ModifierLogic mandatory modifier determination
- `test_modifier_defaults_robustness.py` - Modifier defaults robustness
- `test_modifier_propagation.py` - Group modifier propagation
- `test_modifier_row.py` - ModifierControlRow UI elements, events, callbacks
- `test_modifiers.py` - Modifier add/remove/restrictions/effects/persistence, component cloning
- `test_planetary_complex.py` - Planetary Complex component acceptance/rejection
- `test_resource_manager.py` - ResourceState, ResourceRegistry, consumption abilities
- `test_scaling_logic.py` - Consumption and crew scaling with modifiers
- `test_ship.py` - Ship construction, constraints, mass, damage, serialization, class mutation, defense score
- `test_ship_caching.py` - Ship summary cache, component cache invalidation, weapon cache, HP ratio cache
- `test_ship_classes.py` - Vehicle class existence, mass limits, theme image loading
- `test_ship_di.py` - Ship DI patterns
- `test_ship_formation.py` - ShipFormation comprehensive tests
- `test_ship_physics_mixin.py` - Ship physics calculations
- `test_ship_resources.py` - Resource initialization, capacity, crew, life support
- `test_ship_serialization.py` - Ship serialization round-trip (basic, components, modifiers, resources, stats, hull)
- `test_ship_serialization_di.py` - ShipSerializer DI
- `test_ship_stat_querier.py` - ShipStatQuerier comprehensive tests (~843 lines)
- `test_ship_stats.py` - Ship stats baseline
- `test_ship_theme_logic.py` - ShipThemeManager
- `test_ship_validator_helper.py` - ShipValidatorHelper
- `test_stacking_integration.py` - Sensor/ECM stacking integration on ship
- `test_stacking_rules.py` - Stack group rules (MAX within, MULTIPLY across)
- `ship_helpers/test_component_getters.py` - get_all_components, iter_components, get_by_ability, get_by_layer
- `ship_helpers/test_component_operations.py` - has_components, find_component_with_index, clear_non_hull_components

---

## tests/unit/data/ Analysis

### No Removal Candidates

Both files in this directory are legitimate and worth keeping:

#### test_data_validation.py (KEEP)
- **Location:** `tests/unit/data/test_data_validation.py`
- **Lines:** ~293
- **Reason:** Tests data file integrity (formation naming conventions, vehicle class spelling, builder theme types, placeholder file detection, resource metadata consistency, modifier file validation). These are valuable data integrity guards that catch issues in JSON data files before runtime.

#### test_test_infrastructure.py (KEEP)
- **Location:** `tests/unit/data/test_test_infrastructure.py`
- **Lines:** ~248
- **Reason:** Tests for duplicate script removal and utility script naming conventions. Validates test infrastructure consistency. These meta-tests help maintain test suite hygiene.

---

## Cross-Directory Patterns and Recommendations

### Pattern 1: "Edge Cases" File Duplication
The most common problem across these directories is the `test_X_edge_cases.py` pattern where a secondary file duplicates 60-80% of the primary `test_X.py` file and adds a few unique tests. This pattern appears in:
- `test_json_utils_edge_cases.py` (80% duplicate of `test_json_utils.py`)
- `test_validation_edge_cases.py` (75% duplicate of `test_validation.py`)
- `test_config_edge_cases.py` (25% duplicate of `test_config.py`)
- `test_ship_formation_edge_cases.py` (100% trivial, real tests in `test_ship_formation.py`)
- `test_projectile_edge_cases.py` (100% trivial, no real primary file tests in entities)

**Recommendation:** Merge unique edge case tests into the primary files, then delete the edge case files entirely.

### Pattern 2: Logger Subdirectory Duplication
The `tests/unit/core/logger/` subdirectory contains 4 files that substantially duplicate the monolithic `test_logger.py` file:
- `logger/test_events.py` - duplicates TestEventHandler
- `logger/test_singleton.py` - duplicates TestLoggerSingleton + TestModuleLevelFunctions
- `logger/test_warning.py` - duplicates warning tests
- `logger/test_levels.py` - duplicates enabled flag tests

**Recommendation:** Merge any unique tests from the subdirectory files into `test_logger.py`, then delete the entire `logger/` subdirectory.

### Pattern 3: Trivial Import-Only Tests
Three files contain only trivial import-existence checks:
- `test_ship_formation_edge_cases.py` (2 import checks)
- `test_projectile_edge_cases.py` (2 import checks)
- `test_ability_aggregator_scope.py` (5 import checks)

**Recommendation:** Delete these files. Import failures would be caught by any real test in the corresponding primary test files.

### Pattern 4: Same-File Class Duplication
`test_resource_loading.py` has a `TestLoadResourcesData` class defined twice within the same file (lines 60 and 144). Python silently overwrites the first class with the second, meaning some tests are never executed.

**Recommendation:** Consolidate into `test_resources.py` and delete `test_resource_loading.py`.

---

## Totals by Action

| Action | Files | Estimated Lines |
|--------|-------|-----------------|
| DELETE entirely | 7 | ~696 |
| MERGE unique tests then DELETE | 5 | ~610 (merge ~100, delete ~510) |
| REDUCE (trim excess tests) | 2 | ~280 (reduce by ~150) |
| **Total removable** | **14** | **~1,300** |

### Files to DELETE entirely (no unique content):
1. `tests/unit/core/test_error_codes_coverage.py` (~150 lines)
2. `tests/unit/core/logger/test_warning.py` (~56 lines)
3. `tests/unit/core/test_resource_loading.py` (~185 lines)
4. `tests/unit/entities/test_ship_formation_edge_cases.py` (~22 lines)
5. `tests/unit/entities/test_projectile_edge_cases.py` (~22 lines)
6. `tests/unit/entities/test_ability_aggregator_scope.py` (~37 lines)
7. `tests/unit/core/test_constants.py` (~40 lines)

### Files to MERGE unique tests into primary, then DELETE:
1. `tests/unit/core/test_json_utils_edge_cases.py` -> merge ~27 unique lines into `test_json_utils.py`
2. `tests/unit/core/test_validation_edge_cases.py` -> merge ~45 unique lines into `test_validation.py`
3. `tests/unit/core/test_config_edge_cases.py` -> merge ~79 unique lines into `test_config.py`
4. `tests/unit/core/logger/test_events.py` -> merge ~44 unique lines into `test_logger.py`
5. `tests/unit/core/logger/test_singleton.py` -> merge ~75 unique lines into `test_logger.py`

### Files to REDUCE (trim excess, keep file):
1. `tests/unit/core/test_singleton.py` - reduce from ~313 to ~150 lines
2. `tests/unit/core/logger/test_levels.py` - reduce from ~119 to ~79 lines (remove duplicated enabled flag tests)
