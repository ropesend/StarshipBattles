# Phase 3: Code Hygiene Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-205 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix branching structure, move import, rename misleading comment.

---

## Tasks

### Task 3.1: Restructure AbilityManager branching [Medium]
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ability_manager.py tests/`

- [x] In `get_abilities()` method, restructure the if/else at lines 54-66:
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
- [x] Keep the `[KNOWN_ISSUE]` comment block - this is documented tech debt
- [x] Run ability manager tests
- [x] Run full test suite to verify no regressions

**Notes:** Changed `else:` to `elif target_class is not None:` so MRO walk only fires when isinstance fails for a provided target_class, not when iterating past non-matching abilities.

### Task 3.2: Move runtime import to module level [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [x] Move import from inside `calculate_modifier_stats()` (lines 50-53) to module level:
  ```python
  from game.simulation.components.modifiers import (
      apply_modifier_effects,
      get_default_stat_multipliers
  )
  ```
- [x] Verify no circular import: `python -c "from game.simulation.components.component_stats_calculator import ComponentStatsCalculator"`
- [x] Run tests

**Notes:** Import moved to module level successfully, no circular dependency.

### Task 3.3: Rename misleading AI behavior comment [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** No tests needed (comment-only change)

- [x] Change section header at line 406 from `TEST-SPECIFIC BEHAVIORS` to `UTILITY BEHAVIORS`
- [x] Verify no other references to "TEST-SPECIFIC" in the file

**Notes:** Comment updated. These behaviors are production code used by AIController.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/simulation/components/` passes (927 passed)
- [x] `pytest tests/ -n 12` full suite passes (12,831 passed, 1 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
