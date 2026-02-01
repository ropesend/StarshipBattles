# Phase 1: Dead Code Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove confirmed dead code and duplicates, clean repository artifacts

---

## Tasks

### Task 1.1: Archive Duplicate ProjectileManager [Simple]
**File:** `game/simulation/systems/projectile_manager.py`
**Tests:** `pytest tests/unit/combat/test_projectile_manager.py`

- [x] Verify no imports exist for `game.simulation.systems.projectile_manager` (grep confirms none)
- [x] Create directory `_marked_for_deletion_2026-01-28/` if not exists
- [x] Move file to `_marked_for_deletion_2026-01-28/projectile_manager_systems.py`
- [x] Run tests to confirm no breakage

**Notes:** Confirmed no imports exist. File archived successfully.

---

### Task 1.2: Archive Dead BattleSetupScreen [Simple]
**File:** `game/ui/screens/setup.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Verify `game/app.py` imports from `setup_screen.py` not `setup.py` (line 25)
- [x] Move `setup.py` to `_marked_for_deletion_2026-01-28/setup_screen_old.py`
- [x] Run UI tests to confirm no breakage

**Notes:** Confirmed app.py imports from setup_screen.py (line 26). setup.py had no imports. Archived.

---

### Task 1.3: Remove _ValidatorProxy Dead Code [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [x] Remove lines 29-34 (`_ValidatorProxy` class and `VALIDATOR = _ValidatorProxy()`)
- [x] Verify no references to `VALIDATOR` constant exist (grep confirms none)
- [x] Run ship entity tests

**Notes:** Only references were comments. Removed class and constant. 19 ship tests pass.

---

### Task 1.4: Archive Backup File [Simple]
**File:** `ui/test_lab_scene.py.backup`
**Tests:** None needed

- [x] Move `ui/test_lab_scene.py.backup` to `_marked_for_deletion_2026-01-28/`
- [x] Verify `ui/test_lab_scene.py` (active version) still exists

**Notes:** File did not exist - already cleaned up previously. Skipped.

---

### Task 1.5: Clean Marked-for-Deletion Directory [Simple]
**File:** `_marked_for_deletion_2026-01-27/`
**Tests:** None needed

- [x] Review contents of `_marked_for_deletion_2026-01-27/` for anything to preserve
- [x] Delete entire `_marked_for_deletion_2026-01-27/` directory
- [x] Verify `_marked_for_deletion_2026-01-28/` exists for this project's archived code

**Notes:** Contained legacy refactoring protocols and reports. No active code. Deleted.

---

### Task 1.6: Update .gitignore for __pycache__ [Simple]
**File:** `.gitignore`
**Tests:** None needed

- [x] Verify `__pycache__/` is in `.gitignore`
- [x] If not present, add `__pycache__/` and `*.pyc` patterns
- [x] Remove any tracked `__pycache__` directories: `git rm -r --cached **/__pycache__`

**Notes:** Already configured correctly. No __pycache__ tracked in git.

---

### Task 1.7: Resolve Duplicate Panel Implementations [Medium]
**Files:** `game/ui/hud/panels.py`, `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Trace imports: `battle.py` imports from `hud/panels.py`, `battle_screen.py` imports from `panels/battle_panels.py`
- [x] Run application and check which panels are actually displayed in battle
- [x] Determine which screen is active (likely battle_screen.py based on PROJ-43 refactoring)
- [x] If `hud/panels.py` is unused, archive to `_marked_for_deletion_2026-01-28/`
- [x] Update any remaining imports to use canonical location
- [x] Run UI tests

**Notes:** Traced imports: app.py uses battle_scene.py which uses battle_screen.py which uses panels/battle_panels.py. hud/battle.py and hud/panels.py have NO imports anywhere in code - both are dead. Archived both files.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
