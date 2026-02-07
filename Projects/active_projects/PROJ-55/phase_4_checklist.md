# Phase 4: Update External References

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix all imports and patch paths that referenced the old `game.ui.screens.test_lab_screen` module path

---

## Tasks

### Task 4.1: Update game/app.py [Simple]
**File:** `game/app.py`
**Tests:** `python -c "from game.app import Game"` (or `pytest tests/ -x -q`)

- [ ] Line 30: Change `from game.ui.screens.test_lab_screen import TestLabScreen` to `from game.ui.screens.test_lab import TestLabScreen`

**Notes:**

### Task 4.2: Update test_data_paths.py imports [Medium]
**File:** `tests/unit/test_lab/test_data_paths.py`
**Tests:** `pytest tests/unit/test_lab/test_data_paths.py -v`

Import updates (5 instances of `TestLabScreen`):
- [ ] Line 47: `from game.ui.screens.test_lab_screen import TestLabScreen` -> `from game.ui.screens.test_lab import TestLabScreen`
- [ ] Line 134: Same change
- [ ] Line 180: Same change
- [ ] Line 219: Same change

Import updates (2 instances of `get_test_data_dir`):
- [ ] Line 255: `from game.ui.screens.test_lab_screen import get_test_data_dir` -> `from game.ui.screens.test_lab.screen import get_test_data_dir`
- [ ] Line 274: Same change

Patch path updates (5 `load_json` patches):
- [ ] Line 80: `patch('game.ui.screens.test_lab_screen.load_json'...)` -> `patch('game.ui.screens.test_lab.screen.load_json'...)`
- [ ] Line 118: Same change
- [ ] Line 158: Same change
- [ ] Line 196: Same change
- [ ] Line 238: Same change

Patch path updates (2 `JSONPopup` patches):
- [ ] Line 159: `patch('game.ui.screens.test_lab_screen.JSONPopup')` -> `patch('game.ui.screens.test_lab.screen.JSONPopup')`
- [ ] Line 197: Same change

Patch path updates (4 `WIDTH`/`HEIGHT` patches):
- [ ] Line 160: `patch('game.ui.screens.test_lab_screen.WIDTH', 1920)` -> `patch('game.ui.screens.test_lab.screen.WIDTH', 1920)`
- [ ] Line 161: `patch('game.ui.screens.test_lab_screen.HEIGHT', 1080)` -> `patch('game.ui.screens.test_lab.screen.HEIGHT', 1080)`
- [ ] Line 198: Same as line 160
- [ ] Line 199: Same as line 161

**Notes:** Use `replace_all` for the common prefix change where appropriate.

### Task 4.3: Update test_visual_run.py imports [Simple]
**File:** `tests/unit/test_lab/test_visual_run.py`
**Tests:** `pytest tests/unit/test_lab/test_visual_run.py -v`

Import update:
- [ ] Line 78: `from game.ui.screens.test_lab_screen import TestLabScreen` -> `from game.ui.screens.test_lab import TestLabScreen`

Patch path updates (7 `TestRunner` patches):
- [ ] Line 93: `patch('game.ui.screens.test_lab_screen.TestRunner')` -> `patch('game.ui.screens.test_lab.screen.TestRunner')`
- [ ] Line 104: Same change
- [ ] Line 115: Same change
- [ ] Line 127: Same change
- [ ] Line 139: Same change
- [ ] Line 151: Same change
- [ ] Line 166: Same change

**Notes:** Use `replace_all` for `game.ui.screens.test_lab_screen.TestRunner` -> `game.ui.screens.test_lab.screen.TestRunner`

### Task 4.4: Run targeted test suites [Simple]
**Tests:** Verify all affected tests pass

- [ ] `pytest tests/unit/test_lab/ -v` — all test_lab tests pass
- [ ] `pytest tests/unit/ui/test_lab_scene/ -v` — UI component tests pass (should be unaffected)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All imports updated (1 production + 7 test imports)
- [ ] All 18 patch paths updated
- [ ] All targeted tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
