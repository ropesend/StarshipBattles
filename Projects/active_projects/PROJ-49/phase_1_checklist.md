# Phase 1: Dead Code Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove confirmed dead code and duplicates, clean repository artifacts

---

## Tasks

### Task 1.1: Archive Duplicate ProjectileManager [Simple]
**File:** `game/simulation/systems/projectile_manager.py`
**Tests:** `pytest tests/unit/combat/test_projectile_manager.py`

- [ ] Verify no imports exist for `game.simulation.systems.projectile_manager` (grep confirms none)
- [ ] Create directory `_marked_for_deletion_2026-01-28/` if not exists
- [ ] Move file to `_marked_for_deletion_2026-01-28/projectile_manager_systems.py`
- [ ] Run tests to confirm no breakage

**Notes:** [Filled during implementation]

---

### Task 1.2: Archive Dead BattleSetupScreen [Simple]
**File:** `game/ui/screens/setup.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Verify `game/app.py` imports from `setup_screen.py` not `setup.py` (line 25)
- [ ] Move `setup.py` to `_marked_for_deletion_2026-01-28/setup_screen_old.py`
- [ ] Run UI tests to confirm no breakage

**Notes:** [Filled during implementation]

---

### Task 1.3: Remove _ValidatorProxy Dead Code [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [ ] Remove lines 29-34 (`_ValidatorProxy` class and `VALIDATOR = _ValidatorProxy()`)
- [ ] Verify no references to `VALIDATOR` constant exist (grep confirms none)
- [ ] Run ship entity tests

**Notes:** [Filled during implementation]

---

### Task 1.4: Archive Backup File [Simple]
**File:** `ui/test_lab_scene.py.backup`
**Tests:** None needed

- [ ] Move `ui/test_lab_scene.py.backup` to `_marked_for_deletion_2026-01-28/`
- [ ] Verify `ui/test_lab_scene.py` (active version) still exists

**Notes:** [Filled during implementation]

---

### Task 1.5: Clean Marked-for-Deletion Directory [Simple]
**File:** `_marked_for_deletion_2026-01-27/`
**Tests:** None needed

- [ ] Review contents of `_marked_for_deletion_2026-01-27/` for anything to preserve
- [ ] Delete entire `_marked_for_deletion_2026-01-27/` directory
- [ ] Verify `_marked_for_deletion_2026-01-28/` exists for this project's archived code

**Notes:** [Filled during implementation]

---

### Task 1.6: Update .gitignore for __pycache__ [Simple]
**File:** `.gitignore`
**Tests:** None needed

- [ ] Verify `__pycache__/` is in `.gitignore`
- [ ] If not present, add `__pycache__/` and `*.pyc` patterns
- [ ] Remove any tracked `__pycache__` directories: `git rm -r --cached **/__pycache__`

**Notes:** [Filled during implementation]

---

### Task 1.7: Resolve Duplicate Panel Implementations [Medium]
**Files:** `game/ui/hud/panels.py`, `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Trace imports: `battle.py` imports from `hud/panels.py`, `battle_screen.py` imports from `panels/battle_panels.py`
- [ ] Run application and check which panels are actually displayed in battle
- [ ] Determine which screen is active (likely battle_screen.py based on PROJ-43 refactoring)
- [ ] If `hud/panels.py` is unused, archive to `_marked_for_deletion_2026-01-28/`
- [ ] Update any remaining imports to use canonical location
- [ ] Run UI tests

**Notes:** May need additional investigation - both files appear to be imported

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
