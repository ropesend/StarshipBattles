# Validation Review 2: Simulation + Core/Entities/Data Findings

## Summary
- Findings reviewed: 26 items (12 from Agent 3 Simulation, 14 from Agent 4 Core/Entities/Data)
- CONFIRMED for removal: 12
- DISPUTED (should keep): 9
- MODIFIED (partial removal only): 5

---

## Detailed Validation: Agent 3 (Simulation Tests)

### SIM-HIGH-1: Old Component Test Framework (Scaffold Group)
- **Original claim:** `run_component_tests.py` (506 lines), `update_test_ships.py` (58 lines), `output/logs/` (7 .log files), `test_configs/` (12 .json files) are a superseded framework not discovered by pytest.
- **Verdict:** CONFIRMED
- **Evidence:** I read `run_component_tests.py` fully. It's a standalone script using `pygame.init()`, custom `TestGrid`, `TestConfig.from_file()`, and `TestLogParser` -- entirely outside pytest. It imports `from component_logger import ...` and `from log_parser import ...` (local imports). A grep for all references to these modules shows they are ONLY referenced within this self-contained group of files and the `tests/unit/simulation/__init__.py` (which exports them but nothing else in the codebase imports from that `__init__`). The 7 log files are generated output. The 12 JSON configs are only consumed by `run_component_tests.py`.
- **Unique tests that would be lost:** None. This is not a pytest test suite -- it's a standalone runner that is never executed by `pytest`.
- **Risk of removal:** None
- **Note:** The `__init__.py` in `tests/unit/simulation/` exports `ComponentTestLogger`, `TestEventType`, `enable_test_logging`, `TestLogParser`, `LogEvent` -- these exports should be cleaned up when removing the framework.

### SIM-HIGH-2: Trivially Obvious Test File (`test_ship_stats_phase_ordering.py`)
- **Original claim:** 22 lines, only 2 tests: import check and `hasattr` check. Real tests in `test_ship_stats_calculator_phases.py`.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file. Exactly 2 tests:
  1. `test_ship_stats_calculator_exists` -- `assert ShipStatsCalculator is not None`
  2. `test_calculator_has_calculate_method` -- `assert hasattr(ShipStatsCalculator, 'calculate')`
  The companion file `test_ship_stats_calculator_phases.py` (375 lines) imports and exercises `ShipStatsCalculator` extensively with mock ships, real component objects, and phase extraction tests. Any import failure would be caught immediately by those tests.
- **Unique tests that would be lost:** None. Import/hasattr checks are implicit in any real test.
- **Risk of removal:** None

### SIM-MEDIUM-3: Old Framework Utilities (`component_logger.py`, `component_sim_tools.py`, `log_parser.py`)
- **Original claim:** 797 lines of utilities only used by `run_component_tests.py`.
- **Verdict:** CONFIRMED
- **Evidence:** Grep confirms these are only referenced by each other, `run_component_tests.py`, and the `__init__.py`. `component_logger.py` has `TEST_LOGGING_ENABLED = False` by default. `component_sim_tools.py` creates test ship JSON files for the old framework. `log_parser.py` parses log output from the old framework. All three are dead code if the scaffold group is removed.
- **Unique tests that would be lost:** N/A -- these are utilities, not tests.
- **Risk of removal:** None (remove with scaffold group)

### SIM-MEDIUM-4: Inline Math Formula Tests (`test_physics_formulas.py`)
- **Original claim:** 731 lines testing inline math rather than actual game code paths.
- **Verdict:** DISPUTED (should keep, at least partially)
- **Evidence:** The tests import `K_SPEED`, `K_THRUST`, `K_TURN` from `game.simulation.physics_constants` but then **re-implement formulas inline** (e.g., `max_speed = (thrust * K_SPEED) / mass`) rather than calling actual game functions. The tests verify boundary conditions (zero mass, overflow, NaN, subnormal values) on these inline expressions.
- **Argument for keeping:** These tests serve as **specification tests** -- they document what the formulas SHOULD be. If someone changes the constants, these tests catch it. The boundary condition tests (zero-division guards, NaN propagation, infinity handling) document expected edge-case behavior that would be hard to reconstruct. Even though they don't call game functions directly, they pin the mathematical specifications.
- **Argument for removal:** If the actual game code diverges from these inline formulas, these tests won't catch it (false sense of security).
- **Unique tests that would be lost:** ~40 boundary condition tests for physics formulas (zero mass, negative mass, extreme values, NaN, infinity).
- **Risk of removal:** Medium -- loss of formula specification documentation and boundary condition coverage.
- **Recommendation:** KEEP. These are cheap to maintain (no mocks, no dependencies) and document important math invariants.

### SIM-MEDIUM-5: ShipCombatEngine vs Combat Duplication
- **Original claim:** `ship_combat_engine/test_creation_and_lead.py` (100 lines, 5 tests) and `test_targeting.py` (152 lines, 6 tests) duplicate `combat/test_targeting_system.py` (913 lines, 34 tests).
- **Verdict:** CONFIRMED
- **Evidence:** `ShipCombatEngine` is a **pure delegation layer**:
  ```python
  def solve_lead(self, pos, vel, t_pos, t_vel, p_speed):
      return self._targeting_system.solve_lead(pos, vel, t_pos, t_vel, p_speed)
  def select_target(self, candidates):
      return self._targeting_system.select_target(self._ship, candidates)
  def calculate_firing_solution(self, comp, target):
      return self._targeting_system.calculate_firing_solution(self._ship, comp, target)
  ```
  The 11 tests in the two ship_combat_engine files test `solve_lead`, `select_target`, and `calculate_firing_solution` via the wrapper -- all of which are direct pass-throughs to `TargetingSystem`, which has 34 comprehensive tests.
- **Unique tests that would be lost:** `test_combat_engine_can_be_created` and `test_combat_engine_stores_ship_reference` are engine construction tests, but these are trivially obvious (constructor stores a reference).
- **Risk of removal:** Low

### SIM-LOW-6: `test_battle_config.py` (147 lines)
- **Original claim:** Tests enum string values and dataclass defaults. Partially duplicated by `battle_controller/test_config.py`.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** I read both files. `test_battle_config.py` has 20 test methods across 5 classes:
  - `TestBattleModeEnum` (5 tests: individual mode values + uniqueness check)
  - `TestBattleConfigDefaults` (11 tests: mode, max_ticks, headless, logging, retreat, reinforcements, end_mode, seed, start_paused, test_scenario, source_fleets)
  - `TestBattleConfigHypotheticalMode` (1 test: isolated flag)
  - `TestBattleConfigCustomValues` (4 tests: custom seed, max_ticks, mode, headless)
  - `TestBattleConfigMapBounds` (2 tests: default bounds, custom bounds)

  `battle_controller/test_config.py` has `test_config_defaults` which tests ~9 defaults in a single test, and `test_config_custom_values`. But `test_battle_config.py` tests MORE fields (test_scenario, source_fleets, isolated, map_bounds) that `battle_controller/test_config.py` does NOT cover.

  While testing enum values like `assert BattleMode.MANUAL.value == "manual"` seems trivial, these are **contract tests**. If someone renames an enum value, serialization/deserialization of battle configs would break. The map_bounds tests and hypothetical mode tests are entirely unique.
- **Unique tests that would be lost:** map_bounds tests, hypothetical mode tests, test_scenario/source_fleets defaults, individual enum value assertions (serialization contract).
- **Risk of removal:** Medium -- would lose serialization contract coverage for enum values and config field defaults not tested elsewhere.

### SIM-LOW-7: `test_physics_constants.py` (109 lines)
- **Original claim:** Partially trivial. `isinstance(K_SPEED, int)` and `K_SPEED > 0` are trivially obvious. Formula verification tests have some value.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** I read the file. It has 5 classes with 11 tests:
  - `TestPhysicsConstants` (3 tests): Type and positivity checks for K_SPEED, K_THRUST, K_TURN
  - `TestSpeedFormula` (2 tests): Known-value formula verification, inverse-mass scaling
  - `TestAccelerationFormula` (1 test): Known-value verification
  - `TestTurnFormula` (2 tests): Known-value verification, heavier-ships-turn-slower
  - `TestFormulaDocumentation` (3 tests): Formula doc strings contain expected terms

  The "trivially obvious" type checks (`isinstance(K_SPEED, int)`) actually serve a purpose: if someone changes a constant from `int` to `float`, the physics calculations could behave differently (integer vs float division). The formula verification tests pin specific mathematical relationships. The documentation tests ensure formula strings stay accurate.
- **Unique tests that would be lost:** Formula documentation existence tests, type enforcement on constants, known-value formula calculations.
- **Risk of removal:** Low-Medium -- cheap to maintain, documents formula contracts.

### SIM-LOW-8: `test_layer_restriction_rule_refactor.py` (204 lines)
- **Original claim:** Stale filename, should be renamed or merged with `validation/test_ship_validator_rules.py`.
- **Verdict:** MODIFIED (heavy duplication, but 1 unique test)
- **Evidence:** I read both files and compared test methods:

  | test_layer_restriction_rule_refactor.py | validation/test_ship_validator_rules.py |
  |---|---|
  | test_check_block_rules_exists | (not present -- trivial) |
  | test_check_allow_rules_exists | (not present -- trivial) |
  | test_block_classification_rule_blocks_matching | test_block_classification_blocks_matching |
  | test_block_classification_rule_allows_non_matching | (not present -- but implicitly covered) |
  | test_block_id_rule_blocks_matching | test_block_id_blocks_matching |
  | test_deny_ability_rule_blocks_component | test_deny_ability_blocks_matching |
  | test_allow_classification_accepts_matching | test_allow_classification_passes_matching |
  | test_allow_classification_rejects_non_matching | test_allow_classification_blocks_non_matching |
  | test_allow_id_accepts_matching | test_allow_id_passes_matching |
  | test_allow_ability_accepts_component | test_allow_ability_passes_matching |
  | test_hull_only_accepts_hull_components | test_hull_only_allows_hull_components |
  | test_hull_only_rejects_non_hull_components | test_hull_only_blocks_non_hull_components |
  | test_no_restrictions_allows_all | test_no_restrictions_allows_all |
  | **test_combined_block_and_allow_rules** | **(not present)** |

  11 of 14 functional tests are duplicated. ONE test is unique: `test_combined_block_and_allow_rules` (block-over-allow precedence). The validation file also has a unique test `test_skips_if_layer_doesnt_exist`.
- **Unique tests that would be lost:** `test_combined_block_and_allow_rules` (block-over-allow precedence test).
- **Risk of removal:** Low -- but the precedence test should be migrated first.
- **Recommendation:** Migrate `test_combined_block_and_allow_rules` to `test_ship_validator_rules.py`, then delete this file.

---

## Detailed Validation: Agent 4 (Core/Entities/Data)

### CORE-HIGH-1: `test_error_codes_coverage.py` (~150 lines)
- **Original claim:** Almost entirely duplicates `test_error_codes.py`.
- **Verdict:** CONFIRMED
- **Evidence:** The coverage file has 8 test methods. `test_error_codes.py` has 23 methods covering everything the coverage file tests PLUS access patterns, category existence, minimum required codes, and name uniqueness. Zero unique methods in the coverage file.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

### CORE-HIGH-2: `test_json_utils_edge_cases.py` (~127 lines)
- **Original claim:** 80% overlap, 2 unique tests.
- **Verdict:** MODIFIED (has 4 unique tests, not 2)
- **Evidence:** The edge cases file has 12 tests, of which 8 overlap with `test_json_utils.py`. **4 unique tests** exist:
  1. `test_load_json_io_error_returns_default` -- IOError simulation via mock
  2. `test_load_json_custom_default` -- various default types (42, "custom", None)
  3. `test_save_json_io_error_returns_false` -- IOError on write
  4. `test_save_json_type_error_returns_false` -- non-serializable object handling
- **Unique tests that would be lost:** 4 error-path tests (IOError on read, IOError on write, TypeError on write, custom default types).
- **Risk of removal:** Medium -- error path tests catch real bugs in IO operations.
- **Recommendation:** Merge the 4 unique tests into `test_json_utils.py`, then delete.

### CORE-HIGH-3: `test_validation_edge_cases.py` (~165 lines)
- **Original claim:** 75% overlap, a few unique tests.
- **Verdict:** MODIFIED (has ~7 unique tests)
- **Evidence:** The edge cases file has 16 tests. ~9 overlap with `test_validation.py`. **7 unique tests**:
  1. `test_init_with_none_errors_defaults_to_list` -- None errors edge case
  2. `test_init_with_none_warnings_defaults_to_list` -- None warnings edge case
  3. `test_add_error_with_error_code_enum` -- ErrorCode enum conversion
  4. `test_add_error_with_string_code` -- string code handling
  5. `test_add_error_no_code_leaves_none` -- None code behavior
  6. `test_create_with_errors_list` -- creation with pre-existing errors
  7. `test_create_empty_message_in_errors` -- empty string in errors list
- **Unique tests that would be lost:** 7 edge case tests for ValidationResult initialization and error code handling.
- **Risk of removal:** Medium -- None-handling and ErrorCode enum tests catch real edge cases.
- **Recommendation:** Merge the 7 unique tests into `test_validation.py`, then delete.

### CORE-HIGH-4: `test_config_edge_cases.py` (~104 lines)
- **Original claim:** 25% duplicate, unique boundary tests.
- **Verdict:** DISPUTED (should keep as-is or merge ALL into primary)
- **Evidence:** Only ~3 of 17 tests overlap with `test_config.py`. The edge cases file has **14 unique boundary/constraint tests**:
  - `test_windowed_resolution_tuple` (windowed resolution values)
  - `test_resolution_values_positive` (all resolutions > 0)
  - `test_min_spacing_positive`, `test_flee_distance_greater_than_orbit`, `test_formation_throttle_0_to_1`, `test_formation_slowdown_throttle_valid`, `test_default_orbit_distance_positive`, `test_max_correction_force_positive`, `test_erratic_turn_interval_range` (AIConfig boundary validation)
  - `test_tick_rate_reasonable`, `test_spatial_grid_cell_size_positive`, `test_default_drag_values_positive`, `test_default_base_radius_positive`, `test_reference_mass_positive` (PhysicsConfig constraints)

  These tests enforce **mathematical invariants** (flee > orbit, throttle in (0,1], tick rate < 1.0) that would catch dangerous config changes.
- **Unique tests that would be lost:** 14 constraint/boundary tests for AIConfig and PhysicsConfig.
- **Risk of removal:** High -- would lose relationship constraint validation (e.g., flee distance must exceed orbit distance).
- **Recommendation:** KEEP. If consolidating, merge ALL edge case tests into `test_config.py` (don't discard any).

### CORE-HIGH-5: `logger/test_events.py` (~104 lines)
- **Original claim:** Duplicates TestEventHandler class in `test_logger.py`.
- **Verdict:** MODIFIED (has 5 unique tests)
- **Evidence:** File has 8 tests, 3 overlap with `test_logger.py`. **5 unique tests**:
  1. `test_set_event_handler_exists` -- function existence (trivial)
  2. `test_log_event_exists` -- function existence (trivial)
  3. `test_set_event_handler_replaces_previous` -- handler replacement behavior
  4. `test_log_event_with_no_kwargs` -- no-kwargs edge case
  5. `test_log_event_with_many_kwargs` -- kwargs pass-through with multiple args
- **Unique tests that would be lost:** Handler replacement behavior, no-kwargs and many-kwargs edge cases.
- **Risk of removal:** Medium -- handler replacement and kwargs pass-through are real behaviors.
- **Recommendation:** Merge 3 unique functional tests (not the existence checks) into `test_logger.py`, then delete.

### CORE-HIGH-6: `logger/test_singleton.py` (~175 lines)
- **Original claim:** Duplicates TestLoggerSingleton + TestModuleLevelFunctions.
- **Verdict:** MODIFIED (has 6 unique tests)
- **Evidence:** File has 14 tests, 7 overlap. **6+ unique tests**:
  1. `test_double_checked_locking` -- threading/concurrency test
  2. `test_log_with_none_message` -- None message handling
  3. `test_log_with_empty_string` -- empty string handling
  4. `test_log_with_complex_objects` -- complex object logging
  5. `test_log_unicode_characters` -- Unicode support
  6. `test_log_very_long_message` -- long message handling
- **Unique tests that would be lost:** Concurrency test, edge case message types (None, empty, complex, Unicode, long).
- **Risk of removal:** High -- concurrency test is critical; message type edge cases are important.
- **Recommendation:** Merge all unique tests into `test_logger.py`, then delete.

### CORE-HIGH-7: `logger/test_warning.py` (~56 lines)
- **Original claim:** All 56 lines duplicated.
- **Verdict:** CONFIRMED (with minor caveat)
- **Evidence:** File has 6 tests. 2 are clear duplicates. 2 are existence checks (trivial). The remaining 2 (`test_log_warning_runs_when_enabled`, `test_log_warning_suppressed_when_disabled`) are partially covered by `test_logger.py`'s enabled flag tests which test the same code path via `log_debug`/`log_info`. The coverage gap is minimal since all log methods share the same enabled-flag path.
- **Unique tests that would be lost:** Marginally -- focused `log_warning` enabled/disabled tests, but same code path as other log method tests.
- **Risk of removal:** Low

### CORE-HIGH-8: `logger/test_levels.py` (~119 lines)
- **Original claim:** ~40 lines are duplicates of enabled flag tests.
- **Verdict:** DISPUTED (mostly unique, should keep)
- **Evidence:** File has 11 tests across 3 classes. Only 1 test (`test_all_log_methods_check_enabled`) clearly duplicates `test_logger.py`. **10 tests are unique**:
  - Default log level configuration
  - Debug-level message handling
  - Logger setup method and FileHandler creation
  - Formatter setup and configuration
  - Logger name validation ("starship_battles")
  - Enabled flag initialization
  - Formatter content validation (timestamp, level, message)
- **Unique tests that would be lost:** 10 tests covering logger setup, configuration, formatting, and initialization -- none of which exist in `test_logger.py`.
- **Risk of removal:** High -- would lose ALL logger setup/configuration/formatter tests.
- **Recommendation:** KEEP. The claim of "~40 lines of duplicates" severely understates the unique content. This file tests a completely different concern (setup/configuration) vs `test_logger.py` (runtime behavior).

### CORE-MEDIUM-9: `test_constants.py` (~40 lines)
- **Original claim:** Trivially obvious -- just checks PLANET_RESOURCES is a list of 5 strings.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** 5 tests checking: importability, is_list, exact values, count, element types. While individually trivial, together they form a **contract test** for a constant that is likely consumed by UI rendering and data layers. If someone changes `PLANET_RESOURCES` to a tuple, adds an element, or changes a string, these tests catch it immediately. At 40 lines, the maintenance cost is near-zero.
- **Unique tests that would be lost:** The only tests of the PLANET_RESOURCES constant.
- **Risk of removal:** Low-Medium -- cheap insurance against silent refactoring breaks.

### CORE-MEDIUM-10: `test_superweapon_input_actions.py` (~93 lines)
- **Original claim:** Redundant -- `test_input_actions.py` already has exhaustive coverage via `test_covers_all_actions`.
- **Verdict:** CONFIRMED
- **Evidence:** `test_input_actions.py` has `test_covers_all_actions` which iterates ALL `InputAction` enum members and verifies each has a display name AND a group membership. It also tests uniqueness and dot-notation format for ALL actions. The superweapon file spot-checks 6 specific enum values which are already guaranteed by the exhaustive iteration tests.
- **Unique tests that would be lost:** None that aren't covered by exhaustive iteration.
- **Risk of removal:** None

### CORE-MEDIUM-11: `test_resource_loading.py` (~185 lines)
- **Original claim:** Has duplicate class name within file AND overlaps with `test_resources.py`.
- **Verdict:** CONFIRMED
- **Evidence:** The file has `TestLoadResourcesData` defined TWICE (Python silently overwrites the first with the second, meaning some tests never execute). `test_resources.py` (310 lines) is strictly more comprehensive, covering all scenarios from `test_resource_loading.py` plus additional edge cases (None IDs, empty strings, duplicate IDs, mutation isolation via `test_returns_new_dict_each_time`).
- **Unique tests that would be lost:** None -- `test_resources.py` is a superset.
- **Risk of removal:** None

### CORE-MEDIUM-12: `test_profiling_edge_cases.py` (~361 lines)
- **Original claim:** Moderate overlap with profiling subdirectory.
- **Verdict:** DISPUTED (should keep)
- **Evidence:** While there's 10-15% overlap, `test_profiling_edge_cases.py` has significant unique content:
  - `test_save_history_io_error` -- error logging on save_json failure
  - `test_save_history_appends_to_existing` -- session merging behavior
  - `test_profile_action_preserves_function_name` -- decorator metadata preservation
  - `test_nested_profile_blocks` -- nested context manager behavior
  - `test_profile_block_mixed_with_decorator` -- interaction between decorator and context manager
  - Decorator-with-args/kwargs tests not in `profiling/test_decorators.py`
- **Unique tests that would be lost:** Error paths, session merging, function name preservation, nesting/interaction tests.
- **Risk of removal:** Medium-High -- these test important interaction patterns and error conditions.

### CORE-LOW-13: `test_singleton.py` (~313 lines)
- **Original claim:** 313 lines is overkill for a simple metaclass, could reduce by 50%.
- **Verdict:** DISPUTED (should keep as-is)
- **Evidence:** The thread safety tests (`test_concurrent_instance_calls_return_same_object` with 20 workers/50 calls, `test_concurrent_reset_and_instance_dont_crash` with 80 instance + 20 reset from 20 threads) are **non-negotiable**. `SingletonMeta` uses a `__lock` for thread safety -- if the lock is ever removed or broken, only these stress tests would catch it. The other tests (basic behavior, independence, subclass features, direct construction, edge cases) are standard metaclass validation at ~15 lines each.
- **Unique tests that would be lost:** N/A -- all tests are for a unique class.
- **Risk of removal:** High -- thread safety regressions in singletons cause subtle, hard-to-diagnose production bugs.

### CORE-LOW-14: `test_isolation.py` (~119 lines)
- **Original claim:** Tests require sequential execution, may not work with xdist.
- **Verdict:** DISPUTED (should keep, but note design issue)
- **Evidence:** The file has 6 tests across 3 classes (TestRegistryIsolation, TestStrategyManagerIsolation, TestComponentCacheIsolation), each with part1 (pollute) and part2 (verify clean). These are the **only tests** verifying that the `reset_game_state` fixture properly isolates test state. The claim about xdist is valid -- these tests may fail with parallel execution -- but they work correctly in sequential mode and serve as a critical regression test for the fixture.
- **Unique tests that would be lost:** The only tests of cross-test isolation via `reset_game_state`.
- **Risk of removal:** Medium -- if the isolation fixture breaks, no other test catches it directly.
- **Recommendation:** KEEP. Flag as requiring sequential execution (`pytest tests/unit/core/test_isolation.py -v`). Consider refactoring to be xdist-safe in a future pass.

### ENT-HIGH-15: `test_ship_formation_edge_cases.py` (~22 lines)
- **Original claim:** Only 2 trivial import-existence checks.
- **Verdict:** CONFIRMED
- **Evidence:** Exactly 2 tests: `test_ship_formation_module_exists()` and `test_ship_formation_class_exists()`. Pure import checks. `test_ship_formation.py` has 14 substantive tests.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

### ENT-HIGH-16: `test_projectile_edge_cases.py` (~22 lines)
- **Original claim:** Only 2 trivial import-existence checks.
- **Verdict:** CONFIRMED
- **Evidence:** Exactly 2 tests: `test_projectile_module_exists()` and `test_projectile_manager_exists()`. Pure import checks.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

### ENT-MEDIUM-17: `test_ability_aggregator_scope.py` (~37 lines)
- **Original claim:** Only 5 trivial import-existence checks.
- **Verdict:** CONFIRMED
- **Evidence:** 5 tests all checking `exists()` -- module, enum, enum, function, function. `test_ability_aggregator_layers.py` has 13 substantive tests covering actual filtering, aggregation, and stack group logic.
- **Unique tests that would be lost:** None.
- **Risk of removal:** None

---

## Final Tally

| ID | File | Original Confidence | Verdict | Action |
|----|------|--------------------:|---------|--------|
| SIM-HIGH-1 | Old framework scaffold (5 files + 19 data files) | HIGH | **CONFIRMED** | DELETE all |
| SIM-HIGH-2 | test_ship_stats_phase_ordering.py | HIGH | **CONFIRMED** | DELETE |
| SIM-MEDIUM-3 | Framework utilities (3 files) | MEDIUM | **CONFIRMED** | DELETE with scaffold |
| SIM-MEDIUM-4 | test_physics_formulas.py | MEDIUM | **DISPUTED** | KEEP -- formula specification tests |
| SIM-MEDIUM-5 | ship_combat_engine/{test_creation_and_lead,test_targeting}.py | MEDIUM | **CONFIRMED** | DELETE |
| SIM-LOW-6 | test_battle_config.py | LOW | **DISPUTED** | KEEP -- unique config field coverage |
| SIM-LOW-7 | test_physics_constants.py | LOW | **DISPUTED** | KEEP -- formula contracts + type enforcement |
| SIM-LOW-8 | test_layer_restriction_rule_refactor.py | LOW | **MODIFIED** | Migrate 1 unique test, then DELETE |
| CORE-HIGH-1 | test_error_codes_coverage.py | HIGH | **CONFIRMED** | DELETE |
| CORE-HIGH-2 | test_json_utils_edge_cases.py | HIGH | **MODIFIED** | Merge 4 unique tests, then DELETE |
| CORE-HIGH-3 | test_validation_edge_cases.py | HIGH | **MODIFIED** | Merge 7 unique tests, then DELETE |
| CORE-HIGH-4 | test_config_edge_cases.py | HIGH | **DISPUTED** | KEEP -- 14 unique constraint tests |
| CORE-HIGH-5 | logger/test_events.py | HIGH | **MODIFIED** | Merge 3 unique tests, then DELETE |
| CORE-HIGH-6 | logger/test_singleton.py | HIGH | **MODIFIED** | Merge 6 unique tests, then DELETE |
| CORE-HIGH-7 | logger/test_warning.py | HIGH | **CONFIRMED** | DELETE |
| CORE-HIGH-8 | logger/test_levels.py | HIGH | **DISPUTED** | KEEP -- 10 unique setup/config tests |
| CORE-MEDIUM-9 | test_constants.py | MEDIUM | **DISPUTED** | KEEP -- contract test for constant |
| CORE-MEDIUM-10 | test_superweapon_input_actions.py | MEDIUM | **CONFIRMED** | DELETE |
| CORE-MEDIUM-11 | test_resource_loading.py | MEDIUM | **CONFIRMED** | DELETE |
| CORE-MEDIUM-12 | test_profiling_edge_cases.py | MEDIUM | **DISPUTED** | KEEP -- unique error/interaction tests |
| CORE-LOW-13 | test_singleton.py | LOW | **DISPUTED** | KEEP -- thread safety tests critical |
| CORE-LOW-14 | test_isolation.py | LOW | **DISPUTED** | KEEP -- only isolation fixture tests |
| ENT-HIGH-15 | test_ship_formation_edge_cases.py | HIGH | **CONFIRMED** | DELETE |
| ENT-HIGH-16 | test_projectile_edge_cases.py | HIGH | **CONFIRMED** | DELETE |
| ENT-MEDIUM-17 | test_ability_aggregator_scope.py | MEDIUM | **CONFIRMED** | DELETE |

---

## Summary Statistics

### By Verdict
- **CONFIRMED for removal:** 12 items (safe to delete outright or after merging unique tests)
- **DISPUTED (should keep):** 9 items (original reviewer's assessment was wrong or overstated)
- **MODIFIED (partial removal):** 5 items (merge unique tests to primary file, then delete)

### By Risk Level of Proposed Removal
- **No risk:** SIM-HIGH-1, SIM-HIGH-2, SIM-MEDIUM-3, SIM-MEDIUM-5, CORE-HIGH-1, CORE-MEDIUM-10, CORE-MEDIUM-11, ENT-HIGH-15, ENT-HIGH-16, ENT-MEDIUM-17
- **Low risk:** SIM-LOW-8, CORE-HIGH-7
- **Medium risk:** CORE-HIGH-2, CORE-HIGH-3, CORE-HIGH-5, CORE-HIGH-6, CORE-MEDIUM-9, CORE-LOW-14
- **High risk:** SIM-MEDIUM-4, CORE-HIGH-4, CORE-HIGH-8, CORE-MEDIUM-12, CORE-LOW-13

### Lines Actually Safe to Remove (adjusted estimate)
- **Outright deletion (no merge needed):** ~1,850 lines of code + 19 data files
- **Delete after merge:** ~580 lines (after migrating ~20 unique tests to primary files)
- **Should NOT remove (disputed):** ~2,050 lines the original review recommended removing
- **Net safe removal: ~2,430 lines + 19 data files** (vs original estimate of ~3,960 lines)

### Key Corrections to Original Reviews

1. **Agent 3 overestimated `test_physics_formulas.py` removal** -- these are formula specification tests, not dead code.
2. **Agent 4 systematically underestimated unique content** in "edge cases" files -- most had 4-14 unique tests, not "a few."
3. **Agent 4's claim about `logger/test_levels.py`** was significantly wrong -- 10 of 11 tests are unique (setup/config tests not in `test_logger.py`).
4. **Agent 4's claim about `test_config_edge_cases.py`** was wrong -- 14 of 17 tests are unique boundary/constraint tests.
5. **Agent 4's `test_singleton.py` reduction claim** was dangerous -- thread safety tests should never be cut.
6. **Agent 3's claim about `test_battle_config.py`** was wrong -- it has unique config field coverage not in `battle_controller/test_config.py`.
