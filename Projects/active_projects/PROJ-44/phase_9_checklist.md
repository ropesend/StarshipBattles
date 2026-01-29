# Phase 9: Minor Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address remaining minor issues.

---

## Tasks

### Task 9.1: Fix Naming Inconsistencies [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Issue:** CQ-10 - Mix of naming conventions
**Tests:** `pytest tests/unit/ui/`

- [ ] Audit `fleet_report_window.py` lines 45-65 for consistent naming
- [ ] Document naming conventions in code style guide

**Notes:**

---

### Task 9.2: Remove Unused Parameters [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Issue:** CQ-11 - Methods with unused params
**Tests:** `pytest tests/unit/ui/`

- [ ] Audit `race_setup_screen.py` line 250 and similar
- [ ] Remove or document unused parameters

**Notes:**

---

### Task 9.3: Improve Single Letter Variables [Simple]
**Files:** `game/ui/screens/planet_list_window.py`, `game/ui/screens/race_setup_screen.py`
**Issue:** CQ-06 - Variables named `i`, `x`, `y` in complex logic
**Tests:** `pytest tests/unit/ui/`

- [ ] Replace in `planet_list_window.py` lines 156-157
- [ ] Replace in `race_setup_screen.py` lines 810-926
- [ ] Use descriptive names: `formation_index`, `x_pos`, `panel_width`

**Notes:**

---

### Task 9.4: Fix Constructor Parameter Overload [Simple]
**File:** `game/ui/screens/builder/structure_list_items.py`
**Issue:** AR-009 - UI components with 9+ constructor params
**Tests:** `pytest tests/unit/builder/`

- [ ] Create configuration dataclasses for `structure_list_items.py`
- [ ] Refactor `IndividualComponentItem`, `LayerHeaderItem`, `ComponentGroupItem`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` (full suite, NOT --testmon) - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Run final verification checklist from plan.md
