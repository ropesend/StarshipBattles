# Phase 3: Code Hygiene Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-205 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix branching structure, move import, rename misleading comment.

---

## Tasks

### Task 3.1: Restructure AbilityManager branching [Medium]
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ability_manager.py tests/`

- [ ] In `get_abilities()` method, restructure the if/else at lines 54-66:
  ```python
  # Current (problematic - MRO walk runs for every non-match):
  if target_class and isinstance(ab, target_class):
      found.append(ab)
  else:
      for cls in ab.__class__.mro():
          ...

  # Fixed (MRO walk only runs as fallback for identity drift):
  if target_class and isinstance(ab, target_class):
      found.append(ab)
  elif target_class is not None:
      # [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
      for cls in ab.__class__.mro():
          if cls.__name__ == ability_name:
              found.append(ab)
              break
  ```
- [ ] Keep the `[KNOWN_ISSUE]` comment block - this is documented tech debt
- [ ] Run ability manager tests
- [ ] Run full test suite to verify no regressions

**Notes:** The key change is adding `elif target_class is not None:` so the MRO walk ONLY fires when we had a target_class but isinstance failed (identity drift), not when iterating past non-matching abilities.

### Task 3.2: Move runtime import to module level [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [ ] Move import from inside `calculate_modifier_stats()` (lines 50-53) to module level:
  ```python
  from game.simulation.components.modifiers import (
      apply_modifier_effects,
      get_default_stat_multipliers
  )
  ```
- [ ] Verify no circular import: `python -c "from game.simulation.components.component_stats_calculator import ComponentStatsCalculator"`
- [ ] Run tests

**Notes:** Verified no circular dependency - `modifiers.py` only imports `logging`.

### Task 3.3: Rename misleading AI behavior comment [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** No tests needed (comment-only change)

- [ ] Change section header at line 406 from `TEST-SPECIFIC BEHAVIORS` to `UTILITY BEHAVIORS`
- [ ] Verify no other references to "TEST-SPECIFIC" in the file

**Notes:** These behaviors are instantiated in every AIController and selectable via strategy data.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/simulation/components/` passes
- [ ] `pytest tests/ -n 12` full suite passes (baseline: 12,743+ passed, 0 failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
