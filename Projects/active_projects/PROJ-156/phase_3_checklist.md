# Phase 3: Merge Then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-156 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Merge unique tests from 8 source files into 6 target files, then delete sources. ~1,900 lines saved. Order: simplest to most complex.
**Priority:** High

---

## Tasks

### Task 3.1: Merge Spatial Tests [Simple]
**Source:** `tests/unit/systems/test_spatial_extended.py` (157 lines)
**Target:** `tests/unit/systems/test_spatial.py` (153 lines)
**Tests:** `pytest tests/unit/systems/test_spatial.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Identify 5 unique tests in source NOT present in target:
  - `test_query_radius_empty_grid` - empty grid returns `[]`
  - `test_same_cell_multiple_objects` - 3 objects in same bucket
  - `test_different_cells_different_buckets` - `len(grid.buckets) == 2`
  - `test_negative_coordinates_handled` - cell `(-1, -1)` bucket assignment
  - `test_query_spans_multiple_cells` - cross-cell query finding 3 objects
- [ ] Copy 5 unique tests into appropriate classes in target file
- [ ] Adapt MockObject if needed (target's MockObject may already be compatible)
- [ ] Run `pytest tests/unit/systems/test_spatial.py -v` - all tests pass
- [ ] Delete `tests/unit/systems/test_spatial_extended.py`
- [ ] Run `pytest tests/ -n 12` - no regressions

**Notes:**

### Task 3.2: Merge Collision System Tests [Medium]
**Source:** `tests/unit/systems/test_collision_system.py` (393 lines)
**Target:** `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` (691 lines)
**Tests:** `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Read `tests/unit/engine/collision_edge_cases/conftest.py` for `collision_system` fixture
- [ ] Identify 6 unique tests in source:
  - Beam near-miss geometry (aim offset by 21 units, radius 20)
  - `test_beam_weapon_tangent_hit` - discriminant == 0 edge case
  - `test_beam_weapon_target_behind_origin` - negative t values
  - `test_beam_weapon_origin_inside_target` - ray origin inside sphere
  - `test_ramming_logic` - HP asymmetry cases (rammer < target, rammer > target)
  - `test_ramming_no_logger` - `process_ramming(ships, logger=None)` doesn't raise
- [ ] Adapt tests to use `collision_system` fixture instead of inline `CollisionSystem()`
- [ ] Copy 6 unique tests into target file
- [ ] Run `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py -v` - all tests pass
- [ ] Delete `tests/unit/systems/test_collision_system.py`
- [ ] Run `pytest tests/ -n 12` - no regressions

**Notes:**

### Task 3.3: Merge AI Behavior Tests [Medium]
**Source:** `tests/unit/ai/test_ai_behaviors.py` (~341 lines)
**Target:** `tests/unit/ai/test_behavior_units.py` (735 lines)
**Tests:** `pytest tests/unit/ai/test_behavior_units.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Identify 7 unique tests in source (see design.md Pair 1 for list)
- [ ] **Adapt Vector2:** Source uses `pygame.math.Vector2`, target uses `game.core.math.Vector2`
- [ ] **Adapt fixtures:** Formation tests need master-ship mock setup; create or extend fixtures in target
- [ ] Copy 7 unique tests into target (add section comment: "# Migrated from test_ai_behaviors.py")
- [ ] Run `pytest tests/unit/ai/test_behavior_units.py -v` - all tests pass
- [ ] Delete `tests/unit/ai/test_ai_behaviors.py`
- [ ] Run `pytest tests/ -n 12` - no regressions

**Notes:**

### Task 3.4: Merge Controllable Adapter Tests [Medium]
**Source 1:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` (232 lines)
**Source 2:** `tests/unit/ai/controllable_interface/test_adapter_methods.py` (262 lines)
**Target:** `tests/unit/ai/test_controllable_adapter_edge_cases.py` (475 lines)
**Keep untouched:** `tests/unit/ai/test_controllable_adapter.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v` then `pytest tests/ -n 12`

- [ ] Read both source files and target file fully
- [ ] Read `tests/unit/ai/controllable_interface/conftest.py` for fixture patterns
- [ ] Identify ~7 unique tests across both sources (see design.md Pair 4 for list)
- [ ] Adapt tests to use target's `mock_ship` fixture pattern
- [ ] Copy unique tests into target (add section comment: "# Migrated from controllable_interface/")
- [ ] Run `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py -v` - all tests pass
- [ ] Delete `tests/unit/ai/controllable_interface/test_adapter_basics.py`
- [ ] Delete `tests/unit/ai/controllable_interface/test_adapter_methods.py`
- [ ] Run `pytest tests/ -n 12` - no regressions

**Notes:** The `controllable_interface/` directory cleanup happens in Phase 4 after test_interface_definition.py was already deleted in Phase 1.

### Task 3.5: Merge Evaluation Integration Tests [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (285 lines)
**Target:** `tests/unit/ai/test_target_evaluator_edge_cases.py` (314 lines)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_edge_cases.py -v` then `pytest tests/ -n 12`

- [ ] Read both source and target files fully
- [ ] Read `tests/unit/ai/target_evaluator/conftest.py` for `ship`/`target` fixtures
- [ ] Identify ~11 unique tests (see design.md Pair 3 for list)
- [ ] Add import: `from game.ai.combat_utils import get_hp_percent, is_in_pdc_arc` (if needed by merged tests)
- [ ] Adapt tests to use target's fixture patterns (mock_ship, mock_target, mock_stat_helpers)
- [ ] Copy unique tests into target (add section comments for each group)
- [ ] Run `pytest tests/unit/ai/test_target_evaluator_edge_cases.py -v` - all tests pass
- [ ] Delete `tests/unit/ai/target_evaluator/test_evaluation_integration.py`
- [ ] Verify `test_capabilities_cache.py` still passes: `pytest tests/unit/ai/target_evaluator/ -v`
- [ ] Run `pytest tests/ -n 12` - no regressions

**Notes:**

### Task 3.6: Merge Evaluation Rules Tests [Medium]
**Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (598 lines)
**Target:** `tests/unit/ai/test_target_evaluator_rules.py` (752 lines)
**Tests:** `pytest tests/unit/ai/test_target_evaluator_rules.py -v` then `pytest tests/ -n 12`

**CRITICAL: This merge includes `TestSpeedRulesFactorBased` which documents a known bug. Preserve all test comments.**

- [ ] Read both source and target files fully
- [ ] Identify ~11 unique tests (see design.md Pair 2 for full list)
- [ ] **Merge full `TestSpeedRulesFactorBased` class** (7 tests documenting speed factor bug with inverted results). Preserve ALL comments documenting the bug behavior.
- [ ] Merge additional unique tests: `test_nearest_zero_distance`, `test_largest_same_as_mass`, `test_missing_mass_uses_default`, `TestStrengthRules` (2 tests)
- [ ] Adapt to target's fixture patterns (mock_ship, mock_target, mock_stat_helpers)
- [ ] Run `pytest tests/unit/ai/test_target_evaluator_rules.py -v` - all tests pass (including migrated bug-doc tests)
- [ ] Delete `tests/unit/ai/target_evaluator/test_evaluation_rules.py`
- [ ] Verify `test_capabilities_cache.py` still passes: `pytest tests/unit/ai/target_evaluator/ -v`
- [ ] Run `pytest tests/ -n 12` - no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 6 source files deleted
- [ ] All unique tests verified passing in target files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
