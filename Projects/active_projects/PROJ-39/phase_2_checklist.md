# Phase 2: Core Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate core/critical files to use centralized paths

---

## Tasks

### Task 2.1: Update game/app.py [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/ -v` + manual game launch

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Remove local `base_path` calculation (line 107):
  ```python
  # REMOVE: base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  ```
- [ ] Replace hardcoded paths (lines 108-114):
  - `os.path.join(base_path, "data", "components.json")` → `Paths.COMPONENTS_FILE`
  - `os.path.join(base_path, "data", "modifiers.json")` → `Paths.MODIFIERS_FILE`
  - `os.path.join(base_path, "data", "resources.json")` → `Paths.RESOURCES_FILE`
- [ ] Replace crash log path (line 747):
  - `"crash_log.txt"` → `Paths.CRASH_LOG`
- [ ] Verify game launches correctly

**Notes:**

### Task 2.2: Update game/core/logger.py [Simple]
**File:** `game/core/logger.py`
**Tests:** `pytest tests/ -v -k logger`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded log path (line 36):
  - `'battle.log'` → `Paths.BATTLE_LOG`
- [ ] Verify battle.log is created in project root (not working directory)

**Notes:**

### Task 2.3: Update game/core/profiling.py [Simple]
**File:** `game/core/profiling.py`
**Tests:** N/A (profiling is optional)

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded path (line 109, function parameter default):
  - `'profiling_history.json'` → `Paths.PROFILING_HISTORY`
- [ ] Verify profiling still works if enabled

**Notes:**

### Task 2.4: Update game/simulation/entities/ship_loader.py [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/ -v -k ship`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded path (line 23, function parameter default):
  - `"data/vehicleclasses.json"` → `Paths.VEHICLE_CLASSES_FILE`
- [ ] Replace any other hardcoded data paths in this file
- [ ] Verify ship loading works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `base_path` calculations remain in updated files
- [ ] Game launches and loads all data correctly
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
