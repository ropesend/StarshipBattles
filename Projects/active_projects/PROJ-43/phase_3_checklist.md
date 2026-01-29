# Phase 3: Workshop Circular Import Fix (AR-006)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Resolve circular dependency between workshop_screen and builder package

---

## Prerequisites
- [ ] Phase 2C complete

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

- [ ] Document exact import chain causing the circular dependency
- [ ] Identify which imports in `workshop_screen.py` cause the issue (line 25)
- [ ] Identify which imports in `ui.builder` package cause the issue
- [ ] Document in findings/phase_3_analysis.md

**Notes:**

---

### Task 3.2: Extract Shared Interfaces [Medium]
**File:** `game/ui/interfaces/builder_interfaces.py` (NEW)
**Tests:** `pytest tests/unit/ui/interfaces/`

- [ ] Create `game/ui/interfaces/` directory if not exists
- [ ] Create `game/ui/interfaces/__init__.py`
- [ ] Extract shared protocols/interfaces that both packages need:
  - Any shared event types
  - Any shared panel interfaces
  - Any shared callback signatures
- [ ] Update imports in both packages to use interfaces

**Notes:**

---

### Task 3.3: Refactor workshop_screen Imports [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop*.py`

**Current problematic import (line 25):**
```python
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
```

**Changes:**
- [ ] Analyze if TYPE_CHECKING can be used for some imports
- [ ] Consider lazy imports via properties if runtime instantiation
- [ ] Or restructure to avoid circular chain
- [ ] Update imports to break circular dependency

**Notes:**

---

### Task 3.4: Update game/ui/__init__.py [Simple]
**File:** `game/ui/__init__.py`
**Tests:** Import order tests

**Changes:**
- [ ] Remove the comment about circular dependency (line 4)
- [ ] Add proper workshop_screen import if circular is fixed
- [ ] Or document why lazy import is intentional design choice
- [ ] Verify import order doesn't cause issues

**Notes:**

---

### Task 3.5: Verify Import Order [Simple]
**Tests:** `python -c "import game.ui"`, `pytest tests/ -x`

- [ ] Verify `import game.ui` works without errors
- [ ] Verify `import game.ui.screens.workshop_screen` works
- [ ] Verify pytest-xdist tests don't have import order issues
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Circular dependency resolved or documented as intentional
- [ ] No import errors when importing game.ui
- [ ] All tests pass including with pytest-xdist
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
