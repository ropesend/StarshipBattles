# Phase 4: UI Display Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-97 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update UI components that display build_rate as a scalar

---

## Tasks

### Task 4.1: Update build_queue_selector.py display [Simple]
**File:** `game/ui/screens/build_queue_selector.py` (line 102)
**Tests:** Manual visual check

- [ ] Change `int(source.build_rate)` to display summary (e.g., `max(source.build_rate.values())` if all rates equal, or "varies" if different)
- [ ] Example: `f"{max(source.build_rate.values()):.0f}/turn"` when all rates are equal

**Notes:**

### Task 4.2: Update empire_build_queue_window.py build_rate column [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py` (line 549)
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Change `f"{int(source.build_rate)}/turn"` to handle dict (same logic as 4.1)

**Notes:**

### Task 4.3: Update UI tests [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`, `tests/unit/ui/screens/test_empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Update test at line 475 (build rate column test): mock `source.build_rate` as dict
- [ ] Update formatter test at line 34: `source.build_rate = 10` → `source.build_rate = {"Metals": 10}`
- [ ] Verify all empire build queue window tests pass with dict build_rate

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
