# Phase 1: Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the centralized paths module and update constants.py to use it

---

## Tasks

### Task 1.1: Create game/core/paths.py [Medium] ✓
**File:** `game/core/paths.py` (NEW)
**Tests:** `pytest tests/ -v -k "path or import"`

- [x] Create new file `game/core/paths.py`
- [x] Implement `_find_project_root()` function using marker-based detection
- [x] Create `Paths` class with all path constants (see design.md for full implementation)
- [x] Add pathlib.Path accessor classmethods
- [x] Add backward-compatible module-level exports
- [x] Verify the module imports without errors: `python -c "from game.core.paths import Paths; print(Paths.ROOT_DIR)"`

**Implementation:** See [design.md](design.md) for the complete `paths.py` code.

**Notes:** Created as specified. Module works correctly.

### Task 1.2: Update game/core/constants.py [Simple] ✓
**File:** `game/core/constants.py`
**Tests:** `pytest tests/ -v`

- [x] Add import at top: `from game.core.paths import Paths`
- [x] Replace path definitions (lines 39-53) with imports from Paths:
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
- [x] Keep any non-path constants unchanged
- [x] Run full test suite to verify backward compatibility

**Notes:** Updated constants.py to import from paths.py. All 4594 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python -c "from game.core.paths import Paths; print(Paths.ROOT_DIR)"` works
- [x] `python -c "from game.core.constants import ROOT_DIR; print(ROOT_DIR)"` still works
- [x] Full test suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
