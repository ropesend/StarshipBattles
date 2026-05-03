# Validation Review 3: AI/Research/Combat + Refactor/Builder/Systems Findings

**Reviewer:** Skeptical Validator (Claude Opus 4.6)
**Date:** 2026-02-16
**Methodology:** Every test file read directly. Duplicate claims verified by comparing actual test method names. Dead code claims verified by searching production codebase.

## Summary
- Findings reviewed: **30** (17 from Agent 5 + 13 from Agent 6)
- **CONFIRMED** for removal: **12**
- **DISPUTED** (should keep): **5**
- **MODIFIED** (partial removal only): **13**

---

## Agent 5 Findings (AI/Research/Combat)

---

### H-1: test_interface_definition.py (259 lines, ~30 hasattr checks)
- **Original claim:** DELETE entire file. Pure hasattr checks on IControllable ABC, redundant with ABC mechanism.
- **Verdict:** CONFIRMED
- **Evidence:** Read all 259 lines. Every single test in all 4 classes (TestIControllableDefinition, TestIControllableExtendedMethods, TestIControllableFormationMethods, TestIControllableCombatMethods) follows the exact same pattern: import IControllable, `assert hasattr(IControllable, 'method_name')`. Python's ABC mechanism enforces these at instantiation time. The edge cases file (`test_controllable_adapter_edge_cases.py`) has `test_all_abstract_methods_implemented` which comprehensively verifies the full set.
- **Unique tests that would be lost:** None. The `test_icontrollable_is_protocol_or_abc` test (checks if Protocol or ABCMeta) is mildly interesting but provides zero regression value - the type of the class won't silently change.
- **Risk of removal:** None

---

### H-2: test_combat_endurance_edge_cases.py (27 lines, 2 tests)
- **Original claim:** DELETE entire file. Empty scaffolds.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file. `test_full_resources_baseline` does `from game.simulation.entities import ship; assert hasattr(ship, 'Ship')` - pure import check. `test_resource_levels_affect_combat` is literally `pass`. Zero test value.
- **Unique tests that would be lost:** None
- **Risk of removal:** None

---

### H-3: test_targeting_edge_cases.py (23 lines, 2 tests)
- **Original claim:** DELETE entire file. Import checks only.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file. Both tests are import/hasattr checks. Agent 5's summary is accurate. **Important correction:** Agent 5 did NOT claim targeting_system.py and damage_calculator.py are dead code - they only said these import-check tests are redundant because any test that actually uses the modules validates the imports. My sub-agent confirmed both production modules are actively used (targeting_system.py is used by ShipCombatEngine and WeaponFiringSystem; damage_calculator.py is used by ShipCombatEngine). The tests are redundant, not the code.
- **Unique tests that would be lost:** None
- **Risk of removal:** None

---

### H-4: AI Behavior Test Duplication (4 files, claimed ~682 lines saved)
- **Original claim:** CONSOLIDATE 4 behavior files into test_behavior_units.py. Delete 3 redundant files.
- **Verdict:** MODIFIED - Keep test_advanced_behaviors.py, merge test_ai_behaviors.py, delete test_other_behaviors.py

**Evidence - Behavior Coverage Matrix:**

| Behavior | test_behavior_units.py | test_advanced_behaviors.py | test_ai_behaviors.py | test_other_behaviors.py |
|---|---|---|---|---|
| AIBehavior base | 3 tests | - | - | - |
| RamBehavior | 1 test (navigate_to) | - | 1 test (navigate_to params) | 1 test (navigate_to) |
| FleeBehavior | 4 tests (direction, fire_while, zero_dist) | - | - | 1 test (basic) |
| KiteBehavior | 6 tests (close/far/min_spacing/avoidance) | 1 test (2 scenarios) | 5 tests (opt_dist/clamp/avoidance) | - |
| AttackRunBehavior | 7 tests (states/timer/custom) | 1 test (3-phase) | - | 1 test (approach) |
| FormationBehavior | 7 tests (dead/derelict/no master/drift/fixed) | 1 test (integrity check) | 5 tests (abandon/fixed/relative/drift/sync) | - |
| OrbitBehavior | 5 tests (no_target/zero_dist/close/far/tangent) | 1 test (geometry) | - | 1 test (no_target) |
| DoNothingBehavior | 1 test | - | - | 1 test |
| StationaryFireBehavior | 1 test | - | - | 1 test |
| StraightLineBehavior | 1 test | - | - | 1 test |
| RotateOnlyBehavior | 2 tests | - | - | 1 test |
| ErraticBehavior | 10 tests (timer/interval/strategy/direction) | - | - | - |

**Unique tests NOT in test_behavior_units.py:**
- `test_advanced_behaviors.py::test_formation_integrity__ability_check` - Tests `AIController._check_formation_integrity()` with real `AIController` and `ShipControllableAdapter`. This is the ONLY test that tests formation integrity checking through the actual controller. **UNIQUE AND VALUABLE.**
- `test_ai_behaviors.py::test_opt_dist_calculation` - Verifies exact opt_dist = weapon_range * multiplier and the stop_dist value passed to navigate_to. test_behavior_units.py tests the close/far branching but NOT the exact stop_dist value calculation.
- `test_ai_behaviors.py::test_opt_dist_min_clamp` - Tests that opt_dist is clamped to minimum 150. Not tested anywhere else.
- `test_ai_behaviors.py::test_branching_kite_maintain` - Verifies exact kite_pos calculation with Vector2 math. More rigorous than test_behavior_units.py's test_kite_backs_off_when_too_close.
- `test_ai_behaviors.py::test_target_pos_fixed_rotation` - Tests exact target_pos for fixed rotation mode with precise Vector2 assertions. test_behavior_units.py only checks navigate_to was called.
- `test_ai_behaviors.py::test_target_pos_relative_rotation` - Tests exact target_pos for relative rotation (50,0 rotated 90 degrees = (100,150)). Not in test_behavior_units.py.
- `test_ai_behaviors.py::test_drift_logic_correction` - Tests spring correction drift logic with precise position assertions. Not in test_behavior_units.py.
- `test_ai_behaviors.py::test_velocity_sync` - Tests engine throttle sync with master. Not in test_behavior_units.py.

**Revised recommendation:**
1. **KEEP `test_advanced_behaviors.py`** - The formation integrity test is unique and tests a real AIController code path
2. **MERGE unique tests from `test_ai_behaviors.py` into `test_behavior_units.py`** - 8 unique tests with precise value assertions
3. **DELETE `test_other_behaviors.py`** - ALL tests are strictly less thorough versions of tests in test_behavior_units.py
- **Revised lines saved:** ~164 (test_other_behaviors.py only), not 682
- **Risk of removal (test_other_behaviors.py):** None
- **Risk if test_ai_behaviors.py deleted without merge:** **HIGH** - Would lose precise value assertion tests for kite opt_dist, formation target position calculations, drift correction, and velocity sync

---

### H-5: Capabilities Cache Test Files (2 files, claimed ~225 lines saved)
- **Original claim:** CONSOLIDATE into one file.
- **Verdict:** MODIFIED - Keep both, they test different things

**Evidence:**
- `test_ai_capabilities_cache.py` (225 lines) tests `AIController._build_capabilities_cache()` and `_score_and_sort_enemies()`. It tests the **controller-level** cache building and usage.
- `target_evaluator/test_capabilities_cache.py` (232 lines) tests `TargetEvaluator.evaluate()` with the `ship_capabilities_cache` parameter. It tests the **evaluator-level** cache consumption.

**Unique to test_ai_capabilities_cache.py:**
- `test_build_capabilities_cache_exists`, `test_build_capabilities_cache_returns_dict`, `test_build_capabilities_cache_includes_all_ships` - Tests the cache builder itself
- `test_score_and_sort_uses_capabilities_cache`, `test_score_and_sort_caches_reduces_component_lookups` - Tests that the sorting method uses caching to reduce lookups
- `test_capabilities_cache_passed_to_evaluator` - Integration test

**Unique to target_evaluator/test_capabilities_cache.py:**
- `test_has_weapons_uses_cache_when_available` - Verifies get_components_by_ability NOT called when cache present
- `test_has_weapons_fallback_when_not_in_cache` - Tests cache miss fallback
- `test_has_weapons_cached_false_returns_zero` - Tests unarmed cached value
- `test_has_weapons_required_cached_false_returns_neg_inf` - Tests required flag with cached miss
- `test_multiple_evaluations_with_cache_avoid_redundant_lookups` - 5-target batch test

**These files test different layers (controller vs evaluator) of the same optimization.** The overlap is conceptual, not actual duplicate test methods. Both are valuable.

- **Unique tests that would be lost:** 5+ tests on each side
- **Risk of removal:** **Medium** - Would lose either controller-level or evaluator-level cache testing

---

### H-6: Target Evaluator Rules Files (2 files, claimed ~599 lines saved)
- **Original claim:** CONSOLIDATE. Keep test_target_evaluator_rules.py, delete test_evaluation_rules.py.
- **Verdict:** MODIFIED - Merge unique tests, then delete

**Evidence:** Both files test the same 14 rule types. However:

**Unique to test_evaluation_rules.py (NOT in test_target_evaluator_rules.py):**
- `TestNearestRule::test_nearest_zero_distance` - Zero distance edge case
- `TestMassRules::test_largest_same_as_mass` - Verifies mass/largest equivalence
- `TestMassRules::test_missing_mass_uses_default` - Tests missing attribute handling
- `TestSpeedRules::test_missing_velocity_uses_zero` - Tests missing velocity
- `TestStrengthRules` class (2 tests) - Tests strongest/weakest aliases via mass
- `TestSpeedRulesFactorBased` class (6 tests) - **Documents a KNOWN BUG** in slowest-with-factor logic (double negation makes faster targets score higher). This is critical documentation.
- `TestEdgeCases::test_missing_weight_uses_zero` - Default weight behavior
- `TestEdgeCases::test_missing_factor_uses_one` - Default factor behavior
- `TestEdgeCases::test_same_position_zero_distance` - Zero distance edge
- `TestEdgeCases::test_negative_weight` - Negative weight behavior
- `TestEdgeCases::test_very_large_distance` - Large distance handling

**Assessment:** ~11 unique tests in test_evaluation_rules.py, including the critical `TestSpeedRulesFactorBased` class documenting a bug. These MUST be preserved.

- **Unique tests that would be lost:** 11+ including bug documentation tests
- **Risk of removal without merge:** **HIGH** - Would lose bug documentation and edge case coverage
- **Revised recommendation:** Merge the 11 unique tests into test_target_evaluator_rules.py, then delete test_evaluation_rules.py. Lines saved: ~400 (not 599)

---

### H-7: Evaluation Integration/Edge Case Files (2 files, claimed ~250 lines saved)
- **Original claim:** CONSOLIDATE. Merge integration into edge cases.
- **Verdict:** MODIFIED - Merge unique tests, then delete

**Evidence:**

**Unique to test_evaluation_integration.py (NOT in test_target_evaluator_edge_cases.py):**
- `TestCustomStatHelpers::test_custom_get_hp_percent` - Custom HP percent function
- `TestCustomStatHelpers::test_custom_is_in_pdc_arc` - Custom PDC arc function
- `TestDefaultStatHelpers::test_default_get_hp_percent_no_components` - Tests `get_hp_percent()` from `combat_utils`
- `TestDefaultStatHelpers::test_default_get_hp_percent_calculates_correctly` - HP calculation: (50+25)/(100+100)=0.375
- `TestDefaultStatHelpers::test_default_is_in_pdc_arc_no_pdc_weapons` - Tests `is_in_pdc_arc()` from `combat_utils`
- `TestEdgeCases::test_missing_weight_uses_zero` - Default weight
- `TestEdgeCases::test_missing_factor_uses_one` - Default factor
- `TestEdgeCases::test_negative_weight` - Negative weight
- `TestEdgeCases::test_very_large_distance` - Large distance
- `TestThreatAssessment::test_armed_damaged_target_high_priority` - Realistic scenario
- `TestThreatAssessment::test_close_fast_target_high_threat` - Realistic scenario

**Overlapping tests:** required flag (2 tests), empty rules (1 test), multiple rules additive (1 test), pdc_arc missile tests (3 tests), capabilities cache (1 test)

**Assessment:** 11+ unique tests, including the important `TestDefaultStatHelpers` class testing `combat_utils` functions directly, and `TestThreatAssessment` realistic scenarios.

- **Unique tests that would be lost:** 11 tests including combat_utils function tests
- **Risk of removal without merge:** **Medium-High**
- **Revised recommendation:** Merge the 11 unique tests into test_target_evaluator_edge_cases.py, then delete test_evaluation_integration.py. Lines saved: ~150 (not 250)

---

### M-1: Controllable Adapter Test Files (4 files, claimed ~496 lines saved)
- **Original claim:** CONSOLIDATE into 2 files. Delete adapter_basics.py and adapter_methods.py.
- **Verdict:** MODIFIED - Merge must preserve unique tests

**Evidence from matrix analysis:**

**18+ functionally equivalent tests** between test_adapter_basics.py (File 1) and test_controllable_adapter_edge_cases.py (File 3). Both test basic delegation (get_position, get_velocity, set_throttle, rotate, etc.)

**Unique to test_adapter_basics.py:**
- `test_adapter_can_be_imported` - trivial
- `test_adapter_get_radius_returns_ship_radius` - NOT in File 3. Must be preserved.

**Unique to test_adapter_methods.py (File 2):**
- `test_adapter_uses_interface_methods_not_direct_access` - Tests that adapter uses interface, not direct attribute access
- `test_direct_attribute_access_raises_error` - Tests attribute access guard
- `test_direct_attribute_assignment_does_not_delegate` - Tests assignment behavior
- `test_adapter_get_turn_speed_returns_ship_turn_speed` - NOT in File 3
- `test_adapter_get_acceleration_rate_returns_ship_acceleration_rate` - NOT in File 3
- `test_adapter_get_is_thrusting_returns_ship_is_thrusting` - NOT in File 3
- `test_adapter_get_turn_throttle_returns_ship_turn_throttle` - NOT in File 3
- `test_adapter_set_formation_master_to_none` - Tests None case specifically

**Unique to test_controllable_adapter.py (File 4):**
- ALL 5 tests are unique (ABC contract validation). KEEP entirely.

**Assessment:** Files 1 and 2 have ~9 unique tests between them that must be merged into File 3 before deletion.

- **Unique tests that would be lost without merge:** 9 tests (get_radius, turn_speed, acceleration_rate, is_thrusting, turn_throttle, interface-not-direct-access checks, set_formation_master_to_none)
- **Risk of removal without merge:** **HIGH**
- **Revised recommendation:** Merge the 9 unique tests into test_controllable_adapter_edge_cases.py, then delete adapter_basics.py and adapter_methods.py. Keep test_controllable_adapter.py entirely. Lines saved: ~400 (not 496)

---

### M-2: research_controls/test_handle_event.py (274 lines)
- **Original claim:** DELETE. Over-mocked, tests reimplemented logic not production code.
- **Verdict:** CONFIRMED
- **Evidence:** Sub-agent confirmed: zero imports of production code. Tests create mock objects and test Python's `not` operator, callback invocation on mocks, and basic arithmetic. Lines 196-224 define inline functions that reimplement logic rather than importing it. No production code path exercised.
- **Unique tests that would be lost:** None that test real code
- **Risk of removal:** None

---

### M-3: research_controls/test_event_formatting.py (182 lines)
- **Original claim:** DELETE. Over-mocked, tests inline reimplementation.
- **Verdict:** CONFIRMED
- **Evidence:** Sub-agent confirmed: zero imports of production code. Lines 10-47 manually construct format strings (`f"<font color='#80FF80'>BREAKTHROUGH!</font>"`) and test them, rather than importing production formatting functions. Tests only the test's own string construction.
- **Unique tests that would be lost:** None that test real code
- **Risk of removal:** None

---

### M-4: research_controls/test_node_selection.py (113 lines)
- **Original claim:** DELETE. Over-mocked, tests basic arithmetic.
- **Verdict:** CONFIRMED
- **Evidence:** Sub-agent confirmed: zero imports of production code. Tests `50 + 150 == 200` and hardcoded dict values. No production code paths exercised.
- **Unique tests that would be lost:** None that test real code
- **Risk of removal:** None

---

### M-5: Research Tracker Edge Cases (claimed ~100 lines saved)
- **Original claim:** MERGE edge cases into main tracker test file, delete edge cases file.
- **Verdict:** DISPUTED - Keep both files

**Evidence:**
The edge cases file has 11 unique test methods including:
- `test_node_state_roundtrip` - Full serialization round-trip
- `test_node_state_zero_rp` - Zero allocation edge
- `test_node_state_max_chance` - Maximum chance boundary
- `test_session_seed_consistency` - Seed determinism
- `test_session_seed_from_dict_preserved` - Seed persistence
- `test_auto_spread_enabled_roundtrip` - Auto-spread serialization

While there's moderate serialization overlap, the edge cases file is only 150 lines and provides focused, clear edge case coverage. The main file is already 596 lines. Merging would make the main file overly large (746+ lines) for minimal line savings (~50 lines after merge). The edge case file's focused scope makes it easy to locate and maintain serialization-specific tests.

- **Risk of removal:** Low-Medium - Tests are unique and provide value
- **Recommendation:** KEEP both files as-is. The organizational benefit outweighs the ~50 line savings.

---

### M-6: TechTree Validation Tests (claimed ~200 lines saved)
- **Original claim:** Remove duplicate test classes from test_validation.py.
- **Verdict:** MODIFIED - Partial consolidation appropriate

**Evidence:**
- `test_validation.py::TestDetectCycles` overlaps significantly with `test_cycle_detection.py` (which is more comprehensive with 5 specialized classes)
- `test_validation.py::TestDepthCalculation` overlaps with `test_queries.py::TestTechTreeDepthCalculation`

**Unique to test_validation.py:**
- `TestValidate` - Tests the combined `validate()` method (orchestrator)
- `TestEdgeCases` - Requirements referencing self, empty requirements

**Recommendation:** Remove `TestDetectCycles` and `TestDepthCalculation` classes from test_validation.py. Keep `TestValidateRequirements`, `TestValidate`, and `TestEdgeCases`. Lines saved: ~120 (not 200).

- **Unique tests that would be lost:** None if done correctly
- **Risk of removal:** Low

---

### M-7: Layout Constants Tests (~24 lines)
- **Original claim:** DELETE the TestLayoutConstants class (4 tests).
- **Verdict:** CONFIRMED
- **Evidence:** Tests that `SIDEBAR_WIDTH > 0`, `COLUMN_SPACING > 0`, etc. These are trivial constant-value checks. A developer would have to deliberately set a layout constant to 0 or negative AND not notice the broken UI. These provide no regression safety.
- **Unique tests that would be lost:** 4 trivially obvious assertions
- **Risk of removal:** None

---

### L-1: AI Controller Test Files (4 files, potential overlap)
- **Original claim:** REVIEW for specific overlaps. ~200 lines estimated.
- **Verdict:** DISPUTED - Keep all 4 files

**Evidence:** Agent 5 correctly identified these files serve complementary purposes:
- `test_ai_controller_unit.py` (1149 lines) - Comprehensive mocked unit tests
- `test_ai_controller_edge_cases.py` (404 lines) - StrategyManager integration
- `test_ai_controller_interface.py` (467 lines) - Adapter integration
- `test_ai.py` (316 lines) - Real ship integration

Without a line-by-line comparison (which Agent 5 flagged as needed), any removal risks losing coverage. The LOW confidence rating was appropriate. These files test the same class from 4 deliberately different perspectives (unit/edge/interface/integration).

- **Risk of removal:** High
- **Recommendation:** KEEP all 4. A future audit could identify specific duplicate test methods, but wholesale consolidation is too risky.

---

### L-2: test_lead.py vs test_weapons.py Lead Tests
- **Original claim:** Consider converting test_lead.py to use production code.
- **Verdict:** MODIFIED - DELETE test_lead.py outright

**Evidence:** Sub-agent discovered that `test_lead.py` defines its own `MockVector` and `solve_lead()` function locally and tests ONLY those local implementations. It never imports production code. The real `solve_lead` lives in `game.simulation.combat.targeting_system.TargetingSystem.solve_lead()` and is tested via `test_weapons.py::TestLeadCalculation` which uses the actual `ShipCombatEngine`. This is dead test code that tests an orphaned local algorithm, not production code.

- **Unique tests that would be lost:** None that test production code. The algorithm tests are interesting but verify nothing about the actual game.
- **Risk of removal:** None
- **Lines saved:** ~143

---

### L-3: test_ccd.py - Local Algorithm Test
- **Original claim:** Rewrite to test production CCD or remove.
- **Verdict:** CONFIRMED for removal (DELETE)

**Evidence:** Sub-agent confirmed: `test_ccd.py` defines its own `Vector` class and `check_collision()` function locally. It tests ONLY these local implementations. **No production CCD module exists** in `game/simulation/combat/`. The production collision system (`game/engine/collision.py`) uses beam raycasting and simple distance checks for ramming, not CCD. This is a dead-end feature that was never implemented in production.

**Important note:** There is a SEPARATE `tests/unit/engine/collision_edge_cases/test_ccd.py` that DOES test production code (CCD for projectile collision detection). The combat file is the orphaned one.

- **Unique tests that would be lost:** None that test production code
- **Risk of removal:** None
- **Lines saved:** ~208

---

## Agent 6 Findings (Refactor/Builder/Systems/Engine)

---

### Agent 6 HIGH-1: test_bulk_add.py empty stubs
- **Original claim:** Remove 2 empty `pass` methods.
- **Verdict:** CONFIRMED
- **Evidence:** Read the file. `test_bulk_add_with_limit` has setup code + comments but body is `pass`. `test_bulk_performance_mock` is entirely `pass` with a vague "Verify it runs fast enough?" comment. Neither executes any assertions.
- **Unique tests that would be lost:** None (they test nothing)
- **Risk of removal:** None

---

### Agent 6 HIGH-2: test_ship_loading.py empty class
- **Original claim:** Remove empty `TestShipExpectedStats` class.
- **Verdict:** CONFIRMED
- **Evidence:** `class TestShipExpectedStats: pass` with docstring only. Zero test methods. Its stated purpose is already covered by `TestAllShipDesigns::test_all_ships_match_expected_stats` in the same file.
- **Unique tests that would be lost:** None (class has no tests)
- **Risk of removal:** None

---

### Agent 6 HIGH-3: test_allowed_layers_removal.py partial removal
- **Original claim:** Remove TestAllowedLayersRemoval (5 tests), keep TestBuilderDropValidation (3 tests).
- **Verdict:** CONFIRMED
- **Evidence:** The 5 tests in `TestAllowedLayersRemoval` verify that `allowed_layers` attribute was removed from Component subclasses. This was a one-time refactoring migration. The attribute-creation code was deleted, so it can never silently reappear. The `TestBuilderDropValidation` class (3 tests) verifies ongoing centralized validator behavior for weapon/armor placement rules - this has ongoing value.
- **Unique tests that would be lost:** 5 one-time verification tests (no ongoing value)
- **Risk of removal:** None

---

### Agent 6 MEDIUM-1: Spatial test duplication
- **Original claim:** Consolidate test_spatial_extended.py into test_spatial.py.
- **Verdict:** MODIFIED - Merge unique tests first

**Evidence from comparison matrix:**
- 5 tests duplicate between files (grid_initialization, insert, clear, query_finds_nearby, query_ignores_distant)
- **Unique to test_spatial_extended.py:**
  - `test_query_radius_empty_grid` - Tests empty grid query
  - `test_same_cell_multiple_objects` - Tests bucket grouping
  - `test_different_cells_different_buckets` - Tests cell assignment
  - `test_negative_coordinates_handled` - Edge case (also in test_spatial.py's queries but tests at insert level)
  - `test_query_spans_multiple_cells` - Cross-cell query test

**5 unique tests** must be merged before deletion.

- **Unique tests that would be lost without merge:** 5 tests
- **Risk of removal without merge:** Medium
- **Recommendation:** Merge 5 unique tests into test_spatial.py, then delete test_spatial_extended.py.

---

### Agent 6 MEDIUM-2: Collision system duplication
- **Original claim:** Consolidate test_collision_system.py into engine/test_beam_ramming.py.
- **Verdict:** MODIFIED - Merge unique tests first

**Evidence from comparison matrix:**
- 5 tests duplicate between files (zero direction, dead target, no target, mutual destruction, non-kamikaze, no target ramming)
- **Unique to test_collision_system.py (NOT in test_beam_ramming.py):**
  - `test_beam_weapon_raycasting` - Direct hit + near miss + range limits in one test
  - `test_beam_weapon_tangent_hit` - Discriminant == 0 edge case
  - `test_beam_weapon_target_behind_origin` - Negative t values
  - `test_beam_weapon_origin_inside_target` - Ray origin inside sphere
  - `test_ramming_logic` - Case A & B with different HP values
  - `test_ramming_no_logger` - Ramming without logger instance

**6 unique tests** must be merged before deletion.

- **Unique tests that would be lost without merge:** 6 tests (including the valuable tangent-hit and origin-inside-target geometry tests)
- **Risk of removal without merge:** **High** - Would lose important geometry edge case coverage
- **Recommendation:** Merge 6 unique tests into test_beam_ramming.py, then delete test_collision_system.py.

---

### Agent 6 MEDIUM-3: test_persistence.py naming
- **Original claim:** Rename to test_tkinter_utils.py.
- **Verdict:** DISPUTED - Low priority, not a removal candidate
- **Evidence:** The file contains a valid test for tkinter initialization failure logging. Renaming is a good idea but doesn't save any lines or reduce maintenance burden. Not a cleanup candidate for this review.
- **Risk:** None (cosmetic only)

---

### Agent 6 MEDIUM-4: test_main_integration.py weakness
- **Original claim:** Strengthen test_import_main, keep test_game_instantiation.
- **Verdict:** DISPUTED - Keep as-is
- **Evidence:** The file has 2 smoke tests. `test_import_main` catches ImportError on module load - this is a valid regression test for circular import issues which are notoriously hard to detect. The swallowed non-import exceptions are a valid concern but this isn't a removal candidate. `test_game_instantiation` is clearly valuable. Both should stay.
- **Risk:** None (keep both)

---

### Agent 6 MEDIUM-5: Refactor formula overlap
- **Original claim:** Deduplicate division-by-zero and formula evaluation tests across 3 files.
- **Verdict:** DISPUTED - Keep all
- **Evidence:** The refactor/ directory contains 23 files that are the canonical TDD tests for the modifier system. Agent 6 correctly identified these as permanent production tests despite the misleading directory name. The noted overlaps (division-by-zero tested in both test_formula_error_handling.py and test_formula_edge_cases.py; formula evaluations tested in 3 files) are MINOR and each file tests from a different angle:
  - `test_formula_error_handling.py` - Tests error HANDLING (logging, graceful degradation)
  - `test_formula_edge_cases.py` - Tests edge VALUES (div/0, overflow, real-world formulas)
  - `test_modifier_effect_evaluator.py` - Tests the evaluator CLASS behavior

The triple-testing of `param^2=4` is ~6 lines of overlap across 3 files. Not worth consolidating.

- **Risk of consolidation:** Would blur the testing focus of each file
- **Recommendation:** KEEP all 23 files in refactor/. Consider renaming directory to `modifiers/` for clarity.

---

### Agent 6 MEDIUM-6: test_seeker_multi_ability.py inspect.getsource
- **Original claim:** Replace inspect.getsource() test with behavior-based test.
- **Verdict:** DISPUTED - Keep as-is (for now)
- **Evidence:** The test using `inspect.getsource()` to verify implementation details is admittedly brittle. However, it guards against a specific anti-pattern (direct stats access vs STAT_BINDINGS). Until a behavior-based alternative is written, removing this test creates a regression risk. This is a "refactor, don't remove" situation.
- **Risk of removal:** Low-Medium
- **Recommendation:** Mark as tech debt to refactor, but don't remove.

---

### Agent 6: refactor/ directory assessment
- **Original claim:** KEEP ALL 23 FILES. These are permanent TDD tests for the modifier system.
- **Verdict:** CONFIRMED - Agent 6 was correct
- **Evidence:** All 23 files test real, current production code. All imports resolve. The directory name "refactor" is misleading (they were written during a refactoring project but test permanent production features: StatKey, AbilityStatBinding, ModifierEffect, STAT_BINDINGS, V2 modifier schema, pipeline unification, multi-ability effects, introspection).
- **Recommendation:** Rename directory from `tests/unit/refactor/` to `tests/unit/modifiers/` for clarity. No tests should be removed.

---

## Consolidated Action Items

### DELETE (no merge needed) - 12 items, ~1,130 lines
| File | Lines | Reason |
|------|-------|--------|
| `tests/unit/ai/controllable_interface/test_interface_definition.py` | 259 | Pure hasattr checks, ABC enforces this |
| `tests/unit/combat/test_combat_endurance_edge_cases.py` | 27 | Empty scaffolds |
| `tests/unit/combat/test_targeting_edge_cases.py` | 23 | Import checks only |
| `tests/unit/ai/formation_prediction/test_other_behaviors.py` | 164 | All tests are weaker copies of test_behavior_units.py |
| `tests/unit/research/research_controls/test_handle_event.py` | 274 | Zero production code tested |
| `tests/unit/research/research_controls/test_event_formatting.py` | 182 | Zero production code tested |
| `tests/unit/research/research_controls/test_node_selection.py` | 113 | Zero production code tested |
| `tests/unit/combat/test_lead.py` | 143 | Tests local reimplementation, not production |
| `tests/unit/combat/test_ccd.py` | 208 | Tests algorithm never in production |
| `tests/unit/builder/test_bulk_add.py` (2 methods) | ~30 | Empty pass stubs |
| `tests/unit/builder/test_ship_loading.py` (1 class) | ~3 | Empty class |
| `tests/unit/systems/test_allowed_layers_removal.py` (1 class) | ~50 | One-time migration check |

### MERGE THEN DELETE - 6 items, ~1,700 lines saved after merge
| Source File | Target File | Unique Tests to Merge |
|-------------|-------------|----------------------|
| `test_ai_behaviors.py` (340 lines) | `test_behavior_units.py` | 8 tests (opt_dist, clamp, kite_maintain, fixed/relative rotation, drift, velocity_sync) |
| `test_evaluation_rules.py` (599 lines) | `test_target_evaluator_rules.py` | 11 tests (zero_distance, largest_same_as_mass, missing attrs, strength rules, speed factor bug docs) |
| `test_evaluation_integration.py` (286 lines) | `test_target_evaluator_edge_cases.py` | 11 tests (custom helpers, default helpers, threat scenarios, missing weight/factor) |
| `controllable_interface/test_adapter_basics.py` + `test_adapter_methods.py` (496 lines) | `test_controllable_adapter_edge_cases.py` | 9 tests (get_radius, turn_speed, accel_rate, is_thrusting, turn_throttle, interface checks, set_master_none) |
| `test_spatial_extended.py` (~157 lines) | `test_spatial.py` | 5 tests (empty grid, same cell, different cells, negative coords, cross-cell) |
| `test_collision_system.py` (~393 lines) | `engine/test_beam_ramming.py` | 6 tests (raycasting, tangent hit, behind origin, inside target, ramming logic, no logger) |

### KEEP AS-IS (disputed removals) - 5 items
| File | Reason to Keep |
|------|---------------|
| `tests/unit/research/test_research_tracker_edge_cases.py` | 11 unique tests, organizational value > 50-line savings |
| All 4 AI controller test files (L-1) | Complementary perspectives, removal too risky |
| All 23 refactor/ files | Permanent modifier system tests |
| `tests/unit/systems/test_persistence.py` | Valid test, rename is cosmetic |
| `tests/unit/systems/test_main_integration.py` | Valid smoke tests |

### PARTIAL CLEANUP - 1 item
| File | Action |
|------|--------|
| `test_validation.py` | Remove TestDetectCycles + TestDepthCalculation classes (~120 lines), keep 3 other classes |

### RENAME (cosmetic, optional)
| Item | Recommendation |
|------|---------------|
| `tests/unit/refactor/` | Rename to `tests/unit/modifiers/` |
| `tests/unit/systems/test_persistence.py` | Rename to `test_tkinter_utils.py` |
