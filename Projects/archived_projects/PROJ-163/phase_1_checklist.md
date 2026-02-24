# Phase 1: Update refactor_loop Internal Paths

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-163 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all self-referencing paths inside `refactor_loop/` files so they reference `Projects/refactor_loop/` (the post-move location). Files are edited in-place before the actual move happens in Phase 4.

---

## Tasks

### Task 1.1: Update `refactor_loop/WORKER.md` [Simple]
**File:** `refactor_loop/WORKER.md`
**Find/Replace:** `refactor_loop/` → `Projects/refactor_loop/`

- [x] Line 21: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 72: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 102: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 118: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 195: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

**Notes:**

### Task 1.2: Update `refactor_loop/loop_runner.ps1` [Simple]
**File:** `refactor_loop/loop_runner.ps1`

- [x] Line 7: `$PLAN_FILE = "refactor_loop/refactor_plan.md"` → `"Projects/refactor_loop/refactor_plan.md"`
- [x] Line 86: `--system-prompt-file refactor_loop/WORKER.md` → `Projects/refactor_loop/WORKER.md`
- [x] Line 87: `Read refactor_loop/refactor_plan.md` → `Read Projects/refactor_loop/refactor_plan.md`
- [x] Line 102: `refactor_loop/refactor_plan.md execution log` → `Projects/refactor_loop/refactor_plan.md execution log`

**Notes:**

### Task 1.3: Update `refactor_loop/loop_runner.sh` [Simple]
**File:** `refactor_loop/loop_runner.sh`

- [x] Line 9: `PLAN_FILE="refactor_loop/refactor_plan.md"` → `"Projects/refactor_loop/refactor_plan.md"`
- [x] Line 73: comment `refactor_loop/WORKER.md` → `Projects/refactor_loop/WORKER.md`
- [x] Line 85: `--system-prompt-file refactor_loop/WORKER.md` → `Projects/refactor_loop/WORKER.md`
- [x] Line 86: `Read refactor_loop/refactor_plan.md` → `Read Projects/refactor_loop/refactor_plan.md`
- [x] Line 112: `refactor_loop/refactor_plan.md Agent Context` → `Projects/refactor_loop/refactor_plan.md Agent Context`

**Notes:**

### Task 1.4: Update `refactor_loop/REFACTOR_LOOP_README.md` [Medium]
**File:** `refactor_loop/REFACTOR_LOOP_README.md`

- [x] Global find-replace: all `refactor_loop/` → `Projects/refactor_loop/` (25+ occurrences)
- [x] Verify directory structure diagram (lines 61-79) updated correctly
- [x] Verify command examples updated (e.g., `.\loop_runner.ps1` → `.\Projects\refactor_loop\loop_runner.ps1`)
- [x] Verify the files reference table (lines 341-344) updated correctly
- [x] Check for no double-prefixing (`Projects/Projects/refactor_loop/`)
**Notes:** Also updated 4 bare `./loop_runner.sh` references to `./Projects/refactor_loop/loop_runner.sh`

**Notes:**

### Task 1.5: Verify Phase 1 [Simple]
- [x] Search `refactor_loop/` within all 4 modified files - confirm zero remaining old-path occurrences that aren't prefixed with `Projects/`
- [x] No double-prefixing exists

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
