# Phase 3: Formation Editor Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate duplicate formation_editor.py, update all imports and config, fully remove Tools/ directory

---

## Tasks

### Task 3.1: Verify Game UI Version Is Authoritative [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** Read-only verification — no test run

- [ ] Read `game/ui/screens/formation_editor.py` — confirm it contains `FormationEditorScreen` class
- [ ] Read `Tools/formation_editor.py` — confirm it is the legacy standalone version
- [ ] Confirm the game/ui/screens version is the more complete/refactored version
- [ ] Note any classes/functions in Tools/ version that are NOT in game/ui/screens version (if any exist, they must be migrated before deletion)

**Notes:**

---

### Task 3.2: Update game/app.py Import [Simple]
**File:** `game/app.py` (line 22)
**Tests:** `pytest tests/ --testmon`

- [ ] Read `game/app.py` to find the current import line
- [ ] Change import from:
  ```python
  from Tools.formation_editor import FormationEditorScreen
  ```
  To:
  ```python
  from game.ui.screens.formation_editor import FormationEditorScreen
  ```
- [ ] Verify no other imports from `Tools.formation_editor` exist in `game/app.py`

**Notes:**

---

### Task 3.3: Update Test Imports and Relocate Test File [Medium]
**File:** `tests/unit/builder/test_formation_editor_logic.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py` (before move), then `pytest tests/unit/ui/screens/test_formation_editor_logic.py` (after move)

- [ ] Read `tests/unit/builder/test_formation_editor_logic.py` to understand its imports
- [ ] Update imports to reference `game.ui.screens.formation_editor` instead of bare `formation_editor`
- [ ] Move file: `tests/unit/builder/test_formation_editor_logic.py` -> `tests/unit/ui/screens/test_formation_editor_logic.py`
- [ ] Ensure `tests/unit/ui/screens/` directory exists (create `__init__.py` if needed — check if sibling test dirs use one)
- [ ] Verify moved test passes: `pytest tests/unit/ui/screens/test_formation_editor_logic.py`
- [ ] Check if `tests/unit/builder/` is now empty — if so, delete it

**Notes:**

---

### Task 3.4: Delete Tools/formation_editor.py [Simple]
**File:** `Tools/formation_editor.py` (1,055 lines)
**Tests:** `pytest tests/ --testmon`

- [ ] Delete `Tools/formation_editor.py`
- [ ] Delete `Tools/README.md` if it exists and contains only references to deleted files
- [ ] Verify `Tools/` directory is now completely empty
- [ ] Delete `Tools/` directory entirely

**Notes:**

---

### Task 3.5: Update pytest.ini Configuration [Simple]
**File:** `pytest.ini` (lines 3, 5)
**Tests:** `pytest tests/ -n 12`

- [ ] Read `pytest.ini` to see current content
- [ ] Line 5: Change `pythonpath = . Tools` to `pythonpath = .`
- [ ] Line 3: Remove `--ignore=Tools` from addopts (no longer needed)
- [ ] Verify no other references to `Tools` in pytest.ini

**Notes:**

---

### Task 3.6: Phase 3 Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass
- [ ] Verify `Tools/` directory no longer exists
- [ ] Verify `game/app.py` import works correctly
- [ ] Commit Phase 3 changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
