# Phase 2: Simple Performance Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Quick performance wins with minimal risk

---

## Tasks

### Task 2.1: Fix Projectile List Reconstruction [Simple]
**File:** `game/simulation/projectile_manager.py:137-138`
**Tests:** `pytest tests/unit/combat/test_projectile_manager.py`

- [x] Replace list comprehension rebuild with in-place mark-and-sweep
- [x] Run projectile manager tests
- [x] Run integration combat tests

**Notes:** Implemented in-place mark-and-sweep algorithm that avoids creating a new list. Uses write_idx/read_idx pattern with final truncation via `del self.projectiles[write_idx:]`.

---

### Task 2.2: Build Ability Index at Instantiation [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py tests/unit/refactor/`

- [x] Add `_ability_index: Dict[str, List[Ability]] = {}` to Component.__init__
- [x] Build index in `_instantiate_abilities()` after creating ability_instances
- [x] Update `get_abilities()` to use index with polymorphic fallback
- [x] Update `get_ability()` and `has_ability()` for consistency
- [x] Run component tests (303 tests pass)
- [x] Verify no behavior changes in ability lookups

**Notes:** Index built at end of `_instantiate_abilities()`, includes all MRO class names for polymorphic lookup. Fast O(1) lookup for ability names, falls back to AbilityManager for edge cases.

---

### Task 2.3: Pre-calculate Distances for Targeting [Simple]
**File:** `game/ai/target_evaluator.py`, `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/` (228 tests pass)

- [x] Add `distance_cache` optional parameter to `TargetEvaluator.evaluate()`
- [x] In `controller.py:_score_and_sort_enemies()` pre-calculate distances for all enemies
- [x] Update distance-based rules ('nearest', 'farthest', 'distance') to use cache if available
- [x] Run AI targeting tests

**Notes:** Distance cache built once per scoring pass, avoids redundant distance calculations when multiple rules reference distance.

---

### Task 2.4: Use Shallow Copies Where Safe [Simple]
**File:** `game/simulation/components/component.py:91, 134`
**Tests:** `pytest tests/unit/entities/test_component*.py`

- [x] Analyze line 126 `self.data = copy.deepcopy(data)`:
  - **Finding:** deepcopy REQUIRED - data contains nested mutable structures (abilities dict with lists and sub-dicts). Shallow copy would cause shared references, breaking clone() and modifier isolation.
- [x] Analyze line 166 `self.base_abilities = copy.deepcopy(self.abilities)`:
  - **Finding:** deepcopy REQUIRED - abilities dict has nested mutable values (ResourceConsumption lists, ability config dicts). Used to restore original state after runtime modifications.
- [x] Document analysis in code comments
- [x] Run component tests to verify no changes needed

**Notes:** Both deepcopies are necessary for correctness. Added PERF-ANALYSIS comments explaining why shallow copy would break functionality.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/` - 5745 passed (same as baseline)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
