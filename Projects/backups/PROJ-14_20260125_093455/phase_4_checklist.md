# Phase 4: Delete Legacy UI Components

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove legacy Button/Label/Slider classes after migration complete

**CRITICAL:** Do NOT start this phase until Phase 3 is fully tested and verified!

---

## Tasks

### Task 4.1: Remove Button import from app.py [Simple]
**File:** `game/app.py`
**Line:** 17
**Tests:** Game should launch

- [x] Remove `from ui import Button` import line
- [x] Verify: `python -c "from game.app import Game"` succeeds

**Notes:** Completed 2026-01-25.

---

### Task 4.2: Remove Button import from test_lab_scene.py [Simple]
**File:** `ui/test_lab_scene.py`
**Line:** 9
**Tests:** `python -c "from ui.test_lab_scene import TestLabScene"` succeeds

- [x] Remove `from ui.components import Button` import line

**Notes:** Completed during Phase 3.

---

### Task 4.3: Update ui/__init__.py exports [Simple]
**File:** `ui/__init__.py`
**Line:** 2
**Tests:** `python -c "from ui import Button"` should FAIL with ImportError

- [x] Remove line: `from .components import Button, Label, Slider`
- [x] Keep any other exports if present

**Notes:** Completed 2026-01-25. Added comment about using pygame_gui instead.

---

### Task 4.4: Delete ui/components.py [Simple]
**File:** `ui/components.py` (101 lines)
**Tests:** `pytest tests/` - verify no import errors

- [x] Delete entire file `ui/components.py`
- [x] Verify: `python -c "from game.app import Game"` succeeds

**Notes:** Completed 2026-01-25.

---

### Task 4.5: Delete legacy widget tests [Simple]
**File:** `tests/unit/ui/test_ui_widgets.py` (130 lines)
**Tests:** `pytest tests/unit/ui/` - remaining tests should pass

- [x] Delete entire file (tests Button, Label, Slider which no longer exist)

**Notes:** Completed 2026-01-25. All 452 UI unit tests still pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `ui/components.py` deleted
- [x] `tests/unit/ui/test_ui_widgets.py` deleted
- [x] `ui/__init__.py` no longer exports Button/Label/Slider
- [x] Full test suite passes: `pytest tests/`
- [x] Integration tests pass: `pytest tests/integration/`
- [x] Game launches and all menu buttons work
- [x] Combat Lab works with all dialogs
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `Project Complete`

---

## Final Verification
After Phase 4 is complete, perform this full verification:
- [x] Launch game
- [x] Click each menu button, verify correct scene loads
- [x] Resize window, verify menu still works
- [x] Open Combat Lab
- [x] Use all dialog buttons (JSONPopup close, Confirmation confirm/cancel)
- [x] Click Back button, return to menu
- [x] No warnings about missing imports in console
- [x] No deprecation warnings
