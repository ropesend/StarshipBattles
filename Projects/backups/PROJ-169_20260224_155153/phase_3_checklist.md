# Phase 3: Formation Editor Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate duplicate formation_editor.py, update all imports and config, fully remove Tools/ directory

---

## Tasks

### Task 3.1: Verify Game UI Version Is Authoritative [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** Read-only verification — no test run

- [x] Read `game/ui/screens/formation_editor.py` — confirm it contains `FormationEditorScreen` class
- [x] Read `Tools/formation_editor.py` — confirm it is the legacy standalone version
- [x] Confirm the game/ui/screens version is the more complete/refactored version
- [x] Note any classes/functions in Tools/ version that are NOT in game/ui/screens version (if any exist, they must be migrated before deletion)

**Notes:** game/ui/screens version (942 lines) is properly refactored with FormationRenderer/FormationInputHandler separation, type hints, tkinter_utils. Tools/ version (1056 lines) is legacy monolithic. No unique functionality in Tools/ version.

---

### Task 3.2: Update game/app.py Import [Simple]
**File:** `game/app.py` (line 22)
**Tests:** `pytest tests/ --testmon`

- [x] Read `game/app.py` to find the current import line
- [x] Change import from:
  ```python
  from Tools.formation_editor import FormationEditorScreen
  ```
  To:
  ```python
  from game.ui.screens.formation_editor import FormationEditorScreen
  ```
- [x] Verify no other imports from `Tools.formation_editor` exist in `game/app.py`

**Notes:** Import updated successfully.

---

### Task 3.3: Update Test Imports and Relocate Test File [Medium]
**File:** `tests/unit/builder/test_formation_editor_logic.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py` (before move), then `pytest tests/unit/ui/screens/test_formation_editor_logic.py` (after move)

- [x] Read `tests/unit/builder/test_formation_editor_logic.py` to understand its imports
- [x] Update imports to reference `game.ui.screens.formation_editor` instead of bare `formation_editor`
- [x] Move file: `tests/unit/builder/test_formation_editor_logic.py` -> `tests/unit/ui/screens/test_formation_editor_logic.py`
- [x] Ensure `tests/unit/ui/screens/` directory exists (create `__init__.py` if needed — check if sibling test dirs use one)
- [x] Verify moved test passes: `pytest tests/unit/ui/screens/test_formation_editor_logic.py`
- [x] Check if `tests/unit/builder/` is now empty — if so, delete it

**Notes:** Test relocated and passing. tests/unit/builder/ still has other tests, kept.

---

### Task 3.4: Delete Tools/formation_editor.py [Simple]
**File:** `Tools/formation_editor.py` (1,055 lines)
**Tests:** `pytest tests/ --testmon`

- [x] Delete `Tools/formation_editor.py`
- [x] Delete `Tools/README.md` if it exists and contains only references to deleted files
- [x] Verify `Tools/` directory is now completely empty
- [x] Delete `Tools/` directory entirely

**Notes:** Entire Tools/ directory deleted including formation_editor.py, README.md, and __pycache__.

---

### Task 3.5: Update pytest.ini Configuration [Simple]
**File:** `pytest.ini` (lines 3, 5)
**Tests:** `pytest tests/ -n 12`

- [x] Read `pytest.ini` to see current content
- [x] Line 5: Change `pythonpath = . Tools` to `pythonpath = .`
- [x] Line 3: Remove `--ignore=Tools` from addopts (no longer needed)
- [x] Verify no other references to `Tools` in pytest.ini

**Notes:** pytest.ini updated - removed --ignore=Tools and Tools from pythonpath.

---

### Task 3.6: Phase 3 Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All tests pass
- [x] Verify `Tools/` directory no longer exists
- [x] Verify `game/app.py` import works correctly
- [x] Commit Phase 3 changes

**Notes:** All 12023 tests passing, 1 skipped. Also fixed stale import in tests/unit/ui/test_scene_protocol.py.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
