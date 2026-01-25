# Phase 1: Delete Dead Directories and Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove files/directories confirmed as dead code with zero dependencies

---

## Tasks

### Task 1.1: Delete Marked Directories [Simple]
**Tests:** `python -c "from game.app import Game"` - verify no import errors

- [x] Delete `Marked_For_Deletion_2026-01-21_07-33/` directory (contains 95+ test artifacts)
- [x] Delete `MagicMock/` directory (contains 4 mock JSON files)
- [x] Verify: Run import check, no errors

**Notes:** Completed 2026-01-25. Both directories deleted successfully.

---

### Task 1.2: Delete Log Files [Simple]
**Tests:** Manual - game should still launch

- [x] Delete `battle.log` (~409KB)
- [x] Delete `combat_lab.log` (~108KB)
- [x] Delete `collect_log.txt` (~71KB)
- [x] Delete `collect_log_2.txt` (~302KB)
- [x] Delete `crash_log.txt` (~1.7KB)

**Notes:** Completed 2026-01-25. All 5 log files deleted.

---

### Task 1.3: Delete Debug Tools [Simple]
**File:** `Tools/` directory
**Tests:** `pytest tests/` - no tests should reference these files

Delete these 14 files:
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
- [x] `Tools/fix_modifiers.py` (superseded by v2)
- [x] `Tools/cleanup_pygame.py` (one-time executed)
- [x] `Tools/update_paths.py` (no-op template)

**WARNING:** DO NOT delete `Tools/formation_editor.py` - it's a production dependency!

**Notes:** Completed 2026-01-25. All 14 debug tools deleted. formation_editor.py preserved.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - all tests pass
- [x] Run `python -c "from game.app import Game"` - no import errors
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
