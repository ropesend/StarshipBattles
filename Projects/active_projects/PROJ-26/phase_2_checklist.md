# Phase 2: Core Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate core startup files to use centralized paths

---

## Tasks

### Task 2.1: Migrate game/app.py [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/ -v` (full suite - entry point)

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Remove local `base_path` calculation (line ~107):
  ```python
  # REMOVE: base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  ```
- [ ] Replace `os.path.join(base_path, "data", "components.json")` with `Paths.COMPONENTS_FILE`
- [ ] Replace `os.path.join(base_path, "data", "modifiers.json")` with `Paths.MODIFIERS_FILE`
- [ ] Replace `os.path.join(base_path, "data", "resources.json")` with `Paths.RESOURCES_FILE`
- [ ] Replace `"crash_log.txt"` (line ~747) with `Paths.CRASH_LOG`
- [ ] Verify game launches: `python -m game.app --help` or equivalent

**Notes:**

### Task 2.2: Migrate game/core/logger.py [Simple]
**File:** `game/core/logger.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace `'battle.log'` (line ~36) with `Paths.BATTLE_LOG`
- [ ] Verify logger creates file in correct location

**Notes:**

### Task 2.3: Migrate game/core/profiling.py [Simple]
**File:** `game/core/profiling.py`
**Tests:** `pytest tests/unit/core/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace `'profiling_history.json'` default (line ~109) with `Paths.PROFILING_HISTORY`
- [ ] Verify profiling history loads/saves correctly

**Notes:**

### Task 2.4: Migrate game/simulation/entities/ship_loader.py [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded `"data/vehicleclasses.json"` with `Paths.VEHICLE_CLASSES_FILE`
- [ ] Remove local base_path calculation if present
- [ ] Verify vehicle classes load correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Game launches without errors
- [ ] Battle log created in project root (not working directory)
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
