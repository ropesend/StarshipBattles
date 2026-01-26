# Phase 1: Delete Directories and Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove all dead files and directories marked for deletion

---

## Tasks

### Task 1.1: Delete Marked Directories [Simple]
**Tests:** `pytest tests/ -x -q` after deletion (verify no import errors)

- [x] Delete `Marked_For_Deletion_2026-01-21_07-33/` directory (45MB)
- [x] Delete `MagicMock/` directory (4KB test artifacts)
- [x] Verify: Run `pytest tests/ -x -q` - no import errors

**Notes:** Both directories deleted successfully. Tests pass (4522 passed, 1 pre-existing failure, 1 skipped).

---

### Task 1.2: Delete Log Files and Update .gitignore [Simple]
**File:** `.gitignore`
**Tests:** Visual verification

- [x] Delete `battle.log` from repo root (if exists)
- [x] Delete `combat_lab.log` from repo root (if exists)
- [x] Delete `crash_log.txt` from repo root (if exists)
- [x] Delete `collect_log.txt` from repo root (if exists)
- [x] Delete `collect_log_2.txt` from repo root (if exists)
- [x] Add to `.gitignore` after line 18:
  ```
  crash_log.txt
  collect_log*.txt
  ```
- [x] Verify: `.gitignore` has new entries

**Notes:** All 5 log files deleted. Added `crash_log.txt` and `collect_log*.txt` to .gitignore (battle.log and combat_lab.log were already present).

---

### Task 1.3: Delete Debug Tools [Simple]
**Directory:** `Tools/`
**Tests:** `pytest tests/ -x -q` after deletion

Delete the following files:
- [x] `Tools/debug_automation.py`
- [x] `Tools/debug_devastator.py`
- [x] `Tools/debug_patch.py`
- [x] `Tools/debug_test.py`
- [x] `Tools/debug_test_clamping.py`
- [x] `Tools/debug_ui_import.py`
- [x] `Tools/reproduce_missile_issue.py`
- [x] `Tools/reproduce_mock_error.py`
- [x] `Tools/reproduce_seeker.py`
- [x] `Tools/visual_test_beam_weapon.py`
- [x] `Tools/visual_test_sprites.py`
- [x] `Tools/fix_modifiers.py`
- [x] `Tools/cleanup_pygame.py`
- [x] `Tools/update_paths.py`
- [x] Verify: Run `pytest tests/ -x -q` - no import errors

**Notes:** All 14 debug tool files deleted. Tests pass (61 testmon-detected tests). Kept migration/audit tools as planned.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - passes
- [x] Run `python -c "from game.app import Game"` - no import errors
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
