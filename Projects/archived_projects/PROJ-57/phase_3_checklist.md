# Phase 3: Extract Screen & Wire Up Package

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-57 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move TestLabScreen into screen.py, finalize __init__.py, delete original monolith file

---

## Tasks

### Task 3.1: Create screen.py (TestLabScreen + get_test_data_dir) [Medium]
**Source:** `game/ui/screens/test_lab_screen.py` lines 1-17 (imports/logger/utility), lines 2247-4703 (TestLabScreen)
**New file:** `game/ui/screens/test_lab/screen.py`
**Tests:** `python -c "from game.ui.screens.test_lab.screen import TestLabScreen, get_test_data_dir"`

- [x] Copy all top-of-file imports from original (lines 1-14) — preserve external imports exactly
- [x] Copy `logger = get_logger(__name__)` (line 16)
- [x] Copy `get_test_data_dir()` function (lines 19-33)
- [x] **CRITICAL: Fix path depth** — change from 3 `dirname()` to 4:
  ```python
  # Before (game/ui/screens/ = 3 levels to project root):
  current_dir = os.path.dirname(__file__)  # game/ui/screens
  project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

  # After (game/ui/screens/test_lab/ = 4 levels to project root):
  current_dir = os.path.dirname(__file__)  # game/ui/screens/test_lab
  project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
  ```
- [x] Copy `TestLabScreen` class (lines 2247-4703)
- [x] Add intra-package imports:
  ```python
  from .dialogs import JSONPopup, ConfirmationDialog
  from .json_viewer import ScrollableJSONViewer
  from .ship_panels import ShipPanel, TabbedShipPanel, ComponentPanel
  from .test_run_card import TestRunCard
  from .test_run_details import TestRunDetailsPanel
  from .results_panel import ResultsPanel
  ```
- [x] Verify lazy imports in TestLabScreen remain unchanged (BattleStateViewer, Validator, TestLabUIController, tkinter, BattleStateCapture)
- [x] Verify import works: `python -c "from game.ui.screens.test_lab.screen import TestLabScreen, get_test_data_dir"`

**Notes:** Created screen.py (~2460 lines). Verified path depth fix: get_test_data_dir() returns correct path.

### Task 3.2: Finalize __init__.py [Simple]
**File:** `game/ui/screens/test_lab/__init__.py`

- [x] Write `__init__.py` with:
  - Module docstring describing the package and listing all modules
  - `from .screen import TestLabScreen`
  - `__all__ = ['TestLabScreen']`
- [x] Verify: `python -c "from game.ui.screens.test_lab import TestLabScreen"`

**Notes:** Package exports TestLabScreen correctly.

### Task 3.3: Delete original monolith file [Simple]

- [x] Delete `game/ui/screens/test_lab_screen.py`
- [x] Verify package import still works: `python -c "from game.ui.screens.test_lab import TestLabScreen"`
- [x] Verify old import fails: `python -c "from game.ui.screens.test_lab_screen import TestLabScreen"` (should error)

**Notes:** Original file deleted. Old import fails as expected (ModuleNotFoundError).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/screens/test_lab/` has 9 files: `__init__.py` + 8 modules
- [x] Original `test_lab_screen.py` is deleted
- [x] Package import works correctly
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

**Note:** Tests in tests/unit/test_lab/ fail until Phase 4 updates external references (app.py, test files).
