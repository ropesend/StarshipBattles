# Phase 1: Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the centralized paths module and update constants.py to use it

---

## Tasks

### Task 1.1: Create game/core/paths.py [Medium]
**File:** `game/core/paths.py` (NEW)
**Tests:** `pytest tests/ -v -k "path or import"`

- [ ] Create new file `game/core/paths.py`
- [ ] Implement `_find_project_root()` function using marker-based detection
- [ ] Create `Paths` class with all path constants (see design.md for full implementation)
- [ ] Add pathlib.Path accessor classmethods
- [ ] Add backward-compatible module-level exports
- [ ] Verify the module imports without errors: `python -c "from game.core.paths import Paths; print(Paths.ROOT_DIR)"`

**Implementation:** See [design.md](design.md) for the complete `paths.py` code.

**Notes:**

### Task 1.2: Update game/core/constants.py [Simple]
**File:** `game/core/constants.py`
**Tests:** `pytest tests/ -v`

- [ ] Add import at top: `from game.core.paths import Paths`
- [ ] Replace path definitions (lines 39-53) with imports from Paths:
  ```python
  # Import centralized paths
  from game.core.paths import Paths

  ROOT_DIR = Paths.ROOT_DIR
  GAME_DIR = Paths.GAME_DIR
  CORE_DIR = Paths.CORE_DIR
  ASSET_DIR = Paths.ASSET_DIR
  DATA_DIR = Paths.DATA_DIR
  SHIPS_DIR = Paths.SHIPS_DIR
  SCREENSHOT_DIR = Paths.SCREENSHOTS_DIR

  COMPONENTS_FILE = Paths.COMPONENTS_FILE
  MODIFIERS_FILE = Paths.MODIFIERS_FILE
  VEHICLE_CLASSES_FILE = Paths.VEHICLE_CLASSES_FILE
  ```
- [ ] Keep any non-path constants unchanged
- [ ] Run full test suite to verify backward compatibility

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python -c "from game.core.paths import Paths; print(Paths.ROOT_DIR)"` works
- [ ] `python -c "from game.core.constants import ROOT_DIR; print(ROOT_DIR)"` still works
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
