# Phase 6: Exception Chaining Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `from e` to 3 re-raise patterns that lose the original traceback.
**Estimated Effort:** 15 min

**Note:** Some of these may have already been fixed during Phases 3-4. Verify each before changing.

---

## Tasks

### Task 6.1: battle_state_manager.py chaining [Simple]
**File:** `game/simulation/managers/battle_state_manager.py`
**Tests:** `pytest tests/unit/simulation/managers/test_battle_state_manager.py`

- [ ] Line 79 (approx): Verify the re-raise uses `from e`. If already fixed in Phase 3 Task 3.2, mark as done.
- [ ] If not: change `raise ValidationException(...)` → `raise ValidationException(...) from e`
- [ ] Verify: `pytest tests/unit/simulation/managers/test_battle_state_manager.py`

**Notes:** May already be done in Phase 3.

### Task 6.2: abilities/base.py chaining [Simple]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_ability_base.py`

- [ ] Line 98 (approx): Verify the re-raise uses `from e`. If already fixed in Phase 3 Task 3.3, mark as done.
- [ ] If not: change `raise ValidationException(...)` → `raise ValidationException(...) from e`
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_ability_base.py`

**Notes:** May already be done in Phase 3.

### Task 6.3: density_map.py chaining [Simple]
**File:** `game/strategy/generation/density/density_map.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`

- [ ] Line 208 (approx): Verify the re-raise uses `from e`. If already fixed in Phase 3 Task 3.16, mark as done.
- [ ] If not: change `raise ValidationException(...)` → `raise ValidationException(...) from e`
- [ ] Verify: `pytest tests/unit/strategy/generation/density/test_density_map.py`

**Notes:** May already be done in Phase 3.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 3 re-raise locations use `from e`
- [ ] `pytest tests/unit/simulation/managers/ tests/unit/simulation/components/abilities/ tests/unit/strategy/generation/density/` all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
