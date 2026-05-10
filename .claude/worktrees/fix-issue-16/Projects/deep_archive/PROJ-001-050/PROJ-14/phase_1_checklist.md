# Phase 1: Delete Directories and Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove all dead files and directories marked for deletion

---

## Tasks

### Task 1.1: Delete Marked Directories [Simple]
**Tests:** `pytest tests/ -x -q` after deletion (verify no import errors)

- [ ] Delete `Marked_For_Deletion_2026-01-21_07-33/` directory (45MB)
- [ ] Delete `MagicMock/` directory (4KB test artifacts)
- [ ] Verify: Run `pytest tests/ -x -q` - no import errors

**Notes:** [Filled during implementation]

---

### Task 1.2: Delete Log Files and Update .gitignore [Simple]
**File:** `.gitignore`
**Tests:** Visual verification

- [ ] Delete `battle.log` from repo root (if exists)
- [ ] Delete `combat_lab.log` from repo root (if exists)
- [ ] Delete `crash_log.txt` from repo root (if exists)
- [ ] Delete `collect_log.txt` from repo root (if exists)
- [ ] Delete `collect_log_2.txt` from repo root (if exists)
- [ ] Add to `.gitignore` after line 18:
  ```
  crash_log.txt
  collect_log*.txt
  ```
- [ ] Verify: `.gitignore` has new entries

**Notes:** Log files are actively created by app - will regenerate on next run. This is expected.

---

### Task 1.3: Delete Debug Tools [Simple]
**Directory:** `Tools/`
**Tests:** `pytest tests/ -x -q` after deletion

Delete the following files:
- [ ] `Tools/debug_automation.py`
- [ ] `Tools/debug_devastator.py`
- [ ] `Tools/debug_patch.py`
- [ ] `Tools/debug_test.py`
- [ ] `Tools/debug_test_clamping.py`
- [ ] `Tools/debug_ui_import.py`
- [ ] `Tools/reproduce_missile_issue.py`
- [ ] `Tools/reproduce_mock_error.py`
- [ ] `Tools/reproduce_seeker.py`
- [ ] `Tools/visual_test_beam_weapon.py`
- [ ] `Tools/visual_test_sprites.py`
- [ ] `Tools/fix_modifiers.py`
- [ ] `Tools/cleanup_pygame.py`
- [ ] `Tools/update_paths.py`
- [ ] Verify: Run `pytest tests/ -x -q` - no import errors

**Notes:** Keep `migrate_data.py`, `migrate_legacy_components.py`, `refactor_phase*.py`, `audit_components.py` - may be needed for reference.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - passes
- [ ] Run `python -c "from game.app import Game"` - no import errors
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
