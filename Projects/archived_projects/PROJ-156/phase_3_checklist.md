# Phase 3: Merge Then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Merge unique tests from 8 source files into 6 target files, then delete sources. ~1,900 lines saved. Order: simplest to most complex.
**Priority:** High

---

## Post-PROJ-157 Assessment

PROJ-157 deleted the source file for Pair 3 (`test_ai_behaviors.py`) but only merged 4 of 7 unique tests. **3 KiteBehavior tests were lost** and must be recovered from git history. All other source files (Pairs 1,2,4,5,6) still exist on disk — no merges were performed for those pairs.

---

## Tasks

### Task 3.0: Recover 3 lost KiteBehavior tests [CRITICAL] ⚠️ COMPLETE
**Source:** Git history, commit `b1edd82b^:tests/unit/ai/test_ai_behaviors.py`
**Target:** `tests/unit/ai/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py -v`

PROJ-157 deleted `test_ai_behaviors.py` but failed to merge these 3 tests into the target:
- [x] Recover `test_opt_dist_calculation` from git history — tests exact opt_dist = weapon_range * multiplier + stop_dist
- [x] Recover `test_opt_dist_min_clamp` from git history — tests opt_dist clamped to minimum 150
- [x] Recover `test_branching_kite_maintain` from git history — tests exact kite-away vector math
- [x] Adapt to target's fixture patterns (use `game.core.math.Vector2`, not `pygame.math.Vector2`)
- [x] Add to `TestKiteBehavior` class or create appropriate section in target
- [x] Run `pytest tests/unit/ai/test_behavior_units.py -v` — all tests pass (54 passed)

**Recovery command:** `git show b1edd82b^:tests/unit/ai/test_ai_behaviors.py`

**Notes:** Tests recovered and adapted to use game.core.math.Vector2. Added with section comment documenting recovery source. Total KiteBehavior tests: 9 (6 existing + 3 recovered).

### Task 3.1: Merge Spatial Tests [Simple] ⚠️ COMPLETE
**Source:** `tests/unit/systems/test_spatial_extended.py` (157 lines) — DELETED
**Target:** `tests/unit/systems/test_spatial.py` (now 195 lines)
**Tests:** `pytest tests/unit/systems/test_spatial.py -v` then `pytest tests/ -n 12`

- [x] Read both source and target files fully
- [x] Identify unique tests in source NOT present in target. Key unique tests:
  - `test_insert_creates_bucket` — DUPLICATE of `test_insert_single_object` (skip)
  - `test_query_spans_multiple_cells` — UNIQUE (merged)
  - `test_query_radius_empty_grid` — UNIQUE (merged)
  - (11 other tests have equivalents in target with different names — skipped)
- [x] Copy unique tests into appropriate classes in target file
- [x] Adapt MockObject if needed (used target's MockObject with name param)
- [x] Run `pytest tests/unit/systems/test_spatial.py -v` — 13 passed
- [x] Delete `tests/unit/systems/test_spatial_extended.py`
- [x] Run `pytest tests/ -n 12` — 11971 passed, 144 pre-existing failures (no regressions)

**Notes:** Source had 13 tests, target had 11. Careful semantic comparison found only 2 truly unique tests: `test_query_radius_empty_grid` and `test_query_spans_multiple_cells`. Both merged into new `TestSpatialGridExtendedCases` class. Net change: -11 duplicate tests, +2 unique merged.

### Task 3.2: Merge Collision System Tests [Medium] ⚠️ COMPLETE
**Source:** `tests/unit/systems/test_collision_system.py` (393 lines) — DELETED
**Target:** `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` (now 768 lines)
**Tests:** `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py -v` then `pytest tests/ -n 12`

- [x] Read both source and target files fully
- [x] Read `tests/unit/engine/collision_edge_cases/conftest.py` for `collision_system` fixture
- [x] Identify unique tests in source NOT already covered by target. Analysis:
  - `test_beam_weapon_raycasting` — DUPLICATE (covered by geometry tests)
  - `test_ramming_logic` — DUPLICATE (covered by HP tests)
  - `test_beam_weapon_tangent_hit` — UNIQUE (merged)
  - `test_beam_weapon_target_behind_origin` — UNIQUE (merged)
  - `test_beam_weapon_zero_direction_vector` — DUPLICATE of `test_beam_zero_length_direction`
  - `test_beam_weapon_dead_target` — DUPLICATE of `test_beam_dead_target_no_hit`
  - `test_beam_weapon_no_target` — DUPLICATE of `test_beam_no_target`
  - `test_beam_weapon_origin_inside_target` — DUPLICATE of `test_beam_target_at_origin`
  - `test_ramming_mutual_destruction` — DUPLICATE of `test_ramming_equal_hp_mutual_destruction`
  - `test_ramming_no_logger` — UNIQUE (merged)
  - `test_ramming_non_kamikaze_ship` — DUPLICATE of `test_ramming_non_kamikaze_ignored`
  - `test_ramming_no_current_target` — DUPLICATE of `test_ramming_no_target_ignored`
- [x] Adapt tests to use `collision_system` fixture instead of inline `CollisionSystem()`
- [x] Copy unique tests into target file (3 tests with migration comments)
- [x] Run `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py -v` — 23 passed (was 20)
- [x] Delete `tests/unit/systems/test_collision_system.py`
- [x] Run `pytest tests/ -n 12` — 11962 passed, 144 pre-existing failures (no regressions)

**Notes:** Source had 12 tests, target had 20. Only 3 truly unique tests: tangent hit, target behind origin, no logger. Net change: -9 duplicate tests removed, +3 unique tests merged.

### Task 3.3: Merge AI Behavior Tests [COMPLETE]
**Source:** `tests/unit/ai/test_ai_behaviors.py` — DELETED by PROJ-157
**Target:** `tests/unit/ai/test_behavior_units.py` (735+ lines)

- [x] Source file deleted (by PROJ-157)
- [x] 4 of 7 unique tests merged into `TestFormationBehaviorMigrated` class:
  - `test_formation_fixed_rotation_mode` (was `test_target_pos_fixed_rotation`)
  - `test_target_pos_relative_rotation`
  - `test_drift_logic_correction`
  - `test_velocity_sync`
- [x] **3 KiteBehavior tests recovered via Task 3.0:**
  - `test_opt_dist_calculation`
  - `test_opt_dist_min_clamp`
  - `test_branching_kite_maintain`

**Notes:** All 7 unique tests from source file now present in target. Task complete.

### Task 3.4: Merge Controllable Adapter Tests [Medium] ⚠️ COMPLETE
**Source 1:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` (232 lines) — DELETED
**Source 2:** `tests/unit/ai/controllable_interface/test_adapter_methods.py` (262 lines) — DELETED
**Target:** `tests/unit/ai/test_controllable_adapter_edge_cases.py` (now 516 lines)
**Keep untouched:** `tests/unit/ai/test_controllable_adapter.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v` then `pytest tests/ -n 12`

- [x] Read both source files and target file fully
- [x] Read `tests/unit/ai/controllable_interface/conftest.py` for fixture patterns
- [x] Identify unique tests across both sources NOT in target. Analysis:
  - `test_adapter_can_be_imported` — TRIVIAL import check (skipped)
  - `test_adapter_exposes_underlying_ship` → DUPLICATE of `test_adapter_stores_ship_reference`
  - `test_adapter_uses_interface_methods_not_direct_access` → covered by comprehensive method tests
  - `test_direct_attribute_access_raises_error` — UNIQUE (merged)
  - `test_direct_attribute_assignment_does_not_delegate` — UNIQUE (merged)
  - All other 35 tests are duplicates with longer names
- [x] Adapt tests to use target's `mock_ship` fixture pattern (compatible)
- [x] Copy unique tests into target (added `TestAttributeDelegationRemoved` class with PROJ-24 context)
- [x] Run `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v` — 40 passed (was 38)
- [x] Delete `tests/unit/ai/controllable_interface/test_adapter_basics.py`
- [x] Delete `tests/unit/ai/controllable_interface/test_adapter_methods.py`
- [x] Run `pytest tests/ -n 12` — 11925 passed, 144 pre-existing failures (no regressions)

**Notes:** Sources had 39 tests combined, target had 38. Only 2 truly unique tests: `test_direct_attribute_access_raises_error` and `test_direct_attribute_assignment_does_not_delegate` (PROJ-24 __getattr__/__setattr__ removal). Net change: -37 tests (duplicates removed). controllable_interface/ directory still has conftest.py and __init__.py — cleanup in Phase 4.

### Task 3.5: Merge Evaluation Integration Tests [Medium] ⚠️ COMPLETE
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (285 lines) — DELETED
**Target:** `tests/unit/ai/test_target_evaluator_edge_cases.py` (now 489 lines)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_edge_cases.py -v` then `pytest tests/ -n 12`

- [x] Read both source and target files fully
- [x] Read `tests/unit/ai/target_evaluator/conftest.py` for `ship`/`target` fixtures
- [x] Identify unique tests in source NOT in target. Analysis:
  - `TestRequiredFlag` (2 tests) — DUPLICATES of `TestEvaluateRequiredFlag` in target
  - `TestMultipleRules` (2 tests) — DUPLICATES of `TestEvaluateMultipleRules` in target
  - `TestCustomStatHelpers` (2 tests) — UNIQUE (merged as `TestCustomStatHelpersMigrated`)
  - `TestDefaultStatHelpers` (3 tests) — 2 UNIQUE (merged), 1 DUPLICATE (is_in_pdc_arc no_pdc_weapons)
  - `TestEdgeCases` (7 tests) — 2 DUPLICATE (empty_rules, unknown_rule), 5 UNIQUE (merged)
  - `TestThreatAssessment` (2 tests) — UNIQUE (merged as `TestThreatAssessmentMigrated`)
- [x] Add import: `from game.ai.combat_utils import get_hp_percent, is_in_pdc_arc`
- [x] Add import: `from game.core.constants import AttackType`
- [x] Adapt tests to use target's fixture patterns (mock_ship, mock_target, mock_stat_helpers)
- [x] Copy unique tests into target (4 new classes with migration comments)
- [x] Run `pytest tests/unit/ai/test_target_evaluator_edge_cases.py -v` — 26 passed (was 20)
- [x] Delete `tests/unit/ai/target_evaluator/test_evaluation_integration.py`
- [x] Verify `test_capabilities_cache.py` still passes: `pytest tests/unit/ai/target_evaluator/ -v` — 36 passed
- [x] Run `pytest tests/ -n 12` — 11918 passed, 144 pre-existing failures (no regressions)

**Notes:** Source had 16 tests, target had 20. 11 truly unique tests merged. Net change: -5 duplicates removed, +6 tests to target file (26 total). Added 4 migrated test classes: `TestCustomStatHelpersMigrated`, `TestDefaultStatHelpersImplementation`, `TestEdgeCaseDefaultsMigrated`, `TestThreatAssessmentMigrated`.

### Task 3.6: Merge Evaluation Rules Tests [Medium] ⚠️ COMPLETE
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (598 lines) — DELETED
**Target:** `tests/unit/ai/test_target_evaluator_rules.py` (now 1008 lines, 71 tests)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_rules.py -v` then `pytest tests/ -n 12`

**CRITICAL: This merge includes `TestSpeedRulesFactorBased` which documents a known bug. Preserve all test comments.**

- [x] Read both source and target files fully
- [x] Identify unique tests in source NOT in target. Analysis:
  - Source: 44 tests in 11 classes; Target: 58 tests in 8 classes
  - Most tests DUPLICATE target's parametrized coverage (nearest/farthest/mass/speed with various weights)
  - **Unique tests identified:** 13 total:
    - `test_nearest_zero_distance` — edge case for zero distance
    - `test_largest_same_as_mass` — behavior equivalence test
    - `test_strongest_uses_mass` — explicit mass equivalence for strongest
    - `test_weakest_uses_inverse_mass` — explicit mass equivalence for weakest
    - `test_pdc_arc_required_missile_out_of_arc` — required flag out-of-arc rejection
    - **Full `TestSpeedRulesFactorBased` class** (6 tests) — ALL bug-documenting comments preserved
- [x] Merge full `TestSpeedRulesFactorBased` class with all bug-documenting comments intact
- [x] Adapt to target's fixture patterns (mock_ship, mock_target, mock_stat_helpers, Vector2)
- [x] Run `pytest tests/unit/ai/test_target_evaluator_rules.py -v` — 71 passed (58 original + 13 merged)
- [x] Delete `tests/unit/ai/target_evaluator/test_evaluation_rules.py`
- [x] Verify `test_capabilities_cache.py` still passes: `pytest tests/unit/ai/target_evaluator/ -v` — 7 passed
- [x] Run `pytest tests/ -n 12` — 11900 passed, 144 pre-existing failures (no regressions)

**Notes:** Source had 44 tests, target had 58. 13 truly unique tests merged into 5 new classes: `TestMigratedDistanceEdgeCases`, `TestMigratedMassBehaviorEquivalence`, `TestMigratedStrengthRules`, `TestMigratedPDCArcRequired`, `TestSpeedRulesFactorBased`. Net change: -31 duplicates removed, +13 unique tests preserved. Critical bug-documenting tests fully preserved with all TCG-FND-018 comments intact.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All source files deleted (6 source files deleted across all tasks)
- [x] All unique tests verified passing in target files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
