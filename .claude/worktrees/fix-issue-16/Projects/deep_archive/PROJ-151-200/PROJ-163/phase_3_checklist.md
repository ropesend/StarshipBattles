# Phase 3: Update All External References

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-163 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update every file outside `refactor_loop/` and `continuous_loop/` that references either directory path.

---

## Tasks

### Task 3.1: Update `CLAUDE.md` [Simple]
**File:** `CLAUDE.md`

- [x] Line 5: `refactor_loop/WORKER.md` → `Projects/refactor_loop/WORKER.md`

**Notes:**

### Task 3.2: Update `Projects/scripts/trigger_audit.py` [Simple]
**File:** `Projects/scripts/trigger_audit.py`

- [x] Line 103: `Path("refactor_loop/refactor_plan.md")` → `Path("Projects/refactor_loop/refactor_plan.md")`

**Notes:**

### Task 3.3: Update `Projects/protocols/` [Simple]
**Files:**
- `Projects/protocols/08_automated_loop_protocol.md`
  - [x] Line 11: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
  - [x] Line 12: `continuous_loop/cycle_plan.md` → `Projects/continuous_loop/cycle_plan.md`
- `Projects/protocols/10_manage_refactor_plan.md`
  - [x] Line 3: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

**Notes:**

### Task 3.4: Update `Projects/Prompts/Manage Refactor Plan.txt` [Simple]
**File:** `Projects/Prompts/Manage Refactor Plan.txt`

- [x] Line 3: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

**Notes:**

### Task 3.5: Update `.claude/skills/` (5 files) [Simple]
**Files:**

#### `.claude/skills/reset-baseline/SKILL.md`
- [x] Line 10: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 28: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 73: `.\refactor_loop\loop_runner.ps1` → `.\Projects\refactor_loop\loop_runner.ps1`

#### `.claude/skills/manage-refactor-plan/SKILL.md`
- [x] Line 3: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 16: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### `.claude/skills/archive-project/SKILL.md`
- [x] Line 20: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 39: `refactor_loop/archive.md` → `Projects/refactor_loop/archive.md`
- [x] Line 49: `refactor_loop/archive.md` → `Projects/refactor_loop/archive.md`
- [x] Line 50: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 54: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### `.claude/skills/add-to-plan/SKILL.md`
- [x] Line 10: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 24: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### `.claude/skills/sweep-all/SKILL.md`
- [x] Line 21: exclusion `refactor_loop/` → `Projects/refactor_loop/`

**Notes:**

### Task 3.6: Update `.agent/skills/` (4 files) [Simple]
**Files:**

#### `.agent/skills/reset-baseline/SKILL.md`
- [x] Line 18: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 20: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### `.agent/skills/manage-refactor-plan/SKILL.md`
- [x] Line 3: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 10: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 21: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### `.agent/skills/archive-project/SKILL.md`
- [x] Line 12: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 18: `refactor_loop/archive.md` → `Projects/refactor_loop/archive.md`
- [x] Line 19: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 21: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

#### `.agent/skills/add-to-plan/SKILL.md`
- [x] Line 8: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 16: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`
- [x] Line 37: `refactor_loop/refactor_plan.md` → `Projects/refactor_loop/refactor_plan.md`

**Notes:**

### Task 3.7: Update `Reviews/Prompts/Sweep - *.txt` (5 files) [Simple]
**Files:** Update exclusion lists - `refactor_loop/` → `Projects/refactor_loop/`

- [x] `Reviews/Prompts/Sweep - Duplication.txt` line 12
- [x] `Reviews/Prompts/Sweep - Legacy Holdovers.txt` line 23
- [x] `Reviews/Prompts/Sweep - Consistency Violations.txt` line 23
- [x] `Reviews/Prompts/Sweep - Architecture Drift.txt` line 32
- [x] `Reviews/Prompts/Sweep - Test Coverage Gaps.txt` line 20

**Notes:**

### Task 3.8: Verify all external references [Simple]
- [x] Grep entire repo for bare `refactor_loop/` (not preceded by `Projects/`) excluding `Reviews/results/`, `continuous_loop/logs/`, and `.git/`
- [x] Grep entire repo for bare `continuous_loop/` (not preceded by `Projects/`) excluding same dirs
- [x] Confirm every remaining hit is in an excluded historical file (zero hits found)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
