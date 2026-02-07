# Phase 4: Update External References

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-57 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix all imports and patch paths that referenced the old `game.ui.screens.test_lab_screen` module path

---

## Tasks

### Task 4.1: Update game/app.py [Simple]
**File:** `game/app.py`
**Tests:** `python -c "from game.app import Game"` (or `pytest tests/ -x -q`)

- [x] Line 30: Change `from game.ui.screens.test_lab_screen import TestLabScreen` to `from game.ui.screens.test_lab import TestLabScreen`

**Notes:** Done

### Task 4.2: Update test_data_paths.py imports [Medium]
**File:** `tests/unit/test_lab/test_data_paths.py`
**Tests:** `pytest tests/unit/test_lab/test_data_paths.py -v`

Import updates (4 instances of `TestLabScreen`):
- [x] Line 47: `from game.ui.screens.test_lab_screen import TestLabScreen` -> `from game.ui.screens.test_lab import TestLabScreen`
- [x] Line 134: Same change
- [x] Line 180: Same change
- [x] Line 219: Same change

Import updates (2 instances of `get_test_data_dir`):
- [x] Line 255: `from game.ui.screens.test_lab_screen import get_test_data_dir` -> `from game.ui.screens.test_lab.screen import get_test_data_dir`
- [x] Line 274: Same change

Patch path updates (5 `load_json` patches):
- [x] Line 80: `patch('game.ui.screens.test_lab_screen.load_json'...)` -> `patch('game.ui.screens.test_lab.screen.load_json'...)`
- [x] Line 118: Same change
- [x] Line 158: Same change
- [x] Line 196: Same change
- [x] Line 238: Same change

Patch path updates (2 `JSONPopup` patches):
- [x] Line 159: `patch('game.ui.screens.test_lab_screen.JSONPopup')` -> `patch('game.ui.screens.test_lab.screen.JSONPopup')`
- [x] Line 197: Same change

Patch path updates (4 `WIDTH`/`HEIGHT` patches):
- [x] Line 160: `patch('game.ui.screens.test_lab_screen.WIDTH', 1920)` -> `patch('game.ui.screens.test_lab.screen.WIDTH', 1920)`
- [x] Line 161: `patch('game.ui.screens.test_lab_screen.HEIGHT', 1080)` -> `patch('game.ui.screens.test_lab.screen.HEIGHT', 1080)`
- [x] Line 198: Same as line 160
- [x] Line 199: Same as line 161

**Notes:** Used replace_all for batch updates

### Task 4.3: Update test_visual_run.py imports [Simple]
**File:** `tests/unit/test_lab/test_visual_run.py`
**Tests:** `pytest tests/unit/test_lab/test_visual_run.py -v`

Import update:
- [x] Line 78: `from game.ui.screens.test_lab_screen import TestLabScreen` -> `from game.ui.screens.test_lab import TestLabScreen`

Patch path updates (7 `TestRunner` patches):
- [x] Line 93: `patch('game.ui.screens.test_lab_screen.TestRunner')` -> `patch('game.ui.screens.test_lab.screen.TestRunner')`
- [x] Line 104: Same change
- [x] Line 115: Same change
- [x] Line 127: Same change
- [x] Line 139: Same change
- [x] Line 151: Same change
- [x] Line 166: Same change

**Notes:** Used replace_all for batch updates

### Task 4.4: Run targeted test suites [Simple]
**Tests:** Verify all affected tests pass

- [x] `pytest tests/unit/test_lab/ -v` — all test_lab tests pass (35 passed)
- [x] `pytest tests/unit/ui/test_lab_scene/ -v` — UI component tests pass (79 passed)

**Notes:** Full test suite: 6246 passed

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All imports updated (1 production + 7 test imports)
- [x] All 18 patch paths updated
- [x] All targeted tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
