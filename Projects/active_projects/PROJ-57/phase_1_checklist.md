# Phase 1: Setup & Extract Leaf Nodes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-57 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the package directory, delete legacy file, extract the 5 leaf-node classes (no intra-package dependencies)

---

## Tasks

### Task 1.1: Delete legacy file and create package directory [Simple]
**File:** `game/ui/screens/test_lab.py` (delete), `game/ui/screens/test_lab/` (create)
**Tests:** `pytest tests/ -x -q` (verify no regressions from deleting dead file)

- [x] Delete `game/ui/screens/test_lab.py` (verified: zero imports anywhere in codebase)
- [x] Create directory `game/ui/screens/test_lab/`
- [x] Create empty `game/ui/screens/test_lab/__init__.py` (placeholder)
- [x] Run `pytest tests/ -x -q` to confirm no regressions

**Notes:** Deleted legacy file successfully. 6246 tests passed after deletion.

### Task 1.2: Extract dialogs.py (JSONPopup + ConfirmationDialog) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 36-289
**New file:** `game/ui/screens/test_lab/dialogs.py`
**Tests:** `python -c "from game.ui.screens.test_lab.dialogs import JSONPopup, ConfirmationDialog"`

- [x] Copy `JSONPopup` class (lines 36-139) to `dialogs.py`
- [x] Copy `ConfirmationDialog` class (lines 141-289) to `dialogs.py`
- [x] Add required imports at top: `pygame`, `pygame_gui`, `UIButton`, constants (`WHITE, BLACK, BLUE, FONT_MAIN`)
- [x] Verify import works: `python -c "from game.ui.screens.test_lab.dialogs import JSONPopup, ConfirmationDialog"`

**Notes:** Only FONT_MAIN constant needed.

### Task 1.3: Extract json_viewer.py (ScrollableJSONViewer) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 291-402
**New file:** `game/ui/screens/test_lab/json_viewer.py`
**Tests:** `python -c "from game.ui.screens.test_lab.json_viewer import ScrollableJSONViewer"`

- [x] Copy `ScrollableJSONViewer` class (lines 291-402) to `json_viewer.py`
- [x] Add required imports: `pygame`, `json`, constants (`FONT_MAIN, WHITE, BLACK`)
- [x] Verify import works

**Notes:** Only FONT_MAIN constant needed.

### Task 1.4: Extract component_dropdown.py (ComponentDropdown) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 404-547
**New file:** `game/ui/screens/test_lab/component_dropdown.py`
**Tests:** `python -c "from game.ui.screens.test_lab.component_dropdown import ComponentDropdown"`

- [x] Copy `ComponentDropdown` class (lines 404-547) to `component_dropdown.py`
- [x] Add required imports: `pygame`, constants (`FONT_MAIN`)
- [x] Verify import works

**Notes:** Complete.

### Task 1.5: Extract test_run_card.py (TestRunCard) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 794-1165
**New file:** `game/ui/screens/test_lab/test_run_card.py`
**Tests:** `python -c "from game.ui.screens.test_lab.test_run_card import TestRunCard"`

- [x] Copy `TestRunCard` class (lines 794-1165) to `test_run_card.py`
- [x] Add required imports: `pygame`, `time`, constants (check which constants are used)
- [x] Verify import works

**Notes:** Only FONT_MAIN constant needed. No time module needed.

### Task 1.6: Extract test_run_details.py (TestRunDetailsPanel) [Simple]
**Source:** `game/ui/screens/test_lab_screen.py` lines 1167-1998
**New file:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `python -c "from game.ui.screens.test_lab.test_run_details import TestRunDetailsPanel"`

- [x] Copy `TestRunDetailsPanel` class (lines 1167-1998) to `test_run_details.py`
- [x] Add required imports: `pygame`, `pygame_gui`, `json`, `re` (if used), constants
- [x] Check for `pygame.scrap` usage (clipboard) — include if present
- [x] Verify import works

**Notes:** Only pygame and FONT_MAIN needed. No pygame.scrap or re usage in this class.

### Task 1.7: Verify all leaf extractions [Simple]
**Tests:** Run all 5 import checks + quick test suite

- [x] `python -c "from game.ui.screens.test_lab.dialogs import JSONPopup, ConfirmationDialog"`
- [x] `python -c "from game.ui.screens.test_lab.json_viewer import ScrollableJSONViewer"`
- [x] `python -c "from game.ui.screens.test_lab.component_dropdown import ComponentDropdown"`
- [x] `python -c "from game.ui.screens.test_lab.test_run_card import TestRunCard"`
- [x] `python -c "from game.ui.screens.test_lab.test_run_details import TestRunDetailsPanel"`

**Notes:** All 5 modules import successfully. Full test suite: 6246 passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] 5 new module files exist in `game/ui/screens/test_lab/`
- [x] Legacy `test_lab.py` deleted
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
