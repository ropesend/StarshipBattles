# Phase 1: Dead Code Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-13 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code to reduce maintenance burden
**Priority:** QUICK WINS - Can do immediately

---

## Tasks

### Task 1.1: DC-02 - Delete Marked-For-Deletion Directories [Simple]
**Files:**
- `Marked_For_Deletion_2026-01-21_07-33/` (6 files)
- `Debugging/Marked_for_Deletion_2026-01-20/` (2 test files)

**Issue:** 106+ files in directories explicitly marked for deletion, never removed.

**Implementation:**
- [ ] Review contents briefly to ensure nothing valuable
- [ ] Run: `git rm -r Marked_For_Deletion_2026-01-21_07-33`
- [ ] Run: `git rm -r Debugging/Marked_for_Deletion_2026-01-20`
- [ ] Commit with message: "chore: Remove marked-for-deletion directories"
- [ ] Verify no broken imports

**Notes:** 5-minute task. Removes 106 files of repository clutter.

---

### Task 1.2: DC-01 - Delete Backup File [Simple]
**File:** `ui/test_lab_scene.py.backup` (2,731 lines, 107KB)

**Issue:** Large backup file tracked in repository. Should use git history instead.

**Implementation:**
- [ ] Verify file is truly a backup (compare with test_lab_scene.py)
- [ ] Run: `git rm ui/test_lab_scene.py.backup`
- [ ] Commit with message: "chore: Remove backup file, use git history"

**Notes:** 1-minute task. Reduces repository size.

---

### Task 1.3: DC-04/DC-05/DC-06 - Remove Commented Debug Code [Simple]
**Files:**
- `game/simulation/projectile_manager.py:86-87,93` - Commented log_debug
- `game/core/profiling.py:108` - Commented logger.debug
- `game/core/logger.py:38` - Commented StreamHandler

**Issue:** Commented-out debug statements clutter code.

**Implementation:**
- [ ] Remove commented code in projectile_manager.py
- [ ] Remove commented code in profiling.py
- [ ] Remove commented code in logger.py (document why console disabled if needed)
- [ ] Commit with message: "chore: Remove commented debug code"

**Notes:** 10-minute task across 3 files.

---

### Task 1.4: DC-03 - Document Empty __init__ Files [Medium]
**Files:** 11 empty `__init__.py` files

**Issue:** Empty package files provide no API documentation.

**Implementation:**
- [ ] Add `__all__` exports to key packages:
  - `game/simulation/__init__.py`
  - `game/strategy/__init__.py`
  - `game/ui/__init__.py`
- [ ] Add brief docstring explaining package purpose
- [ ] Consider if explicit imports would help IDE support

**Notes:** 30-minute task. Lower priority than deletions.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No marked-for-deletion directories
- [ ] No .backup files
- [ ] No commented debug code
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
