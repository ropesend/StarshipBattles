# Phase 2: Transfer Dialog Size Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-100 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Increase transfer dialog window size to prevent UI clipping.

---

## Tasks

### Task 2.1: Increase dialog window size [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py`

- [ ] Line 299: Change `win_w, win_h = 600, 500` to `win_w, win_h = 750, 600`
- [ ] Verify: Buttons at bottom of dialog (`self.rect.height - 80`) auto-adjust since they reference `self.rect`
- [ ] Verify: Dropdown widths (`self.rect.width - 150`) auto-adjust
- [ ] Verify: Cancel button x-position (`self.rect.width - btn_w - padding - 30`) auto-adjusts
- [ ] Run: `pytest tests/unit/ui/screens/test_transfer_dialog.py -v`
- [ ] Run: `pytest tests/ --testmon`

**Notes:** The dialog layout uses `self.rect.width` and `self.rect.height` references, so increasing the constructor rect should automatically give more space to all elements. No changes to `transfer_dialog.py` itself should be needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
