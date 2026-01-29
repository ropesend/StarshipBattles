# Phase 3: Workshop Circular Import Fix (AR-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Resolve circular dependency between workshop_screen and builder package

---

## Prerequisites
- [x] Phase 2C complete

## Background

**Current Issue (AR-006):**
- `game/ui/__init__.py` line 4 states: "workshop_screen is NOT eagerly imported here to avoid circular dependency with ui.builder package"
- This forces lazy imports and complicates module initialization
- Test discovery with pytest-xdist can fail if workers import in different order

**Root Cause:**
1. `game/ui/__init__.py` wants to import `workshop_screen`
2. `workshop_screen` imports from `ui.builder` package
3. `ui.builder` package imports back from `game.ui.screens`
4. Circular dependency!

---

## Tasks

### Task 3.1: Analyze Circular Dependency Chain [Simple]
**Files:** `game/ui/__init__.py`, `game/ui/screens/workshop_screen.py`, `ui/builder/__init__.py`
**Tests:** N/A (analysis)

- [x] Document exact import chain causing the circular dependency
- [x] Identify which imports in `workshop_screen.py` cause the issue (line 25)
- [x] Identify which imports in `ui.builder` package cause the issue
- [x] Document in findings/phase_3_analysis.md

**Notes:** FINDING: The circular import issue has been RESOLVED by existing lazy import patterns in ui.builder (left_panel.py, right_panel.py, detail_panel.py). The ui.builder package does NOT import game.ui directly - only specific submodules. All import order tests pass. pytest-xdist runs successfully (151 tests, 4 workers). See findings/phase_3_analysis.md for full analysis.

---

### Task 3.2: Extract Shared Interfaces [Medium] - SKIPPED
**File:** `game/ui/interfaces/builder_interfaces.py` (NEW)
**Tests:** `pytest tests/unit/ui/interfaces/`

- [x] ~~Create `game/ui/interfaces/` directory if not exists~~ NOT NEEDED
- [x] ~~Create `game/ui/interfaces/__init__.py`~~ NOT NEEDED
- [x] ~~Extract shared protocols/interfaces~~ NOT NEEDED
- [x] ~~Update imports in both packages~~ NOT NEEDED

**Notes:** SKIPPED - Analysis in Task 3.1 found circular import is already resolved. Existing lazy import patterns in ui.builder (left_panel.py, right_panel.py, detail_panel.py) break any potential cycle. No new interfaces required.

---

### Task 3.3: Refactor workshop_screen Imports [Medium] - SKIPPED
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop*.py`

**Current problematic import (line 25):**
```python
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
```

**Changes:**
- [x] ~~Analyze if TYPE_CHECKING can be used~~ NOT NEEDED
- [x] ~~Consider lazy imports~~ NOT NEEDED
- [x] ~~Restructure to avoid circular chain~~ NOT NEEDED
- [x] ~~Update imports~~ NOT NEEDED

**Notes:** SKIPPED - No circular import exists. The ui.builder package already uses lazy imports for BuilderEvents (the only shared dependency). Current imports work correctly in all test scenarios including pytest-xdist.

---

### Task 3.4: Update game/ui/__init__.py [Simple]
**File:** `game/ui/__init__.py`
**Tests:** Import order tests

**Changes:**
- [x] Remove the comment about circular dependency (line 4)
- [x] Add proper workshop_screen import if circular is fixed
- [x] Or document why lazy import is intentional design choice
- [x] Verify import order doesn't cause issues

**Notes:** Updated docstring to clarify that the lazy import is NOT due to circular dependency (which is resolved) but due to module-level side effects in workshop_screen.py (Tkinter initialization). Attempting to add workshop_screen to eager imports caused 35 test failures + 29 errors due to test isolation issues. Documentation now accurately reflects the reason for keeping workshop_screen as a lazy import.

---

### Task 3.5: Verify Import Order [Simple]
**Tests:** `python -c "import game.ui"`, `pytest tests/ -x`

- [x] Verify `import game.ui` works without errors
- [x] Verify `import game.ui.screens.workshop_screen` works
- [x] Verify pytest-xdist tests don't have import order issues
- [x] Run full test suite

**Notes:** All verifications passed. Full test suite: 5249 passed, 3 skipped. pytest-xdist with 4 workers: 151 builder tests passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Circular dependency resolved or documented as intentional
- [x] No import errors when importing game.ui
- [x] All tests pass including with pytest-xdist
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
