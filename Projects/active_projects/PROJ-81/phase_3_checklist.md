# Phase 3: Build Yards Panel Width

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-81 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Widen the Build Yards list panel from 280px to 700px. Target: 2560x1600 minimum display, optimized for 4K.

---

## Tasks

### Task 3.1: Increase Build Yards panel width [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test

Layout math at 2560px: Context(480) + QueueSelector(700) + BuildQueue(580) + DesignReport(750) + gaps(50) = 2560

- [ ] Change `panel_width = 280` to `panel_width = 700` in `_create_queue_selector_panel()` (line 261)
- [ ] Change `row_width = 260` to `row_width = 680` (line 299) to match new panel width minus margins
- [ ] Update build queue panel `panel_left` in `_create_build_queue_panel()` (line 438):
  - Change from `10 + 480 + 10 + 280 + 10` to `10 + 480 + 10 + 700 + 10` (= 1210)
- [ ] Verify at 2560px: All panels fit, Build Yards entries on one line, Build Queue has ~580px width
- [ ] Verify: Queue selector button text fits comfortably on one line

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Build Yards list is ~700px wide
- [ ] Queue entries fit on one line
- [ ] All panels fit within 2560px screen width
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
