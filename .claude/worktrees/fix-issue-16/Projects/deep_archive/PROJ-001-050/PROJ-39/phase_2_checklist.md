# Phase 2: Core Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate core/critical files to use centralized paths

---

## Tasks

### Task 2.1: Update game/app.py [Medium] ✓
**File:** `game/app.py`
**Tests:** `pytest tests/ -v` + manual game launch

- [x] Add import: `from game.core.paths import Paths`
- [x] Remove local `base_path` calculation (line 107)
- [x] Replace hardcoded paths:
  - `Paths.COMPONENTS_FILE`, `Paths.MODIFIERS_FILE`, `Paths.RESOURCES_FILE`
- [x] Replace crash log path: `Paths.CRASH_LOG`
- [x] Verify game module imports correctly

**Notes:** Still passes `Paths.ROOT_DIR` to `initialize_ship_data` and `load_sprites` since those functions use it to find subdirectories.

### Task 2.2: Update game/core/logger.py [Simple] ✓
**File:** `game/core/logger.py`
**Tests:** `pytest tests/ -v -k logger`

- [x] Add import: `from game.core.paths import Paths`
- [x] Replace hardcoded log path: `Paths.BATTLE_LOG`

**Notes:** Done.

### Task 2.3: Update game/core/profiling.py [Simple] ✓
**File:** `game/core/profiling.py`
**Tests:** N/A (profiling is optional)

- [x] Add import: `from game.core.paths import Paths`
- [x] Replace hardcoded path default: `Paths.PROFILING_HISTORY`

**Notes:** Done.

### Task 2.4: Update game/simulation/entities/ship_loader.py [Simple] ✓
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/ -v -k ship`

- [x] Add import: `from game.core.paths import Paths`
- [x] Replace hardcoded path default: `Paths.VEHICLE_CLASSES_FILE`

**Notes:** Done.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No `base_path` calculations remain in updated files
- [x] Game module imports correctly
- [x] Full test suite passes (4594 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
