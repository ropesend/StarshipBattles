# Phase 3: Merge Then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partially Complete (Pair 3 source deleted by PROJ-157 but merge incomplete; Pairs 1,2,4,5,6 untouched)
**Objective:** Merge unique tests from 8 source files into 6 target files, then delete sources. ~1,900 lines saved. Order: simplest to most complex.
**Priority:** High

---

## Post-PROJ-157 Assessment

PROJ-157 deleted the source file for Pair 3 (`test_ai_behaviors.py`) but only merged 4 of 7 unique tests. **3 KiteBehavior tests were lost** and must be recovered from git history. All other source files (Pairs 1,2,4,5,6) still exist on disk — no merges were performed for those pairs.

---

## Tasks

### Task 3.0: Recover 3 lost KiteBehavior tests [CRITICAL] ⚠️ NEW
**Source:** Git history, commit `b1edd82b^:tests/unit/ai/test_ai_behaviors.py`
**Target:** `tests/unit/ai/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py -v`

PROJ-157 deleted `test_ai_behaviors.py` but failed to merge these 3 tests into the target:
- [ ] Recover `test_opt_dist_calculation` from git history — tests exact opt_dist = weapon_range * multiplier + stop_dist
- [ ] Recover `test_opt_dist_min_clamp` from git history — tests opt_dist clamped to minimum 150
- [ ] Recover `test_branching_kite_maintain` from git history — tests exact kite-away vector math
- [ ] Adapt to target's fixture patterns (use `game.core.math.Vector2`, not `pygame.math.Vector2`)
- [ ] Add to `TestKiteBehavior` class or create appropriate section in target
- [ ] Run `pytest tests/unit/ai/test_behavior_units.py -v` — all tests pass

**Recovery command:** `git show b1edd82b^:tests/unit/ai/test_ai_behaviors.py`

**Notes:** These tests existed in the source (lines 43, 61, 86) and were confirmed present via git history. PROJ-157 merged 4 other tests (formation rotation, drift, velocity sync) but missed these 3.

### Task 3.1: Merge Spatial Tests [Simple]
**Source:** `tests/unit/systems/test_spatial_extended.py` (157 lines) — STILL EXISTS
**Target:** `tests/unit/systems/test_spatial.py` (153 lines)
**Tests:** `pytest tests/unit/systems/test_spatial.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Identify unique tests in source NOT present in target. Key unique tests:
  - `test_insert_creates_bucket` — verifies bucket creation on insert
  - `test_query_spans_multiple_cells` — cross-cell query finding 3 objects
  - (Other tests have equivalents in target with different names — verify before discarding)
- [ ] Copy unique tests into appropriate classes in target file
- [ ] Adapt MockObject if needed (target's MockObject may already be compatible)
- [ ] Run `pytest tests/unit/systems/test_spatial.py -v` — all tests pass
- [ ] Delete `tests/unit/systems/test_spatial_extended.py`
- [ ] Run `pytest tests/ -n 12` — no regressions

**Notes:** Source has 13 tests, target has 11. Most overlap by function with different names. Carefully compare semantics, not just names.

### Task 3.2: Merge Collision System Tests [Medium]
**Source:** `tests/unit/systems/test_collision_system.py` (393 lines) — STILL EXISTS
**Target:** `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` (691 lines)
**Tests:** `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Read `tests/unit/engine/collision_edge_cases/conftest.py` for `collision_system` fixture
- [ ] Identify unique tests in source NOT already covered by target. Key candidates:
  - `test_beam_weapon_raycasting` — basic raycasting (may overlap with target's geometry tests)
  - `test_ramming_logic` — HP asymmetry cases (rammer < target, rammer > target)
  - `test_beam_weapon_tangent_hit` — discriminant == 0 edge case
  - `test_beam_weapon_target_behind_origin` — negative t values
  - `test_beam_weapon_origin_inside_target` — ray origin inside sphere
  - `test_ramming_no_logger` — `process_ramming(ships, logger=None)` doesn't raise
- [ ] Adapt tests to use `collision_system` fixture instead of inline `CollisionSystem()`
- [ ] Copy unique tests into target file
- [ ] Run `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py -v` — all tests pass
- [ ] Delete `tests/unit/systems/test_collision_system.py`
- [ ] Run `pytest tests/ -n 12` — no regressions

**Notes:** Source has 12 tests, target has 21. Target is much more comprehensive. Carefully check which source tests are truly unique vs covered by different-named target tests.

### Task 3.3: Merge AI Behavior Tests [DONE with recovery needed]
**Source:** `tests/unit/ai/test_ai_behaviors.py` — DELETED by PROJ-157
**Target:** `tests/unit/ai/test_behavior_units.py` (735+ lines)

- [x] Source file deleted (by PROJ-157)
- [x] 4 of 7 unique tests merged into `TestFormationBehaviorMigrated` class:
  - `test_formation_fixed_rotation_mode` (was `test_target_pos_fixed_rotation`)
  - `test_target_pos_relative_rotation`
  - `test_drift_logic_correction`
  - `test_velocity_sync`
- [ ] **3 tests NOT merged — see Task 3.0 for recovery**

**Notes:** Task 3.0 handles the recovery. Once 3.0 is done, this task is complete.

### Task 3.4: Merge Controllable Adapter Tests [Medium]
**Source 1:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` (232 lines) — STILL EXISTS
**Source 2:** `tests/unit/ai/controllable_interface/test_adapter_methods.py` (262 lines) — STILL EXISTS
**Target:** `tests/unit/ai/test_controllable_adapter_edge_cases.py` (475 lines)
**Keep untouched:** `tests/unit/ai/test_controllable_adapter.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v` then `pytest tests/ -n 12`

- [ ] Read both source files and target file fully
- [ ] Read `tests/unit/ai/controllable_interface/conftest.py` for fixture patterns
- [ ] Identify unique tests across both sources NOT in target. Key candidates:
  - `test_adapter_can_be_imported` — import check (may be trivial, consider skipping)
  - `test_adapter_exposes_underlying_ship` — `.ship` property access
  - `test_adapter_uses_interface_methods_not_direct_access` — ensures interface usage
  - `test_direct_attribute_access_raises_error` — validates no __getattr__ delegation
  - `test_direct_attribute_assignment_does_not_delegate` — assignment goes to adapter's __dict__
  - (Many other tests are duplicates of target with longer names — verify carefully)
- [ ] Adapt tests to use target's `mock_ship` fixture pattern
- [ ] Copy unique tests into target (add section comment: "# Migrated from controllable_interface/")
- [ ] Run `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v` — all tests pass
- [ ] Delete `tests/unit/ai/controllable_interface/test_adapter_basics.py`
- [ ] Delete `tests/unit/ai/controllable_interface/test_adapter_methods.py`
- [ ] Run `pytest tests/ -n 12` — no regressions

**Notes:** Sources have 39 tests combined, target has 51. Heavy overlap. ~5 truly unique tests in sources. The `controllable_interface/` directory cleanup happens in Phase 4.

### Task 3.5: Merge Evaluation Integration Tests [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (285 lines) — STILL EXISTS
**Target:** `tests/unit/ai/test_target_evaluator_edge_cases.py` (314 lines)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_edge_cases.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Read `tests/unit/ai/target_evaluator/conftest.py` for `ship`/`target` fixtures
- [ ] Identify unique tests in source NOT in target. Key unique tests:
  - `TestCustomStatHelpers` (2 tests) — custom HP percent and PDC arc functions
  - `TestDefaultStatHelpers` (3 tests) — `get_hp_percent()` and `is_in_pdc_arc()` from combat_utils
  - `TestThreatAssessment` (2 tests) — realistic multi-rule scenarios
  - `test_missing_weight_uses_zero`, `test_missing_factor_uses_one` — edge case defaults
  - `test_same_position_zero_distance` — zero distance edge case
  - `test_negative_weight`, `test_very_large_distance` — boundary tests
- [ ] Add import: `from game.ai.combat_utils import get_hp_percent, is_in_pdc_arc` (if needed)
- [ ] Adapt tests to use target's fixture patterns (mock_ship, mock_target, mock_stat_helpers)
- [ ] Copy unique tests into target (add section comments for each group)
- [ ] Run `pytest tests/unit/ai/test_target_evaluator_edge_cases.py -v` — all tests pass
- [ ] Delete `tests/unit/ai/target_evaluator/test_evaluation_integration.py`
- [ ] Verify `test_capabilities_cache.py` still passes: `pytest tests/unit/ai/target_evaluator/ -v`
- [ ] Run `pytest tests/ -n 12` — no regressions

**Notes:** Source has 16 tests, target has 20. ~12 unique tests in source to merge.

### Task 3.6: Merge Evaluation Rules Tests [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (598 lines) — STILL EXISTS
**Target:** `tests/unit/ai/test_target_evaluator_rules.py` (752 lines)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_rules.py -v` then `pytest tests/ -n 12`

**CRITICAL: This merge includes `TestSpeedRulesFactorBased` which documents a known bug. Preserve all test comments.**

- [ ] Read both source and target files fully
- [ ] Identify unique tests in source NOT in target. Key unique tests:
  - **Full `TestSpeedRulesFactorBased` class** (6 tests documenting speed factor bug with inverted results) — PRESERVE ALL COMMENTS
  - `test_nearest_with_factor`, `test_farthest_with_factor` — factor-specific distance tests
  - `test_distance_rule_applies_factor` — factor application test
  - `test_largest_same_as_mass`, `test_missing_mass_uses_default` — mass edge cases
  - `test_missing_velocity_uses_zero` — velocity edge case
  - `TestStrengthRules` (2 tests) — `test_strongest_uses_mass`, `test_weakest_uses_inverse_mass`
  - Various other factor/weight combination tests
- [ ] Merge full `TestSpeedRulesFactorBased` class with all bug-documenting comments intact
- [ ] Adapt to target's fixture patterns (mock_ship, mock_target, mock_stat_helpers)
- [ ] Run `pytest tests/unit/ai/test_target_evaluator_rules.py -v` — all tests pass (including migrated bug-doc tests)
- [ ] Delete `tests/unit/ai/target_evaluator/test_evaluation_rules.py`
- [ ] Verify `test_capabilities_cache.py` still passes: `pytest tests/unit/ai/target_evaluator/ -v`
- [ ] Run `pytest tests/ -n 12` — no regressions

**Notes:** Source has 44 tests, target has 58. ~12 unique tests in source. The `TestSpeedRulesFactorBased` class is the highest-priority merge item in the entire project.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All source files deleted (5 remaining + 3 recovered tests)
- [ ] All unique tests verified passing in target files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
